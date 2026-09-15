// CIRCLE WALL BOUNCE: positions are integer pixels; one call advances one simulation step.
#include "physics_visual.h"
#include "physics2d_circle.c"
#pragma bank 0
__location(0xC600) u16 result[80];
KQCircleWorld2D world; KQCircleBody2D balls[2];
void main() {
    u8 i;
    phys_begin();
    for(i=0;i<80;i++) result[i]=0;
    // example:kq2dc_world_init:start
    kq2dc_world_init(&world,balls,1);
    result[0]=world.gravity_y; result[1]=world.solver_iterations;
    result[2]=world.max_speed; result[3]=world.linear_damping_q8;
    // example:kq2dc_world_init:end
    balls[0].x=10; balls[0].y=10; balls[0].radius=4;
    balls[1].x=16; balls[1].y=10; balls[1].radius=4;
    // example:kq2dc_overlap_circle:start
    result[4]=kq2dc_overlap_circle(&balls[0],&balls[1]);
    balls[1].x=18; result[5]=kq2dc_overlap_circle(&balls[0],&balls[1]);
    // example:kq2dc_overlap_circle:end
    // example:kq2dc_set_bounds:start
    kq2dc_set_bounds(&world,4,4,60,60);
    // example:kq2dc_set_bounds:end
    balls[0].x=24; balls[0].y=24; balls[0].vx=32; balls[0].vy=0;
    balls[0].radius=6; balls[0].inv_mass_q8=64; balls[0].restitution_q8=128;
    balls[0].friction_q8=0; balls[0].active=1;
    world.linear_damping_q8=255; world.wall_restitution_q8=128; world.wall_friction_q8=0;
    phys_rect(0,4,4,57,57,2,1); phys_circle(0,balls[0].x,balls[0].y,balls[0].radius,1);
    // example:kq2dc_step:start
    kq2dc_step(&world);
    result[6]=balls[0].x; result[7]=balls[0].y; result[8]=balls[0].vx;
    // example:kq2dc_step:end
    phys_rect(1,4,4,57,57,2,1); phys_circle(1,balls[0].x,balls[0].y,balls[0].radius,1);
    m_text(1,0,"CIRCLE WALL BOUNCE");
    m_text(1,4,"BEFORE"); m_text(11,4,"AFTER");
    result[79]=0xA55A; M_LCDC=0x91;
    while(1) { m_wait(); }
}
