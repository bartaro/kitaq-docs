#pragma once
// Each check exercises an actual banked read or call. The display reports
// the requested payload and verifies that bank 2 is restored afterwards.
u8 failures;
u8 first_failure;
u8 buffer[4];
u8 byte_value;
u16 word_value;
BankPtr pointer;
u8 starting_bank;
u8 ending_bank;
#ifndef MANUAL_BANK_FC
u8 requested_bank;
const void* requested_callback;
#endif

void bank_expect(u8 condition,u8 id) {
    if (!condition) {
        if (failures==0) first_failure=id;
        if (failures!=255) failures++;
    }
}

void bank_checks() {
    failures=0;first_failure=0;callback_count=0;callback_byte=0;
    // example:bank_switch:start
    bank_switch(2); // Select the payload window and update library bookkeeping.
    // example:bank_switch:end
    // example:bank_get_current:start
    starting_bank=bank_get_current(); // Last value recorded by bank_switch.
    bank_expect(starting_bank==2,1);
    // example:bank_get_current:end
    bank_expect(home2[0]==0xB2,2);
    // example:__bankof:start
    bank_expect(__bankof(payload)==3,3);
    bank_expect(__bankof(callback)==3,4);
    // example:__bankof:end
    // example:far_data_read8:start
    byte_value=far_data_read8(3,payload); // One byte: 0xD3.
    bank_expect(byte_value==0xD3,5);
    // example:far_data_read8:end
    // example:far_data_read16:start
    word_value=far_data_read16(3,payload+1); // Little-endian 7A 5C -> 0x5C7A.
    bank_expect(word_value==0x5C7A,6);
    // example:far_data_read16:end
    // example:far_data_read:start
    far_data_read(3,payload,buffer,4); // Copy into four writable RAM bytes.
    bank_expect(buffer[0]==0xD3 && buffer[1]==0x7A && buffer[2]==0x5C && buffer[3]==0x96,7);
    // example:far_data_read:end
    // example:farptr_make:start
    farptr_make(&pointer,3,payload+1); // Store a bank and address; do not read ROM.
    bank_expect(pointer.bank==3 && pointer.ptr==payload+1,8);
    farptr_make(0,1,home1); // A null destination is ignored.
    // example:farptr_make:end
    // example:farptr_read8:start
    bank_expect(farptr_read8(pointer)==0x7A,9);
    // example:farptr_read8:end
    // example:farptr_read16:start
    bank_expect(farptr_read16(pointer)==0x5C7A,10);
    // example:farptr_read16:end
    // example:farptr_read:start
    farptr_read(pointer,buffer,3);
    bank_expect(buffer[0]==0x7A && buffer[1]==0x5C && buffer[2]==0x96,11);
    bank_expect(pointer.bank==3 && pointer.ptr==payload+1,23);
    // example:farptr_read:end
    buffer[0]=0xE7;far_data_read(3,payload,buffer,0);
    bank_expect(buffer[0]==0xE7,12); // Empty copies preserve destination bytes.
    // example:__farpeek8:start
#ifdef MANUAL_BANK_FC
    bank_expect(__farpeek8(3,(u16)payload)==0xD3,13);
#else
    bank_expect(__farpeek8(3,payload)==0xD3,13);
#endif
    // example:__farpeek8:end
    // example:__farpeek16:start
#ifdef MANUAL_BANK_FC
    bank_expect(__farpeek16(3,(u16)(payload+1))==0x5C7A,14);
#else
    bank_expect(__farpeek16(3,payload+1)==0x5C7A,14);
#endif
    // example:__farpeek16:end
    // example:far_call:start
    far_call(3,callback); // No arguments; callback reads payload[0] in bank 3.
    bank_expect(callback_count==1 && callback_byte==0xD3,15);
    // example:far_call:end
    // example:__farcall:start
    __farcall(3,callback);
    bank_expect(callback_count==2 && callback_byte==0xD3,16);
    // example:__farcall:end
#ifndef MANUAL_BANK_FC
    // example:__farcall_ptr:start
    requested_bank=3;requested_callback=callback;
    __farcall_ptr(requested_bank,requested_callback); // Runtime bank and address.
    bank_expect(callback_count==3 && callback_byte==0xD3,17);
    // example:__farcall_ptr:end
#endif
    bank_expect(home2[0]==0xB2,18); // A near read proves the actual mapping.
    // example:__bankswitch:start
    __bankswitch(1);
    bank_expect(home1[0]==0xA1,19);
    bank_expect(bank_get_current()==2,20); // Intrinsics bypass the library record.
    __bankswitch(2);
    // example:__bankswitch:end
#ifdef MANUAL_BANK_FC
    // example:__prg_bank_set:start
    __prg_bank_set(1);bank_expect(home1[0]==0xA1,21);
    __prg_bank_set(2); // Same mapper helper as __bankswitch.
    // example:__prg_bank_set:end
#endif
    ending_bank=bank_get_current();
    bank_expect(ending_bank==2 && home2[0]==0xB2,22);
}

// Hexadecimal notation exposes byte order without requiring decimal conversion.
u8 bank_hex_digit(u8 value) { if (value<10) return (u8)('0'+value);return (u8)('A'+value-10); }
void bank_hex(u8 x,u8 y,u8 value) { m_put(x,y,bank_hex_digit(value>>4));m_put((u8)(x+1),y,bank_hex_digit(value&15)); }
void bank_show() {
    m_text(1,0,"BANKED DATA CALLS");m_wait();
    m_text(1,2,"BANK IN");bank_hex(15,2,starting_bank);m_wait();
    m_text(1,4,"BYTE HEX");bank_hex(15,4,byte_value);m_wait();
    m_text(1,6,"WORD HEX");bank_hex(13,6,(u8)(word_value>>8));bank_hex(15,6,(u8)word_value);m_wait();
    m_text(1,8,"CALL COUNT");bank_hex(15,8,callback_count);m_wait();
    m_text(1,10,"BANK OUT");bank_hex(15,10,ending_bank);m_wait();
    m_text(1,12,"FAILED CHECKS");bank_hex(15,12,failures);m_wait();
    m_text(1,14,"FIRST FAILURE");bank_hex(15,14,first_failure);m_wait();
}
