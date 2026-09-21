// LINK4 HOST: inspect the displayed values and the matching endpoint.
#include "gb_link_example.h"
#pragma bank 0
void main(){u8 i;u8 value;u8 other;u8 slot;u8 cmd;u8 len;u8 data[24];lesson_begin();

result[0]=Link4_InitHost(4);result[1]=Link4_GetMode();result[2]=Link4_GetLocalSlot();result[3]=Link4_GetSlotCount();result[4]=Link4_GetSelectedPeer();
result[5]=Link4_GetLastRxPeer();result[6]=Link4_GetLastTxPeer();
lesson_delay(16);
// KOKURA follows Link4_SelectedPeer from compiler metadata. A real transport
// needs its own physical routing; these calls do not drive a DMG-07 adapter.
for(slot=1;slot<4;slot++){
 result[6+slot]=Link4_BeginTransferTo(slot,16+slot);
 for(i=0;i<10;i++){Link_Poll();if(Link4_HasByteFrom(slot))break;m_wait();}
 result[9+slot]=Link4_HasByteFrom(slot);value=0;
 if(slot==1)result[13]=Link4_TryReadByteFrom(slot,&value);
 else {other=255;Link4_TryReadByteAny(&other,&value);result[12+slot]=other;}
 result[15+slot]=value;Link_TryReadByte(0);lesson_delay(6);
}
result[19]=Link4_GetLastRxPeer();result[20]=Link4_GetLastTxPeer();result[21]=Link4_GetSelectedPeer();
data[0]=7;data[1]=42;data[2]=255;
for(slot=1;slot<4;slot++){
 result[21+slot]=Link4_SendPacketTo(slot,data,3,64+slot);
 for(i=0;i<50;i++){Link4_PollPacket();while(Link4_TryReadByteFrom(slot,0)){}m_wait();}
 // Raw peer rings also see protocol bytes. Drain them independently.
 while(Link4_TryReadByteFrom(slot,0)){}
}
result[25]=Link4_SelectPeer(1);result[26]=Link_LastError();

m_wait();M_LCDC=0;m_text(1,0,"LINK4 HOST");
m_text(1,2,"ROLE");lesson_word(2,result[1]);
m_text(1,4,"SLOTS");lesson_word(4,result[3]);
m_text(1,6,"RX PEER 1");lesson_word(6,result[16]);
m_text(1,8,"RX PEER 2");lesson_word(8,result[17]);
m_text(1,10,"RX PEER 3");lesson_word(10,result[18]);
m_text(1,12,"LAST PEER");lesson_word(12,result[19]);
m_text(1,14,"PACKET 3");lesson_word(14,result[24]);
m_text(1,16,"ERROR");lesson_word(16,result[26]);
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
