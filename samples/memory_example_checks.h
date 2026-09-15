#pragma once
// Shared RAM checks for both compilers. No screen pixel is used as memory input.
u8 memory_source[264];
u8 memory_destination[264];
u8 memory_failures;
u8 memory_zero_calls;
u16 memory_copy_word;
u16 memory_fill_word;
u16 memory_copy_byte;
u16 memory_fill_byte;
u16 memory_copy_16;
u16 memory_copy_32;

// Give every source offset a reproducible byte and surround the payload with CC.
void memory_reset(){
    u16 i;
    for(i=0;i<264;i++){
        memory_source[i]=(u8)(i*13+7);
        memory_destination[i]=0xCC;
    }
}

// Verify both complete arrays, including the leading guard and all unused bytes.
// Latch one failure per operation so many bad bytes cannot wrap the error count.
u16 memory_check(u16 count,u8 fill){
    u16 i;
    u8 expected;
    u8 failed;
    failed=0;
    for(i=0;i<264;i++){
        if(memory_source[i]!=(u8)(i*13+7))failed=1;
        expected=0xCC;
        if(i>0&&i<=count){
            if(fill)expected=0x5A;
            else expected=(u8)(i*13+7);
        }
        if(memory_destination[i]!=expected)failed=1;
    }
    if(failed){memory_failures++;return 0;}
    return count;
}

// These observable counters show that even a zero-length call evaluates arguments.
u8* memory_get_destination(){memory_zero_calls++;return memory_destination+1;}
const u8* memory_get_source(){memory_zero_calls++;return memory_source+1;}

void memory_checks(){
    memory_failures=0;
    // example:__memcpy:start
    memory_reset();
    __memcpy(memory_destination+1,memory_source+1,257);
    memory_copy_word=memory_check(257,0); // 257 copied bytes; guards unchanged.
    // example:__memcpy:end
    // example:__memset:start
    memory_reset();
    __memset(memory_destination+1,0x5A,257);
    memory_fill_word=memory_check(257,1); // Repeat one byte, not a 16-bit word.
    // example:__memset:end
    // example:__memcpy_small:start
    memory_reset();
    __memcpy_small(memory_destination+1,memory_source+1,255);
    memory_copy_byte=memory_check(255,0); // Maximum representable byte count.
    // example:__memcpy_small:end
    // example:__memset_small:start
    memory_reset();
    __memset_small(memory_destination+1,0x5A,255);
    memory_fill_byte=memory_check(255,1);
    // example:__memset_small:end
    // example:__copy16:start
    memory_reset();
    __copy16(memory_destination+1,memory_source+1);
    memory_copy_16=memory_check(16,0); // Exactly 16 bytes, not 16 bits.
    // example:__copy16:end
    // example:__copy32:start
    memory_reset();
    __copy32(memory_destination+1,memory_source+1);
    memory_copy_32=memory_check(32,0);
    // example:__copy32:end
    memory_reset();memory_zero_calls=0;
    __memcpy(memory_get_destination(),memory_get_source(),0);
    memory_check(0,0);
    if(memory_zero_calls!=2)memory_failures++;
}

// Present the verified payload lengths, argument-call count and failure latch.
void memory_show(){
    memory_label(0,"RAM COPY AND FILL");
    memory_value(2,"COPY WORD",memory_copy_word);
    memory_value(4,"FILL WORD",memory_fill_word);
    memory_value(6,"COPY BYTE",memory_copy_byte);
    memory_value(8,"FILL BYTE",memory_fill_byte);
    memory_value(10,"COPY16",memory_copy_16);
    memory_value(12,"COPY32",memory_copy_32);
    memory_value(14,"ZERO CALLS",memory_zero_calls);
    memory_value(16,"FAILED",memory_failures);
}
