// 3D BOX CONTACT: positions are integer pixels; one call advances one simulation step.
#include "physics_visual.h"
#include "physics3d.c"
#pragma bank 0
__location(0xC600) u16 result[80];
KQWorld3D world; KQBody3D bodies[2]; KQBody3D temp;
void main() {
    u8 i;
    phys_begin();
    for(i=0;i<80;i++) result[i]=0;
    // example:kq3d_world_init:start
    kq3d_world_init(&world,bodies,2);
    result[0]=world.gravity_y; result[1]=world.solver_iterations; result[2]=world.max_speed;
    // example:kq3d_world_init:end
    // example:kq3d_body_init:start
    kq3d_body_init(&temp,10,20,30,8,8,8,256);
    result[3]=temp.inv_mass_q8; result[4]=temp.restitution_q8; result[5]=temp.active;
    // example:kq3d_body_init:end
    // example:kq3d_body_set_mass:start
    kq3d_body_set_mass(&temp,32); result[6]=temp.mass_q8; result[7]=temp.inv_mass_q8;
    kq3d_body_set_mass(&temp,0); result[8]=temp.inv_mass_q8;
    kq3d_body_set_mass(&temp,256);
    // example:kq3d_body_set_mass:end
    temp.vx=1; temp.vy=2; temp.vz=3; temp.ax=2; temp.ay=3; temp.az=4; temp.last_impact_speed=99;
    world.gravity_x=-1; world.gravity_y=1; world.gravity_z=0; world.max_speed=6;
    // example:kq3d_integrate_body:start
    kq3d_integrate_body(&world,&temp);
    result[9]=temp.x; result[10]=temp.y; result[11]=temp.z; result[12]=temp.last_impact_speed;
    // example:kq3d_integrate_body:end
    // example:kq3d_dot_q8_8:start
    result[13]=kq3d_dot_q8_8(256,128,0,64,-64,127);
    // example:kq3d_dot_q8_8:end
    kq3d_body_init(&bodies[0],24,24,16,8,8,8,256);
    kq3d_body_init(&bodies[1],24,24,16,8,8,8,256);
    // example:kq3d_overlap_aabb:start
    result[14]=kq3d_overlap_aabb(&bodies[0],&bodies[1]);
    bodies[1].z=32; result[15]=kq3d_overlap_aabb(&bodies[0],&bodies[1]);
    // example:kq3d_overlap_aabb:end
    kq3d_body_init(&bodies[1],48,32,24,4,24,24,0);
    bodies[0].vx=16; bodies[0].vz=8; bodies[0].break_speed=1;
    world.gravity_x=0; world.gravity_y=0; world.gravity_z=0; world.max_speed=32;
    phys_rect(0,44,8,8,48,2,0); phys_rect(1,44,0,8,48,2,0);
    phys_rect(0,16,16,16,16,3,1); phys_rect(1,16,8,16,16,3,1);
    // example:kq3d_step:start
    kq3d_step(&world);
    result[16]=bodies[0].x; result[17]=bodies[0].y; result[18]=bodies[0].z;
    result[19]=bodies[0].vx; result[20]=bodies[0].vz;
    result[21]=bodies[0].last_impact_speed; result[22]=bodies[0].flags;
    // example:kq3d_step:end
    phys_rect(0,bodies[0].x-8,bodies[0].y-8,16,16,1,0);
    phys_rect(1,bodies[0].x-8,bodies[0].z-8,16,16,1,0);
    m_text(1,0,"3D BOX CONTACT");
    m_text(1,4,"X/Y"); m_text(11,4,"X/Z");
    result[79]=0xA55A; M_LCDC=0x91;
    while(1) { m_wait(); }
}
