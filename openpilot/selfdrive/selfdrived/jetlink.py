"""Per-prediction readiness and freshness checks; no IO on the control loop."""
from dataclasses import dataclass


MAX_AGE_NS = 150_000_000
PROVE_NS = 1_000_000_000
PROVE_FRAMES = 20


def add_events(events, decision):
  from openpilot.cereal import log
  if decision.required:
    event = (log.OnroadEvent.EventName.jetlinkUnavailable if decision.fault else
             log.OnroadEvent.EventName.jetlinkReady if decision.ready else log.OnroadEvent.EventName.jetlinkNotReady)
    events.add(event)


@dataclass(frozen=True)
class Decision:
  required: bool
  ready: bool = False
  fault: bool = False
  reason: str = ''


class JetlinkGuard:
  def __init__(self, required: bool, sha256: str):
    # Latched for this onroad session: turning the setting off cannot bypass
    # a fault in a drive that started with remote inference enabled.
    self.required = required
    self.sha256 = sha256
    self.session = None
    self.last_message = 0
    self.last_output = 0
    self.prove_since = 0
    self.prove_frames = 0
    self.proven = False

  def _reset(self):
    self.prove_since = 0
    self.prove_frames = 0
    self.proven = False

  def _fault(self, reason):
    self._reset()
    return Decision(True, fault=True, reason=reason)

  def update(self, model, valid: bool, message_ns: int, now_ns: int, in_control: bool) -> Decision:
    health = model.jetlink
    self.required |= health.present
    if not self.required:
      return Decision(False)
    if not valid or not 0 < message_ns <= now_ns or now_ns - message_ns >= MAX_AGE_NS:
      return self._fault('Model messages stale')
    if not health.present or not health.active or not model.big:
      return self._fault('Mac model unavailable')
    if health.sha256 != self.sha256:
      return self._fault('Unexpected Mac model')
    output_ns = health.lastOutputMonoTime
    if not 0 < output_ns <= message_ns or now_ns - output_ns >= MAX_AGE_NS:
      return self._fault('Mac prediction stale')
    if not health.sessionId:
      return self._fault('Missing model session')

    session = (health.sessionId, health.generation)
    if session != self.session:
      self.session = session
      self.last_message = self.last_output = 0
      self._reset()
      if in_control:
        return self._fault('Model changed while engaged')

    if message_ns < self.last_message:
      return self._fault('Model message out of order')
    if message_ns != self.last_message:
      if output_ns < self.last_output or (not health.held and output_ns == self.last_output):
        return self._fault('Prediction timestamp did not advance')
      self.last_message, self.last_output = message_ns, output_ns
      if not health.held:
        if not self.prove_since:
          self.prove_since = now_ns
        self.prove_frames += 1

    if health.held:
      # A bounded held output can bridge a delayed frame while already
      # engaged. It never admits a new engagement or counts as fresh proof.
      if not self.proven:
        self._reset()
      return Decision(True, reason='Waiting for fresh Mac prediction')

    self.proven |= self.prove_frames >= PROVE_FRAMES and now_ns - self.prove_since >= PROVE_NS
    return Decision(True, ready=self.proven, reason='' if self.proven else 'Mac model warming up')
