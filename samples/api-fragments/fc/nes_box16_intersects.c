// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/collision.h
unsigned char example_nes_box16_intersects(struct NesBox16* a, struct NesBox16* b) {
    return nes_box16_intersects(a, b);
}
