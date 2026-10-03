#include "physics3d.c"
#pragma bank 0
__location(0xC700) u16 result[64];
KQWorld3D w; KQBody3D b[2];
void main(){u8 i;for(i=0;i<64;i++)result[i]=0;kq3d_world_init(&w,b,2);w.gravity_y=0;w.solver_iterations=1;kq3d_body_init(&b[0],16,16,16,8,8,8,256);kq3d_body_init(&b[1],16,16,16,8,8,8,0);b[0].x=8;b[1].x=20;b[0].vx=8;b[0].restitution_q8=256;b[1].restitution_q8=256;kq3d_step(&w);result[0]=b[0].x;result[1]=b[0].vx;result[2]=b[0].last_impact_speed;result[3]=b[1].last_impact_speed;result[63]=0xA55A;while(1){}}