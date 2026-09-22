// Copyright (c) 2026 DAISUKE OBA. SPDX-License-Identifier: MIT
// Original cube, not model data from any commercial game.
#include "wire3d.c"
__location(0x0600) u16 wire_frames;
__location(0x0602) u8 wire_angle;
__location(0x0603) u8 wire_batches;
__location(0x0604) u8 wire_tiles;
__prg_rom const s8 cube_vertices[24]={
    -24,-24,-24, 24,-24,-24, 24,24,-24, -24,24,-24,
    -24,-24,24, 24,-24,24, 24,24,24, -24,24,24
};
__prg_rom const u8 cube_edges[24]={0,1,1,2,2,3,3,0,4,5,5,6,6,7,7,4,0,4,1,5,2,6,3,7};
void main(void) {
    Wire3DFC_Init();wire_frames=0;wire_angle=0;
    while(1) {
        Wire3DFC_BeginFrame();
        Wire3DFC_DrawModel((const Wire3DFC_Vec3*)cube_vertices,8,(const Wire3DFC_Edge*)cube_edges,12,0,0,96,0,wire_angle,0);
        Wire3DFC_EndFrame();
        wire_batches=wire3d_transfer_frames;wire_tiles=wire3d_uploaded_tiles;
        wire_frames++;wire_angle=(u8)((wire_angle+1)&31);
    }
}
