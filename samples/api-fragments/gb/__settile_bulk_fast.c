// Usage fragment, not a standalone ROM.
// Declaration source: kitaqgb/lib/cgb_tile.h
void example_settile_bulk_fast(u16 dest, const u8* src, u8 count) {
    __settile_bulk_fast(dest, src, count);
}
