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

#include "pad.h"
#include "input_repeat.h"
u16 held_ticks;
u16 pulse_count;
u16 previous_pulse;
u16 expected_pulses;
u8 first_held;
u8 first_trigger;
u8 first_repeat;
u8 release_bits;
u8 failures;
void main(void) {
    m_init(); failures=0; held_ticks=0; pulse_count=0; previous_pulse=0;
    m_text(1,0,"NES PAD REPEAT"); m_wait();
    m_text(1,2,"HOLD B THEN RELEASE"); m_wait();
    nes_pad1_cur=0; nes_pad1_prev=0; nes_pad1_pressed=0; nes_pad1_released=0;
    // example:nes_pad_repeat_config:start
    nes_pad_repeat_config(3,1); // Next pulse after 4 held updates, then every 2.
    // example:nes_pad_repeat_config:end
    while (1) {
        // example:nes_pad_poll:start
        nes_pad_poll(); // Read controller 1 and update its held/pressed/released snapshots.
        // example:nes_pad_poll:end
        // example:nes_pad_repeat_step:start
        nes_pad_repeat_step(); // Once after each fresh poll; getters do not advance time.
        // example:nes_pad_repeat_step:end
        // example:nes_pad_held:start
        if (nes_pad_held(0x02)!=0) held_ticks++; // B is bit 1 in NES raw format.
        // example:nes_pad_held:end
        // example:nes_pad_trigger:start
        if (nes_pad_trigger(0x02)!=0) {
            first_trigger=nes_pad_trigger(0x02); // Returns 2, not Boolean 1.
            first_held=nes_pad_held(0x02); first_repeat=nes_pad_repeat(0x02);
            if (first_trigger!=2 || first_held!=2 || first_repeat!=2) failures++;
        }
        // example:nes_pad_trigger:end
        // example:nes_pad_repeat:start
        if (nes_pad_repeat(0x02)!=0) {
            if (pulse_count==1 && held_ticks-previous_pulse!=4) failures++;
            if (pulse_count>1 && held_ticks-previous_pulse!=2) failures++;
            previous_pulse=held_ticks; pulse_count++;
            if (nes_pad_repeat(0x02)!=2) failures++; // Querying again preserves the pulse.
        }
        // example:nes_pad_repeat:end
        // example:nes_pad_release:start
        if (nes_pad_release(0x02)!=0) {
            release_bits=nes_pad_release(0x02); // Returns the released B bit, 2.
            if (nes_pad_held(0x02)!=0 || nes_pad_trigger(0x02)!=0 || nes_pad_repeat(0x02)!=0) failures++;
            break;
        }
        // example:nes_pad_release:end
        m_wait();
    }
    expected_pulses=1;
    if (held_ticks>=5) expected_pulses=2+(held_ticks-5)/2;
    if (pulse_count!=expected_pulses || release_bits!=2) failures++;
    if (nes_pad_held(0)!=0 || nes_pad_trigger(0)!=0 || nes_pad_release(0)!=0 || nes_pad_repeat(0)!=0) failures++;
    m_wait(); nes_pad_poll(); nes_pad_repeat_step();
    if (nes_pad_release(2)!=0 || nes_pad_repeat(2)!=0) failures++;
    show_value(2,"FIRST HELD",first_held); show_value(3,"FIRST TRIGGER",first_trigger);
    show_value(4,"FIRST REPEAT",first_repeat); show_value(6,"HELD TICKS",held_ticks);
    show_value(7,"PULSE COUNT",pulse_count); show_value(9,"RELEASE BITS",release_bits);
    show_value(13,"FAILED CHECKS",failures);
    while (1) m_wait();
}
