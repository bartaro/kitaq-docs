#include "fc_oam_alias_example.h"
// nes_game.h selects the zero-argument macros; no C runtime source is linked.
void main() {
    fc_oam_alias_prepare();fc_oam_alias_labels();
    nes_oam_dma();__ppu_ctrl_set(0x80);__ppu_mask_set(0x1E);
    while(1) {
        // example:nes_oam_dma:start
        m_wait();nes_oam_dma(); // Expand to the page-02 compiler intrinsic.
        // example:nes_oam_dma:end
    }
}
