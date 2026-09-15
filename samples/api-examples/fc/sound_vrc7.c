// Mapper 85: an FM preset followed by a simple original user instrument.
#include "fc_sound_example.h"
#include "vrc7_sound.c"
__prg_rom u8 patch[8]={0x21,0x21,0x3F,0x00,0xF0,0xF0,0x0F,0x0F};
void main(void) {
    // Map the supplied 8 KiB font as eight consecutive 1 KiB CHR windows.
    *((u8*)0xA000)=0; *((u8*)0xA010)=1;
    *((u8*)0xB000)=2; *((u8*)0xB010)=3;
    *((u8*)0xC000)=4; *((u8*)0xC010)=5;
    *((u8*)0xD000)=6; *((u8*)0xD010)=7;
    sound_begin("VRC7 PRESET AND PATCH");
    nes_vrc7_silence_all();
    nes_vrc7_channel_set(0,1,3,290,4,VRC7_KEY_ON);
    sound_wait(60); nes_vrc7_key_off(0); sound_wait(30);
    nes_vrc7_set_user_patch(patch);
    nes_vrc7_channel_set(0,0,3,290,4,VRC7_KEY_ON);
    sound_wait(60);
    // Raw register 30 selects instrument zero and maximum attenuation.
    nes_vrc7_write(0x30,0x0F);
    nes_vrc7_key_off(0);
    nes_vrc7_silence_all(); sound_wait(30);
    sound_end();
}
