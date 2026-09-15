#include "fc_oam_example.h"
void main() {
    fc_oam_prepare();fc_oam_labels();
    // Initial transfer with rendering disabled.
    __oam_dma();__ppu_ctrl_set(0x80);__ppu_mask_set(0x1E);
    while(1) {
        // example:__oam_dma:start
        m_wait();__oam_dma(); // Transfer all 256 bytes from page 02 at VBlank.
        // example:__oam_dma:end
    }
}
