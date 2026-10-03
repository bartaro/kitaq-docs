#include "fixed.c"
#include "physics2d.c"
#pragma bank 0
__location(0xC700) u16 result[64];
KQWorld2D w; KQBody2D b[2]; KQSurface2D s; KQRect r; KQRect q;
void main(){u8 i;for(i=0;i<64;i++)result[i]=0;r.x=-8;r.y=-8;r.w=16;r.h=16;q.x=8;q.y=-8;q.w=8;q.h=8;result[0]=kq2d_rect_intersect(r,q);q.x=7;result[1]=kq2d_rect_intersect(r,q);result[2]=kq2d_point_in_rect(-8,-8,r);result[3]=kq2d_point_in_rect(8,0,r);result[4]=kq2d_point_in_rect(0,8,r);kq2d_body_init(&b[0],0,0,4,4);kq2d_body_init(&b[1],7,0,4,4);b[0].active=0;result[5]=kq2d_overlap_aabb(&b[0],&b[1]);b[1].x=8;result[6]=kq2d_overlap_aabb(&b[0],&b[1]);result[63]=0xA55A;while(1){}}