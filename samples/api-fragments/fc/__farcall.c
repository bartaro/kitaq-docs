// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/intrinsics.h
u8 example_farcall(u8 bank, u16 func) {
    return __farcall(bank, func);
}
