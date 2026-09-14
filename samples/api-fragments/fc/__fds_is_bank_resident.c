// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/fds_overlay.h
u8 example_fds_is_bank_resident(u8 bank) {
    return __fds_is_bank_resident(bank);
}
