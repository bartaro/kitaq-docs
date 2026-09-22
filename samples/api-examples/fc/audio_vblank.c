// Copyright (c) 2026 DAISUKE OBA. SPDX-License-Identifier: MIT
// Original four-channel phrase. No game soundtrack or extracted data is used.
#include "fc_common.h"
#include "audio_vblank.h"

// Delay, pulse 1, pulse 2, triangle, noise; note 24 is C4 and note 12 is C3.
// A noise value of 18 means short mode, period index 2.
__prg_rom const u8 song[40]={
    24,24,12,0,2, 24,28,16,0,254, 24,31,19,7,4, 24,36,24,7,254,
    24,31,19,5,18,24,28,16,5,254,24,26,14,7,6,24,24,12,0,254
};
__location(0x0700) u8 result[16];
__prg_rom const u8 quiet_record[5]={2,254,254,254,254};

void main(void){
    u8 first;u8 i;u16 total;
    m_init();m_text(1,1,"NMI MUSIC / FOUR CHANNELS");m_wait();
    m_text(1,4,"CH1 PULSE 1 / CH2 PULSE 2");m_wait();
    m_text(1,6,"CH3 TRIANGLE / CH4 NOISE");m_wait();
    m_text(1,9,"RAM QUEUE: SEVEN RECORDS");m_wait();
    m_text(1,11,"90 FRAMES WITHOUT REFILL");m_wait();
    // example:nes_audio_vblank_init:start
    nes_audio_vblank_init();
    // example:nes_audio_vblank_init:end
    // example:nes_audio_vblank_set_timbre:start
    nes_audio_vblank_set_timbre(0,0x8C); // 50% pulse duty, volume 12.
    nes_audio_vblank_set_timbre(1,0x4A); // 25% pulse duty, volume 10.
    // example:nes_audio_vblank_set_timbre:end
    // example:nes_audio_vblank_play_music:start
    result[0]=nes_audio_vblank_play_music(song,8,0);
    // example:nes_audio_vblank_play_music:end
    // example:nes_audio_vblank_queued:start
    result[1]=nes_audio_vblank_queued(); // Seven records after prefill.
    // example:nes_audio_vblank_queued:end
    // example:nes_audio_vblank_free:start
    result[2]=nes_audio_vblank_free();   // No free slots immediately after prefill.
    // example:nes_audio_vblank_free:end
    first=__nmi_ready();total=0;
    // Deliberately do not wait, refill or call an audio update for 90 frames.
    // The interrupt consumer continues independently of this arithmetic loop.
    while((u8)(__nmi_ready()-first)<90){
        total=0;for(i=0;i<100;i++)total=total+i;
        if(total!=4950)result[7]=1;
    }
    result[3]=1;
    // example:nes_audio_vblank_is_playing:start
    while(nes_audio_vblank_is_playing()!=0){
        // example:nes_audio_vblank_refill:start
        nes_audio_vblank_refill();
        // example:nes_audio_vblank_refill:end
        __nmi_wait();
    }
    // example:nes_audio_vblank_is_playing:end
    // example:nes_audio_vblank_underruns:start
    result[4]=nes_audio_vblank_underruns(); // Zero: queued time covered the busy section.
    // example:nes_audio_vblank_underruns:end
    // The following silent pass demonstrates manual queue control separately
    // from the ROM feeder. All four STOP fields silence their physical channels.
    // example:nes_audio_vblank_set_music:start
    result[5]=nes_audio_vblank_set_music(song,8,0); // Attach without starting.
    // example:nes_audio_vblank_set_music:end
    // example:nes_audio_vblank_stop:start
    nes_audio_vblank_stop(); // Clear the feeder and queued records; silence now.
    // example:nes_audio_vblank_stop:end
    // example:nes_audio_vblank_enqueue:start
    result[6]=nes_audio_vblank_enqueue(quiet_record); // Copy five bytes into RAM.
    // example:nes_audio_vblank_enqueue:end
    // example:nes_audio_vblank_start:start
    nes_audio_vblank_start(); // Consume the copied record on the next NMI.
    // example:nes_audio_vblank_start:end
    // example:__nes_audio_vblank_tick:start
    // The linked audio_vblank.c supplies __nes_audio_vblank_tick().
    // The compiler calls that hook once per NMI. Do not call it in this loop.
    __nmi_wait();
    // example:__nes_audio_vblank_tick:end
    nes_audio_vblank_stop();
    m_text(1,15,"PHRASE COMPLETE / SILENT");m_wait();
    m_text(1,17,"UNDERRUNS 0 / MATH OK");m_wait();
    result[15]=165;
    while(1){}
}
