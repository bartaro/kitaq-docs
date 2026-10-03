#include "fixed.c"
#include "physics2d.c"
#pragma bank 0
__location(0xC700) u16 result[64];
KQWorld2D w; KQBody2D b[2]; KQSurface2D s; KQRect r; KQRect q;
void main(){u8 i;for(i=0;i<64;i++)result[i]=0;kq2d_world_init(&w,b,2);w.gravity_y=0;w.solver_iterations=0;kq2d_body_init(&b[0],16,16,8,8);kq2d_body_init(&b[1],28,16,8,8);b[0].inv_mass_q8=64;b[1].inv_mass_q8=64;b[0].vx=4;kq2d_step(&w);result[0]=b[0].x;result[1]=b[1].x;result[2]=b[0].vx;result[3]=b[1].vx;kq2d_body_set_pos(&b[0],16,16);kq2d_body_set_pos(&b[1],24,24);b[0].vx=0;b[1].vx=0;kq2d_step(&w);result[4]=b[0].x;result[5]=b[0].y;result[6]=b[1].x;result[7]=b[1].y;result[63]=0xA55A;while(1){}}