# Mac Chestnut USB bench

This branch connects stock openpilot's camera/model loop to Jetlink on an
Apple Silicon Mac. It is an isolated, parked benchmark integration. The
normal manager does not start the owner, and the adapter requires both
`JETLINK_BENCH=1` and a private `OPENPILOT_PREFIX`.

The comma preprocesses its two road-camera frames with its existing Adreno
warp. Jetlink transfers those inputs over USB to the Mac, which runs the
large driving model and maintains its recurrent state. The comma parses the
returned predictions and publishes its usual `modelV2`, `drivingModelData`
and `cameraOdometry` messages inside the benchmark's private namespace.

## Model and runtime

`bench.sh` pins Mountain Dew by the original ONNX SHA-256:

```
87fe86ca0813c099efddf9173ba503be2e40ea4c5362c36812a44141f4cb07d4
```

On 2026-11-09 this matched stable `commaai/openpilot:release-chestnut`
commit `68400059d4389d12137fb25bb63126fe3f52fac3`, checkpoint
`8d736683-fed4-4e48-96fd-eae5d9d5bc56/12864`. Identification used the
compiled model's checkpoint metadata and sampled weights against comma's
ONNX export. This is not a claim of bitwise equality between the compiled
Qualcomm/AMD artifact and the CoreML execution graph. Nightly is a separate
model and has not been tested here.

The Mac uses Jetlink's ONNX Runtime backend, `--device ane`, with CoreML
CPU/Neural Engine and CPU/GPU sessions. The prepared model cache is reused
from the previous synthetic parity and five-minute inference tests.

## Run on a separately powered, parked comma

Keep SSH over Wi-Fi for test control. The Mac connects to the comma's
data/Chestnut port; the comma has its own power supply.

On the Mac, from the Jetlink checkout:

```sh
caffeinate -i JetlinkKit/.build/release/jetlink-server --usb \
  --backend ort --device ane --cache ../model-cache
```

On the comma, from a built checkout with its submodules available:

```sh
OUTPUT=/data/jetlink-bench/runs/my-test bash tools/jetlink/bench.sh \
  --seconds 180 --resources
```

Use a new output directory each time. `--small` measures the comma's local
model without starting the USB owner. The runner reads the real device's
offroad flag and saved vehicle/calibration parameters before entering a
private params and messaging namespace. It starts only the USB owner,
camerad, modeld and optional resource sampler. It stops if the real offroad
flag changes or a child exits. No controls or pandad process is started.
The owner setting is cleared before shutdown so it restores its USB/VM
tuning. Jetlink keeps USB input current cut while a host remains attached;
the comma therefore continues to require its separate power supply.

## Installed-release test copy

The user's installed release is older than this development branch. The
first hardware tests use `/data/jetlink-bench/openpilot`, a separate copy of
release-mici `f7db927c728bab57bb1263e05465766a8f28fc9d`, to preserve its
compiled camera, tinygrad, model and messaging compatibility. The boot
checkout `/data/openpilot` is unchanged.

Copy `openpilot/jetlink_adapter.py`, this directory and the pinned
`jetlink_repo` into that separate release copy, using LF line endings.
Then, **inside that copy**, run:

```sh
python3 tools/jetlink/apply_release_overlay.py
ln -sfn jetlink_repo/jetlink jetlink
PATH=/usr/local/venv/bin:$PATH PYTHONPATH=$PWD \
  /usr/local/venv/bin/scons -j4 openpilot/common/libparams_c.so
PYTHONPATH=$PWD /usr/local/venv/bin/python3 -m unittest discover -s tools/jetlink -v
```

The overlay refuses the live boot checkout, an unexpected release, or an
already-patched file. It changes only the model-loop seams and parameter
keys; the other integration files are the same as this branch. This is an
overlay test, not validation of a complete development-branch device build.

## Validation and next work

The adapter has six tests covering the Jetlink contract, hook placement,
normal-mode gating, private namespace requirement and missing-dependency
fallback. Jetlink's fork adds five USB-owner setup tests; its openpilot suite
passed 659 tests and 198 subtests, with two skipped on macOS. The adapter
tests also ran against the comma's compiled runtime.

Hardware evidence belongs in `bench-results.json` beside this document.
Frame CSV, owner/modeld logs and resource samples remain in the experiment
directories on the comma and Mac.

Before any driving integration: validate a complete fork build; measure
USB 3 negotiation and sustained latency under recording/driver-monitoring
load; compare recorded-route outputs; test cable removal, stalled host and
recovery; then implement manager ownership, UI/status, shutdown and model
transition handling. This bench does not qualify vehicle actuation or
closed-course driving.
