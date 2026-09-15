#pragma bank 0
// A near square hides the middle of a farther blue line, regardless of array order.
#include "wire_cgb_example.h"
#include "wire_cgb_plane.h"
__prg_rom Wire3DCGB_Vec3 back_vertices[2]={{-96,0,0},{96,0,0}};
__prg_rom Wire3DCGB_Edge back_edges[1]={{0,1}};
Wire3DCGB_Model back;
Wire3DCGB_Object objects[2];
void main() {
    u8 i;
    wire_results_clear();wire_plane_setup();
    back.vertices=back_vertices;back.edges=back_edges;back.faces=0;back.edge_faces=0;
    back.vertex_count=2;back.edge_count=1;back.face_count=0;back.flags=0;
    for(i=0;i<2;i++) {
        objects[i].x=0;objects[i].y=0;objects[i].rx=0;objects[i].ry=0;objects[i].rz=0;
        objects[i].scale_q8=256;objects[i].visible=1;
    }
    objects[0].model=&back;objects[0].z=128;objects[0].color=2;
    objects[1].model=&plane;objects[1].z=64;objects[1].color=1;
    Wire3DCGB_Init();wire_colors();Wire3DCGB_BeginFrame();Wire3DCGB_SetLineColor(3);
    Wire3DCGB_DrawScene(objects,2);
    result[0]=objects[0].z;result[1]=objects[1].z;result[2]=Wire3DCGB_GetLineColor();
    Wire3DCGB_EndFrame();result[7]=0xA55A;
    while(1) {}
}
