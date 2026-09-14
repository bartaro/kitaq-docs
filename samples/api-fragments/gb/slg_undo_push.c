// Usage fragment, not a standalone ROM.
// Declaration source: kitaqgb/lib/slg.h
u8 example_slg_undo_push(SLGUndoStack* stack, u8 x, u8 y, u8 old_value) {
    return slg_undo_push(stack, x, y, old_value);
}
