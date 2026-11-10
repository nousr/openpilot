"""USB Jetlink integration, with opt-in live mode and isolated bench support."""
import functools
import os
from pathlib import Path
import re

API = 3
OWNER = 'jetlinkd'
MODEL_SHA256 = '87fe86ca0813c099efddf9173ba503be2e40ea4c5362c36812a44141f4cb07d4'


def bench_enabled() -> bool:
  prefix = os.environ.get('OPENPILOT_PREFIX', '')
  return (os.environ.get('JETLINK_BENCH') == '1' and prefix != 'd'
          and re.fullmatch(r'[A-Za-z0-9_-]+', prefix) is not None)


def supported_namespace() -> bool:
  # An explicitly requested bench must never fall through to live mode.
  if os.environ.get('JETLINK_BENCH') == '1':
    return bench_enabled()
  return os.environ.get('OPENPILOT_PREFIX', 'd') in ('', 'd')


def _adapter_class():
  from dataclasses import replace
  from jetlink.openpilot.stock import Stock

  class Adapter(Stock):
    ADAPTER_MODULE = 'openpilot.jetlink_adapter'
    KEYS = replace(Stock.KEYS, big_model='JetlinkModel')
    OWNER_LOG = Path(os.environ.get('JETLINK_BENCH_OUTPUT', '/data/jetlink')) / 'owner.log'

    def model_root(self) -> Path:
      return self.basedir / '.jetlink-models'

  return Adapter


def adapter():
  return _adapter_class()()


def owner_config():
  return _adapter_class().owner_config()


def main():
  if not supported_namespace():
    raise SystemExit('Jetlink requires the normal namespace or an explicitly isolated bench')
  _adapter_class().main()


def link_on() -> bool:
  if not supported_namespace():
    return False
  prefix = os.environ.get('OPENPILOT_PREFIX') or 'd'
  root = os.environ.get('PARAMS_ROOT') or ('/data/params' if os.path.isfile('/AGNOS') else
                                        os.path.expanduser(f'~/.comma{prefix}/params'))
  try:
    return (Path(root) / prefix / 'JetlinkLink').read_text().strip() == '1'
  except OSError:
    return False


def _cloudlog():
  from openpilot.common.swaglog import cloudlog
  return cloudlog


@functools.cache
def hooks():
  if not supported_namespace():
    return _NoJetlink('')
  try:
    from jetlink.openpilot.hooks import Hooks
    return Hooks(API, adapter, link_on=link_on, log=_cloudlog)
  except Exception as e:
    return _NoJetlink(f'Jetlink is unavailable: {e}')


def should_run(started, params, CP) -> bool:
  return link_on() and hooks().should_run(started, params, CP)


def fill_health(message, model, requested: bool) -> None:
  """Publish health alongside the exact prediction it describes."""
  if not requested:
    return
  message.jetlink.present = True
  try:
    health = model.frame_health
    for name, value in health.items():
      setattr(message.jetlink, name, value)
  except Exception:
    # Default inactive health blocks engagement even if the adapter failed.
    message.jetlink.active = False


class _NoJetlink:
  def __init__(self, why): self._why = why
  def should_run(self, started, params, CP): return False
  def status(self): return None
  def reason(self): return self._why if link_on() else None
  def prepare(self, chestnut): return False
  def handed_over(self, model): return False
  def state(self, model): return 'none'
  def shutdown_step(self, should_shutdown, reason=''): return should_shutdown
  def runtime(self): return None
  def swap_events(self, tick_s): return None


if __name__ == '__main__':
  main()
