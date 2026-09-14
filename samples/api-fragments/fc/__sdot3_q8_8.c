// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/intrinsics.h
u16 example_sdot3_q8_8(u16 a0, u16 a1, u16 a2, u8 b0, u8 b1, u8 b2) {
    return __sdot3_q8_8(a0, a1, a2, b0, b1, b2);
}
