#pragma bank 0
// Draw a frame with a gap, a projected diagonal, and a copied corner tile.
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
u8 projected_x;
u8 projected_y;
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
    Wire3DDMG_SetCamera(8,0,0,0,0,0);
    result[1]=Wire3DDMG_ProjectPoint(0,0,96,&projected_x,&projected_y);
    result[2]=projected_x; result[3]=projected_y;
    projected_x=91; projected_y=92;
    result[4]=Wire3DDMG_ProjectPoint(0,0,7,&projected_x,&projected_y);
    result[5]=projected_x; result[6]=projected_y;
    Wire3DDMG_SetCamera(0,0,0,0,0,0);
    Wire3DDMG_BeginFrame();
    Wire3DDMG_DrawLine2D(8,8,56,8);
    Wire3DDMG_DrawLine2D(56,8,56,40);
    Wire3DDMG_DrawLine2D(56,40,8,40);
    Wire3DDMG_DrawLine2D(8,40,8,8);
    Wire3DDMG_EraseSpan2D(8,40,24); // Inclusive endpoints are ordered internally.
    Wire3DDMG_DrawLine3D(-24,-24,96,24,24,96);
    // Copy the viewport's top-left frame corner to a separate map cell.
    Wire3DDMG_PutBgTile(1,1,160);
    Wire3DDMG_EndFrame();
    result[7]=0xA55A;
    while(1) {}
}
