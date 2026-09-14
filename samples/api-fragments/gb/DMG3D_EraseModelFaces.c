// Usage fragment, not a standalone ROM.
// Declaration source: kitaqgb/lib/dmg3d.h
void example_DMG3D_EraseModelFaces(const Wire3DDMG_Model* model, w3ddmg_i16 x, w3ddmg_i16 y, w3ddmg_i16 z, w3ddmg_u8 rx, w3ddmg_u8 ry, w3ddmg_u8 rz, w3ddmg_i16 scale_q8) {
    DMG3D_EraseModelFaces(model, x, y, z, rx, ry, rz, scale_q8);
}
