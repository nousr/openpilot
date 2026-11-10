"""Exercise the real Jetlink input packer without a camera, GPU, USB or policy."""
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

import numpy as np

from jetlink.openpilot.model_state import JetlinkModelState
from opendbc.car.structs import CarState
from openpilot.cereal import log
from openpilot.selfdrive.controls.lib.desire_helper import DesireHelper
from openpilot.selfdrive.modeld.constants import ModelConstants


class TestTurnDesireInput(unittest.TestCase):
  def test_both_turns_reach_correct_policy_slots_once(self):
    for left, slot in ((True, log.Desire.turnLeft), (False, log.Desire.turnRight)):
      with self.subTest(left=left):
        helper = DesireHelper(turn_desire_enabled=True)
        cs = CarState.new_message(vEgo=2.0, gearShifter="drive", leftBlinker=left, rightBlinker=not left)
        # Only camera/GPU/transport boundaries are replaced. prepare() is the
        # pinned Jetlink implementation, including rising-edge conversion.
        state = object.__new__(JetlinkModelState)
        state.warp = Mock()
        state.client = Mock()
        state.log_telemetry = Mock()
        state.prev_desire = np.zeros(ModelConstants.DESIRE_LEN, dtype=np.float32)
        state.npy = {'desire': np.zeros_like(state.prev_desire), 'traffic_convention': np.zeros(2), 'action_t': np.zeros(2)}
        camera = SimpleNamespace(data=bytes(16))
        inputs = {'traffic_convention': np.array([1, 0], dtype=np.float32), 'action_t': np.array([0.2, 0.3], dtype=np.float32)}
        pulses = []
        for _ in range(100):
          # Match modeld's ordering: use the previous update, then update DH.
          inputs['desire_pulse'] = np.eye(ModelConstants.DESIRE_LEN, dtype=np.float32)[helper.desire]
          state.prepare({'img': camera, 'big_img': camera}, dict.fromkeys(('img', 'big_img'), np.eye(3)), inputs)
          pulses.append(state.npy['desire'].copy())
          helper.update(cs, True, 0.0)
        expected = np.zeros(ModelConstants.DESIRE_LEN)
        expected[slot] = 1
        np.testing.assert_array_equal(np.sum(pulses, axis=0), expected)

        # A fresh model's edge history must not re-issue an already-sent turn
        # just because the turn signal is still held.
        state.prev_desire.fill(0)
        inputs['desire_pulse'] = np.eye(ModelConstants.DESIRE_LEN, dtype=np.float32)[helper.desire]
        state.prepare({'img': camera, 'big_img': camera}, dict.fromkeys(('img', 'big_img'), np.eye(3)), inputs)
        self.assertFalse(state.npy['desire'].any())


if __name__ == '__main__':
  unittest.main()
