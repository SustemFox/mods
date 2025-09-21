# OWML Cyrillic font helper

The mods bundled in `OWML_fonts_patch` rely on [Noto Sans Regular](https://fonts.google.com/specimen/Noto+Sans) so that the
configuration menus and overlays can display Cyrillic characters.  The upstream font is more than half a megabyte, so it is kept
out of version control to keep pull requests reviewable.  Instead, run the helper below whenever you clone or update the patch.

```bash
python scripts/install_fonts.py
```

The script downloads the official font file from the Google Fonts repository, verifies its SHA-256 hash, and copies it into every
location the packaged mods expect (`OWML_fonts_patch/Fonts/` and each mod's `Fonts/` folder).  Rerun it with `--force` if you ever
need to refresh the files, or with `--dry-run` to preview the affected paths.

After downloading the font you can optionally run the quick check in `tests/test_fonts.py` to make sure the Cyrillic glyphs that
the mods depend on are present:

```bash
python scripts/install_fonts.py  # populate font files
pip install --user fonttools      # one-time dependency for the verification script
python -m tests.test_fonts
```

The helper downloads the font under its original SIL Open Font License; no local modifications are made.
