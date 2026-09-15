#pragma once
// A square split into two triangles with positive area after screen projection.
__prg_rom Wire3DCGB_Vec3 plane_vertices[4]={{-24,-24,0},{24,-24,0},{24,24,0},{-24,24,0}};
__prg_rom Wire3DCGB_Edge plane_edges[4]={{0,1},{1,2},{2,3},{3,0}};
__prg_rom Wire3DCGB_Face plane_faces[2]={{0,2,1},{0,3,2}};
Wire3DCGB_Model plane;
void wire_plane_setup() {
    plane.vertices=plane_vertices;plane.edges=plane_edges;plane.faces=plane_faces;
    plane.edge_faces=0;plane.vertex_count=4;plane.edge_count=4;plane.face_count=2;
    plane.flags=WIRE3DCGB_MODEL_HIDDEN_LINES;
}
