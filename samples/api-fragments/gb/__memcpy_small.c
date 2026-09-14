// Usage fragment, not a standalone ROM.
// Declaration source: kitaqgb/lib/rpg.h
void example_memcpy_small(void* dst, const void* src, u8 len) {
    __memcpy_small(dst, src, len);
}
