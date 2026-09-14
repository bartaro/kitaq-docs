// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/intrinsics.h
u8 example_fkb_read_row_col(u8 row, u8 col) {
    return __fkb_read_row_col(row, col);
}
