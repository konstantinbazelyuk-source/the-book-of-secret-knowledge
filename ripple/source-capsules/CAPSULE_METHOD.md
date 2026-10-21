# Ripple source capsule method and boundaries

**Original source:** SHA256-identified ZIPs recovered from the project Library and conversation attachments. In the initial collection there were 44 byte-distinct original ZIP files and 1,014 text files chosen for this public, curated source-only distribution. The original ZIPs were not modified.

**Selection:** Read original ZIP members; reject unsafe paths, binary/media, vendored parent archives, checkpoints, results/datasets, dependency directories, files larger than 350 KB, most self-contained HTML bundles larger than 100 KB, and common credential patterns. For each archive, prioritize root README, mathematical documents, tests, and project source; cap selected source at approximately 900 KB per archive. The exclusions are explicitly recorded by `excluded_members` in SOURCE_CAPSULES.json. Every original member retains its original path, file SHA256 and byte length, so earlier versions remain differentiable.

**Cryptographic chain:** Original ZIP SHA256 is recorded for archive provenance; source-only capsule has its own SHA256; its ASCII base64 stored in Git has another SHA256; and every selected source member has a SHA256. Hashes detect corruption/tampering but do not confer legal publishing rights or establish test success. All tools operate offline after download.

**Extraction:** `python ripple/source-capsules/restore_capsules.py --verify` verifies all capsules and members without executing them. `--extract --dest DIR` writes each package into its own subfolder; known changed files are never overwritten. `--only NAME` selects one. `build_source_bundle.py` regenerates the downloadable ZIP and checksum record.

**Testing:** `python -m unittest discover -s ripple/source-capsules -p 'test_capsules.py' -v` checks every capsule, refuses tampered bytes, disallows unsafe paths, and reports exact source-member counts. Historical code-specific tests were **not** all rerun by this archive integrity workflow; dependencies, compiled programs, and asset-heavy products require project-specific build steps.

**Evidence and scope:** The concept and milestone records represent the supported chronological thread and archive survey. No claim of exhaustively searching every archived ChatGPT message, every corporate account, cloud container, or private app is made. FireClay-related concepts are listed, not reconstructed as corporate source code. The binary ZIP archives already cataloged in `ripple/recovery-2026-10/` remain separate and are not republished here.
