#pragma bank 0
// Preprojected edge arrays, a clipped square, a tiny marker and a projectile.
#include "wire_cgb_example.h"
__prg_rom Wire3DCGB_Edge edges[4]={{0,1},{1,2},{2,3},{3,0}};
__prg_rom s8 vx8[4]={-8,8,8,-8};
__prg_rom s8 vy8[4]={-8,-8,8,8};
__prg_rom s16 vx16[4]={-12,12,12,-12};
__prg_rom s16 vy16[4]={-8,-8,8,8};
__prg_rom u8 mask[1]={5};
Wire3DCGB_Model shape;
void main() {
    wire_results_clear(); Wire3DCGB_Init(); wire_colors(); Wire3DCGB_BeginFrame();
    shape.vertices=0;shape.edges=edges;shape.faces=0;shape.edge_faces=0;
    shape.vertex_count=4;shape.edge_count=4;shape.face_count=0;shape.flags=0;
    Wire3DCGB_SetLineColor(2);
    Wire3DCGB_DrawMaskedModel2D(&shape,vx8,vy8,mask,24,24,1);
    Wire3DCGB_DrawEdgeList2D(edges,4,vx8,vy8,64,24,2);
    Wire3DCGB_DrawEdgeListClipped2D(edges,4,vx16,vy16,4,4,64,3);
    Wire3DCGB_DrawTinyModel2D(104,24,16,3);
    result[0]=Wire3DCGB_ProjectAxis48(48,96);
    result[1]=Wire3DCGB_ProjectAxis48(-48,96);
    Wire3DCGB_DrawFastProjectile(96,64,64,0,1);
    result[2]=Wire3DCGB_GetLineColor();
    Wire3DCGB_EndFrame();result[7]=0xA55A;
    while(1) {}
}
