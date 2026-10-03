#include "fixed.c"
#include "physics2d.c"
#pragma bank 0
__location(0xC700) u16 result[64];
KQWorld2D w; KQBody2D b[2]; KQSurface2D s; KQRect r; KQRect q;
void main(){u8 i;for(i=0;i<64;i++)result[i]=0;kq2d_world_init(&w,b,1);kq2d_body_init(&b[0],10,20,4,4);b[0].vx=3;b[0].vy=4;b[0].active=0;kq2d_integrate_body(&w,&b[0]);result[0]=b[0].x;result[1]=b[0].vy;b[0].active=1;b[0].inv_mass_q8=0;kq2d_body_apply_gravity(&b[0],20,20,30);result[2]=b[0].vx;result[3]=b[0].vy;kq2d_body_set_velocity(&b[0],9,10);result[4]=b[0].vx;kq2d_body_init(0,0,0,1,1);kq2d_world_init(0,b,1);kq2d_step(0);w.bodies=0;kq2d_step(&w);kq2d_integrate_body(0,&b[0]);kq2d_integrate_body(&w,0);kq2d_body_set_pos(0,1,2);kq2d_body_set_velocity(0,1,2);kq2d_body_apply_gravity(0,1,2,3);kq2d_body_apply_friction(0,64);result[63]=0xA55A;while(1){}}