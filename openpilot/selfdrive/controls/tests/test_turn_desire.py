import unittest

from opendbc.car.structs import CarState
from openpilot.cereal import log
from openpilot.common.constants import CV
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.controls.lib.desire_helper import DesireHelper, LaneChangeState
from openpilot.selfdrive.controls.lib.turn_desire_helper import TURN_REQUEST_FRAMES_MAX, TurnDelivery, TurnState


class TestTurnDesire(unittest.TestCase):
  def setUp(self):
    self.helper = DesireHelper(turn_desire_enabled=True)
    self.cs = CarState.new_message(vEgo=5 * CV.MPH_TO_MS, gearShifter="drive", leftBlinker=True)

  def run_for(self, seconds, *, active=True, valid=True, probability=0.0, **changes):
    for field, value in changes.items():
      setattr(self.cs, field, value)
    desires = []
    for _ in range(round(seconds / DT_MDL)):
      self.helper.update(self.cs, active, probability, turn_inputs_valid=valid)
      desires.append(self.helper.desire)
    return [d for d in desires if d != log.Desire.none]

  def release_signal(self):
    self.run_for(0.6, leftBlinker=False, rightBlinker=False)

  def test_left_and_right_have_correct_policy_enum_and_one_pulse(self):
    for left, expected in ((True, log.Desire.turnLeft), (False, log.Desire.turnRight)):
      with self.subTest(left=left):
        self.release_signal()
        self.assertEqual(self.run_for(3, leftBlinker=left, rightBlinker=not left), [expected])
        self.assertEqual(self.helper.lane_change_state, LaneChangeState.off)

  def test_disabled_by_default(self):
    self.helper = DesireHelper()
    self.assertEqual(self.run_for(3), [])
    self.assertEqual(self.helper.turn.state, TurnState.idle)

  def test_long_red_light_waits_for_motion(self):
    self.assertEqual(self.run_for(60, vEgo=0.0, standstill=True), [])
    self.assertEqual(self.helper.turn.state, TurnState.armed)
    self.assertEqual(self.run_for(1, vEgo=0.6, standstill=False), [log.Desire.turnLeft])

  def test_no_pulse_at_action_hold_speed(self):
    self.assertEqual(self.run_for(2, vEgo=0.3), [])
    self.assertEqual(self.run_for(1, vEgo=0.5), [log.Desire.turnLeft])

  def test_signal_debounce(self):
    self.assertEqual(self.run_for(0.2), [])
    self.release_signal()
    self.assertEqual(self.run_for(0.2, leftBlinker=True), [])
    self.assertEqual(self.run_for(0.2), [log.Desire.turnLeft])

  def test_approach_with_existing_signal(self):
    # A lane-change pre-state clears as the driver slows below 20 mph.
    self.assertEqual(self.run_for(1, vEgo=30 * CV.MPH_TO_MS), [])
    self.assertEqual(self.helper.lane_change_state, LaneChangeState.preLaneChange)
    self.assertEqual(self.run_for(1, vEgo=17 * CV.MPH_TO_MS), [])
    self.assertEqual(self.run_for(1, vEgo=12 * CV.MPH_TO_MS), [log.Desire.turnLeft])

  def test_start_speed_envelope(self):
    # CarState stores Float32; use points on either side of the threshold rather
    # than assuming the converted 15 mph value is exactly representable.
    for mph, expected in ((14.99, [log.Desire.turnLeft]), (15.01, []), (15.1, []), (19.9, [])):
      with self.subTest(mph=mph):
        self.release_signal()
        self.assertEqual(self.run_for(1, leftBlinker=True, vEgo=mph * CV.MPH_TO_MS), expected)

  def test_acceleration_does_not_retrigger_or_become_lane_change(self):
    self.assertEqual(self.run_for(1), [log.Desire.turnLeft])
    for mph in (12.5, 16, 19.9):
      self.assertEqual(self.run_for(0.5, vEgo=mph * CV.MPH_TO_MS), [])
      self.assertEqual(self.helper.turn.state, TurnState.active)
    self.assertEqual(self.run_for(1, vEgo=21 * CV.MPH_TO_MS, steeringPressed=True, steeringTorque=1.5), [])
    self.assertEqual(self.helper.turn.state, TurnState.blocked)
    self.assertEqual(self.helper.lane_change_state, LaneChangeState.off)
    self.assertEqual(self.run_for(1, vEgo=5 * CV.MPH_TO_MS), [])

  def test_cannot_start_after_accelerating_out_of_arming_range(self):
    self.assertEqual(self.run_for(0.1), [])
    self.assertEqual(self.run_for(1, vEgo=16 * CV.MPH_TO_MS), [])
    self.assertEqual(self.run_for(1, vEgo=5 * CV.MPH_TO_MS), [])
    self.assertEqual(self.helper.turn.state, TurnState.blocked)

  def test_one_held_signal_expires_without_retrigger(self):
    self.assertEqual(self.run_for(25), [log.Desire.turnLeft])
    self.assertEqual(self.helper.turn.state, TurnState.blocked)
    self.assertEqual(self.run_for(5), [])
    self.release_signal()
    self.assertEqual(self.run_for(1, leftBlinker=True), [log.Desire.turnLeft])

  def test_brief_signal_dropout_does_not_rearm(self):
    self.assertEqual(self.run_for(1), [log.Desire.turnLeft])
    self.run_for(0.1, leftBlinker=False)
    self.assertEqual(self.run_for(1, leftBlinker=True), [])
    self.release_signal()
    self.assertEqual(self.run_for(1, leftBlinker=True), [log.Desire.turnLeft])

  def test_direct_direction_flip_requires_release(self):
    self.assertEqual(self.run_for(1), [log.Desire.turnLeft])
    self.assertEqual(self.run_for(1, leftBlinker=False, rightBlinker=True), [])
    self.release_signal()
    self.assertEqual(self.run_for(1, rightBlinker=True), [log.Desire.turnRight])

  def test_hazards_require_release(self):
    self.assertEqual(self.run_for(1, rightBlinker=True), [])
    self.assertEqual(self.run_for(1, rightBlinker=False), [])
    self.release_signal()
    self.assertEqual(self.run_for(1, leftBlinker=True), [log.Desire.turnLeft])

  def test_blindspot_blocks_and_does_not_auto_resume(self):
    for left in (True, False):
      with self.subTest(left=left):
        self.release_signal()
        self.assertEqual(self.run_for(1, leftBlinker=left, rightBlinker=not left, leftBlindspot=left, rightBlindspot=not left), [])
        self.assertEqual(self.run_for(1, leftBlindspot=False, rightBlindspot=False), [])
        self.assertEqual(self.helper.turn.state, TurnState.blocked)

  def test_opposite_blindspot_does_not_block(self):
    self.assertEqual(self.run_for(1, rightBlindspot=True), [log.Desire.turnLeft])

  def test_opposing_steering_blocks_both_directions(self):
    for left, torque in ((True, -1.5), (False, 1.5)):
      with self.subTest(left=left):
        self.release_signal()
        self.assertEqual(self.run_for(1, leftBlinker=left, rightBlinker=not left, steeringPressed=True, steeringTorque=torque), [])
        self.assertEqual(self.run_for(1, steeringPressed=False, steeringTorque=0.0), [])

  def test_matching_driver_steering_does_not_block(self):
    self.assertEqual(self.run_for(1, steeringPressed=True, steeringTorque=1.5), [log.Desire.turnLeft])

  def test_no_turn_until_lateral_control_active(self):
    self.assertEqual(self.run_for(1, active=False), [])
    self.assertEqual(self.run_for(1, active=True), [log.Desire.turnLeft])

  def test_disengagement_does_not_rearm_held_signal(self):
    self.assertEqual(self.run_for(1), [log.Desire.turnLeft])
    self.assertEqual(self.run_for(1, active=False), [])
    self.assertEqual(self.run_for(1, active=True), [])
    self.release_signal()
    self.assertEqual(self.run_for(1, leftBlinker=True), [log.Desire.turnLeft])

  def test_invalid_or_stale_inputs_cancel_arming(self):
    self.assertEqual(self.run_for(0.1), [])
    self.assertEqual(self.run_for(1, valid=False), [])
    self.assertEqual(self.run_for(1, valid=True), [])

  def test_bad_speed_and_non_drive_gears_never_start(self):
    for changes in ({'vEgo': float('nan')}, {'vEgo': float('inf')}, {'vEgo': -1.0},
                    {'gearShifter': 'reverse'}, {'gearShifter': 'park'}, {'gearShifter': 'neutral'}, {'gearShifter': 'unknown'}):
      with self.subTest(changes=changes):
        self.setUp()
        self.assertEqual(self.run_for(1, **changes), [])

  def test_no_turn_can_interrupt_lane_change_starting(self):
    self.run_for(0.1, vEgo=30 * CV.MPH_TO_MS)
    self.run_for(0.1, steeringPressed=True, steeringTorque=1.5, probability=1.0)
    self.assertEqual(self.helper.lane_change_state, LaneChangeState.laneChangeStarting)
    self.assertEqual(set(self.run_for(1, vEgo=5 * CV.MPH_TO_MS, probability=1.0)), {log.Desire.laneChangeLeft})
    self.assertEqual(self.helper.turn.state, TurnState.idle)

  def test_completed_lane_change_cannot_become_turn_with_same_signal(self):
    self.run_for(0.1, vEgo=30 * CV.MPH_TO_MS)
    self.run_for(0.1, steeringPressed=True, steeringTorque=1.5, probability=1.0)
    self.assertEqual(self.helper.lane_change_state, LaneChangeState.laneChangeStarting)
    # Complete the lane change and then slow down with the signal still on.
    self.run_for(1, steeringPressed=False, steeringTorque=0.0, probability=0.0)
    self.assertEqual(self.run_for(2, vEgo=5 * CV.MPH_TO_MS), [])
    self.assertEqual(self.helper.turn.state, TurnState.idle)
    self.release_signal()
    self.assertEqual(self.run_for(1, leftBlinker=True), [log.Desire.turnLeft])

  def test_high_speed_lane_changes_still_require_torque_and_clear_blindspot(self):
    for enabled in (True, False):
      for left, expected in ((True, log.Desire.laneChangeLeft), (False, log.Desire.laneChangeRight)):
        with self.subTest(enabled=enabled, left=left):
          self.helper = DesireHelper(turn_desire_enabled=enabled)
          self.cs = CarState.new_message(vEgo=30 * CV.MPH_TO_MS, gearShifter="drive", leftBlinker=left, rightBlinker=not left)
          self.assertEqual(self.run_for(1), [])
          self.assertEqual(self.helper.lane_change_state, LaneChangeState.preLaneChange)
          self.assertEqual(self.run_for(0.1, steeringPressed=True, steeringTorque=1.5 if left else -1.5,
                                        leftBlindspot=left, rightBlindspot=not left), [])
          self.assertEqual(self.run_for(DT_MDL, leftBlindspot=False, rightBlindspot=False), [expected])
          self.assertEqual(self.helper.turn.state, TurnState.idle)


class TestTurnRequest(unittest.TestCase):
  """The request between update() queueing it and the model runner's word that
  it went. The integration order is exercised in tools/jetlink/test_turn_request_delivery.py."""

  def setUp(self):
    self.helper = DesireHelper(turn_desire_enabled=True)
    self.cs = CarState.new_message(vEgo=5 * CV.MPH_TO_MS, gearShifter="drive", leftBlinker=True)
    self.now = 0.0

  def update(self, sent=True, changed=False, active=True, valid=True):
    self.now += DT_MDL
    self.helper.update(self.cs, active, 0.0, turn_inputs_valid=valid, turn_desire_sent=sent, model_changed=changed, now=self.now)

  def queue(self):
    for _ in range(40):
      self.update()
      if self.helper.turn.pending:
        return
    self.fail("not queued")

  def timers(self):
    turn = self.helper.turn
    return (turn.state, turn.signal_timer, turn.off_timer, turn.turn_timer, turn.lane_change_consumed,
            self.helper.lane_change_state, self.helper.lane_change_timer, self.helper.lane_change_direction)

  def test_presend_moves_no_timer(self):
    self.queue()
    before = self.timers()
    for _ in range(50):
      self.assertEqual(self.helper.presend(self.cs, True, now=self.now), log.Desire.turnLeft)
    self.assertEqual(self.timers(), before)
    self.assertEqual(self.helper.turn.offers, 1)

  def test_presend_is_a_passthrough_without_a_queued_request(self):
    for enabled in (False, True):
      helper = DesireHelper(turn_desire_enabled=enabled)
      cs = CarState.new_message(vEgo=30 * CV.MPH_TO_MS, gearShifter="drive", leftBlinker=True)
      for _ in range(30):
        helper.update(cs, True, 1.0)
      cs.steeringPressed, cs.steeringTorque = True, 1.5
      helper.update(cs, True, 1.0)
      self.assertEqual(helper.desire, log.Desire.laneChangeLeft)
      # nothing a turn request would be cancelled for touches a lane change's desire
      self.assertEqual(helper.presend(cs, False, turn_inputs_valid=False, now=1e9), log.Desire.laneChangeLeft)
      self.assertEqual(helper.lane_change_state, LaneChangeState.laneChangeStarting)

  def test_asked_until_sent_then_never_again(self):
    self.queue()
    self.update(sent=False)
    self.assertEqual((self.helper.desire, self.helper.turn.delivery), (log.Desire.turnLeft, TurnDelivery.queued))
    self.update(sent=True)
    self.assertEqual((self.helper.desire, self.helper.turn.delivery), (log.Desire.none, TurnDelivery.transmitted))
    for _ in range(100):
      self.update(sent=False)
      self.assertEqual(self.helper.desire, log.Desire.none)

  def test_asked_at_most_a_few_frames(self):
    self.queue()
    offered = 1
    for _ in range(20):
      self.update(sent=False)
      offered += self.helper.desire == log.Desire.turnLeft
    self.assertEqual(offered, TURN_REQUEST_FRAMES_MAX)
    self.assertEqual((self.helper.turn.state, self.helper.turn.drop_reason), (TurnState.blocked, "expired"))

  def test_presend_drops_on_each_reason(self):
    cases = {
      "signal off": {"leftBlinker": False}, "hazards": {"rightBlinker": True},
      "direction changed": {"leftBlinker": False, "rightBlinker": True}, "blindspot": {"leftBlindspot": True},
      "driver opposing": {"steeringPressed": True, "steeringTorque": -1.0}, "not in drive": {"gearShifter": "park"},
      "speed": {"vEgo": 25 * CV.MPH_TO_MS},
    }
    for reason, changes in cases.items():
      with self.subTest(reason=reason):
        self.setUp()
        self.queue()
        for field, value in changes.items():
          setattr(self.cs, field, value)
        self.assertEqual(self.helper.presend(self.cs, True, now=self.now), log.Desire.none)
        self.assertEqual((self.helper.turn.delivery, self.helper.turn.drop_reason), (TurnDelivery.dropped, reason))
    for reason, kw in (("lateral inactive", {"lateral_active": False}), ("inputs invalid", {"turn_inputs_valid": False})):
      with self.subTest(reason=reason):
        self.setUp()
        self.queue()
        args = {"lateral_active": True, "turn_inputs_valid": True, "now": self.now} | kw
        self.assertEqual(self.helper.presend(self.cs, **args), log.Desire.none)
        self.assertEqual(self.helper.turn.drop_reason, reason)

  def test_a_dropped_request_stays_dropped_while_the_signal_is_held(self):
    self.queue()
    self.helper.presend(self.cs, False, now=self.now)
    for _ in range(200):
      self.update()
      self.assertEqual(self.helper.desire, log.Desire.none)
    self.assertEqual(self.helper.turn.state, TurnState.blocked)

  def test_a_model_change_drops_a_queued_request(self):
    self.queue()
    self.helper.turn_model_changed()
    self.assertEqual((self.helper.desire, self.helper.turn.drop_reason), (log.Desire.none, "model changed"))
    helper = DesireHelper(turn_desire_enabled=True)
    helper.turn_model_changed()
    self.assertEqual((helper.turn.delivery, helper.turn.state), (TurnDelivery.none, TurnState.idle))

  def test_a_model_change_while_arming_blocks_that_signal(self):
    for how in ("update", "direct"):
      with self.subTest(how=how):
        self.setUp()
        self.update()
        self.update()
        self.assertEqual(self.helper.turn.state, TurnState.armed)
        if how == "update":
          self.update(changed=True)
        else:
          self.helper.turn_model_changed()
        self.assertEqual((self.helper.turn.state, self.helper.turn.drop_reason, self.helper.turn.pending), (TurnState.blocked, "model changed", False))
        for _ in range(200):
          self.update()
          self.assertEqual(self.helper.desire, log.Desire.none)
        # released and given again, it is a new signal to the model now driving
        self.cs.leftBlinker = False
        for _ in range(15):
          self.update()
        self.cs.leftBlinker = True
        self.queue()

  def test_the_update_that_would_queue_does_not_on_a_model_change(self):
    for _ in range(40):
      before = self.helper.turn.signal_timer
      self.update()
      if self.helper.turn.pending:
        break
    frames = round(before / DT_MDL) + 1          # updates from the signal to the queueing one
    self.setUp()
    for _ in range(frames - 1):
      self.update()
    self.assertEqual((self.helper.turn.state, self.helper.turn.pending), (TurnState.armed, False))
    self.update(changed=True)                    # this update would have queued it
    self.assertEqual((self.helper.turn.pending, self.helper.desire, self.helper.turn.state), (False, log.Desire.none, TurnState.blocked))

  def test_a_model_change_after_the_request_went_changes_nothing(self):
    self.queue()
    self.update(sent=True)
    self.update(changed=True)
    self.helper.turn_model_changed()
    self.assertEqual((self.helper.turn.state, self.helper.turn.delivery), (TurnState.active, TurnDelivery.transmitted))

  def test_sent_on_the_frame_the_model_changed_is_transmitted_not_asked_again(self):
    # the old model took the frame and that frame was its last (a lag hand-back)
    self.queue()
    self.update(sent=True, changed=True)
    self.assertEqual((self.helper.turn.delivery, self.helper.turn.pending, self.helper.desire), (TurnDelivery.transmitted, False, log.Desire.none))

  def test_a_lane_change_desire_survives_a_model_change(self):
    helper = DesireHelper(turn_desire_enabled=True)
    cs = CarState.new_message(vEgo=30 * CV.MPH_TO_MS, gearShifter="drive", leftBlinker=True)
    for _ in range(30):
      helper.update(cs, True, 1.0)
    cs.steeringPressed, cs.steeringTorque = True, 1.5
    helper.update(cs, True, 1.0)
    helper.turn_model_changed()
    helper.update(cs, True, 1.0, model_changed=True)
    self.assertEqual((helper.desire, helper.lane_change_state), (log.Desire.laneChangeLeft, LaneChangeState.laneChangeStarting))


if __name__ == '__main__':
  unittest.main()
