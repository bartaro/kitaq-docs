// Usage fragment, not a standalone ROM.
// Declaration source: kitaqgb/lib/bank.h
u8 example_far_data_read8(u8 bank, const void* addr) {
    return far_data_read8(bank, addr);
}
