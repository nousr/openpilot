# Low-speed turn intent

This branch adds explicit `turnLeft` / `turnRight` inputs to the driving policy
on top of `jetlink-usb-bench` at `5e29d4fe3`, including the manager integration,
Mac Chestnut home-screen readiness UI and executable-mode fixes.
The feature is off by default. It is an experimental input to the model, not a
90-degree trajectory generator, navigation system, or increase in Ford steering
authority. Ford/opendbc, Panda safety, longitudinal control and engagement rules
are unchanged. In particular, this does not add MADS or steering while disengaged.

## Enable when ready

In a **full build of this branch**, open Settings → Toggles → **Low-Speed Turn
Intent (Experimental)**. The `LowSpeedTurnDesire` setting is read at modeld start;
the toggle uses the existing restart mechanism and is unavailable while engaged.
Leave it off for baseline comparisons. Turn intent is separate from the
`JetlinkLink=1` setting that enables the USB owner in the normal manager.
Changing the turn-intent setting does not enable Jetlink or deploy this branch.

The older `apply_release_overlay.py` only applies the original isolated Jetlink
bench seams. It does **not** install this feature; use the full branch build.
The parked bench does not publish live `carControl.latActive`, so a parked latency
run alone cannot demonstrate turn activation.

## Initial settings

Both directions deliberately use the same intent gates. There are no measured
Mach-E results yet that justify different left/right settings.

| Gate | Initial value | Purpose |
| --- | --- | --- |
| Start below | 15 mph / 24.1 km/h | Includes approaches that were above the old 10 mph cutoff |
| Minimum moving speed | 0.5 m/s / 1.1 mph | Wait through a stop instead of spending the pulse at a red light |
| Stable signal | 0.3 seconds | Reject very brief signal inputs |
| End tracking at | 20 mph / 32.2 km/h | Allow acceleration through the turn without issuing a lane change |
| Maximum tracking after pulse | 20 seconds | Bound the active intent latch; no automatic repeat |
| Signal off to rearm | At least 0.5 seconds | Prevent repeats from brief signal dropouts |

These are **initial test settings, not vehicle-validated tuning or target speeds**.
They live in `openpilot/selfdrive/controls/lib/turn_desire_helper.py` and use the
20 Hz model-loop timestep. They do not slow the car. Required conditions are:
valid/recent carState and carControl, active lateral assistance, drive gear, a
single signal, no blind-spot indication on the indicated side, and no opposing
driver steering input. An already-starting lane change retains its existing logic,
and a signal used to start a lane change cannot also request a turn until released.

An existing signal can arm as the car slows below 15 mph. The helper can wait
while stopped. Once moving, it emits **one frame** of the corresponding turn
desire. The stock and Jetlink model runners convert that to a rising-edge pulse
in the policy input vector: slot 1 for `turnLeft`, slot 2 for `turnRight`.
Lane-change desires use separate slots 3 and 4 and retain the existing
20 mph threshold and driver torque confirmation.

After a turn has armed, loss of lateral activity or input validity, a non-drive
gear, hazards, a direction flip, the corresponding blind spot, or opposing driver
steering blocks further requests for that held signal. Releasing both signals for
at least 0.5 seconds rearms it. Acceleration or timeout also blocks that held
signal from becoming a lane change. No repeated pulses are sent during a turn.

The `active` helper state tracks the consumed signal; it does not continuously
instruct the model to turn. The recurrent model decides when its maneuver is
complete. Clearing the helper state, reaching a speed threshold, or cancelling
the signal does **not** erase intent already received by the model. **Disengage
to cancel steering assistance.** Blind-spot gating is not an intersection-clearance
check and does not detect all cross traffic, pedestrians or cyclists.

## Verify the intent before testing steering

1. Build the full branch, including the updated params library. Run the tests
   below. Confirm the default toggle is off, enable it while disengaged, and
   confirm modeld logs `low-speed turn desires enabled: True` after restarting.
2. In replay or a bench with synthetic car messages, verify a stopped signalled
   approach remains `armed`, moving produces one `active` transition, and release,
   hazards, disengagement and stale inputs behave as described. Use an isolated
   messaging/params prefix, as in the existing Jetlink bench.
3. Check `low_speed_turn_desire` entries in modeld logs. They record helper state,
   direction (1/2), desired input and speed. `active` records the pulse scheduled
   for the next inference; it is **not** proof the remote policy received it or
   that steering followed it. `modelV2.meta.desireState` is the model's prediction,
   not this input signal. Lane-change metadata stays off for turns.
4. Before vehicle actuation, validate turn intent with the inherited Jetlink
   manager integration and its timing, fallback and disconnect handling. A skipped/busy USB inference
   can miss an intent pulse; this branch does not retry it automatically. Confirm
   delivery in the transport/input trace as well as the helper log. After an
   interruption, disengage and start a fresh attempt rather than relying on the
   old turn intent carrying across a model swap.
5. For subsequent closed-course left/right trials, keep model/controller versions
   fixed, control entry speed, and log requested curvature, outgoing limited
   curvature, measured yaw/steering response, model execution time and driver
   intervention. Compare feature off/on on the same geometry. A correct policy
   turn request with a clipped outgoing command is a controller-authority issue;
   changing these intent thresholds does not resolve it.

The current Ford controller still uses its curvature-only path and existing
limits. This branch alone cannot establish that a tight right or left turn is
achievable. Ford path-angle control remains a separate integration.

## Automated checks

In an openpilot development environment with the pinned opendbc and Jetlink
submodules available on the Python path:

```sh
python -m unittest openpilot.selfdrive.controls.tests.test_turn_desire tools.jetlink.test_turn_desire_input tools.jetlink.test_adapter -v
ruff check openpilot/selfdrive/controls/lib/turn_desire_helper.py openpilot/selfdrive/controls/lib/desire_helper.py openpilot/selfdrive/controls/tests/test_turn_desire.py tools/jetlink/test_turn_desire_input.py openpilot/selfdrive/modeld/modeld.py openpilot/selfdrive/ui/layouts/settings/toggles.py
```

The policy-input test runs the pinned Jetlink input packer with camera/GPU/USB
boundaries mocked. It checks the real enum encoding and edge conversion, not a
CoreML prediction, physical USB transfer, or vehicle response.

Local validation on November 9, 2026: all 31 tests above passed on Python 3.12,
along with Ruff, Python compilation of modeld/settings and `git diff --check`.
With the feature disabled, all helper outputs and lane-change state matched the
original branch over 10,000 seeded randomized input frames.
The adapter contract test exercised its fallback for unavailable native messaging
bindings on the Mac. No full device build, live UI, CoreML inference or vehicle
actuation was tested for this change.

Rebase validation on November 10, 2026 against `jetlink-usb-bench` at `5e29d4fe3`:
49 turn-desire, policy-input, adapter and Jetlink guard tests passed, using the
pinned Jetlink revision `88a9f8969947e6c984b2766f5db531d86f840582`. Ruff,
Python compilation (including the inherited home-screen change), diff whitespace
checks and the inherited executable modes also passed inspection. The native
engagement-event suite, live UI and device build were not rerun on this Mac.
