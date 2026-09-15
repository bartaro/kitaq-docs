#ifndef FC_SOUND_EXAMPLE_H
#define FC_SOUND_EXAMPLE_H
#include "fc_common.h"
#include "audio.c"
__location(0x0600) u8 sound_result[128];
void sound_wait(u8 frames) {
    while (frames != 0) { m_wait(); frames--; }
}
void sound_begin(const u8* title) {
    u8 i;
    m_init();
    for(i=0;i<128;i++) sound_result[i]=0;
    nes_apu_init();
    // Flush between rows so their combined text cannot overflow the tile queue.
    m_text(1,1,title); m_wait();
#ifdef SOUND_PORT_ONLY
    m_text(1,3,"EXTERNAL PORT DATA"); m_wait();
#else
    m_text(1,3,"LISTEN TO THE WAV"); m_wait();
#endif
    sound_wait(30);
}
void sound_end(void) {
    nes_apu_silence_all();
    sound_result[127]=0xA5;
    m_text(1,5,"SEQUENCE COMPLETE");
    while (1) { m_wait(); }
}
#endif
