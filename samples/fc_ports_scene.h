// SPDX-License-Identifier: MIT
// Copyright (c) 2026 DAISUKE OBA
#ifndef FC_PORTS_SCENE_H
#define FC_PORTS_SCENE_H
#include "fc_common.h"
__location(0x0600) u8 port_result[32];
__location(0x0640) u8 key_matrix[18];
__location(0x0700) u8 port_phase;
void port_number(u8 x,u8 y,u8 value){
    m_put(x,y,'0'+value/100);m_put(x+1,y,'0'+(value/10)%10);m_put(x+2,y,'0'+value%10);
}
u8 port_hex_digit(u8 value){if(value<10)return '0'+value;return 'A'+value-10;}
void port_hex(u8 x,u8 y,u8 value){m_put(x,y,port_hex_digit(value>>4));m_put(x+1,y,port_hex_digit(value&15));}
#endif
