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
