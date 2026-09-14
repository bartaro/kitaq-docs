// Learn fixed-pool allocation, checked lookup, release, ID reuse and callback dispatch.
// The labeled counts explain each stage; A and B mark the two active entities.
#include "gb_tile_example.h"

#include "entity.h"
u8 update_calls;
u8 draw_calls;
// Keep the observations in named state so the FC function's scratch use stays small.
u8 first;
u8 second;
u8 created;
u8 after_free;
u8 reused;
u8 after_clear;
u8 automatic_updates;
u8 automatic_draws;
u8 failures;
Entity* current_entity;

// This example chooses tile coordinates as the game's position unit.
void demo_update(u8 id) {
    Entity* entity;
    entity = entity_get(id);
    if (entity != 0) { entity->x = entity->x + 1; update_calls++; }
}

// The callback places a font character; the pool itself does not draw it.
void demo_draw(u8 id) {
    Entity* entity;
    entity = entity_get(id);
    if (entity != 0) {
        m_put((u8)entity->x, (u8)entity->y, (u8)('A' + entity->type - 1));
        draw_calls++;
    }
}

// Flush each short label/value row so the FC command queue cannot overflow.
void show_count(u8 row, const u8* label, u8 value) {
    m_text(2,row,label);
    m_put(15,row,(u8)('0'+value/100));
    m_put(16,row,(u8)('0'+(value/10)%10));
    m_put(17,row,(u8)('0'+value%10));
    m_wait();
}

void main() {
    failures = 0;
#ifdef ENTITY_EXAMPLE_FC
    m_init();
#else
    tile_example_begin(); M_LCDC = 0x91;
#endif
    // Start with an empty pool, then allocate two logical objects.
    // example:entity_init:start
    entity_init();
    if (entity_count_active() != 0) { failures++; }
    // example:entity_init:end
    // example:entity_create:start
    first = entity_create(1, 2, 12);
    second = entity_create(2, 6, 12);
    if (first == 0xFF || second == 0xFF) { failures++; }
    // example:entity_create:end
    // example:entity_count_active:start
    created = entity_count_active();
    if (created != 2) { failures++; }
    // example:entity_count_active:end
    // example:entity_get:start
    current_entity = entity_get(first);
    if (current_entity != 0) { current_entity->vx = 5; }
    else { failures++; }
    // example:entity_get:end
    // Free the first slot and show that its old ID no longer looks up an object.
    // example:entity_destroy:start
    entity_destroy(first);
    after_free = entity_count_active();
    if (entity_get(first) != 0 || after_free != 1) { failures++; }
    // example:entity_destroy:end
    reused = entity_create(3, 4, 12);
    current_entity = entity_get(reused);
    if (reused != first || current_entity == 0) { failures++; }
    else {
        // Reallocation resets fields; the old object's velocity is not retained.
        if (current_entity->vx != 0 || current_entity->sprite != 0xFF) { failures++; }
    }
    // example:entity_clear_all:start
    entity_clear_all();
    after_clear = entity_count_active();
    if (after_clear != 0 || entity_get(reused) != 0) { failures++; }
    // example:entity_clear_all:end

    // Give the callbacks two objects to process and display.
    first = entity_create(1, 2, 12);
    second = entity_create(2, 6, 12);
    // example:entity_update_all:start
    update_calls = 0;
    entity_update_all(demo_update);
    automatic_updates = update_calls;
    if (automatic_updates != 2) { failures++; }

    // example:entity_update_all:end
    if (update_calls != 2) { failures++; }
    // example:entity_draw_all:start
    draw_calls = 0;
    entity_draw_all(demo_draw);
    automatic_draws = draw_calls;
    if (automatic_draws != 2) { failures++; }

    // example:entity_draw_all:end
    if (draw_calls != 2) { failures++; }
    m_wait();
    m_text(2,0,"ENTITY POOL"); m_wait();
    show_count(2,"CREATED",created);
    show_count(3,"AFTER FREE",after_free);
    show_count(4,"REUSED ID",reused);
    show_count(5,"AFTER CLEAR",after_clear);
    show_count(7,"UPDATE CALLS",automatic_updates);
    show_count(8,"DRAW CALLS",automatic_draws);
    m_text(2,10,"ENTITIES A B"); m_wait();
    show_count(15,"FAILED CHECKS",failures);
    while (1) { m_wait(); }
}
