// No adapter: observe the 12-frame timeout and distinguish request errors.
#include "gb_dmg07_example.h"
#pragma bank 0
void main(){u8 i;u8 value[4];d_begin();LinkDmg07_Init(0);
result[0]=LinkDmg07_GetPhase();result[1]=LinkDmg07_GetLocalSlot();result[2]=LinkDmg07_GetConnectedMask();
result[3]=LinkDmg07_RequestTransmission();result[4]=LinkDmg07_RequestRestart();
LinkDmg07_ClearError();result[5]=LinkDmg07_LastError();
// Tick once for each actual frame; keep polling during all intervening scanlines.
while(LinkDmg07_GetSilenceFrames()<12)d_poll();
result[6]=LinkDmg07_GetSilenceFrames();result[7]=LinkDmg07_GetTimeoutCount();result[8]=LinkDmg07_GetDisconnectCount();result[9]=LinkDmg07_LastError();
while(LinkDmg07_GetSilenceFrames()<20)d_poll();
result[10]=LinkDmg07_GetTimeoutCount();result[11]=LinkDmg07_GetErrorCount();result[12]=LinkDmg07_GetRestartState();
for(i=0;i<4;i++)value[i]=77;result[13]=LinkDmg07_ReadPacket(value);result[14]=value[0];result[15]=LinkDmg07_GetPacketSlot(0);result[16]=LinkDmg07_GetPacketSlot(5);
LinkDmg07_ClearError();result[17]=LinkDmg07_LastError();result[18]=LinkDmg07_GetTimeoutCount();
m_wait();M_LCDC=0;m_text(1,0,"DMG07 NO ADAPTER");
m_text(1,2,"PLAYER");d_word(2,result[1]);
m_text(1,4,"START ERROR");d_word(4,result[3]);
m_text(1,6,"SILENT FRAME");d_word(6,result[6]);
m_text(1,8,"TIMEOUTS");d_word(8,result[7]);
m_text(1,10,"DISCONNECTS");d_word(10,result[8]);
m_text(1,12,"ERROR");d_word(12,result[9]);
m_text(1,14,"EMPTY BUFFER");d_word(14,result[14]);
m_text(1,16,"CLEARED");d_word(16,result[17]);
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
