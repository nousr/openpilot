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
  --seconds 300 --record --resources
```

Use a new output directory each time. `--small` measures the comma's local
model without starting the USB owner. The runner reads the real device's
offroad flag and saved vehicle/calibration parameters before entering a
private params and messaging namespace. It starts the USB owner, camerad,
modeld and optional resource sampler. `--record` also starts logmessaged,
loggerd, encoderd, dmonitoringmodeld and dmonitoringd. It checks for valid
driver-model and monitoring-policy messages and recordings from all three
cameras; runs of at least 150 seconds must exercise segment rotation.
It stops if the real offroad
flag changes or a child exits. No controls or pandad process is started.
The owner setting is cleared before shutdown so it restores its USB/VM
tuning. Jetlink keeps USB input current cut while a host remains attached;
the comma therefore continues to require its separate power supply.

## Installed development fork

On 2026-11-09, the complete `nousr/openpilot:jetlink-usb-bench` fork was
installed on the comma four at integration commit
`f3046cb2c436f384a9bdce6bce730e9f88bf93f3`, pinning
`nousr/jetlink:mac-chestnut` at
`903123938148e63d7b5c2fb2ccac86fe1ef51eec`.

`/data/openpilot` points to `/data/jetlink-bench/full-openpilot`. The previous
release checkout was preserved at `/data/jetlink-bench/stock-openpilot-f7db927`.
The official AGNOS updater installed and hash-verified version 20.3 in slot A;
slot B retains the previous OS. Both the initial build and the native rebuild
after reboot completed. The checkout has its own `.venv`, with its interpreter
and dependency cache under `/data/jetlink-bench` so they survive an OS update.
The launch script and bench wrapper select that environment when available.

Normal offroad startup was checked through `deviceState`, `managerState` and
`pandaStates`, including the UI, hardwared and pandad. Automatic updates are
disabled for this development checkout; upstream `updated` intentionally exits
when `DisableUpdates` is set. Six adapter tests and 235 params/messaging tests
passed on the device runtime. Installing this fork does not enable Jetlink in
the normal driving manager: the private benchmark gate remains in place.

## Earlier installed-release test copy

The first hardware tests used `/data/jetlink-bench/openpilot`, a separate copy
of release-mici `f7db927c728bab57bb1263e05465766a8f28fc9d`, to preserve its
compiled camera, tinygrad, model and messaging compatibility. At that stage
the boot checkout was unchanged. This directory is retained as historical
evidence; current tests use the installed development fork described above.

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

The initial release-overlay evidence is in `bench-results.json`; complete-fork
evidence is in `full-fork-results.json`. Frame CSV, owner/modeld logs and
resource samples remain in the experiment directories. Camera recordings and
device settings are not committed to either fork.

### Full fork on AGNOS 20.3

The five-minute USB 3 workload included recording from all three cameras,
driver-model inference and the monitoring policy. It published 5,813
large-model frames and produced five complete recording segments. Excluding
the first ten large-model frames, execution time was 28.90 ms median,
31.22 ms p99 and 34.97 ms maximum, with zero frames over 50 ms. The first
large-model frame took 53.08 ms. The local model also had a cold-start spike.

After the first large-model second, camera frame IDs were consecutive, all
model messages were valid, and the largest subscriber-observed arrival gap
was 69.50 ms. Camera EOF to publication was 53.15 ms median and 55.52 ms p99;
this is a different measurement from model execution time. There were no
held-frame log entries. Driver-model output ran at 19.99 Hz, with 5,955 valid
frames; monitoring-policy messages became valid after the driving model
started. System available memory remained above 1.81 GiB.

A separate two-minute recording run froze the Mac server with SIGSTOP for
20 seconds. The comma held five predictions, switched to its local model,
and rejoined Chestnut after SIGCONT. The first local frame took 27.68 ms;
the gap between published messages at that transition was 79.92 ms. One
camera frame ID was missing during the run, despite the filtered drop
counter staying at zero. Held predictions are explicitly separate from
fresh inference and from missing messages.

A third recording run physically disconnected the data cable for about
76 seconds while keeping separate power connected. The fallback frame's
published execution time was 39.04 ms (the inner fallback log measured
38 ms), with a 60.10 ms message-arrival gap. Reconnecting the same cable
restored USB 3 and Chestnut rejoined automatically; that first rejoin frame
took 51.51 ms. After startup, there were no missing camera frame IDs or
invalid model messages in this run, which produced three complete segments.

### Earlier release-overlay results

The three-minute USB 3 run published 3,449 large-model frames. Excluding the
first ten large-model frames, execution time was 28.95 ms median, 31.18 ms
p99 and 37.54 ms maximum, with zero frames over 50 ms. The first large-model
frame took 51.97 ms; local-model cold startup also has a separate spike.
USB 2 measured 37.97 ms median and 40.02 ms p99 after the same exclusion.
Replacing the cable changed both endpoints from USB 2 to USB 3.

A separate USB 2 test stopped the Mac server with SIGTERM, left it stopped
for about 21 seconds, then restarted it. Predictions switched to the local
model and back to the large model. This tests host process recovery, not a
physical cable pull or an indefinitely stalled host.

Next work is recorded-route numerical parity, longer thermal/load tests,
and normal-manager integration with ownership, UI/status, shutdown and
model transition handling. In particular, expose held-output age and the
engagement restrictions around fallback/rejoin instead of relying only on
message validity or the filtered drop counter. This bench does not qualify
vehicle actuation or closed-course driving.
