#!/usr/bin/env python3
"""Apply the bench seams to an isolated copy of the installed release.

Run once in a copy of release-mici f7db927, after copying this directory,
openpilot/jetlink_adapter.py and jetlink_repo into it. Rebuild libparams_c.so.
This preserves the release's model runner and compiled tinygrad ABI.
"""
from pathlib import Path
import subprocess

RELEASE = 'f7db927c728bab57bb1263e05465766a8f28fc9d'


def main():
  root = Path(__file__).resolve().parents[2]
  if root == Path('/data/openpilot').resolve() or not (root / 'openpilot/jetlink_adapter.py').is_file():
    raise SystemExit('Run only inside the isolated bench checkout with the adapter installed')
  if subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip() != RELEASE:
    raise SystemExit(f'This overlay is for {RELEASE} only')

  modeld = root / 'openpilot/selfdrive/modeld/modeld.py'
  params = root / 'openpilot/common/params_keys.h'
  patches = {
    modeld: [
      ('import openpilot.cereal.messaging as messaging\n', 'import openpilot.cereal.messaging as messaging\nfrom openpilot import jetlink_adapter\n'),
      ('  CHESTNUT = chestnut_compiled() and (chestnut_present() or cable_connected())',
       '  HOOKS = jetlink_adapter.hooks()\n  CHESTNUT = chestnut_compiled() and (chestnut_present() or (cable_connected() and not jetlink_adapter.link_on()))'),
      ('  config_realtime_process(7, 54)', '''  if HOOKS.prepare(CHESTNUT):
    model = HOOKS.attach(model, small_model, vipc_client_main.width, vipc_client_main.height)
  config_realtime_process(7, 54)'''),
      ('    frame_drop_ratio = frames_dropped / (1 + frames_dropped)', '''    frame_drop_ratio = frames_dropped / (1 + frames_dropped)
    model.frame_drop_ratio = frame_drop_ratio'''),
      ('      model_output = model.run(bufs, transforms, inputs, chestnut_state.send if send_chestnut else None)',
       '''      model_output = model.run(bufs, transforms, inputs, chestnut_state.send if send_chestnut else None)
      if HOOKS.handed_over(model):
        run_count = 0'''),
    ],
    params: [('    {"IsOffroad", {CLEAR_ON_MANAGER_START, BOOL}},', '''    {"IsOffroad", {CLEAR_ON_MANAGER_START, BOOL}},
    {"JetlinkLink", {PERSISTENT, INT, "0"}},
    {"JetlinkModel", {PERSISTENT, JSON}},
    {"JetlinkProgress", {CLEAR_ON_MANAGER_START, JSON}},
    {"JetlinkSpec", {PERSISTENT, JSON}},
    {"JetlinkChargePhone", {PERSISTENT, BOOL, "0"}},''')],
  }
  changed = {}
  for path, replacements in patches.items():
    text = path.read_text()
    if 'jetlink_adapter' in text or 'JetlinkLink' in text:
      raise SystemExit(f'Already patched: {path}')
    for before, after in replacements:
      if text.count(before) != 1:
        raise SystemExit(f'Unexpected release source in {path}: {before!r}')
      text = text.replace(before, after)
    changed[path] = text
  for path, text in changed.items():
    path.write_text(text)
    print(f'Patched {path.relative_to(root)}')


if __name__ == '__main__':
  main()
