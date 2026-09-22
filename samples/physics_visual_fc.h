#pragma once
#pragma bank 2
#include "fc_common.h"
#pragma bank 0
#include "physics_font_fc.h"
// Two 64x64 panels occupy CHR RAM tiles 128..255. Keep rendering off
// until phys_end. The framebuffer borrows cartridge RAM $6800..$6FFF.
__location(0x6800) u8 phys_pixels[2048];
__location(0xA001) u8 phys_ram_control;
__location(0x8000) u8 phys_bank_select;
__location(0x8001) u8 phys_bank_data;
__prg_rom u8 phys_palette[16]={15,22,18,26,15,22,18,26,15,48,48,48,15,48,48,48};
#pragma bank 2
void phys_begin() {
    u16 i; u8 panel; u8 x; u8 y;
    phys_ram_control=0x80;
    m_init(); m_wait(); __ppu_ctrl_set(0); __ppu_mask_set(0);
    // Map the eight CHR RAM pages linearly before uploading either bitplane.
    phys_bank_select=0; phys_bank_data=0;
    phys_bank_select=1; phys_bank_data=2;
    phys_bank_select=2; phys_bank_data=4;
    phys_bank_select=3; phys_bank_data=5;
    phys_bank_select=4; phys_bank_data=6;
    phys_bank_select=5; phys_bank_data=7;
    __palette_bg_load(phys_palette);
    for(i=0;i<2048;i++) phys_pixels[i]=0;
    for(i=0;i<2048;i+=128) __vram_write(i,physics_font_fc+i,128);
    __vram_fill(0x23C0,0,64);
    // White text above the panels; red/blue/green geometry inside them.
    for(x=0;x<8;x++) {
        __attr_set(x*4,0,170);
        __attr_set(x*4,4,10);
    }
    for(panel=0;panel<2;panel++) for(y=0;y<8;y++) for(x=0;x<8;x++)
        __nametable_rect((u8)(1+panel*10+x),(u8)(6+y),1,1,(u8)(128+panel*64+y*8+x));
}
// Clip panel-local coordinates, then update both NES bitplanes in RAM.
void phys_pixel(u8 panel,s16 x,s16 y,u8 color) {
    u16 address; u8 mask; u8* p;
    if(panel>=2||x<0||y<0||x>=64||y>=64) return;
    address=(u16)((u16)panel*1024+((u16)y/8*8+(u16)x/8)*16+((u16)y&7));
    mask=(u8)(128>>(x&7)); p=phys_pixels+address;
    if(color&1) *p=(u8)(*p|mask); else *p=(u8)(*p&~mask);
    p+=8;
    if(color&2) *p=(u8)(*p|mask); else *p=(u8)(*p&~mask);
}
void phys_rect(u8 panel,s16 x,s16 y,s16 w,s16 h,u8 color,u8 outline) {
    s16 dx; s16 dy;
    for(dy=0;dy<h;dy++) for(dx=0;dx<w;dx++)
        if(!outline||dx==0||dy==0||dx==w-1||dy==h-1) phys_pixel(panel,x+dx,y+dy,color);
}
// Short DDA vectors make the velocity direction visible in these lessons.
void phys_vector(u8 panel,s16 x,s16 y,s16 vx,s16 vy,u8 color) {
    s16 n; s16 ax; s16 ay; s16 k;
    ax=vx<0?0-vx:vx; ay=vy<0?0-vy:vy; n=ax>ay?ax:ay;
    if(n==0) { phys_pixel(panel,x,y,color); return; }
    for(k=0;k<=n;k++) phys_pixel(panel,x+vx*k/n,y+vy*k/n,color);
}
// Upload completed panels and labels before enabling the display.
void phys_end() {
    u16 i;
    for(i=0;i<2048;i+=128) __vram_write((u16)(0x0800+i),phys_pixels+i,128);
    __vramq_commit(); __vramq_exec();
    __scroll_set(0,0); __ppu_ctrl_set(0x80); __ppu_mask_set(0x0A);
}
