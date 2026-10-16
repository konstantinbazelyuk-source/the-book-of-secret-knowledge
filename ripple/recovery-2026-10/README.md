# Ripple historical research recovery — October 2026

This directory publicly documents the **retrieved Ripple project family** from the owner's ChatGPT Library, including renamed/derived research (Charlie, MUSHROOM, Ring of Mushrooms, Kokoro/Ripple integrations) and versions predating the currently installed Dell runtime.

## Publicly committed in this directory

- [COMPLETE_PROJECT_CATALOG.md](COMPLETE_PROJECT_CATALOG.md): grouped release descriptions, historical versions and evidence classifications.
- [ARCHIVE_CATALOG.csv](ARCHIVE_CATALOG.csv): 104 archive records including original filename, full SHA-256, size, ZIP integrity check, and archived project overview.
- [LOOSE_FILE_INDEX.csv](LOOSE_FILE_INDEX.csv): 331 standalone/supporting files with hashes and classification.

**Publication scope:** These files describe and authenticate recovery records. They are **not** the 104 original ZIP archives or the eleven consolidated download bundles. Until GitHub Release assets are separately uploaded and independently verified, do not report those binaries as publicly available. The existing [Ripple native desktop source](../native-alpha-v2.0/), [genetic weights](../genetic-weights-v1.7/) and [mathematics](../docs/MATHEMATICAL_STUDY.md) are already published in this repository.

## Recovered files and reproducibility

- 104 ZIP entries representing 98 SHA-256-unique archives; six pairs are exact duplicates.
- 6,974 ZIP member records were indexed in the private recovery workspace.
- 331 extra files were recovered or collected for review; **not all are proven Ripple descendants**.
- ZIP CRC validation confirms readable archive structure, not code correctness, scientific replication, safety, real sensor results, or phone/Dell deployment.
- Original projects are not merged together, overwritten, or relabeled as one functioning application.

## Publishing full source packages

The full recovery was divided into eleven ZIP bundles (`00_` through `10_`) for distribution. Several are larger than GitHub's regular 100 MB Git-object limit; use **GitHub Releases**, not a normal Git commit. GitHub Releases supports release assets under 2 GiB each. The [checksum-verified cross-platform upload helper](upload_release_bundles.py) expects those eleven bundles in a local directory (default: current directory) and the checksum manifest alongside the script, checks that all expected filenames are present, and uses `gh release create` / `gh release upload` on an authenticated machine. **This helper is published, not executed in this GitHub connector session.**

Download bundles from the source owner, preserve them unchanged, then review inherited third-party licenses and ensure materials intended to remain private are not included before publishing assets. A checksum list for release bundles should accompany public assets.

## Precise project status

Only call a release an executable software model where that project's original test documentation supports it. A simulated neural, optical, EEG or motor signal is not an empirical hardware measurement. Renamed or borrowed architectures must retain original attribution and archived source hashes. Some Kokoro-only modules are context material, not independently demonstrated Ripple descendants.

## Repository preservation

This directory was added without changing the repository root README, LICENSE, earlier Ripple installation files, or current executable source.