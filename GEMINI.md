# QMK Firmware - Moonlander to Geonix R2 Port

This is a personal fork ([ems107/qmk_firmware_geonixr2mod](https://github.com/ems107/qmk_firmware_geonixr2mod)) originating from [carlosedp/qmk_firmware](https://github.com/carlosedp/qmk_firmware). The primary objective is to port a custom ZSA Moonlander configuration to the Chosfox Geonix R2 keyboard, maintaining full support for its ES32FS026 MCU and wireless features without using VIA/Vial.

## Project Goal
Port a complex configuration from a ZSA Moonlander (~72 keys, split) to a Chosfox Geonix R2 (47 keys, 40% ortho). This requires:
- Intensive use of layers, Tap-Dance, and Mod-Tap to compensate for the reduced key count.
- Integration with the open-source ES32 drivers (reverse-engineered) to maintain 3-mode connectivity (USB/BT/2.4G).

## Relevant Directories
Although this repository is a full QMK fork, work is strictly limited to:
- `keyboards/chosfox/geonixr2`: Main keyboard definition and configuration.
- `keyboards/chosfox/geonixr2/keymaps/zsa-moonlander`: Target directory for the generated Geonix R2 keymap. **Do not edit manually — regenerated on every script run.**
- `keyboards/chosfox/geonixr2/porting_zsa-moonlander`: Conversion workspace. See `README.md` inside for full documentation.
    - `reference/`: Contains the original Moonlander source code (read-only input).
    - `convert_moonlander.py`: Main conversion script.
    - `mapping.json`: Position mapping and manual overrides configuration.
- `lib/rdmctmzt_common`: Shared library for wireless connectivity and LED logic (ES32 specific). **Note:** Avoid modifying this unless necessary for wireless behavior.

## Technical Environment (Windows)
The project requires **QMK MSYS** and must be compiled using the following PowerShell command to ensure correct environment variables and path handling.

### AI Safety & Boundaries
**CRITICAL:** The AI must NEVER attempt to flash the firmware to the keyboard. Flashing is a manual operation that must be performed strictly by the user. The AI's scope ends at successful compilation and verification of the binary.

### Compilation Command
```powershell
$env:MSYSTEM="MINGW64"
$env:CHERE_INVOKING="1"
C:\QMK_MSYS\usr\bin\bash.exe -lc "qmk compile -kb chosfox/geonixr2 -km <keymap_name> --clean"
```

**Example (zsa-moonlander keymap):**
```powershell
$env:MSYSTEM="MINGW64"
$env:CHERE_INVOKING="1"
C:\QMK_MSYS\usr\bin\bash.exe -lc "qmk compile -kb chosfox/geonixr2 -km zsa-moonlander --clean"
```

## Development Workflow

The porting process is automated. **Never edit `keymaps/zsa-moonlander/` directly** — it is fully regenerated on every script run.

1. **Configure mapping:** Edit `keyboards/chosfox/geonixr2/porting_zsa-moonlander/mapping.json`.
   - `geonix_layout`: maps Geonix physical positions to Moonlander key IDs.
   - `overrides`: manually patch specific keycodes on specific layers without touching generated files.
   - See `porting_zsa-moonlander/README.md` for full reference.

2. **Generate keymap:**
   ```powershell
   python keyboards/chosfox/geonixr2/porting_zsa-moonlander/convert_moonlander.py
   ```
   The script cleans and fully regenerates `keymaps/zsa-moonlander/`.

3. **Compile and validate:**
   ```powershell
   $env:MSYSTEM="MINGW64"; $env:CHERE_INVOKING="1"
   C:\QMK_MSYS\usr\bin\bash.exe -lc "qmk compile -kb chosfox/geonixr2 -km zsa-moonlander --clean"
   ```

4. **Flash:** manual operation by the user only.

## What the Script Generates

| File | Description |
|---|---|
| `keymap.c` | All layers, Tap Dance, macros, process_record_user, RGB logic |
| `config.h` | Timing/behavior defines ported from Moonlander config (ZSA-exclusives stripped) |
| `rules.mk` | Feature flags: TAP_DANCE, MOUSEKEY, EXTRAKEY, DYNAMIC_KEYMAP, SPACE_CADET=no |
| `version.h` | Build identifier string |
| `i18n.h` | Copied verbatim from reference (ES layout keycodes) |

## Special MCU Considerations (ES32FS026)
- Uses a custom ChibiOS-Contrib integration for ES32 support.
- Bootloader type is `custom` in `rules.mk`.
- Wireless states are managed by the `rdmctmzt_common` library. Keymaps must respect these states for proper operation.
- `DYNAMIC_KEYMAP_ENABLE = yes` is mandatory in the keymap's `rules.mk` because the keyboard-level build includes `quantum/dynamic_keymap.c` unconditionally.
