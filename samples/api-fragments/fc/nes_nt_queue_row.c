// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/nametable_asset.h
unsigned char example_nes_nt_queue_row(unsigned short nt_base, unsigned char row, unsigned char* src32) {
    return nes_nt_queue_row(nt_base, row, src32);
}
