// PACKET DEADLINE: inspect the displayed values and the matching endpoint.
#include "gb_link_example.h"
#pragma bank 0
void main(){u8 i;u8 value;u8 other;u8 slot;u8 cmd;u8 len;u8 data[24];lesson_begin();

u16 ticks;Link_InitMaster();result[0]=Link_SendPacket(0,0,7);
// An absent peer cannot acknowledge the packet, despite completed FF exchanges.
for(ticks=0;ticks<300;ticks++){Link_PollPacket();m_wait();}
result[1]=Link_LastError();Link_Cancel();result[2]=Link_IsBusy();Link_ClearError();result[3]=Link_LastError();

m_wait();M_LCDC=0;m_text(1,0,"PACKET DEADLINE");
m_text(1,2,"QUEUED");lesson_word(2,result[0]);
m_text(1,4,"NO ACK ERROR");lesson_word(4,result[1]);
m_text(1,6,"CANCEL BUSY");lesson_word(6,result[2]);
m_text(1,8,"CLEARED");lesson_word(8,result[3]);
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
