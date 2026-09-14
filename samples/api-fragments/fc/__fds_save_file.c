// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/fds_file.h
u8 example_fds_save_file(u8 id, const u8* src, u16 len) {
    return __fds_save_file(id, src, len);
}
