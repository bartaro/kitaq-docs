#include "fixed.c"
#include "physics2d.c"
#pragma bank 0
__location(0xC700) u16 result[64];
KQWorld2D w; KQBody2D b[2]; KQSurface2D s; KQRect r; KQRect q;
void main(){u8 i;for(i=0;i<64;i++)result[i]=0;result[0]=kq2d_surface_toi_q8(6,-2);result[1]=kq2d_surface_toi_q8(1,-8191);result[2]=kq2d_surface_toi_q8(8191,-8191);result[3]=kq2d_surface_toi_q8(0,10);result[4]=kq2d_surface_toi_q8(-1,-2);result[5]=kq2d_surface_toi_q8(6,0);result[6]=kq2d_surface_toi_q8(6,2);result[63]=0xA55A;while(1){}}