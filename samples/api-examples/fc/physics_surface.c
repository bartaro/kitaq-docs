// SURFACE VELOCITY: positions are integer pixels; one call advances one simulation step.
#include "physics_visual_fc.h"
#pragma bank 1
#include "fixed.c"
#include "physics2d.c"
#pragma bank 0
__location(0x0600) u16 result[80];
KQBody2D body; KQSurface2D surface;
void main() {
    u8 i;
    phys_begin();
    for(i=0;i<80;i++) result[i]=0;
    // example:kq2d_scale_q8:start
    result[0]=kq2d_scale_q8(-257,128);
    result[1]=kq2d_scale_q8(300,-256);
    // example:kq2d_scale_q8:end
    kq2d_body_init(&body,24,40,4,4); body.vx=300; body.vy=400;
    // example:kq2d_body_limit_speed:start
    kq2d_body_limit_speed(&body,250);
    result[2]=body.vx; result[3]=body.vy;
    // example:kq2d_body_limit_speed:end
    // example:kq2d_surface_toi_q8:start
    result[4]=kq2d_surface_toi_q8(6,-2);
    result[5]=kq2d_surface_toi_q8(6,0);
    // example:kq2d_surface_toi_q8:end
    body.vx=8; body.vy=16;
    surface.nx_q8=0; surface.ny_q8=-256; surface.vx=0; surface.vy=0;
    surface.bounce_threshold=2; surface.kick=0; surface.restitution_q8=128; surface.friction_q8=64;
    phys_rect(0,4,48,56,4,2,0); phys_rect(0,20,36,8,8,1,0);
    phys_vector(0,body.x,body.y,body.vx,body.vy,3);
    // example:kq2d_body_resolve_surface:start
    result[6]=kq2d_body_resolve_surface(&body,&surface);
    result[7]=body.vx; result[8]=body.vy; result[9]=body.y;
    // example:kq2d_body_resolve_surface:end
    phys_rect(1,4,48,56,4,2,0); phys_rect(1,20,36,8,8,1,0);
    phys_vector(1,body.x,body.y,body.vx,body.vy,3);
    m_text(1,0,"SURFACE VELOCITY");
    m_text(1,4,"BEFORE"); m_text(11,4,"AFTER");
    result[79]=0xA55A; phys_end();
    while(1) { m_wait(); }
}
