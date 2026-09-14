// Check callback order, pool mutations and the compiler's typed near-call ABI.
// Expected screen: CALLBACK CHECK, FAILED CHECKS 000, TOTAL CHECKS 024.
#include "fc_common.h"
#include "entity.h"
#pragma bank 0
u8 failures;
u8 checks;
u8 first_failure;
u8 last_failure;
u8 calls;
u16 order;
u8 slot;
u16 stress_calls;
u8 stress_pass;
__prg_rom u8 stress_tiles[3] = {'A','B','C'};
typedef u16 (*MathFn)(u16 value, u8 delta);
typedef s8 (*SignedFn)(u8 value);
typedef __packed struct Dispatch { MathFn math; } Dispatch;
MathFn operation;
MathFn operations[2];
SignedFn signed_operation;
Dispatch dispatch;

void check(u8 condition) {
    checks++;
    if (condition == 0) {
        if (failures==0) first_failure=checks;
        last_failure=checks;
        failures++;
    }
}
void visit(u8 id) { calls++; order = order * 10 + id + 1; }
void skip_later(u8 id) { visit(id); if (id == 0) entity_destroy(1); }
void add_later(u8 id) { visit(id); if (id == 0) entity_create(3,0,0); }
void remove_self(u8 id) { calls++; entity_destroy(id); }
void stress(u8 id) { stress_calls++; if(id>=ENTITY_MAX) failures++; }
u16 add(u16 value,u8 delta) { return value + delta; }
u16 subtract(u16 value,u8 delta) { return value - delta; }
s8 negative(u8 value) { return (s8)(0-value); }
u16 nested(MathFn fn,u16 value) { return fn(value,7) + 0x1200; }

void main(void) {
    m_init(); failures=0; checks=0; calls=0; order=0;
    entity_init();
    entity_update_all(visit); entity_draw_all(visit);
    check(calls==0);
    entity_create(1,0,0); entity_create(2,0,0); entity_create(3,0,0);
    entity_update_all(0); entity_draw_all(0); check(calls==0);
    entity_update_all(skip_later); check(calls==2); check(order==13);
    calls=0; order=0; entity_draw_all(visit); check(calls==2); check(order==13);
    entity_init(); entity_create(1,0,0); entity_create(2,0,0);
    calls=0; order=0; entity_update_all(add_later); check(calls==3); check(order==123);
    calls=0; entity_update_all(remove_self); check(calls==3); check(entity_count_active()==0);
    // Full pools reject new entities with FF; inactive and invalid IDs are skipped.
    for(slot=0;slot<ENTITY_MAX;slot++) entity_create(1,0,0);
    check(entity_create(1,0,0)==0xFF);
    calls=0; entity_draw_all(visit); check(calls==ENTITY_MAX);
    entity_destroy(0xFF); check(entity_count_active()==ENTITY_MAX);
    // All these expressions must call through the stored pointer, including a 16-bit result.
    operation=add; check(operation(0x1234,7)==0x123B);
    operation=&subtract; check((*operation)(0x1234,7)==0x122D);
    dispatch.math=add; check(dispatch.math(0x2345,8)==0x234D);
    operations[0]=add; operations[1]=subtract; slot=1;
    check(operations[slot](0x3456,9)==0x344D);
    operation=add; check(nested(operation,0x1234)==0x243B);
    check(operation(operation(0x2345,2),3)==0x234A);
    signed_operation=negative; check((s16)signed_operation(7)==-7);
    check(operation(0xFFFF,1)==0); check(operation(0x00FF,1)==0x0100);
    // Keep callbacks running across NMI while copy/fill/put records share the argument scratch.
    // The last row must contain ABC, FFFF and P at tile X positions 2, 10 and 18.
    __vramq_copy(0x2222,stress_tiles,3); __vramq_fill(0x222A,'F',4); __vramq_put(0x2232,'P');
    __vramq_commit(); stress_calls=0;
    for(stress_pass=0;stress_pass<32;stress_pass++) entity_update_all(stress);
    check(stress_calls==512); check(entity_count_active()==ENTITY_MAX);
    m_text(2,0,"CALLBACK CHECK"); m_wait();
    m_text(2,7,"FAILED CHECKS"); m_number(failures); m_wait();
    m_text(2,10,"TOTAL CHECKS");
    m_put(3,11,(u8)('0'+checks/100));
    m_put(4,11,(u8)('0'+(checks/10)%10));
    m_put(5,11,(u8)('0'+checks%10)); m_wait();
    // Failure IDs identify the first and last failing assertion; successful runs show 00 00.
    m_text(2,12,"FAILURE IDS"); m_wait();
    m_put(3,13,(u8)('0'+first_failure/10)); m_put(4,13,(u8)('0'+first_failure%10));
    m_put(6,13,(u8)('0'+last_failure/10)); m_put(7,13,(u8)('0'+last_failure%10)); m_wait();
    while(1) m_wait();
}
