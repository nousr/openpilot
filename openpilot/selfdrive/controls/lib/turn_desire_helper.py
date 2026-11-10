"""Opt-in intersection intent. This selects a policy input, not a steering command."""
from enum import StrEnum
import math
import time

from opendbc.car.structs import CarState
from openpilot.cereal import log
from openpilot.common.constants import CV
from openpilot.common.realtime import DT_MDL


# Initial closed-course settings, shared by left and right turns. These are intent
# gates, not target speeds or a claim that the car can execute a particular curve.
TURN_START_SPEED_MAX = 15 * CV.MPH_TO_MS
TURN_END_SPEED = 20 * CV.MPH_TO_MS
TURN_START_SPEED_MIN = 0.5  # m/s; don't spend the one-shot intent while stopped
TURN_SIGNAL_TIME = 0.3
TURN_SIGNAL_OFF_TIME = 0.5
TURN_TIME_MAX = 20.0
# A request is offered to the model runner until the runner says the frame
# carrying it went out, for at most this many frames and this long. Jetlink
# hands the drive back after five held frames in a row; a request older than
# this is dropped and reported, never delivered late.
TURN_REQUEST_FRAMES_MAX = 4
TURN_REQUEST_AGE_MAX = 0.3  # s, by the clock: the frame count assumes 20 Hz


class TurnState(StrEnum):
  idle = "idle"
  armed = "armed"
  active = "active"
  blocked = "blocked"


class TurnDelivery(StrEnum):
  """How far the one request of a signal episode got. `transmitted` is the
  runner's word that the frame carrying it went to the model that drives
  (for Jetlink: handed to the link). Whether the host then ran that frame is
  the runner's to trace (desire_trace); whether the policy acts on it shows
  only in what it plans."""
  none = "none"
  queued = "queued"
  transmitted = "transmitted"
  dropped = "dropped"


class TurnDesireHelper:
  def __init__(self, enabled=False):
    self.enabled = enabled
    self.reset()

  def reset(self):
    self.state = TurnState.idle
    self.direction = log.Desire.none
    self.desire = log.Desire.none
    self.signal_timer = 0.0
    self.off_timer = 0.0
    self.turn_timer = 0.0
    self.lane_change_consumed = False
    # the request: offered and not yet acknowledged, how often and since when
    self.pending = False
    self.offers = 0
    self.queued_at = 0.0
    self.delivery = TurnDelivery.none
    self.drop_reason = ""

  @property
  def consumes_blinker(self):
    # Never convert a turn's still-held signal into a lane change on acceleration.
    return self.state != TurnState.idle

  def presend(self, CS, lateral_active, inputs_valid=True, now=None):
    """Right before the model runs, on inputs newer than the last update()
    saw: is a request about to be offered still wanted? update() computed it
    from the previous frame's car state, so without this a request cancelled
    in between would still go out. Changes nothing but the request: no timer
    moves here, update() still runs once per frame after the model."""
    if not self.enabled or not self.pending:
      return
    reason = self._cancel_reason(CS, lateral_active, inputs_valid)
    if not reason and self._now(now) - self.queued_at > TURN_REQUEST_AGE_MAX:
      reason = "expired"
    if reason:
      self._drop(reason)

  def model_changed(self):
    """The model that would have run the request was replaced before it took
    it. The replacement never heard the question; do not ask it."""
    if self.pending:
      self._drop("model changed")

  def update(self, CS, lateral_active, lane_change_state, inputs_valid=True, *, desire_sent=True, model_changed=False, now=None):
    """Once per model frame, after the model ran. `desire_sent` is the model
    runner's word on the frame that just ran: did it carry a desire pulse to
    the model that drives. `model_changed`: did another model take over."""
    self.desire = log.Desire.none
    if not self.enabled:
      self.reset()
      return

    was_pending, before = self.pending, self.state
    self._step(CS, lateral_active, lane_change_state, inputs_valid)

    if before == TurnState.armed and self.state == TurnState.active:
      # Queued: the next model frame is offered it. presend() checks it again
      # on that frame's inputs before it is packed.
      self.pending, self.offers, self.queued_at = True, 1, self._now(now)
      self.delivery, self.drop_reason = TurnDelivery.queued, ""
      self.desire = self.direction
      return
    if not was_pending:
      return

    # A request was offered to the frame that just ran.
    if self.state != TurnState.active:
      self._drop("cancelled", block=False)   # one of the rules above ended it
    elif desire_sent:
      self.pending, self.delivery = False, TurnDelivery.transmitted
    elif model_changed:
      self._drop("model changed")
    elif self.offers >= TURN_REQUEST_FRAMES_MAX or self._now(now) - self.queued_at > TURN_REQUEST_AGE_MAX:
      self._drop("expired")
    else:
      self.offers += 1
      self.desire = self.direction

  @staticmethod
  def _now(now):
    return time.monotonic() if now is None else now

  def _drop(self, reason, block=True):
    self.pending = False
    self.desire = log.Desire.none
    self.delivery, self.drop_reason = TurnDelivery.dropped, reason
    if block:
      self.state = TurnState.blocked

  def _cancel_reason(self, CS, lateral_active, inputs_valid):
    """Why a queued request must not go out on this car state, or "". The
    same conditions _step() blocks an armed or active turn on."""
    if not CS.leftBlinker and not CS.rightBlinker:
      return "signal off"
    if CS.leftBlinker and CS.rightBlinker:
      return "hazards"
    direction = log.Desire.turnLeft if CS.leftBlinker else log.Desire.turnRight
    if direction != self.direction:
      return "direction changed"
    if not inputs_valid:
      return "inputs invalid"
    if not lateral_active:
      return "lateral inactive"
    if CS.gearShifter != CarState.GearShifter.drive or not math.isfinite(CS.vEgo) or CS.vEgo < 0:
      return "not in drive"
    if CS.leftBlindspot if direction == log.Desire.turnLeft else CS.rightBlindspot:
      return "blindspot"
    if CS.steeringPressed and ((direction == log.Desire.turnLeft and CS.steeringTorque < 0) or
                               (direction == log.Desire.turnRight and CS.steeringTorque > 0)):
      return "driver opposing"
    if CS.vEgo >= TURN_END_SPEED:
      return "speed"
    return ""

  def _step(self, CS, lateral_active, lane_change_state, inputs_valid):

    # A signal already used for a lane change cannot also request a turn if the
    # car slows down. Merely arming a lane change on an approach does not consume
    # it: the driver must have confirmed and started the lane change.
    if lane_change_state == log.LaneChangeState.laneChangeStarting:
      self.lane_change_consumed = True

    if not CS.leftBlinker and not CS.rightBlinker:
      self.off_timer += DT_MDL
      if self.off_timer >= TURN_SIGNAL_OFF_TIME:
        self.reset()
      elif self.consumes_blinker:
        self.state = TurnState.blocked
      return

    self.off_timer = 0.0
    if self.lane_change_consumed:
      return

    if CS.leftBlinker and CS.rightBlinker:
      if self.consumes_blinker or CS.vEgo < TURN_START_SPEED_MAX:
        self.state = TurnState.blocked
      return

    if self.state == TurnState.blocked:
      return

    direction = log.Desire.turnLeft if CS.leftBlinker else log.Desire.turnRight
    usable = inputs_valid and lateral_active and CS.gearShifter == CarState.GearShifter.drive and math.isfinite(CS.vEgo) and CS.vEgo >= 0
    if not usable:
      if self.consumes_blinker:
        self.state = TurnState.blocked
      return

    if self.state == TurnState.idle:
      if lane_change_state != log.LaneChangeState.off or CS.vEgo >= TURN_START_SPEED_MAX:
        return
      self.state = TurnState.armed
      self.direction = direction

    blindspot = CS.leftBlindspot if direction == log.Desire.turnLeft else CS.rightBlindspot
    opposing_driver = CS.steeringPressed and ((direction == log.Desire.turnLeft and CS.steeringTorque < 0) or
                                            (direction == log.Desire.turnRight and CS.steeringTorque > 0))
    if direction != self.direction or blindspot or opposing_driver or CS.vEgo >= TURN_END_SPEED:
      self.state = TurnState.blocked
      return

    if self.state == TurnState.armed:
      self.signal_timer += DT_MDL
      if CS.vEgo >= TURN_START_SPEED_MAX:
        self.state = TurnState.blocked
      elif self.signal_timer >= TURN_SIGNAL_TIME and CS.vEgo >= TURN_START_SPEED_MIN:
        # One request per signal episode; update() queues it. Both stock and
        # Jetlink model runners turn the desire into a rising-edge policy pulse
        # and say whether its frame went (desire_sent). It is asked again only
        # until then, never across a model handover: holding it through one
        # could re-issue the maneuver to a fresh recurrent model.
        self.state = TurnState.active
    elif self.state == TurnState.active:
      self.turn_timer += DT_MDL
      if self.turn_timer >= TURN_TIME_MAX:
        self.state = TurnState.blocked

    # Clearing our desire does NOT erase intent from the recurrent policy. The
    # model decides when its maneuver is finished; disengagement is still the
    # means of cancelling steering assistance.
