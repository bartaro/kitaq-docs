#pragma bank 0
// Remove the previous frame and upload only the tracked current/previous tiles.
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
        DMG3D_SetDirtyTransfer(1); DMG3D_SetAuxTransfer(0);
    DMG3D_BeginFrame();
    DMG3D_DrawLine2D(8,8,24,8); DMG3D_DrawLine2D(24,8,24,24);
    DMG3D_DrawLine2D(24,24,8,24); DMG3D_DrawLine2D(8,24,8,8);
    DMG3D_EndFrame();
    DMG3D_BeginFrame();
    DMG3D_DrawLine2D(80,80,104,80); DMG3D_DrawLine2D(104,80,104,104);
    DMG3D_DrawLine2D(104,104,80,104); DMG3D_DrawLine2D(80,104,80,80);

    DMG3D_EndFrame(); result[7]=0xA55A; while(1) {}
}
