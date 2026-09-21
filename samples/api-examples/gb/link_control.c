// LINK CONTROL: inspect the displayed values and the matching endpoint.
#include "gb_link_example.h"
#pragma bank 0
void main(){u8 i;u8 value;u8 other;u8 slot;u8 cmd;u8 len;u8 data[24];lesson_begin();

// Reset returns to an idle external-clock configuration and empties the queues.
Link_InitCommon();result[0]=Link_IsBusy();result[1]=Link_HasByte();result[2]=Link_LastError();
// IRQ masking is configured without starting a transfer or installing a vector.
Link_SetUseInterrupt(1);result[3]=(IE_REG&8)!=0;Link_SetUseInterrupt(0);result[4]=(IE_REG&8)!=0;
// No external clocks arrive: reject a second start and preserve the first byte.
Link_InitSlave();result[5]=Link_BeginTransfer(0x55);result[6]=Link_BeginTransfer(0x66);result[7]=Link_IsBusy();
Link_ClearError();result[8]=Link_LastError();value=77;result[9]=Link_WaitByte(2,&value);result[10]=value;result[11]=Link_LastError();
Link_Cancel();result[12]=Link_IsBusy();result[13]=(SC&128)!=0;Link_ClearError();
// A disconnected internally clocked exchange receives FF. Service the completed
// hardware request explicitly while IE.serial is disabled; this is a dispatcher
// body demonstration, not installation of a CPU interrupt-vector stub.
Link_InitMaster();Link_SetFastClock(__cgb_is_cgb());Link_BeginTransfer(42);
lesson_delay(2);result[14]=(IF_REG&8)!=0;Link_OnSerialIRQ();result[15]=Link_HasByte();result[16]=Link_ReadByte();result[17]=(IF_REG&8)!=0;
// Each eight-slot ring reserves one slot. The eighth unread byte is dropped.
Link_InitMaster();for(i=0;i<8;i++){Link_BeginTransfer(i);lesson_delay(1);Link_Poll();}
result[18]=Link_LastError();other=0;while(Link_TryReadByte(0))other++;result[19]=other;result[20]=Link_ReadByte();
// A zero timeout performs an immediate poll; null output returns without waiting.
value=88;Link_ClearError();result[21]=Link_WaitByte(0,&value);result[22]=value;result[23]=Link_LastError();
Link_ClearError();result[24]=Link_WaitByte(9,0);result[25]=Link_LastError();

m_wait();M_LCDC=0;m_text(1,0,"LINK CONTROL");
m_text(1,2,"BUSY ERROR");lesson_word(2,result[6]);
m_text(1,4,"TIMEOUT");lesson_word(4,result[11]);
m_text(1,6,"IRQ REQUEST");lesson_word(6,result[14]);
m_text(1,8,"OPEN RX");lesson_word(8,result[16]);
m_text(1,10,"OVERFLOW");lesson_word(10,result[18]);
m_text(1,12,"QUEUE BYTES");lesson_word(12,result[19]);
m_text(1,14,"NULL WAIT");lesson_word(14,result[24]);
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
