# Ripple — Laptop runtime and verified research code

## Public archive & mathematical registry (updated 20 October 2026)

- **[Recovered Ripple/Charlie versions and release-status audit](releases/README.md)** — full inventory of published source, standalone artifacts, and Library archives that still need public ZIP publication.
- **[33 archived executable HTML and replay files](standalone-archive/README.md)** — historical offline implementations and viewers; runtime compatibility varies.
- **[Recovered mathematical studies](mathematics/library-2026-10-20/README.md)** — 30 documented studies supplementing the existing 171-entry formula registry, with duplicate/assumption caveats.
- **[Original curated mathematics registry](mathematics/FORMULA_REGISTRY.json)** — approved formulas remain unchanged; supplemental study documents are referenced separately.


## Public browser laboratory

The original neuron runs directly in JavaScript in the [public research site source](../docs/index.html), alongside five archived, standalone Alpha experiment explorers. The site's files are also prepared for GitHub Pages publishing from `master /docs`.

**Hosting status:** Source files are public through GitHub. A public `github.io` website URL must be independently verified after GitHub Pages is enabled in repository settings; the presence of the HTML files alone is not a deployment.

**Study limitations:** The neuron outputs are calculated model events. Archived Alpha demonstrations use synthetic data, not calibrated physical sensors or measured cognition.


This is an **independent software subdirectory** of *The Book of Secret Knowledge*. Existing book contents remain untouched. This directory is not a claim that the original reference-book author authored Ripple.

## Install on a Dell / Windows 10 or 11

Install Python 3.11+ and Node.js 20+. Download or clone the whole repository, then open PowerShell **in `ripple/native-alpha-v2.0`** and run:

```powershell
.\bin\Setup-Dell.ps1
.\bin\Start-Ripple-Windows.cmd
```

Visit `http://127.0.0.1:8765`. Retrieve the locally generated token from `%LOCALAPPDATA%\RippleLaptop\local_api_token.txt` (do not commit that token). The setup generates `dell_probe_local.json` with hardware information from the machine actually running it.

To run the v1.7 genetic-composition experiment, use:

```powershell
.\.venv\Scripts\python.exe -m ripple_native submit v17_composition '{}'
```

The installed source-only v1.7 sibling is integrity-checked, and its synthetic cases are regenerated with a checksum matching the archived study.

For a Linux development machine, install the dependencies in `ripple/native-alpha-v2.0/requirements.txt` and run `python3 -m unittest discover -s tests -p 'test_*.py'` from the runtime folder.

## Contents and evidence

- [`native-alpha-v2.0/`](native-alpha-v2.0/) — **runnable** Python desktop runtime: job/process management, authenticated localhost HTTP, SQLite, workspace operations, restricted registered apps, Ripple neuron and quaternary execution, and optional PyTorch workloads. Windows/Dell hardware has **not yet been verified**.
- [`genetic-weights-v1.7/`](genetic-weights-v1.7/) — **runnable** preserved mathematical program composition and case generator, packaged as source files without heavyweight cached experimental data. Only one approved entrypoint executes in the laptop runtime.
- [`docs/MATHEMATICAL_STUDY.md`](docs/MATHEMATICAL_STUDY.md) — 56-formula recovered mathematical codex.
- [`mathematics/README.md`](mathematics/README.md) — unified 171-formula registry, original/derivative lineage, Charlie and Kokoro mathematical integrations, Samsung optical reconstruction, and source evidence. Its descriptions distinguish original equations, derived relationships, and synthetic experiments.
- [`SOURCE_INTEGRITY.json`](SOURCE_INTEGRITY.json) — source checksums, independently verifiable.
- [`RELEASE_CATALOG.md`](RELEASE_CATALOG.md) — earlier Ripple branches and status. Not all past branches are installed by this checkout.

### What remains separate

This folder does not bundle all historical Ripple archive packages or represent every prototype as executable. Physical sensor integrations, robot operation, GPU performance on Dell and cloud deployment remain **unverified**. The original v0.1 LIF equations are unchanged.

### Security

The software runs under your user account, not as a privileged operating-system service. Do not expose the localhost token or open the local port to the internet. External JavaScript and installed applications require separate authorization. Windows startup-task registration is opt-in. No paid cloud service is enabled by this repository.

## Calcium battery engineering lab

- [`battery-lab/v1/`](battery-lab/v1/) — tested Python electrochemical calculations plus an offline Samsung-compatible browser measurement interface. Scientific lineage: recovered 2024 calcium-ion equations and later battery sizing; the software can integrate external physical I/V CSV recordings. Peer-reviewed calcium-cell observations are recorded separately from Ripple-generated calculations. **No physical calcium cell has been fabricated or measured by this project.**

## Recovered derivative sources, concepts and milestones (October 2026)

- [Concept and lineage register](concepts/CONCEPTS.md): 33 individually described software, mathematical and research concepts, including unfinished corporate execution plans.
- [Milestone and negative-result ledger](concepts/MILESTONES.md): 34 recorded version/milestone checkpoints.
- [Additional source-traced formulas](mathematics/ADDITIONAL_MATHEMATICS.md): 20 deduplication candidates alongside the existing historical registry.
- [Full source coverage and verification notes](concepts/SOURCE_COVERAGE.md): 44 distinct research archives, 1,014 curated code/test/documentation files.
- [Restorable source capsules](source-capsules/): SHA-256-verified source-only snapshots, restoration script and tests.
- [GitHub downloadable source-only release](https://github.com/konstantinbazelyuk-source/the-book-of-secret-knowledge/releases/tag/ripple-lineage-source-2026-10-20).

The historical binary ZIPs, hardware requirements and private/corporate records were not silently imported into this public source-only release.
