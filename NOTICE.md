# Notices and provenance

This is an independent research project. It is not affiliated with,
authorized by, endorsed by, or supported by Nikon Corporation. Nikon and Z 50
are trademarks of their respective owners and are used only to identify the
compatible camera.

The source tree contains no Nikon firmware, extracted firmware asset, or
modified camera update. A prebuilt, modified EG module is distributed
separately as a GitHub Release asset:

- `EG163060.BIN`
- SHA-256:
  `241afae261d39633c7b7061a38719423980feacaf3a428996971b75fbf0ab2a1`

That binary is derived from Nikon firmware and is not relicensed under this
project's MIT License. Users remain responsible for Nikon's terms and for
deciding whether to download or install it.

The legacy Nikon XOR tables are shared across several EXPEED 6 / legacy-format
models. The table is derived material rather than original project code. It is
not included or relicensed here; users must supply it locally. The parser and
firmware-relative patch logic are original work for this project.

The Z5 C 1.50 cross-check uses publicly documented grid fields and behavior
from the WonderLantern organization and its contributors:

- [WonderLantern/wonder-lantern-z5](https://github.com/WonderLantern/wonder-lantern-z5)

- `GRID_COUNT_X = 0x0A`
- `GRID_COUNT_Y = 0x16`
- the camera-verified 3x3 mode sets both fields to 2
- the camera-verified feature documentation describes 3x3/4x4 and 2x2 modes

The project also acknowledges the publicly available research in:

- [WonderLantern/wonder-lantern-z30](https://github.com/WonderLantern/wonder-lantern-z30),
  used as a reference for standalone EG-module construction, module CRCs,
  patch-target validation and hardware-risk documentation;
- [WonderLantern/nikon-fw-key-tool](https://github.com/WonderLantern/nikon-fw-key-tool),
  whose GPL-3.0 project documents recovery of Nikon legacy firmware XOR tables.
  This repository does not copy or redistribute that project's source, binary
  or recovered key tables; it only accepts a user-provided compatible JSON key.

See [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md) for the Chinese attribution and
license boundaries. Upstream projects are not the publishers of this project
and provide no warranty for it.

The Z50 addresses, template match, patch offsets and module identities were
recovered independently from the user-supplied Z50 C 2.60 package.

Unicorn is used only as an optional test dependency. Capstone and Keystone are
not required by the data-only builder.

