// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/intrinsics.h
u8 example_xy_in_rect(u8 x, u8 y, u8 rx, u8 ry, u8 rw, u8 rh) {
    return __xy_in_rect(x, y, rx, ry, rw, rh);
}
