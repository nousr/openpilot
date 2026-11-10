import unittest

from opendbc.car import gen_empty_fingerprint, structs
from opendbc.car.ford.interface import CarInterface
from opendbc.car.ford.path_angle import Stage
from opendbc.car.ford.values import CAR, FordFlags, FordSafetyFlags
from openpilot.selfdrive.car import ford_path_angle


class Params(dict):
  def get(self, key):
    return dict.get(self, key)


def mach_e():
  CP = CarInterface.get_params(CAR.FORD_MUSTANG_MACH_E_MK1, gen_empty_fingerprint(), [], True, False, False)
  return CP, CarInterface(CP)


class TestFordPathAngleHost(unittest.TestCase):
  def setUp(self):
    self.events = []
    self.event = lambda name, **kw: self.events.append((name, kw))

  def test_nothing_without_the_param(self):
    for value in (None, "", b""):
      CP, CI = mach_e()
      before = (CP.flags, CP.safetyConfigs[-1].safetyParam)
      self.assertFalse(ford_path_angle.setup(Params({ford_path_angle.PARAM: value} if value is not None else {}), CP, CI.CC, self.event))
      self.assertEqual((CP.flags, CP.safetyConfigs[-1].safetyParam), before)
      self.assertEqual(CI.CC.path_angle_test.stage, Stage.idle)
    self.assertEqual(self.events, [])

  def test_a_valid_param_opts_in_and_arms(self):
    for value in ("0.10,-0.10,0.20,-0.20", b"0.3, -0.3 ; hold=3 ; rise=0.25;fall=1.0"):
      CP, CI = mach_e()
      self.assertTrue(ford_path_angle.setup(Params({ford_path_angle.PARAM: value}), CP, CI.CC, self.event))
      self.assertTrue(CP.flags & FordFlags.PATH_ANGLE)
      self.assertTrue(CP.safetyConfigs[-1].safetyParam & FordSafetyFlags.PATH_ANGLE)
      self.assertEqual(CI.CC.path_angle_test.stage, Stage.armed)
      self.assertTrue(self.events[-1][1]["armed"])
    self.assertEqual([p.level for p in CI.CC.path_angle_test.profiles], [0.3, -0.3])
    self.assertEqual((CI.CC.path_angle_test.profiles[0].hold, CI.CC.path_angle_test.profiles[0].rise, CI.CC.path_angle_test.profiles[0].fall), (3.0, 0.25, 1.0))

  def test_anything_not_fully_understood_arms_nothing(self):
    for value in ("0.6", "0.1,,0.2", "left", "0.1;speed=3", "0.1;hold=2;hold=3", "0.1;rise=9", "0", "0.1;hold", ",".join(["0.1"] * 25), "0.1 0.2"):
      with self.subTest(value=value):
        CP, CI = mach_e()
        before = (CP.flags, CP.safetyConfigs[-1].safetyParam)
        self.assertFalse(ford_path_angle.setup(Params({ford_path_angle.PARAM: value}), CP, CI.CC, self.event))
        self.assertEqual((CP.flags, CP.safetyConfigs[-1].safetyParam), before, "not opted in either")
        self.assertEqual(CI.CC.path_angle_test.stage, Stage.idle)
        self.assertFalse(self.events[-1][1]["armed"])

  def test_only_a_controllable_can_fd_ford(self):
    CP, CI = mach_e()
    CP.brand = "toyota"
    self.assertFalse(ford_path_angle.setup(Params({ford_path_angle.PARAM: "0.1"}), CP, CI.CC, self.event))
    self.assertFalse(CP.flags & FordFlags.PATH_ANGLE)
    CP = CarInterface.get_non_essential_params(CAR.FORD_FOCUS_MK4)
    before = (CP.flags, CP.safetyConfigs[-1].safetyParam)
    self.assertFalse(ford_path_angle.setup(Params({ford_path_angle.PARAM: "0.1"}), CP, CarInterface(CP).CC, self.event))
    self.assertEqual((CP.flags, CP.safetyConfigs[-1].safetyParam), before)
    CP, _ = mach_e()
    self.assertFalse(ford_path_angle.setup(Params({ford_path_angle.PARAM: "0.1"}), CP, None, self.event))

  def test_stage_changes_are_logged_once_each(self):
    CP, CI = mach_e()
    ford_path_angle.setup(Params({ford_path_angle.PARAM: "0.1"}), CP, CI.CC, self.event)
    log = ford_path_angle.StageLog(CI.CC, self.event)
    cs = structs.CarState(vEgo=2.0, vEgoRaw=2.0, gearShifter=structs.CarState.GearShifter.drive)
    test = CI.CC.path_angle_test
    press = [structs.CarState.ButtonEvent(type=structs.CarState.ButtonEvent.Type.gapAdjustCruise, pressed=True)]
    self.events.clear()
    for i in range(200):
      if i == 20:
        test.buttons(press)
      test.update(cs, True)
      log.update(cs)
    self.assertEqual([kw["stage"] for _, kw in self.events], ["armed", "rise", "hold", "fall", "done"])
    self.assertEqual(self.events[-1][1]["ended"], "completed")
    quiet = ford_path_angle.StageLog(mach_e()[1].CC, self.event)
    quiet.update(cs)
    self.assertEqual(len(self.events), 5, "nothing is logged for a car that was never armed")


if __name__ == "__main__":
  unittest.main()
