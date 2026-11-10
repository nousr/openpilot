"""Run with unittest in openpilot's environment; no camera processes needed."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from openpilot import jetlink_adapter as fork
from jetlink.openpilot.testing import FORBIDDEN, check_adapter, check_fallback, check_seam, install_guard

# The staged checkout itself lives under /data. Protect the live installation,
# params, recordings and logs while allowing source reads in the bench checkout.
GUARD = install_guard(tuple(p for p in FORBIDDEN if p != '/data/') +
                      ('/data/params/', '/data/openpilot/', '/data/media/', '/data/log/'))


class TestAdapter(unittest.TestCase):
  def setUp(self):
    self.temp = tempfile.TemporaryDirectory()
    self.env = patch.dict(os.environ, {'PARAMS_ROOT': self.temp.name, 'OPENPILOT_PREFIX': 'benchtest', 'JETLINK_BENCH': '1'})
    self.env.start()
    self.store = Path(self.temp.name) / 'benchtest'
    self.store.mkdir()
    (self.store / 'JetlinkLink').write_text('1')
    fork.hooks.cache_clear()
    GUARD.start()

  def tearDown(self):
    problems = GUARD.stop()
    fork.hooks.cache_clear()
    self.env.stop()
    self.temp.cleanup()
    self.assertEqual(problems, [])

  def test_adapter_contract(self):
    self.assertEqual(check_adapter(fork, heavy=('openpilot.common.params', 'openpilot.common.swaglog', 'openpilot.cereal')), [])

  def test_modeld_contract(self):
    self.assertEqual(check_seam(Path(__file__).resolve().parents[2] / 'openpilot/selfdrive/modeld/modeld.py'), [])

  def test_link_requires_private_bench(self):
    self.assertTrue(fork.link_on())
    for changes in ({'JETLINK_BENCH': '0'}, {'OPENPILOT_PREFIX': ''}, {'OPENPILOT_PREFIX': 'd'},
                    {'OPENPILOT_PREFIX': '../d'}, {'OPENPILOT_PREFIX': '/data/params/d'}):
      with self.subTest(changes=changes), patch.dict(os.environ, changes):
        self.assertFalse(fork.link_on())
        with self.assertRaises(SystemExit):
          fork.main()

  def test_link_requires_usb_setting(self):
    for value in ('0', '', '2', 'garbage'):
      (self.store / 'JetlinkLink').write_text(value)
      self.assertFalse(fork.link_on())
    (self.store / 'JetlinkLink').unlink()
    self.assertFalse(fork.link_on())

  def test_live_mode_requires_explicit_usb_setting(self):
    live = Path(self.temp.name) / 'd'
    live.mkdir()
    with patch.dict(os.environ, {'OPENPILOT_PREFIX': 'd', 'JETLINK_BENCH': '0'}):
      self.assertFalse(fork.link_on())
      (live / 'JetlinkLink').write_text('1')
      self.assertTrue(fork.link_on())
      (live / 'JetlinkLink').write_text('0')
      self.assertFalse(fork.link_on())

  def test_bench_cannot_fall_through_to_live_namespace(self):
    live = Path(self.temp.name) / 'd'
    live.mkdir()
    (live / 'JetlinkLink').write_text('1')
    with patch.dict(os.environ, {'OPENPILOT_PREFIX': 'd', 'JETLINK_BENCH': '1'}):
      self.assertFalse(fork.link_on())
      with self.assertRaises(SystemExit):
        fork.main()

  def test_frame_health_missing_adapter_is_explicitly_inactive(self):
    from types import SimpleNamespace
    msg = SimpleNamespace(jetlink=SimpleNamespace())
    fork.fill_health(msg, object(), requested=True)
    self.assertTrue(msg.jetlink.present)
    self.assertFalse(msg.jetlink.active)

  def test_normal_modeld_does_not_bind_jetlink(self):
    with patch.dict(os.environ, {'JETLINK_BENCH': '0'}), patch.object(fork, 'adapter', side_effect=AssertionError('must not bind')):
      self.assertFalse(fork.hooks().prepare(False))
      self.assertIsNone(fork.hooks().runtime())

  def test_missing_jetlink_fallback(self):
    hooks = ('prepare', 'handed_over', 'runtime', 'state', 'reason', 'shutdown_step', 'swap_events')
    self.assertEqual(check_fallback(fork._NoJetlink('missing'), hooks, link_on=fork.link_on), [])


if __name__ == '__main__':
  unittest.main()
