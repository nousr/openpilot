"""Lateral-only engagement, both halves in one loop: selfdrived's side (LateralOnly and the state machine, as in
test_lateral_only) and panda's (the compiled Ford safety, through its rx and tx hooks), fed the same car. The
buttons reach selfdrived the way they do in the car: Ford's CarState parses the same message panda is given.

The question is agreement. Whenever openpilot holds itself engaged for steering only, panda must accept its steering
message; whenever openpilot is not engaged, panda's permission must not outlive it for long. Every scenario is run
across how late pandad's heartbeat reports openpilot's state and how soon the driver tries again.

Found by review with panda toggling its permission on each press: after a refused engagement, or one openpilot
ended by itself, the driver's next press left openpilot engaged and panda refusing (188 of these cases). Panda now
grants on every press and holds the grant only while the heartbeat says openpilot is engaged.

Per 100 Hz frame, in the order the car produces it: the car's messages reach panda and carState; selfdrived runs;
card sends LateralMotionControl2 at 20 Hz (steering requested while engaged); pandad sends its heartbeat at 10 Hz,
with what selfdrived said `hb_lag` frames ago, and reports refused messages at 10 Hz; panda's 1 Hz checks run.

Needs a C compiler and cffi (libsafety builds on import); runs on the Mac and on the device.
"""
import unittest

from opendbc.can import CANPacker
from opendbc.car import gen_empty_fingerprint, structs
from opendbc.car.can_definitions import CanData
from opendbc.car.ford import fordcan
from opendbc.car.ford import lateral_only as ford_lateral_only
from opendbc.car.ford.interface import CarInterface
from opendbc.car.ford.values import CAR
from opendbc.safety.tests.libsafety import libsafety_py
from openpilot.selfdrive.selfdrived.tests.test_lateral_only import REAL, EventName, Rig

LMC2 = 0x3D6
HB_EVERY, STEER_EVERY, BUTTON_EVERY, SECOND = 10, 5, 10, 100
PRESS_FRAMES = 20          # a press is held for two button messages


class Car:
  """The driver and the car: what is on the bus this frame."""

  def __init__(self):
    self.cruise = 3          # CcStat_D_Actl: standby
    self.brake = False
    self.lane_until = self.cancel_until = -1
    self.door = False



class Both:
  def __init__(self, hb_lag=0, button_phase=0, speed=3.0):
    CP = CarInterface.get_params(CAR.FORD_MUSTANG_MACH_E_MK1, gen_empty_fingerprint(), [], True, False, False)
    ford_lateral_only.enable(CP)               # the opt-in, as card applies it: car flag and panda's bit together
    self.CI = CarInterface(CP)
    self.CI.update([])
    self.CAN = fordcan.CanBus(CP)
    self.packer = CANPacker("ford_lincoln_base_pt")
    self.safety = libsafety_py.libsafety
    assert self.safety.set_safety_hooks(structs.CarParams.SafetyModel.ford, CP.safetyConfigs[-1].safetyParam) == 0
    self.safety.init_tests()
    self.safety.safety_redundancy_fault = False
    self.host = Rig()
    self.car = Car()
    self.hb_lag, self.button_phase, self.speed = hb_lag, button_phase, speed
    self.frame = 0
    self.enabled_history = [False]
    self.lane_prev = self.cancel_prev = False
    self.refused = []            # frames at which panda refused a steering request from an engaged openpilot
    self.refused_unreported = 0
    self.orphan = 0              # consecutive frames panda's permission stood with openpilot not engaged
    self.longest_orphan = 0
    self.mismatches = 0

  def press(self, button="lane"):
    """The driver presses a button. A press exists on the bus only after the button was seen released there (the
    message is 10 Hz), so this first runs until it was; a faster double press is one press to everybody."""
    while self.lane_prev if button == "lane" else self.cancel_prev:
      self.step()
    if button == "lane":
      self.car.lane_until = self.frame + PRESS_FRAMES
    else:
      self.car.cancel_until = self.frame + PRESS_FRAMES

  def _rx(self, name, values):
    addr, dat, bus = self.packer.make_can_msg(name, 0, values)
    self.safety.safety_rx_hook(libsafety_py.make_CANPacket(addr, bus, dat))

  def step(self, extra=()):
    f, car = self.frame, self.car
    self.safety.set_timer(int(f * 1e4))
    # the car
    self._rx("BrakeSysFeatures", {"Veh_V_ActlBrk": self.speed * 3.6, "VehVActlBrk_D_Qf": 3})
    self._rx("EngVehicleSpThrottle2", {"Veh_V_ActlEng": self.speed * 3.6, "VehVActlEng_D_Qf": 3})
    self._rx("Yaw_Data_FD1", {"VehYaw_W_Actl": 0.0, "VehYawWActl_D_Qf": 3})
    self._rx("EngVehicleSpThrottle", {"ApedPos_Pc_ActlArb": 0})
    self._rx("DesiredTorqBrk", {"VehStop_D_Stat": 0})
    self._rx("EngBrakeData", {"BpedDrvAppl_D_Actl": 2 if car.brake else 1, "CcStat_D_Actl": car.cruise})
    press = release = cancel = cancel_release = False
    if f % BUTTON_EVERY == self.button_phase:
      lane, cncl = f < car.lane_until, f < car.cancel_until
      addr, dat, bus = self.packer.make_can_msg("Steering_Data_FD1", 0, {"TjaButtnOnOffPress": int(lane), "CcAslButtnCnclPress": int(cncl)})
      self.safety.safety_rx_hook(libsafety_py.make_CANPacket(addr, bus, dat))
      seen_by_car = [(str(b.type), b.pressed) for b in self.CI.update([(int(f * 1e7), [CanData(addr, dat, bus)])]).buttonEvents]
      press, release = ("lkas", True) in seen_by_car, ("lkas", False) in seen_by_car
      cancel, cancel_release = ("cancel", True) in seen_by_car, ("cancel", False) in seen_by_car
      assert len(seen_by_car) == press + release + cancel + cancel_release, seen_by_car
      self.lane_prev, self.cancel_prev = lane, cncl
    # selfdrived
    kw = {"cancel": cancel, "cancel_release": cancel_release}
    events = tuple(extra) + ((EventName.doorOpen,) if car.door else ())
    blocked = 0
    if f % HB_EVERY == 0:                      # pandaStates: the refused count reaches selfdrived at 10 Hz
      blocked, self.refused_unreported = self.refused_unreported, 0
    seen = self.host.step(press=press, release=release, brake=car.brake, cruise=car.cruise in (4, 5), available=car.cruise in (3, 4, 5),
                          extra=events, blocked=blocked, **kw)
    self.mismatches += EventName.controlsMismatch in seen and EventName.controlsMismatch not in extra
    self.enabled_history.append(self.host.enabled)
    # card
    if f % STEER_EVERY == 0:
      addr, dat, bus = fordcan.create_lat_ctl2_msg(self.packer, self.CAN, 1 if self.host.enabled else 0, 0., 0., 0., 0., (f // STEER_EVERY) % 16)
      ok = bool(self.safety.safety_tx_hook(libsafety_py.make_CANPacket(addr, bus, dat)))
      if not ok:
        assert self.host.enabled, "a frame without a steering request is always allowed"
        self.refused.append(f)
        self.refused_unreported += 1
    # pandad and panda's clock
    if f % HB_EVERY == 0:
      self.safety.safety_heartbeat(self.enabled_history[max(0, len(self.enabled_history) - 1 - self.hb_lag)])
    if f % SECOND == SECOND - 1:
      self.safety.safety_heartbeat_check()
      self.safety.safety_tick()
    # a permission nobody is using, counted from the request that made it (a new press is a new request)
    self.orphan = 0 if press else self.orphan + 1 if self.safety.get_lateral_only_allowed() and not self.host.enabled else 0
    self.longest_orphan = max(self.longest_orphan, self.orphan)
    self.frame += 1

  def run(self, n, **kw):
    for _ in range(n):
      self.step(**kw)

  @property
  def state(self):
    return self.host.enabled, self.host.lo.on, bool(self.safety.get_lateral_only_allowed())


LAGS = (0, 5, 15, 30)                                # frames between openpilot's state and the heartbeat carrying it
DELAYS = (3, 10, 20, 30, 50, 100, 150, 250, 310, 400)  # frames from the first event to the driver trying again
PHASES = (0, 7)


ORPHAN_MAX = 5 * HB_EVERY + HB_EVERY       # five heartbeats, and up to one more period before the first of them
CASES = [(lag, delay, phase) for lag in LAGS for delay in DELAYS for phase in PHASES]


class TestOpenpilotAndPandaAgree(unittest.TestCase):
  def tearDown(self):
    self.assertFalse(libsafety_py.libsafety.safety_redundancy_fault, "the two safety copies disagreed")

  def each(self, scenario, **more):
    for lag, delay, phase in CASES:
      with self.subTest(hb_lag=lag, retry_after=delay, phase=phase, **more):
        b = Both(hb_lag=lag, button_phase=phase)
        b.run(30)
        scenario(b, delay)
        self.assertLessEqual(b.longest_orphan, ORPHAN_MAX + lag, "panda's permission outlived openpilot's use of it")

  def engaged_and_agreed(self, b, seconds=5):
    """The driver's last press engaged steering only, panda agrees, and it stays that way."""
    b.run(PRESS_FRAMES + 15)
    self.assertEqual(b.state, (True, True, True))
    b.run(seconds * SECOND)
    self.assertEqual(b.state, (True, True, True))
    self.assertEqual(b.refused, [], "panda refused steering openpilot believed it had")
    self.assertEqual(b.mismatches, 0)

  def test_a_plain_press_on_and_off(self):
    def scenario(b, _):
      b.press()
      self.engaged_and_agreed(b)
      b.press()
      b.run(60)
      self.assertEqual(b.state[:2], (False, False))
      b.run(4 * SECOND)
      self.assertEqual(b.state, (False, False, False))
    self.each(scenario)

  def test_refused_then_a_prompt_retry(self):
    # the review's first case: a door open at the press, closed, and the driver presses again
    def scenario(b, delay):
      b.car.door = True
      b.press()
      b.run(PRESS_FRAMES + 5)
      self.assertEqual(b.state[:2], (False, False), "refused")
      b.car.door = False
      b.run(delay)
      b.press()
      self.engaged_and_agreed(b)
    self.each(scenario)

  def test_refused_twice_then_a_retry(self):
    def scenario(b, delay):
      b.car.door = True
      for _ in range(2):
        b.press()
        b.run(PRESS_FRAMES + delay)
      self.assertEqual(b.state[:2], (False, False))
      b.car.door = False
      b.run(delay)
      b.press()
      self.engaged_and_agreed(b)
    self.each(scenario)

  def test_ended_by_openpilot_then_a_prompt_retry(self):
    # the review's second case, and its relatives: openpilot disengages for a reason panda does not see
    for reason in (EventName.buttonCancel, EventName.controlsMismatch):
      def scenario(b, delay, reason=reason):
        b.press()
        self.engaged_and_agreed(b, seconds=1)
        b.step(extra=(reason,))
        self.assertEqual(b.state[:2], (False, False))
        b.run(delay)
        b.press()
        self.engaged_and_agreed(b)
      self.each(scenario, reason=str(reason))

  def test_off_and_straight_back_on(self):
    def scenario(b, delay):
      b.press()
      self.engaged_and_agreed(b, seconds=1)
      b.press()
      b.run(PRESS_FRAMES + delay)
      self.assertEqual(b.state[:2], (False, False))
      b.press()
      self.engaged_and_agreed(b)
    self.each(scenario)

  def test_the_cancel_button_ends_it_on_both_sides_at_once(self):
    def scenario(b, delay):
      b.press()
      self.engaged_and_agreed(b, seconds=1)
      b.press("cancel")
      while not b.cancel_prev:
        self.assertEqual(b.state, (True, True, True))
        b.step()
      self.assertEqual(b.state, (False, False, False), "in the frame the cancel message arrived")
      while b.cancel_prev:                     # the driver lets go of cancel
        b.step()
      b.run(delay)
      b.press()
      self.engaged_and_agreed(b)
    self.each(scenario)

  def test_lane_centering_pressed_with_cancel_still_down_is_taken_by_neither(self):
    def scenario(b, delay):
      b.press()
      self.engaged_and_agreed(b, seconds=1)
      b.press("cancel")
      b.car.cancel_until = b.frame + PRESS_FRAMES + delay + 40      # held on
      b.run(12)
      self.assertEqual(b.state, (False, False, False))
      b.press()                                # lane centering, while cancel is down
      b.run(PRESS_FRAMES + delay)
      self.assertEqual(b.state, (False, False, False))
      b.run(60)                                # both buttons released by now
      self.assertEqual(b.state, (False, False, False), "and letting go of cancel is not a request")
      b.press()
      self.engaged_and_agreed(b)
    self.each(scenario)

  def test_cruise_switched_off_ends_it_on_both_sides_at_once(self):
    def scenario(b, delay):
      b.press()
      self.engaged_and_agreed(b, seconds=1)
      b.car.cruise = 0
      b.step()
      self.assertEqual(b.state, (False, False, False))
      b.run(delay)
      b.press()
      b.run(PRESS_FRAMES + 20)
      self.assertEqual(b.state, (False, False, False), "no request is taken with cruise off, by either")
      b.car.cruise = 3
      b.run(delay)
      b.press()
      self.engaged_and_agreed(b)
    self.each(scenario)

  def test_a_heartbeat_later_than_the_allowance_fails_safe(self):
    # openpilot's state reaching panda 0.8 s late is outside what the count allows for. Then panda lets go of a
    # request openpilot did take up, and openpilot must notice and disengage, not carry on believing it steers.
    for phase in PHASES:
      with self.subTest(phase=phase):
        b = Both(hb_lag=80, button_phase=phase)
        b.run(30)
        b.press()
        b.run(3 * SECOND)
        self.assertEqual(b.state, (False, False, False))
        self.assertGreaterEqual(b.mismatches, 1)
        self.assertLessEqual(len(b.refused), 12, "refused frames before openpilot gave up: about half a second's worth")

  def test_a_pressed_pedal_changes_nothing_between_them(self):
    def scenario(b, delay):
      b.car.brake = True
      b.press()
      self.engaged_and_agreed(b, seconds=1)
      b.car.brake = False
      b.run(delay)
      b.car.brake = True
      self.engaged_and_agreed(b, seconds=2)
    self.each(scenario)

  def test_engaged_with_acc_then_a_press_for_steering_only(self):
    # ACC on, panda's ordinary permission; the press turns it into steering only and the car's cruise drops out
    def scenario(b, delay):
      b.car.cruise = 5
      b.run(20)
      self.assertEqual(b.state, (True, False, False))
      b.press()
      b.run(min(delay, 30))                    # ACC takes this long to act on openpilot's cancel
      b.car.cruise = 3
      self.engaged_and_agreed(b)
      b.car.brake = True                       # and now the brake ends nothing
      self.engaged_and_agreed(b, seconds=1)
    self.each(scenario)

  def test_engaged_with_acc_braked_out_then_steering_only(self):
    def scenario(b, delay):
      b.car.cruise = 5
      b.run(20)
      self.assertEqual(b.state[:2], (True, False))
      b.car.brake, b.car.cruise = True, 3
      b.run(delay)
      self.assertEqual(b.state[:2], (False, False))
      b.press()
      self.engaged_and_agreed(b)
    self.each(scenario)


if __name__ == "__main__":
  print("selfdrived's own Events and StateMachine:", REAL)
  unittest.main()
