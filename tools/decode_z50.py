#!/usr/bin/env python3
"""Decode the exact Nikon Z 50 C 2.60 update package."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from z50_grid.nikon_legacy import FormatError, load, main_module

PACKAGE_SIZE = 31_972_272
PACKAGE_SHA256 = "69745c9e8f3156e936918e62a4a1fad18e7078e9ea3b95d8b8e08144b1542e49"


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
    try:
        package = load(
            args.source,
            mask_path=mask_path,
            expected_size=PACKAGE_SIZE,
            expected_sha256=PACKAGE_SHA256,
        )
        main = main_module(package)
    except (OSError, FormatError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    args.output_dir.mkdir(parents=True, exist_ok=True)
    decoded_path = args.output_dir / "Z_50_0260.dec"
    module_path = args.output_dir / main.name
    report_path = args.output_dir / "manifest.json"
    for path in (decoded_path, module_path, report_path):
        if path.exists():
            print(f"error: {path} exists; refusing to overwrite", file=sys.stderr)
            return 2

    decoded_path.write_bytes(package.body)
    module_path.write_bytes(main.data)
    report = {
        "camera": "Nikon Z 50",
        "firmware": "C 2.60",
        "package": {
            "name": args.source.name,
            "size": len(package.raw),
            "sha256": hashlib.sha256(package.raw).hexdigest(),
        },
        "decoded_body": {
            "name": decoded_path.name,
            "size": len(package.body),
            "sha256": hashlib.sha256(package.body).hexdigest(),
        },
        "modules": [
            {
                "name": module.name,
                "offset": module.offset,
                "length": module.length,
                "payload_length": len(module.payload),
                "sha256": module.sha256,
            }
            for module in package.modules
        ],
        "main_module": {
            "name": main.name,
            "size": main.length,
            "sha256": main.sha256,
        },
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

