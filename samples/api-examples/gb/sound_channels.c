// Four isolated voices, each lasting 30 frames, separated by 15 silent frames.
#include "gb_sound_example.h"
void main() {
    sound_begin("FOUR SOUND CHANNELS");
    Audio_SetMasterVolume(3,3);
    // CH1: A4, 50% duty, fixed envelope volume 12.
    Audio_SetCh1Duty(2);
    sound_result[0]=Audio_Ch1Duty;
    Audio_Ch1NoteOn(33,0xC0,Audio_Ch1Duty);
    sound_result[1]=NR12;
    sound_wait(30); Audio_StopChannel(AUDIO_CHANNEL_CH1); sound_wait(15);
    // CH2: A4, 25% duty. Changing the cached duty takes effect on this trigger.
    Audio_SetCh2Duty(1);
    sound_result[2]=Audio_Ch2Duty;
    Audio_Ch2NoteOn(33,0xC0,Audio_Ch2Duty);
    sound_result[3]=NR22;
    sound_wait(30); Audio_StopChannel(AUDIO_CHANNEL_CH2); sound_wait(15);
    // CH3: the initialized triangle wave, at 50% digital output level.
    Audio_SetCh3Level(AUDIO_CH3_LEVEL_50);
    sound_result[4]=Audio_Ch3Level;
    Audio_Ch3NoteOn(33,Audio_Ch3Level);
    sound_result[5]=NR32;
    sound_wait(30); Audio_StopChannel(AUDIO_CHANNEL_CH3); sound_wait(15);
    // CH4: a sustained noise burst; param is NR43, not a pitched note number.
    Audio_SetCh4Param(0x35);
    sound_result[6]=Audio_Ch4Param;
    Audio_Ch4NoteOn(Audio_Ch4Param,0xC0);
    sound_result[7]=NR43;
    sound_wait(30); Audio_StopChannel(AUDIO_CHANNEL_CH4); sound_wait(15);
    sound_end();
}
