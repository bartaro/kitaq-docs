#pragma bank 0
// Erase a screen triangle and a projected model face from separate filled panels.
// The selected 120-line profile determines the stage layout and camera center.
#define WIRE3D_DMG_HEIGHT 120
#include "dmg3d.h"
__location(0xC110) u16 result[8];
__location(0xFF47) u8 sample_bgp;
__location(0xFF40) u8 sample_lcdc;
__location(0xFF44) u8 sample_ly;
__location(0xFF4F) u8 sample_vbk;
__location(0xFF68) u8 sample_bgpi;
__location(0xFF69) u8 sample_bgpd;
__prg_rom DMG3D_Vec3 vertices[4]={{-24,-24,0},{24,-24,0},{24,24,0},{-24,24,0}};
__prg_rom DMG3D_Edge edges[4]={{0,1},{1,2},{2,3},{3,0}};
__prg_rom DMG3D_Face faces[2]={{0,2,1},{0,3,2}};
DMG3D_Model plane;

void main() {

    u8 i;
    for(i=0;i<8;i++) result[i]=0;
    DMG3D_Init();
    // A CGB-compatible ROM also needs CGB palette and tile-map attributes.
    if(__cgb_is_cgb()) {
        while(sample_ly>=144) {} while(sample_ly<144) {}
        sample_lcdc=0; sample_vbk=1;
        __vram_memset_unsafe(0x9800,0,1024); sample_vbk=0;
        sample_bgpi=0x80; sample_bgpd=255; sample_bgpd=127;
        for(i=0;i<6;i++) sample_bgpd=0;
        sample_lcdc=0x81;
    }
    DMG3D_SetPalette(0xFC); // White background; every nonzero shade is black.
    result[0]=sample_bgp;
        plane.vertices=vertices;plane.edges=edges;plane.faces=faces;plane.edge_faces=0;
    plane.vertex_count=4;plane.edge_count=4;plane.face_count=2;plane.flags=1;
    DMG3D_BeginFrame();
    // Separate panels show a direct screen triangle and a projected square face.
    for(i=8;i<=32;i++) DMG3D_DrawLine2D(8,i,32,i);
    for(i=36;i<=84;i++) DMG3D_DrawLine2D(40,i,88,i);
    DMG3D_EraseTriangle2D(12,12,28,12,12,28);
    DMG3D_EraseModelFaces(&plane,0,0,64,0,0,0,256);

    DMG3D_EndFrame(); result[7]=0xA55A; while(1) {}
}
