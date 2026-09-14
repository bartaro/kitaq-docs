// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/intrinsics.h
void example_midi_note_off(u8 ch, u8 note, u8 velocity) {
    __midi_note_off(ch, note, velocity);
}
