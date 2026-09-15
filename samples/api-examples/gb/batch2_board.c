// board demonstrates a complete, reproducible library workflow.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "slg_board.c"
__location(0xC600) u16 result[80];
void demo_label(u8 y,const u8* label){m_text(1,y,label);}
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}}
SLGBoard board;u8 cells[12];SLGMoveList moves;SLGMove move_data[2];SLGUndoStack undo;SLGMove undo_data[2];SLGMove old;
void main(){u8 i;tile_example_begin();M_LCDC=0;vram_example_color(1,2,18,14,2);for(i=0;i<80;i++)result[i]=0;
// example:slg_board_init:start
cells[0]=9;slg_board_init(&board,4,3,cells);result[0]=slg_board_get(&board,0,0);
// example:slg_board_init:end
// example:slg_board_clear:start
slg_board_clear(&board,0);result[1]=cells[0];result[2]=cells[11];
// example:slg_board_clear:end
// example:slg_board_set:start
slg_board_set(&board,1,1,7);slg_board_set(&board,4,1,9);
// example:slg_board_set:end
// example:slg_board_get:start
result[3]=slg_board_get(&board,1,1);result[4]=slg_board_get(&board,4,1);
// example:slg_board_get:end
// example:slg_move_list_init:start
slg_move_list_init(&moves,move_data,2);result[5]=moves.count;
// example:slg_move_list_init:end
// example:slg_move_list_push:start
result[6]=slg_move_list_push(&moves,1,1,7);result[7]=slg_move_list_push(&moves,2,1,8);result[8]=slg_move_list_push(&moves,3,1,9);result[9]=moves.count;
// example:slg_move_list_push:end
// example:slg_move_list_clear:start
slg_move_list_clear(&moves);result[10]=moves.count;result[11]=move_data[0].value;
// example:slg_move_list_clear:end
// example:slg_undo_init:start
slg_undo_init(&undo,undo_data,2);result[12]=undo.count;
// example:slg_undo_init:end
// example:slg_undo_push:start
result[13]=slg_undo_push(&undo,1,1,slg_board_get(&board,1,1));slg_board_set(&board,1,1,8);slg_undo_push(&undo,1,1,8);result[14]=slg_undo_push(&undo,0,0,9);
// example:slg_undo_push:end
// example:slg_undo_pop:start
result[15]=slg_undo_pop(&undo,&old);result[16]=old.value;result[17]=slg_board_get(&board,1,1);slg_undo_pop(&undo,&old);slg_board_set(&board,old.x,old.y,old.value);result[18]=slg_board_get(&board,1,1);result[19]=slg_undo_pop(&undo,&old);
// example:slg_undo_pop:end


demo_label(0,"BOARD / MOVE / UNDO");
demo_label(2,"INIT RETAINS");demo_word(2,result[0]);
demo_label(4,"CELL VALUE");demo_word(4,result[3]);
demo_label(6,"LIST FULL");demo_word(6,result[8]);
demo_label(8,"CLEAR COUNT");demo_word(8,result[10]);
demo_label(10,"POP VALUE");demo_word(10,result[16]);
demo_label(12,"BOARD STILL");demo_word(12,result[17]);
demo_label(14,"APPLIED UNDO");demo_word(14,result[18]);
demo_label(16,"EMPTY POP");demo_word(16,result[19]);
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
