// Compare expansion-pad D1 reads with normal controller D0 input and the microphone bit.
// KUROSAKI currently supplies only D0: D1 and microphone values stay zero there.
// Nonzero expansion/microphone behavior requires suitable hardware or another emulator.
#include "fc_common.h"
#include "fc.h"
u8 pad1;
u8 pad2;
u8 d1_first;
u8 d1_second;
u8 expansion_first;
u8 expansion_second;
u8 voice;
u8 mic_direct;
void show(u8 row,const u8* label,u8 value) {
    m_text(1,row,label);
    m_put(16,row,(u8)('0'+value/100));
    m_put(17,row,(u8)('0'+(value/10)%10));
    m_put(18,row,(u8)('0'+value%10));
    m_wait();
}
void main(void) {
    m_init();
    m_text(1,0,"EXPANSION INPUT"); m_wait();
    m_text(1,2,"P1 A AND P2 B"); m_wait();
    pad1=0; pad2=0;
    while (pad1!=1 || pad2!=2) {
        pad1=__pad_read1_safe(); pad2=__pad_read2_safe(); m_wait();
    }
    // The normal controllers above occupy D0. These next calls read D1 instead.
    // example:__pad_read1_d1:start
    d1_first=__pad_read1_d1();
    // example:__pad_read1_d1:end
    // example:__pad_read2_d1:start
    d1_second=__pad_read2_d1();
    // example:__pad_read2_d1:end
    // example:__exp_pad_read1:start
    expansion_first=__exp_pad_read1(); // Same helper as __pad_read1_d1.
    // example:__exp_pad_read1:end
    // example:__exp_pad_read2:start
    expansion_second=__exp_pad_read2(); // Same helper as __pad_read2_d1.
    // example:__exp_pad_read2:end
    // This is a digital level from $4016 bit 2, not audio samples or voice recognition.
    // example:__joypad2p_voice:start
    voice=__joypad2p_voice();
    // example:__joypad2p_voice:end
    // example:__mic_read2p:start
    mic_direct=__mic_read2p(); // A separate sample of the same digital signal.
    // example:__mic_read2p:end
    show(4,"NORMAL P1",pad1); show(5,"NORMAL P2",pad2);
    show(7,"D1 PORT 1",d1_first); show(8,"D1 PORT 2",d1_second);
    show(9,"EXP ALIAS 1",expansion_first); show(10,"EXP ALIAS 2",expansion_second);
    show(12,"MIC LEVEL",voice);
    show(13,"MIC DIRECT",mic_direct);
    m_text(1,14,"SIGNAL SNAPSHOT"); m_wait();
    while (1) m_wait();
}
