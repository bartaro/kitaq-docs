// Copyright (c) 2026 DAISUKE OBA. SPDX-License-Identifier: MIT
// Learn the difference between model coordinates, camera-space projection and
// viewport pixels. Expect a cyan border, cube, upper cross and lower 3D line.
// Define both WIRE3D_FC_WIDTH/HEIGHT before this include to select another size.
#include "wire3d.c"
__location(0x0600) u16 wire_result[8];
__prg_rom const Wire3DFC_Vec3 example_vertices[8]={
    {-12,-12,-12},{12,-12,-12},{12,12,-12},{-12,12,-12},
    {-12,-12,12},{12,-12,12},{12,12,12},{-12,12,12}
};
__prg_rom const Wire3DFC_Edge example_edges[12]={
    {0,1},{1,2},{2,3},{3,0},{4,5},{5,6},{6,7},{7,4},
    {0,4},{1,5},{2,6},{3,7}
};

void main(void) {
    s16 px,py,pz,sx,sy;
    u8 projected;
    // Init owns CHR RAM, nametable zero and palette; keep other PPU writers off.
    Wire3DFC_Init();
    Wire3DFC_BeginFrame();

    // Viewport coordinates: draw a border without any camera projection.
    Wire3DFC_DrawLine2D(0,0,WIRE3D_FC_WIDTH-1,0);
    Wire3DFC_DrawLine2D(WIRE3D_FC_WIDTH-1,0,WIRE3D_FC_WIDTH-1,WIRE3D_FC_HEIGHT-1);
    Wire3DFC_DrawLine2D(WIRE3D_FC_WIDTH-1,WIRE3D_FC_HEIGHT-1,0,WIRE3D_FC_HEIGHT-1);
    Wire3DFC_DrawLine2D(0,WIRE3D_FC_HEIGHT-1,0,0);

    // Rotate (24,0,0) a quarter turn about Z to (0,24,0). A full turn is 32.
    px=24;py=0;pz=0;
    Wire3DFC_RotatePoint(&px,&py,&pz,0,0,8);
    wire_result[0]=px;wire_result[1]=py;wire_result[2]=pz;
    // Translate away from the camera before projecting. Positive Y goes up.
    projected=Wire3DFC_ProjectPoint(px,py,pz+96,&sx,&sy);
    wire_result[3]=projected;wire_result[4]=sx;wire_result[5]=sy;
    if(projected) {
        Wire3DFC_DrawLine2D(sx-3,sy,sx+3,sy);
        Wire3DFC_DrawLine2D(sx,sy-3,sx,sy+3);
    }

    // Both endpoints are already camera-space coordinates; no model rotation.
    Wire3DFC_DrawLine3D(-24,-24,96,24,-24,96);
    // Model vertices are transformed once, then reused by the twelve edges.
    Wire3DFC_DrawModel(example_vertices,8,example_edges,12,0,0,96,0,3,0);
    // This blocking call uploads the hidden CHR table, then makes it visible.
    Wire3DFC_EndFrame();
    wire_result[6]=wire3d_uploaded_tiles;
    wire_result[7]=0xA55A;
    while(1) {}
}
