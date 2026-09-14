// Show actual CGB GDMA, HBlank DMA and cancellation using original 8x8 shapes.
// Build as a dual-mode ROM. DMG displays only the software-written sentinels.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
void __cgb_safe_set_hdma1(u8 value);
void __cgb_safe_set_hdma2(u8 value);
void __cgb_safe_set_hdma3(u8 value);
void __cgb_safe_set_hdma4(u8 value);
void __cgb_safe_set_hdma5(u8 value);
void __cgb_safe_set_svbk(u8 value);
__location(0xFF55) u8 D_CONTROL;
// The transfer source is explicitly aligned and lives in fixed WRAM bank 0.
__location(0xC600) u8 transfer[64];
const u8 patterns[64]={
    128,128,192,192,224,224,240,240,248,248,252,252,254,254,255,255,
    255,255,129,129,129,129,129,129,129,129,129,129,129,129,255,255,
    240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,
    255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255
};
u8 failures;
u8 color_mode;
u8 canceled_status;

// Compare VRAM bytes with fixed-WRAM source bytes only while the LCD is stopped.
void compare_bytes(u16 address,u8 start,u8 count) {
    u8 i;
    u8* destination=(u8*)address;
    for (i=0;i<count;i++) {
        if (*(destination+i)!=transfer[(__safe_index u8)(start+i)]) failures++;
    }
}

void main() {
    u8 i;
    tile_example_begin();
    color_mode=__cgb_is_cgb();
    __cgb_safe_set_svbk(1); // This program uses fixed WRAM and a fixed stack.
    for(i=0;i<64;i++) transfer[(__safe_index u8)i]=patterns[(__safe_index u8)i];
    __vram_fill(0x8010,0,96);
    // Preserve these two shapes through a canceled transfer: half tile, solid tile.
    __vram_copy(0x8050,patterns+32,32);
    // example:__cgb_safe_set_hdma1:start
    __cgb_safe_set_hdma1(0xC6); // Source high byte: fixed-WRAM buffer at $C600.
    // example:__cgb_safe_set_hdma1:end
    // example:__cgb_safe_set_hdma2:start
    __cgb_safe_set_hdma2(0x0F); // Low four bits are ignored by hardware: source remains $C600.
    // example:__cgb_safe_set_hdma2:end
    // example:__cgb_safe_set_hdma3:start
    __cgb_safe_set_hdma3(0xE0); // Only low five bits select the high VRAM offset.
    // example:__cgb_safe_set_hdma3:end
    // example:__cgb_safe_set_hdma4:start
    __cgb_safe_set_hdma4(0x1F); // Destination aligns to $8010, not $801F.
    // example:__cgb_safe_set_hdma4:end
    // example:__cgb_safe_set_hdma5:start
    __cgb_safe_set_hdma5(1); // LCD is off: GDMA, (1+1)*16 = 32 bytes.
    if (color_mode && D_CONTROL!=255) failures++;
    // example:__cgb_safe_set_hdma5:end
    if (color_mode) compare_bytes(0x8010,0,32);
    else {
        for(i=0;i<32;i++) if (*((u8*)(0x8010+i))!=0) failures++;
    }
    __settile_unsafe(2,3,1); __settile_unsafe(3,3,2);
    __settile_unsafe(2,6,3); __settile_unsafe(3,6,4);
    __settile_unsafe(2,9,5); __settile_unsafe(3,9,6);
    vram_example_color(2,3,2,1,1); // Red GDMA row.
    vram_example_color(2,6,2,1,2); // Blue HBlank-DMA row.
    vram_example_color(2,9,2,1,3); // Green unchanged sentinels.
    M_LCDC=0x91;
    m_wait(); // Start in VBlank, not in HBlank (STAT mode 0).
    __cgb_safe_set_hdma1(0xC6); __cgb_safe_set_hdma2(0x20);
    __cgb_safe_set_hdma3(0); __cgb_safe_set_hdma4(0x30);
    __cgb_safe_set_hdma5(0x81); // Two blocks, one on each of the next two visible HBlanks.
    if (color_mode) {
        while ((D_CONTROL&128)==0) { } // Busy poll: HALT would also pause HBlank DMA.
        if (D_CONTROL!=255) failures++;
    }
    m_wait(); M_LCDC=0;
    if (color_mode) compare_bytes(0x8030,32,32);
    else {
        for(i=0;i<32;i++) if (*((u8*)(0x8030+i))!=0) failures++;
    }
    M_LCDC=0x91;
    m_wait(); // Arm and cancel entirely within VBlank, before the first HBlank block.
    __cgb_safe_set_hdma1(0xC6); __cgb_safe_set_hdma2(0);
    __cgb_safe_set_hdma3(0); __cgb_safe_set_hdma4(0x50);
    __cgb_safe_set_hdma5(0x81);
    __cgb_safe_set_hdma5(0); // Cancel the active HBlank transfer; do not start GDMA here.
    if (color_mode) {
        canceled_status=D_CONTROL;
        if (canceled_status!=0x81) failures++; // Inactive, two blocks remaining.
    }
    m_wait(); M_LCDC=0;
    compare_bytes(0x8050,32,32); // A full intervening frame must leave the sentinels unchanged.
    M_LCDC=0x91;
    m_text(1,0,"CGB DMA SHAPES");
    m_text(6,3,"GDMA 32B");
    m_text(6,6,"HDMA 32B");
    m_text(6,9,"CANCELED");
    m_text(1,12,"CGB MODE"); m_put(16,12,(u8)('0'+color_mode));
    m_text(1,15,"FAILED CHECKS");
    m_put(16,15,(u8)('0'+failures/100));
    m_put(17,15,(u8)('0'+(failures/10)%10));
    m_put(18,15,(u8)('0'+failures%10));
    while(1) { m_wait(); }
}
