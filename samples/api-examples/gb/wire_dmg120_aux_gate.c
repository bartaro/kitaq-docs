#pragma bank 0
// Use the auxiliary-transfer gate to consume an overlapping stage strip.
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
        Wire3DDMG_SetDirtyTransfer(1); Wire3DDMG_SetAuxTransfer(1);
    Wire3DDMG_BeginFrame();
    for(i=24;i<=31;i++) Wire3DDMG_DrawLine2D(40,i,47,i);
    // Auxiliary upload consumes this source before the dirty main tile is sent.

    Wire3DDMG_EndFrame(); result[7]=0xA55A; while(1) {}
}
