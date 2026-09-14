// Usage fragment, not a standalone ROM.
// Declaration source: kitaqgb/lib/slg.h
u8 example_slg_move_list_push(SLGMoveList* list, u8 x, u8 y, u8 value) {
    return slg_move_list_push(list, x, y, value);
}
