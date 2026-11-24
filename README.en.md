# Nikon Z50 3x3 Framing Grid

English | [简体中文](README.md)

> [!CAUTION]
> **Firmware modification can leave the camera unable to boot, unresponsive,
> without saved settings, or outside warranty coverage.** This is not Nikon
> software, and no modified-firmware update can be guaranteed brick-proof.
> Hardware evidence is currently limited to one Z50 C 2.60 unit. Do not flash
> without a fully charged battery, the official rollback package, and a clear
> understanding of the risk. An interrupted update, wrong model, or wrong
> firmware version may cause an unrecoverable failure.

Source-relative firmware tooling for the Nikon Z 50, with a data-only 3x3
grid patch that has been installed on one Z50 C 2.60 camera.

The first target is a single user-visible change:

- keep the stock `d8 Framing grid display` switch;
- when it is on, draw a 3x3 grid instead of the stock fixed grid;
- leave all other factory behavior untouched.

This repository intentionally does not include Nikon firmware, a modified
camera update, a decoded module, or the legacy XOR mask. Supply your own
unmodified official update package:

| Camera | Firmware | File | Size | SHA-256 |
| --- | --- | --- | --- | --- |
| Nikon Z 50 | C 2.60 | `Z_50_0260.bin` | 31,972,272 | `69745c9e8f3156e936918e62a4a1fad18e7078e9ea3b95d8b8e08144b1542e49` |

The update package is encrypted with Nikon's legacy XOR scheme. This project
uses the public, camera-independent legacy tables to decode it locally and
checks both module and package CRCs before accepting the result.

The 768-byte legacy XOR mask is **not included in this repository** because it
is derived material and its upstream distribution grants no license over the
table itself. Keep your own local copy at
`firmware/legacy_nikon_mask.hex`; that directory is ignored by Git. The format
also accepts a JSON key from WonderLantern's `nikon-fw-key-tool` through the
`--mask` option.

## Build the first candidate

Run:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
python tools/build_grid3x3.py `
  --source firmware/Z_50_0260.bin `
  --output-dir output/grid3x3-v3
```

The two output files must not already exist. The builder writes:

```text
EG163060.BIN
grid3x3-report.json
```

Audit the exact artifact independently with:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
python tools/verify_candidate.py `
  --source firmware/Z_50_0260.bin `
  --mask firmware/legacy_nikon_mask.hex `
  --candidate output/grid3x3-v3/EG163060.BIN
```

The candidate sets both axis line counts in the stock grid-template records
to 2 and recalculates the main-module CRC. See
[implementation evidence](docs/IMPLEMENTATION.md).

## Scope

Only the data-only 3x3 patch is part of this release. Selectable-menu
experiments are not distributed or built by the public entry points. A menu
prototype caused an unresponsive state during hardware testing and is not
considered safe.

## Status

This is a narrow firmware research project, not a general-purpose Nikon
firmware modification kit.

The first milestone is complete:

- [x] Decode the exact stock C 2.60 package.
- [x] Extract and fingerprint the main `eg` module.
- [x] Locate the stock grid template used by d8.
- [x] Change only the grid line count from the stock fixed style to 3x3.
- [x] Rebuild and verify the modified main module.
- [x] Complete emulator checks and report initial physical-camera installation.

The repository remains source-only. Build outputs are ignored locally and are
not published as release binaries.

The artifact with SHA-256
`241afae261d39633c7b7061a38719423980feacaf3a428996971b75fbf0ab2a1`
was installed on one Z50 running C 2.60 and the owner reported that basic
operation remained normal. That is not proof that every mode, display path or
camera unit is safe. See [verified scope](docs/VERIFICATION.md).

Do not install any intermediate or unreported build on a camera.

## Safety

Firmware modification can damage the camera or make it unusable. Keep an
unmodified copy of the official update package and confirm that the camera can
still reach `SETUP MENU -> Firmware version`. The build tools never connect to
or flash a camera. A modified update can be rejected or fail despite passing
offline checks.

Read the full [safety assessment](docs/SAFETY.md). This project cannot promise
that flashing is brick-proof.

## References and acknowledgements

This research project acknowledges
[WonderLantern](https://github.com/WonderLantern) and its contributors:

- [wonder-lantern-z5](https://github.com/WonderLantern/wonder-lantern-z5):
  grid-count fields, the 3x3 value, and public verification records;
- [wonder-lantern-z30](https://github.com/WonderLantern/wonder-lantern-z30):
  EG-module build, CRC/target validation, and risk-control practices;
- [nikon-fw-key-tool](https://github.com/WonderLantern/nikon-fw-key-tool):
  legacy XOR-table research and JSON key interoperability.

This repository does not include those projects' firmware, recovered key
tables, or complete source code. See
[references and acknowledgements](ACKNOWLEDGEMENTS.md) for attribution and
license boundaries.

Nikon is not affiliated with or endorsing this project.

