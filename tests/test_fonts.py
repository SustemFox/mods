"""Sanity checks that the downloaded fonts cover the mod's Cyrillic text."""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from typing import Iterable

try:
    from fontTools.ttLib import TTFont
except ImportError as exc:  # pragma: no cover - dependency guard
    raise SystemExit(
        "fontTools is required for this check. Install it with `pip install fonttools`."
    ) from exc

from scripts import install_fonts

REPO_ROOT = Path(__file__).resolve().parent.parent


def _iter_cyrillic_characters(strings: Iterable[str]) -> set[str]:
    characters: set[str] = set()
    for text in strings:
        for char in text:
            if "CYRILLIC" in unicodedata.name(char, ""):
                characters.add(char)
    return characters


def load_required_characters() -> set[str]:
    """Collect the Cyrillic characters present in the mod configuration."""

    cheats_config = REPO_ROOT / "OWML_fonts_patch/Mods/PacificEngine.CheatsMod/config.json"
    clock_config = REPO_ROOT / "OWML_fonts_patch/Mods/clubby789.OWClock/config.json"
    clock_events = REPO_ROOT / "OWML_fonts_patch/Mods/clubby789.OWClock/events.json"

    texts: list[str] = []

    with cheats_config.open(encoding="utf-8") as handle:
        config = json.load(handle)
    for section in config.get("settings", {}).values():
        if isinstance(section, dict):
            texts.extend(
                value for key, value in section.items() if isinstance(value, str)
            )
        elif isinstance(section, str):
            texts.append(section)

    with clock_config.open(encoding="utf-8") as handle:
        config = json.load(handle)
    for section in config.get("settings", {}).values():
        if isinstance(section, dict):
            texts.extend(
                value for key, value in section.items() if isinstance(value, str)
            )
        elif isinstance(section, str):
            texts.append(section)

    with clock_events.open(encoding="utf-8") as handle:
        events = json.load(handle)
    for entry in events.get("eventList", []):
        name = entry.get("Name")
        if isinstance(name, str):
            texts.append(name)
    texts.append(
        "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
        "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    )
    return _iter_cyrillic_characters(texts)


def verify_font_contains(font_path: Path, required_chars: set[str]) -> None:
    """Assert that ``font_path`` includes glyphs for ``required_chars``."""

    font = TTFont(str(font_path))
    try:
        cmap = font.getBestCmap() or {}
    finally:
        font.close()
    missing = [char for char in sorted(required_chars) if ord(char) not in cmap]
    assert not missing, f"{font_path} is missing glyphs for: {''.join(missing)}"


def main() -> None:
    install_fonts.main([])
    required = load_required_characters()
    assert required, "Did not detect any Cyrillic characters to verify."

    for target in install_fonts.FONT_TARGETS:
        assert target.exists(), f"Expected font at {target}"
        digest = install_fonts.sha256_digest(target.read_bytes())
        assert (
            digest == install_fonts.FONT_SHA256
        ), f"Unexpected font hash at {target}: {digest}"
        verify_font_contains(target, required)

    print("All fonts include the required Cyrillic glyphs.")


if __name__ == "__main__":  # pragma: no cover - CLI usage
    main()
