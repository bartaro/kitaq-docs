// Physical player 2 requests an aligned restart; all four consoles rediscover.
#include "gb_dmg07_example.h"
#pragma bank 0
void main(){u8 slot;u8 configured;u8 started;u8 transferring;u8 requested;u8 packet[4];
d_begin();LinkDmg07_Init(0);configured=0;started=0;transferring=0;requested=0;
while(1){
    d_poll();
    if(configured==0 && LinkDmg07_HasPingStatus()){
        slot=LinkDmg07_GetLocalSlot();
        if(LinkDmg07_GetConnectedMask()==15){result[0]=slot;LinkDmg07_ConsumePingStatus();LinkDmg07_SetLocalByte(32+slot);configured=1;}
    }
    if(configured && started==0 && slot==1){LinkDmg07_RequestTransmission();started=1;}
    if(LinkDmg07_GetPhase()==LINK_DMG07_PHASE_TRANSFER)transferring=1;
    if(LinkDmg07_HasPacket()){
        result[1]=LinkDmg07_IsPipelinePrimed();LinkDmg07_ReadPacket(packet);
        result[2]=(packet[0]==33 && packet[1]==34 && packet[2]==35 && packet[3]==36);
        if(slot==2 && requested==0){
            result[3]=LinkDmg07_RequestRestart();result[4]=LinkDmg07_GetRestartState();requested=1;
        }
    }
    if(LinkDmg07_GetRestartState()==LINK_DMG07_RESTART_SENDING)result[5]=1;
    if(transferring && LinkDmg07_GetPhase()==LINK_DMG07_PHASE_PING){
        result[6]=LinkDmg07_GetPhase();result[7]=LinkDmg07_GetLocalSlot();result[8]=LinkDmg07_GetConnectedMask();
        result[9]=LinkDmg07_IsPipelinePrimed();result[10]=LinkDmg07_GetRestartState();result[11]=LinkDmg07_GetTimeoutCount();
        result[12]=LinkDmg07_GetDisconnectCount();result[13]=LinkDmg07_GetErrorCount();result[14]=LinkDmg07_LastError();break;
    }
}
m_wait();M_LCDC=0;m_text(1,0,"DMG07 RESTART");
m_text(1,2,"PLAYER");d_word(2,result[0]);
m_text(1,4,"DATA VALID");d_word(4,result[2]);
m_text(1,6,"PENDING");d_word(6,result[4]);
m_text(1,8,"SENT FF");d_word(8,result[5]);
m_text(1,10,"RESET PHASE");d_word(10,result[6]);
m_text(1,12,"SLOT AFTER");d_word(12,result[7]);
m_text(1,14,"RESET PRIME");d_word(14,result[9]);
m_text(1,16,"ERROR");d_word(16,result[14]);
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
