from __future__ import annotations

import binascii
import unittest
from pathlib import Path

from z50_grid.grid3x3 import (
    BASE,
    GRID_RECORD_SIZE,
    GRID_TEMPLATE_ADDRESS,
    PACKAGE_SHA256,
    PACKAGE_SIZE,
    apply_patch,
    grid_patches,
)
from z50_grid.nikon_legacy import load, main_module

try:
    from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
    from unicorn.arm_const import (
        UC_ARM_REG_R7,
        UC_ARM_REG_R9,
        UC_CPU_ARM_CORTEX_A15,
    )
except ImportError:
    Uc = None

ROOT = Path(__file__).resolve().parents[1]
FIRMWARE = ROOT / "firmware" / "Z_50_0260.bin"
MASK = ROOT / "firmware" / "legacy_nikon_mask.hex"


@unittest.skipIf(Uc is None, "Unicorn is not installed")
@unittest.skipUnless(
    FIRMWARE.exists() and MASK.exists(),
    "Z_50_0260.bin or legacy_nikon_mask.hex is not present",
)
class GridInstructionExecution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        package = load(
            FIRMWARE,
            mask_path=MASK,
            expected_size=PACKAGE_SIZE,
            expected_sha256=PACKAGE_SHA256,
        )
        cls.stock_module = main_module(package)
        cls.patched_module, _ = apply_patch(cls.stock_module)

    def machine(self, image: bytes):
        upper = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        upper.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_A15)
        size = (len(image) + 0xFFF) & ~0xFFF
        upper.mem_map(BASE, size)
        upper.mem_write(BASE, image)
        return upper

    def x_count(self, image: bytes, mode: int) -> int:
        upper = self.machine(image)
        upper.reg_write(UC_ARM_REG_R7, mode)
        # Stop at the instruction after the stock count is copied into sb/r9.
        upper.emu_start(0x103558DA | 1, 0x103558E4, count=8)
        return upper.reg_read(UC_ARM_REG_R9)

    def y_count(self, image: bytes, mode: int) -> int:
        upper = self.machine(image)
        upper.reg_write(
            UC_ARM_REG_R7,
            GRID_TEMPLATE_ADDRESS + mode * GRID_RECORD_SIZE,
        )
        # Stop before the following helper call.
        upper.emu_start(0x1035594E | 1, 0x10355954, count=4)
        return upper.reg_read(UC_ARM_REG_R9)

    def test_all_template_modes_use_both_candidate_axes(self):
        self.assertEqual(
            [self.x_count(self.stock_module.data, mode) for mode in range(3)],
            [3, 3, 3],
        )
        self.assertEqual(
            [self.y_count(self.stock_module.data, mode) for mode in range(3)],
            [3, 3, 3],
        )
        self.assertEqual(
            [self.x_count(self.patched_module, mode) for mode in range(3)],
            [2, 2, 2],
        )
        self.assertEqual(
            [self.y_count(self.patched_module, mode) for mode in range(3)],
            [2, 2, 2],
        )

    def test_candidate_diff_is_counts_plus_crc_only(self):
        stock = self.stock_module.data
        candidate = self.patched_module
        changed = {
            index
            for index, (before, after) in enumerate(zip(stock, candidate))
            if before != after
        }
        expected = {
            index
            for patch in grid_patches()
            for index, (before, after) in enumerate(
                zip(patch.before, patch.after),
                patch.offset,
            )
            if before != after
        }
        expected.update({len(stock) - 2, len(stock) - 1})
        self.assertEqual(changed, expected)
        self.assertFalse(binascii.crc_hqx(candidate, 0))


if __name__ == "__main__":
    unittest.main()

