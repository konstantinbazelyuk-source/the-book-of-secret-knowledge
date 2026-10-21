# Kokoro Reality Anchor Memory — v0.1

**Working subsystem:** Persistent, typed *episodic versus meaning* memory with explicit authored relationship tracing and read-only integration envelopes for Kokoro. Python standard library only. This package preserves the existing Kokoro and Ripple code because it installs separately.

## What it does

* Records events with separately typed UTC, simulation/model-clock, and virtual-clock fields. The recorded-UTC time is not mistaken for the event time.
* Keeps physical-space, virtual-space, symbolic, and unlocated data separate. Different XYZ meanings are not silently compared.
* Stores user meanings and competing interpretations as append-only records. No interpretation overwrites the underlying event.
* Links thoughts through authored typed relationships (`transforms_to`, `inspires`, `refines`, etc.), then retrieves the exact documented path across otherwise unrelated vocabulary.
* Prevents unsupported paths from being created by retrieval: a missing link returns **not found**.
* Provides a read-only Kokoro event-v1 adapter, a Ripple signed-state adapter, a digest-bound Psyche-oriented context envelope, and a Oneiric-oriented graph export. **The source programs are not imported into this release; native coupling must be tested with the actual programs.**
* Provides a local browser interface as well as programmatic API and command line commands.

### Run it (Windows / Dell with Python 3.10+)

Extract the entire ZIP to a directory. Double-click `START_WINDOWS.cmd`. The script starts Python's built-in HTTP server bound **only to `127.0.0.1:8765`** and opens `http://127.0.0.1:8765` in the default browser. Close the command window to stop it. Python must be installed and on PATH.

Or from a terminal in this directory:

```sh
python cli.py --db anchor.sqlite3 serve
```

Run tests:

```sh
python -m unittest discover -s tests -v
python demo.py
```

### Quick command line example

```sh
python cli.py --db anchor.sqlite3 record "An observation or a thought" --source user_reported
python cli.py --db anchor.sqlite3 search "thought"
python cli.py --db anchor.sqlite3 context <event-id>
python cli.py --db anchor.sqlite3 interpret <event-id> "An interpretation" --author person
python cli.py --db anchor.sqlite3 link <first-event-id> <second-event-id> --relation transforms_to --note "Stated relationship" --author person
python cli.py --db anchor.sqlite3 trace <first-event-id> <second-event-id>
```

### Connection with the existing Kokoro event contract

Existing `kokoro/contracts/event-v1.schema.json` defines a motor, sensor, camera, or psyche_reference event with `schema: "kokoro/event/1"`, source, classification, model_time_s, and payload. Save a **real event emitted by the original runtime** as a JSON file, then:

```sh
python cli.py --db anchor.sqlite3 ingest-event real_event.json --clock-id studio-v2.3-run-001 --source-ref studio-v2.3/run001/evt-0001
```

Programmatic use in a running authorized Python process:

```python
from anchor import RealityAnchor
with RealityAnchor("anchor.sqlite3") as memory:
    event_id = memory.ingest_kokoro_event(existing_event_dict, clock_id="run-id", source_ref="original-event-id")
    packet = memory.continuity_packet(event_id)  # candidate for actual Psyche adapter
    oneiric_graph = memory.export_association_graph() # read-only candidate for Oneiric
```

For Ripple numeric data, `memory.ingest_ripple_state(clock_id=...,source_ref=...,model_time=...,temporal_signed=...,rg_signed=...,bg_signed=...)` records the **actual passed** signed features with source clock and no invented physical XYZ. Tests confirm validation and persistence, not that a live Ripple stream was connected in this release.

## Important boundaries

**Stored content is plaintext SQLite**, including user-authored reflections. The SHA-256 value detects accidental or unsophisticated uncoordinated changes to an event row; an attacker with database write privileges could recompute it. This subsystem performs neither encryption nor external fact verification. The web application is localhost only, and must not be exposed over the network.

`user_reported`, `hypothesis`, `computed`, `measured_software`, `external_source`, and `example` classify **origin**, not proof of metaphysical or physical claims. Interpretations and derived associations do not become verified facts automatically. Color encoding, spirituality, mind, and consciousness are not injected into the code. The optional example fixture uses only general conversation themes and is explicitly marked as an example.

The meaning graph is an **authored evidence-preserving graph**, not a trained semantic understanding model. It retrieves paths only when links have been supplied. It does not execute Kokoro Core, Oneiric 2.0, Heartspace, or Psyche itself. Device installation and performance have not been measured on Samsung or Dell hardware.

## Integration sequencing

See [`docs/INTEGRATION.md`](docs/INTEGRATION.md). Existing archived sources remain locked. Bring up the authentic Core and boards, ingest actual typed events read-only, compare recalled context against a no-memory baseline, then permit only an explicitly approved, verified interface to influence the Core context. Identity and Genesis source files are not modified.