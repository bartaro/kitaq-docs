// Usage fragment, not a standalone ROM.
// Declaration source: kitaqgb/lib/rpg.h
void example_vram_memset(u16 dst, u8 value, u16 len) {
    __vram_memset(dst, value, len);
}
