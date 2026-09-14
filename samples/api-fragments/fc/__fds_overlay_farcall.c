// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/fds_overlay.h
u8 example_fds_overlay_farcall(u8 bank, u16 func) {
    return __fds_overlay_farcall(bank, func);
}
