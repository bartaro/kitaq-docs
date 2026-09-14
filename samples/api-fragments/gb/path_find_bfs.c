// Usage fragment, not a standalone ROM.
// Declaration source: kitaqgb/lib/rpg.h
u8 example_path_find_bfs(u8 sx, u8 sy, u8 gx, u8 gy, u8* out_path, u8 max_len) {
    return path_find_bfs(sx, sy, gx, gy, out_path, max_len);
}
