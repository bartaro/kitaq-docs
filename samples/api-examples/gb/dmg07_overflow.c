// Deliberately skip one mailbox read; show overwrite detection and retained counters.
#include "gb_dmg07_example.h"
#pragma bank 0
void main(){u8 slot;u8 configured;u8 started;u8 packet[4];
d_begin();LinkDmg07_Init(0);configured=0;started=0;
while(1){
    d_poll();
    if(configured==0 && LinkDmg07_HasPingStatus()){
        slot=LinkDmg07_GetLocalSlot();
        if(LinkDmg07_GetConnectedMask()==15){
            result[0]=slot;result[1]=LinkDmg07_GetConnectedMask();result[2]=LinkDmg07_GetLastStatus();
            result[3]=LinkDmg07_ConsumePingStatus();result[4]=LinkDmg07_HasPingStatus();
            LinkDmg07_SetLocalByte(32+slot);configured=1;
        }
    }
    if(configured && started==0 && slot==1){result[5]=LinkDmg07_RequestTransmission();started=1;}
    if(LinkDmg07_HasPacket() && LinkDmg07_GetPacketSequence()==2){
        // The second published packet replaces the unread first packet.
        result[6]=LinkDmg07_GetSentSequence();result[7]=LinkDmg07_GetPacketSequence();
        result[8]=LinkDmg07_GetPhase();result[9]=LinkDmg07_IsPipelinePrimed();
        result[10]=LinkDmg07_ReadPacket(packet);result[11]=packet[0];result[12]=packet[1];result[13]=packet[2];result[14]=packet[3];
        result[15]=LinkDmg07_HasPacket();result[16]=LinkDmg07_GetPacketSlot(4);
        result[17]=LinkDmg07_GetTimeoutCount();result[18]=LinkDmg07_GetDisconnectCount();result[19]=LinkDmg07_GetErrorCount();result[20]=LinkDmg07_LastError();
        LinkDmg07_ClearError();result[21]=LinkDmg07_LastError();result[22]=LinkDmg07_GetErrorCount();
        break;
    }
}
// Freeze this observation on screen. A game continues polling instead.
m_wait();M_LCDC=0;m_text(1,0,"DMG07 OVERFLOW");
m_text(1,2,"PLAYER");d_word(2,result[0]);
m_text(1,4,"PLAYERS MASK");d_word(4,result[1]);
m_text(1,6,"SENT SEQ");d_word(6,result[6]);
m_text(1,8,"PACKET SEQ");d_word(8,result[7]);
m_text(1,10,"PLAYER 1");d_word(10,result[11]);
m_text(1,11,"PLAYER 2");d_word(11,result[12]);
m_text(1,12,"PLAYER 3");d_word(12,result[13]);
m_text(1,13,"PLAYER 4");d_word(13,result[14]);
m_text(1,15,"ERROR");d_word(15,result[20]);
m_text(1,16,"CLEAR ERROR");d_word(16,result[21]);
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
