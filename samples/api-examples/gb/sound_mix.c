// A sustained pulse moves left, right and center, then fades to a quieter level.
#include "gb_sound_example.h"
void main() {
    sound_begin("PAN AND VOLUME");
    Audio_SetMasterVolume(7,7);
    Audio_Ch1NoteOn(33,0xC0,2);
    Audio_SetPan(AUDIO_CHANNEL_CH1,AUDIO_PAN_LEFT);
    sound_result[0]=NR51;
    sound_wait(30);
    // Packed low two bits are CH1: 2 means right. Other channels remain centered.
    Audio_SetPanPacked(2);
    sound_result[1]=NR51;
    sound_wait(30);
    Audio_SetPanPacked(0);
    sound_result[2]=NR51;
    Audio_FadeToMasterVolume(1,1,5);
    sound_wait(30);
    sound_result[3]=NR50;
    sound_result[4]=Audio_FadeActive;
    sound_wait(30);
    // Cancel halfway through a rise: retain volume 4 instead of reaching 7.
    Audio_FadeToMasterVolume(7,7,5);
    sound_wait(15);
    Audio_CancelMasterVolumeFade();
    sound_result[5]=NR50;
    sound_wait(30);
    sound_result[6]=NR50;
    // A zero fade interval sets the target immediately. Level zero is not mute.
    Audio_FadeToMasterVolume(0,0,0);
    sound_result[7]=NR50;
    sound_wait(30);
    Audio_StopChannel(AUDIO_CHANNEL_CH1);
    sound_wait(15);
    sound_end();
}
