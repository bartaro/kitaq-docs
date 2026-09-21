// PACKET MASTER: inspect the displayed values and the matching endpoint.
#include "gb_link_example.h"
#pragma bank 0
void main(){u8 i;u8 value;u8 other;u8 slot;u8 cmd;u8 len;u8 data[24];lesson_begin();

Link_InitMaster();data[0]=7;data[1]=42;data[2]=255;lesson_delay(12);
// The sender owns a copy after acceptance, so the caller can reuse its buffer.
result[0]=Link_SendPacket(data,3,0x31);data[1]=0;result[1]=Link_SendPacket(data,3,0x32);
for(i=0;i<100;i++){Link_PollPacket();m_wait();}
result[2]=Link_LastError();Link_ClearError();result[3]=Link_LastError();
result[4]=Link_HasPacket();

m_wait();M_LCDC=0;m_text(1,0,"PACKET MASTER");
m_text(1,2,"QUEUED");lesson_word(2,result[0]);
m_text(1,4,"SECOND SEND");lesson_word(4,result[1]);
m_text(1,6,"LATCHED ERR");lesson_word(6,result[2]);
m_text(1,8,"CLEARED ERR");lesson_word(8,result[3]);
m_text(1,10,"RX MAILBOX");lesson_word(10,result[4]);
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
