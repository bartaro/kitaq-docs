// Learn direct PPU access, register/scroll control, attributes and both palette targets.
#include "fc_common.h"
__location(0x2006) u8 address_port;
__location(0x2007) u8 data_port;
__prg_rom u8 scene_palette[16]={0x0F,0x30,0x10,0x30,0x0F,0x16,0x16,0x16,0x0F,0x12,0x12,0x12,0x0F,0x1A,0x1A,0x1A};
__prg_rom u8 scene_attributes[64]={160,160,160,160,160,160,160,160,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,170,170,85,0,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
u8 pattern[32];u8 status_snapshot;
// Static labels use bounded queue batches while NMI and rendering are disabled.
void label(u8 y,const u8* text) {
    m_text(1,y,text);__vramq_commit();__vramq_exec();__scroll_set(0,0);
}
void main() {
    u8 i;
    m_init();m_wait();
    // example:__ppu_off:start
    __ppu_off(); // PPUMASK and its software shadow become zero; NMI is unchanged.
    __ppu_ctrl_set(0); // Disable NMI separately while preparing the whole scene.
    // example:__ppu_off:end
    // example:__palette_bg_load:start
    __palette_bg_load(scene_palette); // Four background palettes, 16 bytes total.
    // example:__palette_bg_load:end
    // example:__palette_sp_load:start
    __palette_sp_load(scene_palette); // Four sprite palettes, 16 bytes total.
    // example:__palette_sp_load:end
    __vram_write(0x23C0,scene_attributes,64);
    for(i=0;i<32;i++)pattern[i]=(u8)(i%3+1);
    // example:__vram_write:start
    __vram_write(0x2040,pattern,32); // Blue row: solid tile, left half, triangle.
    pattern[0]=3; // The completed transfer keeps its first solid tile.
    // example:__vram_write:end
    // example:__vram_fill:start
    __vram_fill(0x2060,2,32); // A second blue row of 4-pixel-wide left halves.
    // example:__vram_fill:end
    // example:__attr_set:start
    for(i=2;i<12;i=(u8)(i+4)) {
        __attr_set(i,6,0xFF);__attr_set(i,10,0xFF); // All quadrants select green.
    }
    // example:__attr_set:end
    // example:__attr_set_nt:start
    for(i=18;i<28;i=(u8)(i+4)) {
        __attr_set_nt(4,i,6,0x55);__attr_set_nt(4,i,10,0x55); // nt&3=0; red.
    }
    // example:__attr_set_nt:end
    // example:__nametable_rect:start
    __nametable_rect(2,6,8,4,1); // Solid green rectangle at (16,48), 64x32 pixels.
    // example:__nametable_rect:end
    // example:__nametable_rect_nt:start
    __nametable_rect_nt(4,18,6,8,4,3); // nt&3=0; red triangle tiles at (144,48).
    // example:__nametable_rect_nt:end
    // example:__nametable_put:start
    __nametable_put(2,12,1); // Blue solid marker at (16,96).
    // example:__nametable_put:end
    // example:__nametable_put_nt:start
    __nametable_put_nt(4,10,12,2); // Red left-half marker at (80,96), table 0.
    // example:__nametable_put_nt:end
    // example:__scroll_latch_reset:start
    address_port=0x21; // Leave the shared latch halfway through an address pair.
    __scroll_latch_reset();
    address_port=0x21;address_port=0x83;data_port=2; // Blue left-half marker.
    // example:__scroll_latch_reset:end
    // example:__ppu_read_status:start
    address_port=0x21;
    status_snapshot=__ppu_read_status(); // Also resets the shared write latch.
    address_port=0x21;address_port=0x84;data_port=3; // Blue triangle at (32,96).
    // example:__ppu_read_status:end
    // example:__ppu_addr:start
    address_port=0x21;
    __ppu_addr(0x2192); // Reset latch and set the cell at tile (18,12).
    // example:__ppu_addr:end
    // example:__ppu_data:start
    __ppu_data(3); // Green triangle at (144,96); destination advances by one.
    // example:__ppu_data:end
    // Sprite colors prove the separate sprite-palette load visually.
    __oam_clear();__sprite_set(0,16,143,1,1);
    __sprite_set(1,80,143,2,2);__sprite_set(2,144,143,3,3);__oam_dma();
    // example:__scroll_set:start
    __scroll_set(19,27); // Save both coordinates and write the two-scroll-byte pair.
    // example:__scroll_set:end
    // example:__scroll_x_set:start
    __scroll_x_set(0); // Keeps saved Y=27 while changing X to zero.
    // example:__scroll_x_set:end
    // example:__scroll_y_set:start
    __scroll_y_set(0); // Keeps saved X=0; the scene is now at the origin.
    // example:__scroll_y_set:end
    label(0,"PPU INTRINSICS");label(20,"TOP: BLUE COPY AND FILL");
    label(21,"MIDDLE: GREEN / RED");label(22,"LOWER: ADDRESS MARKERS");
    label(23,"SPRITES: RED BLUE GREEN");label(25,"PPU DRAWING EXAMPLE");
    // example:__ppu_ctrl_set:start
    __ppu_ctrl_set(0x80); // NMI enabled, increment 1, nametable/pattern tables 0.
    // example:__ppu_ctrl_set:end
    // example:__ppu_mask_set:start
    __ppu_mask_set(0x0A); // Background enabled, including its leftmost eight pixels.
    // example:__ppu_mask_set:end
    // example:__ppu_on:start
    __ppu_on(); // Replace mask with 0x1E: enable sprites and background at both edges.
    // example:__ppu_on:end
    while(1)m_wait();
}
