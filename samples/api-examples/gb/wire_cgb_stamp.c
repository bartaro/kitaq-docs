#pragma bank 0
// A complete cube-stamp frame removes the preceding stamp's old map cells.
#include "wire_cgb_example.h"
Wire3DCGB_FastCube cube[1];
void main() {
    u8 bank;
    wire_results_clear(); Wire3DCGB_Init(); wire_colors();
    cube[0].x=-24;cube[0].y=0;cube[0].z=96;
    cube[0].rx=0;cube[0].ry=0;cube[0].rz=0;cube[0].color=1;
    bank=sample_svbk;sample_svbk=2;
    Wire3DCGB_DrawFastCubeFrame(cube,1,1,0);
    cube[0].x=24;
    Wire3DCGB_DrawFastCubeFrame(cube,1,1,0);
    sample_svbk=bank;result[0]=cube[0].x;result[7]=0xA55A;
    while(1) {}
}
