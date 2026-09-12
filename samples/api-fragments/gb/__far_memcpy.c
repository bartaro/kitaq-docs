// Usage fragment, not a standalone ROM.
// Declaration source: lib/rpg.h
void example_far_memcpy(void* dst, u8 bank, const void* src, u16 len) {
    __far_memcpy(dst, bank, src, len);
}
