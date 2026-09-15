#pragma once
// Keep several independent on/off flags in the individual bits of two RAM bytes.
u8 bit_flags[2];
u8 bit_off;
u8 bit_on;
u8 bit_set_value;
u8 bit_clear_value;
u8 bit_toggle_value;
u8 bit_restore_value;
u8 bit_next_byte;
u8 bit_failures;
u8 bit_is_on;

void bit_checks(){
    bit_failures=0;bit_flags[0]=0xA4;bit_flags[1]=0x80;
    // example:__bit_test:start
    bit_off=__bit_test(bit_flags,1); // Bit 1 of A4 is clear: zero.
    bit_on=__bit_test(bit_flags,7);  // Bit 7 is set: GB returns 1; FC returns 128.
    bit_is_on=0;
    if(bit_on!=0)bit_is_on=1; // The same nonzero test works on both targets.
    // example:__bit_test:end
    if(bit_off!=0 || bit_on!=BIT_EXPECTED_ON || bit_is_on!=1 || bit_flags[0]!=0xA4)bit_failures++;
    // example:__bit_set:start
    __bit_set(bit_flags,1);
    bit_set_value=bit_flags[0]; // A4 | 02 = A6, decimal 166.
    __bit_set(bit_flags,1);     // Setting it twice leaves it set.
    // example:__bit_set:end
    if(bit_set_value!=0xA6 || bit_flags[0]!=0xA6)bit_failures++;
    // example:__bit_clear:start
    __bit_clear(bit_flags,2);
    bit_clear_value=bit_flags[0]; // A6 & FB = A2, decimal 162.
    __bit_clear(bit_flags,2);     // Clearing it twice leaves it clear.
    // example:__bit_clear:end
    if(bit_clear_value!=0xA2 || bit_flags[0]!=0xA2)bit_failures++;
    // example:__bit_toggle:start
    __bit_toggle(bit_flags,7);
    bit_toggle_value=bit_flags[0]; // A2 ^ 80 = 22, decimal 34.
    __bit_toggle(bit_flags,7);
    bit_restore_value=bit_flags[0]; // Two toggles restore A2.
    // example:__bit_toggle:end
    if(bit_toggle_value!=0x22 || bit_restore_value!=0xA2)bit_failures++;
    // Index 9 selects bit 1 in the second byte, without changing the first byte.
    __bit_set(bit_flags,9);bit_next_byte=bit_flags[1];
    if(bit_next_byte!=0x82 || bit_flags[0]!=0xA2)bit_failures++;
}

void bit_show(){
    bit_label(0,"PACKED BIT FLAGS");
    bit_value(2,"TEST OFF",bit_off);bit_value(4,"TEST ON",bit_on);
    bit_value(6,"SET BIT1",bit_set_value);bit_value(8,"CLEAR BIT2",bit_clear_value);
    bit_value(10,"TOGGLE BIT7",bit_toggle_value);bit_value(12,"RESTORE",bit_restore_value);
    bit_value(14,"NEXT BYTE",bit_next_byte);bit_value(16,"FAILED",bit_failures);
}
