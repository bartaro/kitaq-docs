// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/fds_file.h
u8 example_fds_load_file(u8 id, u8* dst) {
    return __fds_load_file(id, dst);
}
