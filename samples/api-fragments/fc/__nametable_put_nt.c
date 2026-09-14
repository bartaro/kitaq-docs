// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/intrinsics.h
void example_nametable_put_nt(u8 nt, u8 x, u8 y, u8 tile) {
    __nametable_put_nt(nt, x, y, tile);
}
