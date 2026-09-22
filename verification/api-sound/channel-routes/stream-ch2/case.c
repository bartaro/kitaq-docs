#include "gb_sound_example.h"
__location(0xFF70) u8 Sound_SVBK;
__prg_rom u8 route_song[]={AUDIO_CMD_SET_INST,AUDIO_STREAM_CHANNEL_CH2,0,0xC0,AUDIO_CMD_SET_CH3_LEVEL,0x20,AUDIO_CMD_NOTE,AUDIO_STREAM_CHANNEL_CH2,33,AUDIO_CMD_WAIT,30,AUDIO_CMD_STOP_CHANNEL,AUDIO_STREAM_CHANNEL_CH2,AUDIO_CMD_WAIT,90,AUDIO_CMD_STOP};
void main() {
    u8 i;
    sound_begin("CH2 STREAM");
    __asm { DI }
    Audio_SetMasterVolume(3,3);
    // Odd physical channels go left; even physical channels go right.
    Audio_SetPan(AUDIO_CHANNEL_CH1,AUDIO_PAN_LEFT);
    Audio_SetPan(AUDIO_CHANNEL_CH2,AUDIO_PAN_RIGHT);
    Audio_SetPan(AUDIO_CHANNEL_CH3,AUDIO_PAN_LEFT);
    Audio_SetPan(AUDIO_CHANNEL_CH4,AUDIO_PAN_RIGHT);
    Audio_PlayMusic(0,route_song);
// Starting a song resets pan; apply the test routing after that reset.
Audio_SetPan(AUDIO_CHANNEL_CH1,AUDIO_PAN_LEFT);Audio_SetPan(AUDIO_CHANNEL_CH2,AUDIO_PAN_RIGHT);Audio_SetPan(AUDIO_CHANNEL_CH3,AUDIO_PAN_LEFT);Audio_SetPan(AUDIO_CHANNEL_CH4,AUDIO_PAN_RIGHT);
    sound_wait(10);
    sound_result[0]=(u8)(NR52&15);
    sound_result[1]=NR51;
    sound_result[2]=NR32;
    sound_result[3]=NR43;
    sound_wait(25);
    sound_wait(10);
    sound_result[4]=(u8)(NR52&15);
    sound_wait(25);
    sound_end();
}
