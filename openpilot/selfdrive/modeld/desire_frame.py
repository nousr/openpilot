"""The order modeld runs desire logic in around one model frame.

Kept out of modeld's loop so the tests drive the same code the car does, with
the real DesireHelper and the real Jetlink model states:

  before()  after sm.update(), before model.run(): the desire vector for this
            frame, a queued turn request first checked against these inputs
  ran()     after model.run(): what the runner says became of the desire, and
            whether another model took the drive over
  failed()  model.run() raised and modeld replaced the model
  after()   with the frame's output: the helper's once-a-frame update

A turn request is queued by after(), offered by before() on the next frame,
transmitted when the runner says its frame went (desire_sent), and processed
when the Jetlink host has answered that frame (desire_trace). Each step is
logged; none of them says the policy acted on it.
"""
import time

import numpy as np

from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.controls.lib.turn_desire_helper import TurnState
from openpilot.selfdrive.modeld.constants import ModelConstants


class DesireFrame:
  def __init__(self, DH, event=cloudlog.event, monotonic=time.monotonic):
    self.DH = DH
    self._event = event
    self._monotonic = monotonic
    self.desire_sent = True
    self.handed_over = False
    self._logged = None
    self._trace = None

  def before(self, CS, lat_active, inputs_valid) -> np.ndarray:
    desire = self.DH.presend(CS, lat_active, turn_inputs_valid=inputs_valid, now=self._monotonic())
    self._log(CS)
    vec_desire = np.zeros(ModelConstants.DESIRE_LEN, dtype=np.float32)
    if desire >= 0 and desire < ModelConstants.DESIRE_LEN:
      vec_desire[desire] = 1
    return vec_desire

  def ran(self, model, handed_over: bool) -> None:
    # A runner that does not say ran the frame it was given, where it stands.
    self.desire_sent = bool(getattr(model, 'desire_sent', True))
    self.handed_over = bool(handed_over)
    trace = getattr(model, 'desire_trace', None)
    if trace is not None and trace != self._trace:
      # transmitted (fate flight), then processed (answered) or lost: the Jetlink link's own account
      self._event("turn_request_trace", **trace)
    self._trace = trace

  def failed(self) -> None:
    self.desire_sent, self.handed_over = False, True
    self.DH.turn_model_changed()

  def after(self, CS, lat_active, lane_change_prob, inputs_valid) -> None:
    self.DH.update(CS, lat_active, lane_change_prob, turn_inputs_valid=inputs_valid,
                   turn_desire_sent=self.desire_sent, model_changed=self.handed_over, now=self._monotonic())
    self.desire_sent, self.handed_over = True, False
    self._log(CS)

  def _log(self, CS) -> None:
    turn = self.DH.turn
    now = (turn.state, turn.delivery, turn.drop_reason)
    if now != self._logged and (self._logged is not None or turn.state != TurnState.idle):
      self._event("low_speed_turn_desire", state=turn.state.value, direction=int(turn.direction),
                  desire=int(self.DH.desire), v_ego=CS.vEgo, delivery=turn.delivery.value,
                  drop_reason=turn.drop_reason, offers=turn.offers)
    self._logged = now
