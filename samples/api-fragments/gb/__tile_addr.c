// Usage fragment, not a standalone ROM.
// Declaration source: lib/rpg.h
u16 example_tile_addr(u16 base, u8 x, u8 y) {
    return __tile_addr(base, x, y);
}
