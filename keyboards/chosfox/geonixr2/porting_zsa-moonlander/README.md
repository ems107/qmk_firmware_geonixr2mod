# Moonlander → Geonix R2 Keymap Converter

Herramienta de conversión automática de keymaps ZSA Moonlander al firmware QMK del Chosfox Geonix R2.

## Estructura de directorios

```
porting_zsa-moonlander/
├── convert_moonlander.py          # Script principal de conversión
├── mapping.json                   # Configuración: mapeo de posiciones y overrides
├── README.md                      # Este fichero
└── reference/
    └── zsa_moonlander_test-layout_source/
        ├── keymap.c               # Fuente original del Moonlander (no modificar)
        ├── config.h               # Config original del Moonlander
        ├── rules.mk               # Rules original del Moonlander
        └── i18n.h                 # Definiciones de keycodes internacionales
```

El script genera (y sobreescribe cada ejecución) el keymap completo en:

```
keymaps/zsa-moonlander/
├── keymap.c      # Keymap generado
├── config.h      # Config generada (defines portados)
├── rules.mk      # Rules generado
├── version.h     # Versión del build
└── i18n.h        # Copiado del fuente
```

---

## Cómo ejecutar

Desde la raíz del repositorio:

```powershell
python keyboards/chosfox/geonixr2/porting_zsa-moonlander/convert_moonlander.py
```

Para compilar el resultado:

```powershell
$env:MSYSTEM="MINGW64"; $env:CHERE_INVOKING="1"
C:\QMK_MSYS\usr\bin\bash.exe -lc "qmk compile -kb chosfox/geonixr2 -km zsa-moonlander --clean"
```

---

## Qué hace el script

1. **Limpia** el directorio `keymaps/zsa-moonlander/` antes de regenerar.
2. **Parsea** el `keymap.c` del Moonlander y extrae:
   - Todas las capas (`[0]` a `[11]`)
   - `enum custom_keycodes` (macros `ST_MACRO_*`)
   - `enum tap_dance_codes` y todas las funciones de Tap Dance
   - `#define DUAL_FUNC_*`
   - `process_record_user` (limpiado de código RGB ZSA-exclusivo)
   - `ledmap` RGB (adaptado de 72 LEDs Moonlander a 47 LEDs Geonix)
   - Funciones RGB: `hsv_to_rgb_with_value`, `set_layer_color`, `rgb_matrix_indicators_user`
3. **Aplica el mapeo** de posiciones definido en `mapping.json` para traducir cada tecla Moonlander a su posición equivalente en el Geonix.
4. **Aplica overrides** (si los hay) para sustituir keycodes concretos en posiciones específicas.
5. **Genera** todos los ficheros del keymap.

---

## mapping.json — Referencia completa

### `invert_layout` (boolean)

Indica si el teclado Geonixr2 está girado 180°.

```json
"invert_layout": true
```

Cuando es `true`, la matriz de posiciones se invierte (filas al revés, columnas al revés) antes de procesarse. Esto permite que el usuario piense en coordenadas visuales del teclado tal como lo tiene delante, y el script aplica la transformación automáticamente.

---

### `geonix_layout` (array 4×12)

Define qué tecla del Moonlander ocupa cada posición física del Geonix R2.

```json
"geonix_layout": [
    ["L11", "L12", "L13", "L14", "L15",    "",    "", "R11", "R12", "R13", "R14", "R15"],
    ["L21", "L22", "L23", "L24", "L25", "L52", "R50", "R21", "R22", "R23", "R24", "R25"],
    ["L31", "L32", "L33", "L34", "L35", "L45", "R40", "R30", "R31", "R32", "R33", "R34"],
    [   "",    "",    "", "L44", "L50", "L51", "R51", "R52", "R41",    "",    "",    ""]
]
```

**IDs del Moonlander:** `L` = mano izquierda, `R` = mano derecha. El primer dígito es la fila (0–5), el segundo la columna (0–6).

```
MANO IZQUIERDA                    MANO DERECHA
F0: L00 L01 L02 L03 L04 L05 L06 | R00 R01 R02 R03 R04 R05 R06
F1: L10 L11 L12 L13 L14 L15 L16 | R10 R11 R12 R13 R14 R15 R16
F2: L20 L21 L22 L23 L24 L25 L26 | R20 R21 R22 R23 R24 R25 R26
F3: L30 L31 L32 L33 L34 L35     |     R30 R31 R32 R33 R34 R35
F4: L40 L41 L42 L43 L44 L45     |     R40 R41 R42 R43 R44 R45
            PULGAR: L50 L51 L52 | R50 R51 R52
```

**Posición especial:** La celda `[fila_3][col_6]` siempre se omite. Corresponde al hueco del spacebar 2U del Geonix y nunca genera un keycode. El LAYOUT resultante tiene siempre exactamente 47 keycodes.

**Strings vacíos `""`:** Una posición vacía significa que no hay tecla Moonlander mapeada en esa posición del Geonix. Genera `KC_TRNS` (transparente — hereda la capa inferior).

---

### `overrides` (object)

Sistema de parche manual por capas. Permite sobreescribir keycodes concretos en posiciones específicas sin modificar el keymap generado a mano (que se sobreescribiría en la siguiente ejecución).

```json
"overrides": {
    "0": [
        ["", "", "", "", "", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", "", "", "", "", ""]
    ],
    "1": [ ... ]
}
```

**Claves:** número de capa como string (`"0"`, `"1"`, ..., `"11"`).

**Valor:** matriz 4×12 con QMK keycodes directos (no IDs Moonlander).

**Semántica de celdas:**
- `""` (string vacío) → no overridear esta posición; usa el keycode que generaría la conversión automática del Moonlander.
- `"KC_ESC"` (cualquier QMK keycode válido) → sustituye incondicionalmente el keycode en esa posición.

**Orientación:** misma que `geonix_layout`. Si `invert_layout` es `true`, la matriz de overrides también se invierte antes de aplicarse. Escribe en las coordenadas visuales que te resulten naturales.

**Posición especial:** La celda `[fila_3][col_6]` también se ignora, igual que en `geonix_layout`.

**Ejemplo:** colocar `KC_ESC` en la posición visual `[fila_1][col_2]` de la capa 0:

```json
"0": [
    ["", "", "", "", "", "", "", "", "", "", "", ""],
    ["", "", "KC_ESC", "", "", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "",    "", "", "",    "", "", ""]
]
```

---

## Keycodes y traducciones

### Traducciones automáticas

El script traduce automáticamente keycodes renombrados entre la versión QMK del Moonlander y la del Geonix R2:

| Moonlander | Geonix R2 |
|---|---|
| `KC_MS_UP/DOWN/LEFT/RIGHT` | `MS_UP/DOWN/LEFT/RGHT` |
| `KC_MS_BTN1..5` | `MS_BTN1..5` |
| `KC_MS_WH_UP/DOWN/LEFT/RIGHT` | `MS_WHLU/WHLD/WHLL/WHLR` |
| `KC_MS_ACCEL0..2` | `MS_ACL0..2` |
| `RGB_TOG`, `RGB_HUI`, `RGB_VAI`... | `RM_TOGG`, `RM_HUEU`, `RM_VALU`... |

### Keycodes bloqueados → `KC_NO`

Los siguientes keycodes ZSA-exclusivos no tienen equivalente en el Geonix y se convierten en `KC_NO` (tecla muerta — no hace nada, no hereda capas inferiores):

- `RGB_SLD`, `HSV_*`, `TOGGLE_LAYER_COLOR` — control RGB ZSA propietario
- `AU_TOGG`, `MU_TOGG`, `MU_NEXT` — audio (no disponible en este firmware)

El script imprime un `[WARN]` por cada sustitución.

---

## Lógica RGB

El Moonlander define un `ledmap` con colores HSV por tecla para capas concretas (tipicamente la capa de ratón y la de gaming). El script:

1. Parsea el `ledmap` original (72 entradas por capa, una por LED Moonlander).
2. Usa el mismo `geonix_layout` + `invert_layout` para construir un mapeo de LED Moonlander → LED Geonix.
3. Genera un nuevo `ledmap` con exactamente 47 entradas por capa.
4. Genera `rgb_matrix_indicators_user` adaptado (sin dependencias ZSA como `rawhid_state`).

Solo las capas con datos de color en el `ledmap` original tendrán iluminación específica. El resto usa el comportamiento por defecto del RGB Matrix.
