// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/collision.h
unsigned char example_nes_box16_contains_point(struct NesBox16* box, unsigned short px, unsigned short py) {
    return nes_box16_contains_point(box, px, py);
}
