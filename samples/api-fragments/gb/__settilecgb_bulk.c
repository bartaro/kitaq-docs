// Usage fragment, not a standalone ROM.
// Declaration source: kitaqgb/lib/cgb_tile.h
void example_settilecgb_bulk(u16 dest, const u8* tile_src, const u8* attr_src, u8 count) {
    __settilecgb_bulk(dest, tile_src, attr_src, count);
}
