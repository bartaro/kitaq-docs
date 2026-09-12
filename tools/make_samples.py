"""Original small programs for the Japanese programming manuals."""
from pathlib import Path
import json
S=Path(__file__).resolve().parents[1]
D=S/'samples'

def write(p,t):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='utf-8')
def main():
 from font_asset import convert
 gbfont,fcfont=convert()
 (D/'font.chr').write_bytes(fcfont)
 write(D/'font_gb.h','// Derived without glyph changes from samples/assets/ascii.c (user-specified).\n// ASCII-indexed GB 2bpp tiles; see verification/font_conversion.json.\n__prg_rom u8 manual_font[] = {\n'+',\n'.join(','.join(str(x) for x in gbfont[i:i+32]) for i in range(0,len(gbfont),32))+'\n};\n')
 write(D/'gb_common.h','''#pragma once
// Include this small support file once per program.
#include "font_gb.h"
__location(0xFF40) u8 M_LCDC;
__location(0xFF47) u8 M_BGP;
__location(0xFF48) u8 M_OBP0;
void __wait_vblank();
void __vram_fill(u16 dst, u8 value, u16 len);
void __vram_copy(u16 dst, const void* src, u16 len);
void __settile_xy(u8 x, u8 y, u8 tile);
void m_init() {
    __wait_vblank(); M_LCDC = 0; M_BGP = 0xE4; M_OBP0 = 0xE4;
    __vram_copy(0x8000, manual_font, 2048);
    __vram_fill(0x9800, 0, 1024); M_LCDC = 0x91;
}
void m_put(u8 x,u8 y,u8 ch) { __settile_xy(x,y,ch); }
void m_wait() { __wait_vblank(); }
void m_text(u8 x,u8 y,const u8* text) {
    while (*text != 0) { m_put(x,y,*text); x++; text++; }
}
void m_number(u8 value) {
    m_put(3,8,(u8)('0'+value/100));
    m_put(4,8,(u8)('0'+(value/10)%10));
    m_put(5,8,(u8)('0'+value%10));
}
''')
 write(D/'fc_common.h','''#ifndef MANUAL_FC_COMMON_H
#define MANUAL_FC_COMMON_H
#include "intrinsics.h"
#ifdef MANUAL_FC_RUNTIME
#include "runtime.h"
#endif
__prg_rom u8 manual_pal[16] = {0x0F,0x30,0x10,0x30,0x0F,0x30,0x10,0x30,0x0F,0x30,0x10,0x30,0x0F,0x30,0x10,0x30};
void m_init(void) {
    __ppu_off(); __vramq_clear(); __oam_clear();
#ifdef MANUAL_FC_RUNTIME
    nes_vram_queue_clear();
#endif
    __palette_bg_load(manual_pal);
    __nametable_rect(0,0,32,30,0);
    __scroll_set(0,0); __ppu_ctrl_set(0x80); __ppu_mask_set(0x0A);
}
#ifdef MANUAL_FC_RUNTIME
void m_put(u8 x,u8 y,u8 ch) { nes_vram_queue_try_write((u16)(0x2000+(u16)y*32+x),&ch,1); }
void m_wait(void) { nes_wait_nmi(); __scroll_set(0,0); }
#else
void m_put(u8 x,u8 y,u8 ch) { __vramq_put((u16)(0x2000+(u16)y*32+x),ch); }
void m_wait(void) { __vramq_commit(); __nmi_wait(); __scroll_set(0,0); }
#endif
void m_text(u8 x,u8 y,const u8* text) {
    while (*text != 0) { m_put(x,y,*text); x++; text++; }
}
void m_number(u8 value) {
    m_put(3,8,(u8)('0'+value/100));
    m_put(4,8,(u8)('0'+(value/10)%10));
    m_put(5,8,(u8)('0'+value%10));
}
#endif
''')
 demos=[]
 def demo(platform,name,title,body,libs='',decl='',includes='',expect='',loop='',opts=None):
  filename=platform+'_'+name+'.c'
  text='// '+title+'\n// Expected: '+expect+'\n#include "'+platform+'_common.h"\n'+includes+'\n'+decl+'\nvoid main(void) {\n    m_init();\n    m_text(2,3,"'+name.upper().replace('_',' ')[:16]+'");\n'+body+'\n    while (1) { m_wait(); '+loop+' }\n}\n'
  if platform=='gb': text=text.replace('main(void)','main()')
  if platform=='fc' and name=='scene': text='#define MANUAL_FC_RUNTIME 1\n'+text
  write(D/filename,text)
  demos.append(dict(id=platform+'_'+name,platform=platform,title=title,file=filename,libs=libs.split(),expected=expect,options=opts or [],kind='original'))
 for p in ['gb','fc']:
  demo(p,'font','指定ascii.cの英数字・記号一覧','''    m_text(2,5,"ABCDEFGHIJKLMNOP"); m_wait();
    m_text(2,6,"QRSTUVWXYZ"); m_wait();
    m_text(2,8,"0123456789"); m_wait();
    m_text(2,10,"abcdefghijklmnop"); m_wait();
    m_text(2,11,"qrstuvwxyz"); m_wait();
    m_text(2,13,"!#$%&'()*+,-./"); m_wait();
    m_text(2,14,":;<=>?@[]^_`{}~"); m_wait();
    m_put(16,13,34); m_wait();''',expect='Uppercase, lowercase, numbers and all 30 supplied punctuation glyphs')
  demo(p,'hello','最初の画面表示','    m_text(2,5,"HELLO WORLD");\n    m_number(42);',expect='HELLO WORLD and 042')
  demo(p,'arithmetic','変数・算術・型変換','    u16 sum;\n    sum = (u16)200 + 100;\n    m_number((u8)(sum / 10));',expect='030')
  demo(p,'control','条件分岐と繰り返し','''    u8 i; u8 sum; sum=0;
    for (i=0;i<8;i++) { if (i==3) continue; sum=(u8)(sum+i); }
    while (sum<30) { sum++; }
    do { sum++; } while (sum<32);
    switch (sum) { case 32: sum=42; break; default: sum=0; break; }
    m_number(sum);''' if p=='gb' else '''    u8 i; u8 sum; sum=0;
    for (i=0;i<8;i++) { if (i==3) continue; sum=(u8)(sum+i); }
    while (sum<32) { sum++; }
    if (sum==32) sum=42; else sum=0;
    m_number(sum);''',expect='042')
  demo(p,'aggregate','関数・配列・構造体・ポインタ','''    Point a; Point b; u8 i; u8 data[4]; u8* ptr;
    a.x=10; a.y=20; b=a; ptr=data;
    for(i=0;i<4;i++) ptr[i]=(u8)(i+1);
    m_number((u8)(add(b.x,b.y)+ptr[0]+ptr[1]+ptr[3]+5));''',decl='typedef struct { u8 x; u8 y; } Point;\nu8 add(u8 a,u8 b) { return (u8)(a+b); }',expect='042')
  demo(p,'bits_memory','ビット操作・メモリ転送','''    u8 data[4]; u8 copy[4];
    __memset(data,0,4); __bit_set(data,3); __bit_toggle(data,1);
    __memcpy(copy,data,4); m_number(copy[0]);''',includes=('void __memset(void* dst,u8 value,u16 len);\nvoid __memcpy(void* dst,const void* src,u16 len);\nvoid __bit_set(u8* base,u16 bit);\nvoid __bit_toggle(u8* base,u16 bit);' if p=='gb' else ''),expect='010')
  demo(p,'input','ボタン入力と押した瞬間','    input_init();\n    m_number(0);','input.c',decl='u8 manual_count;',includes='#include "input.h"',loop='input_update(); if(input_pressed(BTN_A)) { manual_count++; m_number(manual_count); }',expect='000 initially; A increments once per press')
  demo(p,'fixed','固定小数点Q8.8','    fix8 a; fix8 b; a=fix_from_int(3); b=fix_from_int(4);\n    m_number((u8)fix_to_int(fix_mul(a,b)));','fixed.c',includes='#include "fixed.h"',expect='012')
  demo(p,'entity','固定長オブジェクトプール','    u8 id; entity_init(); id=entity_create(1,20,30);\n    if(id!=0xFF) entity_get(id)->vx=2; m_number(entity_count_active());','entity.c',includes='#include "entity.h"',expect='001')
  demo(p,'debug','値の記録とアサート','    debug_init(); debug_set_frame(1); debug_trace_u8("HP",42);\n    m_number(debug_get_trace_count());','debug.c',includes='#include "debug.h"',expect='001; trace log contains HP=42')
  demo(p,'chain','座標履歴のリングバッファ','    chain_init(&trail,points,4); chain_push_head(&trail,20,30);\n    m_number(42);','chain.c',decl='Chain trail; ChainPoint points[4];',includes='#include "chain.h"',expect='042; history contains (20,30)')
  demo(p,'system','フレームカウンター','    system_init(); system_wait_vblank(); system_wait_vblank();\n    m_number(system_get_frame8());','system.c',includes='#include "system.h"',expect='002')
  demo(p,'scene','シーン番号の切替','    scene_init(manual_scenes,2); scene_change(1);\n    m_number(scene_get_current());','scene.c',decl='SceneDef manual_scenes[2];',includes='#include "scene.h"',expect='001; no callbacks registered')
  if p=='fc': demos[-1]['libs'].insert(0,'runtime.c')
 demo('gb','camera','世界座標から画面座標へ','    Camera_Init(&cam); Camera_Set(&cam,2560,0);\n    m_number((u8)Camera_WorldToScreenX(&cam,52));','scroll.c camera.c',decl='Camera8_8 cam;',includes='#include "camera.h"',expect='042: world x=52 minus camera x=10')
 demo('gb','rle','連長圧縮データの展開','    u8 out[3]; rle_decode(out,packed); m_number(out[2]);','rle.c',decl='__prg_rom u8 packed[] = {3,42,0};',includes='#include "rpg.h"',expect='042; three bytes each equal to 42')
 demo('gb','board','盤面の読み書き','    slg_board_init(&board,4,4,cells); slg_board_clear(&board,0);\n    slg_board_set(&board,2,1,42); m_number(slg_board_get(&board,2,1));','slg_board.c',decl='SLGBoard board; u8 cells[16];',includes='#include "slg.h"',expect='042')
 demo('gb','physics','矩形の運動を1ステップ','    kq2d_world_init(&world,boxes,1);\n    kq2d_body_init(&boxes[0],40,40,4,4);\n    kq2d_body_set_velocity(&boxes[0],2,0);\n    world.gravity_x=0; world.gravity_y=0;\n    kq2d_step(&world); m_number((u8)boxes[0].x);','fixed.c physics2d.c',decl='KQWorld2D world; KQBody2D boxes[1];',includes='#include "physics2d.h"',expect='042: integer pixel coordinates')
 demo('gb','link','通信が届かない場合の扱い','    u8 value; Link_InitMaster(); Link_BeginTransfer(42);\n    if(Link_WaitByte(4,&value)) m_number(value);\n    else { Link_Cancel(); m_number(0); }','link_hwregs_gb.c link.c',includes='#include "link.h"',expect='255 for disconnected link; 000 if timeout; peer value when connected')
 demo('gb','bank','バンク番号付きデータ','    far_data_read(0,values,copied,2); m_number(copied[1]);','bank.c',decl='__prg_rom u8 values[] = {7,42}; u8 copied[2];',includes='#include "bank.h"',expect='042; bank 0 fixed-ROM data copy')
 demo('gb','asset','素材IDからRAMへ読み込む','    table[0].type=ASSET_TYPE_RAW; table[0].bank=0;\n    table[0].ptr=values; table[0].len=2;\n    asset_set_table(0,table,1); asset_load_raw(0,copied,2);\n    m_number(copied[1]);','asset.c',decl='AssetDesc table[1]; __prg_rom u8 values[] = {7,42}; u8 copied[2];',includes='#include "asset.h"',expect='042')
 demo('gb','danmaku','弾プールの生成と個数','    danmaku_reset(); danmaku_spawn(40,40,16,0);\n    m_number(dm_count);','danmaku.c',includes='#include "danmaku.h"',expect='001; numeric pool example, no bullet BG compositor')
 demo('fc','subpixel','Q5.3の1/8画素を整数座標へ加算','    KQ2DPosition x; KQ2DFraction frac; KQ2DSpeed speed; u8 i;\n    x=40; frac=0; speed=2;\n    for(i=0;i<8;i++) {\n        frac=(u8)(frac+speed);\n        x=(u8)(x+(frac>>KQ2D_SUBPIXEL_BITS));\n        frac=(u8)(frac & KQ2D_SUBPIXEL_MASK);\n    }\n    m_number(x);',includes='#include "physics2d.h"',expect='042; explicit game-side integration using header constants')
 demo('gb','cgb_palette','CGBの色指定','    cgb_bg_rgb(0,0,31,31,31); cgb_bg_rgb(0,3,12,0,22);\n    m_number(42);','cgb_palette.c',includes='#include "cgb_palette.h"',expect='042 in purple on white; CGB mode',opts=['--cgb=cgb'])
 demo('gb','scroll','背景スクロール','    Scroll_SetBg(0,0);','scroll.c',includes='#include "scroll.h"',decl='u8 phase;',loop='phase++; Scroll_SetBg(phase,0);',expect='title moves left as SCX increases')
 demo('gb','vram_queue','VRAM更新キュー','    vram_init();\n    vram_queue_bg_tile(3,8,52); vram_flush();','vram.c',includes='#include "vram.h"',expect='4 at (3,8)')
 demo('gb','sprite','スプライトとOAM DMA','    sprite_init(); sprite_set_tile(sprite_alloc(),65);\n    sprite_set_pos(0,70,80); M_LCDC=(u8)(M_LCDC|2);','sprite.c',includes='#include "sprite.h"',loop='sprite_flush_oam_now();',expect='letter A at sprite position')
 demo('gb','rng','乱数とseed','    rng_seed(1234); m_number(rng_range(10));','rng.c',includes='#include "rpg.h"',expect='value 000 through 009; same seed repeats')
 demo('gb','flags','フラグとクエスト状態','    flag_clear(12); flag_set(12); m_number(flag_get(12));','flags.c',includes='#include "rpg.h"',expect='001')
 demo('gb','circle','円の物理計算','''    kq2dc_world_init(&world,balls,1);
    balls[0].active=1; balls[0].x=40; balls[0].y=40;
    balls[0].radius=4; balls[0].inv_mass_q8=256;
    balls[0].vx=2; balls[0].vy=0;
    world.gravity_x=0; world.gravity_y=0; world.linear_damping_q8=255;
    kq2dc_step(&world); m_number((u8)balls[0].x);''','physics2d_circle.c',decl='KQCircleBody2D balls[1]; KQCircleWorld2D world;',includes='#include "physics2d_circle.h"',expect='042 after one step; this example uses integer pixels')
 demo('fc','scroll','NESの背景スクロール','    __scroll_set(0,0);',decl='u8 phase;',loop='phase++; __scroll_set(phase,0);',expect='title scrolls horizontally')
 demo('fc','vram_queue','NMIでVRAM更新','    __vramq_put(0x2103,52); __vramq_commit();',expect='4 at (3,8)')
 demo('fc','sprite','NESのOAM','    __palette_sp_load(manual_pal); __sprite_set(0,70,80,65,0);\n    __ppu_mask_set(0x1E);',loop='__oam_dma();',expect='A sprite on screen')
 demo('fc','sound','内蔵APUの効果音','    nes_apu_init(); nes_sfx_square1(0xBF,400,20);\n    m_number(42);','audio.c',includes='#include "audio.h"',expect='042 and a pulse tone')
 demo('gb','sound','GBの効果音','    Audio_Init(); Audio_PlaySFX(tone,1); m_number(42);','audio_hwregs_gb.c audio.c',includes='#include "audio.h"',decl='__prg_rom u8 tone[] = { 24,0xF0,24,0xE0,24,0xC0,24,0xA0,24,0x80,24,0x60,0 };',loop='Audio_Update();',expect='042 and a short pulse tone')
 (D/'manifest.json').write_text(json.dumps(demos,ensure_ascii=False,indent=2),encoding='utf-8')
 print('Created',len(demos),'complete programs')
if __name__=='__main__': main()
