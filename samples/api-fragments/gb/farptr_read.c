// Usage fragment, not a standalone ROM.
// Declaration source: kitaqgb/lib/bank.h
void example_farptr_read(BankPtr ptr, void* dst, u16 len) {
    farptr_read(ptr, dst, len);
}
