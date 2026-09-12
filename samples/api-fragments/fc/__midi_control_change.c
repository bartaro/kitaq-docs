// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc_project/kitaqfc/lib/intrinsics.h
void example_midi_control_change(u8 ch, u8 cc, u8 value) {
    __midi_control_change(ch, cc, value);
}
