// Original two-note phrase: pause preserves the cursor; the enable gate does not.
#include "gb_sound_example.h"
__prg_rom u8 song[]={
    AUDIO_CMD_SET_INST,AUDIO_STREAM_CHANNEL_CH1,2,0xC0,
    AUDIO_CMD_NOTE,AUDIO_STREAM_CHANNEL_CH1,33,AUDIO_CMD_WAIT,59,
    AUDIO_CMD_NOTE,AUDIO_STREAM_CHANNEL_CH1,40,AUDIO_CMD_WAIT,59,
    AUDIO_CMD_LOOP
};
void main() {
    u8 delay;
    sound_begin("MUSIC PAUSE GATE");
    Audio_SetMasterVolume(3,3);
    Audio_PlayMusic(0,song);
    sound_wait(30);
    delay=Audio_Delay;
    Audio_SetPaused(1);
    sound_wait(30);
    sound_result[0]=(u8)(Audio_Delay==delay);
    sound_result[1]=Audio_Paused;
    Audio_SetPaused(0);
    sound_wait(30);
    sound_result[2]=Audio_Paused;
    // Disabling suppresses note writes; the next 30 updates still consume data.
    Audio_SetMusicEnabled(0);
    sound_wait(30);
    sound_result[3]=Audio_Delay;
    sound_result[4]=Audio_MusicEnabled;
    // Explicitly stop the sounding channel while leaving the stream running.
    Audio_StopChannel(AUDIO_CHANNEL_CH1);
    sound_wait(30);
    Audio_SetMusicEnabled(1);
    sound_wait(30);
    Audio_StopMusic();
    sound_result[5]=Audio_PlayingMusic;
    sound_wait(30);
    sound_end();
}
