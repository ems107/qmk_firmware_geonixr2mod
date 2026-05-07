#!/usr/bin/env python3
"""
convert_moonlander.py
Porta el keymap ZSA Moonlander al Chosfox Geonix R2.

Estado actual: Fase 2 — todas las capas, keycodes extendidos.
"""

import re
import os
import json
import shutil

# ==============================================================================
# RUTAS
# ==============================================================================
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
PATH_SOURCE  = os.path.join(BASE_DIR, "reference/zsa_moonlander_test-layout_source/keymap.c")
PATH_REF_DIR = os.path.join(BASE_DIR, "reference/zsa_moonlander_test-layout_source")
PATH_MAPPING = os.path.join(BASE_DIR, "mapping.json")
PATH_TARGET  = os.path.join(BASE_DIR, "../keymaps/zsa-moonlander")

# ==============================================================================
# ORDEN DE TECLAS EN EL LAYOUT MOONLANDER
# Cada ID identifica una posición física: L=izquierda, R=derecha, fila+columna.
# ==============================================================================
MOON_ORDER = [
    "L00","L01","L02","L03","L04","L05","L06", "R00","R01","R02","R03","R04","R05","R06",
    "L10","L11","L12","L13","L14","L15","L16", "R10","R11","R12","R13","R14","R15","R16",
    "L20","L21","L22","L23","L24","L25","L26", "R20","R21","R22","R23","R24","R25","R26",
    "L30","L31","L32","L33","L34","L35",        "R30","R31","R32","R33","R34","R35",
    "L40","L41","L42","L43","L44","L45",        "R40","R41","R42","R43","R44","R45",
    "L50","L51","L52",                          "R50","R51","R52",
]

# ==============================================================================
# FASE 1: FILTRO DE KEYCODES BÁSICOS
# Solo se permiten keycodes de la forma KC_XXX sin argumentos.
# Todo lo demás se sustituye por KC_TRNS y se emite un warning.
# ==============================================================================
def is_basic_keycode(keycode: str) -> bool:
    """Devuelve True si el keycode es un KC_* simple sin paréntesis."""
    return bool(re.match(r'^KC_[A-Z0-9_]+$', keycode))


# ==============================================================================
# PARSEO DEL KEYMAP MOONLANDER
# ==============================================================================
def parse_moonlander_layers(content: str) -> dict:
    """
    Parsea todas las capas del keymap.c Moonlander.
    Devuelve: {num_capa: {moon_id: keycode_string}}
    """
    layers = {}
    for match in re.finditer(r'\[(\d+)\]\s*=\s*LAYOUT_moonlander\(', content):
        layer_num = int(match.group(1))
        start = match.end()
        depth = 1
        end = start
        for i in range(start, len(content)):
            if content[i] == '(':
                depth += 1
            elif content[i] == ')':
                depth -= 1
                if depth == 0:
                    end = i
                    break

        # Tokenizar respetando paréntesis anidados
        keys = []
        depth = 0
        current = ""
        for char in content[start:end]:
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            if char == ',' and depth == 0:
                token = re.sub(r'//.*', '', current).strip()
                if token:
                    keys.append(token)
                current = ""
            else:
                current += char
        token = re.sub(r'//.*', '', current).strip()
        if token:
            keys.append(token)

        layer_data = {}
        for idx, key in enumerate(keys):
            if idx < len(MOON_ORDER):
                layer_data[MOON_ORDER[idx]] = key
        layers[layer_num] = layer_data

    return layers


# ==============================================================================
# FASE 2: RESOLVER DE KEYCODES EXTENDIDOS
# Enfoque blocklist: todo pasa salvo patrones ZSA-exclusivos o de fases futuras.
# Keycodes no soportados -> KC_TRNS + warning en consola.
# ==============================================================================
_BLOCKED_PHASE2 = [
    # Fase 3: Tap Dance y macros de string
    re.compile(r'^TD\('),
    re.compile(r'^ST_MACRO_\d+$'),
    re.compile(r'^DUAL_FUNC_\d+$'),
    # Fase 5: RGB ZSA-exclusivo
    re.compile(r'^RGB_SLD$'),
    re.compile(r'^HSV_\d+_\d+_\d+$'),
    re.compile(r'^TOGGLE_LAYER_COLOR$'),
    # Audio (no disponible en este firmware)
    re.compile(r'^AU_TOGG$'),
    re.compile(r'^MU_TOGG$'),
    re.compile(r'^MU_NEXT$'),
]

# Tabla de traduccion de keycodes renombrados en versiones modernas de QMK.
_KEYCODE_TRANSLATIONS = {
    # Mouse cursor (KC_MS_* -> MS_*)
    "KC_MS_UP":    "MS_UP",
    "KC_MS_DOWN":  "MS_DOWN",
    "KC_MS_LEFT":  "MS_LEFT",
    "KC_MS_RIGHT": "MS_RGHT",    # Ojo: RGHT, no RIGHT
    # Mouse buttons (KC_MS_BTN* -> MS_BTN*)
    "KC_MS_BTN1": "MS_BTN1",
    "KC_MS_BTN2": "MS_BTN2",
    "KC_MS_BTN3": "MS_BTN3",
    "KC_MS_BTN4": "MS_BTN4",
    "KC_MS_BTN5": "MS_BTN5",
    # Mouse wheel (KC_MS_WH_* -> MS_WHL*)
    "KC_MS_WH_UP":    "MS_WHLU",
    "KC_MS_WH_DOWN":  "MS_WHLD",
    "KC_MS_WH_LEFT":  "MS_WHLL",
    "KC_MS_WH_RIGHT": "MS_WHLR",
    # Mouse acceleration (KC_MS_ACCEL* -> MS_ACL*)
    "KC_MS_ACCEL0": "MS_ACL0",
    "KC_MS_ACCEL1": "MS_ACL1",
    "KC_MS_ACCEL2": "MS_ACL2",
    # RGB matrix (RGB_* -> RM_*)
    "RGB_TOG":          "RM_TOGG",
    "RGB_MODE_FORWARD": "RM_NEXT",
    "RGB_MODE_REVERSE": "RM_PREV",
    "RGB_HUI": "RM_HUEU",
    "RGB_HUD": "RM_HUED",
    "RGB_SAI": "RM_SATU",
    "RGB_SAD": "RM_SATD",
    "RGB_VAI": "RM_VALU",
    "RGB_VAD": "RM_VALD",
    "RGB_SPI": "RM_SPDU",
    "RGB_SPD": "RM_SPDD",
}

def translate_keycode(keycode: str) -> str:
    """
    Traduce keycodes renombrados entre versiones de QMK.
    Para keycodes compuestos (ej. LSFT(KC_MS_BTN1)) aplica la traduccion
    sobre el contenido interno si el keycode completo no esta en la tabla.
    """
    # Traduccion directa (keycode simple)
    if keycode in _KEYCODE_TRANSLATIONS:
        return _KEYCODE_TRANSLATIONS[keycode]
    # Para keycodes compuestos, sustituir ocurrencias internas
    result = keycode
    for old, new in _KEYCODE_TRANSLATIONS.items():
        result = result.replace(old, new)
    return result


def resolve_keycode_phase2(moon_id: str, layer_data: dict, warnings: list) -> str:
    """
    Fase 2: acepta todos los keycodes QMK estandar y de i18n (ES_*).
    Bloquea solo patrones de fases futuras o ZSA-exclusivos.
    Traduce keycodes renombrados en versiones modernas de QMK.
    """
    if not moon_id:
        return "KC_TRNS"

    keycode = layer_data.get(moon_id, "KC_TRNS")
    if not keycode:
        return "KC_TRNS"

    for pattern in _BLOCKED_PHASE2:
        if pattern.search(keycode):
            warnings.append(f"    {moon_id:5s}: '{keycode}' -> KC_TRNS  (no soportado en Fase 2)")
            return "KC_TRNS"

    return translate_keycode(keycode)


def build_layout_block(layer_num: int, layer_data: dict, geonix_mapping: list,
                       invert: bool, resolver, warnings: list) -> str:
    """
    Construye el bloque [N] = LAYOUT_tkl_ansi(...) para el Geonix R2.

    Reglas del mapping.json:
    - El grid es de 4×12 (48 celdas).
    - Primero se aplica invert_layout si es True (inversión de filas y columnas).
    - Después se ignora SIEMPRE la celda [fila=3][col=6] (hueco de la barra 2U).
    - Resultado: exactamente 47 keycodes para LAYOUT_tkl_ansi.
    """
    grid = [row[:] for row in geonix_mapping]
    if invert:
        grid = [row[::-1] for row in grid[::-1]]

    all_keys = []
    for r_idx, row in enumerate(grid):
        for c_idx, moon_id in enumerate(row):
            if r_idx == 3 and c_idx == 6:
                continue  # hueco barra espaciadora 2U — siempre ignorado
            all_keys.append(resolver(moon_id, layer_data, warnings))

    assert len(all_keys) == 47, \
        f"[BUG] Capa {layer_num}: {len(all_keys)} keycodes generados, se esperan exactamente 47"

    return _format_layout_block(layer_num, all_keys)


def _format_layout_block(layer_num: int, keys: list) -> str:
    """
    Formatea 47 keycodes con columnas alineadas, estilo default/keymap.c.

    Filas:  Row 0 = keys[0..11]   (12 teclas)
            Row 1 = keys[12..23]  (12 teclas)
            Row 2 = keys[24..35]  (12 teclas)
            Row 3 = keys[36..46]  (11 teclas + gap visual donde iria col 5)

    Alineacion por columnas visuales 0-11:
      Cols 0-4  -> presentes en las 4 filas
      Col 5     -> solo filas 0-2 (fila 3 tiene gap de barra 2U)
      Cols 6-11 -> filas 0-2 usan idx c; fila 3 usa idx c-1 (desplazado por el gap)
    """
    row0 = keys[0:12]
    row1 = keys[12:24]
    row2 = keys[24:36]
    row3 = keys[36:47]  # 11 teclas

    def col_w(c):
        if c <= 4:
            return max(len(row0[c]), len(row1[c]), len(row2[c]), len(row3[c]))
        elif c == 5:
            return max(len(row0[5]), len(row1[5]), len(row2[5]))
        else:  # 6-11: row3 tiene offset -1 respecto al indice visual
            return max(len(row0[c]), len(row1[c]), len(row2[c]), len(row3[c - 1]))

    w = [col_w(c) for c in range(12)]
    IND = "        "

    def fmt_full_row(row, trailing):
        # (key + ",").ljust(w+2): coma pegada al keycode, espacios detras
        parts = [(k + ",").ljust(w[c] + 2) for c, k in enumerate(row[:11])]
        parts.append(row[11] + trailing)   # ultima columna: sin padding
        return IND + "".join(parts)

    def fmt_bottom_row(row):
        parts  = [(k + ",").ljust(w[c] + 2) for c, k in enumerate(row[:5])]
        parts += [" " * (w[5] + 2)]                      # gap barra 2U
        parts += [(k + ",").ljust(w[6 + i] + 2) for i, k in enumerate(row[5:10])]
        parts += [row[10]]                               # ultima sin coma
        return IND + "".join(parts)

    return "\n".join([
        f"    [{layer_num}] = LAYOUT_tkl_ansi(",
        fmt_full_row(row0, ","),
        fmt_full_row(row1, ","),
        fmt_full_row(row2, ","),
        fmt_bottom_row(row3),
        "    )",
    ])


# ==============================================================================
# GENERACIÓN DE ARCHIVOS DE SALIDA
# ==============================================================================
def generate_keymap_c(layer_blocks: list) -> str:
    lines = [
        "#include QMK_KEYBOARD_H",
        '#include "rdmctmzt_common.h"',
        '#include "i18n.h"',
        "",
        "// clang-format off",
        "const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {",
        ",\n".join(layer_blocks),
        "};",
        "// clang-format on",
        "",
    ]
    return "\n".join(lines)


def generate_rules_mk() -> str:
    return (
        "# Generado automaticamente por convert_moonlander.py\n"
        "# Fase 2: todas las capas, keycodes extendidos\n"
        "\n"
        "# DYNAMIC_KEYMAP_ENABLE debe quedar en yes: el rules.mk del teclado\n"
        "# incluye quantum/dynamic_keymap.c incondicionalmente y necesita esta flag.\n"
        "DYNAMIC_KEYMAP_ENABLE = yes\n"
        "\n"
        "# VIA desactivado (no se usa en este keymap)\n"
        "VIA_ENABLE            = no\n"
        "\n"
        "TAP_DANCE_ENABLE      = no\n"
        "MOUSEKEY_ENABLE       = yes\n"
        "EXTRAKEY_ENABLE       = yes\n"
    )


def generate_config_h() -> str:
    return "// Keymap config — generado por convert_moonlander.py (Fase 2)\n"


def generate_version_h() -> str:
    return '#define QMK_VERSION "ems107-port-phase2"\n'


# ==============================================================================
# PUNTO DE ENTRADA
# ==============================================================================
def run():
    print("\n" + "=" * 60)
    print("  convert_moonlander.py — Fase 2")
    print("  Todas las capas · keycodes extendidos")
    print("=" * 60 + "\n")

    # Validaciones
    for path, label in [(PATH_SOURCE, "keymap.c fuente"), (PATH_MAPPING, "mapping.json")]:
        if not os.path.exists(path):
            print(f"[ERROR] No se encuentra {label}: {path}")
            return False

    # Limpiar y crear directorio destino
    if os.path.exists(PATH_TARGET):
        print(f"[INFO] Limpiando: {PATH_TARGET}")
        shutil.rmtree(PATH_TARGET)
    os.makedirs(PATH_TARGET)

    # Cargar mapping
    with open(PATH_MAPPING, "r", encoding="utf-8") as f:
        mapping_data = json.load(f)
    geonix_mapping = mapping_data["geonix_layout"]
    invert_layout  = mapping_data.get("invert_layout", False)
    print(f"[INFO] mapping.json: grid {len(geonix_mapping)}x{len(geonix_mapping[0])}, invert={invert_layout}")

    # Parsear capas Moonlander
    with open(PATH_SOURCE, "r", encoding="utf-8") as f:
        content = f.read()
    moon_layers = parse_moonlander_layers(content)
    print(f"[INFO] Capas encontradas en fuente Moonlander: {sorted(moon_layers.keys())}")

    if 0 not in moon_layers:
        print("[ERROR] No se encontro la capa 0 en el keymap Moonlander fuente.")
        return False

    # --- Fase 2: generar TODAS las capas ---
    warnings = []
    layer_blocks = []
    for layer_num in sorted(moon_layers.keys()):
        block = build_layout_block(layer_num, moon_layers[layer_num], geonix_mapping,
                                   invert_layout, resolve_keycode_phase2, warnings)
        layer_blocks.append(block)
    print(f"[INFO] Capas generadas: {sorted(moon_layers.keys())}")

    if warnings:
        # Agrupar warnings por keycode para no repetir
        unique = sorted(set(warnings))
        print(f"\n[WARN] {len(unique)} sustitucion(es) -> KC_TRNS (keycodes de fases futuras):")
        for w in unique:
            print(w)

    # Escribir archivos
    print()
    files = {
        "keymap.c":  generate_keymap_c(layer_blocks),
        "rules.mk":  generate_rules_mk(),
        "config.h":  generate_config_h(),
        "version.h": generate_version_h(),
    }
    for filename, content_out in files.items():
        path = os.path.join(PATH_TARGET, filename)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content_out)
        print(f"[OK] {filename}")

    # Copiar i18n.h del fuente Moonlander
    shutil.copy2(os.path.join(PATH_REF_DIR, "i18n.h"), PATH_TARGET)
    print("[OK] i18n.h")

    print(f"\n{'=' * 60}")
    print(f"  Fase 2 completada -> {os.path.normpath(PATH_TARGET)}")
    print(f"{'=' * 60}")
    print("\nPara compilar (PowerShell):")
    print('  $env:MSYSTEM="MINGW64"; $env:CHERE_INVOKING="1"')
    print('  C:\\QMK_MSYS\\usr\\bin\\bash.exe -lc "qmk compile -kb chosfox/geonixr2 -km zsa-moonlander --clean"')
    return True


if __name__ == "__main__":
    success = run()
    raise SystemExit(0 if success else 1)
