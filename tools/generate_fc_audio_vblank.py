"""Generate the independent fixed-bank sequencer and NTSC equal-tempered tables.

The IRQ hot path uses no zero-page/compiler expression scratch. The producer
publishes a slot only after copying all five bytes; the consumer frees it last.
"""
from pathlib import Path
SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.is_dir():REPOS=SITE.parent
OUT=REPOS/'kitaqfc/lib/audio_vblank.c'
code='''// Copyright (c) 2026 DAISUKE OBA. SPDX-License-Identifier: MIT
#include "audio_vblank.h"
#pragma fixed_bank 0

// Eight physical slots, one always empty, distinguish full from empty using
// byte offsets 0,5,...,35. Only foreground code writes head; NMI writes tail.
u8 nav_queue[40];
u8 nav_head;u8 nav_tail;u8 nav_active;u8 nav_delay;
u8 nav_enabled;u8 nav_starved;u8 nav_underruns;u8 nav_invalid;
u8 nav_timbre[4];
const u8* nav_source;const u8* nav_cursor;
u16 nav_count;u16 nav_left;u8 nav_loop;
__prg_rom const u8 nav_end[5]={0,255,255,255,255};
__location(0x4015) u8 nav_status;
__location(0x4017) u8 nav_frame;
__location(0x4001) u8 nav_sweep1;
__location(0x4005) u8 nav_sweep2;
__location(0x4010) u8 nav_dmc_flags;
__location(0x4011) u8 nav_dmc_level;

// Publish inactive before changing queue state. An NMI that occurs afterwards
// exits without reading partially reset producer or consumer fields.
void nes_audio_vblank_stop(void){
    nav_active=0;nav_status=0;nav_delay=0;nav_enabled=0;
    nav_head=0;nav_tail=0;nav_source=0;nav_cursor=0;nav_count=0;nav_left=0;
    nav_starved=0;
}
void nes_audio_vblank_init(void){
    nes_audio_vblank_stop();nav_underruns=0;nav_frame=0x40;
    nav_sweep1=8;nav_sweep2=8;nav_dmc_flags=0;nav_dmc_level=0;
    nav_timbre[0]=0xBC;nav_timbre[1]=0x7A;nav_timbre[2]=0xFF;nav_timbre[3]=0x38;
}

// Validate before claiming a slot. A bad record leaves the queue unchanged.
u8 nes_audio_vblank_enqueue(const u8* record){
    u8 next;u8 i;u8 value;
    nav_invalid=0;
    if(record==0){nav_invalid=1;return 0;}
    next=nav_head+5;if(next==40)next=0;
    if(next==nav_tail)return 0;
    if(record[0]!=0){
        for(i=1;i<5;i++){
            value=record[i];
            if(value<254){
                if(i<4){if(value>71){nav_invalid=1;return 0;}}
                else{if(value>31){nav_invalid=1;return 0;}}
            }
        }
    }
    for(i=0;i<5;i++)nav_queue[nav_head+i]=record[i];
    nav_head=next;return 1;
}
// Tail may advance between reads; head is stable in the foreground producer.
// The result is a momentary occupancy, not a reservation of future slots.
u8 nes_audio_vblank_queued(void){
    u8 head;u8 tail;head=nav_head;tail=nav_tail;
    if(head<tail)head=head+40;
    return (head-tail)/5;
}
u8 nes_audio_vblank_free(void){return 7-nes_audio_vblank_queued();}
void nes_audio_vblank_start(void){nav_active=1;}
u8 nes_audio_vblank_is_playing(void){return nav_active;}
u8 nes_audio_vblank_underruns(void){return nav_underruns;}
u8 nes_audio_vblank_set_timbre(u8 channel,u8 control){
    if(channel>=4)return 0;
    if(channel<2)nav_timbre[channel]=(control&0xCF)|0x30;
    else if(channel==2){if(control==0)nav_timbre[2]=0x80;else nav_timbre[2]=0xFF;}
    else nav_timbre[3]=(control&15)|0x30;
    return 1;
}
u8 nes_audio_vblank_set_music(const u8* records,u16 count,u8 loop){
    nes_audio_vblank_stop();
    if(records==0||count==0||count>13107)return 0;
    nav_source=records;nav_cursor=records;nav_count=count;nav_left=count;nav_loop=loop;
    return 1;
}
// Work is bounded even for a looping song. Copying happens outside NMI so no
// bank switch, variable-length parse or shared compiler arithmetic runs there.
u8 nes_audio_vblank_refill(void){
    u8 copied;copied=0;
    while(copied<7&&nav_source!=0){
        if(nav_left==0){
            if(nav_loop!=0){nav_cursor=nav_source;nav_left=nav_count;}
            else {if(nes_audio_vblank_enqueue(nav_end)!=0){copied++;nav_source=0;}return copied;}
        }
        if(nes_audio_vblank_enqueue(nav_cursor)==0){
            // The producer-only flag distinguishes malformed data from full.
            // Re-reading occupancy here would race NMI freeing a full queue.
            if(nav_invalid!=0){nes_audio_vblank_stop();return 0;}
            return copied;
        }
        copied++;nav_cursor=nav_cursor+5;nav_left--;
    }
    return copied;
}
u8 nes_audio_vblank_play_music(const u8* records,u16 count,u8 loop){
    if(nes_audio_vblank_set_music(records,count,loop)==0)return 0;
    if(nes_audio_vblank_refill()==0)return 0;
    nes_audio_vblank_start();return 1;
}

// Rounded NTSC timer values: CPU/(16*f)-1 for pulse, CPU/(32*f)-1
// for triangle; f=440*2^((MIDI_note-69)/12), MIDI notes 36..107.
'''
for channel,divisor in [('pulse',16),('triangle',32)]:
    periods=[max(0,round(1789773/(divisor*(440*2**((note-69)/12)))-1)) for note in range(36,108)]
    for part in ['lo','hi']:
        values=[n&255 if part=='lo' else n>>8 for n in periods]
        code+='__prg_rom const u8 nav_'+channel+'_'+part+'[72]={'+','.join(map(str,values))+'};\n'
code+='''
// This routine is reached by the compiler's NMI hook, never by a frame wait.
// Branch to nearby labels only, so the all-channel path stays within 6502
// relative-branch range. P is restored by RTI in the enclosing NMI handler.
void __nes_audio_vblank_tick(void){
    __asm {
        PHA
        TXA
        PHA
        TYA
        PHA
        LDA nav_active
        BNE nav_tick_active
        JMP nav_tick_exit
nav_tick_active:
        LDA nav_delay
        BEQ nav_tick_next
        DEC nav_delay
        BEQ nav_tick_next
        JMP nav_tick_exit
nav_tick_next:
        LDX nav_tail
        CPX nav_head
        BNE nav_tick_record
        LDA #0
        STA $4015
        STA nav_enabled
        LDA nav_starved
        BNE nav_tick_empty_done
        INC nav_starved
        LDA nav_underruns
        CMP #255
        BEQ nav_tick_empty_done
        INC nav_underruns
nav_tick_empty_done:
        JMP nav_tick_exit
nav_tick_record:
        LDA #0
        STA nav_starved
        LDA nav_queue,X
        BNE nav_tick_timed
        STA nav_active
        STA nav_enabled
        STA $4015
        JMP nav_tick_release
nav_tick_timed:
        STA nav_delay
'''
for ch,(bit,base,table) in enumerate([(1,0x4000,'pulse'),(2,0x4004,'pulse'),(4,0x4008,'triangle'),(8,0x400C,'noise')]):
    label='nav_tick_ch'+str(ch+1)
    code+=f'''        INX
        LDA nav_queue,X
        CMP #255
        BEQ {label}_done
        CMP #254
        BNE {label}_note
        LDA nav_enabled
        AND #{255-bit}
        STA nav_enabled
        STA $4015
        JMP {label}_done
{label}_note:
        TAY
        LDA nav_enabled
        ORA #{bit}
        STA nav_enabled
        STA $4015
        LDA nav_timbre+{ch}
        STA ${base:04X}
'''
    if table!='noise':
        code+=f'''        LDA nav_{table}_lo,Y
        STA ${base+2:04X}
        LDA nav_{table}_hi,Y
        STA ${base+3:04X}
'''
    else:
        code+='''        TYA
        AND #16
        BEQ nav_tick_noise_long
        TYA
        AND #15
        ORA #128
        JMP nav_tick_noise_period
nav_tick_noise_long:
        TYA
nav_tick_noise_period:
        STA $400E
        LDA #0
        STA $400F
'''
    code+=label+'_done:\n'
code+='''nav_tick_release:
        LDA nav_tail
        CLC
        ADC #5
        CMP #40
        BNE nav_tick_publish
        LDA #0
nav_tick_publish:
        STA nav_tail
nav_tick_exit:
        PLA
        TAY
        PLA
        TAX
        PLA
    }
}
'''
OUT.write_text(code,encoding='ascii')
print(OUT)
