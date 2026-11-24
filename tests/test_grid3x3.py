from __future__ import annotations

import binascii
import hashlib
import struct
import unittest
from pathlib import Path

from z50_grid.grid3x3 import (
    PACKAGE_SIZE,
    PACKAGE_SHA256,
    apply_patch,
    grid_patches,
)
from z50_grid.nikon_legacy import load, main_module

ROOT = Path(__file__).resolve().parents[1]
FIRMWARE = ROOT / "firmware" / "Z_50_0260.bin"
MASK = ROOT / "firmware" / "legacy_nikon_mask.hex"


class GridPatchDefinition(unittest.TestCase):
    def test_three_records_change_only_count_words(self):
        patches = grid_patches()
        self.assertEqual(len(patches), 6)
        self.assertEqual({p.after for p in patches}, {b"\x02\x00"})
        self.assertEqual(
            [p.offset for p in patches],
            [0x6427C2, 0x6427CE, 0x6427E2, 0x6427EE, 0x642802, 0x64280E],
        )


@unittest.skipUnless(
    FIRMWARE.exists() and MASK.exists(),
    "Z_50_0260.bin or legacy_nikon_mask.hex is not present",
)
class GridBuild(unittest.TestCase):
    def test_exact_stock_package_builds_valid_module(self):
        package = load(
            FIRMWARE,
            mask_path=MASK,
            expected_size=PACKAGE_SIZE,
            expected_sha256=PACKAGE_SHA256,
        )
        module = main_module(package)
        output, patches = apply_patch(module)
        self.assertEqual(len(output), len(module.data))
        self.assertFalse(binascii.crc_hqx(output, 0))
        self.assertEqual(
            struct.unpack_from(">H", output, len(output) - 2)[0],
            binascii.crc_hqx(output[:-2], 0),
        )
        self.assertNotEqual(hashlib.sha256(output).digest(), hashlib.sha256(module.data).digest())
        self.assertEqual(len(patches), 6)


if __name__ == "__main__":
    unittest.main()

