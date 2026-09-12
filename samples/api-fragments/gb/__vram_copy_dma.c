// Usage fragment, not a standalone ROM.
// Declaration source: lib/rpg.h
void example_vram_copy_dma(u16 dst, const void* src, u16 len) {
    __vram_copy_dma(dst, src, len);
}
