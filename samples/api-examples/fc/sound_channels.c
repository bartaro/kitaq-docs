// NTSC: pulse A4 (~440 Hz), triangle A3 (~220 Hz), noise, then two short effects.
#include "fc_sound_example.h"
void main(void) {
    sound_begin("APU CHANNELS AND BLIPS");
    // Constant volume 12, length halt and 50% duty. Each helper replaces 4015.
    nes_sfx_square1(0xBC,253,0);
    sound_result[0]=(u8)(APU_STATUS&0x1F);
    sound_wait(30);
    nes_apu_channel_enable(0); sound_wait(15);
    nes_sfx_square2(0x7C,253,0);
    sound_result[1]=(u8)(APU_STATUS&0x1F);
    sound_wait(30); nes_apu_silence_all(); sound_wait(15);
    nes_sfx_triangle(0xFF,253,0);
    sound_result[2]=(u8)(APU_STATUS&0x1F);
    sound_wait(30); nes_apu_silence_all(); sound_wait(15);
    nes_sfx_noise(0x3C,5,0);
    sound_result[3]=(u8)(APU_STATUS&0x1F);
    sound_wait(30); nes_apu_silence_all(); sound_wait(15);
    nes_sfx_tick_blip(); sound_wait(30); nes_apu_silence_all(); sound_wait(15);
    nes_sfx_move_blip(); sound_wait(30); nes_apu_silence_all(); sound_wait(15);
    sound_end();
}
