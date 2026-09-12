// Usage fragment, not a standalone ROM.
// Declaration source: lib/rpg.h
void example_memset_small(void* dst, u8 value, u8 len) {
    __memset_small(dst, value, len);
}
