// LINK4 PEER 3: inspect the displayed values and the matching endpoint.
#include "gb_link_example.h"
#pragma bank 0
void main(){u8 i;u8 value;u8 other;u8 slot;u8 cmd;u8 len;u8 data[24];lesson_begin();

result[0]=Link4_InitPeer(3,4);result[1]=Link4_GetMode();result[2]=Link4_GetLocalSlot();result[3]=Link4_GetSlotCount();result[4]=Link4_GetSelectedPeer();
result[5]=Link4_BeginTransferTo(0,163);
for(i=0;i<100;i++){Link_Poll();if(Link4_HasByteFrom(0))break;m_wait();}
result[6]=Link4_HasByteFrom(0);value=0;result[7]=Link4_TryReadByteFrom(0,&value);result[8]=value;
Link_TryReadByte(0);
for(i=0;i<220;i++){Link4_PollPacket();while(Link4_TryReadByteFrom(0,0)){}m_wait();}
result[9]=Link4_HasPacketFrom(0);result[10]=Link4_ReadPacketFrom(0,&cmd,&len,data);
result[11]=cmd;result[12]=len;result[13]=data[0];result[14]=data[1];result[15]=data[2];
result[16]=Link_HasPacket();result[17]=Link4_HasPacketFrom(0);result[18]=Link4_ReadPacketFrom(0,0,0,0);result[19]=Link_LastError();Link_Cancel();

m_wait();M_LCDC=0;m_text(1,0,"LINK4 PEER 3");
m_text(1,2,"LOCAL SLOT");lesson_word(2,result[2]);
m_text(1,4,"HOST BYTE");lesson_word(4,result[8]);
m_text(1,6,"PACKET READY");lesson_word(6,result[9]);
m_text(1,8,"COMMAND");lesson_word(8,result[11]);
m_text(1,10,"LENGTH");lesson_word(10,result[12]);
m_text(1,12,"PAYLOAD 2");lesson_word(12,result[14]);
m_text(1,14,"CONSUMED");lesson_word(14,result[17]);
m_text(1,16,"ERROR");lesson_word(16,result[19]);
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
