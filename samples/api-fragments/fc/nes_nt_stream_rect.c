// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/nametable_asset.h
void example_nes_nt_stream_rect(unsigned short nt_base, unsigned char tile_x, unsigned char tile_y, unsigned char width, unsigned char height, unsigned char pitch, unsigned char* src) {
    nes_nt_stream_rect(nt_base, tile_x, tile_y, width, height, pitch, src);
}
