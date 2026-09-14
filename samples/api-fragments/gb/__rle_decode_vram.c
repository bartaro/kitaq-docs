// Usage fragment, not a standalone ROM.
// Declaration source: kitaqgb/lib/rpg.h
u16 example_rle_decode_vram(u16 dst, u8 bank, const void* src) {
    return __rle_decode_vram(dst, bank, src);
}
