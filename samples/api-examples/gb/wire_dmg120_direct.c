#pragma bank 0
// Upload a main line and an auxiliary block separately; verify source consumption.
// The selected 120-line profile determines the stage layout and camera center.
#define WIRE3D_DMG_HEIGHT 120
#include "wire3d_dmg.h"
__location(0xC110) u16 result[8];
__location(0xFF47) u8 sample_bgp;
__location(0xFF40) u8 sample_lcdc;
__location(0xFF44) u8 sample_ly;
__location(0xFF4F) u8 sample_vbk;
__location(0xFF68) u8 sample_bgpi;
__location(0xFF69) u8 sample_bgpd;
__prg_rom Wire3DDMG_Vec3 vertices[2]={{-32,0,0},{32,0,0}};
__prg_rom u8 edge_pairs[2]={0,1};
u8* stage_byte;

void main() {

    u8 i;
    for(i=0;i<8;i++) result[i]=0;
    Wire3DDMG_Init();
    // A CGB-compatible ROM also needs CGB palette and tile-map attributes.
    if(__cgb_is_cgb()) {
        while(sample_ly>=144) {} while(sample_ly<144) {}
        sample_lcdc=0; sample_vbk=1;
        __vram_memset_unsafe(0x9800,0,1024); sample_vbk=0;
        sample_bgpi=0x80; sample_bgpd=255; sample_bgpd=127;
        for(i=0;i<6;i++) sample_bgpd=0;
        sample_lcdc=0x81;
    }
    Wire3DDMG_SetPalette(0xFC); // White background; every nonzero shade is black.
    result[0]=sample_bgp;
        Wire3DDMG_BeginFrame();
    Wire3DDMG_DrawIndexedEdges(vertices,2,edge_pairs,1,-64,104,96,1);
    Wire3DDMG_TransferMainNow();
    // Direct auxiliary transfer writes a separate tile after the main upload.
    for(i=24;i<=31;i++) Wire3DDMG_DrawLine2D(40,i,47,i);
    stage_byte=(u8*)0xD518;result[1]=*stage_byte;
    Wire3DDMG_TransferAuxNow();result[2]=*stage_byte;

    // Do not upload the consumed stage again.
    result[7]=0xA55A; while(1) {}
}
