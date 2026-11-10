"""Lateral-only engagement, driven in selfdrived's own order: the events of a frame, LateralOnly.update_events, the
state machine, LateralOnly.update_state.

Where selfdrived's Events and StateMachine import (the device, a built checkout) these tests use them. Where they do
not (a Mac without the built message library) they use the stand-ins below, which carry the same rules for the event
types used here; REAL says which, and the device run is the one that counts for the state machine.
"""
import itertools
import unittest
from pathlib import Path
from types import SimpleNamespace

from opendbc.car import structs
from opendbc.car.ford.values import FordFlags, FordSafetyFlags
from openpilot.cereal import log
from openpilot.selfdrive.selfdrived import lateral_only
from openpilot.selfdrive.selfdrived.lateral_only import ANNOUNCE, BLOCKED_FRAMES, BLOCKED_WINDOW, LateralOnly, cruise_control

EventName = log.OnroadEvent.EventName
ButtonType = structs.CarState.ButtonEvent.Type
DT = 0.01

try:
  from openpilot.selfdrive.selfdrived.events import ET, EVENTS, Events
  from openpilot.selfdrive.selfdrived.state import StateMachine
  REAL = True
except Exception:   # the message library is not built here
  REAL = False

  class ET:
    ENABLE, NO_ENTRY, USER_DISABLE, IMMEDIATE_DISABLE, SOFT_DISABLE, WARNING = 'enable', 'noEntry', 'userDisable', 'immediateDisable', 'softDisable', 'warning'

  EVENTS = {
    EventName.buttonEnable: {ET.ENABLE}, EventName.pcmEnable: {ET.ENABLE},
    EventName.buttonCancel: {ET.USER_DISABLE, ET.NO_ENTRY}, EventName.pedalPressed: {ET.USER_DISABLE, ET.NO_ENTRY},
    EventName.pcmDisable: {ET.USER_DISABLE}, EventName.wrongCarMode: {ET.USER_DISABLE, ET.NO_ENTRY},
    EventName.controlsMismatch: {ET.IMMEDIATE_DISABLE, ET.NO_ENTRY}, EventName.doorOpen: {ET.SOFT_DISABLE, ET.NO_ENTRY},
    EventName.steeringOnly: {ET.WARNING},
  }

  class Events:
    def __init__(self):
      self.events = []

    @property
    def names(self):
      return self.events

    def add(self, name):
      self.events = sorted(self.events + [name])

    def clear(self):
      self.events = []

    def contains(self, event_type):
      return any(event_type in EVENTS.get(e, ()) for e in self.events)

  class StateMachine:
    SOFT_FRAMES = 300

    def __init__(self):
      self.state, self.timer = 'disabled', 0

    def update(self, events):
      self.timer = max(0, self.timer - 1)
      if self.state != 'disabled':
        if events.contains(ET.IMMEDIATE_DISABLE) or events.contains(ET.USER_DISABLE):
          self.state = 'disabled'
        elif self.state == 'enabled' and events.contains(ET.SOFT_DISABLE):
          self.state, self.timer = 'softDisabling', self.SOFT_FRAMES
        elif self.state == 'softDisabling':
          if not events.contains(ET.SOFT_DISABLE):
            self.state = 'enabled'
          elif self.timer <= 0:
            self.state = 'disabled'
      elif events.contains(ET.ENABLE) and not events.contains(ET.NO_ENTRY):
        self.state = 'enabled'
      return self.state != 'disabled', self.state != 'disabled'


def car_params(opted_in=True, brand="ford", long=True, pcm=True):
  flags = FordFlags.CANFD | (FordFlags.LAT_ONLY if opted_in else 0)
  return SimpleNamespace(brand=brand, flags=int(flags), openpilotLongitudinalControl=long, pcmCruise=pcm)


class Rig:
  """One selfdrived, as far as engagement goes. The car events of a frame are made by selfdrived's and CarEvents'
  own rules from the car state given: pcmEnable / pcmDisable from the cruise state, pedalPressed from the pedals,
  wrongCarMode from cruise being switched off."""

  def __init__(self, CP=None):
    self.CP = CP or car_params()
    self.lo = LateralOnly(self.CP)
    self.events, self.sm = Events(), StateMachine()
    self.enabled = False
    self.frame = 0
    self.prev = SimpleNamespace(brake=False, gas=False, cruise=False)
    self.blocked = 0
    self.log = []

  def step(self, press=False, release=False, brake=False, gas=False, cruise=False, available=True, standstill=False, extra=(), blocked=0):
    self.frame += 1
    t = self.frame * DT
    self.blocked += blocked
    buttons = [SimpleNamespace(type=ButtonType.lkas, pressed=True)] if press else []
    buttons += [SimpleNamespace(type=ButtonType.lkas, pressed=False)] if release else []
    CS = SimpleNamespace(buttonEvents=buttons)
    self.events.clear()
    # CarEvents
    if not available:
      self.events.add(EventName.wrongCarMode)
    if cruise and not self.prev.cruise:
      self.events.add(EventName.pcmEnable)
    elif not cruise:
      self.events.add(EventName.pcmDisable)
    # selfdrived: rising edge of either pedal, and the brake whenever moving
    if (gas and not self.prev.gas) or (brake and (not self.prev.brake or not standstill)):
      self.events.add(EventName.pedalPressed)
    for e in extra:
      self.events.add(e)
    self.lo.update_events(CS, self.events, self.enabled, self.blocked, t)
    seen = list(self.events.names)
    self.enabled, _ = self.sm.update(self.events)
    self.lo.update_state(self.enabled, t)
    self.prev = SimpleNamespace(brake=brake, gas=gas, cruise=cruise)
    self.log.append(seen)
    return seen

  def run(self, n, **kw):
    for _ in range(n):
      self.step(**kw)

  @property
  def state(self):
    return self.enabled, self.lo.on


class TestLateralOnly(unittest.TestCase):
  def setUp(self):
    self.rig = Rig()
    self.rig.run(20)
    self.assertEqual(self.rig.state, (False, False))

  def enter(self, **kw):
    self.rig.step(press=True, **kw)
    self.assertEqual(self.rig.state, (True, True))
    self.rig.step(release=True, **kw)
    self.assertEqual(self.rig.state, (True, True))

  def test_not_opted_in_the_button_does_nothing(self):
    for CP in (car_params(opted_in=False), car_params(brand="toyota")):
      rig = Rig(CP)
      self.assertFalse(rig.lo.available)
      for kw in ({}, {"brake": True}, {"cruise": True}):
        before = rig.state
        seen = rig.step(press=True, **kw)
        self.assertNotIn(EventName.buttonEnable, seen)
        self.assertNotIn(EventName.buttonCancel, seen)
        self.assertEqual(rig.lo.on, False)
        self.assertEqual(rig.enabled, before[0] or kw.get("cruise", False))

  def test_a_press_enters_and_the_pedals_do_not_end_it(self):
    self.enter()
    for kw in ({"brake": True}, {"brake": True, "standstill": True}, {}, {"gas": True}, {"gas": True, "brake": True}, {}):
      self.rig.run(30, **kw)
      self.assertEqual(self.rig.state, (True, True), kw)

  def test_entry_with_a_pedal_down(self):
    for kw in ({"brake": True}, {"brake": True, "standstill": True}, {"gas": True}):
      with self.subTest(kw=kw):
        self.setUp()
        self.rig.run(5, **kw)
        self.enter(**kw)

  def test_the_next_press_ends_it_and_stock_rules_are_back(self):
    self.enter()
    self.rig.run(10)
    self.rig.step(press=True)
    self.assertEqual(self.rig.state, (False, False))
    self.rig.step(release=True)
    self.assertEqual(self.rig.state, (False, False))
    # engaged with ACC now: the brake disengages, as it always did
    self.rig.run(5, cruise=True)
    self.assertEqual(self.rig.state, (True, False))
    self.rig.step(cruise=True, brake=True)
    self.assertEqual(self.rig.state, (False, False))

  def test_a_release_is_not_a_press(self):
    self.rig.step(release=True)
    self.assertEqual(self.rig.state, (False, False))
    self.enter()
    self.rig.run(3, release=True)
    self.assertEqual(self.rig.state, (True, True))

  def test_what_refuses_an_engagement_refuses_this_one(self):
    for kw in ({"available": False}, {"extra": (EventName.doorOpen,)}, {"extra": (EventName.controlsMismatch,)}):
      with self.subTest(kw=kw):
        self.setUp()
        self.rig.step(press=True, **kw)
        self.assertEqual(self.rig.state, (False, False))
        self.assertFalse(self.rig.lo.requested)
        self.rig.run(50)                       # the reason gone: the old press does not engage later
        self.assertEqual(self.rig.state, (False, False))

  def test_what_ends_an_engagement_ends_this_one(self):
    for kw, frames in (({"available": False}, 1), ({"extra": (EventName.controlsMismatch,)}, 1), ({"extra": (EventName.buttonCancel,)}, 1)):
      with self.subTest(kw=kw):
        self.setUp()
        self.enter()
        self.rig.run(frames, **kw)
        self.assertEqual(self.rig.state, (False, False))
        self.rig.run(20)
        self.assertEqual(self.rig.state, (False, False), "and it does not come back by itself")

  def test_a_soft_disable_runs_its_course(self):
    self.enter()
    self.rig.run(100, extra=(EventName.doorOpen,))
    self.assertEqual(self.rig.state, (True, True), "soft disabling: still steering, alerting")
    self.rig.run(10)
    self.assertEqual(self.rig.state, (True, True), "the reason went away in time")
    self.rig.run(400, extra=(EventName.doorOpen,))
    self.assertEqual(self.rig.state, (False, False))

  def test_engaged_with_acc_a_press_keeps_steering_and_cancels_acc(self):
    self.rig.run(5, cruise=True)
    self.assertEqual(self.rig.state, (True, False))
    self.rig.step(press=True, cruise=True)
    self.assertEqual(self.rig.state, (True, True))
    self.assertEqual(cruise_control(True, self.rig.lo.on, False, True, False, False, self.rig.CP), (False, False, True, False))
    self.rig.run(5, cruise=True)               # until the car has cancelled
    self.rig.run(50, brake=True)
    self.assertEqual(self.rig.state, (True, True))

  def test_acc_set_while_steering_only_is_cancelled_not_adopted(self):
    self.enter()
    self.rig.run(20, cruise=True)
    self.assertEqual(self.rig.state, (True, True))
    long_active, override, cancel, resume = cruise_control(True, True, False, True, True, False, self.rig.CP)
    self.assertEqual((long_active, override, cancel, resume), (False, False, True, False))

  def test_panda_refusing_messages_is_a_mismatch(self):
    def blocked_run(per_frame_every, frames):
      self.setUp()
      self.rig.blocked = 37                    # refused before entry: not this state's business
      self.enter()
      for i in range(frames):
        self.rig.step(blocked=1 if i % per_frame_every == 0 else 0)
        if not self.rig.enabled:
          return i
      return None
    self.assertIsNone(blocked_run(10 ** 6, 300), "one refused frame")
    self.assertIsNotNone(blocked_run(5, 300), "every steering frame refused (20 Hz)")
    self.assertLessEqual(blocked_run(5, 300), 5 * BLOCKED_FRAMES)
    slow = int(BLOCKED_WINDOW / DT / (BLOCKED_FRAMES - 1)) + 1
    self.assertIsNone(blocked_run(slow, 1000), "fewer than the limit in any window")
    # the count restarting (panda reset) is not a refusal, and refusals after it are still seen
    self.setUp()
    self.rig.blocked = 1000
    self.enter()
    self.rig.blocked = 0
    self.rig.run(50)
    self.assertEqual(self.rig.state, (True, True))
    self.rig.run(5 * BLOCKED_FRAMES + 5, blocked=1)
    self.assertEqual(self.rig.state, (False, False))

  def test_refusals_between_two_engagements_are_not_held_against_the_second(self):
    self.enter()
    self.rig.run(20)
    self.rig.step(press=True)                  # off
    self.rig.step(release=True, blocked=40)    # whatever panda refused while disengaged
    self.enter()                               # on again inside the window
    self.rig.run(int(2 * BLOCKED_WINDOW / DT))
    self.assertEqual(self.rig.state, (True, True))

  def test_the_notice_shows_after_entry_and_goes(self):
    self.enter()
    seen = [EventName.steeringOnly in self.rig.step() for _ in range(int(ANNOUNCE / DT) + 50)]
    self.assertTrue(all(seen[:int(ANNOUNCE / DT) - 5]))
    self.assertFalse(any(seen[int(ANNOUNCE / DT):]))

  def test_the_pedal_events_are_dropped_only_in_this_state(self):
    seen = self.rig.step(brake=True)
    self.assertIn(EventName.pedalPressed, seen)
    self.assertIn(EventName.pcmDisable, seen)
    self.enter()
    seen = self.rig.step(brake=True)
    self.assertNotIn(EventName.pedalPressed, seen)
    self.assertNotIn(EventName.pcmDisable, seen)


class TestCruiseControl(unittest.TestCase):
  def test_without_lateral_only_it_is_controlsds_own_logic(self):
    for long, pcm in itertools.product((True, False), repeat=2):
      CP = car_params(long=long, pcm=pcm)
      for enabled, override, cruise, standstill, stop in itertools.product((True, False), repeat=5):
        long_active = enabled and not override and CP.openpilotLongitudinalControl
        expected = (long_active, enabled and not long_active and CP.openpilotLongitudinalControl,
                    cruise and (not enabled or not CP.pcmCruise), enabled and standstill and not stop)
        self.assertEqual(cruise_control(enabled, False, override, cruise, standstill, stop, CP), expected)

  def test_steering_only_commands_nothing_and_cancels_acc(self):
    for long, pcm in itertools.product((True, False), repeat=2):
      CP = car_params(long=long, pcm=pcm)
      for override, cruise, standstill, stop in itertools.product((True, False), repeat=4):
        self.assertEqual(cruise_control(True, True, override, cruise, standstill, stop, CP), (False, False, cruise, False))


class TestSetup(unittest.TestCase):
  class P:
    def __init__(self, on):
      self.on = on

    def get_bool(self, key):
      assert key == "FordLateralOnly"
      return self.on

  def CP(self, brand="ford", canfd=True):
    return SimpleNamespace(brand=brand, flags=int(FordFlags.CANFD) if canfd else 0, safetyConfigs=[SimpleNamespace(safetyParam=3)])

  def test_off_by_default_and_only_on_a_can_fd_ford(self):
    cases = ((False, "ford", True, False), (True, "ford", True, True), (True, "ford", False, False), (True, "toyota", True, False))
    for on, brand, canfd, expect in cases:
      with self.subTest(on=on, brand=brand, canfd=canfd):
        CP, events = self.CP(brand, canfd), []

        def event(*a, _events=events, **kw):
          _events.append(kw)
        self.assertEqual(lateral_only.setup(self.P(on), CP, event), expect)
        self.assertEqual(CP.safetyConfigs[-1].safetyParam, 3 | (FordSafetyFlags.LAT_ONLY if expect else 0))
        self.assertEqual(LateralOnly(CP).available, expect)
        self.assertEqual([e["opted_in"] for e in events], [expect] if on else [])


class TestSelfdrivedCallsItInOrder(unittest.TestCase):
  """selfdrived and controlsd only run on the device; this holds their source to what the tests above assume."""

  def setUp(self):
    self.src = (Path(__file__).resolve().parents[1] / "selfdrived.py").read_text()
    self.controlsd = (Path(__file__).resolve().parents[2] / "controls/controlsd.py").read_text()

  def test_controlsd_takes_all_four_from_cruise_control(self):
    self.assertIn("CC.longActive = self.cruise_control(CC, CS)[0]", self.controlsd)
    self.assertIn("_, CC.cruiseControl.override, CC.cruiseControl.cancel, CC.cruiseControl.resume = self.cruise_control(CC, CS)", self.controlsd)
    for old in ("CC.longActive = CC.enabled", "CC.cruiseControl.cancel = CS.cruiseState.enabled"):
      self.assertNotIn(old, self.controlsd)

  def order(self, *parts, within=None):
    s = self.src if within is None else self.src[self.src.index(within):]
    at = -1
    for part in parts:
      nxt = s.find(part, at + 1)
      self.assertGreater(nxt, at, part)
      at = nxt

  def test_events_then_lateral_only_then_the_state_machine(self):
    self.order("def update_events", "self.events.clear()", "self.car_events.update(", "EventName.pedalPressed",
               "self.lateral_only.update_events(", "def data_sample")
    self.order("self.update_events(CS)", "self.state_machine.update(self.events)", "self.lateral_only.update_state(",
               "self.update_alerts(CS)", within="def step(self)")
    self.assertEqual(self.src.count("self.lateral_only.update_events("), 1)
    self.assertNotIn("return", self.src[self.src.index("self.lateral_only.update_events("):self.src.index("def data_sample")])

  def test_the_panda_comparison_and_the_published_bit(self):
    self.assertIn("if self.enabled and not self.lateral_only.on and any(not ps.controlsAllowed", self.src)
    self.assertIn("ss.lateralOnly = self.enabled and self.lateral_only.on", self.src)


if __name__ == "__main__":
  unittest.main()
