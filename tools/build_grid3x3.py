#!/usr/bin/env python3
"""Decode Z50 C 2.60 and build a data-only 3x3 framing-grid module."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from z50_grid.grid3x3 import (
    OUTPUT_NAME,
    PACKAGE_SHA256,
    PACKAGE_SIZE,
    apply_patch,
    report,
)
from z50_grid.nikon_legacy import FormatError, load, main_module

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument(
        "--mask",
        type=Path,
        help="legacy Nikon 768-byte XOR mask (default: next to --source)",
    )
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    mask_path = args.mask or args.source.with_name("legacy_nikon_mask.hex")
    output_path = args.output_dir / OUTPUT_NAME
    report_path = args.output_dir / "grid3x3-report.json"
    for path in (output_path, report_path):
        if path.exists():
            print(f"error: {path} exists; refusing to overwrite", file=sys.stderr)
            return 2

    try:
        package = load(
            args.source,
            mask_path=mask_path,
            expected_size=PACKAGE_SIZE,
            expected_sha256=PACKAGE_SHA256,
        )
        module = main_module(package)
        output, patches = apply_patch(module)
    except (OSError, ValueError, FormatError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(output)
    manifest = report(module, output, patches)
    report_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

