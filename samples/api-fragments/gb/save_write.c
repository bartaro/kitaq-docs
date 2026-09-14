// Usage fragment, not a standalone ROM.
// Declaration source: kitaqgb/lib/rpg.h
u8 example_save_write(u8 slot, const void* data, u16 len) {
    return save_write(slot, data, len);
}
