#pragma once
// Display support, original font and hardware declarations precede the driver.
#include "gb_common.h"
#include "audio_hwregs_gb.c"
#ifdef SOUND_VBLANK
#define AUDIO_EXCLUDE_LEGACY_MUSIC_SERVICE
#define AUDIO_VBLANK_SFX_RESTORE
#include "audio_vblank.h"
__hram u8 Audio_NoiseEffectActive;
#endif
#include "audio.c"
#ifdef SOUND_VBLANK
#include "audio_vblank.c"
#endif
#pragma bank 0
__location(0xC600) u8 sound_result[128];
__location(0xFF44) u8 Sound_LY;
__location(0xFF68) u8 Sound_BGPI;
__location(0xFF69) u8 Sound_BGPD;
u8 __cgb_is_cgb();

// Poll a whole scanline cycle: exactly one driver update per displayed frame.
void sound_wait(u8 frames) {
    while (frames != 0) {
        while (Sound_LY >= 144) {}
        while (Sound_LY < 144) {}
        Audio_Update();
        frames--;
    }
}
void sound_begin(const u8* title) {
    u8 i;
    m_init();
    if (__cgb_is_cgb()) {
        m_wait(); M_LCDC=0;
        Sound_BGPI=0x80;
        Sound_BGPD=255; Sound_BGPD=127;
        Sound_BGPD=181; Sound_BGPD=86;
        Sound_BGPD=74; Sound_BGPD=41;
        Sound_BGPD=0; Sound_BGPD=0;
        M_LCDC=0x91;
    }
    for (i=0;i<128;i++) sound_result[i]=0;
    Audio_Init();
    m_text(1,1,title);
    m_text(1,3,"LISTEN TO THE WAV");
    sound_wait(30);
}
void sound_end() {
    Audio_StopMusic();
    Audio_StopSfx();
    sound_result[127]=0xA5;
    m_text(1,5,"SEQUENCE COMPLETE");
    while (1) { sound_wait(1); }
}
