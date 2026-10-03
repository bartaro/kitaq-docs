#include "physics2d_circle.c"
#pragma bank 0
__location(0xC700) u16 result[64];
KQCircleWorld2D w; KQCircleBody2D b[2];
void main(){u8 i;for(i=0;i<64;i++)result[i]=0;b[0].x=0;b[0].y=0;b[0].radius=8;b[1].radius=8;b[1].x=15;b[1].y=0;result[0]=kq2dc_overlap_circle(&b[0],&b[1]);b[1].x=16;b[1].y=0;result[1]=kq2dc_overlap_circle(&b[0],&b[1]);b[1].x=11;b[1].y=11;result[2]=kq2dc_overlap_circle(&b[0],&b[1]);b[1].x=12;b[1].y=12;result[3]=kq2dc_overlap_circle(&b[0],&b[1]);b[1].x=15;b[1].y=5;result[4]=kq2dc_overlap_circle(&b[0],&b[1]);b[1].x=16;b[1].y=1;result[5]=kq2dc_overlap_circle(&b[0],&b[1]);b[1].x=0;b[1].y=0;result[6]=kq2dc_overlap_circle(&b[0],&b[1]);result[63]=0xA55A;while(1){}}