// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/bank.h
u16 example_far_data_read16(u8 bank, const void* addr) {
    return far_data_read16(bank, addr);
}
