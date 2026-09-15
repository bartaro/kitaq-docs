#pragma bank 0
// Fast cube approximations use screen offsets and depth size bands, not a camera.
#include "wire_cgb_example.h"
Wire3DCGB_FastCube cubes[2];
void main() {
    u8 i;
    wire_results_clear(); Wire3DCGB_Init(); wire_colors(); Wire3DCGB_BeginFrame();
    for(i=0;i<2;i++){cubes[i].rx=0;cubes[i].ry=0;cubes[i].rz=0;}
    cubes[0].x=-32;cubes[0].y=-8;cubes[0].z=90;cubes[0].color=1;
    cubes[1].x=32;cubes[1].y=8;cubes[1].z=160;cubes[1].color=2;
    Wire3DCGB_SetCamera(100,0,0,4,4,4); // FastCubes intentionally ignores this.
    Wire3DCGB_DrawFastCubes(cubes,2,1,0);
    Wire3DCGB_DrawFastStatus(1,0);
    result[0]=Wire3DCGB_GetLineColor();
    result[1]=cubes[0].z;result[2]=cubes[1].z;
    Wire3DCGB_EndFrame();result[7]=0xA55A;
    while(1) {}
}
