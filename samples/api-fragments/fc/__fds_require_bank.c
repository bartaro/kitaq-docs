// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/fds_overlay.h
u8 example_fds_require_bank(u8 bank) {
    return __fds_require_bank(bank);
}
