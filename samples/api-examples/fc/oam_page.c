#include "fc_oam_example.h"
__location(0x0400) u8 alternate_oam[256];
void main() {
    u16 i;
    fc_oam_prepare();fc_oam_labels();
    // Keep page 02 intact and make a separate complete page at address 0x0400.
    for(i=0;i<256;i++)alternate_oam[i]=*((u8*)(0x0200+i));
    alternate_oam[29]=129; // Entry 7 tile: a green square instead of the page-02 arrow.
    __oam_dma_page(4);__ppu_ctrl_set(0x80);__ppu_mask_set(0x1E);
    while(1) {
        // example:__oam_dma_page:start
        m_wait();__oam_dma_page(4); // The argument is a page number, not 0x0400.
        // example:__oam_dma_page:end
    }
}
