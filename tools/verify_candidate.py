#!/usr/bin/env python3
"""Independently audit the generated Z50 3x3 grid module."""

from __future__ import annotations

import argparse
import binascii
import hashlib
import json
import sys
from pathlib import Path

from z50_grid.grid3x3 import PACKAGE_SHA256, PACKAGE_SIZE, apply_patch, grid_patches
from z50_grid.nikon_legacy import FormatError, load, main_module


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--mask", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failures: list[str] = []
    try:
        package = load(
            args.source,
            mask_path=args.mask,
            expected_size=PACKAGE_SIZE,
            expected_sha256=PACKAGE_SHA256,
        )
        module = main_module(package)
        expected, _ = apply_patch(module)
        candidate = args.candidate.read_bytes()
    except (OSError, ValueError, FormatError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2

    if len(candidate) != len(module.data):
        failures.append(
            f"size differs: candidate {len(candidate)}, stock {len(module.data)}"
        )
    if candidate != expected:
        failures.append("candidate does not match the independently rebuilt module")
    if binascii.crc_hqx(candidate, 0):
        failures.append("candidate CRC residual is nonzero")

    changed = {
        index
        for index, (before, after) in enumerate(zip(module.data, candidate))
        if before != after
    }
    allowed = {
        index
        for patch in grid_patches()
        for index, (before, after) in enumerate(
            zip(patch.before, patch.after),
            patch.offset,
        )
        if before != after
    }
    allowed.update({len(module.data) - 2, len(module.data) - 1})
    unexpected = sorted(changed - allowed)
    missing = sorted(allowed - changed)
    if unexpected:
        failures.append(
            "unexpected changed offsets: "
            + ", ".join(f"{offset:#x}" for offset in unexpected)
        )
    if missing:
        failures.append(
            "missing expected changes: "
            + ", ".join(f"{offset:#x}" for offset in missing)
        )

    result = {
        "status": "PASS" if not failures else "FAIL",
        "camera_verified": False,
        "scope": "Offline byte-level audit; does not prove camera boot or display behavior",
        "source": {
            "name": args.source.name,
            "size": len(package.raw),
            "sha256": hashlib.sha256(package.raw).hexdigest(),
        },
        "stock_module": {
            "name": module.name,
            "size": module.length,
            "sha256": module.sha256,
        },
        "candidate": {
            "name": args.candidate.name,
            "size": len(candidate),
            "sha256": hashlib.sha256(candidate).hexdigest(),
            "crc_residual": f"{binascii.crc_hqx(candidate, 0):04x}",
        },
        "changed_offsets": [f"{offset:#x}" for offset in sorted(changed)],
        "allowed_offsets": [f"{offset:#x}" for offset in sorted(allowed)],
        "failures": failures,
    }
    print(json.dumps(result, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

