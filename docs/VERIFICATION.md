# Verified scope

## Artifact

The documented data-only build has:

| Property | Value |
| --- | --- |
| Camera family | Nikon Z 50 |
| Required firmware | C 2.60 |
| Output filename | `EG163060.BIN` |
| Output size | 31,404,090 bytes |
| Output SHA-256 | `241afae261d39633c7b7061a38719423980feacaf3a428996971b75fbf0ab2a1` |
| Stock package SHA-256 | `69745c9e8f3156e936918e62a4a1fad18e7078e9ea3b95d8b8e08144b1542e49` |

The build changes six 16-bit grid-template count fields from `3` to `2` and
recalculates the module CRC. An independent rebuild reports a zero CRC
residual and byte differences only at those six fields and the two CRC bytes.

## Hardware evidence

The project owner reported that this artifact installed successfully on one
Z50 running C 2.60 and that the camera remained operational afterward.

This report does not establish:

- behavior on another Z50 unit or another firmware version;
- pixel-level geometry on LCD and EVF in every display mode;
- movie, playback, sleep/wake or uncommon display paths;
- that a failed or interrupted update can always be recovered.

Treat the artifact as camera-tested, not universally certified.

## Distribution policy

Nikon firmware, decoded modules and the legacy XOR mask are not distributed as
source-tree files. The verified modified EG module is distributed separately
as the `EG163060.BIN` GitHub Release asset. Users may download that file,
verify its SHA-256, and retain the stock official updater for recovery.

The release asset is firmware-derived and is not covered by the project's MIT
License. Users remain responsible for checking compatibility and Nikon's terms
before downloading or installing it.
