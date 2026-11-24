# Notices and provenance

This is an independent research project. It is not affiliated with,
authorized by, endorsed by, or supported by Nikon Corporation. Nikon and Z 50
are trademarks of their respective owners and are used only to identify the
compatible camera.

No Nikon firmware, extracted firmware asset, or modified camera update is
included in this repository.

The legacy Nikon XOR tables are shared across several EXPEED 6 / legacy-format
models. The table is derived material rather than original project code. It is
not included or relicensed here; users must supply it locally. The parser and
firmware-relative patch logic are original work for this project.

The Z5 C 1.50 cross-check uses the publicly documented grid fields and behavior
from WonderLantern's `wonder-lantern-z5` project:

- `GRID_COUNT_X = 0x0A`
- `GRID_COUNT_Y = 0x16`
- the camera-verified 3x3 mode sets both fields to 2
- the camera-verified feature documentation describes 3x3/4x4 and 2x2 modes

The Z50 addresses, template match, patch offsets and module identities were
recovered independently from the user-supplied Z50 C 2.60 package.

Unicorn is used only as an optional test dependency. Capstone and Keystone are
not required by the data-only builder.

