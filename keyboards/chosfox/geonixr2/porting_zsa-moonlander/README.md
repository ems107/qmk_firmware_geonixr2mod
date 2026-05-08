# Moonlander → Geonix R2 Keymap Converter

Herramienta de conversión automática de keymaps ZSA Moonlander al firmware QMK del Chosfox Geonix R2.

## Estructura de directorios

```
porting_zsa-moonlander/
├── convert_moonlander.py          # Script principal de conversión
├── mapping.json                   # Configuración: mapeo de posiciones, overrides y flags
├── README.md                      # Este fichero
├── led_config/                    # Sistema de personalización de LEDs indicadores
│   ├── led_config.json            # Configuración de posiciones y colores de LEDs
│   └── led_config_gen.py          # Generador de led_indicators.h (llamado por convert_moonlander.py)
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
├── keymap.c           # Keymap generado (capas, TD, macros, RGB, FN_LAYERS[])
├── config.h           # Config generada (define portados + #include "led_indicators.h" si aplica)
├── rules.mk           # Rules generado
├── version.h          # Versión del build
├── i18n.h             # Copiado del fuente
└── led_indicators.h   # Generado por led_config_gen.py (solo si hasToOverrideLedConfig=true)
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
5. **Si `hasToOverrideLedConfig: true`**, llama a `led_config_gen.py` para generar `led_indicators.h` con la configuración de LEDs personalizada e inyecta `FN_LAYERS[]` y `#include "led_indicators.h"` en los ficheros generados.
6. **Genera** todos los ficheros del keymap.

---

## mapping.json — Referencia completa

### `invert_layout` (boolean)

Indica si el teclado Geonixr2 está girado 180°.

```json
"invert_layout": true
```

Cuando es `true`, la matriz de posiciones se invierte (filas al revés, columnas al revés) antes de procesarse. Esto permite que el usuario piense en coordenadas visuales del teclado tal como lo tiene delante, y el script aplica la transformación automáticamente.

---

### `hasToOverrideLedConfig` (boolean)

Activa el sistema de personalización de LEDs indicadores del sistema.

```json
"hasToOverrideLedConfig": true
```

- **`false` (por defecto):** el script no llama a `led_config_gen.py`. El keymap generado usa los valores de `LED_*_INDEX` definidos en `keyboards/chosfox/geonixr2/config.h`. Comportamiento idéntico al original.
- **`true`:** el script llama a `led_config_gen.py` al final de la generación, que lee `led_config/led_config.json` y genera `keymaps/zsa-moonlander/led_indicators.h`. Este fichero sobreescribe los índices LED por defecto con los configurados por el usuario.

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

**Claves:** número de capa como string (`"0"`, `"1"`, ..., `"12"`).

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

---

## Sistema de personalización de LEDs indicadores

El Geonix R2 tiene dos sistemas de LED independientes:

- **RGB Matrix:** efectos per-key configurables. Gestionado por el código generado del Moonlander. No entra en este sistema.
- **Indicadores de sistema** (librería `rdmctmzt_common`): LEDs de estado siempre activos con prioridad sobre el RGB Matrix. **Este sistema es el que configura `led_config.json`.**

### Activación

En `mapping.json`:
```json
"hasToOverrideLedConfig": true
```

### Fichero de configuración: `led_config/led_config.json`

#### Formato de posición

Todas las posiciones se especifican como coordenadas **visuales** `[fila, col]` (0-indexed):

- **Fila 0** = fila superior visual (la que el usuario ve arriba)
- **Fila 3** = fila inferior visual
- **Col 0** = columna más a la izquierda visual
- **Col 11** = columna más a la derecha visual

El script aplica `invert_layout` automáticamente. Con `invert_layout: true`, la posición visual `[0][0]` corresponde al LED hardware 46 (esquina superior-derecha del PCB).

> **Nota:** La posición visual `[0,6]` con `invert_layout=true` (o `[3,5]` con `invert_layout=false`) resulta en NO_LED (hueco del spacebar) y se descarta silenciosamente.

#### Referencia de posiciones con `invert_layout: true`

```
Visual [0][0..11] → hw [3][11..0]  (fila superior visual = fila inferior hardware)
Visual [1][0..11] → hw [2][11..0]
Visual [2][0..11] → hw [1][11..0]
Visual [3][0..11] → hw [0][11..0]  (fila inferior visual = fila superior hardware)
```

Con el layout actual (capa 12), las posiciones visuales de los keycodes de conexión son:

| Visual | LED idx | Keycode capa 12 |
|---|---|---|
| [0][0] | 46 | MD_USB |
| [0][1] | 45 | MD_BLE1 |
| [0][2] | 44 | MD_BLE2 |
| [0][3] | 43 | MD_BLE3 |
| [0][4] | 42 | MD_24G |

#### Estructura de `led_config.json`

```json
{
  "connection_leds": {
    "_comment": "Indicadores de modo de conexión y capas Fn.",

    "indicator_layers": {
      "_comment": "Capas MO(N) que muestran el modo activo mientras se mantienen.",
      "layers": [12]
    },

    "usb":  { "pos": [0, 0] },
    "ble1": { "pos": [0, 1], "name": "Geonix rev.2-1" },
    "ble2": { "pos": [0, 2], "name": "Geonix rev.2-2" },
    "ble3": { "pos": [0, 3], "name": "Geonix rev.2-3" },
    "g24":  { "pos": [0, 4] }
  },

  "caps_lock_led": {
    "_comment": "LED que se ilumina en blanco cuando Caps Lock está activo.",
    "pos": [1, 0]
  },

  "win_lock_led": {
    "_comment": "LED que se ilumina en blanco cuando Win Lock está activo.",
    "pos": [2, 0]
  },

  "battery_low_led": {
    "_comment": "LED que parpadea en rojo cuando la batería está críticamente baja.",
    "pos": [3, 11]
  },

  "battery_bar": {
    "_comment": "LEDs para QK_BAT. Orden del array = orden de llenado.",
    "low_threshold": 20,
    "med_threshold": 50,
    "leds": [
      [3,0],[2,0],[1,0],[0,0], [3,1],[2,1],[1,1],[0,1],
      [3,2],[2,2],[1,2],[0,2], [3,3],[2,3],[1,3],[0,3],
      [3,4],[2,4],[1,4],[0,4], [3,5],[2,5],[1,5],[0,5],
      [3,6],[2,6],[1,6],[0,6], [3,7],[2,7],[1,7],[0,7],
      [3,8],[2,8],[1,8],[0,8], [3,9],[2,9],[1,9],[0,9],
      [3,10],[2,10],[1,10],[0,10], [3,11],[2,11],[1,11],[0,11]
    ]
  }
}
```

#### Campos configurables

| Campo | Descripción |
|---|---|
| `connection_leds.usb/ble1/ble2/ble3/g24.pos` | Posición visual del LED de cada modo |
| `connection_leds.ble1/ble2/ble3.name` | Nombre del perfil BT (se envía al módulo BLE) |
| `connection_leds.indicator_layers.layers` | Capas `MO(N)` que activan el indicador Fn |
| `caps_lock_led.pos` | Posición visual del LED de Caps Lock |
| `win_lock_led.pos` | Posición visual del LED de Win Lock |
| `battery_low_led.pos` | Posición visual del LED de batería crítica |
| `battery_bar.leds` | Array de posiciones visuales para la barra de batería (QK_BAT) |
| `battery_bar.low_threshold` | Porcentaje por debajo del cual la barra es roja (default: 20) |
| `battery_bar.med_threshold` | Porcentaje por debajo del cual la barra es amarilla (default: 50) |

#### Lo que `led_config_gen.py` genera

El script produce `keymaps/zsa-moonlander/led_indicators.h` con:
- `#undef` + `#define` para sobreescribir los `LED_*_INDEX` por defecto del teclado
- `#define USER_BLE*_NAME` con los nombres de los perfiles BLE
- `#define BATTERY_LED_COUNT`, `BATTERY_LED_ARRAY`, `BATTERY_LOW/MED_THRESHOLD`
- `#define FN_LAYER_COUNT` — número de capas Fn configuradas

Y en `keymap.c` inyecta:
```c
const uint8_t FN_LAYERS[FN_LAYER_COUNT] = {12};
```

#### Indicadores de sistema que NO se configuran aquí

Los siguientes comportamientos son fijos en la librería `rdmctmzt_common` y no se modifican:

- Colores de los indicadores (azul para BT, verde para 2.4G, blanco para USB)
- Animaciones de parpadeo al emparejar o reconectar
- Feedback visual de reset EEPROM (`EE_CLR`)
- Modo test de colores (`TEST_CL`)
- Feedback de límites de brillo/velocidad RGB
- Feedback de NKRO y Mac/Win mode
- USB Auto-Switch (flash 1s al enchufar USB)
