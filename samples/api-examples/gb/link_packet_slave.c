// PACKET SLAVE: inspect the displayed values and the matching endpoint.
#include "gb_link_example.h"
#pragma bank 0
void main(){u8 i;u8 value;u8 other;u8 slot;u8 cmd;u8 len;u8 data[24];lesson_begin();

Link_InitSlave();for(i=0;i<120;i++){Link_PollPacket();m_wait();}
result[0]=Link_HasPacket();cmd=0;len=0;result[1]=Link_ReadPacket(&cmd,&len,data);
result[2]=cmd;result[3]=len;result[4]=data[0];result[5]=data[1];result[6]=data[2];
result[7]=Link_HasPacket();result[8]=Link_ReadPacket(0,0,0);result[9]=Link_LastError();Link_Cancel();

m_wait();M_LCDC=0;m_text(1,0,"PACKET SLAVE");
m_text(1,2,"READY");lesson_word(2,result[0]);
m_text(1,4,"COMMAND");lesson_word(4,result[2]);
m_text(1,6,"LENGTH");lesson_word(6,result[3]);
m_text(1,8,"PAYLOAD 1");lesson_word(8,result[4]);
m_text(1,10,"PAYLOAD 2");lesson_word(10,result[5]);
m_text(1,12,"PAYLOAD 3");lesson_word(12,result[6]);
m_text(1,14,"CONSUMED");lesson_word(14,result[7]);
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
