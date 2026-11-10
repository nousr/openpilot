"""A turn request from the signal to the model that drives, in modeld's order.

Nothing here is a helper-only test. Every frame goes through DesireFrame, the
object modeld's loop calls (before, model.run, ran/failed, after), with the
real DesireHelper, Jetlink's real JoiningModelState and JetlinkModelState over
its test link, and the real JetlinkGuard deciding whether lateral stays
active. The small model stands in for stock modeld's ModelState and takes the
desire edge the same way.

What is pinned: a request is checked against the inputs of the frame that
would carry it, on its first frame and on every retry; it is asked again only
until its frame went, a few frames at most; and it never reaches a model other
than the one driving when it was asked.
"""
import os
import re
import sys
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(os.environ.get('JETLINK_REPO', str(ROOT / 'jetlink_repo')))   # jetlink's own test link

from jetlink.openpilot import joining, model_state
from jetlink.openpilot.joining import JoiningModelState
from jetlink.openpilot.model_state import JetlinkModelState
from opendbc.car.structs import CarState
from openpilot.cereal import log
from openpilot.selfdrive.controls.lib.desire_helper import DesireHelper, LaneChangeState
from openpilot.selfdrive.controls.lib.turn_desire_helper import TURN_REQUEST_FRAMES_MAX, TurnDelivery, TurnState
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.selfdrive.modeld.desire_frame import DesireFrame
from openpilot.selfdrive.selfdrived.jetlink import JetlinkGuard
from tests.openpilot import fakes
from tests.openpilot.test_model_state import STATEFUL, FakeClient, FakeWarp, spec_for

LEFT, RIGHT = int(log.Desire.turnLeft), int(log.Desire.turnRight)
DT = 0.05


def car(left=True, **changes):
  fields = {'vEgo': 2.0, 'gearShifter': "drive", 'leftBlinker': left, 'rightBlinker': not left}
  fields.update(changes)
  return CarState.new_message(**fields)


class Link(FakeClient):
  """Jetlink's test link, which a model state closes when it is retired."""
  closed = False

  def close(self):
    self.closed = True


class StockSmall:
  """Stock modeld's ModelState as far as the desire goes (modeld.py run())."""
  chestnut = False
  vision_input_names = ['img', 'big_img']

  def __init__(self):
    self.prev_desire = np.zeros(ModelConstants.DESIRE_LEN, dtype=np.float32)
    self.lat_delay = 0.0
    self.pulses = []   # the desire slot of every pulse this model took
    self.frames = 0

  def run(self, bufs, transforms, inputs, after_enqueue=None):
    self.frames += 1
    inputs['desire_pulse'][0] = 0
    pulse = np.where(inputs['desire_pulse'] - self.prev_desire > .99, inputs['desire_pulse'], 0)
    self.prev_desire[:] = inputs['desire_pulse']
    self.desire_sent = bool(pulse.any())
    if self.desire_sent:
      self.pulses.append(int(np.argmax(pulse)))
    return {'from': 'small'}

  def reset(self):
    self.prev_desire[:] = 0


class Loop:
  """modeld's frame loop around a model, and selfdrived's guard around its health."""
  BUFS = {k: SimpleNamespace(data=np.zeros(8, np.uint8)) for k in ('img', 'big_img')}

  def __init__(self, test, model, turn_enabled=True, guard_latency=0):
    self.model = model
    self.DH = DesireHelper(turn_desire_enabled=turn_enabled)
    self.events = []
    self.clock = 100.0
    self.frame = DesireFrame(self.DH, event=lambda name, **f: self.events.append((name, f)), monotonic=lambda: self.clock)
    self.guard = JetlinkGuard(True, test.spec.sha256)
    # selfdrived is another process: its fault reaches modeld's carControl some frames later, or (None) never
    # within the test. The request must not depend on the guard winning that race.
    self.guard_latency = guard_latency
    self.fault_at = None
    self.frames = 0
    self.handovers = getattr(model, 'handovers', 0)
    self.guard_fault = False
    self.failed_model = None

  def handed_over(self):
    # jetlink.openpilot.Jetlink.handed_over, which modeld calls through HOOKS
    handovers = getattr(self.model, 'handovers', 0)
    changed, self.handovers = handovers != self.handovers, handovers
    return changed

  def step(self, cs, lat_active=True, valid=True):
    """One iteration of modeld's loop: the same calls, in the same order."""
    self.clock += DT
    self.frames += 1
    seen = (self.guard_fault and self.guard_latency is not None and self.frames - self.fault_at > self.guard_latency)
    lat_active = lat_active and not seen
    vec_desire = self.frame.before(cs, lat_active, valid)
    inputs = {'desire_pulse': vec_desire, 'traffic_convention': np.array([1, 0], np.float32),
              'action_t': np.array([.2, .3], np.float32)}
    try:
      self.model.run(self.BUFS, {'img': np.eye(3), 'big_img': np.eye(3)}, inputs, None)
      self.frame.ran(self.model, self.handed_over())
    except Exception:
      # modeld: "big model failed, fall back to small", and no output this frame
      self.frame.failed()
      self.model = self.failed_model
      return
    self.frame.after(cs, lat_active, 0.0, valid)
    # selfdrived, on the health published with this frame's output
    health = getattr(self.model, 'frame_health', None)
    if health is not None:
      now = time.monotonic_ns()
      msg = SimpleNamespace(big=self.model.chestnut, jetlink=SimpleNamespace(present=True, **health))
      if self.guard.update(msg, True, now - 1, now, lat_active).fault and not self.guard_fault:
        self.guard_fault, self.fault_at = True, self.frames

  def run(self, cs, n, **kw):
    for _ in range(n):
      self.step(cs, **kw)

  def until_queued(self, cs):
    for _ in range(40):
      self.step(cs)
      if self.DH.turn.pending:
        return
    raise AssertionError("no turn request was queued")

  def states(self):
    return [(f['state'], f['delivery'], f['drop_reason']) for name, f in self.events if name == 'low_speed_turn_desire']


class Base(unittest.TestCase):
  def setUp(self):
    fakes.isolate(self, Path(tempfile.mkdtemp()))
    for target, name, value in ((joining, 'SMALL_WARMUP_FRAMES', 0), (model_state, 'HOLDS_IN_A_ROW', 99),
                                (model_state, 'PROVING_FRAMES', 0), (model_state, 'HOLDS_ALLOWED', 99)):
      patcher = mock.patch.object(target, name, value)
      patcher.start()
      self.addCleanup(patcher.stop)
    self.spec = spec_for(STATEFUL)
    self.client = Link()
    self.small = StockSmall()

  def big(self, client=None):
    client = client or self.client
    return JetlinkModelState(client, self.spec, FakeWarp(np.zeros(np.prod(self.spec.warped_shape), np.uint8)),
                             face=fakes.FACE, log=fakes.RecordingLog(), event=lambda name, **f: None)

  def joined(self, guard_latency=0):
    """The joining model with the large model driving, as after a swap while disengaged."""
    built = []
    def build(client, spec):
      built.append(self.big())
      return built[-1]
    s = JoiningModelState(self.small, lambda should_stop=None: (mock.MagicMock(name='link'), 'spec'), build,
                          reset_small=self.small.reset, progress=mock.Mock(), log=fakes.RecordingLog())
    self.addCleanup(lambda: (s.close(), s._thread.join(5)))
    deadline = time.monotonic() + 5
    while s._joined is None and time.monotonic() < deadline:
      time.sleep(0.001)
    s.in_control = False
    loop = Loop(self, s, guard_latency=guard_latency)
    loop.step(CarState.new_message(vEgo=2.0, gearShifter="drive"), lat_active=False)
    self.assertTrue(s.chestnut, 'the large model drives')
    s.in_control = True
    self.big_state = built[-1]
    return loop

  def sent(self, client=None):
    """Desire pulses the host was sent: (frame_id, slot), read back from the bytes handed to the link."""
    at, shape = self.spec.packed_layout['desire']
    out = []
    for _, packed, frame_id, _ in (client or self.client).sent:
      d = packed[at].reshape(shape)
      if d.any():
        out.append((frame_id, int(np.argmax(d))))
    return out

  def refuse(self, loop, offsets):
    """The link refuses the frames `offsets` from the next one."""
    self.client.busy = {self.big_state._frame_id + 1 + k for k in offsets}


CANCELS = {
  'lateral disengaged': lambda left: (car(left), {'lat_active': False}),
  'signal off': lambda left: (car(left, leftBlinker=False, rightBlinker=False), {}),
  'hazards': lambda left: (car(left, leftBlinker=True, rightBlinker=True), {}),
  'direction changed': lambda left: (car(not left), {}),
  'blindspot': lambda left: (car(left, leftBlindspot=left, rightBlindspot=not left), {}),
  'driver opposing': lambda left: (car(left, steeringPressed=True, steeringTorque=-2.0 if left else 2.0), {}),
  'inputs invalid': lambda left: (car(left), {'valid': False}),
  'not in drive': lambda left: (car(left, gearShifter="neutral"), {}),
  'too fast': lambda left: (car(left, vEgo=9.5), {}),
}


class TestOverJetlink(Base):
  def test_one_request_one_pulse_and_its_trace(self):
    for left, slot in ((True, LEFT), (False, RIGHT)):
      with self.subTest(left=left):
        self.setUp()
        loop = self.joined()
        cs = car(left)
        loop.until_queued(cs)
        self.assertEqual(self.sent(), [], 'queued is not sent')
        self.assertEqual(loop.DH.turn.delivery, TurnDelivery.queued)
        loop.run(cs, 60)
        self.assertEqual([s for _, s in self.sent()], [slot])
        self.assertEqual(loop.DH.turn.delivery, TurnDelivery.transmitted)
        self.assertEqual(loop.DH.turn.state, TurnState.active)
        self.assertEqual(loop.DH.lane_change_state, LaneChangeState.off)
        traces = [f['fate'] for name, f in loop.events if name == 'turn_request_trace']
        self.assertEqual(traces, ['answered'], 'answered in the frame it was sent in')

  def test_cancelled_before_its_first_send_nothing_goes(self):
    # the request was computed from the last frame's car state; this frame's says no
    for reason, make in CANCELS.items():
      for left in (True, False):
        with self.subTest(reason=reason, left=left):
          self.setUp()
          loop = self.joined()
          loop.until_queued(car(left))
          cs, kw = make(left)
          loop.run(cs, 30, **kw)
          self.assertEqual(self.sent(), [])
          self.assertIn('dropped', [delivery for _, delivery, _ in loop.states()], 'and the log says it was dropped')
          self.assertFalse(loop.DH.turn.pending)

  def test_cancelled_between_a_refused_send_and_its_retry_nothing_goes(self):
    # the review's case: the first frame is refused with the request still wanted, the
    # reason to cancel appears before the next frame, and that frame's send would succeed
    for reason, make in CANCELS.items():
      for left in (True, False):
        with self.subTest(reason=reason, left=left):
          self.setUp()
          loop = self.joined()
          loop.until_queued(car(left))
          self.refuse(loop, (0,))
          loop.step(car(left))
          self.assertTrue(loop.DH.turn.pending, 'refused, still wanted, asked again')
          cs, kw = make(left)
          loop.run(cs, 30, **kw)
          self.assertEqual(self.sent(), [])
          self.assertIn('dropped', [delivery for _, delivery, _ in loop.states()])
          self.assertFalse(loop.DH.turn.pending)

  def test_re_engaging_with_the_signal_still_on_does_not_send_it_late(self):
    loop = self.joined()
    loop.until_queued(car())
    self.refuse(loop, (0,))
    loop.step(car())
    loop.step(car(), lat_active=False)
    loop.run(car(), 60)
    self.assertEqual(self.sent(), [])
    self.assertEqual(loop.DH.turn.state, TurnState.blocked)

  def test_a_refused_request_goes_once_on_a_later_frame(self):
    for refused in range(1, TURN_REQUEST_FRAMES_MAX):
      for left, slot in ((True, LEFT), (False, RIGHT)):
        with self.subTest(refused=refused, left=left):
          self.setUp()
          loop = self.joined()
          cs = car(left)
          loop.until_queued(cs)
          first = self.big_state._frame_id + 1
          self.refuse(loop, range(refused))
          loop.run(cs, 60)
          self.assertEqual(self.sent(), [(first + refused, slot)])
          self.assertEqual(loop.DH.turn.delivery, TurnDelivery.transmitted)

  def test_refused_too_long_it_is_dropped_and_said_not_sent_late(self):
    loop = self.joined()
    loop.until_queued(car())
    self.refuse(loop, range(TURN_REQUEST_FRAMES_MAX))
    loop.run(car(), 80)
    self.assertEqual(self.sent(), [])
    self.assertEqual((loop.DH.turn.state, loop.DH.turn.delivery, loop.DH.turn.drop_reason),
                     (TurnState.blocked, TurnDelivery.dropped, 'expired'))
    self.assertIn(('blocked', 'dropped', 'expired'), loop.states())

  def test_a_loop_that_stalls_expires_the_request_by_the_clock(self):
    loop = self.joined()
    loop.until_queued(car())
    self.refuse(loop, (0,))
    loop.step(car())
    loop.clock += 1.0   # modeld did not run for a second
    loop.run(car(), 30)
    self.assertEqual(self.sent(), [])
    self.assertEqual(loop.DH.turn.drop_reason, 'expired')

  def test_a_reply_that_is_late_is_not_a_reason_to_ask_again(self):
    loop = self.joined()
    loop.until_queued(car())
    frame = self.big_state._frame_id + 1
    self.client.late = {frame}
    loop.step(car())
    self.assertTrue(self.big_state.held, 'the output before is published again')
    self.assertEqual(loop.DH.turn.delivery, TurnDelivery.transmitted)
    self.assertEqual([f['fate'] for n, f in loop.events if n == 'turn_request_trace'], ['flight'])
    self.client.late = set()
    loop.run(car(), 40)
    self.assertEqual(self.sent(), [(frame, LEFT)], 'exactly once')
    self.assertEqual([f['fate'] for n, f in loop.events if n == 'turn_request_trace'], ['flight', 'answered'])

  # How long selfdrived's fault takes to reach modeld: at once, a few frames, never within the test.
  GUARD = (0, 3, None)

  def test_the_large_model_fails_on_the_request_frame_and_the_small_one_never_hears_it(self):
    for latency in self.GUARD:
      with self.subTest(guard_latency=latency):
        self.setUp()
        loop = self.joined(latency)
        loop.until_queued(car())
        with mock.patch.object(self.client, 'infer_begin', side_effect=RuntimeError('link gone')):
          loop.step(car())   # Jetlink falls back to the small model inside this frame
        self.assertFalse(loop.model.chestnut)
        self.assertEqual(self.small.frames, 1, 'the small model ran this frame')
        self.assertEqual(self.small.pulses, [], 'without the desire')
        self.assertEqual((loop.DH.turn.state, loop.DH.turn.drop_reason), (TurnState.blocked, 'model changed'))
        self.assertTrue(loop.guard_fault, 'and selfdrived disengages on the model change')
        loop.run(car(), 60)
        self.assertEqual(self.small.pulses, [])
        self.assertEqual(self.sent(), [])

  def test_the_large_model_fails_on_the_retry_frame_and_the_small_one_never_hears_it(self):
    for latency in self.GUARD:
      with self.subTest(guard_latency=latency):
        self.setUp()
        loop = self.joined(latency)
        loop.until_queued(car())
        self.refuse(loop, (0,))
        loop.step(car())
        self.assertTrue(loop.DH.turn.pending)
        with mock.patch.object(self.client, 'infer_begin', side_effect=RuntimeError('link gone')):
          loop.step(car())
        self.assertEqual(loop.DH.turn.drop_reason, 'model changed')
        loop.run(car(), 60)
        self.assertEqual(self.small.pulses, [])
        self.assertEqual(self.sent(), [])

  def test_handed_back_for_lag_with_the_request_pending_the_small_model_never_hears_it(self):
    for latency in self.GUARD:
      with self.subTest(guard_latency=latency):
        self.setUp()
        loop = self.joined(latency)
        loop.until_queued(car())
        self.refuse(loop, (0,))
        with mock.patch.object(JetlinkModelState, '_note_hold', lambda state, held: 'held 5 frames in a row' if held else None):
          loop.step(car())   # refused and held, and Jetlink says this was the large model's last frame
        self.assertEqual((loop.DH.turn.pending, loop.DH.turn.drop_reason), (False, 'model changed'))
        loop.step(car())     # the hand-back: this frame is the small model's
        self.assertFalse(loop.model.chestnut)
        self.assertEqual(self.small.frames, 1)
        loop.run(car(), 60)
        self.assertEqual(self.small.pulses, [])
        self.assertEqual(self.sent(), [])

  def test_a_model_change_after_the_request_went_does_not_send_it_again(self):
    for latency in self.GUARD:
      with self.subTest(guard_latency=latency):
        self.setUp()
        loop = self.joined(latency)
        loop.until_queued(car())
        loop.run(car(), 5)
        self.assertEqual(len(self.sent()), 1)
        with mock.patch.object(self.client, 'infer_begin', side_effect=RuntimeError('link gone')):
          loop.step(car())
        loop.run(car(), 60)
        self.assertEqual(self.small.pulses, [], 'the signal is still on, the replacement is not asked')
        self.assertEqual(len(self.sent()), 1)

  def test_modelds_own_fallback_drops_a_queued_request(self):
    # a chestnut's failure: model.run raises out of modeld's try and modeld swaps the model itself
    big = self.big()
    big.chestnut = True
    loop = Loop(self, big)
    loop.failed_model = self.small
    loop.until_queued(car())
    with mock.patch.object(self.client, 'infer_begin', side_effect=RuntimeError('big model failed')):
      loop.step(car())
    self.assertIs(loop.model, self.small)
    loop.run(car(), 60)
    self.assertEqual(self.small.pulses, [])
    self.assertEqual(loop.DH.turn.drop_reason, 'model changed')

  def test_a_host_reset_rides_the_frame_that_carries_the_request(self):
    loop = self.joined()
    loop.until_queued(car())
    first = self.big_state._frame_id + 1
    self.refuse(loop, (0,))
    self.big_state._need_reset = True
    loop.run(car(), 5)
    resets = {frame_id: reset for _, _, frame_id, reset in self.client.sent}
    self.assertNotIn(first, resets)
    self.assertTrue(resets[first + 1])
    self.assertEqual(self.sent(), [(first + 1, LEFT)])

  def test_two_signal_episodes_two_requests(self):
    loop = self.joined()
    loop.until_queued(car())
    loop.run(car(), 20)
    loop.run(car(leftBlinker=False, rightBlinker=False), 20)
    loop.until_queued(car(False))
    loop.run(car(False), 20)
    self.assertEqual([s for _, s in self.sent()], [LEFT, RIGHT])

  def test_a_lane_change_is_untouched_and_survives_a_refused_frame(self):
    loop = self.joined()
    fast = {'vEgo': 30 * 0.44704}
    loop.run(car(**fast), 3)
    self.assertEqual(loop.DH.lane_change_state, LaneChangeState.preLaneChange)
    self.refuse(loop, (1,))
    loop.run(car(steeringPressed=True, steeringTorque=1.5, **fast), 6)
    self.assertEqual(loop.DH.lane_change_state, LaneChangeState.laneChangeStarting)
    self.assertEqual([s for _, s in self.sent()], [int(log.Desire.laneChangeLeft)])
    self.assertEqual(loop.DH.turn.state, TurnState.idle)
    self.assertEqual(loop.states(), [])


class TestOverTheStockModel(Base):
  """The small model alone, as on a comma without the link."""

  def test_one_request_one_pulse(self):
    for left, slot in ((True, LEFT), (False, RIGHT)):
      with self.subTest(left=left):
        self.setUp()
        loop = Loop(self, self.small)
        loop.run(car(left), 100)
        self.assertEqual(self.small.pulses, [slot])
        self.assertEqual(loop.DH.turn.delivery, TurnDelivery.transmitted)

  def test_cancelled_before_its_first_frame_nothing_is_asked(self):
    for reason, make in CANCELS.items():
      with self.subTest(reason=reason):
        self.setUp()
        loop = Loop(self, self.small)
        loop.until_queued(car())
        cs, kw = make(True)
        loop.run(cs, 30, **kw)
        self.assertEqual(self.small.pulses, [])

  def test_disabled_nothing_is_asked(self):
    loop = Loop(self, self.small, turn_enabled=False)
    loop.run(car(), 100)
    self.assertEqual(self.small.pulses, [])
    self.assertEqual(loop.events, [])


class TestModeldCallsItInThisOrder(unittest.TestCase):
  """modeld cannot be imported off a comma; pin the calls Loop.step mirrors."""

  def test_the_loop_calls_before_run_ran_failed_after_in_order(self):
    source = (ROOT / 'openpilot/selfdrive/modeld/modeld.py').read_text()
    loop = source[source.index('  while True:', source.index('desire_frame = DesireFrame(DH)')):]
    names = ('sm.update(0)', 'desire_frame.before(', 'model.run(', 'HOOKS.handed_over(model)',
             'desire_frame.ran(', 'desire_frame.failed(', 'desire_frame.after(')
    calls = [m.group(0) for m in re.finditer('|'.join(map(re.escape, names)), loop)]
    self.assertEqual(calls, list(names))
    self.assertNotIn('DH.desire', loop, 'the desire reaches the model through desire_frame.before() alone')
    self.assertNotIn('DH.update(', loop)
    self.assertIn("'desire_pulse': vec_desire", loop)


if __name__ == '__main__':
  unittest.main()
