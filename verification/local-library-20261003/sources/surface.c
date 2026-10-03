#include "physics2d.h"

__wram u8 test_ready;
__wram u8 test_command;
__wram s16 test_input[12];
__wram s16 test_output[3];
__wram KQBody2D test_body;
__wram KQSurface2D test_surface;

void main() {
    test_command = 0;
    test_ready = 165;
    while(1) {
        if(test_command != 0) {
            test_body.vx = test_input[0];
            test_body.vy = test_input[1];
            test_output[2] = 0;
            if(test_command == 1) kq2d_body_limit_speed(&test_body,test_input[10]);
            if(test_command == 2) {
                test_surface.nx_q8 = test_input[2];
                test_surface.ny_q8 = test_input[3];
                test_surface.vx = test_input[4];
                test_surface.vy = test_input[5];
                test_surface.restitution_q8 = (u8)test_input[6];
                test_surface.friction_q8 = (u8)test_input[7];
                test_surface.bounce_threshold = test_input[8];
                test_surface.kick = test_input[9];
                test_output[2] = kq2d_body_resolve_surface(&test_body,&test_surface);
            }
            if(test_command == 3) {
                kq2d_body_limit_speed(0,(s16)640);
                test_output[2] = kq2d_body_resolve_surface(0,&test_surface);
                test_output[2] = kq2d_body_resolve_surface(&test_body,0);
            }
            if(test_command == 4) {
                test_body.active = 1;
                test_body.inv_mass_q8 = 256;
                kq2d_body_apply_gravity(&test_body,(s16)5,(s16)11,(s16)640);
            }
            if(test_command == 5) test_body.vx = kq2d_scale_q8(test_input[0],test_input[2]);
            if(test_command == 6) test_body.vx = (s16)kq2d_surface_toi_q8(test_input[0],test_input[1]);
            test_output[0] = test_body.vx;
            test_output[1] = test_body.vy;
            test_command = 0;
        }
    }
}
