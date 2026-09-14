// Learn how a five-byte repeat state selects one action and schedules pulses.
// Controlled snapshots make the delay, direction priority and reset reproducible.
#include "gb_tile_example.h"
void __padrep_init(u8* state, u8 das, u8 arr);
void __padrep_reset(u8* state);
u8 __padrep_lr(u8* state, u8 keys, u8 trigger);
u8 __padrep_down(u8* state, u8 keys, u8 trigger);
u8 __padrep(u8* state, u8 keys, u8 trigger, u8 mask);
u8 __padrep_mask(u8* state, u8 keys, u8 trigger, u8 mask);
u8 lr[5];
u8 down[5];
u8 actions[5];
u8 alias_state[5];
u8 failures;
u8 checks;
u8 tick;
u8 keys;
u8 trigger;
u8 result;
u8 pulses;
u8 down_pulses;
u8 action_pulses;
u8 alias_pulses;
u8 left_value;
u8 right_value;

void expect(u8 actual, u8 expected) {
    checks++;
    if (actual != expected) failures++;
}
void show(u8 row, const u8* label, u8 value) {
    m_text(1,row,label);
    m_put(16,row,(u8)('0'+value/100));
    m_put(17,row,(u8)('0'+(value/10)%10));
    m_put(18,row,(u8)('0'+value%10));
    m_wait();
}
void main() {
    tile_example_begin(); M_LCDC=0x91;
    failures=0; checks=0;
    // example:__padrep_init:start
    __padrep_init(lr,3,2);
    // Active action and counters are zero; delay and interval are retained.
    expect(lr[0],0); expect(lr[1],3); expect(lr[2],2);
    expect(lr[3],0); expect(lr[4],0);
    // example:__padrep_init:end
    __padrep_init(down,3,2);
    __padrep_init(actions,3,2);
    __padrep_init(alias_state,3,2);
    pulses=0; down_pulses=0; action_pulses=0; alias_pulses=0;
    tick=0;
    while (tick<8) {
        // Tick 0 is a new press. Ticks 1..7 hold the same buttons.
        keys=1; trigger=0;
        if (tick==0) trigger=keys;
        // example:__padrep_lr:start
        result=__padrep_lr(lr,keys,trigger);
        if (result!=0) pulses++;
        // example:__padrep_lr:end
        if (tick==0 || tick==3 || tick==5 || tick==7) expect(result,1);
        else expect(result,0);
        keys=8; trigger=0; if (tick==0) trigger=keys;
        // example:__padrep_down:start
        result=__padrep_down(down,keys,trigger);
        if (result!=0) down_pulses++;
        // example:__padrep_down:end
        if (tick==0 || tick==3 || tick==5 || tick==7) expect(result,8);
        else expect(result,0);
        keys=48; trigger=0; if (tick==0) trigger=keys;
        // example:__padrep:start
        result=__padrep(actions,keys,trigger,48); // A|B: select A, the lower bit.
        if (result!=0) action_pulses++;
        // example:__padrep:end
        if (tick==0 || tick==3 || tick==5 || tick==7) expect(result,16);
        else expect(result,0);
        // example:__padrep_mask:start
        result=__padrep_mask(alias_state,keys,trigger,48);
        if (result!=0) alias_pulses++;
        // example:__padrep_mask:end
        if (tick==0 || tick==3 || tick==5 || tick==7) expect(result,16);
        else expect(result,0);
        tick++;
    }
    // Both fresh directions choose Right. A continued two-direction hold pauses the counters.
    result=__padrep_lr(lr,3,3); expect(result,1);
    result=__padrep_lr(lr,3,0); expect(result,0); expect(lr[3],0);
    // Losing all eligible held buttons clears the active action and counters.
    result=__padrep_lr(lr,0,0); expect(result,0); expect(lr[0],0);
    result=__padrep_lr(lr,2,0); expect(result,0); expect(lr[0],2);
    // example:__padrep_reset:start
    __padrep_reset(lr);
    expect(lr[0],0); expect(lr[1],3); expect(lr[2],2);
    expect(lr[3],0); expect(lr[4],0);
    // example:__padrep_reset:end
    // Zero delay skips the first-delay equality path: ARR controls the first held pulse.
    __padrep_init(lr,0,2);
    result=__padrep_lr(lr,1,1); expect(result,1);
    result=__padrep_lr(lr,1,0); expect(result,0);
    result=__padrep_lr(lr,1,0); expect(result,1);
    __padrep_init(lr,1,0);
    result=__padrep_lr(lr,1,1); expect(result,1);
    result=__padrep_lr(lr,1,0); expect(result,1);
    result=__padrep_lr(lr,1,0); expect(result,1);
    // Arguments may be expressions; evaluating ARR must preserve the supplied DAS.
    left_value=1; right_value=1;
    __padrep_init(lr,3,left_value+right_value);
    expect(lr[1],3); expect(lr[2],2);
    m_text(1,0,"REPEAT STATE"); m_wait();
    m_text(1,2,"TICKS 0 3 5 7"); m_wait();
    show(4,"RIGHT PULSES",pulses); show(5,"DOWN PULSES",down_pulses);
    show(6,"ACTION PULSES",action_pulses); show(7,"ALIAS PULSES",alias_pulses);
    show(10,"CHECKS",checks); show(12,"FAILED CHECKS",failures);
    while (1) m_wait();
}
