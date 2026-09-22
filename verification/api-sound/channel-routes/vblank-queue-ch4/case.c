#define SOUND_VBLANK
#include "gb_sound_example.h"
__location(0xFF70) u8 Sound_SVBK;
__prg_rom u8 route_song[]={30,AUDIO_VBLANK_REST,AUDIO_VBLANK_REST,AUDIO_VBLANK_REST,0x35,90,AUDIO_VBLANK_REST,AUDIO_VBLANK_REST,AUDIO_VBLANK_REST,AUDIO_VBLANK_STOP,AUDIO_VBLANK_END};
void main() {
    u8 i;
    sound_begin("CH4 VBLANK-QUEUE");
    __asm { DI }
    Audio_SetMasterVolume(3,3);
    // Odd physical channels go left; even physical channels go right.
    Audio_SetPan(AUDIO_CHANNEL_CH1,AUDIO_PAN_LEFT);
    Audio_SetPan(AUDIO_CHANNEL_CH2,AUDIO_PAN_RIGHT);
    Audio_SetPan(AUDIO_CHANNEL_CH3,AUDIO_PAN_LEFT);
    Audio_SetPan(AUDIO_CHANNEL_CH4,AUDIO_PAN_RIGHT);
    Audio_NoiseEffectActive=0;AudioVBlank_Init();AudioVBlank_Ch1Envelope=0xC0;AudioVBlank_Ch2Envelope=0xC0;AudioVBlank_Ch3Level=0x20;AudioVBlank_Ch4Envelope=0xC0;AudioVBlank_PlayMusic(route_song);
// Publish both records before enabling their ISR consumer.
Sound_SVBK=1;for(i=0;i<10;i++)AudioVBlank_QueueBuffer[i]=route_song[i];AudioVBlank_QueueReadIndex=0;AudioVBlank_QueueWriteIndex=2;AudioVBlank_QueueCount=2;AudioVBlank_QueueMode=1;AudioVBlank_EnableIrq();
    sound_wait(10);
    sound_result[0]=(u8)(NR52&15);
    sound_result[1]=NR51;
    sound_result[2]=NR32;
    sound_result[3]=NR43;
    sound_wait(25);
    sound_wait(10);
    sound_result[4]=(u8)(NR52&15);
    sound_wait(25);
    AudioVBlank_DisableIrq();AudioVBlank_Stop();
    sound_end();
}
