"""Build the first Z50 C 2.60 3x3 framing-grid candidate."""

from __future__ import annotations

import binascii
import dataclasses
import hashlib
import struct

from .nikon_legacy import Module

STOCK_MODULE_NAME = "eg1630_026000.bi"
STOCK_MODULE_SIZE = 31_404_090
STOCK_MODULE_SHA256 = "57e834fac8f921c18c99abe0b1469edbaca71cb1957794bb9f138bd223d30fc1"
OUTPUT_NAME = "EG163060.BIN"
PACKAGE_SIZE = 31_972_272
PACKAGE_SHA256 = "69745c9e8f3156e936918e62a4a1fad18e7078e9ea3b95d8b8e08144b1542e49"

BASE = 0x10020000
GRID_TEMPLATE_ADDRESS = 0x106627B8
GRID_TEMPLATE_OFFSET = GRID_TEMPLATE_ADDRESS - BASE
GRID_RECORD_SIZE = 32
GRID_LINE_COUNT_X_OFFSET = 0x0A
GRID_LINE_COUNT_Y_OFFSET = 0x16
STOCK_LINE_COUNT = 3
TARGET_LINE_COUNT = 2

# Runtime code evidence for the stock renderer.
GRID_BUILDER_ADDRESS = 0x1035580C
GRID_WRAPPER_ADDRESS = 0x103559D2
GRID_TEMPLATE_LITERAL_ADDRESS = 0x10355C2C


@dataclasses.dataclass(frozen=True)
class Patch:
    name: str
    offset: int
    before: bytes
    after: bytes

    @property
    def address(self) -> int:
        return BASE + self.offset


def grid_patches() -> tuple[Patch, ...]:
    target = struct.pack("<H", TARGET_LINE_COUNT)
    patches = []
    for record in range(3):
        base = GRID_TEMPLATE_OFFSET + record * GRID_RECORD_SIZE
        patches.append(
            Patch(
                name=f"grid_record_{record}_line_count_x",
                offset=base + GRID_LINE_COUNT_X_OFFSET,
                before=struct.pack("<H", STOCK_LINE_COUNT),
                after=target,
            )
        )
        patches.append(
            Patch(
                name=f"grid_record_{record}_line_count_y",
                offset=base + GRID_LINE_COUNT_Y_OFFSET,
                before=struct.pack("<H", STOCK_LINE_COUNT),
                after=target,
            )
        )
    return tuple(patches)


def validate_stock_module(module: Module) -> None:
    if module.name != STOCK_MODULE_NAME:
        raise ValueError(
            f"unexpected main module {module.name!r}, expected {STOCK_MODULE_NAME!r}"
        )
    if module.length != STOCK_MODULE_SIZE:
        raise ValueError(
            f"main module is {module.length} bytes, expected {STOCK_MODULE_SIZE}"
        )
    if module.sha256 != STOCK_MODULE_SHA256:
        raise ValueError(
            f"main module SHA-256 is {module.sha256}, expected {STOCK_MODULE_SHA256}"
        )
    if binascii.crc_hqx(module.data, 0):
        raise ValueError("stock main module CRC does not validate")


def apply_patch(module: Module) -> tuple[bytes, tuple[Patch, ...]]:
    """Return a patched module, including a freshly calculated CRC16."""
    validate_stock_module(module)
    payload = bytearray(module.payload)
    patches = grid_patches()
    for patch in patches:
        actual = bytes(payload[patch.offset:patch.offset + len(patch.before)])
        if actual != patch.before:
            raise ValueError(
                f"{patch.name}: expected {patch.before.hex()} at "
                f"{patch.address:#010x}, found {actual.hex()}"
            )
        payload[patch.offset:patch.offset + len(patch.after)] = patch.after
    crc = binascii.crc_hqx(payload, 0)
    output = bytes(payload) + struct.pack(">H", crc)
    if binascii.crc_hqx(output, 0):
        raise AssertionError("rebuilt module CRC does not validate")
    if len(output) != STOCK_MODULE_SIZE:
        raise AssertionError("rebuilt module changed length")
    return output, patches


def report(module: Module, output: bytes, patches: tuple[Patch, ...]) -> dict:
    return {
        "status": "camera_install_reported_on_one_z50_c260",
        "camera": "Nikon Z 50",
        "firmware": "C 2.60",
        "change": "d8 Framing grid display becomes a 3x3 grid",
        "stock_module": {
            "name": module.name,
            "size": module.length,
            "sha256": module.sha256,
        },
        "output": {
            "name": OUTPUT_NAME,
            "size": len(output),
            "sha256": hashlib.sha256(output).hexdigest(),
            "crc16": f"{struct.unpack_from('>H', output, len(output) - 2)[0]:04x}",
        },
        "evidence": {
            "grid_template": f"{GRID_TEMPLATE_ADDRESS:#x}",
            "builder_function": f"{GRID_BUILDER_ADDRESS:#x}",
            "builder_wrapper": f"{GRID_WRAPPER_ADDRESS:#x}",
            "template_literal_load_site": "0x103558da",
            "template_literal": f"{GRID_TEMPLATE_LITERAL_ADDRESS:#x}",
            "record_size": GRID_RECORD_SIZE,
            "line_count_x_offset": GRID_LINE_COUNT_X_OFFSET,
            "line_count_y_offset": GRID_LINE_COUNT_Y_OFFSET,
            "stock_x_line_count": STOCK_LINE_COUNT,
            "target_x_line_count": TARGET_LINE_COUNT,
            "target_y_line_count": TARGET_LINE_COUNT,
            "scope": "Data-only change to both axis counts in the stock grid template",
        },
        "patches": [
            {
                "name": patch.name,
                "module_offset": f"{patch.offset:#x}",
                "runtime_address": f"{patch.address:#x}",
                "before": patch.before.hex(),
                "after": patch.after.hex(),
            }
            for patch in patches
        ],
        "limitations": [
            "Hardware evidence is limited to one Z50 C 2.60 unit.",
            "LCD and EVF geometry have not been measured across firmware and display modes.",
            "Movie mode, playback and other grid-related paths are not separately verified.",
            "Keep the stock Z_50_0260.bin for recovery.",
        ],
    }

