"""Write complete input teaching programs with explicit interaction and result checks."""
from pathlib import Path

SITE=Path(__file__).resolve().parents[2]
display=r'''
// Labels make each observed count meaningful; queue one row per frame on FC.
void show_value(u8 row, const u8* label, u16 value) {
    m_text(1,row,"                   "); m_wait();
    m_text(1,row,label);
    m_put(16,row,(u8)('0'+(value/100)%10));
    m_put(17,row,(u8)('0'+(value/10)%10));
    m_put(18,row,(u8)('0'+value%10));
    m_wait();
}
'''
logical=r'''
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
    DEMO_INIT
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
'''
gb_raw=r'''
// Raw hardware reads do not need the input library's cached state.
#define BTN_RIGHT 1
#define BTN_A 16
u16 __readpadex(u8 previous);
u8 __readpad(void);
u8 __readpaddir(void);
u8 __readpadbtn(void);
u16 packed_first;
u16 packed_held;
u8 all_keys;
u8 directions;
u8 buttons;
u8 current_keys;
u8 press_keys;
u8 failures;
void main(void) {
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
'''
fc_raw=r'''
#include "fc.h"
u8 raw1;
u8 raw2;
u8 safe1;
u8 safe2;
u8 buttons;
u8 directions;
u8 alias1;
u8 alias2;
u8 failures;
void main(void) {
    m_init(); failures=0;
    m_text(1,0,"FC RAW INPUT"); m_wait();
    m_text(1,2,"P1 A RIGHT"); m_wait();
    m_text(1,3,"P2 B LEFT"); m_wait();
    while (__pad_read1_safe()!=129 || __pad_read2_safe()!=66) m_wait();
    // These snapshots retain the NES serial-button bit order.
    // example:__pad_read1:start
    raw1=__pad_read1(); // Controller 1: A (1) | Right (128) = 129.
    // example:__pad_read1:end
    // example:__pad_read2:start
    raw2=__pad_read2(); // Controller 2: B (2) | Left (64) = 66.
    // example:__pad_read2:end
    // example:__pad_read1_safe:start
    safe1=__pad_read1_safe(); // Repeat paired controller-1 reads until they agree.
    // example:__pad_read1_safe:end
    // example:__pad_read2_safe:start
    safe2=__pad_read2_safe(); // The same consistency check on controller 2.
    // example:__pad_read2_safe:end
    // example:__pad_buttons:start
    buttons=__pad_buttons(raw1); // Low nibble of 129: 1, the A button.
    // example:__pad_buttons:end
    // example:__pad_dirs:start
    directions=__pad_dirs(raw1); // High nibble retained in place: 128, not 8.
    // example:__pad_dirs:end
    // example:nes_pad1:start
    alias1=nes_pad1(); // Macro for __pad_read1_safe(), using NES raw bits.
    // example:nes_pad1:end
    // example:nes_pad2:start
    alias2=nes_pad2(); // Macro for __pad_read2_safe(), using NES raw bits.
    // example:nes_pad2:end
    if (raw1!=129 || safe1!=129 || alias1!=129) failures++;
    if (raw2!=66 || safe2!=66 || alias2!=66) failures++;
    if (buttons!=1 || directions!=128) failures++;
    show_value(5,"RAW P1",raw1); show_value(6,"RAW P2",raw2);
    show_value(7,"SAFE P1",safe1); show_value(8,"SAFE P2",safe2);
    show_value(9,"BUTTONS P1",buttons); show_value(10,"DIRS P1",directions);
    show_value(11,"ALIAS P1",alias1); show_value(12,"ALIAS P2",alias2);
    show_value(14,"FAILED CHECKS",failures);
    while (1) m_wait();
}
'''
fc_repeat=r'''
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
'''

def write(platform,name,body):
    prefix='#include "'+('gb_tile_example.h' if platform=='gb' else 'fc_common.h')+'"\n'
    body=body.replace('DEMO_INIT','tile_example_begin(); M_LCDC=0x91;' if platform=='gb' else 'm_init();')
    if platform=='gb':body=body.replace('(void)','()')
    path=SITE/'samples/api-examples'/platform/(name+'.c')
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('// Interactive input example; see its manual entry for the input timeline and expected display.\n'+prefix+display+body,encoding='utf-8',newline='\n')

if __name__=='__main__':
    for platform in ['gb','fc']:write(platform,'input_edges',logical)
    write('gb','input_raw',gb_raw);write('fc','input_raw',fc_raw);write('fc','pad_repeat',fc_repeat)
    print('Five complete input examples written.')
