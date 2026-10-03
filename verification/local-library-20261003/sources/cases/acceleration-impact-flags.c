#include "physics3d.c"
#pragma bank 0
__location(0xC700) u16 result[64];
KQWorld3D w; KQBody3D b[2];
void main(){u8 i;for(i=0;i<64;i++)result[i]=0;kq3d_world_init(&w,b,1);w.gravity_y=0;kq3d_body_init(&b[0],0,0,0,4,4,4,256);b[0].ax=1;b[0].last_impact_speed=99;b[0].flags=1;b[0].break_speed=1;kq3d_integrate_body(&w,&b[0]);kq3d_integrate_body(&w,&b[0]);result[0]=b[0].x;result[1]=b[0].vx;result[2]=b[0].ax;result[3]=b[0].last_impact_speed;result[4]=b[0].flags;b[0].inv_mass_q8=0;b[0].last_impact_speed=77;kq3d_step(&w);result[5]=b[0].last_impact_speed;result[6]=b[0].x;kq3d_world_init(0,b,1);kq3d_body_init(0,0,0,0,1,1,1,256);kq3d_body_set_mass(0,256);kq3d_integrate_body(0,&b[0]);kq3d_integrate_body(&w,0);kq3d_step(0);w.bodies=0;kq3d_step(&w);result[63]=0xA55A;while(1){}}