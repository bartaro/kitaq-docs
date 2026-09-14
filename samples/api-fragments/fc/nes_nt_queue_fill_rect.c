// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/nametable_asset.h
unsigned char example_nes_nt_queue_fill_rect(unsigned short nt_base, unsigned char tile_x, unsigned char tile_y, unsigned char width, unsigned char height, unsigned char value) {
    return nes_nt_queue_fill_rect(nt_base, tile_x, tile_y, width, height, value);
}
