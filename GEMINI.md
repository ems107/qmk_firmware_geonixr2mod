# QMK Firmware - Moonlander to Geonix R2 Port

This is a personal fork ([ems107/qmk_firmware_geonixr2mod](https://github.com/ems107/qmk_firmware_geonixr2mod)) originating from [carlosedp/qmk_firmware](https://github.com/carlosedp/qmk_firmware). The primary objective is to port a custom ZSA Moonlander configuration to the Chosfox Geonix R2 keyboard, maintaining full support for its ES32FS026 MCU and wireless features without using VIA/Vial.

## Project Goal
Port a complex configuration from a ZSA Moonlander (~72 keys, split) to a Chosfox Geonix R2 (47 keys, 40% ortho). This requires:
- Intensive use of layers, Tap-Dance, and Mod-Tap to compensate for the reduced key count.
- Integration with the open-source ES32 drivers (reverse-engineered) to maintain 3-mode connectivity (USB/BT/2.4G).

## Relevant Directories
Although this repository is a full QMK fork, work is strictly limited to:
- `keyboards/chosfox/geonixr2`: Main keyboard definition and configuration.
- `keyboards/chosfox/geonixr2/keymaps/zsa-moonlander`: Target directory for the generated Geonix R2 keymap.
- `keyboards/chosfox/geonixr2/porting_zsa-moonlander`: Workspace for the conversion logic.
    - `reference/`: Contains the original Moonlander source code.
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

**Example (Default Keymap):**
```powershell
$env:MSYSTEM="MINGW64"
$env:CHERE_INVOKING="1"
C:\QMK_MSYS\usr\bin\bash.exe -lc "qmk compile -kb chosfox/geonixr2 -km default --clean"
```


## Development Strategy
The porting process is automated via a script to ensure consistency and a clean build environment:
1. **Configure Mapping:** The user defines the key mapping in `keyboards/chosfox/geonixr2/porting_zsa-moonlander/mapping.json`.
2. **Automated Generation:** The script `keyboards/chosfox/geonixr2/porting_zsa-moonlander/convert_moonlander.py` performs the following:
    - Cleans the target directory: `keyboards/chosfox/geonixr2/keymaps/zsa-moonlander/`.
    - Parses the Moonlander reference source for layers, macros, and logic.
    - Generates the new `keymap.c` for Geonix R2.
    - Copies support files (`i18n.h`, `config.h`, `rules.mk`) from reference to target.
3. **Execution:** Run the script using `python keyboards/chosfox/geonixr2/porting_zsa-moonlander/convert_moonlander.py`.
4. **Validation:** Compile the generated keymap using the patterns defined in the Technical Environment section.

## Special MCU Considerations (ES32FS026)
- Uses a custom ChibiOS-Contrib integration for ES32 support.
- Bootloader type is `custom` in `rules.mk`.
- Wireless states are managed by the `rdmctmzt_common` library. Keymaps must respect these states for proper operation.
