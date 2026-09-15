#pragma bank 0
// Compare direct model scaling with an object-array scene.
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
__prg_rom DMG3D_Vec3 vertices[8]={{-16,-16,-16},{16,-16,-16},{16,16,-16},{-16,16,-16},{-16,-16,16},{16,-16,16},{16,16,16},{-16,16,16}};
__prg_rom DMG3D_Edge edges[12]={{0,1},{1,2},{2,3},{3,0},{4,5},{5,6},{6,7},{7,4},{0,4},{1,5},{2,6},{3,7}};
DMG3D_Model cube;
DMG3D_Object objects[2];
s16 px; s16 py; s16 pz;
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

    cube.vertices=vertices;cube.edges=edges;cube.faces=0;cube.edge_faces=0;
    cube.vertex_count=8;cube.edge_count=12;cube.face_count=0;cube.flags=0;

    DMG3D_BeginFrame();
    // Upper pair: direct model calls at unity and half scale.
    DMG3D_DrawModel(&cube,-32,32,96,0,0,0);
    DMG3D_DrawModelScaled(&cube,32,32,96,0,0,0,128);
    // Lower pair: the caller owns both object records and the model tables.
    for(i=0;i<2;i++) {
        objects[i].model=&cube;objects[i].x=-32+(s16)i*64;
        objects[i].y=-32;objects[i].z=96;
        objects[i].rx=0;objects[i].ry=0;objects[i].rz=0;
        objects[i].scale_q8=256-(s16)i*128;objects[i].visible=1;
    }
    DMG3D_DrawScene(objects,2);
    // Numeric checks cover the operation supplied by this viewport profile.
    px=16;py=0;pz=0;DMG3D_RotatePoint(&px,&py,&pz,0,4,0);
    result[1]=px; result[2]=py; result[3]=pz;
    DMG3D_EndFrame(); result[7]=0xA55A;
    while(1) {}
}
