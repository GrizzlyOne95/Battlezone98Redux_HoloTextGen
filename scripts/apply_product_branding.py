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
        count = data.count(old)
        if count != 1:
            raise RuntimeError(
                f"Expected exactly one occurrence of {old!r} in {path}, found {count}"
            )
        data = data.replace(old, new, 1)

    path.write_bytes(data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="hud_gen.py", type=Path)
    args = parser.parse_args()
    apply_branding(args.path)


if __name__ == "__main__":
    main()
