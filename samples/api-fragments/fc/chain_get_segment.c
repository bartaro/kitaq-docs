// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/chain.h
u8 example_chain_get_segment(const Chain* chain, u8 index, ChainPoint* out) {
    return chain_get_segment(chain, index, out);
}
