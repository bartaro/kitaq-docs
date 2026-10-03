#include "fixed.c"
#include "physics2d.c"
#pragma bank 0
__location(0xC700) u16 result[64];
KQWorld2D w; KQBody2D b[2]; KQSurface2D s; KQRect r; KQRect q;
void main(){u8 i;for(i=0;i<64;i++)result[i]=0;kq2d_body_init(&b[0],0,0,1,1);b[0].vx=256;b[0].vy=-256;kq2d_body_apply_friction(&b[0],128);result[0]=b[0].vx;result[1]=b[0].vy;b[0].vx=256;b[0].vy=-257;kq2d_body_apply_friction(&b[0],255);result[2]=b[0].vx;result[3]=b[0].vy;result[63]=0xA55A;while(1){}}