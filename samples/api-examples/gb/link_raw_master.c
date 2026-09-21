// BYTE MASTER: inspect the displayed values and the matching endpoint.
#include "gb_link_example.h"
#pragma bank 0
void main(){u8 i;u8 value;u8 other;u8 slot;u8 cmd;u8 len;u8 data[24];lesson_begin();

Link_InitMaster();Link_SetUseInterrupt(0);Link_SetFastClock(0);
// Let the other endpoint arm its external-clock transfer first.
lesson_delay(12);result[0]=Link_BeginTransfer(42);value=0;result[1]=Link_WaitByte(8,&value);result[2]=value;
result[3]=Link_IsBusy();result[4]=Link_HasByte();
// A zero-valued byte is valid data. Use fast clocks only on two CGB endpoints.
lesson_delay(12);Link_SetFastClock(__cgb_is_cgb());result[5]=Link_BeginTransfer(0);value=77;
result[6]=Link_WaitByte(8,&value);result[7]=value;result[8]=Link_LastError();

m_wait();M_LCDC=0;m_text(1,0,"BYTE MASTER");
m_text(1,2,"START");lesson_word(2,result[0]);
m_text(1,4,"RECEIVED");lesson_word(4,result[1]);
m_text(1,6,"PEER BYTE");lesson_word(6,result[2]);
m_text(1,8,"BUSY");lesson_word(8,result[3]);
m_text(1,10,"ZERO READY");lesson_word(10,result[6]);
m_text(1,12,"ZERO BYTE");lesson_word(12,result[7]);
m_text(1,14,"ERROR");lesson_word(14,result[8]);
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
