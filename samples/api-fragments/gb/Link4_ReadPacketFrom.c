// Usage fragment, not a standalone ROM.
// Declaration source: kitaqgb/lib/link.h
u8 example_Link4_ReadPacketFrom(u8 peer_slot, u8 *cmd, u8 *len, u8 *dst) {
    return Link4_ReadPacketFrom(peer_slot, cmd, len, dst);
}
