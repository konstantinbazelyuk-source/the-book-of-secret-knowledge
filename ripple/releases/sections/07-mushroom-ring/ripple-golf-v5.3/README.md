# Ripple Ring × Golf — Software Interoperability v5.3

**Working integration of two existing executable systems.** The inherited Ring of Mushrooms FieldSphere v5.2 and Golf Ripple Dell v0.5 sources are retained unmodified inside `inherited/`.

## What executes

- Real OpenCV decoding, or an actual local camera if the host has one.
- The existing 8-colony / 216-neuron Ring, via `workstation.engine.Workstation.process`. Every frame and its model output is recorded in the inherited SQLite observation schema.
- An explicit event gate on original Ring `spike_marker`, per-frame spike count, active-region count, cooldown and maximum event count.
- The **actual Golf v0.5 job scheduler**, restricted workspace file-write and hash-verification operations, with persistent Golf SQLite jobs and events.
- An **opt-in** local application launch using Golf's `app_run` with an exactly configured Python executable and fixed argv. The bundled receiver validates model-event consistency and writes a separate event inventory JSON. No dynamic shell command or network call is constructed from neuron activity.
- An **opt-in** invocation of the **unchanged Golf Digital Eyes v0.2** parser on the actual inherited `src/engine.py` source file. It returns static source symbols/imports and SHA-256, not arbitrary code execution or unbounded semantic understanding.
- Tkinter desktop controls and a CLI that call the same computation; no decorative simulator backend.

## Quick start

Python 3.11+ (verified here with 3.13), OpenCV, NumPy, psutil and Node.js 20+ recommended for inherited functionality. In a terminal, from the extracted root:

```
python -m pip install -r requirements.txt
python -m bridge.cli replay --frames 24 --out results/my_run.json
```

The example video is a **generated, archived** video from the Ring v5 research. To analyze an authorized recorded video:

```
python -m bridge.cli replay --video /path/to/recording.avi --frames 120 --out results/replay.json
```

To enable the actual OS program bridge and inherited Digital Eyes code inspection, **explicitly** opt in:

```
python -m bridge.cli replay --frames 24 --external-app --inspect-code --out results/connected.json
```

For a physical webcam (requires an accessible camera; no fallback to simulation):

```
python -m bridge.cli camera --device 0 --frames 120 --external-app --out results/webcam.json
```

Interactive GUI (Linux/macOS with a graphical session, or Windows with Tkinter):

```
python -m bridge.gui
```

On Windows the included `START_WINDOWS.cmd` starts the GUI. On Linux use `./START_LINUX.sh`.

No Golf subprocess automatically gets general command-execution permission. The external receiver is a fixed Python script with a constant argument pointing into the bounded Golf workspace. By default this optional application execution and Digital Eyes inspection are **off**. Golf's audited `file_write` and `file_digest` still run when the Ring emits a matching event.

## Data and evidence

- The Ring workstation database is `<runtime>/observations.sqlite`. The Golf job/event ledger is `<runtime>/golf/golf.sqlite3`.
- Triggered events are immutable `<runtime>/golf/workspace/events/*.json`, followed by verified SHA-256 digests.
- Approved external receiver output is `<runtime>/golf/workspace/ring_event_inventory.json`.
- Each event records 8 region spike counts, total, marker, originating frame's bytes digest, phase-order variable, declared source and a timestamp.
- Default active controls: two active regions, four spikes, inherited marker debouncing, 3-frame cooldown, no more than 10 actions in a session. These are engineering choices, not a learned policy.
- Inherited source hashes and file counts in `results/source_audit.json`, tests in `results/bridge_tests.log`, `results/gui_smoke.log`, and `results/inherited_*_test.log`.
- `runtime_data`, `runtime_gui` and private session data are **not shipped** with the release. A new local SQLite record is created at runtime.

## Actually executed in development container

- 24 real OpenCV decoded **synthetic-video** frames; 357 computed neuron spikes; 6 real Golf event files; 6 Golf `app_run` launches with exit code zero; 6 inherited Digital Eyes static inspections; zero bridge errors.
- 18 new regression tests, GUI interaction under Xvfb using the actual Tk callbacks, and 78 inherited Ring/FieldSphere/Golf tests (38 + 26 + 14).
- A separate Ring-to-Golf ablation ran equal 24-frame input through enabled and disabled event gates: inherited Ring spike counts matched exactly, while the disabled gate performed zero Golf actions.
- No actual user's Dell or Samsung, external camera, magnetic instrument, network service, or GUI application other than the bundled receiver was physically validated.

## Scientific interpretation

The release **implements executable inter-process interoperability**. It is not a new intelligence model: internal spikes only trigger a predefined, bounded policy that performs specific approved software operations. Golf's receiver is a real external process that transforms a real input event ledger into a separate validated inventory. Digital Eyes performs real syntax parsing. Neither is evidence of general program understanding.

## Tests

```
python -m unittest discover -s tests -p 'test_*.py' -v
```

For the graphical check on Linux, start a display server (or `Xvfb`) and run `python tests/gui_smoke.py`. Run inherited tests as documented in the packaged `inherited/` trees.

## Version continuity

- All Ring v5.2 and Golf v0.5 source files remain under `inherited/`, without edits.
- All new bridge code is under `bridge/` and `tools/`; no changes were made to inherited model equations or source files.
- Standalone complete release includes all inherited sources. Add-on package needs the original inherited archives extracted into `inherited/` as specified.
- Newly written code: MIT. Archived libraries retain their original licenses.

## Future engineering gate

Measure reliability of `Golf` actions using an actual user-approved external program on the Dell; verify Windows Tkinter and process launch; optionally add strict adapters for a named application's documented API (instead of uncontrolled desktop clicking). This can be tested without hardware sensors by using real filesystem and OS process feedback.