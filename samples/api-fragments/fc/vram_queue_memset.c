// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/vram.h
u8 example_vram_queue_memset(u16 dst, u8 value, u16 len) {
    return vram_queue_memset(dst, value, len);
}
