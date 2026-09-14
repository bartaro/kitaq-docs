// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/intrinsics.h
void example_memcpy_small(u8* dst, const u8* src, u8 len) {
    __memcpy_small(dst, src, len);
}
