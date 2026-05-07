import re
import os
import json
import shutil

# ==============================================================================
# RUTAS DE ARCHIVOS
# ==============================================================================
# Rutas relativas al script
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
PATH_SOURCE  = os.path.join(BASE_DIR, "reference/zsa_moonlander_test-layout_source/keymap.c")
PATH_REF_DIR = os.path.join(BASE_DIR, "reference/zsa_moonlander_test-layout_source")
PATH_MAPPING = os.path.join(BASE_DIR, "mapping.json")
PATH_TARGET  = os.path.join(BASE_DIR, "../keymaps/zsa-moonlander")

# Orden interno del Moonlander para el parser
MOON_ORDER = [
    "L00", "L01", "L02", "L03", "L04", "L05", "L06", "R00", "R01", "R02", "R03", "R04", "R05", "R06",
    "L10", "L11", "L12", "L13", "L14", "L15", "L16", "R10", "R11", "R12", "R13", "R14", "R15", "R16",
    "L20", "L21", "L22", "L23", "L24", "L25", "L26", "R20", "R21", "R22", "R23", "R24", "R25", "R26",
    "L30", "L31", "L32", "L33", "L34", "L35",        "R30", "R31", "R32", "R33", "R34", "R35",
    "L40", "L41", "L42", "L43", "L44", "L45",        "R40", "R41", "R42", "R43", "R44", "R45",
    "L50", "L51", "L52",                             "R50", "R51", "R52"
]

def parse_moonlander_layers(content):
    layers = {}
    matches = re.finditer(r'\[(\d+)\]\s*=\s*LAYOUT_moonlander\((.*?)\),', content, re.DOTALL)
    for match in matches:
        layer_num = int(match.group(1))
        keys_str = match.group(2)
        keys = []
        depth = 0
        current = ""
        for char in keys_str:
            if char == '(' : depth += 1
            elif char == ')': depth -= 1
            if char == ',' and depth == 0:
                keys.append(current.strip())
                current = ""
            else:
                current += char
        keys.append(current.strip())
        
        layer_data = {}
        for i, key in enumerate(keys):
            if i < len(MOON_ORDER):
                layer_data[MOON_ORDER[i]] = key
        layers[layer_num] = layer_data
    return layers

def generate_geonix_layer(layer_data, geonix_mapping, invert):
    # 1. Aplicar inversión si es necesario (rotación 180 grados)
    # Formula: (r, c) -> (max_r - r, max_c - c)
    if invert:
        # Invertir orden de filas y luego invertir cada fila
        geonix_mapping = [row[::-1] for row in geonix_mapping[::-1]]

    rows = []
    for r_idx, row in enumerate(geonix_mapping):
        row_keys = []
        for c_idx, moon_id in enumerate(row):
            # 2. Ignorar la posición 6 de la última fila (la tecla 2u del centro en Geonix R2)
            # Esto se aplica al RESULTADO de la inversión.
            if r_idx == 3 and c_idx == 6:
                continue
            
            key = layer_data.get(moon_id, "KC_NO")
            if not key or key == "": key = "KC_NO"
            row_keys.append(key)
        
        line = "    " + ", ".join(row_keys)
        rows.append(line)
    
    return "  LAYOUT_tkl_ansi(\n" + ",\n".join(rows) + "\n  )"

def run():
    print("Iniciando proceso de portabilidad...")
    
    # 1. Validaciones
    if not os.path.exists(PATH_SOURCE):
        print(f"Error: No se encuentra {PATH_SOURCE}")
        return
    if not os.path.exists(PATH_MAPPING):
        print(f"Error: No se encuentra {PATH_MAPPING}")
        return

    # 2. Limpiar carpeta destino
    if os.path.exists(PATH_TARGET):
        print(f"Limpiando directorio destino: {PATH_TARGET}")
        shutil.rmtree(PATH_TARGET)
    os.makedirs(PATH_TARGET)

    # 3. Leer mapeo y fuente
    with open(PATH_MAPPING, "r", encoding="utf-8") as f:
        mapping_data = json.load(f)
        geonix_mapping = mapping_data["geonix_layout"]
        invert_layout  = mapping_data.get("invert_layout", False)

    with open(PATH_SOURCE, "r", encoding="utf-8") as f:
        content = f.read()

    # 4. Parsear capas y secciones
    moon_layers = parse_moonlander_layers(content)
    extra_sections = []
    
    enums = re.search(r'enum custom_keycodes \{.*?\};', content, re.DOTALL)
    if enums: extra_sections.append(enums.group(0))
    
    td_enums = re.search(r'enum tap_dance_codes \{.*?\};', content, re.DOTALL)
    if td_enums: extra_sections.append(td_enums.group(0))
    
    defines = re.findall(r'#define\s+\w+\s+.*?\n', content)
    for d in defines:
        if "MOON_LED_LEVEL" not in d and "ZSA_SAFE_RANGE" not in d:
            extra_sections.append(d.strip())

    # 5. Generar keymap.c
    new_content = [
        '#include QMK_KEYBOARD_H',
        '#include "i18n.h"',
        '#include "version.h"',
        '',
        '// Secciones extraídas del Moonlander',
        '\n'.join(extra_sections),
        '',
        'const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {'
    ]

    for layer_num in sorted(moon_layers.keys()):
        new_content.append(f'  [{layer_num}] = {generate_geonix_layer(moon_layers[layer_num], geonix_mapping, invert_layout)},')
    
    new_content.append('};')
    
    td_logic = re.search(r'void on_dance_0.*?tap_dance_action_t tap_dance_actions\[\] = \{.*?\};', content, re.DOTALL)
    if td_logic:
        new_content.append('\n' + td_logic.group(0))
        
    process_user = re.search(r'bool process_record_user\(uint16_t keycode, keyrecord_t \*record\) \{.*?\}', content, re.DOTALL)
    if process_user:
        new_content.append('\n' + process_user.group(0))

    # Guardar keymap.c
    with open(os.path.join(PATH_TARGET, "keymap.c"), "w", encoding="utf-8") as f:
        f.write('\n'.join(new_content))

    # 6. Copiar archivos de soporte necesarios
    support_files = ["i18n.h", "rules.mk", "config.h"]
    for s_file in support_files:
        src_path = os.path.join(PATH_REF_DIR, s_file)
        if os.path.exists(src_path):
            print(f"Copiando archivo de soporte: {s_file}")
            shutil.copy2(src_path, PATH_TARGET)
        else:
            print(f"Aviso: No se encontró {s_file} en la referencia.")

    # Crear un version.h básico si no existe (Moonlander suele requerirlo)
    version_path = os.path.join(PATH_TARGET, "version.h")
    if not os.path.exists(version_path):
        with open(version_path, "w") as f:
            f.write('#define QMK_VERSION "ems107-port"\n')

    print(f"\n¡Éxito! Keymap completo generado en: {PATH_TARGET}")
    print("Ahora puedes compilar usando el comando definido en GEMINI.md.")

if __name__ == "__main__":
    run()
