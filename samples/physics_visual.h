#pragma once
#include "gb_tile_example.h"
// Two 64x64 drawing panels use tiles 128..255. Draw only with the LCD off.
// Color 1 is red, 2 blue, 3 green on CGB; DMG shows all marks in black.
void phys_begin() {
    u8 panel; u8 x; u8 y;
    tile_example_begin(); M_LCDC=0; M_BGP=0xFC;
    __vram_fill(0x8800,0,2048);
    for(panel=0;panel<2;panel++) {
        for(y=0;y<8;y++) for(x=0;x<8;x++)
            __settile_xy((u8)(1+panel*10+x),(u8)(6+y),(u8)(128+panel*64+y*8+x));
    }
    if(__cgb_is_cgb()) {
        T_BGPI=0x88;
        T_BGPD=255; T_BGPD=127;
        T_BGPD=31; T_BGPD=0;
        T_BGPD=0; T_BGPD=124;
        T_BGPD=224; T_BGPD=3;
        __cgb_safe_set_vbk(1);
        for(panel=0;panel<2;panel++) for(y=0;y<8;y++)
            __vram_memset_unsafe((u16)(0x9800+(6+y)*32+1+panel*10),1,8);
        __cgb_safe_set_vbk(0);
    }
}
// Panel-local pixel coordinates are clipped to 0..63.
void phys_pixel(u8 panel,s16 x,s16 y,u8 color) {
    u16 address; u8 mask; u8* p;
    if(x<0||y<0||x>=64||y>=64) return;
    address=(u16)(0x8800+(u16)panel*1024+((u16)y/8*8+(u16)x/8)*16+((u16)y&7)*2);
    mask=(u8)(128>>(x&7)); p=(u8*)address;
    if(color&1) *p=(u8)(*p|mask); else *p=(u8)(*p&~mask);
    p++;
    if(color&2) *p=(u8)(*p|mask); else *p=(u8)(*p&~mask);
}
void phys_rect(u8 panel,s16 x,s16 y,s16 w,s16 h,u8 color,u8 outline) {
    s16 dx; s16 dy;
    for(dy=0;dy<h;dy++) for(dx=0;dx<w;dx++)
        if(!outline||dx==0||dy==0||dx==w-1||dy==h-1) phys_pixel(panel,x+dx,y+dy,color);
}
void phys_circle(u8 panel,s16 x,s16 y,s16 radius,u8 color) {
    s16 dx; s16 dy;
    for(dy=0-radius;dy<=radius;dy++) for(dx=0-radius;dx<=radius;dx++)
        if(dx*dx+dy*dy<=radius*radius) phys_pixel(panel,x+dx,y+dy,color);
}
// These examples need only short arrows; DDA plots both endpoints.
void phys_vector(u8 panel,s16 x,s16 y,s16 vx,s16 vy,u8 color) {
    s16 n; s16 ax; s16 ay; s16 k;
    ax=vx<0?0-vx:vx; ay=vy<0?0-vy:vy; n=ax>ay?ax:ay;
    if(n==0) { phys_pixel(panel,x,y,color); return; }
    for(k=0;k<=n;k++) phys_pixel(panel,x+vx*k/n,y+vy*k/n,color);
}
