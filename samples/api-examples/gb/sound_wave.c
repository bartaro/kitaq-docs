// Compare a triangle preset with an original packed 32-sample pulse waveform.
#include "gb_sound_example.h"
__prg_rom u8 custom_wave[16]={0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0,0,0,0,0,0,0,0};
void main() {
    sound_begin("WAVE PRESET CUSTOM");
    Audio_SetMasterVolume(3,3);
    Audio_LoadWave(AUDIO_WAVE_TRIANGLE);
    Audio_Ch3NoteOn(33,AUDIO_CH3_LEVEL_100);
    sound_wait(45); Audio_StopChannel(AUDIO_CHANNEL_CH3); sound_wait(15);
    // Loading copies all sixteen bytes and enables the DAC without triggering a note.
    Audio_LoadCustomWave(custom_wave);
    sound_result[0]=Audio_CustomWave[0]; sound_result[1]=Audio_CustomWave[8];
    Audio_Ch3NoteOn(33,AUDIO_CH3_LEVEL_100);
    sound_wait(45); Audio_StopChannel(AUDIO_CHANNEL_CH3); sound_wait(15);
    // The cache survives another preset load; select CUSTOM to reuse it.
    Audio_LoadWave(AUDIO_WAVE_SAW);
    Audio_LoadWave(AUDIO_WAVE_CUSTOM);
    sound_result[2]=WAVE0; sound_result[3]=WAVE8;
    Audio_Ch3NoteOn(33,AUDIO_CH3_LEVEL_100);
    sound_wait(45); Audio_StopChannel(AUDIO_CHANNEL_CH3); sound_wait(15);
    sound_end();
}
