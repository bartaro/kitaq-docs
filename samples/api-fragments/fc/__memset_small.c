// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/intrinsics.h
void example_memset_small(u8* dst, u8 value, u8 len) {
    __memset_small(dst, value, len);
}
