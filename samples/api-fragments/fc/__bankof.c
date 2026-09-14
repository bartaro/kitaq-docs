// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/intrinsics.h
u8 example_bankof(u16 symbol_or_function) {
    return __bankof(symbol_or_function);
}
