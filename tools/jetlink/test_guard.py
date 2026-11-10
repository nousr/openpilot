"""100 Hz control-loop tests with a 20 Hz model producer; no hardware IO."""
from types import SimpleNamespace
import unittest

from openpilot.jetlink_adapter import MODEL_SHA256
from openpilot.selfdrive.selfdrived.jetlink import JetlinkGuard, MAX_AGE_NS


class TestGuard(unittest.TestCase):
  def setUp(self):
    self.guard = JetlinkGuard(True, MODEL_SHA256)
    self.now = 10_000_000_000
    self.model = SimpleNamespace(big=True, jetlink=SimpleNamespace(
      present=True, active=True, held=False, lastOutputMonoTime=0,
      sessionId=123, generation=1, sha256=MODEL_SHA256))
    self.message = 0

  def tick(self, publish=False, held=False, engaged=False):
    self.now += 10_000_000
    if publish:
      self.message = self.now - 1_000_000
      self.model.jetlink.held = held
      if not held:
        self.model.jetlink.lastOutputMonoTime = self.now - 2_000_000
    return self.guard.update(self.model, True, self.message, self.now, engaged)

  def prove(self):
    for i in range(111):
      result = self.tick(publish=i % 5 == 0)
      if i < 100:
        self.assertFalse(result.ready)
    self.assertTrue(result.ready)
    return result

  def test_proves_at_model_rate_not_control_rate(self):
    self.prove()

  def test_repeated_control_ticks_cannot_prove_one_model_frame(self):
    self.tick(publish=True)
    for _ in range(200):
      self.assertFalse(self.tick().ready)

  def test_missing_messages_expire_without_a_new_message(self):
    self.prove()
    for _ in range(14):
      self.assertFalse(self.tick(engaged=True).fault)
    self.assertTrue(self.tick(engaged=True).fault)

  def test_held_prediction_does_not_refresh_age(self):
    self.prove()
    for i in range(14):
      result = self.tick(publish=i % 5 == 0, held=True, engaged=True)
      self.assertFalse(result.fault)
      self.assertFalse(result.ready)
    self.assertTrue(self.tick(publish=True, held=True, engaged=True).fault)

  def test_single_held_frame_allows_existing_control_but_blocks_entry(self):
    self.prove()
    result = self.tick(publish=True, held=True, engaged=True)
    self.assertFalse(result.fault)
    self.assertFalse(result.ready)
    self.assertTrue(self.tick(publish=True, engaged=True).ready)

  def test_fault_recovery_requires_new_proof(self):
    self.prove()
    for _ in range(16):
      self.tick(engaged=True)
    self.assertFalse(self.tick(publish=True).ready)
    for i in range(1, 101):
      result = self.tick(publish=i % 5 == 0)
      if i < 100:
        self.assertFalse(result.ready)
    self.assertTrue(result.ready)

  def test_hold_during_startup_restarts_proof(self):
    for i in range(80):
      self.tick(publish=i % 5 == 0)
    self.tick(publish=True, held=True)
    self.prove()

  def test_fallback_is_a_fault_even_with_valid_model_messages(self):
    self.prove()
    self.model.big = False
    self.model.jetlink.active = False
    self.assertTrue(self.tick(publish=True, engaged=True).fault)

  def test_model_restart_or_swap_while_engaged_is_a_fault(self):
    for field in ('sessionId', 'generation'):
      with self.subTest(field=field):
        self.setUp()
        self.prove()
        setattr(self.model.jetlink, field, getattr(self.model.jetlink, field) + 1)
        self.assertTrue(self.tick(publish=True, engaged=True).fault)

  def test_rejoin_while_disengaged_restarts_proof(self):
    self.prove()
    self.model.jetlink.generation += 1
    self.assertFalse(self.tick(publish=True).ready)

  def test_missing_health_or_wrong_model_blocks(self):
    for field, value in (('present', False), ('sha256', 'other'), ('sessionId', 0)):
      with self.subTest(field=field):
        self.setUp()
        setattr(self.model.jetlink, field, value)
        self.assertTrue(self.tick(publish=True).fault)

  def test_fresh_flag_cannot_hide_repeated_prediction(self):
    self.prove()
    self.message += 1
    self.assertTrue(self.tick(engaged=True).fault)

  def test_invalid_future_and_expired_timestamps_fail_closed(self):
    self.prove()
    for message, now, valid in ((self.message, self.now, False),
                                (self.now + 1, self.now, True),
                                (self.message, self.message + MAX_AGE_NS, True)):
      with self.subTest(message=message, now=now, valid=valid):
        self.assertTrue(self.guard.update(self.model, valid, message, now, True).fault)

  def test_normal_local_mode_is_unchanged(self):
    guard = JetlinkGuard(False, MODEL_SHA256)
    self.model.jetlink.present = False
    result = guard.update(self.model, False, 0, self.now, False)
    self.assertFalse(result.required)
    self.assertFalse(result.fault)

  def test_unexpected_remote_output_latches_guard(self):
    guard = JetlinkGuard(False, MODEL_SHA256)
    self.assertTrue(guard.update(self.model, True, 0, self.now, False).required)
    self.model.jetlink.present = False
    self.assertTrue(guard.update(self.model, True, 0, self.now, False).fault)


if __name__ == '__main__':
  unittest.main()
