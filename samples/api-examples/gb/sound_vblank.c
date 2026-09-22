// Direct fixed-bank music with an actual VBlank ISR and a counting frame hook.
#define SOUND_VBLANK
#include "gb_sound_example.h"
__wram u8 hook_count;
__prg_rom u8 irq_song[]={30,33,0xFF,0xFF,0xFF,30,40,0xFF,0xFF,0xFF,0xFE};
void frame_hook() { hook_count++; }
void main() {
    u8 before;
    sound_begin("VBLANK MUSIC GATES");
    Audio_NoiseEffectActive=0;
    AudioVBlank_Init();
    sound_result[0]=AudioVBlank_MusicPlaying;
    AudioVBlank_Ch1Envelope=0xC0;
    Audio_SetMasterVolume(3,3);
    hook_count=0; AudioVBlank_FrameHook=frame_hook;
    AudioVBlank_SetMusic(irq_song);
    AudioVBlank_Play();
    AudioVBlank_EnableIrq();
    sound_wait(45);
    // Disable music processing while the hook and current note remain active.
    __asm { DI }
    AudioVBlank_SetEnabled(0); before=hook_count;
    __asm { EI }
    sound_wait(30);
    sound_result[1]=(u8)(hook_count!=before);
    __asm { DI }
    AudioVBlank_Stop();
    __asm { EI }
    sound_wait(30);
    __asm { DI }
    AudioVBlank_SetEnabled(1); AudioVBlank_PlayMusic(irq_song);
    __asm { EI }
    sound_wait(45);
    AudioVBlank_DisableIrq();
    before=hook_count;
    sound_wait(30);
    sound_result[2]=(u8)(hook_count==before);
    sound_result[3]=(u8)(AudioVBlank_IE&1);
    AudioVBlank_Stop(); sound_wait(30);
    sound_end();
}
