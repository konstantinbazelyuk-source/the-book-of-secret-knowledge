# Kokoro v1.6 — Installed visual-goal action and colony-worker repair

This component is installed under `exports/installed_visual_action_v1_6/` of the **existing Shipyard v1.2 cargo**. Original code and source packages are unchanged. No new Shipyard version is required.

## Capability

A recorded VTK-generated 3D RGB image contains diagnostic red/green/blue markers at known joints. The **original v2.3 source** measures marker pixels and fits 3D joint angles to those pixels. Two existing distinct source-authenticated 10° and 40° movement frames establish a *bounded software calibration*. An unseen 25° or 32° rendered goal frame is measured without its original action label. The fitted command is sent to the **original v2.3 motor**, then the **original Spatial Episodic Memory, Ripple XYZ encoder, Reality Anchor, and Spatial Information Colony** process and persist the result.

Golf Ripple Digital Eyes v0.2 is also executed on the actual image bytes to compute meaningful RGB, edge, sharpness and image-hash metrics. These features are recorded and checked, not asserted to recognize identity or jointly infer joint angles.

### Why the interrupted 32° integration now works

The original information-colony worker `job_calc` is defined in a real Python source file, `colony.py`. The previous integration loaded that file through a temporary import module. Python's process-pool `spawn` could not import/serialize that temporary symbol. We instead launch the unchanged installed `colony.py` as a subprocess by its stable path, so `spawn` child processes can import the original worker. The 32° end-to-end test executed with two distinct child process IDs and exactly matched a serial reference. The 25° run requested two workers but only one PID got work; resource accounting does not infer distribution that did not occur.

### Workflow

Extract cargo with existing Shipyard's **Open Cargo ZIP**. For terminal operation provide existing unmodified v1.2 Shipyard folder and extracted project:

```
python exports/installed_visual_action_v1_6/visual_action.py --project PROJECT --shipyard SHIPYARD measure PROJECT/exports/installed_visual_action_v1_6/goal_source_32_render.png
python exports/installed_visual_action_v1_6/visual_action.py --project PROJECT --shipyard SHIPYARD act PROJECT/exports/installed_visual_action_v1_6/goal_source_32_render.png --workers 0
```

`--workers 0` defaults to serial execution for the current small colony jobs because measured process startup is slower than serial execution. `--workers 2` is retained for explicit worker verification.

### Tests after moving the cargo

The included tests are project-relative, not tied to the development machine. Set `KOKORO_TEST_SHIPYARD` to the existing extracted Shipyard v1.2 directory when it is not beside the extracted project, then run:

```
python -m unittest discover -s exports/installed_visual_action_v1_6/tests -v
```

On Windows you can also run `exports\installed_visual_action_v1_6\RUN_VISUAL_GOAL_WINDOWS.bat` with `KOKORO_SHIPYARD` set appropriately. It runs a known virtual goal image and records a new episode; no physical robot is controlled. An actual Dell installation has not been executed here.

### Acceptance evidence

See `ACCEPTANCE_EVIDENCE.json`, `action_*.json`, `tests/test_visual_action.py`. Image-goal decisions are from actual stored PNG pixels and original geometric inversion, not filenames or test labels. The source target renders were generated separately by the original virtual motor and reserved as held-out inputs. Baseline nearest-remembered-action pose errors are compared against replay after measured image pose inference. A target equal to calibration imagery is rejected for independent test claims. Missing fiducials or out-of-calibration positions block motor execution.

### Limits

This is mathematically executable 3D image feedback with known virtual landmarks. The final errors are from same-renderer deterministic numerical playback, not real hardware. No markerless vision, unknown-camera recovery, external sensory generalization, original learned Psyche, or original trained Core has been validated. Memory databases are SQLite, with the continuity checkpoint protected separately by original Ripple Repair.
