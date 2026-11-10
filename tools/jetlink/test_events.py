"""Exercise the production event mapping and openpilot engagement state machine."""
from unittest.mock import Mock, patch
import unittest

from openpilot.cereal import log
from openpilot.selfdrive.selfdrived.jetlink import Decision, add_events
from openpilot.selfdrive.selfdrived.events import Events
from openpilot.selfdrive.selfdrived.state import StateMachine
from openpilot.system.manager.process import PythonProcess, RestartingPythonProcess


class TestEngagement(unittest.TestCase):
  def setUp(self):
    self.machine = StateMachine()

  def step(self, decision, *extra):
    events = Events()
    add_events(events, decision)
    for event in extra:
      events.add(event)
    return self.machine.update(events)

  def test_cannot_engage_before_readiness_or_during_fault(self):
    for decision in (Decision(True), Decision(True, fault=True)):
      self.assertEqual(self.step(decision, log.OnroadEvent.EventName.buttonEnable), (False, False))

  def test_fault_disables_and_recovery_needs_an_enable_event(self):
    ready = Decision(True, ready=True)
    self.assertEqual(self.step(ready, log.OnroadEvent.EventName.buttonEnable), (True, True))
    self.assertEqual(self.step(Decision(True, fault=True)), (False, False))
    self.assertEqual(self.step(Decision(True)), (False, False))
    self.assertEqual(self.step(ready), (False, False))
    self.assertEqual(self.step(ready, log.OnroadEvent.EventName.buttonEnable), (True, True))

  def test_bounded_hold_keeps_existing_control_but_never_enables(self):
    hold = Decision(True, ready=False, fault=False)
    self.assertEqual(self.step(hold, log.OnroadEvent.EventName.buttonEnable), (False, False))
    self.step(Decision(True, ready=True), log.OnroadEvent.EventName.buttonEnable)
    self.assertEqual(self.step(hold), (True, True))

  def test_brake_and_cancel_remain_user_disables(self):
    ready = Decision(True, ready=True)
    for event in (log.OnroadEvent.EventName.pedalPressed, log.OnroadEvent.EventName.buttonCancel):
      with self.subTest(event=event):
        self.assertEqual(self.step(ready, log.OnroadEvent.EventName.buttonEnable), (True, True))
        self.assertEqual(self.step(ready, event), (False, False))

  def test_stock_safety_fault_takes_priority_over_ready(self):
    ready = Decision(True, ready=True)
    self.step(ready, log.OnroadEvent.EventName.buttonEnable)
    self.assertEqual(self.step(ready, log.OnroadEvent.EventName.controlsMismatch), (False, False))


class TestOwnerRestart(unittest.TestCase):
  def test_dead_owner_is_reaped_before_restart(self):
    owner = RestartingPythonProcess('jetlinkd', 'openpilot.jetlink_adapter', lambda *_: True)
    owner.proc = Mock(exitcode=1)
    calls = []
    def reap():
      calls.append('stop')
      owner.proc = None
    with patch.object(owner, 'stop', side_effect=reap), patch.object(PythonProcess, 'start', side_effect=lambda: calls.append('start')):
      owner.start()
    self.assertEqual(calls, ['stop', 'start'])

  def test_live_owner_is_not_stopped(self):
    owner = RestartingPythonProcess('jetlinkd', 'openpilot.jetlink_adapter', lambda *_: True)
    owner.proc = Mock(exitcode=None)
    with patch.object(owner, 'stop') as stop, patch.object(PythonProcess, 'start'):
      owner.start()
    stop.assert_not_called()


if __name__ == '__main__':
  unittest.main()
