// Usage fragment, not a standalone ROM.
// Declaration source: lib/cgb_tile.h
void example_settileatcgb_unsafe(u16 base, u8 x, u8 y, u8 tile, u8 attr) {
    __settileatcgb_unsafe(base, x, y, tile, attr);
}
