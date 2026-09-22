// A red 3D box hits a static wall and rebounds along Z. The panels show X/Z.
#include "fixed.c"
#include "physics2d.c"
#include "physics3d.c"
#pragma bank 0
#include "fc_common.h"
__location(0x0600) u16 physics_result[8];
KQWorld3D world;
KQBody3D bodies[2];
__prg_rom u8 physics_palette[16]={15,22,22,22,15,18,18,18,15,48,48,48,15,48,48,48};

void caption(u8 x,u8 y,const u8* text) {
    m_text(x,y,text);__vramq_commit();__vramq_exec();
}
void main() {
    u8 i;
    m_init();m_wait();__ppu_ctrl_set(0);__ppu_mask_set(0);
    __palette_bg_load(physics_palette);__vram_fill(0x23C0,0,64);
    for(i=0;i<8;i++){__attr_set(i*4,0,170);__attr_set(i*4,4,170);__attr_set(i*4,20,170);}
    caption(1,1,"3D WALL BOUNCE: XZ VIEW");
    caption(1,5,"BEFORE");caption(17,5,"AFTER 1 STEP");
    kq3d_world_init(&world,bodies,2);
    world.gravity_y=0;world.solver_iterations=1;
    kq3d_body_init(&bodies[0],48,32,8,8,8,8,256);
    kq3d_body_init(&bodies[1],48,32,40,32,16,8,0);
    bodies[0].vz=24;bodies[0].restitution_q8=256;bodies[1].restitution_q8=256;
    // Left panel: red box at Z=8, wall centered at Z=40.
    __nametable_rect(5,8,2,2,1);
    __nametable_rect(2,12,8,2,1);__nametable_rect(18,12,8,2,1);
    for(i=0;i<8;i++)__attr_set(i*4,12,85);
    kq3d_step(&world);
    physics_result[0]=bodies[0].x;physics_result[1]=bodies[0].y;
    physics_result[2]=bodies[0].z;physics_result[3]=bodies[0].vz;
    physics_result[4]=bodies[0].last_impact_speed;
    physics_result[5]=kq3d_overlap_aabb(&bodies[0],&bodies[1]);
    __nametable_rect((u8)(16+(bodies[0].x-8)/8),(u8)(8+(bodies[0].z-8)/8),2,2,1);
    caption(1,21,"RED BOX / BLUE WALL");
    caption(1,23,"Z=8 -> 24   VZ=-24");
    physics_result[7]=0xA55A;
    __scroll_set(0,0);__ppu_ctrl_set(0x80);__ppu_mask_set(0x0A);
    while(1)m_wait();
}
