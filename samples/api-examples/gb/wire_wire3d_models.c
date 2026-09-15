#pragma bank 0
// Compare direct model scaling with an object-array scene.
// The selected 96-line profile determines the stage layout and camera center.
#define WIRE3D_DMG_HEIGHT 96
#include "wire3d.h"
__location(0xC110) u16 result[8];
__location(0xFF47) u8 sample_bgp;
__location(0xFF40) u8 sample_lcdc;
__location(0xFF44) u8 sample_ly;
__location(0xFF4F) u8 sample_vbk;
__location(0xFF68) u8 sample_bgpi;
__location(0xFF69) u8 sample_bgpd;
__prg_rom Wire3D_Vec3 vertices[8]={{-16,-16,-16},{16,-16,-16},{16,16,-16},{-16,16,-16},{-16,-16,16},{16,-16,16},{16,16,16},{-16,16,16}};
__prg_rom Wire3D_Edge edges[12]={{0,1},{1,2},{2,3},{3,0},{4,5},{5,6},{6,7},{7,4},{0,4},{1,5},{2,6},{3,7}};
Wire3D_Model cube;
Wire3D_Object objects[2];
u16 masks[2];
void main() {

    u8 i;
    for(i=0;i<8;i++) result[i]=0;
    Wire3D_Init();
    // A CGB-compatible ROM also needs CGB palette and tile-map attributes.
    if(__cgb_is_cgb()) {
        while(sample_ly>=144) {} while(sample_ly<144) {}
        sample_lcdc=0; sample_vbk=1;
        __vram_memset_unsafe(0x9800,0,1024); sample_vbk=0;
        sample_bgpi=0x80; sample_bgpd=255; sample_bgpd=127;
        for(i=0;i<6;i++) sample_bgpd=0;
        sample_lcdc=0x81;
    }
    Wire3D_SetPalette(0xFC); // White background; every nonzero shade is black.
    result[0]=sample_bgp;

    cube.vertices=vertices;cube.edges=edges;cube.faces=0;cube.edge_faces=0;
    cube.vertex_count=8;cube.edge_count=12;cube.face_count=0;cube.flags=0;
    cube.edge_masks=0; cube.edge_mask_count=0;
    Wire3D_BeginFrame();
    // Upper pair: direct model calls at unity and half scale.
    Wire3D_DrawModel(&cube,-32,32,96,0,0,0);
    Wire3D_DrawModelScaled(&cube,32,32,96,0,0,0,128);
    // Lower pair: the caller owns both object records and the model tables.
    for(i=0;i<2;i++) {
        objects[i].model=&cube;objects[i].x=-32+(s16)i*64;
        objects[i].y=-32;objects[i].z=96;
        objects[i].rx=0;objects[i].ry=0;objects[i].rz=0;
        objects[i].scale_q8=256-(s16)i*128;objects[i].visible=1;
    }
    Wire3D_DrawScene(objects,2);
    // Numeric checks cover the operation supplied by this viewport profile.
    masks[0]=3;masks[1]=12;cube.edge_masks=masks; cube.edge_mask_count=2;
    result[1]=Wire3D_SelectEdgeMask(&cube,0,0,0);
    result[2]=Wire3D_SelectEdgeMask(&cube,0,8,0);
    Wire3D_EndFrame(); result[7]=0xA55A;
    while(1) {}
}
