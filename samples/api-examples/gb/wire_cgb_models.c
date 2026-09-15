#pragma bank 0
// Four cubes compare unity/half scale and persistent/temporary line colors.
#include "wire_cgb_example.h"
__prg_rom Wire3DCGB_Vec3 vertices[8]={
    {-16,-16,-16},{16,-16,-16},{16,16,-16},{-16,16,-16},
    {-16,-16,16},{16,-16,16},{16,16,16},{-16,16,16}
};
__prg_rom Wire3DCGB_Edge edges[12]={
    {0,1},{1,2},{2,3},{3,0},{4,5},{5,6},
    {6,7},{7,4},{0,4},{1,5},{2,6},{3,7}
};
Wire3DCGB_Model cube;
u8 sx;
u8 sy;
void main() {
    wire_results_clear();
    cube.vertices=vertices; cube.edges=edges;
    cube.faces=0; cube.edge_faces=0;
    cube.vertex_count=8; cube.edge_count=12; cube.face_count=0; cube.flags=0;
    Wire3DCGB_Init(); wire_colors(); Wire3DCGB_BeginFrame();
    Wire3DCGB_SetLineColor(1);
    Wire3DCGB_DrawModel(&cube,-32,32,96,0,0,0);
    Wire3DCGB_DrawModelScaled(&cube,32,32,96,0,0,0,128);
    Wire3DCGB_DrawModelColor(&cube,-32,-32,96,0,0,0,2);
    Wire3DCGB_DrawModelScaledColor(&cube,32,-32,96,0,0,0,128,3);
    result[0]=Wire3DCGB_GetLineColor();
    Wire3DCGB_DrawLine3D(0,56,96,0,-56,96);
    Wire3DCGB_DrawLine3DColor(-80,0,96,80,0,96,3);
    result[1]=Wire3DCGB_ProjectPoint(0,0,96,&sx,&sy);
    result[2]=sx; result[3]=sy;
    // Camera setters affect future projection, leaving the staged cubes intact.
    Wire3DCGB_SetCamera(0,0,0,0,4,0);
    result[4]=Wire3DCGB_ProjectPoint(0,0,96,&sx,&sy);
    result[5]=Wire3DCGB_ProjectPointNoRotation(0,0,96,&sx,&sy);
    result[6]=sx;
    Wire3DCGB_EndFrame(); result[7]=0xA55A;
    while(1) {}
}
