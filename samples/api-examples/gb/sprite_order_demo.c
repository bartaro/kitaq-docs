// Copyright (c) 2026 DAISUKE OBA. MIT License.
// Two red diamonds keep priority while twelve blue squares take turns among
// the remaining eight hardware slots on their shared scanline (DMG: grayscale).
#pragma fixed_bank 0
#include "gb_tile_example.h"
#include "sprite.c"
#include "sprite_order.c"

__location(0xFF6A) u8 order_obj_index;
__location(0xFF6B) u8 order_obj_data;
__location(0xC700) u8 order_demo_state[4];
SpriteOrder order_demo;
SpriteOrderItem order_demo_items[14];
// Original diamond (color 1) and square (color 3), independent of the font.
__prg_rom u8 order_demo_tiles[32]={
    0x00,0x00,0x18,0x00,0x3C,0x00,0x7E,0x00,
    0x7E,0x00,0x3C,0x00,0x18,0x00,0x00,0x00,
    0x00,0x00,0x7E,0x7E,0x7E,0x7E,0x7E,0x7E,
    0x7E,0x7E,0x7E,0x7E,0x7E,0x7E,0x00,0x00
};

// Submit normal objects first to demonstrate that priority, rather than their
// original queue position, brings the two important objects to the front.
void order_demo_build()
{
    u8 i;
    u8 phase;
    sprite_order_begin(&order_demo);
    for(i=0;i<12;i++)sprite_order_push(&order_demo,(s16)(40+i*8),64,129,0,1);
    sprite_order_push(&order_demo,8,64,128,0,0);
    sprite_order_push(&order_demo,20,64,128,0,0);
    phase=order_demo.phase;
    order_demo_state[0]=phase;
    order_demo_state[1]=sprite_order_build(&order_demo,(SpriteOrderOamEntry*)kq_sprite_oam,40);
    order_demo_state[2]=order_demo.count;
    order_demo_state[3]=0xA5;
    m_put(7,12,(u8)('0'+phase/10));m_put(8,12,(u8)('0'+phase%10));
}

void main()
{
    u8 i;
    u8 ticks;
    tile_example_begin();M_LCDC=0x13;
    __vram_copy(0x8800,order_demo_tiles,32);
    if(__cgb_is_cgb()){
        order_obj_index=0x80;
        for(i=0;i<8;i++){
            order_obj_data=0;order_obj_data=0;
            order_obj_data=31;order_obj_data=0;
            order_obj_data=0xE0;order_obj_data=3;
            order_obj_data=0;order_obj_data=0x7C;
        }
    }
    sprite_init();sprite_order_init(&order_demo,order_demo_items,14,8);
    m_text(1,0,"SPRITE ORDER");m_text(1,6,"HIGH");m_text(6,6,"NORMAL");
    m_text(5,10,"0123456789AB");m_text(1,12,"PHASE");
    m_text(1,15,"2 HIGH + 8 NORMAL");
#ifdef SPRITE_ORDER_DEMO_PHASE
    // A fixed phase makes screenshots reproducible; omit this definition for
    // the interactive demonstration's one-second changes.
    order_demo.phase=SPRITE_ORDER_DEMO_PHASE;
#endif
    order_demo_build();sprite_flush_oam_now();M_LCDC=0x93;ticks=0;
    while(1){
        sprite_flush_oam();
#ifndef SPRITE_ORDER_DEMO_PHASE
        ticks++;
        if(ticks==60){ticks=0;order_demo_build();}
#endif
    }
}
