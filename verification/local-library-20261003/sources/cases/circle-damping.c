#include "physics2d_circle.c"
#pragma bank 0
__location(0xC700) u16 result[64];
KQCircleWorld2D w; KQCircleBody2D b[2];
void main(){u8 i;for(i=0;i<64;i++)result[i]=0;kq2dc_world_init(&w,b,1);w.linear_damping_q8=255;b[0].radius=4;b[0].active=1;b[0].inv_mass_q8=64;b[0].vy=0;b[0].x=0;b[0].vx=-2;kq2dc_step(&w);result[0]=b[0].vx;b[0].x=0;b[0].vx=-1;kq2dc_step(&w);result[1]=b[0].vx;b[0].x=0;b[0].vx=0;kq2dc_step(&w);result[2]=b[0].vx;b[0].x=0;b[0].vx=1;kq2dc_step(&w);result[3]=b[0].vx;b[0].x=0;b[0].vx=2;kq2dc_step(&w);result[4]=b[0].vx;b[0].x=0;b[0].vx=256;kq2dc_step(&w);result[5]=b[0].vx;b[0].x=0;b[0].vx=-256;kq2dc_step(&w);result[6]=b[0].vx;result[63]=0xA55A;while(1){}}