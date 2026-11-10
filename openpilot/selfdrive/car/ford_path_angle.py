"""Host side of opendbc's Ford low-speed path angle test (opendbc/car/ford/path_angle.py).

Nothing here steers. It reads one param when card starts and, only if that param holds a valid list of profiles on a
CAN FD Ford, opts the car in and arms them. The driver starts each run with the ACC distance button; see the opendbc
module for what a run is and what ends it.

FordPathAngleTest is cleared when the manager starts and when the car goes offroad, so it arms one drive and has to
be set again, on purpose, for the next. Format, levels in rad, positive left, one run per level:

    0.10,-0.10,0.20,-0.20              defaults: hold 2.0 s, rise 0.5 rad/s, fall 0.5 rad/s
    0.30,-0.30;hold=3;rise=0.25;fall=0.5

Opting in sets a panda safety param bit that only a debug panda build with the matching opendbc honours. This file
does not change what firmware the panda runs.
"""
from opendbc.car.ford import path_angle
from opendbc.car.ford.values import FordFlags

PARAM = "FordPathAngleTest"
MAX_PROFILES = 24


def parse(text: str) -> list[path_angle.Profile]:
  """The profiles a param value asks for. Raises ValueError on anything it does not fully understand."""
  levels, *options = (part.strip() for part in text.strip().split(";"))
  kw = {}
  for option in options:
    name, _, value = option.partition("=")
    if name.strip() not in ("hold", "rise", "fall") or name.strip() in kw:
      raise ValueError(f"unknown or repeated option: {option!r}")
    kw[name.strip()] = float(value)
  profiles = [path_angle.Profile(float(level), **kw) for level in levels.split(",")]
  if not 0 < len(profiles) <= MAX_PROFILES:
    raise ValueError(f"between 1 and {MAX_PROFILES} profiles")
  return profiles


def setup(params, CP, CC, event) -> bool:
  """Opt in and arm, if the param asks for it and everything about it is in order. Returns whether it did.
  Call before CarParams is written, so panda gets the matching safety param."""
  raw = params.get(PARAM)
  if not raw:
    return False
  text = raw.decode() if isinstance(raw, bytes) else str(raw)
  try:
    if CP.brand != "ford" or not CP.flags & FordFlags.CANFD or CC is None:
      raise ValueError("not a controllable CAN FD Ford")
    profiles = parse(text)
    path_angle.enable(CP)
    CC.path_angle_test.arm(profiles)
  except Exception as e:
    # a test that cannot be set up exactly as asked is not set up at all
    event("ford_path_angle_test", armed=False, param=text, error=str(e))
    return False
  event("ford_path_angle_test", armed=True, param=text, levels=[p.level for p in profiles], hold=profiles[0].hold,
        rise=profiles[0].rise, fall=profiles[0].fall, safety_param=CP.safetyConfigs[-1].safetyParam)
  return True


class StageLog:
  """Logs every change of the test's stage, with what it was asking for and why the last run ended."""

  def __init__(self, CC, event):
    self.test = getattr(CC, "path_angle_test", None)
    self.event = event
    self.last = None

  def update(self, CS) -> None:
    if self.test is None or not self.test.armed:
      return
    now = (str(self.test.stage), self.test.index, self.test.ended)
    if now != self.last:
      profile = self.test.profile
      self.event("ford_path_angle_test", stage=now[0], run=self.test.runs, index=now[1], ended=now[2],
                 level=profile.level if profile is not None else None, v_ego=CS.vEgo, steering_angle_deg=CS.steeringAngleDeg)
      self.last = now
