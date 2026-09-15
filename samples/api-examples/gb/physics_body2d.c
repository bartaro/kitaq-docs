// 2D BOX CONTACT: positions are integer pixels; one call advances one simulation step.
#include "physics_visual.h"
#include "fixed.c"
#include "physics2d.c"
#pragma bank 0
__location(0xC600) u16 result[80];
KQWorld2D world; KQBody2D bodies[2]; KQBody2D temp; KQRect r1; KQRect r2;
void main() {
    u8 i;
    phys_begin();
    for(i=0;i<80;i++) result[i]=0;
    // example:kq2d_world_init:start
    kq2d_world_init(&world,bodies,2);
    result[0]=world.gravity_y; result[1]=world.solver_iterations; result[2]=world.max_speed;
    // example:kq2d_world_init:end
    // example:kq2d_body_init:start
    kq2d_body_init(&temp,10,20,8,8);
    result[3]=temp.inv_mass_q8; result[4]=temp.active;
    // example:kq2d_body_init:end
    // example:kq2d_body_set_pos:start
    kq2d_body_set_pos(&temp,-12,20);
    result[5]=temp.x; result[6]=temp.y;
    // example:kq2d_body_set_pos:end
    // example:kq2d_body_set_velocity:start
    kq2d_body_set_velocity(&temp,40,-30);
    result[7]=temp.vx; result[8]=temp.vy;
    // example:kq2d_body_set_velocity:end
    // example:kq2d_body_apply_gravity:start
    kq2d_body_apply_gravity(&temp,5,-10,32);
    result[9]=temp.vx; result[10]=temp.vy;
    // example:kq2d_body_apply_gravity:end
    // example:kq2d_body_apply_friction:start
    kq2d_body_apply_friction(&temp,64);
    result[11]=temp.vx; result[12]=temp.vy;
    // example:kq2d_body_apply_friction:end
    // example:__smul16x8:start
    result[13]=__smul16x8(-257,64);
    // example:__smul16x8:end
    r1.x=0; r1.y=0; r1.w=16; r1.h=16;
    r2.x=8; r2.y=8; r2.w=16; r2.h=16;
    // example:kq2d_rect_intersect:start
    result[14]=kq2d_rect_intersect(r1,r2);
    r2.x=16; result[15]=kq2d_rect_intersect(r1,r2);
    // example:kq2d_rect_intersect:end
    // example:kq2d_point_in_rect:start
    result[16]=kq2d_point_in_rect(0,0,r1);
    result[17]=kq2d_point_in_rect(16,0,r1);
    // example:kq2d_point_in_rect:end
    kq2d_body_init(&temp,10,20,8,8);
    temp.vx=1; temp.vy=2; world.gravity_x=2; world.gravity_y=3; world.max_speed=8;
    // example:kq2d_integrate_body:start
    kq2d_integrate_body(&world,&temp);
    result[18]=temp.x; result[19]=temp.y;
    // example:kq2d_integrate_body:end
    kq2d_body_init(&bodies[0],24,24,8,8);
    kq2d_body_init(&bodies[1],24,24,8,8);
    // example:kq2d_overlap_aabb:start
    result[20]=kq2d_overlap_aabb(&bodies[0],&bodies[1]);
    bodies[1].x=40; result[21]=kq2d_overlap_aabb(&bodies[0],&bodies[1]);
    // example:kq2d_overlap_aabb:end
    kq2d_body_init(&bodies[1],32,48,28,4); bodies[1].inv_mass_q8=0;
    bodies[0].vx=4; bodies[0].vy=16; world.gravity_x=0; world.gravity_y=0; world.max_speed=32;
    phys_rect(0,4,44,56,8,2,0); phys_rect(0,bodies[0].x-8,bodies[0].y-8,16,16,1,0);
    // example:kq2d_step:start
    kq2d_step(&world);
    result[22]=bodies[0].x; result[23]=bodies[0].y;
    result[24]=bodies[0].vx; result[25]=bodies[0].vy;
    // example:kq2d_step:end
    phys_rect(1,4,44,56,8,2,0); phys_rect(1,bodies[0].x-8,bodies[0].y-8,16,16,1,0);
    m_text(1,0,"2D BOX CONTACT");
    m_text(1,4,"BEFORE"); m_text(11,4,"AFTER");
    result[79]=0xA55A; M_LCDC=0x91;
    while(1) { m_wait(); }
}
