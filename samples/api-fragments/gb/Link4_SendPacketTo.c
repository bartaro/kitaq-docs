// Usage fragment, not a standalone ROM.
// Declaration source: kitaqgb/lib/link.h
u8 example_Link4_SendPacketTo(u8 peer_slot, const u8 *data, u8 len, u8 cmd) {
    return Link4_SendPacketTo(peer_slot, data, len, cmd);
}
