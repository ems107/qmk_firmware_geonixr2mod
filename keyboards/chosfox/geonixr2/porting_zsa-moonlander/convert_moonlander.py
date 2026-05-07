#!/usr/bin/env python3
"""
convert_moonlander.py
Porta el keymap ZSA Moonlander al Chosfox Geonix R2.

Estado actual: Fase 1 — capa 0, keycodes básicos KC_* únicamente.
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
# GENERACIÓN DEL LAYOUT GEONIX
# ==============================================================================
def resolve_keycode_phase1(moon_id: str, layer_data: dict, warnings: list) -> str:
    """
    Fase 1: resuelve el keycode para una posición del Geonix.
    - moon_id vacío ("") -> KC_TRNS (posición sin asignación en el mapping)
    - keycode básico KC_* -> se usa tal cual
    - cualquier otro -> KC_TRNS + warning
    """
    if not moon_id:
        return "KC_TRNS"

    keycode = layer_data.get(moon_id, "KC_TRNS")
    if not keycode:
        return "KC_TRNS"

    if is_basic_keycode(keycode):
        return keycode

    warnings.append(f"    {moon_id:5s}: '{keycode}' -> KC_TRNS  (no soportado en Fase 1)")
    return "KC_TRNS"


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

    # Formatear en 4 filas: 12, 12, 12, 11
    row_sizes = [12, 12, 12, 11]
    formatted_rows = []
    idx = 0
    for size in row_sizes:
        chunk = all_keys[idx:idx + size]
        formatted_rows.append("        " + ", ".join(chunk))
        idx += size

    body = ",\n".join(formatted_rows)
    return f"    [{layer_num}] = LAYOUT_tkl_ansi(\n{body}\n    )"


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
        "# Fase 1: capa 0, keycodes basicos unicamente\n"
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
    return "// Keymap config — generado por convert_moonlander.py (Fase 1)\n"


def generate_version_h() -> str:
    return '#define QMK_VERSION "ems107-port-phase1"\n'


# ==============================================================================
# PUNTO DE ENTRADA
# ==============================================================================
def run():
    print("\n" + "=" * 60)
    print("  convert_moonlander.py — Fase 1")
    print("  Capa 0 · solo keycodes básicos KC_*")
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
    print(f"[INFO] mapping.json: grid {len(geonix_mapping)}×{len(geonix_mapping[0])}, invert={invert_layout}")

    # Parsear capas Moonlander
    with open(PATH_SOURCE, "r", encoding="utf-8") as f:
        content = f.read()
    moon_layers = parse_moonlander_layers(content)
    print(f"[INFO] Capas encontradas en fuente Moonlander: {sorted(moon_layers.keys())}")

    if 0 not in moon_layers:
        print("[ERROR] No se encontró la capa 0 en el keymap Moonlander fuente.")
        return False

    # --- Fase 1: generar solo capa 0 ---
    warnings = []
    block = build_layout_block(0, moon_layers[0], geonix_mapping, invert_layout,
                               resolve_keycode_phase1, warnings)
    layer_blocks = [block]

    omitted = sorted(n for n in moon_layers if n != 0)
    if omitted:
        print(f"[INFO] Capas omitidas (Fase 1): {omitted} -> se añadirán en Fase 2")

    if warnings:
        print(f"\n[WARN] {len(warnings)} keycode(s) no soportados -> KC_TRNS:")
        for w in warnings:
            print(w)
    else:
        print("[INFO] Sin warnings — todos los keycodes de la capa 0 son básicos.")

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
    print(f"  Fase 1 completada -> {os.path.normpath(PATH_TARGET)}")
    print(f"{'=' * 60}")
    print("\nPara compilar (PowerShell):")
    print('  $env:MSYSTEM="MINGW64"; $env:CHERE_INVOKING="1"')
    print('  C:\\QMK_MSYS\\usr\\bin\\bash.exe -lc "qmk compile -kb chosfox/geonixr2 -km zsa-moonlander --clean"')
    return True


if __name__ == "__main__":
    success = run()
    raise SystemExit(0 if success else 1)
