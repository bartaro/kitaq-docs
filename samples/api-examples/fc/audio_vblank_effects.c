// Copyright (c) 2026 DAISUKE OBA. SPDX-License-Identifier: MIT
// Original tones demonstrate ownership, pause/resume and a noise envelope.
#include "fc_common.h"
#include "audio_vblank.h"
__prg_rom const u8 background[5]={255,21,254,254,254}; // A3, 220 Hz on CH1.
__prg_rom const u8 effect[5]={30,45,255,255,255};      // A5, 880 Hz on CH1.
__prg_rom const u8 long_effect[5]={90,45,255,255,255};
__prg_rom const u8 noise[5]={90,255,255,255,8};
__location(0x0700) u8 result[16];
__location(0x0710) u8 phase;
void wait_frames(u8 count){u8 i;for(i=0;i<count;i++){nes_audio_vblank_refill();__nmi_wait();}}
void main(void){
    m_init();m_text(1,1,"NMI MUSIC / PAUSE AND SFX");m_wait();
    m_text(1,4,"CH1 BGM 220 HZ / SFX 880 HZ");m_wait();
    m_text(1,7,"SFX ENDS: BGM RETURNS");m_wait();
    m_text(1,10,"PAUSE: SILENT FOR 30 FRAMES");m_wait();
    m_text(1,13,"CH4: ONE SHOT NOISE DECAY");m_wait();
    nes_audio_vblank_init();nes_audio_vblank_set_timbre(0,0x8C);
    result[0]=nes_audio_vblank_play_music(background,1,1);
    phase=1;wait_frames(30);
    // example:nes_audio_vblank_play_sfx:start
    result[1]=nes_audio_vblank_play_sfx(effect,1,1); // Mask bit 0 owns CH1.
    // The BGM timeline keeps advancing; its current CH1 note returns after 30 ticks.
    // example:nes_audio_vblank_play_sfx:end
    phase=2;wait_frames(45);
    // example:nes_audio_vblank_pause:start
    nes_audio_vblank_pause(1); // Freeze BGM and SFX, and mute immediately.
    phase=3;wait_frames(30);   // Refill may copy data; neither timeline advances.
    nes_audio_vblank_pause(0); // Restore held notes on the next NMI.
    // example:nes_audio_vblank_pause:end
    phase=4;wait_frames(30);
    result[2]=nes_audio_vblank_play_sfx(long_effect,1,1);
    phase=5;wait_frames(15);
    // example:nes_audio_vblank_stop_sfx:start
    nes_audio_vblank_stop_sfx(); // Release effect ownership at the next NMI.
    // BGM continues at its current position; this does not restart the song.
    // example:nes_audio_vblank_stop_sfx:end
    phase=6;wait_frames(30);
    nes_audio_vblank_stop();
    // example:nes_audio_vblank_set_timbre:start
    nes_audio_vblank_set_timbre(3,NES_AUDIO_NOISE_ENVELOPE|15);
    result[3]=nes_audio_vblank_play_sfx(noise,1,8); // Bit 3 owns CH4; no BGM needed.
    // The slow one-shot envelope fades by itself. It does not loop at zero.
    // example:nes_audio_vblank_set_timbre:end
    phase=7;wait_frames(90);nes_audio_vblank_stop();phase=8;
    result[4]=nes_audio_vblank_underruns();
    m_text(1,17,"COMPLETE / ALL CHANNELS OFF");m_wait();
    result[15]=165;while(1){}
}
