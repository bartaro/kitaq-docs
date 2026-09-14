// Usage fragment, not a standalone ROM.
// Declaration source: kitaqgb/lib/link.h
u8 example_Link_ReadPacket(u8 *cmd, u8 *len, u8 *dst) {
    return Link_ReadPacket(cmd, len, dst);
}
