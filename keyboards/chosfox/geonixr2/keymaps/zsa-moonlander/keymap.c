#include QMK_KEYBOARD_H
#include "rdmctmzt_common.h"
#include "i18n.h"

// clang-format off
const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [0] = LAYOUT_tkl_ansi(
        KC_TRNS,  KC_TRNS, KC_TRNS,  KC_TRNS, KC_LEFT_SHIFT, KC_TRNS, KC_TRNS, KC_SPACE, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS,
        KC_ENTER, KC_DOT,  KC_COMMA, KC_H,    KC_K,          KC_TRNS, KC_TRNS, KC_V,     KC_D,    KC_TRNS, KC_X,    KC_Z,
        KC_O,     KC_I,    KC_E,     KC_TRNS, KC_M,          KC_TRNS, KC_TRNS, KC_G,     KC_T,    KC_S,    KC_R,    KC_A,
        KC_BSPC,  KC_Y,    KC_U,     KC_L,    KC_J,                   KC_TRNS, KC_B,     KC_P,    KC_F,    KC_W,    KC_Q
    )
};
// clang-format on
