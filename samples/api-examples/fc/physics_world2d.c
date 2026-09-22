// One simulation unit is one pixel. A falling red box lands on a blue floor.
#include "fixed.c"
#include "physics2d.c"
#pragma bank 0
#include "fc_common.h"
__location(0x0600) u16 physics_result[8];
KQWorld2D world;
KQBody2D bodies[2];
__prg_rom u8 physics_palette[16]={15,22,22,22,15,18,18,18,15,48,48,48,15,48,48,48};

void caption(u8 x,u8 y,const u8* text) {
    m_text(x,y,text);__vramq_commit();__vramq_exec();
}
void main() {
    u8 i;
    m_init();m_wait();__ppu_ctrl_set(0);__ppu_mask_set(0);
    __palette_bg_load(physics_palette);
    __vram_fill(0x23C0,0,64);
    // Text rows use a white palette; the simulation boxes use red and blue.
    for(i=0;i<8;i++){__attr_set(i*4,0,170);__attr_set(i*4,4,170);__attr_set(i*4,20,170);}
    caption(1,1,"2D GRAVITY AND FLOOR");
    caption(1,5,"BEFORE");caption(17,5,"AFTER 4 STEPS");
    kq2d_world_init(&world,bodies,2);
    world.gravity_y=8;world.max_speed=16;world.solver_iterations=1;
    kq2d_body_init(&bodies[0],48,32,8,8);
    kq2d_body_init(&bodies[1],48,88,32,8);
    bodies[1].inv_mass_q8=0;
    // Left panel is the initial state: center (48,32), zero velocity.
    __nametable_rect(5,11,2,2,1);
    // Floors at y=88 in both panels, drawn 64 pixels below the text origin.
    __nametable_rect(2,18,8,2,1);__nametable_rect(18,18,8,2,1);
    for(i=0;i<8;i++)__attr_set(i*4,16,85);
    for(i=0;i<4;i++)kq2d_step(&world);
    physics_result[0]=bodies[0].x;physics_result[1]=bodies[0].y;
    physics_result[2]=bodies[0].vx;physics_result[3]=bodies[0].vy;
    physics_result[4]=kq2d_overlap_aabb(&bodies[0],&bodies[1]);
    // Right panel is computed from the body's final center (48,72).
    __nametable_rect((u8)(16+(bodies[0].x-8)/8),(u8)(8+(bodies[0].y-8)/8),2,2,1);
    // The box's bottom row shares the floor attribute cell; select red there.
    __attr_set(20,16,80);
    caption(1,21,"RED BOX / BLUE FLOOR");
    caption(1,23,"Y=32 -> 72   VY=0");
    physics_result[7]=0xA55A;
    __scroll_set(0,0);__ppu_ctrl_set(0x80);__ppu_mask_set(0x0A);
    while(1)m_wait();
}
