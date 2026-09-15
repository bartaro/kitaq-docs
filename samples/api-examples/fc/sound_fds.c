// Mapper 20 sound lesson: original 64-step triangle and two sustained pitches.
#include "fc_sound_example.h"
#include "fds_sound.h"
#include "nes_game.h"
__location(0x4087) u8 mod_control;
__location(0x4085) u8 mod_counter;
u8 triangle[64]; u8 modulation[32];
void main(void) {
    u8 i;
    sound_begin("FDS WAVE AND VOLUME");
    for(i=0;i<32;i++) { triangle[i]=(u8)(i*2); triangle[63-i]=(u8)(i*2); modulation[i]=0; }
    __fds_sound_enable();
    // Halt/reset modulation before writing the 32 values (each writes two slots).
    mod_control=0x80; mod_counter=0;
    __fds_mod_load(modulation);
    __fds_wave_load(triangle);
    sound_result[0]=*((u8*)0x4040); sound_result[1]=*((u8*)0x405F);
    __fds_freq_set(1031);
    __fds_volume_set(24);
    sound_wait(60);
    __fds_volume_set(0); sound_wait(30);
    // This macro forwards the same 64-byte load. Use raw envelope registers.
    nes_fds_wave_load(triangle);
    __fds_env_set(0x98,0x80,0);
    __fds_freq_set(1545);
    sound_wait(60);
    __fds_volume_set(0); sound_wait(30);
    sound_end();
}
