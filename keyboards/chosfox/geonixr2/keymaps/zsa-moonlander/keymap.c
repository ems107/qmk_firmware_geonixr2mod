#include QMK_KEYBOARD_H
#include "rdmctmzt_common.h"
#include "i18n.h"

enum custom_keycodes {
    ST_MACRO_0 = SAFE_RANGE,
    ST_MACRO_1,
    ST_MACRO_2,
    ST_MACRO_3,
    ST_MACRO_4,
    ST_MACRO_5,
    ST_MACRO_6,
    ST_MACRO_7,
    ST_MACRO_8,
    ST_MACRO_9,
    ST_MACRO_10,
    ST_MACRO_11,
    ST_MACRO_12,
    ST_MACRO_13,
    ST_MACRO_14,
};

enum tap_dance_codes {
  DANCE_0,
  DANCE_1,
};

#define DUAL_FUNC_0 LT(14, KC_D)

// clang-format off
const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [0] = LAYOUT_tkl_ansi(
        KC_TRNS,  KC_RIGHT, KC_LEFT,  MO(5),       KC_LEFT_SHIFT, MO(2),        MO(6),              KC_SPACE, MO(4), KC_UP,       KC_DOWN, KC_TRNS,
        KC_ENTER, KC_DOT,   KC_COMMA, KC_H,        KC_K,          LGUI(KC_TAB), LALT(LCTL(KC_TAB)), KC_V,     KC_D,  TD(DANCE_0), KC_X,    KC_Z,
        KC_O,     KC_I,     KC_E,     TD(DANCE_1), KC_M,          MO(8),        MO(7),              KC_G,     KC_T,  KC_S,        KC_R,    KC_A,
        KC_BSPC,  KC_Y,     KC_U,     KC_L,        KC_J,                        KC_TRNS,            KC_B,     KC_P,  KC_F,        KC_W,    KC_Q
    ),
    [1] = LAYOUT_tkl_ansi(
        KC_TRNS,    KC_TRNS,    KC_TRNS,    KC_TRANSPARENT, LT(3, KC_SPACE), ES_TILD,        KC_TRANSPARENT, KC_SPACE,   KC_TRANSPARENT, KC_TRNS,    KC_TRNS,    KC_TRNS,
        ES_UNDS,    ES_COLN,    ES_SCLN,    LSFT(KC_H),     LSFT(KC_K),      KC_TRANSPARENT, KC_TRANSPARENT, LSFT(KC_V), LSFT(KC_D),     LSFT(KC_C), LSFT(KC_X), LSFT(KC_Z),
        LSFT(KC_O), LSFT(KC_I), LSFT(KC_E), LSFT(KC_N),     LSFT(KC_M),      DUAL_FUNC_0,    KC_TRANSPARENT, LSFT(KC_G), LSFT(KC_T),     LSFT(KC_S), LSFT(KC_R), LSFT(KC_A),
        ES_DQUO,    LSFT(KC_Y), LSFT(KC_U), LSFT(KC_L),     LSFT(KC_J),                      KC_TRNS,        LSFT(KC_B), LSFT(KC_P),     LSFT(KC_F), LSFT(KC_W), LSFT(KC_Q)
    ),
    [2] = LAYOUT_tkl_ansi(
        KC_TRNS, KC_TRNS,    KC_TRNS, KC_NO,   KC_NO,   KC_NO, KC_NO,   KC_TRANSPARENT, KC_NO,   KC_TRNS, KC_TRNS, KC_TRNS,
        ES_QUES, LSFT(KC_1), ES_GRTR, ES_DQUO, ES_PIPE, KC_NO, KC_NO,   ES_AMPR,        ES_RCBR, ES_RPRN, ES_RBRC, ES_SLSH,
        KC_0,    KC_9,       KC_8,    KC_7,    KC_6,    KC_NO, KC_NO,   KC_5,           KC_4,    KC_3,    KC_2,    KC_1,
        ES_IQUE, ES_IEXL,    ES_LESS, ES_APOS, ES_EQL,         KC_TRNS, ES_HASH,        ES_LCBR, ES_LPRN, ES_LBRC, LALT(LCTL(ES_OVRR))
    ),
    [3] = LAYOUT_tkl_ansi(
        KC_TRNS,     KC_TRNS,     KC_TRNS,     KC_TRANSPARENT,   KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRNS,    KC_TRNS, KC_TRNS,
        ST_MACRO_14, ST_MACRO_13, LSFT(KC_4),  LALT(LCTL(KC_E)), KC_NO,          KC_TRANSPARENT, KC_TRANSPARENT, ES_NOT,         ES_PIPE,        ST_MACRO_3, ES_OVDT, ST_MACRO_2,
        ST_MACRO_12, ST_MACRO_11, ST_MACRO_10, ST_MACRO_9,       ST_MACRO_8,     KC_TRANSPARENT, KC_TRANSPARENT, ES_AT,          ES_AMPR,        ES_EQL,     ES_PLUS, ST_MACRO_1,
        ES_OVRR,     ST_MACRO_7,  ST_MACRO_6,  ST_MACRO_5,       ST_MACRO_4,                     KC_TRNS,        ST_MACRO_0,     LSFT(KC_5),     ES_HASH,    ES_ASTR, LSFT(ES_OVRR)
    ),
    [4] = LAYOUT_tkl_ansi(
        KC_TRNS,        KC_TRNS,        KC_TRNS,        KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRNS,     KC_TRNS,     KC_TRNS,
        KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_F5,          KC_F4,          KC_F3,       KC_F2,       KC_F1,
        KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_F11,         KC_LEFT_SHIFT,  KC_LEFT_ALT, KC_LEFT_GUI, KC_LEFT_CTRL,
        KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                 KC_TRNS,        KC_TRANSPARENT, MS_BTN1,        MS_BTN3,     MS_BTN2,     KC_LEFT_SHIFT
    ),
    [5] = LAYOUT_tkl_ansi(
        KC_TRNS,        KC_TRNS,       KC_TRNS,     KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRNS,        KC_TRNS,        KC_TRNS,
        KC_F10,         KC_F9,         KC_F8,       KC_F7,          KC_F6,          KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
        KC_LEFT_CTRL,   KC_LEFT_GUI,   KC_LEFT_ALT, KC_LEFT_SHIFT,  KC_F12,         KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
        KC_TRANSPARENT, LSFT(ES_ACUT), ES_GRV,      ES_ACUT,        ES_CIRC,                        KC_TRNS,        KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT
    ),
    [6] = LAYOUT_tkl_ansi(
        KC_TRNS,  KC_TRNS,  KC_TRNS, KC_NO,   KC_WWW_FORWARD, KC_WWW_BACK, KC_NO,   KC_NO,         KC_NO,         KC_TRNS,     KC_TRNS,     KC_TRNS,
        KC_ENTER, ES_PLUS,  KC_NO,   ES_MINS, KC_NO,          KC_NO,       KC_NO,   KC_NO,         KC_NO,         KC_NO,       KC_NO,       KC_NO,
        KC_TAB,   KC_RIGHT, KC_DOWN, KC_LEFT, KC_INSERT,      KC_NO,       KC_NO,   KC_LEFT_SHIFT, KC_LEFT_SHIFT, KC_LEFT_ALT, KC_LEFT_GUI, KC_LEFT_CTRL,
        KC_BSPC,  KC_END,   KC_UP,   KC_HOME, KC_DELETE,                   KC_TRNS, KC_NO,         KC_NO,         KC_NO,       KC_NO,       KC_ESCAPE
    ),
    [7] = LAYOUT_tkl_ansi(
        KC_TRNS,        KC_TRNS,        KC_TRNS,        KC_WWW_BACK,    KC_WWW_FORWARD, KC_WWW_BACK,    KC_TRANSPARENT, KC_WWW_BACK,    KC_WWW_FORWARD, KC_TRNS,        KC_TRNS,        KC_TRNS,
        KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, MS_BTN3,        KC_TRANSPARENT, KC_TRANSPARENT, MS_ACL2,        MS_ACL1,        MS_ACL0,        KC_TRANSPARENT,
        KC_F21,         MS_WHLR,        MS_WHLD,        MS_WHLL,        KC_F20,         KC_WWW_FORWARD, KC_TRANSPARENT, KC_TRANSPARENT, MS_BTN1,        MS_BTN3,        MS_BTN2,        KC_TRANSPARENT,
        KC_F19,         KC_F24,         MS_WHLU,        KC_F23,         KC_F18,                         KC_TRNS,        KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT
    ),
    [8] = LAYOUT_tkl_ansi(
        KC_TRNS,        KC_TRNS,             KC_TRNS,             KC_TRANSPARENT,      KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRNS, KC_TRNS, KC_TRNS,
        KC_TRANSPARENT, KC_TRANSPARENT,      KC_TRANSPARENT,      KC_TRANSPARENT,      KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_NO,          KC_NO,          RM_TOGG, KC_NO,   RM_NEXT,
        KC_TRANSPARENT, KC_AUDIO_VOL_UP,     KC_MEDIA_PLAY_PAUSE, KC_AUDIO_VOL_DOWN,   KC_AUDIO_MUTE,  KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, RM_SPDU,        RM_VALU, RM_HUEU, RM_SATU,
        KC_TRANSPARENT, KC_MEDIA_NEXT_TRACK, KC_MEDIA_STOP,       KC_MEDIA_PREV_TRACK, KC_TRANSPARENT,                 KC_TRNS,        KC_TRANSPARENT, RM_SPDD,        RM_VALD, RM_HUED, RM_SATD
    ),
    [9] = LAYOUT_tkl_ansi(
        KC_TRNS,      KC_TRNS,      KC_TRNS,      KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRNS,      KC_TRNS,      KC_TRNS,
        LALT(KC_F23), LALT(KC_F22), LALT(KC_F21), LALT(KC_F20),   LALT(KC_F19),   KC_TRANSPARENT, KC_TRANSPARENT, LALT(KC_F18),   LALT(KC_F17),   LALT(KC_F16), LALT(KC_F15), LALT(KC_F14),
        LCTL(KC_F23), LCTL(KC_F22), LCTL(KC_F21), LCTL(KC_F20),   LCTL(KC_F19),   KC_TRANSPARENT, KC_TRANSPARENT, LCTL(KC_F18),   LCTL(KC_F17),   LCTL(KC_F16), LCTL(KC_F15), LCTL(KC_F14),
        LSFT(KC_F23), LSFT(KC_F22), LSFT(KC_F21), LSFT(KC_F20),   LSFT(KC_F19),                   KC_TRNS,        LSFT(KC_F18),   LSFT(KC_F17),   LSFT(KC_F16), LSFT(KC_F15), LSFT(KC_F14)
    ),
    [10] = LAYOUT_tkl_ansi(
        KC_TRNS, KC_TRNS, KC_TRNS, MS_BTN4, MS_BTN1, MS_ACL2, KC_F16,  KC_SPACE, KC_LEFT_ALT, KC_TRNS, KC_TRNS, KC_TRNS,
        KC_NO,   KC_NO,   KC_NO,   KC_NO,   MS_ACL1, MS_BTN3, KC_F18,  KC_V,     KC_C,        KC_X,    KC_F20,  KC_LEFT_CTRL,
        MS_ACL0, MS_RGHT, MS_DOWN, MS_LEFT, TO(11),  KC_NO,   KC_F17,  KC_F,     KC_D,        KC_S,    KC_A,    KC_LEFT_SHIFT,
        KC_NO,   MS_WHLU, MS_UP,   MS_WHLD, KC_NO,            KC_TRNS, KC_R,     KC_E,        KC_W,    KC_Q,    KC_TAB
    ),
    [11] = LAYOUT_tkl_ansi(
        KC_TRNS, KC_TRNS, KC_TRNS, KC_NO, KC_Z,  KC_X,  KC_NO,   KC_W,  KC_NO, KC_TRNS, KC_TRNS, KC_TRNS,
        KC_H,    KC_L,    KC_K,    KC_J,  KC_NO, KC_NO, KC_NO,   KC_NO, KC_NO, KC_NO,   KC_NO,   KC_NO,
        KC_Y,    KC_O,    KC_I,    KC_U,  KC_NO, KC_C,  KC_NO,   KC_NO, KC_D,  KC_S,    KC_A,    KC_NO,
        KC_NO,   KC_NO,   KC_NO,   KC_NO, KC_NO,        KC_TRNS, KC_NO, KC_NO, KC_W,    KC_NO,   KC_NO
    )
};
// clang-format on

typedef struct {
    bool is_press_action;
    uint8_t step;
} tap;

enum {
    SINGLE_TAP = 1,
    SINGLE_HOLD,
    DOUBLE_TAP,
    DOUBLE_HOLD,
    DOUBLE_SINGLE_TAP,
    MORE_TAPS
};

static tap dance_state[2];

uint8_t dance_step(tap_dance_state_t *state);

uint8_t dance_step(tap_dance_state_t *state) {
    if (state->count == 1) {
        if (state->interrupted || !state->pressed) return SINGLE_TAP;
        else return SINGLE_HOLD;
    } else if (state->count == 2) {
        if (state->interrupted) return DOUBLE_SINGLE_TAP;
        else if (state->pressed) return DOUBLE_HOLD;
        else return DOUBLE_TAP;
    }
    return MORE_TAPS;
}


void on_dance_0(tap_dance_state_t *state, void *user_data);
void dance_0_finished(tap_dance_state_t *state, void *user_data);
void dance_0_reset(tap_dance_state_t *state, void *user_data);

void on_dance_0(tap_dance_state_t *state, void *user_data) {
    if(state->count == 3) {
        tap_code16(KC_C);
        tap_code16(KC_C);
        tap_code16(KC_C);
    }
    if(state->count > 3) {
        tap_code16(KC_C);
    }
}

void dance_0_finished(tap_dance_state_t *state, void *user_data) {
    dance_state[0].step = dance_step(state);
    switch (dance_state[0].step) {
        case SINGLE_TAP: register_code16(KC_C); break;
        case DOUBLE_TAP: register_code16(KC_C); register_code16(KC_C); break;
        case DOUBLE_HOLD: register_code16(ES_CCED); break;
        case DOUBLE_SINGLE_TAP: tap_code16(KC_C); register_code16(KC_C);
    }
}

void dance_0_reset(tap_dance_state_t *state, void *user_data) {
    wait_ms(10);
    switch (dance_state[0].step) {
        case SINGLE_TAP: unregister_code16(KC_C); break;
        case DOUBLE_TAP: unregister_code16(KC_C); break;
        case DOUBLE_HOLD: unregister_code16(ES_CCED); break;
        case DOUBLE_SINGLE_TAP: unregister_code16(KC_C); break;
    }
    dance_state[0].step = 0;
}
void on_dance_1(tap_dance_state_t *state, void *user_data);
void dance_1_finished(tap_dance_state_t *state, void *user_data);
void dance_1_reset(tap_dance_state_t *state, void *user_data);

void on_dance_1(tap_dance_state_t *state, void *user_data) {
    if(state->count == 3) {
        tap_code16(KC_N);
        tap_code16(KC_N);
        tap_code16(KC_N);
    }
    if(state->count > 3) {
        tap_code16(KC_N);
    }
}

void dance_1_finished(tap_dance_state_t *state, void *user_data) {
    dance_state[1].step = dance_step(state);
    switch (dance_state[1].step) {
        case SINGLE_TAP: register_code16(KC_N); break;
        case DOUBLE_TAP: register_code16(KC_N); register_code16(KC_N); break;
        case DOUBLE_HOLD: register_code16(ES_NTIL); break;
        case DOUBLE_SINGLE_TAP: tap_code16(KC_N); register_code16(KC_N);
    }
}

void dance_1_reset(tap_dance_state_t *state, void *user_data) {
    wait_ms(10);
    switch (dance_state[1].step) {
        case SINGLE_TAP: unregister_code16(KC_N); break;
        case DOUBLE_TAP: unregister_code16(KC_N); break;
        case DOUBLE_HOLD: unregister_code16(ES_NTIL); break;
        case DOUBLE_SINGLE_TAP: unregister_code16(KC_N); break;
    }
    dance_state[1].step = 0;
}

tap_dance_action_t tap_dance_actions[] = {
        [DANCE_0] = ACTION_TAP_DANCE_FN_ADVANCED(on_dance_0, dance_0_finished, dance_0_reset),
        [DANCE_1] = ACTION_TAP_DANCE_FN_ADVANCED(on_dance_1, dance_1_finished, dance_1_reset),
};

bool process_record_user(uint16_t keycode, keyrecord_t *record) {

  switch (keycode) {
  case QK_MODS ... QK_MODS_MAX: 
    // Mouse keys with modifiers work inconsistently across operating systems, this makes sure that modifiers are always
    // applied to the mouse key that was pressed.
    if (IS_MOUSE_KEYCODE(QK_MODS_GET_BASIC_KEYCODE(keycode))) {
    if (record->event.pressed) {
        add_mods(QK_MODS_GET_MODS(keycode));
        send_keyboard_report();
        wait_ms(2);
        register_code(QK_MODS_GET_BASIC_KEYCODE(keycode));
        return false;
      } else {
        wait_ms(2);
        del_mods(QK_MODS_GET_MODS(keycode));
      }
    }
    break;
    case ST_MACRO_0:
    if (record->event.pressed) {
      SEND_STRING(SS_LALT(SS_TAP(X_KP_2) SS_TAP(X_KP_4) SS_TAP(X_KP_7) ));
    }
    break;
    case ST_MACRO_1:
    if (record->event.pressed) {
      SEND_STRING(SS_LALT(SS_TAP(X_KP_1) SS_TAP(X_KP_4) SS_TAP(X_KP_5) ));
    }
    break;
    case ST_MACRO_2:
    if (record->event.pressed) {
      SEND_STRING(SS_LALT(SS_TAP(X_KP_1) SS_TAP(X_KP_4) SS_TAP(X_KP_6) ));
    }
    break;
    case ST_MACRO_3:
    if (record->event.pressed) {
      SEND_STRING(SS_LALT(SS_TAP(X_KP_0) SS_TAP(X_KP_1) SS_TAP(X_KP_5) SS_TAP(X_KP_1) ));
    }
    break;
    case ST_MACRO_4:
    if (record->event.pressed) {
      SEND_STRING(SS_LALT(SS_TAP(X_KP_2) SS_TAP(X_KP_4) SS_TAP(X_KP_0) ));
    }
    break;
    case ST_MACRO_5:
    if (record->event.pressed) {
      SEND_STRING(SS_LALT(SS_TAP(X_KP_0) SS_TAP(X_KP_1) SS_TAP(X_KP_7) SS_TAP(X_KP_8) ));
    }
    break;
    case ST_MACRO_6:
    if (record->event.pressed) {
      SEND_STRING(SS_LALT(SS_TAP(X_KP_2) SS_TAP(X_KP_4) ));
    }
    break;
    case ST_MACRO_7:
    if (record->event.pressed) {
      SEND_STRING(SS_LALT(SS_TAP(X_KP_0) SS_TAP(X_KP_1) SS_TAP(X_KP_7) SS_TAP(X_KP_9) ));
    }
    break;
    case ST_MACRO_8:
    if (record->event.pressed) {
      SEND_STRING(SS_LALT(SS_TAP(X_KP_2) SS_TAP(X_KP_4) SS_TAP(X_KP_1) ));
    }
    break;
    case ST_MACRO_9:
    if (record->event.pressed) {
      SEND_STRING(SS_LALT(SS_TAP(X_KP_2) SS_TAP(X_KP_6) ));
    }
    break;
    case ST_MACRO_10:
    if (record->event.pressed) {
      SEND_STRING(SS_LALT(SS_TAP(X_KP_2) SS_TAP(X_KP_5) ));
    }
    break;
    case ST_MACRO_11:
    if (record->event.pressed) {
      SEND_STRING(SS_LALT(SS_TAP(X_KP_2) SS_TAP(X_KP_7) ));
    }
    break;
    case ST_MACRO_12:
    if (record->event.pressed) {
      SEND_STRING(SS_LALT(SS_TAP(X_KP_0) SS_TAP(X_KP_1) SS_TAP(X_KP_5) SS_TAP(X_KP_6) ));
    }
    break;
    case ST_MACRO_13:
    if (record->event.pressed) {
      SEND_STRING(SS_LALT(SS_TAP(X_KP_0) SS_TAP(X_KP_1) SS_TAP(X_KP_6) SS_TAP(X_KP_3) ));
    }
    break;
    case ST_MACRO_14:
    if (record->event.pressed) {
      SEND_STRING(SS_LALT(SS_TAP(X_KP_0) SS_TAP(X_KP_1) SS_TAP(X_KP_4) SS_TAP(X_KP_0) ));
    }
    break;

    case DUAL_FUNC_0:
      if (record->tap.count > 0) {
        if (record->event.pressed) {
          register_code16(ES_CCED);
        } else {
          unregister_code16(ES_CCED);
        }
      } else {
        if (record->event.pressed) {
          register_code16(LSFT(ES_CCED));
        } else {
          unregister_code16(LSFT(ES_CCED));
        }  
      }  
      return false;
  }
  return true;
}

const uint8_t PROGMEM ledmap[][RGB_MATRIX_LED_COUNT][3] = {
    [10] = { {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,255}, {0,0,0}, {0,245,245}, {0,0,0}, {0,0,255}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,255}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,255}, {74,255,255}, {0,0,0}, {74,255,255}, {0,0,0}, {0,0,0}, {0,0,0}, {219,255,255}, {0,0,0}, {0,0,0}, {0,0,255}, {0,0,0}, {0,0,0}, {219,255,255}, {0,0,255}, {25,255,255}, {0,0,255}, {131,255,255}, {25,255,255}, {219,255,255}, {131,255,255}, {219,255,255}, {74,255,255}, {131,255,255}, {0,0,255}, {0,0,0}, {25,255,255}, {131,255,255}, {0,0,255}, {0,0,255}, {219,255,255} },
    [11] = { {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,245,245}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,245,245}, {0,245,245}, {0,0,0}, {0,245,245}, {0,0,0}, {0,0,0}, {0,0,0}, {0,245,245}, {0,245,245}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,245,245}, {0,0,0}, {0,245,245}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,245,245}, {0,0,0}, {0,0,0}, {0,0,0}, {0,245,245}, {0,245,245}, {0,0,0} },
};

extern rgb_config_t rgb_matrix_config;

RGB hsv_to_rgb_with_value(HSV hsv) {
  RGB rgb = hsv_to_rgb( hsv );
  float f = (float)rgb_matrix_config.hsv.v / UINT8_MAX;
  return (RGB){ f * rgb.r, f * rgb.g, f * rgb.b };
}

void keyboard_post_init_user(void) {
  rgb_matrix_enable();
}

void set_layer_color(int layer) {
  for (int i = 0; i < RGB_MATRIX_LED_COUNT; i++) {
    HSV hsv = {
      .h = pgm_read_byte(&ledmap[layer][i][0]),
      .s = pgm_read_byte(&ledmap[layer][i][1]),
      .v = pgm_read_byte(&ledmap[layer][i][2]),
    };
    if (!hsv.h && !hsv.s && !hsv.v) {
        rgb_matrix_set_color( i, 0, 0, 0 );
    } else {
        RGB rgb = hsv_to_rgb_with_value(hsv);
        rgb_matrix_set_color(i, rgb.r, rgb.g, rgb.b);
    }
  }
}

bool rgb_matrix_indicators_user(void) {
  switch (biton32(layer_state)) {
    case 10:
      set_layer_color(10);
      break;
    case 11:
      set_layer_color(11);
      break;
    default:
      if (rgb_matrix_get_flags() == LED_FLAG_NONE) {
        rgb_matrix_set_color_all(0, 0, 0);
      }
  }
  return true;
}
