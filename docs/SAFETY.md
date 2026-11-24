# Safety assessment

## Bottom line

There is no honest way to guarantee that installing a modified firmware module
will not brick a Z50. The data-only build has a small, auditable change surface
and was reported to install successfully on one Z50 C 2.60 unit.

If this camera is your only camera, or is used for paid or irreplaceable work,
use an HDMI monitor or physical overlay unless you can accept the remaining
risk and have a recovery path.

## Why this candidate has a relatively small change surface

- It is for the exact stock Z50 C 2.60 main module.
- It changes six 16-bit grid parameters and the two-byte module CRC.
- It changes no machine code, jump, pointer, font, menu or sensor path.
- The full artifact matches an independent rebuild byte for byte.
- The CRC residual is zero.
- The X/Y count fields were verified by executing the stock and patched loader
  instructions with Unicorn.
- The two count fields and values match the Z5 camera-verified implementation.

The independent audit result is `PASS`. That proves file consistency. It does
not prove camera boot, update acceptance, display behavior or recovery.

## Residual risks that remain

1. **Wrong camera firmware.** This artifact is only for Z50 C 2.60. Do not use
   it on another Z50 firmware version or another Nikon model.
2. **Limited hardware evidence.** Installation was reported on one Z50 C 2.60.
   Another unit or Nikon firmware release can behave differently.
3. **Display-context differences.** The three template modes are changed
   together. LCD, EVF, movie, playback and uncommon display states have not
   been exhaustively checked.
4. **Update interruption.** Loss of power or removing the card during an
   update can leave the camera unusable regardless of the patch itself.
5. **Recovery is not absolute.** Reinstalling the stock `Z_50_0260.bin` is the
   intended rollback, but it depends on the camera still reaching the
   firmware-update service.

## Selectable menu experiments

Selectable-menu builds are excluded from the public release. The attempted
menu implementation caused an unresponsive camera during hardware testing.
Offline checks are not sufficient evidence for a menu or code-injection build.

Do not install or redistribute the local `grid-menu-*` outputs. They are not
part of the documented or supported artifact in this repository.

## Preflight checklist

Complete every item before considering installation:

- Confirm `SETUP MENU -> Firmware version` shows **C 2.60**.
- Verify the candidate SHA-256 is
  `241afae261d39633c7b7061a38719423980feacaf3a428996971b75fbf0ab2a1`.
  Never install the artifact if its hash differs from this value.
- Re-run `tools/verify_candidate.py` and require `PASS`.
- Keep an unmodified `Z_50_0260.bin`.
- Back up photos and camera settings.
- Use a camera-formatted card and place only the intended update file at its
  root.
- Use a sufficiently charged, healthy battery.
- Do not touch buttons, remove the card, or disconnect power during the update.

## Immediate post-install checks

- The camera boots normally.
- `SETUP MENU -> Firmware version` still opens.
- d8 on gives two vertical and two horizontal interior lines.
- d8 off removes the grid.
- Photo mode works on both LCD and EVF.
- Sleep/wake, DISP changes and menu return preserve normal operation.

If the camera boots but grid behavior is wrong, reinstall stock C 2.60 before
doing further testing. If it does not boot, stop trying repeated updates and
seek service support.

