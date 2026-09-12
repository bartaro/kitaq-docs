// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc_project/kitaqfc/lib/intrinsics.h
void example_irq_restore(u8 state) {
    __irq_restore(state);
}
