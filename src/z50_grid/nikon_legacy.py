"""Decode and validate a legacy-scheme Nikon firmware update package."""

from __future__ import annotations

import binascii
import dataclasses
import hashlib
import json
import re
import struct
from pathlib import Path

HEADER_SIZE = 0x20
SPACE_LABEL_SIZE = 0x20
TABLE_OFFSET = 0x20
DIRECTORY_HEADER = 0x10
DIRECTORY_ENTRY = 0x20
TRAILER_SIZE = 16

class FormatError(ValueError):
    """The firmware package is not valid or not the expected artifact."""


@dataclasses.dataclass(frozen=True)
class Module:
    name: str
    offset: int
    length: int
    data: bytes

    @property
    def payload(self) -> bytes:
        """Module bytes without the trailing big-endian CRC16."""
        return self.data[:-2]

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.data).hexdigest()


@dataclasses.dataclass(frozen=True)
class Package:
    raw: bytes
    body: bytes
    modules: tuple[Module, ...]


def load_legacy_mask(path: Path) -> bytes:
    """Load the three 256-byte legacy XOR tables supplied by the user."""
    raw = path.read_bytes()
    if len(raw) == 768:
        return raw
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        text = raw.decode("ascii", errors="strict")
        tables = []
        for name in ("T1", "T2", "T3"):
            match = re.search(
                rf"(?ims)^\s*{name}:\s*(.*?)(?=^\s*T[123]:|\Z)",
                text,
            )
            if not match:
                raise FormatError(f"{path} does not define legacy mask table {name}")
            table = bytes.fromhex(re.sub(r"[^0-9A-Fa-f]", "", match.group(1)))
            if len(table) != 256:
                raise FormatError(
                    f"{path} {name} table is {len(table)} bytes, expected 256"
                )
            tables.append(table)
        return b"".join(tables)

    tables = []
    for name in ("T1", "T2", "T3"):
        try:
            table = bytes.fromhex(data[name])
        except (KeyError, TypeError, ValueError) as exc:
            raise FormatError(f"{path} has an invalid {name} table") from exc
        if len(table) != 256:
            raise FormatError(
                f"{path} {name} table is {len(table)} bytes, expected 256"
            )
        tables.append(table)
    return b"".join(tables)


def _keystream(length: int, mask: bytes) -> bytes:
    if len(mask) != 768:
        raise AssertionError("legacy Nikon XOR mask must contain three 256-byte tables")
    t1, t2, t3 = mask[:256], mask[256:512], mask[512:]
    plane = b"".join(bytes(t1[x] ^ t2[y] for x in range(256)) for y in range(256))
    plane_int = int.from_bytes(plane, "little")
    blocks = []
    for block in range((length + 0xFFFF) >> 16):
        fill = int.from_bytes(bytes([t3[block & 0xFF]]) * len(plane), "little")
        blocks.append((plane_int ^ fill).to_bytes(len(plane), "little"))
    return b"".join(blocks)[:length]


def decode_body(encoded_body: bytes, mask: bytes) -> bytes:
    """Decode a legacy package body while retaining its plaintext space label."""
    if len(encoded_body) < HEADER_SIZE + SPACE_LABEL_SIZE + TRAILER_SIZE:
        raise FormatError("firmware body is truncated")
    if encoded_body[:SPACE_LABEL_SIZE] != b" " * SPACE_LABEL_SIZE:
        raise FormatError("legacy plaintext space label is missing")
    stream = _keystream(len(encoded_body), mask)
    start = SPACE_LABEL_SIZE
    plain_tail = (
        int.from_bytes(encoded_body[start:], "little")
        ^ int.from_bytes(stream[start:], "little")
    )
    return (
        encoded_body[:start]
        + plain_tail.to_bytes(len(encoded_body) - start, "little")
    )


def parse_modules(body: bytes) -> tuple[Module, ...]:
    if len(body) < TABLE_OFFSET + DIRECTORY_HEADER + 1 + TRAILER_SIZE:
        raise FormatError("decoded body is truncated")
    count, directories = struct.unpack_from(">II", body, TABLE_OFFSET)
    if not 0 < count <= 64:
        raise FormatError(f"invalid module count {count}")
    if directories != 48 + DIRECTORY_ENTRY * count:
        raise FormatError(
            f"directory size {directories} does not match module count {count}"
        )
    if body[TABLE_OFFSET + 8:TABLE_OFFSET + 16] != bytes(8):
        raise FormatError("module-directory reserved bytes are nonzero")

    modules: list[Module] = []
    expected = directories
    payload_end = len(body) - TRAILER_SIZE
    for index in range(count):
        base = TABLE_OFFSET + DIRECTORY_HEADER + index * DIRECTORY_ENTRY
        raw_name = body[base:base + 16].rstrip(b"\0")
        try:
            name = raw_name.decode("ascii")
        except UnicodeDecodeError as exc:
            raise FormatError(f"module {index + 1} has a non-ASCII name") from exc
        start, length = struct.unpack_from(">II", body, base + 16)
        if body[base + 24:base + 32] != bytes(8):
            raise FormatError(f"module {name!r} reserved bytes are nonzero")
        if start != expected:
            raise FormatError(
                f"module {name!r} starts at {start:#x}, expected {expected:#x}"
            )
        if length < 2 or start + length > payload_end:
            raise FormatError(f"module {name!r} has an invalid extent")
        data = body[start:start + length]
        stored = struct.unpack_from(">H", data, length - 2)[0]
        actual = binascii.crc_hqx(data[:-2], 0)
        if actual != stored:
            raise FormatError(
                f"module {name!r} CRC mismatch: stored {stored:#06x}, "
                f"computed {actual:#06x}"
            )
        modules.append(Module(name, start, length, data))
        expected += length

    if expected != payload_end:
        raise FormatError(
            f"last module ends at {expected:#x}, expected {payload_end:#x}"
        )
    if body[-TRAILER_SIZE + 2:] != bytes(TRAILER_SIZE - 2):
        raise FormatError("checksum trailer padding is nonzero")
    stored = struct.unpack_from(">H", body, len(body) - TRAILER_SIZE)[0]
    actual = binascii.crc_hqx(body[:-TRAILER_SIZE], 0)
    if actual != stored:
        raise FormatError(
            f"package CRC mismatch: stored {stored:#06x}, computed {actual:#06x}"
        )
    return tuple(modules)


def load(
    path: Path,
    *,
    mask_path: Path,
    expected_size: int,
    expected_sha256: str,
) -> Package:
    raw = path.read_bytes()
    if len(raw) != expected_size:
        raise FormatError(
            f"{path.name} is {len(raw)} bytes, expected {expected_size}"
        )
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256.lower():
        raise FormatError(
            f"{path.name} SHA-256 is {digest}, expected {expected_sha256.lower()}"
        )
    body = decode_body(raw[HEADER_SIZE:], load_legacy_mask(mask_path))
    return Package(raw, body, parse_modules(body))


def main_module(package: Package) -> Module:
    candidates = [module for module in package.modules if module.name.startswith("eg")]
    if len(candidates) != 1:
        names = ", ".join(module.name for module in package.modules)
        raise FormatError(f"expected one eg module, found {len(candidates)} ({names})")
    return candidates[0]

