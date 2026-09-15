// Observe the CPU IRQ mask independently of the PPU's default NMI counter.
// The final screen appears after more than 256 NMI callbacks. Link no runtime.c:
// this example deliberately uses the compiler's default NMI handler.
#include "fc_common.h"

__prg_rom u8 demo_pal[16]={0x0F,0x22,0x22,0x22,0x0F,0x22,0x22,0x22,0x0F,0x22,0x22,0x22,0x0F,0x22,0x22,0x22};
u8 failures;
u8 disabled;
u8 enabled;
u8 inside;
u8 restored;
u8 saved_state;
u8 before_count;
u8 delta;
u8 wrapped;
u8 frozen;

// Execute static text transfers immediately while both rendering and NMI are off.
void label(u8 row,const u8* text,u8 value){
    m_text(1,row,text);__vramq_commit();__vramq_exec();
    m_put(27,row,(u8)('0'+value/100));m_put(28,row,(u8)('0'+value/10%10));m_put(29,row,(u8)('0'+value%10));__vramq_commit();__vramq_exec();
}

void main(void){
    u16 i;
    __ppu_off();__ppu_ctrl_set(0);__vramq_clear();__oam_clear();
    __palette_bg_load(demo_pal);__nametable_rect(0,0,32,30,0);__scroll_set(0,0);
    failures=0;
    // example:__irq_disable:start
    __irq_disable();
    disabled=(__irq_save()&4)>>2; // The CPU I bit must be 1.
    // example:__irq_disable:end
    // example:__irq_enable:start
    __irq_enable();
    enabled=(__irq_save()&4)>>2; // Save returns the old I bit: 0, then masks IRQ.
    // example:__irq_enable:end
    __irq_enable();
    // example:__irq_save:start
    saved_state=__irq_save(); // Save all processor-status bits, then set I.
    inside=(__irq_save()&4)>>2; // IRQ remains masked inside this section.
    // example:__irq_save:end
    // example:__irq_restore:start
    __irq_restore(saved_state); // Restore the caller's original IRQ mask.
    restored=(__irq_save()&4)>>2; // Original I was 0; this probe masks it again.
    // example:__irq_restore:end
    if(disabled!=1||enabled!=0||inside!=1||restored!=0)failures++;

    // example:__nmi_enable:start
    __nmi_enable(); // Preserve the PPUCTRL shadow's other bits; CPU I stays set.
    __nmi_wait(); // The default NMI handler still runs with IRQ masked.
    // example:__nmi_enable:end
    // example:__nmi_ready:start
    before_count=__nmi_ready(); // A wrapping byte, not a Boolean ready flag.
    // example:__nmi_ready:end
    // example:__nmi_wait:start
    __nmi_wait();__nmi_wait();__nmi_wait();
    delta=(u8)(__nmi_ready()-before_count); // Three completed default NMIs.
    // example:__nmi_wait:end
    if(delta!=3)failures++;
    before_count=__nmi_ready();
    for(i=0;i<256;i++)__nmi_wait();
    wrapped=(u8)(__nmi_ready()-before_count); // 256 advances wrap to zero.
    if(wrapped!=0)failures++;

    // example:__nmi_disable:start
    __nmi_disable();
    before_count=__nmi_ready();
    for(i=0;i<2000;i++)frozen=__nmi_ready();
    frozen=(u8)(frozen-before_count); // No default-handler advances while off.
    // example:__nmi_disable:end
    if(frozen!=0)failures++;
    m_text(1,1,"IRQ MASK AND NMI COUNTER");__vramq_commit();__vramq_exec();
    label(4,"IRQ DISABLED I",disabled);
    label(6,"IRQ ENABLED I",enabled);
    label(8,"SAVED SECTION I",inside);
    label(10,"RESTORED I",restored);
    label(14,"NMI DELTA 3 WAITS",delta);
    label(16,"NMI DELTA 256 WAITS",wrapped);
    label(18,"NMI OFF DELTA",frozen);
    label(22,"FAILED CHECKS",failures);
    m_text(1,25,"DEFAULT HANDLER ONLY");__vramq_commit();__vramq_exec();
    __scroll_set(0,0);__ppu_mask_set(0x0A);
    while(1){}
}
