// Interactive input example; see its manual entry for the input timeline and expected display.
#include "gb_tile_example.h"

// Labels make each observed count meaningful; queue one row per frame on FC.
void show_value(u8 row, const u8* label, u16 value) {
    m_text(1,row,"                   "); m_wait();
    m_text(1,row,label);
    m_put(16,row,(u8)('0'+(value/100)%10));
    m_put(17,row,(u8)('0'+(value/10)%10));
    m_put(18,row,(u8)('0'+value%10));
    m_wait();
}

// Raw hardware reads do not need the input library's cached state.
#define BTN_RIGHT 1
#define BTN_A 16
u16 __readpadex(u8 previous);
u8 __readpad();
u8 __readpaddir();
u8 __readpadbtn();
u16 packed_first;
u16 packed_held;
u8 all_keys;
u8 directions;
u8 buttons;
u8 current_keys;
u8 press_keys;
u8 failures;
void main() {
    tile_example_begin(); M_LCDC=0x91; failures=0;
    m_text(1,0,"GB RAW INPUT"); m_wait();
    m_text(1,2,"HOLD A AND RIGHT"); m_wait();
    while (__readpad()!=(BTN_A|BTN_RIGHT)) m_wait();
    // Each intrinsic samples hardware; the button-only result uses a low nibble.
    // example:__readpad:start
    all_keys=__readpad(); // A + Right: 0x11, decimal 17.
    // example:__readpad:end
    // example:__readpaddir:start
    directions=__readpaddir(); // Right: 1. The held A button is not included.
    // example:__readpaddir:end
    // example:__readpadbtn:start
    buttons=__readpadbtn(); // A: 1, not BTN_A (16).
    // example:__readpadbtn:end
    // example:__readpadex:start
    packed_first=__readpadex(0); // First sample: current 0x11, new presses 0x11.
    current_keys=(u8)packed_first;
    press_keys=(u8)(packed_first>>8);
    packed_held=__readpadex(current_keys); // Held without a change: new presses are 0.
    // example:__readpadex:end
    if (all_keys!=17 || directions!=1 || buttons!=1) failures++;
    if (current_keys!=17 || press_keys!=17 || packed_held!=17) failures++;
    m_text(1,2,"SNAPSHOT CAPTURED"); m_wait();
    show_value(4,"ALL KEYS",all_keys); show_value(5,"DIRECTIONS",directions);
    show_value(6,"BUTTONS LOW",buttons); show_value(8,"EX CURRENT",current_keys);
    show_value(9,"EX NEW PRESS",press_keys); show_value(10,"HELD PRESS",(u8)(packed_held>>8));
    show_value(13,"FAILED CHECKS",failures);
    while (1) m_wait();
}
