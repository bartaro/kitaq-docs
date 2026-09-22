// Exercise rendering-mask timing, then display an annotated timeline.
// No robot command or commercial game data is embedded in this example.
#include "fc_common.h"
__prg_rom u8 optical_palette[16]={15,48,16,48,15,48,16,48,15,48,16,48,15,48,16,48};
__location(0x0700) u8 rob_result[5];

void main() {
    u8 start;
    u8 bit;
    u8 frame;
    u8 x;
    u8 y;
    u8 on;
    m_init();
    __ppu_off();
    // Tile 1 in vram_shapes.chr is solid. White foreground, black backdrop.
    __palette_bg_load(optical_palette);
    __nametable_rect(0,0,32,30,1);
    __ppu_addr(0x2000);
    __scroll_set(0,0);
    __ppu_mask_set(0);
    __nmi_wait();

    // example:__rob_flash:start
    start=__nmi_ready();
    __rob_flash(1); // Enable rendering and wait for one NMI-counter change.
    rob_result[0]=(u8)(__nmi_ready()-start);
    __rob_flash(0); // Disable rendering; the black backdrop remains visible.
    // example:__rob_flash:end

    // example:__rob_pulse:start
    start=__nmi_ready();
    __rob_pulse(3,2); // Three enabled waits, then two disabled waits.
    rob_result[1]=(u8)(__nmi_ready()-start);
    // example:__rob_pulse:end

    // example:__rob_send_byte:start
    start=__nmi_ready();
    __rob_send_byte(0xA5); // 10100101, most-significant bit first; 48 waits.
    rob_result[2]=(u8)(__nmi_ready()-start);
    rob_result[3]=__ppu_mask_get(); // Zero: the sequence ends with rendering off.
    // example:__rob_send_byte:end

    // Show the expected waveform after transmission; these blocks are a diagram.
    m_init();
    m_text(1,0,"OPTICAL MASK TIMING");m_wait();
    m_text(1,2,"FLASH WAITS 1");m_wait();
    m_text(1,3,"PULSE 3 ON / 2 OFF = 5");m_wait();
    m_text(1,4,"A5 BYTE WAITS 48");m_wait();
    m_text(1,6,"ONE BLOCK = ONE WAIT");m_wait();
    m_text(1,7,"WHITE ON / BLANK OFF");m_wait();
    for(bit=0;bit<8;bit++) {
        x=(u8)(2+(bit&3)*6);
        y=(u8)(bit<4 ? 10 : 17);
        on=(u8)((0xA5 & (0x80>>bit))!=0 ? 4 : 2);
        m_put(x,y,on==4 ? '1' : '0');m_wait();
        for(frame=0;frame<6;frame++) {
            m_put((u8)(x+frame),(u8)(y+2),frame<on ? 1 : 0);
        }
        m_wait();
    }
    m_text(1,22,"FINAL MASK 0");m_wait();
    if(rob_result[0]==1 && rob_result[1]==5 && rob_result[2]==48 && rob_result[3]==0)
        m_text(1,24,"TIMING CHECKS OK");
    else m_text(1,24,"TIMING CHECKS FAILED");
    m_wait();rob_result[4]=165;
    while(1)m_wait();
}
