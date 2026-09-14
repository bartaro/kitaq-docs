// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/audio.h
void example_nes_dmc_play(u8 flags_rate, u8 output_level, u16 sample_addr, u16 sample_len) {
    nes_dmc_play(flags_rate, output_level, sample_addr, sample_len);
}
