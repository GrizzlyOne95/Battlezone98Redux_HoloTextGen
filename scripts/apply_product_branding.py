#!/usr/bin/env python3
"""Apply packaged-app product branding without normalizing hud_gen.py line endings."""

from __future__ import annotations

import argparse
from pathlib import Path

REPLACEMENTS = (
    (b'BZ Holographic Suite - Gen 2', b'Battlezone Holo Text Generator'),
    (b'BZ HOLOGRAPHIC SUITE', b'BATTLEZONE HOLO TEXT'),
    (b'GEN 2', b'GENERATOR'),
)


def apply_branding(path: Path) -> None:
    data = path.read_bytes()

    for old, new in REPLACEMENTS:
        old_count = data.count(old)
        new_count = data.count(new)
        if old_count == 1:
            data = data.replace(old, new, 1)
        elif old_count == 0 and new_count >= 1:
            continue
        else:
            raise RuntimeError(
                f"Expected exactly one legacy or branded occurrence in {path}: "
                f"{old!r}={old_count}, {new!r}={new_count}"
            )

    path.write_bytes(data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="hud_gen.py", type=Path)
    args = parser.parse_args()
    apply_branding(args.path)


if __name__ == "__main__":
    main()
