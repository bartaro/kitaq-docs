// Store on/off story flags and multi-step quest states in RAM.
#include "gb_tile_color_example.h"
#include "rpg.h"
u8 before;
u8 opened;
u8 neighbor;
u8 cleared;
u8 started;
u8 finished;
u8 last;
u8 failures;
void flag_value(u8 row,const u8* text,u8 value){
    m_text(1,row,text);m_put(16,row,(u8)('0'+value/100));
    m_put(17,row,(u8)('0'+value/10%10));m_put(18,row,(u8)('0'+value%10));
}
void main(){
    tile_color_example_begin();failures=0;
    // Explicitly initialize the few entries owned by this demonstration.
    flag_clear(9);flag_clear(8);quest_set_state(2,0);quest_set_state(63,0);
    // example:flag_get:start
    before=flag_get(9); // Door-open flag: 0 after explicit initialization.
    // example:flag_get:end
    // example:flag_set:start
    flag_set(9); // Mark the door as open; setting an already set flag is harmless.
    flag_set(9);
    opened=flag_get(9);neighbor=flag_get(8); // 1 and 0: adjacent flag is unchanged.
    // example:flag_set:end
    // example:flag_clear:start
    flag_clear(9);flag_clear(9); // Mark it closed; clearing twice still leaves 0.
    cleared=flag_get(9);
    // example:flag_clear:end
    // example:quest_set_state:start
    quest_set_state(2,1); // In this game, 1 means accepted.
    started=quest_state(2);
    quest_set_state(2,3); // In this game, 3 means completed; replace the whole byte.
    // example:quest_set_state:end
    // example:quest_state:start
    finished=quest_state(2); // Read back 3 without advancing any quest logic.
    // example:quest_state:end
    // The last valid quest entry also accepts the full unsigned byte range.
    quest_set_state(63,255);last=quest_state(63);
    if(before!=0 || opened!=1 || neighbor!=0 || cleared!=0 || started!=1 || finished!=3 || last!=255)failures++;
    M_LCDC=0x91;m_text(1,0,"FLAGS AND QUESTS");
    flag_value(2,"BEFORE",before);flag_value(4,"DOOR OPEN",opened);
    flag_value(6,"NEIGHBOR",neighbor);flag_value(8,"DOOR CLOSED",cleared);
    flag_value(10,"ACCEPTED",started);flag_value(12,"COMPLETED",finished);
    flag_value(14,"LAST QUEST",last);flag_value(16,"FAILED",failures);
    while(1){m_wait();}
}
