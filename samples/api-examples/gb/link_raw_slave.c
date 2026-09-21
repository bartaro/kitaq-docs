// BYTE SLAVE: inspect the displayed values and the matching endpoint.
#include "gb_link_example.h"
#pragma bank 0
void main(){u8 i;u8 value;u8 other;u8 slot;u8 cmd;u8 len;u8 data[24];lesson_begin();

Link_InitSlave();result[0]=Link_BeginTransfer(99);
for(i=0;i<24;i++){Link_Poll();if(Link_HasByte())break;m_wait();}
result[1]=Link_HasByte();value=77;result[2]=Link_TryReadByte(&value);result[3]=value;
result[4]=Link_HasByte();result[5]=Link_BeginTransfer(0);
for(i=0;i<32;i++){Link_Poll();if(Link_HasByte())break;m_wait();}
result[6]=Link_HasByte();result[7]=Link_ReadByte();result[8]=Link_ReadByte();result[9]=Link_LastError();

m_wait();M_LCDC=0;m_text(1,0,"BYTE SLAVE");
m_text(1,2,"START");lesson_word(2,result[0]);
m_text(1,4,"READY");lesson_word(4,result[1]);
m_text(1,6,"PEER BYTE");lesson_word(6,result[3]);
m_text(1,8,"DRAINED");lesson_word(8,result[4]);
m_text(1,10,"ZERO READY");lesson_word(10,result[6]);
m_text(1,12,"ZERO BYTE");lesson_word(12,result[7]);
m_text(1,14,"EMPTY READ");lesson_word(14,result[8]);
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
