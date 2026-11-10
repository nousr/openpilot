"""Opt-in intersection intent. This selects a policy input, not a steering command."""
from enum import StrEnum
import math

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


class TurnState(StrEnum):
  idle = "idle"
  armed = "armed"
  active = "active"
  blocked = "blocked"


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

  @property
  def consumes_blinker(self):
    # Never convert a turn's still-held signal into a lane change on acceleration.
    return self.state != TurnState.idle

  def update(self, CS, lateral_active, lane_change_state, inputs_valid=True):
    self.desire = log.Desire.none
    if not self.enabled:
      self.reset()
      return

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
        self.state = TurnState.active
        # Exactly one frame. Both stock and Jetlink model runners turn this into
        # a rising-edge policy pulse. Holding it through a model handover could
        # re-issue the maneuver to a fresh recurrent model.
        self.desire = self.direction
    elif self.state == TurnState.active:
      self.turn_timer += DT_MDL
      if self.turn_timer >= TURN_TIME_MAX:
        self.state = TurnState.blocked

    # Clearing our desire does NOT erase intent from the recurrent policy. The
    # model decides when its maneuver is finished; disengagement is still the
    # means of cancelling steering assistance.
