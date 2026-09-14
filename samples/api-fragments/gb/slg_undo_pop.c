// Usage fragment, not a standalone ROM.
// Declaration source: kitaqgb/lib/slg.h
u8 example_slg_undo_pop(SLGUndoStack* stack, SLGMove* out_move) {
    return slg_undo_pop(stack, out_move);
}
