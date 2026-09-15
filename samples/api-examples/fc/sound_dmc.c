// A 17-byte original delta pattern, aligned to a 64-byte DMC start boundary.
#include "fc_sound_example.h"
#pragma bank 0
__aligned(64) __prg_rom u8 delta[17]={0xFF,0xFF,0,0,0xFF,0xFF,0,0,0xFF,0xFF,0,0,0xFF,0xFF,0,0,0xAA};
void main(void) {
    sound_begin("DMC ORIGINAL DELTAS");
    sound_result[0]=(u8)(((u16)delta&63)==0);
    sound_result[1]=(u8)((u16)delta>=0xC000);
    // Loop at NTSC rate index 10; start the output accumulator at its midpoint.
    nes_dmc_config(0x4A,64,(u16)delta,17);
    nes_dmc_start();
    sound_wait(60);
    nes_dmc_stop(); sound_wait(30);
    nes_dmc_play(0x4C,64,(u16)delta,17);
    sound_wait(60);
    nes_dmc_stop(); sound_wait(30);
    sound_end();
}
