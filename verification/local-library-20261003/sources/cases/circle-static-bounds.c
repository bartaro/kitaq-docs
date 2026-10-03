#include "physics2d_circle.c"
#pragma bank 0
__location(0xC700) u16 result[64];
KQCircleWorld2D w; KQCircleBody2D b[2];
void main(){u8 i;for(i=0;i<64;i++)result[i]=0;kq2dc_world_init(&w,b,1);kq2dc_set_bounds(&w,4,4,60,60);w.wall_restitution_q8=128;w.wall_friction_q8=0;b[0].x=0;b[0].y=24;b[0].radius=6;b[0].active=1;b[0].inv_mass_q8=0;b[0].vx=-8;b[0].vy=0;kq2dc_step(&w);result[0]=b[0].x;result[1]=b[0].vx;b[0].active=0;b[0].x=0;kq2dc_step(&w);result[2]=b[0].x;kq2dc_world_init(0,b,1);kq2dc_set_bounds(0,0,0,1,1);kq2dc_step(0);w.bodies=0;kq2dc_step(&w);result[63]=0xA55A;while(1){}}