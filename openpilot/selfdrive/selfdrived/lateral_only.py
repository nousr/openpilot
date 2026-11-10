"""Lateral-only engagement: steering without ACC, the pedals the driver's own (CAN FD Ford, opt-in).

What the driver does
  Cruise switched on (standby is enough). The lane centering button on the wheel:
    disengaged          -> steering only. Entry is refused by everything that refuses a normal engagement,
                           except a pressed pedal.
    steering only       -> disengaged.
    engaged with ACC    -> steering only: ACC is cancelled, steering carries on.
  In steering only, the brake and the accelerator do not disengage, and openpilot commands no acceleration or
  braking. If ACC becomes engaged it is cancelled; to drive with ACC, press the button off and set cruise as usual.
  Everything else ends it exactly as it ends a normal engagement: cruise switched off, a door, the belt, the gear,
  driver monitoring, a steering fault, the Jetlink guard, a panda fault. Taking the wheel overrides, as engaged.

How it is built
  It is the ordinary `enabled` state of selfdrived's state machine with one extra bit, `selfdriveState.lateralOnly`.
  So driver monitoring, the Jetlink guard (which is told `enabled`), the panda heartbeat and the UI treat it as
  engaged without knowing about it. This module does three things to the events of a frame before the state machine
  sees them: asks for entry or exit on the button, drops the two events that mean "the driver took the pedals"
  (pedalPressed, pcmDisable), and watches panda.

Panda
  Panda reads the same button off the bus and keeps its own permission (opendbc safety/modes/ford.h). It is not in
  panda's health packet, so agreement is checked by what panda does: if it refuses BLOCKED_FRAMES messages within
  BLOCKED_WINDOW seconds while steering only is on, the two disagree and this disengages (controlsMismatch).
  The usual controlsAllowed comparison is skipped in this state: panda's controls_allowed is false by design.

Nothing here runs unless the car was opted in when card started (FordLateralOnly, off by default), which also gives
panda the matching safety param.
"""
from collections import deque

from opendbc.car import structs
from opendbc.car.ford import lateral_only as ford_lateral_only
from openpilot.cereal import log

EventName = log.OnroadEvent.EventName
ButtonType = structs.CarState.ButtonEvent.Type

PARAM = "FordLateralOnly"
IGNORED = (EventName.pedalPressed, EventName.pcmDisable)
BLOCKED_FRAMES = 5      # messages panda refused...
BLOCKED_WINDOW = 1.0    # ...within this many seconds: panda does not agree that steering is allowed
ANNOUNCE = 3.0          # seconds the "Steering Only" notice shows after entry


def setup(params, CP, event) -> bool:
  """Opt the car in if the owner's setting asks for it. Call in card before CarParams is written."""
  if not params.get_bool(PARAM):
    return False
  try:
    if CP.brand != "ford":
      raise ValueError("not a Ford")
    ford_lateral_only.enable(CP)
  except Exception as e:
    event("lateral_only", opted_in=False, error=str(e))
    return False
  event("lateral_only", opted_in=True, safety_param=CP.safetyConfigs[-1].safetyParam)
  return True


class LateralOnly:
  def __init__(self, CP):
    self.available = ford_lateral_only.enabled(CP)
    self.on = False            # enabled, steering only
    self.requested = False     # this frame asks the state machine to enter steering only
    self.since = 0.
    self.reason = ""           # why steering only last ended, for the log
    self._blocked: deque[tuple[float, int]] = deque()

  def update_events(self, CS, events, enabled: bool, tx_blocked: int, t: float) -> None:
    """Once per frame, after every other event of the frame was added and before the state machine runs."""
    self.requested = False
    if not self.available:
      return
    if not enabled:
      self.on = False

    if any(be.type == ButtonType.lkas and be.pressed for be in CS.buttonEvents):
      if not enabled:
        self.requested = True
        events.add(EventName.buttonEnable)
      elif self.on:
        events.add(EventName.buttonCancel)
      else:
        self._enter(t)         # engaged with ACC: steering carries on, controlsd cancels ACC

    if self.on or self.requested:
      events.events = [e for e in events.events if e not in IGNORED]

    if self.on:
      self._blocked.append((t, tx_blocked))
      while self._blocked[0][0] < t - BLOCKED_WINDOW:
        self._blocked.popleft()
      if tx_blocked < self._blocked[0][1]:
        self._blocked.clear()  # panda's counter restarted
      elif tx_blocked - self._blocked[0][1] >= BLOCKED_FRAMES:
        events.add(EventName.controlsMismatch)
      if t - self.since < ANNOUNCE:
        events.add(EventName.steeringOnly)

  def update_state(self, enabled: bool, t: float) -> None:
    """After the state machine ran."""
    if self.requested and enabled:
      self._enter(t)
    elif not enabled:
      self.on = False
    self.requested = False

  def _enter(self, t: float) -> None:
    self.on, self.since = True, t
    self._blocked.clear()


def cruise_control(enabled: bool, lateral_only: bool, override_longitudinal: bool, cruise_enabled: bool, cruise_standstill: bool,
                   should_stop: bool, CP) -> tuple[bool, bool, bool, bool]:
  """What controlsd may do about speed: (longActive, cruise override, cruise cancel, cruise resume).
  With lateral_only False these are controlsd's own expressions. With it True there is no longitudinal control, and
  an engaged ACC is cancelled, as it is when openpilot is not engaged."""
  long_active = enabled and not lateral_only and not override_longitudinal and CP.openpilotLongitudinalControl
  override = enabled and not lateral_only and not long_active and CP.openpilotLongitudinalControl
  cancel = cruise_enabled and (not enabled or lateral_only or not CP.pcmCruise)
  resume = enabled and not lateral_only and cruise_standstill and not should_stop
  return long_active, override, cancel, resume
