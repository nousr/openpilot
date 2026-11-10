"""Jetlink integration for isolated, parked camera/model benchmarks."""
import functools
import os
from pathlib import Path
import re

API = 3
OWNER = 'jetlinkd'


def bench_enabled() -> bool:
  prefix = os.environ.get('OPENPILOT_PREFIX', '')
  return (os.environ.get('JETLINK_BENCH') == '1' and prefix != 'd'
          and re.fullmatch(r'[A-Za-z0-9_-]+', prefix) is not None)


def _adapter_class():
  from dataclasses import replace
  from jetlink.openpilot.stock import Stock

  class Adapter(Stock):
    ADAPTER_MODULE = 'openpilot.jetlink_adapter'
    KEYS = replace(Stock.KEYS, big_model='JetlinkModel')
    OWNER_LOG = Path(os.environ.get('JETLINK_BENCH_OUTPUT', '/data/jetlink-bench')) / 'owner.log'

    def model_root(self) -> Path:
      return self.basedir / '.jetlink-models'

  return Adapter


def adapter():
  return _adapter_class()()


def owner_config():
  return _adapter_class().owner_config()


def main():
  if not bench_enabled():
    raise SystemExit('Jetlink requires JETLINK_BENCH=1 and a private OPENPILOT_PREFIX')
  _adapter_class().main()


def link_on() -> bool:
  if not bench_enabled():
    return False
  prefix = os.environ['OPENPILOT_PREFIX']
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
  if not bench_enabled():
    return _NoJetlink('')
  try:
    from jetlink.openpilot.hooks import Hooks
    return Hooks(API, adapter, link_on=link_on, log=_cloudlog)
  except Exception as e:
    return _NoJetlink(f'Jetlink is unavailable: {e}')


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
