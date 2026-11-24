# Z50 C 2.60 3x3 framing-grid candidate

## Goal

Keep the stock `d8 Framing grid display` switch and draw a 3x3 grid when it is
on. This first candidate changes no user-facing labels and adds no code.

## Stock evidence

The official Z50 manual documents `d8 Framing grid display` as an on/off
setting. The exact Z50 C 2.60 main module is `eg1630_026000.bi`, 31,404,090
bytes, SHA-256
`57e834fac8f921c18c99abe0b1469edbaca71cb1957794bb9f138bd223d30fc1`.

The XOR tables are not stored in this repository. The builder reads a user-
supplied legacy mask next to the package, or an explicitly selected key file.

The module contains a 96-byte grid template at runtime address `0x106627B8`.
Its bytes are identical to the Z5 C 1.50 template that has already been used
for camera-verified 3x3/4x4 grid work:

```text
00000000000000000000030000000000
00000000000000000000030009000100
00000000000000000000030000000000
00000000000000000000030009000400
00000000000000000000030000000000
0000000000000000000003000a000200
```

Each record is 32 bytes. The X and Y line counts are little-endian `uint16`
values at record offsets `+0x0A` and `+0x16`. The Z5 camera-verified module
sets both fields to 2 for its 3x3 mode.

Relevant Z50 code:

| Address | Role |
| --- | --- |
| `0x10355C2C` | literal containing `0x106627B8` |
| `0x103558DA` | `ldr r0, [pc, #0x350]` loading the template |
| `0x103558DC` | `add.w r7, r0, r7, lsl #5` selecting a 32-byte record |
| `0x103558E0` | `ldrh r0, [r7, #0xA]` reading the X line count |
| `0x1035580C` | grid builder function |
| `0x103559D2` | mode-selecting wrapper |

## Candidate change

Change these six payload offsets:

| Runtime address | Stock | Candidate |
| --- | --- | --- |
| `0x106627C2` | X `03 00` | `02 00` |
| `0x106627CE` | Y `03 00` | `02 00` |
| `0x106627E2` | X `03 00` | `02 00` |
| `0x106627EE` | Y `03 00` | `02 00` |
| `0x10662802` | X `03 00` | `02 00` |
| `0x1066280E` | Y `03 00` | `02 00` |

The main-module CRC16 is then recalculated. The output name follows the
existing Nikon standalone-EG convention:

```text
EG163060.BIN
```

The change is twelve bytes in a data template. No jump, hook, appended code or
camera-communication path is involved.

## Verification status

An independent audit can be run with:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
python tools/verify_candidate.py `
  --source firmware/Z_50_0260.bin `
  --mask firmware/legacy_nikon_mask.hex `
  --candidate output/grid3x3-v3/EG163060.BIN
```

It rebuilds the expected module from the official package and refuses any
candidate with an unexpected changed offset, a missing expected change, a size
difference, or a nonzero CRC residual.

The audited v3 artifact reports `PASS`, with only the six X/Y count words and
the two-byte CRC changed. See [safety assessment](SAFETY.md) for residual
risks.

Completed offline:

- official package size and SHA-256;
- legacy XOR decode;
- package CRC and every module CRC;
- extraction of `eg1630_026000.bi`;
- exact stock template match against the Z5 camera-verified reference;
- one template-literal reference and its decode/use site;
- replacement-byte checks;
- rebuilt module CRC;
- Unicorn execution of the X-count load for template modes 0, 1 and 2
  (`3,3,3 -> 2,2,2`);
- Unicorn execution of the Y-count load for the same three modes
  (`3,3,3 -> 2,2,2`);
- a full byte diff showing only the six count words and the two-byte CRC
  changed.

Hardware evidence:

- the project owner reported a successful installation on one Z50 C 2.60;
- the camera remained operational after installation;
- the data-only patch is the only artifact supported by this repository.

Not comprehensively verified:

- other Z50 units and firmware versions;
- LCD and EVF pixel-level geometry in every mode;
- movie, playback and other display-context checks;
- sleep/wake and uncommon display states.

The one-unit installation report does not make modified firmware brick-proof.

## Physical checklist

1. Verify the camera can still open `SETUP MENU -> Firmware version` before
   installing any candidate.
2. Install only the reported artifact with a matching SHA-256.
3. Turn d8 on; confirm two vertical and two horizontal interior lines.
4. Check photo mode on the LCD and EVF.
5. Check the same behavior after sleep/wake, DISP changes and menu return.
6. Turn d8 off; confirm all lines disappear.
7. Keep the stock update package available for recovery.

