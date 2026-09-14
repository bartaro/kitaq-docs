// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/bank.h
void example_far_data_read(u8 bank, const void* addr, void* dst, u16 len) {
    far_data_read(bank, addr, dst, len);
}
