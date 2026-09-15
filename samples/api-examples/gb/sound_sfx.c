// Each pair lasts one update. Priority controls replacement within each slot.
#include "gb_sound_example.h"
#pragma bank 2
__prg_rom u8 effect[]={33,0xC0,33,0xC0,33,0xC0,33,0xC0,33,0xC0,33,0xC0,
    40,0xC0,40,0xC0,40,0xC0,40,0xC0,40,0xC0,40,0xC0,0};
__prg_rom u8 wave_effect[]={AUDIO_SFX_CH3_MARKER,
    33,0x20,33,0x20,33,0x20,33,0x20,33,0x20,33,0x20,
    40,0x20,40,0x20,40,0x20,40,0x20,40,0x20,40,0x20,0};
#pragma bank 0
void main() {
    sound_begin("BANKED SOUND EFFECT");
    Audio_SetMasterVolume(3,3);
    // Read the marker in bank 2 while restoring the caller's original mapping.
    Audio_PlaySFXPannedBanked(2,effect,5,AUDIO_PAN_LEFT);
    sound_result[0]=Audio_EffectPriority;
    Audio_PlaySFXBanked(2,effect,4);
    sound_result[1]=Audio_EffectPriority;
    sound_wait(30);
    Audio_PlaySFXPannedBanked(2,wave_effect,5,AUDIO_PAN_RIGHT);
    sound_result[2]=Audio_EffectPriority3;
    sound_wait(30);
    // Implicit-bank entry points capture bank 2; the service restores bank 1.
    __bankswitch(2);
    Audio_PlaySFX(effect,5);
    __bankswitch(1);
    sound_result[3]=Audio_EffectBank;
    sound_wait(30);
    __bankswitch(2);
    Audio_PlaySFXPanned(effect,5,AUDIO_PAN_RIGHT);
    __bankswitch(1);
    sound_wait(6);
    Audio_StopSfx();
    sound_result[4]=(u8)(Audio_EffectPointer==0);
    sound_wait(24);
    // Disabling effects releases current owners; re-enable before the next request.
    Audio_PlaySFXBanked(2,effect,5);
    sound_wait(6);
    Audio_SetSfxEnabled(0);
    sound_result[5]=Audio_SfxEnabled;
    sound_result[6]=(u8)(Audio_EffectPointer==0);
    sound_wait(24);
    Audio_SetSfxEnabled(1);
    Audio_PlaySFXBanked(2,effect,5);
    sound_wait(30);
    sound_result[7]=Audio_SfxEnabled;
    sound_end();
}
