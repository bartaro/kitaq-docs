#include "gb_sound_example.h"
__location(0xFF70) u8 Sound_SVBK;
void main() {
    u8 i;
    sound_begin("CH1 DIRECT");
    __asm { DI }
    Audio_SetMasterVolume(3,3);
    // Odd physical channels go left; even physical channels go right.
    Audio_SetPan(AUDIO_CHANNEL_CH1,AUDIO_PAN_LEFT);
    Audio_SetPan(AUDIO_CHANNEL_CH2,AUDIO_PAN_RIGHT);
    Audio_SetPan(AUDIO_CHANNEL_CH3,AUDIO_PAN_LEFT);
    Audio_SetPan(AUDIO_CHANNEL_CH4,AUDIO_PAN_RIGHT);
    Audio_Ch1NoteOn(33,0xC0,2);
    sound_wait(10);
    sound_result[0]=(u8)(NR52&15);
    sound_result[1]=NR51;
    sound_result[2]=NR32;
    sound_result[3]=NR43;
    sound_wait(25);Audio_StopChannel(AUDIO_CHANNEL_CH1);
    sound_wait(10);
    sound_result[4]=(u8)(NR52&15);
    sound_wait(25);
    sound_end();
}
