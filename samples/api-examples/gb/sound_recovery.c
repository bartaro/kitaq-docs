// Exercise the recovery API with IRQ disabled and explicit effect ownership.
#define SOUND_VBLANK
#include "gb_sound_example.h"
void main() {
    sound_begin("EFFECT RECOVERY");
    Audio_NoiseEffectActive=0; AudioVBlank_Init();
    Audio_SetMasterVolume(3,3);
    AudioVBlank_MusicPlaying=1;
    AudioVBlank_Ch1Envelope=0xC0; AudioVBlank_Ch1LatchedNote=33;
    AudioVBlank_Ch3LatchedNote=33;
    // Value 1 represents a suppressed BGM event and survives a release request.
    AudioVBlank_RestoreCh1Pending=1;
    AudioVBlank_RequestRestoreCh1();
    sound_result[0]=AudioVBlank_RestoreCh1Pending;
    AudioVBlank_RestoreCh1(); AudioVBlank_RestoreCh1Pending=0;
    sound_wait(30);
    // Without a pending event, RequestRestore creates release-only value 2.
    AudioVBlank_RequestRestoreCh1();
    sound_result[1]=AudioVBlank_RestoreCh1Pending;
    AudioVBlank_RestoreCh1(); AudioVBlank_RestoreCh1Pending=0;
    sound_wait(30);
    AudioVBlank_RestoreCh3Pending=1;
    AudioVBlank_RequestRestoreCh3();
    sound_result[2]=AudioVBlank_RestoreCh3Pending;
    AudioVBlank_RestoreCh3(); AudioVBlank_RestoreCh3Pending=0;
    sound_wait(30);
    AudioVBlank_RequestRestoreCh3();
    sound_result[3]=AudioVBlank_RestoreCh3Pending;
    AudioVBlank_RestoreCh3(); AudioVBlank_RestoreCh3Pending=0;
    sound_wait(30);
    AudioVBlank_Stop();
    sound_end();
}
