#!/usr/bin/env python3
"""Utility for fetching the Cyrillic-capable font used by bundled mods.

The repository intentionally excludes the Noto Sans Regular TTF binary so that
pull requests stay lightweight.  This helper downloads the upstream font and
copies it into every location expected by OWML and the packaged mods.
"""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request
from typing import Iterable

FONT_URL = (
    "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/"
    "NotoSans-Regular.ttf"
)
FONT_SHA256 = "b85c38ecea8a7cfb39c24e395a4007474fa5a4fc864f6ee33309eb4948d232d5"
FONT_FILENAME = "NotoSans-Regular.ttf"

REPO_ROOT = Path(__file__).resolve().parent.parent
FONT_TARGETS = [
    REPO_ROOT / "OWML_fonts_patch" / "Fonts" / FONT_FILENAME,
    REPO_ROOT
    / "OWML_fonts_patch"
    / "Mods"
    / "PacificEngine.CheatsMod"
    / "Fonts"
    / FONT_FILENAME,
    REPO_ROOT
    / "OWML_fonts_patch"
    / "Mods"
    / "clubby789.OWClock"
    / "Fonts"
    / FONT_FILENAME,
]


def sha256_digest(data: bytes) -> str:
    """Return the hex encoded SHA-256 digest of ``data``."""

    return hashlib.sha256(data).hexdigest()


def existing_font_bytes() -> bytes | None:
    """Return cached font bytes if a valid copy already exists on disk."""

    for target in FONT_TARGETS:
        if not target.exists():
            continue
        try:
            data = target.read_bytes()
        except OSError as exc:  # pragma: no cover - defensive
            print(f"Warning: could not read {target}: {exc}", file=sys.stderr)
            continue
        digest = sha256_digest(data)
        if digest == FONT_SHA256:
            return data
        print(
            f"Existing font at {target} has unexpected hash ({digest}); replacing.",
            file=sys.stderr,
        )
    return None


def download_font() -> bytes:
    """Download the upstream font and validate its checksum."""

    request = urllib.request.Request(
        FONT_URL, headers={"User-Agent": "OWML-font-fetcher/1.0"}
    )
    try:
        with urllib.request.urlopen(request) as response:
            payload = response.read()
    except urllib.error.URLError as exc:  # pragma: no cover - network failure
        raise RuntimeError(f"Failed to download {FONT_URL}: {exc}") from exc

    digest = sha256_digest(payload)
    if digest != FONT_SHA256:
        raise RuntimeError(
            "Downloaded font does not match expected SHA-256. "
            f"Expected {FONT_SHA256}, got {digest}."
        )
    return payload


def ensure_targets(font_bytes: bytes, force: bool = False, dry_run: bool = False) -> None:
    """Copy ``font_bytes`` into each required location."""

    for target in FONT_TARGETS:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and not force:
            try:
                existing = target.read_bytes()
            except OSError as exc:  # pragma: no cover - defensive
                print(f"Warning: could not read {target}: {exc}", file=sys.stderr)
            else:
                if sha256_digest(existing) == FONT_SHA256:
                    print(f"{target}: up to date")
                    continue
                print(f"{target}: checksum mismatch, refreshing")
        if dry_run:
            print(f"Would write font to {target}")
            continue
        tmp_path = target.with_suffix(target.suffix + ".tmp")
        with tmp_path.open("wb") as handle:
            handle.write(font_bytes)
        os.replace(tmp_path, target)
        print(f"Wrote {target}")


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing fonts even if the checksum already matches",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="display actions without writing any files",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    font_bytes = None if args.force else existing_font_bytes()
    if font_bytes is None:
        font_bytes = download_font()
    ensure_targets(font_bytes, force=args.force, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
