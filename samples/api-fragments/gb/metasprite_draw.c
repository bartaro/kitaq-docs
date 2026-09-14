// Usage fragment, not a standalone ROM.
// Declaration source: kitaqgb/lib/sprite.h
u8 example_metasprite_draw(u8 first_id, u8 x, u8 y, const MetaSpritePart* parts, u8 count) {
    return metasprite_draw(first_id, x, y, parts, count);
}
