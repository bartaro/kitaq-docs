// Usage fragment, not a standalone ROM.
// Declaration source: kitaqgb/lib/rpg.h
void example_vram_copy_hblank(u16 dst, const void* src, u16 len) {
    __vram_copy_hblank(dst, src, len);
}
