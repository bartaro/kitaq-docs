// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/intrinsics.h
void example_midi_program_change(u8 ch, u8 program) {
    __midi_program_change(ch, program);
}
