#include "fixed.c"
#include "physics2d.c"
#pragma bank 0
__location(0xC700) u16 result[64];
KQWorld2D w; KQBody2D b[2]; KQSurface2D s; KQRect r; KQRect q;
void main(){u8 i;for(i=0;i<64;i++)result[i]=0;kq2d_body_init(&b[0],0,0,4,4);b[0].vx=-300;b[0].vy=-400;b[0].active=0;b[0].inv_mass_q8=0;kq2d_body_limit_speed(&b[0],250);result[0]=b[0].vx;result[1]=b[0].vy;b[0].vx=100;b[0].vy=0;kq2d_body_limit_speed(&b[0],200);result[2]=b[0].vx;kq2d_body_limit_speed(&b[0],-1);result[3]=b[0].vx;result[4]=b[0].vy;kq2d_body_limit_speed(0,5);result[63]=0xA55A;while(1){}}