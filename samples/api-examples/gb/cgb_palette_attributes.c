// Demonstrate palette addressing, RGB packing, register aliases and tile attributes.
// All palette, VRAM and OAM setup occurs with the LCD off. The 92-glyph font
// comes from gb_common.h; the two asymmetric tile patterns below are original.
#include "gb_tile_example.h"
#include "cgb_palette.c"

void __cgb_safe_set_bgpi(u8 value);
void __cgb_safe_set_bgpd(u8 value);
void __cgb_safe_set_obpi(u8 value);
void __cgb_safe_set_obpd(u8 value);
__location(0xFF6A) u8 P_OBPI;
__location(0xFF6B) u8 P_OBPD;
__location(0xFF4F) u8 P_VBK;

const u8 shape0[16] = {128,128,192,192,224,224,240,240,248,248,252,252,254,254,255,255};
const u8 shape1[16] = {255,255,129,129,129,129,129,129,129,129,129,129,129,129,255,255};
const u8 solid[16] = {255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255};
const u16 neutral[4] = {32767,0,0,0};
const u16 red_palette[4] = {32767,0,0,31};
const u16 blue_palette[4] = {32767,0,0,31744};
const u16 tail_green[2] = {0,992};
const u16 tail_red[2] = {0,31};
const u16 blue_word[1] = {31744};
const u16 green_word[1] = {992};
const u16 boundary[3] = {31,31744,992};
u8 failures;
u8 color_mode;
u8 component;
u8 enabled;

// Read a complete color without auto-increment; these reads are CGB-only and LCD-off.
u16 read_color(u8 object, u8 slot) {
    u8 low;
    u8 high;
    if (object) {
        P_OBPI=(u8)(slot*2); low=P_OBPD;
        P_OBPI=(u8)(slot*2+1); high=P_OBPD;
    } else {
        T_BGPI=(u8)(slot*2); low=T_BGPD;
        T_BGPI=(u8)(slot*2+1); high=T_BGPD;
    }
    return (u16)((u16)low | ((u16)high<<8));
}

// Check the palette word only when that store is present on the running machine.
void expect_color(u8 object, u8 slot, u16 expected) {
    if (color_mode && read_color(object,slot)!=expected) failures++;
}

// Populate one map cell and its CGB attributes through an explicit address.
void cell(u8 x,u8 y,u8 tile,u8 attr) {
    u16 address=(u16)(0x9800+(u16)y*32+x);
    __cgb_safe_set_vbk(0); *((u8*)address)=tile;
    if (color_mode) {
        __cgb_safe_set_vbk(1); *((u8*)address)=attr;
        __cgb_safe_set_vbk(0);
    }
}

// OAM coordinates include the hardware offsets: screen X+8 and Y+16.
void sprite(u8 index,u8 x,u8 y,u8 tile,u8 attr) {
    u8* entry=(u8*)(0xFE00+(u16)index*4);
    *entry=(u8)(y+16); *(entry+1)=(u8)(x+8);
    *(entry+2)=tile; *(entry+3)=attr;
}

void main() {
    u8 i;
    u8 before;
    u8 attr;
    tile_example_begin();
    // example:__cgb_is_cgb:start
    color_mode=__cgb_is_cgb(); // 0 in DMG mode, 1 in CGB mode for this dual-mode ROM.
    if (color_mode>1) failures++;
    // example:__cgb_is_cgb:end
    component=63; enabled=2;
    // example:CGB_RGB15:start
    if (CGB_RGB15(component,64,95)!=31775) failures++; // (31,0,31), not saturation.
    // example:CGB_RGB15:end
    // example:cgb_rgb15:start
    if (cgb_rgb15(component,64,95)!=31775) failures++; // Same packed value through a function.
    // example:cgb_rgb15:end

    // Test wrapping, cross-palette writes, clamping and empty input before drawing.
    for (i=0;i<8;i++) { cgb_bg_palette(i,neutral); cgb_obj_palette(i,neutral); }
    cgb_bg_color(9,7,31); expect_color(0,7,31);
    cgb_obj_color(9,7,31744); expect_color(1,7,31744);
    cgb_bg_colors(6,3,boundary,3);
    cgb_obj_colors(6,3,boundary,3);
    expect_color(0,27,31); expect_color(0,28,31744); expect_color(0,29,992);
    expect_color(1,27,31); expect_color(1,28,31744); expect_color(1,29,992);
    cgb_bg_colors_raw(63,boundary,3); cgb_obj_colors_raw(63,boundary,3);
    expect_color(0,31,31); expect_color(1,31,31);
    expect_color(0,0,32767); expect_color(1,0,32767); // No wrap from slot 31 to zero.
    if (color_mode) {
        before=T_BGPI;
        cgb_bg_colors_raw(12,0,3); cgb_bg_colors_raw(12,boundary,0);
        if (T_BGPI!=before) failures++;
        before=P_OBPI;
        cgb_obj_colors_raw(12,0,3); cgb_obj_colors_raw(12,boundary,0);
        if (P_OBPI!=before) failures++;
    }
    for (i=0;i<8;i++) { cgb_bg_palette(i,neutral); cgb_obj_palette(i,neutral); }

    // Each column uses a different API; BG and OBJ palettes are independent.
    // example:cgb_bg_color:start
    cgb_bg_color(1,3,31); // Red background color 3 of palette 1.
    expect_color(0,7,31);
    // example:cgb_bg_color:end
    // example:cgb_obj_color:start
    cgb_obj_color(1,3,31744); // Blue sprite color at the same palette/color indices.
    expect_color(1,7,31744);
    // example:cgb_obj_color:end
    // example:cgb_bg_rgb:start
    cgb_bg_rgb(2,3,0,0,31); // Blue, supplied as three five-bit components.
    expect_color(0,11,31744);
    // example:cgb_bg_rgb:end
    // example:cgb_obj_rgb:start
    cgb_obj_rgb(2,3,0,31,0); // Green sprite color.
    expect_color(1,11,992);
    // example:cgb_obj_rgb:end
    // example:cgb_bg_colors:start
    cgb_bg_colors(3,2,tail_green,2); // Two color words; color 3 becomes green.
    expect_color(0,14,0); expect_color(0,15,992);
    // example:cgb_bg_colors:end
    // example:cgb_obj_colors:start
    cgb_obj_colors(3,2,tail_red,2); // Sprite color 3 becomes red.
    expect_color(1,14,0); expect_color(1,15,31);
    // example:cgb_obj_colors:end
    // example:cgb_bg_palette:start
    cgb_bg_palette(4,red_palette); // Exactly four color words for BG palette 4.
    expect_color(0,16,32767); expect_color(0,19,31);
    // example:cgb_bg_palette:end
    // example:cgb_obj_palette:start
    cgb_obj_palette(4,blue_palette); // Exactly four words; OBJ color zero is transparent on screen.
    expect_color(1,16,32767); expect_color(1,19,31744);
    // example:cgb_obj_palette:end
    // example:cgb_bg_colors_raw:start
    cgb_bg_colors_raw(23,blue_word,1); // Absolute slot 23 = palette 5, color 3.
    expect_color(0,23,31744);
    // example:cgb_bg_colors_raw:end
    // example:cgb_obj_colors_raw:start
    cgb_obj_colors_raw(23,green_word,1); // Same absolute slot in the separate OBJ store.
    expect_color(1,23,992);
    // example:cgb_obj_colors_raw:end
    // example:__cgb_safe_set_bcps:start
    __cgb_safe_set_bcps(0xB6); // BG byte 54, with auto-increment enabled (slot 27 low byte).
    // example:__cgb_safe_set_bcps:end
    // example:__cgb_safe_set_bcpd:start
    __cgb_safe_set_bcpd(0xE0); __cgb_safe_set_bcpd(0x03); // Green word 0x03E0, low then high.
    expect_color(0,27,992);
    // example:__cgb_safe_set_bcpd:end
    // example:__cgb_safe_set_ocps:start
    __cgb_safe_set_ocps(0xB6); // OBJ byte 54; this does not select a BG color.
    // example:__cgb_safe_set_ocps:end
    // example:__cgb_safe_set_ocpd:start
    __cgb_safe_set_ocpd(31); __cgb_safe_set_ocpd(0); // Red sprite color.
    expect_color(1,27,31);
    // example:__cgb_safe_set_ocpd:end
    // example:__cgb_safe_set_bgpi:start
    __cgb_safe_set_bgpi(0xBE); // Alias of BCPS: BG byte 62, auto-increment enabled.
    // example:__cgb_safe_set_bgpi:end
    // example:__cgb_safe_set_bgpd:start
    __cgb_safe_set_bgpd(31); __cgb_safe_set_bgpd(0); // Alias of BCPD: red at slot 31.
    expect_color(0,31,31);
    // example:__cgb_safe_set_bgpd:end
    // example:__cgb_safe_set_obpi:start
    __cgb_safe_set_obpi(0xBE); // Alias of OCPS: select the OBJ store's last word.
    // example:__cgb_safe_set_obpi:end
    // example:__cgb_safe_set_obpd:start
    __cgb_safe_set_obpd(0); __cgb_safe_set_obpd(0x7C); // Alias of OCPD: blue at slot 31.
    expect_color(1,31,31744);
    // example:__cgb_safe_set_obpd:end

    // Load different shapes at the same tile number in the two VRAM banks.
    __vram_copy(0x8010,shape0,16); __vram_copy(0x8020,solid,16);
    // example:__cgb_safe_set_vbk:start
    if (color_mode) {
        __cgb_safe_set_vbk(3); // Only bit zero is kept: CPU accesses now use bank 1.
        if ((P_VBK&1)!=1) failures++;
        __vram_copy(0x8010,shape1,16);
        __cgb_safe_set_vbk(2); // Bit zero is clear, so return to bank 0.
        if ((P_VBK&1)!=0) failures++;
    }
    // example:__cgb_safe_set_vbk:end
    __vram_fill(0xFE00,0,160);
    for (i=1;i<8;i++) {
        cell((u8)(i*2),3,1,i);
        sprite((u8)(i-1),(u8)(i*16),64,1,i);
    }
    // example:KQ_CGB_ATTR_PAL:start
    attr=KQ_CGB_ATTR_PAL(9); // 9 & 7 = palette 1, red in this BG example.
    if (attr!=1) failures++;
    cell(2,11,1,attr);
    // example:KQ_CGB_ATTR_PAL:end
    // example:KQ_CGB_ATTR_BANK:start
    attr=(u8)(2|KQ_CGB_ATTR_BANK(enabled)); // Any nonzero value selects tile-data bank 1.
    if (attr!=10) failures++;
    cell(4,11,1,attr); // Blue hollow square, unlike the bank-0 triangle.
    // example:KQ_CGB_ATTR_BANK:end
    // example:KQ_CGB_ATTR_XFLIP_IF:start
    attr=(u8)(3|KQ_CGB_ATTR_XFLIP_IF(enabled));
    if (attr!=35) failures++;
    cell(6,11,1,attr); // Green triangle reflected horizontally.
    // example:KQ_CGB_ATTR_XFLIP_IF:end
    // example:KQ_CGB_ATTR_YFLIP_IF:start
    attr=(u8)(1|KQ_CGB_ATTR_YFLIP_IF(enabled));
    if (attr!=65) failures++;
    cell(8,11,1,attr); // Red triangle reflected vertically.
    // example:KQ_CGB_ATTR_YFLIP_IF:end
    // example:KQ_CGB_ATTR:start
    attr=KQ_CGB_ATTR(10,0,2,2,0); // Palette 2, bank 0, both reflections: 0x62.
    if (attr!=98 || KQ_CGB_ATTR(10,2,3,4,5)!=234) failures++;
    cell(10,11,1,attr);
    // example:KQ_CGB_ATTR:end
    // example:KQ_CGB_ATTR_PRIORITY_IF:start
    attr=(u8)(3|KQ_CGB_ATTR_PRIORITY_IF(enabled)); // Keep nonzero BG pixels in front of sprites.
    if (attr!=131) failures++;
    cell(12,11,1,attr);
    sprite(7,96,88,2,3); // Red full tile behind the green priority triangle.
    // example:KQ_CGB_ATTR_PRIORITY_IF:end
    cell(14,11,1,3); sprite(8,112,88,2,3); // Control: sprite in front without BG priority.
    if (KQ_CGB_ATTR_BANK(0)!=0 || KQ_CGB_ATTR_XFLIP_IF(0)!=0 ||
        KQ_CGB_ATTR_YFLIP_IF(0)!=0 || KQ_CGB_ATTR_PRIORITY_IF(0)!=0) failures++;

    M_LCDC=0x93; // BG enabled (including CGB priority), 8x8 sprites, tile data at $8000.
    m_text(1,0,"CGB PALETTE / ATTR");
    m_text(1,2,"BG 1 2 3 4 5 6 7");
    m_text(1,6,"OBJ 1 2 3 4 5 6 7");
    m_text(1,10,"PAL BANK X Y XY PRI");
    m_text(1,13,"CGB MODE"); m_put(16,13,(u8)('0'+color_mode));
    m_text(1,15,"FAILED CHECKS");
    m_put(16,15,(u8)('0'+failures/100));
    m_put(17,15,(u8)('0'+(failures/10)%10));
    m_put(18,15,(u8)('0'+failures%10));
    while (1) { m_wait(); }
}
