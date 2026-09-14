// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/vram.h
u8 example_vram_queue_bg_block(u16 base, u8 x, u8 y, u8 w, u8 h, const u8* src) {
    return vram_queue_bg_block(base, x, y, w, h, src);
}
