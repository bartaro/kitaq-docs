// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/intrinsics.h
void example_vram_fill(u16 ppu_addr, u8 value, u8 len) {
    __vram_fill(ppu_addr, value, len);
}
