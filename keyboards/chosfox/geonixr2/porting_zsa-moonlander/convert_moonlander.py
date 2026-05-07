#!/usr/bin/env python3
"""
convert_moonlander.py
Porta el keymap ZSA Moonlander al Chosfox Geonix R2.

Estado actual: Fase 5 -- Adaptacion RGB (ledmap + indicadores por capa).
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
# Cada ID identifica una posicion fisica: L=izquierda, R=derecha, fila+columna.
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
# FASE 1: FILTRO DE KEYCODES BASICOS (mantenido por referencia interna)
# ==============================================================================
def is_basic_keycode(keycode: str) -> bool:
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
# FASE 4: PARSEO DE config.h DEL FUENTE MOONLANDER
# Extrae defines de timing y comportamiento seguros para el Geonix R2.
# Descarta defines ZSA-exclusivos o de Fase 5 (RGB).
# ==============================================================================

# Defines que se omiten aunque aparezcan en el config.h fuente:
_CONFIG_BLOCKLIST = {
    "SERIAL_NUMBER",        # identificador unico ZSA, no aplica
    "RGB_MATRIX_STARTUP_SPD", # Fase 5
    "RGB_MATRIX_STARTUP_MODE",
    "RGB_MATRIX_STARTUP_HUE",
    "RGB_MATRIX_STARTUP_SAT",
    "RGB_MATRIX_STARTUP_VAL",
    "ORYX_CONFIGURATOR",    # ZSA-specific
    "FIRMWARE_VERSION",     # ZSA-specific
}

def parse_ref_config_h(ref_dir: str) -> str:
    """
    Lee el config.h del fuente Moonlander y extrae solo los defines
    que son seguros para el Geonix R2.
    Devuelve el bloque listo para escribir en el config.h generado.
    """
    path = os.path.join(ref_dir, "config.h")
    if not os.path.exists(path):
        return ""

    lines = []
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    for line in raw.splitlines():
        stripped = line.strip()
        # Solo procesar lineas #define
        if not stripped.startswith("#define"):
            continue
        # Extraer nombre del define
        parts = stripped.split()
        define_name = parts[1] if len(parts) > 1 else ""
        if define_name in _CONFIG_BLOCKLIST:
            continue
        lines.append(line)

    if not lines:
        return ""
    return "\n".join(lines)


def _extract_block(content: str, open_pos: int) -> str:
    """Extrae el bloque delimitado por llaves comenzando en open_pos ('{')."""
    depth = 1
    i = open_pos + 1
    while i < len(content) and depth > 0:
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
        i += 1
    return content[open_pos:i]


def parse_tap_dance_enum(content: str) -> str:
    """Extrae 'enum tap_dance_codes { ... };' del fuente."""
    m = re.search(r'enum tap_dance_codes\s*\{([^}]*)\}', content)
    if not m:
        return ""
    return m.group(0) + ";"


def parse_dual_func_defines(content: str) -> list:
    """Extrae todos los #define DUAL_FUNC_* del fuente."""
    return re.findall(r'#define\s+DUAL_FUNC_\d+\s+[^\n]+', content)


def build_custom_keycodes_enum(content: str) -> str:
    """
    Construye enum custom_keycodes con solo los ST_MACRO_* del fuente.
    Arranca con SAFE_RANGE (no con ZSA_SAFE_RANGE).
    """
    m = re.search(r'enum custom_keycodes\s*\{([^}]*)\}', content)
    if not m:
        return ""
    macros = re.findall(r'ST_MACRO_\d+', m.group(1))
    if not macros:
        return ""
    entries = [f"    {macros[0]} = SAFE_RANGE,"]
    entries += [f"    {x}," for x in macros[1:]]
    return "enum custom_keycodes {\n" + "\n".join(entries) + "\n};"


def parse_tap_dance_block(content: str) -> str:
    """
    Extrae el bloque de Tap Dance desde 'typedef struct { bool is_press_action'
    hasta el cierre de 'tap_dance_action_t tap_dance_actions[]'.
    """
    start_m = re.search(r'typedef struct \{\s*\n\s*bool is_press_action', content)
    if not start_m:
        return ""
    end_m = re.search(r'tap_dance_action_t tap_dance_actions\[\]\s*=\s*\{', content)
    if not end_m:
        return ""
    brace_pos = end_m.end() - 1
    block_end = content.index('};', brace_pos) + 2
    return content[start_m.start():block_end]


def parse_process_record_user(content: str) -> str:
    """
    Extrae process_record_user del fuente y lo sanitiza para Fase 3.
    Estrategia: copia todo hasta llegar a 'case RGB_SLD:' o 'case HSV_',
    luego cierra el switch y la funcion limpiamente.
    """
    m = re.search(r'bool process_record_user\s*\(', content)
    if not m:
        return ""

    # Find function start
    brace_pos = content.index('{', m.end())
    func_start = content[m.start():brace_pos + 1]

    # Extract inner body up to the first RGB/ZSA case
    inner_start = brace_pos + 1
    # Find where RGB cases begin (these are always last in the switch)
    rgb_case = re.search(r'\n\s*case RGB_SLD:', content[inner_start:])
    hsv_case = re.search(r'\n\s*case HSV_\d+', content[inner_start:])

    cut_points = []
    if rgb_case:
        cut_points.append(rgb_case.start())
    if hsv_case:
        cut_points.append(hsv_case.start())

    if cut_points:
        cut = min(cut_points)
        inner = content[inner_start: inner_start + cut]
    else:
        # No RGB cases found: use full function
        end_m = re.search(r'\n\s*return true;\s*\n\}', content[inner_start:])
        inner = content[inner_start: inner_start + end_m.end()] if end_m else ""

    # Rebuild function: signature + filtered inner + clean closing
    return func_start.strip() + "\n" + inner.rstrip() + "\n  }\n  return true;\n}"


# ==============================================================================
# RESOLVER DE KEYCODES (Fase 5: lista final)
# RGB_SLD / HSV_* / TOGGLE_LAYER_COLOR son keycodes custom ZSA sin equivalente
# en el Geonix. Se mantienen como KC_TRNS en el layout.
# ==============================================================================
_BLOCKED = [
    re.compile(r'^RGB_SLD$'),
    re.compile(r'^HSV_\d+_\d+_\d+$'),
    re.compile(r'^TOGGLE_LAYER_COLOR$'),
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
    "KC_MS_RIGHT": "MS_RGHT",
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
    if keycode in _KEYCODE_TRANSLATIONS:
        return _KEYCODE_TRANSLATIONS[keycode]
    result = keycode
    for old, new in _KEYCODE_TRANSLATIONS.items():
        result = result.replace(old, new)
    return result


def resolve_keycode_phase3(moon_id: str, layer_data: dict, warnings: list) -> str:
    """
    Resuelve el keycode para una posicion del Geonix.
    TD(), ST_MACRO_*, DUAL_FUNC_* son validos. RGB ZSA-exclusivos -> KC_TRNS.
    """
    if not moon_id:
        return "KC_TRNS"
    keycode = layer_data.get(moon_id, "KC_TRNS")
    if not keycode:
        return "KC_TRNS"
    for pattern in _BLOCKED:
        if pattern.search(keycode):
            warnings.append(f"    {moon_id:5s}: '{keycode}' -> KC_NO  (keycode ZSA sin equivalente)")
            return "KC_NO"
    return translate_keycode(keycode)


# ==============================================================================
# FASE 5: ADAPTACION RGB
# El Moonlander tiene 72 LEDs. El Geonix R2 tiene 47.
# Mapeamos las posiciones usando el mismo mapping.json.
# ==============================================================================

def build_led_mapping(geonix_mapping: list, invert: bool) -> list:
    """
    Devuelve lista de 47 elementos (indice LED del Moonlander o None)
    en el mismo orden de iteracion que build_layout_block.
    """
    moon_id_to_led = {mid: idx for idx, mid in enumerate(MOON_ORDER)}
    grid = [row[:] for row in geonix_mapping]
    if invert:
        grid = [row[::-1] for row in grid[::-1]]
    result = []
    for r_idx, row in enumerate(grid):
        for c_idx, moon_id in enumerate(row):
            if r_idx == 3 and c_idx == 6:
                continue
            result.append(moon_id_to_led.get(moon_id))
    return result


def parse_and_adapt_ledmap(content: str, led_mapping: list) -> tuple:
    """
    Parsea el ledmap del fuente Moonlander (72 LEDs/capa) y lo adapta
    a 47 LEDs del Geonix R2 usando el led_mapping.
    Devuelve (ledmap_c_string, dict_layer_num -> list_of_triplets).
    """
    m = re.search(r'const uint8_t PROGMEM ledmap\[\]\[RGB_MATRIX_LED_COUNT\]\[3\]\s*=\s*\{', content)
    if not m:
        return "", {}

    # Extraer el bloque completo del ledmap
    outer = content.index('{', m.start())
    depth, i = 1, outer + 1
    while i < len(content) and depth > 0:
        if content[i] == '{': depth += 1
        elif content[i] == '}': depth -= 1
        i += 1
    ledmap_block = content[outer + 1: i - 1]

    # Parsear cada entrada [N] = { ... }
    layer_data = {}
    for lm in re.finditer(r'\[(\d+)\]\s*=\s*\{', ledmap_block):
        ln = int(lm.group(1))
        start = lm.end() - 1  # position of '{'
        depth, j = 1, start + 1
        while j < len(ledmap_block) and depth > 0:
            if ledmap_block[j] == '{': depth += 1
            elif ledmap_block[j] == '}': depth -= 1
            j += 1
        inner = ledmap_block[start + 1: j - 1]
        triplets = re.findall(r'\{(\d+),(\d+),(\d+)\}', inner)
        layer_data[ln] = [(int(h), int(s), int(v)) for h, s, v in triplets]

    if not layer_data:
        return "", {}

    # Construir ledmap adaptado (47 LEDs)
    adapted = {}
    lines = ["const uint8_t PROGMEM ledmap[][RGB_MATRIX_LED_COUNT][3] = {"]
    for ln in sorted(layer_data):
        moon_colors = layer_data[ln]
        geonix_colors = []
        for moon_idx in led_mapping:
            if moon_idx is not None and moon_idx < len(moon_colors):
                geonix_colors.append(moon_colors[moon_idx])
            else:
                geonix_colors.append((0, 0, 0))
        adapted[ln] = geonix_colors
        triplet_strs = ", ".join(f"{{{h},{s},{v}}}" for h, s, v in geonix_colors)
        lines.append(f"    [{ln}] = {{ {triplet_strs} }},")
    lines.append("};")
    return "\n".join(lines), adapted


def build_rgb_post_block(content: str, adapted_layers: dict) -> str:
    """
    Genera el bloque RGB post-keymaps para el Geonix R2:
    - extern rgb_config_t
    - hsv_to_rgb_with_value (verbatim)
    - keyboard_post_init_user (verbatim)
    - set_layer_color (verbatim)
    - rgb_matrix_indicators_user (adaptado: sin rawhid_state ni keyboard_config)
    """
    parts = []

    # extern + hsv_to_rgb_with_value: copiar verbatim del fuente
    extern_m = re.search(r'extern rgb_config_t rgb_matrix_config;', content)
    hsv_fn_m = re.search(r'RGB hsv_to_rgb_with_value\s*\(', content)
    if extern_m and hsv_fn_m:
        brace_pos = content.index('{', hsv_fn_m.end())
        depth, i = 1, brace_pos + 1
        while i < len(content) and depth > 0:
            if content[i] == '{': depth += 1
            elif content[i] == '}': depth -= 1
            i += 1
        parts.append(content[extern_m.start():i].strip())

    # keyboard_post_init_user: verbatim
    kpiu_m = re.search(r'void keyboard_post_init_user\s*\(void\)\s*\{', content)
    if kpiu_m:
        brace_pos = kpiu_m.end() - 1
        depth, i = 1, brace_pos + 1
        while i < len(content) and depth > 0:
            if content[i] == '{': depth += 1
            elif content[i] == '}': depth -= 1
            i += 1
        parts.append(content[kpiu_m.start():i].strip())

    # set_layer_color: verbatim
    slc_m = re.search(r'void set_layer_color\s*\(', content)
    if slc_m:
        brace_pos = content.index('{', slc_m.end())
        depth, i = 1, brace_pos + 1
        while i < len(content) and depth > 0:
            if content[i] == '{': depth += 1
            elif content[i] == '}': depth -= 1
            i += 1
        parts.append(content[slc_m.start():i].strip())

    # rgb_matrix_indicators_user: generado sin ZSA-specific checks
    cases = []
    for ln in sorted(adapted_layers.keys()):
        cases.append(f"    case {ln}:")
        cases.append(f"      set_layer_color({ln});")
        cases.append(f"      break;")
    cases_str = "\n".join(cases)
    rgb_indicators = (
        "bool rgb_matrix_indicators_user(void) {\n"
        "  switch (biton32(layer_state)) {\n"
        + cases_str + "\n"
        "    default:\n"
        "      if (rgb_matrix_get_flags() == LED_FLAG_NONE) {\n"
        "        rgb_matrix_set_color_all(0, 0, 0);\n"
        "      }\n"
        "  }\n"
        "  return true;\n"
        "}"
    )
    parts.append(rgb_indicators)

    return "\n\n".join(parts)


# ==============================================================================
# CONSTRUCCION DEL LAYOUT GEONIX
# ==============================================================================
def build_keycodes(layer_num: int, layer_data: dict, geonix_mapping: list,
                   invert: bool, resolver, warnings: list) -> list:
    """Genera la lista de 47 keycodes para una capa sin formatear."""
    grid = [row[:] for row in geonix_mapping]
    if invert:
        grid = [row[::-1] for row in grid[::-1]]
    all_keys = []
    for r_idx, row in enumerate(grid):
        for c_idx, moon_id in enumerate(row):
            if r_idx == 3 and c_idx == 6:
                continue
            all_keys.append(resolver(moon_id, layer_data, warnings))
    assert len(all_keys) == 47, \
        f"[BUG] Capa {layer_num}: {len(all_keys)} keycodes, se esperan 47"
    return all_keys


def apply_override_patch(keycodes: list, override_matrix: list, invert: bool) -> tuple:
    """
    Parchea la lista de 47 keycodes con los valores no vacios del override.
    override_matrix: lista 4x12 con QMK keycodes o strings vacios.
    Mismo tratamiento que geonix_layout: aplica invert y skip [3][6].
    Retorna (lista_parchada, num_posiciones_parchadas).
    """
    grid = [row[:] for row in override_matrix]
    if invert:
        grid = [row[::-1] for row in grid[::-1]]
    flat = []
    for r_idx, row in enumerate(grid):
        for c_idx, val in enumerate(row):
            if r_idx == 3 and c_idx == 6:
                continue
            flat.append(val)
    if len(flat) != 47:
        raise ValueError(f"Override matrix genera {len(flat)} entradas, se esperan 47")
    patched = keycodes[:]
    count = 0
    for i, val in enumerate(flat):
        if val and val.strip():
            patched[i] = val.strip()
            count += 1
    return patched, count


def build_layout_block(layer_num: int, layer_data: dict, geonix_mapping: list,
                       invert: bool, resolver, warnings: list) -> str:
    """Wrapper de compatibilidad: genera keycodes y formatea."""
    keys = build_keycodes(layer_num, layer_data, geonix_mapping, invert, resolver, warnings)
    return _format_layout_block(layer_num, keys)


def _format_layout_block(layer_num: int, keys: list) -> str:
    row0, row1, row2, row3 = keys[0:12], keys[12:24], keys[24:36], keys[36:47]

    def col_w(c):
        if c <= 4:
            return max(len(row0[c]), len(row1[c]), len(row2[c]), len(row3[c]))
        elif c == 5:
            return max(len(row0[5]), len(row1[5]), len(row2[5]))
        else:
            return max(len(row0[c]), len(row1[c]), len(row2[c]), len(row3[c - 1]))

    w = [col_w(c) for c in range(12)]
    IND = "        "

    def fmt_full_row(row, trailing):
        parts = [(k + ",").ljust(w[c] + 2) for c, k in enumerate(row[:11])]
        parts.append(row[11] + trailing)
        return IND + "".join(parts)

    def fmt_bottom_row(row):
        parts  = [(k + ",").ljust(w[c] + 2) for c, k in enumerate(row[:5])]
        parts += [" " * (w[5] + 2)]
        parts += [(k + ",").ljust(w[6 + i] + 2) for i, k in enumerate(row[5:10])]
        parts += [row[10]]
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
# GENERACION DE ARCHIVOS DE SALIDA
# ==============================================================================
def generate_keymap_c(layer_blocks: list, pre_blocks: list, post_blocks: list) -> str:
    parts = [
        "#include QMK_KEYBOARD_H",
        '#include "rdmctmzt_common.h"',
        '#include "i18n.h"',
        "",
    ]
    for block in pre_blocks:
        if block:
            parts.append(block)
            parts.append("")
    parts += [
        "// clang-format off",
        "const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {",
        ",\n".join(layer_blocks),
        "};",
        "// clang-format on",
        "",
    ]
    for block in post_blocks:
        if block:
            parts.append(block)
            parts.append("")
    return "\n".join(parts)


def generate_rules_mk() -> str:
    return (
        "# Generado automaticamente por convert_moonlander.py\n"
        "# Fase 5: RGB adaptado + ledmap por capas\n"
        "\n"
        "# DYNAMIC_KEYMAP_ENABLE debe quedar en yes: el rules.mk del teclado\n"
        "# incluye quantum/dynamic_keymap.c incondicionalmente.\n"
        "DYNAMIC_KEYMAP_ENABLE = yes\n"
        "\n"
        "VIA_ENABLE            = no\n"
        "SPACE_CADET_ENABLE    = no\n"
        "\n"
        "TAP_DANCE_ENABLE      = yes\n"
        "MOUSEKEY_ENABLE       = yes\n"
        "EXTRAKEY_ENABLE       = yes\n"
    )


def generate_config_h(ported_defines: str) -> str:
    lines = [
        "// Keymap config -- generado por convert_moonlander.py (Fase 5)",
        "// Defines portados del config.h Moonlander (ZSA-exclusivos omitidos).",
        "",
    ]
    if ported_defines:
        lines.append(ported_defines)
    return "\n".join(lines) + "\n"


def generate_version_h() -> str:
    return '#define QMK_VERSION "ems107-port-phase5"\n'


# ==============================================================================
# PUNTO DE ENTRADA
# ==============================================================================
def run():
    print("\n" + "=" * 60)
    print("  convert_moonlander.py -- Fase 5")
    print("  RGB adaptado: ledmap + indicadores por capa")
    print("=" * 60 + "\n")

    for path, label in [(PATH_SOURCE, "keymap.c fuente"), (PATH_MAPPING, "mapping.json")]:
        if not os.path.exists(path):
            print(f"[ERROR] No se encuentra {label}: {path}")
            return False

    if os.path.exists(PATH_TARGET):
        print(f"[INFO] Limpiando: {PATH_TARGET}")
        shutil.rmtree(PATH_TARGET)
    os.makedirs(PATH_TARGET)

    with open(PATH_MAPPING, "r", encoding="utf-8") as f:
        mapping_data = json.load(f)
    geonix_mapping = mapping_data["geonix_layout"]
    invert_layout  = mapping_data.get("invert_layout", False)
    print(f"[INFO] mapping.json: grid {len(geonix_mapping)}x{len(geonix_mapping[0])}, invert={invert_layout}")

    with open(PATH_SOURCE, "r", encoding="utf-8") as f:
        content = f.read()

    moon_layers = parse_moonlander_layers(content)
    print(f"[INFO] Capas encontradas: {sorted(moon_layers.keys())}")

    if 0 not in moon_layers:
        print("[ERROR] No se encontro la capa 0.")
        return False

    # --- Generar todas las capas con resolver Fase 3 ---
    warnings = []
    layer_blocks = []
    overrides = mapping_data.get("overrides", {})

    warnings = []
    layer_blocks = []
    total_patched = 0
    for layer_num in sorted(moon_layers.keys()):
        keycodes = build_keycodes(layer_num, moon_layers[layer_num], geonix_mapping,
                                  invert_layout, resolve_keycode_phase3, warnings)
        override_key = str(layer_num)
        if override_key in overrides:
            keycodes, patch_count = apply_override_patch(keycodes, overrides[override_key], invert_layout)
            if patch_count > 0:
                print(f"[INFO] Override capa {layer_num}: {patch_count} posicion(es) parchada(s)")
                total_patched += patch_count
        block = _format_layout_block(layer_num, keycodes)
        layer_blocks.append(block)
    if total_patched:
        print(f"[INFO] Total overrides aplicados: {total_patched} posiciones")
    print(f"[INFO] Capas generadas: {sorted(moon_layers.keys())}")

    # --- Extraer bloques del fuente Moonlander ---
    custom_enum  = build_custom_keycodes_enum(content)
    td_enum      = parse_tap_dance_enum(content)
    dual_defines = parse_dual_func_defines(content)
    td_block     = parse_tap_dance_block(content)
    proc_record  = parse_process_record_user(content)

    # --- Fase 4: extraer defines del config.h fuente ---
    ported_defines = parse_ref_config_h(PATH_REF_DIR)
    if ported_defines:
        print(f"[OK] config.h defines portados:")
        for line in ported_defines.splitlines():
            print(f"       {line}")
    else:
        print("[INFO] config.h fuente sin defines portables.")

    for name, val in [("custom_keycodes enum", custom_enum),
                      ("tap_dance_codes enum", td_enum),
                      ("tap dance block",      td_block),
                      ("process_record_user",  proc_record)]:
        status = "OK" if val else "WARN: no encontrado"
        print(f"[{status}] {name}")
    for d in dual_defines:
        print(f"[INFO] Define extraido: {d}")

    if warnings:
        unique = sorted(set(warnings))
        print(f"\n[WARN] {len(unique)} keycode(s) ZSA sin equivalente -> KC_TRNS:")
        for w in unique:
            print(w)

    # --- Fase 5: RGB ---
    led_mapping = build_led_mapping(geonix_mapping, invert_layout)
    ledmap_str, adapted_layers = parse_and_adapt_ledmap(content, led_mapping)
    rgb_block = build_rgb_post_block(content, adapted_layers) if adapted_layers else ""
    if adapted_layers:
        print(f"[OK] RGB ledmap adaptado: capas {sorted(adapted_layers.keys())} ({len(led_mapping)} LEDs)")
    else:
        print("[INFO] Sin datos RGB en el fuente Moonlander.")

    # Bloques que van ANTES de los keymaps
    pre_blocks = [custom_enum, td_enum] + dual_defines

    # Bloques que van DESPUES de los keymaps (ledmap antes del bloque RGB)
    post_blocks = [td_block, proc_record, ledmap_str, rgb_block]

    print()
    keymap_c = generate_keymap_c(layer_blocks, pre_blocks, post_blocks)
    files = {
        "keymap.c":  keymap_c,
        "rules.mk":  generate_rules_mk(),
        "config.h":  generate_config_h(ported_defines),
        "version.h": generate_version_h(),
    }
    for filename, content_out in files.items():
        path = os.path.join(PATH_TARGET, filename)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content_out)
        print(f"[OK] {filename}")

    shutil.copy2(os.path.join(PATH_REF_DIR, "i18n.h"), PATH_TARGET)
    print("[OK] i18n.h")

    print(f"\n{'=' * 60}")
    print(f"  Fase 5 completada -> {os.path.normpath(PATH_TARGET)}")
    print(f"{'=' * 60}")
    print("\nPara compilar (PowerShell):")
    print('  $env:MSYSTEM="MINGW64"; $env:CHERE_INVOKING="1"')
    print('  C:\\QMK_MSYS\\usr\\bin\\bash.exe -lc "qmk compile -kb chosfox/geonixr2 -km zsa-moonlander --clean"')
    return True


if __name__ == "__main__":
    success = run()
    raise SystemExit(0 if success else 1)
