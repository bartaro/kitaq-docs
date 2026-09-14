// Usage fragment, not a standalone ROM.
// Declaration source: kitaqfc/lib/actor.h
unsigned char example_nes_actor_draw_metasprite(struct NesActor* actor, unsigned char oam_index, unsigned char* metasprite) {
    return nes_actor_draw_metasprite(actor, oam_index, metasprite);
}
