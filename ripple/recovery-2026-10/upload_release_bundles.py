#!/usr/bin/env python3
"""Publish previously recovered Ripple ZIP bundles as a draft-then-public GitHub Release.

Runs on Windows, macOS or Linux with Python 3.9+ and authenticated GitHub CLI.
No upload occurs without --publish. Does not alter tracked repository source.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

REPO = "konstantinbazelyuk-source/the-book-of-secret-knowledge"
DEFAULT_TAG = "ripple-library-recovery-2026-10-16"


def gh(*args):
    p = subprocess.run(["gh", *args], text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError(f"gh {' '.join(args[:3])} failed:\n{p.stderr.strip()}")
    return p.stdout.strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--directory", type=Path, default=Path.cwd(),
                    help="Directory containing the eleven recovered ZIP bundles")
    ap.add_argument("--tag", default=DEFAULT_TAG)
    ap.add_argument("--publish", action="store_true",
                    help="Explicitly upload bundles and publish a GitHub Release")
    args = ap.parse_args()
    base = args.directory.expanduser().resolve()
    manifest = Path(__file__).with_name("BUNDLE_SHA256SUMS.txt")
    if not manifest.is_file():
        raise RuntimeError("Missing BUNDLE_SHA256SUMS.txt beside this script.")

    expected = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split(None, 1)
        name = name.strip()
        if "/" in name or "\\" in name or Path(name).name != name:
            raise RuntimeError(f"Invalid bundle basename in manifest: {name!r}")
        expected[name] = digest.lower()
    if len(expected) != 11:
        raise RuntimeError(f"Expected 11 bundle records, found {len(expected)}")

    paths = []
    total = 0
    for name, sha in expected.items():
        path = base / name
        if not path.is_file():
            raise RuntimeError(f"Bundle missing: {path}")
        hasher = hashlib.sha256()
        with path.open("rb") as handle:
            while chunk := handle.read(4 * 1024 * 1024):
                hasher.update(chunk)
        if hasher.hexdigest() != sha:
            raise RuntimeError(f"SHA-256 mismatch: {name}; refusing publication")
        paths.append(path)
        total += path.stat().st_size

    print(f"Validated {len(paths)} ZIP bundles ({total:,} bytes) with SHA-256.")
    if not args.publish:
        print("Dry run: no GitHub changes made. Pass --publish to upload.")
        return 0

    if shutil.which("gh") is None:
        raise RuntimeError("GitHub CLI 'gh' is not installed.")
    gh("auth", "status")
    # An existing release is never overwritten; this avoids modifying other assets.
    probe = subprocess.run(
        ["gh", "release", "view", args.tag, "--repo", REPO],
        text=True, capture_output=True
    )
    if probe.returncode == 0:
        raise RuntimeError(f"Release tag {args.tag!r} already exists; refusing overwrite.")

    notes = (
        "Full archived Ripple family recovery: 104 original ZIP records, "
        "98 unique source archives and 331 supporting files across eleven "
        "distribution bundles. See ripple/recovery-2026-10/ for archive hashes, "
        "provenance and evidence boundaries. Some included Kokoro packages are "
        "related context, not verified Ripple descendants. Archived code and "
        "third-party license terms remain those of the respective original sources."
    )
    gh("release", "create", args.tag, "--repo", REPO, "--target", "master",
       "--draft", "--title", "Ripple historical library recovery", "--notes", notes)

    # If an upload fails, the release stays a private draft, never a partial public release.
    for path in paths:
        print(f"Uploading {path.name}...")
        gh("release", "upload", args.tag, str(path), "--repo", REPO)

    assets = json.loads(gh("release", "view", args.tag, "--repo", REPO,
                           "--json", "assets"))["assets"]
    received = {asset["name"]: asset["size"] for asset in assets}
    for path in paths:
        if received.get(path.name) != path.stat().st_size:
            raise RuntimeError(f"Missing or incomplete upload: {path.name}")
    gh("release", "edit", args.tag, "--repo", REPO, "--draft=false")
    print(f"Published and size-verified {len(paths)} assets:")
    print(f"https://github.com/{REPO}/releases/tag/{args.tag}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
