// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/intrinsics.h
u8 example_metasprite_draw(u8 oam_index, u8 base_x, u8 base_y, const u8* metasprite) {
    return __metasprite_draw(oam_index, base_x, base_y, metasprite);
}
