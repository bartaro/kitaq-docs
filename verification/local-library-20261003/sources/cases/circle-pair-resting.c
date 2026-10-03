#include "physics2d_circle.c"
#pragma bank 0
__location(0xC700) u16 result[64];
KQCircleWorld2D w; KQCircleBody2D b[2];
void main(){u8 i;for(i=0;i<64;i++)result[i]=0;kq2dc_world_init(&w,b,2);w.solver_iterations=1;w.linear_damping_q8=255;for(i=0;i<2;i++){b[i].x=16+i*16;b[i].y=24;b[i].radius=8;b[i].inv_mass_q8=64;b[i].active=1;b[i].vx=0;b[i].vy=0;b[i].restitution_q8=128;b[i].friction_q8=0;}b[0].vx=8;kq2dc_step(&w);result[0]=b[0].x;result[1]=b[1].x;result[2]=b[0].vx;result[3]=b[1].vx;result[4]=kq2dc_overlap_circle(&b[0],&b[1]);b[0].x=16;b[1].x=20;b[0].vx=0;b[1].vx=0;kq2dc_step(&w);result[5]=b[0].x;result[6]=b[1].x;result[63]=0xA55A;while(1){}}