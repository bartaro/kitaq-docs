#pragma bank 0
// Reuse both VRAM banks and remove old geometry while presenting sparse frames.
#include "wire_cgb_example.h"
void main() {
    wire_results_clear(); Wire3DCGB_Init();
    Wire3DCGB_ClearFrameTiles();
    Wire3DCGB_EnableAtomicMaps(); wire_colors();
    // First frame: red on the left. Fast begin invalidates both bank histories.
    Wire3DCGB_BeginFrameFast(); wire_frame(8,8,32,32,1);
    Wire3DCGB_EndFrameFast();
    // Second frame: blue in the middle, with the old red frame removed.
    Wire3DCGB_BeginFrameSparse(); wire_frame(40,40,64,64,2);
    Wire3DCGB_EndFrameSparse();
    // Third frame: explicitly clearing a stage discards its first green point.
    Wire3DCGB_BeginFrameSparse();
    Wire3DCGB_SetLineColor(3); Wire3DCGB_DrawPoint2D(4,4);
    Wire3DCGB_ClearSparseStageFast();
    // The final image contains only this green frame on the right.
    wire_frame(80,8,112,32,3);
    Wire3DCGB_MarkDirtyRect2D(80,8,112,32);
    Wire3DCGB_InvalidateFrameHistory();
    Wire3DCGB_EndFrameSparseNow();
    result[0]=Wire3DCGB_GetLineColor();
    result[7]=0xA55A;
    while(1) {}
}
