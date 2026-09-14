// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/intrinsics.h
u8 example_bit_test(u8* base, u16 bit) {
    return __bit_test(base, bit);
}
