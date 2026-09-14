// Usage fragment, not a standalone ROM.
// Declaration source: kitaqgb/lib/bank.h
void example_far_call(u8 bank, const void* func) {
    far_call(bank, func);
}
