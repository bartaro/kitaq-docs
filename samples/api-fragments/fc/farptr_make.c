// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/bank.h
void example_farptr_make(BankPtr* out, u8 bank, const u8* ptr) {
    farptr_make(out, bank, ptr);
}
