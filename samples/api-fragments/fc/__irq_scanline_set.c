// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/intrinsics.h
void example_irq_scanline_set(u8 line) {
    __irq_scanline_set(line);
}
