// Interactive input example; see its manual entry for the input timeline and expected display.
#include "fc_common.h"

// Labels make each observed count meaningful; queue one row per frame on FC.
void show_value(u8 row, const u8* label, u16 value) {
    m_text(1,row,"                   "); m_wait();
    m_text(1,row,label);
    m_put(16,row,(u8)('0'+(value/100)%10));
    m_put(17,row,(u8)('0'+(value/10)%10));
    m_put(18,row,(u8)('0'+value%10));
    m_wait();
}

#include "input.h"
u16 held_ticks;
u16 repeat_count;
u16 previous_pulse;
u16 expected_repeats;
u8 press_count;
u8 first_down;
u8 first_press;
u8 first_repeat;
u8 first_current;
u8 first_previous;
u8 release_result;
u8 last_current;
u8 last_previous;
u8 seen_press;
u8 failures;

void main(void) {
    m_init();
    // Learn the difference between held state, a press edge, a release edge and repeat pulses.
    // Press only A, hold it, then release. The verifier holds it for 40 emulator frames.
    m_text(1,0,"INPUT EDGES"); m_wait();
    m_text(1,2,"HOLD A THEN RELEASE"); m_wait();
    held_ticks=0; repeat_count=0; previous_pulse=0; press_count=0; seen_press=0; failures=0;
    // example:input_init:start
    input_init();
    if (input_current()!=0 || input_previous()!=0) failures++;
    // example:input_init:end
    while (1) {
        // example:input_update:start
        input_update(); // One update per input tick, followed by any number of queries.
        // example:input_update:end
        // example:input_down:start
        if (input_down(BTN_A)!=0) held_ticks++;
        // example:input_down:end
        // example:input_pressed:start
        if (input_pressed(BTN_A)!=0) {
            press_count++; seen_press=1;
            first_down=input_down(BTN_A); first_press=input_pressed(BTN_A);
            first_repeat=input_repeat(BTN_A);
            // example:input_current:start
            first_current=input_current(); // Only A held: BTN_A, or decimal 16.
            // example:input_current:end
            // example:input_previous:start
            first_previous=input_previous(); // No buttons in the preceding sample: 0.
            // example:input_previous:end
            if (first_down!=1 || first_press!=1 || first_repeat!=1) failures++;
            if (first_current!=BTN_A || first_previous!=0) failures++;
            if (input_down(BTN_A|BTN_B)!=1 || input_down(0)!=0) failures++;
        }
        // example:input_pressed:end
        // example:input_repeat:start
        if (input_repeat(BTN_A)!=0) {
            // The initial press is pulse 1. Defaults then wait 19 updates, followed by 6.
            if (repeat_count==1 && held_ticks-previous_pulse!=19) failures++;
            if (repeat_count>1 && held_ticks-previous_pulse!=6) failures++;
            previous_pulse=held_ticks; repeat_count++;
            if (input_repeat(BTN_A)!=1) failures++; // Reading again does not consume it.
        }
        // example:input_repeat:end
        // example:input_released:start
        if (input_released(BTN_A)!=0) {
            release_result=input_released(BTN_A);
            last_current=input_current(); last_previous=input_previous();
            if (input_down(BTN_A)!=0 || input_pressed(BTN_A)!=0 || input_repeat(BTN_A)!=0) failures++;
            break;
        }
        // example:input_released:end
        m_wait();
    }
    expected_repeats=1;
    if (held_ticks>=20) expected_repeats=2+(held_ticks-20)/6;
    if (seen_press!=1 || press_count!=1 || repeat_count!=expected_repeats) failures++;
    if (release_result!=1 || last_current!=0 || last_previous!=BTN_A) failures++;
    // One more update clears the release edge; the saved observation remains available for display.
    m_wait(); input_update();
    if (input_released(BTN_A)!=0 || input_previous()!=0) failures++;
    show_value(2,"FIRST DOWN",first_down);
    show_value(3,"FIRST PRESS",first_press);
    show_value(4,"FIRST REPEAT",first_repeat);
    show_value(5,"FIRST CURRENT",first_current);
    show_value(6,"HELD TICKS",held_ticks);
    show_value(7,"PRESS COUNT",press_count);
    show_value(8,"REPEAT COUNT",repeat_count);
    show_value(9,"RELEASE",release_result);
    show_value(10,"LAST CURRENT",last_current);
    show_value(11,"LAST PREVIOUS",last_previous);
    show_value(13,"FAILED CHECKS",failures);
    while (1) m_wait();
}
