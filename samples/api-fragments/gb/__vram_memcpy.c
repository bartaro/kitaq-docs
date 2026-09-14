// Usage fragment, not a standalone ROM.
// Declaration source: kitaqgb/lib/rpg.h
void example_vram_memcpy(u16 dst, const void* src, u16 len) {
    __vram_memcpy(dst, src, len);
}
