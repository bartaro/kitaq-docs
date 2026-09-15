// Mapper 24: two pulse voices followed by the saw accumulator.
#include "fc_sound_example.h"
#include "vrc6_sound.c"
void main(void) {
    // The background font occupies the first four 1 KiB CHR windows.
    *((u8*)0xD000)=0; *((u8*)0xD001)=1;
    *((u8*)0xD002)=2; *((u8*)0xD003)=3;
    sound_begin("VRC6 PULSE PULSE SAW");
    nes_vrc6_silence_all();
    nes_vrc6_pulse1_set(0x7C,253);
    sound_wait(45); nes_vrc6_pulse1_off(); sound_wait(15);
    nes_vrc6_pulse2_set(0x3C,253);
    sound_wait(45); nes_vrc6_pulse2_off(); sound_wait(15);
    nes_vrc6_saw_set(32,289);
    sound_wait(45); nes_vrc6_saw_off(); sound_wait(15);
    nes_vrc6_silence_all();
    sound_end();
}
