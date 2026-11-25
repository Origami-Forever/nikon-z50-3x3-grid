# Nikon Z50 3×3 Viewfinder Grid

[简体中文](README.md) | English

> [!CAUTION]
> **Flashing firmware is risky. It may leave the camera unable to power on, unresponsive, reset its settings, or void the warranty.**
> This project is not official Nikon software and cannot guarantee that a modified firmware will never brick the camera. If you are not willing to accept that risk, do not flash.
> An interrupted update, the wrong model, or the wrong firmware version can all cause unrecoverable failure.

There are two ways to use this project: **[Option 1: Direct Download](#option-1-direct-download)** or **[Option 2: Build from Source](#option-2-build-from-source)**. Pick either one.

This is a firmware research tool for the **Nikon Z50** on firmware C 2.60. It applies a data-level patch that changes the stock `d8 viewfinder grid display` grid line count from 4×4 to 3×3, without touching the menus, so the risk is limited.

## Option 1: Direct Download

Download from one of the following releases:

- [GitHub Release](https://github.com/Origami-Forever/nikon-z50-grid/releases/tag/v0.1.0-z50-c260-3x3)
- [Direct download `EG163060.BIN`](https://github.com/Origami-Forever/nikon-z50-grid/releases/download/v0.1.0-z50-c260-3x3/EG163060.BIN)

File details:

- Camera: **Nikon Z50**
- Required firmware: C 2.60
- Size: 31,404,090 bytes
- SHA-256:
  `241afae261d39633c7b7061a38719423980feacaf3a428996971b75fbf0ab2a1`

Installation steps:

1. Confirm `Setup Menu -> Firmware Version` reports **C 2.60**;
2. Verify the size and SHA-256 of the downloaded file;
3. Copy `EG163060.BIN` to the root of a card formatted in the camera;
4. Charge the battery fully, turn the camera off, and insert the card;
5. Turn the camera on and follow the prompt under `Setup Menu -> Firmware Version`;
6. Do not press any button, remove the card, or cut power until the update finishes.

## Features

- Keeps the stock `d8 viewfinder grid display` toggle;
- Shows a 3×3 grid when the grid is enabled;
- Restores the stock "off" behavior when the grid is disabled;
- Changes only 6 grid template counters and the module CRC;
- Does not modify code, jumps, pointers, fonts, menus, or sensor paths.

## Source Code and Firmware Boundary

The source repository does not include:

- Official Nikon firmware;
- Decoded firmware modules;
- The legacy XOR key table.

The verified patched EG module is published separately through GitHub Releases and is not committed as source.

You must obtain the unmodified official firmware package yourself:

| Camera | Firmware | File | Size | SHA-256 |
| --- | --- | --- | --- | --- |
| **Nikon Z50** | C 2.60 | `Z_50_0260.bin` | 31,972,272 | `69745c9e8f3156e936918e62a4a1fad18e7078e9ea3b95d8b8e08144b1542e49` |

Official update packages use Nikon's legacy XOR format. The build tool decodes them locally and checks the module and package CRCs, but it does not download firmware and never connects to or flashes a camera.

The 768-byte legacy XOR table is firmware-derived material and is therefore not provided in this repository. Obtain a legal local copy yourself and place it at:

```text
firmware/legacy_nikon_mask.hex
```

The build tool also accepts JSON key files produced by WonderLantern `nikon-fw-key-tool`.

## Option 2: Build from Source

Requires Python 3.10 or newer. Building the data-only 3×3 variant requires no third-party Python packages at all.

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
python tools/build_grid3x3.py `
  --source firmware/Z_50_0260.bin `
  --output-dir output/grid3x3-v3
```

The builder never overwrites existing files. On success it produces:

```text
EG163060.BIN
grid3x3-report.json
```

The build known to have been installed on real hardware:

- File name: `EG163060.BIN`
- Size: 31,404,090 bytes
- SHA-256:
  `241afae261d39633c7b7061a38719423980feacaf3a428996971b75fbf0ab2a1`

## Independent Verification

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
python tools/verify_candidate.py `
  --source firmware/Z_50_0260.bin `
  --mask firmware/legacy_nikon_mask.hex `
  --candidate output/grid3x3-v3/EG163060.BIN
```

The auditor rebuilds the result independently from the official package and rejects files that:

- do not match the independent rebuild;
- have an unexpected size;
- are missing an expected change;
- contain an unexpected change;
- leave a non-zero residue in the module CRC.

This build changes only the following 6 data fields plus the trailing 2-byte CRC:

| Runtime address | Stock value | 3×3 |
| --- | --- | --- |
| `0x106627C2` | X `03 00` | `02 00` |
| `0x106627CE` | Y `03 00` | `02 00` |
| `0x106627E2` | X `03 00` | `02 00` |
| `0x106627EE` | Y `03 00` | `02 00` |
| `0x10662802` | X `03 00` | `02 00` |
| `0x1066280E` | Y `03 00` | `02 00` |

See [implementation notes](docs/IMPLEMENTATION.md) for the underlying rationale.

## Verification Scope

Phase one is complete:

- [x] Decoded the official Z50 C 2.60 update package;
- [x] Extracted and verified the main `eg` module;
- [x] Located the grid templates used by `d8`;
- [x] Changed only the grid counters from the stock value 3 to 2;
- [x] Rebuilt the module and independently verified the whole file;

Not yet fully verified:

- Pixel-level positioning of the LCD and EVF in every display mode;
- Uncommon paths such as movie recording, playback, and wake from sleep;
- Guaranteed recovery after an interrupted update.


See [verification records](docs/VERIFICATION.md) for the full scope.

## License

This project's own code and documentation are under the MIT License. That license does not apply to Nikon firmware, firmware-derived keys, or other third-party material; see [NOTICE.md](NOTICE.md).

## Credits and Referenced Projects

This project's research references the [WonderLantern organization](https://github.com/WonderLantern) and projects its contributors published publicly:

- [wonder-lantern-z5](https://github.com/WonderLantern/wonder-lantern-z5):
  grid counter fields, 3×3 mode values, and published verification records;
- [wonder-lantern-z30](https://github.com/WonderLantern/wonder-lantern-z30):
  EG module construction, CRC/target checksum, and risk-control methods;
- [nikon-fw-key-tool](https://github.com/WonderLantern/nikon-fw-key-tool):
  legacy firmware XOR key research and JSON key compatibility.

This project does not contain firmware, key tables, or full source code from those projects. See [credits and referenced projects](ACKNOWLEDGEMENTS.md) for detailed attribution and license boundaries.

This project is not affiliated with, authorized by, or endorsed by Nikon Corporation.
