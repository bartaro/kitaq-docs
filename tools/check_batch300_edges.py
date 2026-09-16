"""Boundary and state tests independent of the teaching screenshots (stdlib only)."""
from pathlib import Path
import sys,json,subprocess,hashlib
from check_batch200 import dependencies
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
OUT=SITE/'verification/api-batch300/state';OUT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
def case(p,name,code,want,inc='',glob='',runtime=False,ime=None):
    folder=OUT/(p+'-'+name);folder.mkdir(exist_ok=True)
    source=folder/'case.c';rom=folder/('case.gb' if p=='gb' else 'case.nes')
    addr=0xC000 if p=='gb' else 0x600
    source.write_text(f'__location({addr}) u16 result[64];\n'+inc+'\n'+glob+'\nvoid main(){u8 i;for(i=0;i<64;i++)result[i]=0;'+code+'result[63]=0xA55A;while(1){}}',encoding='utf-8')
    lib=REPOS/('kitaq'+p)/'lib';compiler=lib.parent/('kitaq'+p+'.exe');emulator=REPOS/('kokura/kokura-cli.exe' if p=='gb' else 'kurosaki/kurosaki.exe')
    command=[str(compiler)]+([str(lib/'runtime.c')] if runtime else [])+[str(source),'-I',str(lib),'-o',str(rom),'--no-cache','--no-disasm']
    command+=['--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb','--cart=mbc5','--romsize=64k','--ramsize=8k'] if p=='gb' else ['--mapper=nrom']
    built=subprocess.run(command,cwd=folder,capture_output=True,timeout=120);(folder/'build.txt').write_bytes(built.stdout+built.stderr)
    if built.returncode:raise RuntimeError('Build '+name)
    cleanup_build_outputs(folder)
    for mode in (['dmg','cgb'] if p=='gb' else ['nrom']):
        statefile=folder/(mode+'.json')
        if p=='gb':
            command=[str(emulator),str(rom),'--hardware',mode,'--run-frames','300','--dump-report',str(statefile),'--report-sections','meta,cpu,watched_memory','--watch-fields','preview']
            for off in range(0,128,16):command+=['--watch-window',f'r{off}:{addr+off}:16']
        else:command=[str(emulator),'run',str(rom),'--frames','180','--headless','--snapshot',str(statefile)]
        run=subprocess.run(command,cwd=folder,capture_output=True,timeout=120);assert run.returncode==0,name
        state=json.loads(statefile.read_text(encoding='utf-8'))
        if p=='gb':
            watches={w['name']:w['preview_bytes'] for w in state['watched_memory']};raw=sum([watches['r'+str(off)] for off in range(0,128,16)],[])
        else:raw=state['bus']['ram'][addr:addr+128]
        actual=[raw[i]+256*raw[i+1] for i in range(0,128,2)];expected=[v&65535 for v in want]+[0]*(63-len(want))+[0xA55A]
        inputs=dependencies(source,lib)
        if runtime:inputs.update(dependencies(lib/'runtime.c',lib))
        row={'platform':p,'group':name,'mode':mode,'source':source.relative_to(SITE).as_posix(),'source_sha256':sha(source),'rom':rom.relative_to(SITE).as_posix(),'rom_sha256':sha(rom),'compiler_sha256':sha(compiler),'emulator_sha256':sha(emulator),'input_sha256':inputs,'actual':actual,'expected':expected,'passed':actual==expected}
        if ime is not None:row.update(interrupts_enabled=state['cpu']['ime']);row['passed'] &= bool(state['cpu']['ime'])==ime
        rows.append(row);print(p,name,mode,'PASS' if row['passed'] else 'FAIL',[(i,a,b) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b][:8],flush=True)
        (OUT.parent/'edge_checks.json').write_text(json.dumps({'script_sha256':sha(Path(__file__)),'records':rows},indent=2))
for p in ['gb','fc']:
    case(p,'coordinate-variables','a=255;b=1;c=250;d=0;e=10;f=2;result[0]=__xy_in_rect(a,b,c,d,e,f);a=0;result[1]=__xy_in_rect(a,b,c,d,e,f);a=250;e=0;result[2]=__xy_in_rect(a,b,c,d,e,f);a=255;b=255;c=0;d=0;result[3]=__manhattan(a,b,c,d);result[4]=__map_index(a,b,a);',[1,0,0,254,65280],inc='#include "rpg.h"' if p=='gb' else '#include "intrinsics.h"',glob='u8 a;u8 b;u8 c;u8 d;u8 e;u8 f;')
for finish,enabled in [('inner',False),('outer',True)]:
    code='*((u8*)0xFFFF)=0;a=__critical_enter();b=__critical_enter();result[0]=a;result[1]=b;__critical_leave(b);'
    if enabled:code+='__critical_leave(a);'
    case('gb','critical-'+finish,code,[0,1],glob='u8 a;u8 b;',ime=enabled)
case('gb','bullet-capacity','danmaku_reset();for(i=0;i<96;i++)danmaku_spawn(40,40,0,0);result[0]=dm_count;result[1]=dm_peak;result[2]=danmaku_spawn(40,40,0,0);result[3]=dm_rejected;result[4]=danmaku_spawn(255,40,0,0);result[5]=dm_rejected;dm_spawned=65535;danmaku_clear();danmaku_spawn(0,0,-16,0);result[6]=dm_spawned;danmaku_clear_map();danmaku_step();result[7]=dm_count;danmaku_fan(40,40,32,4,255,255);result[8]=dm_count;result[9]=dm_bullets[1].vx;danmaku_reset();result[10]=dm_peak;result[11]=dm_spawned;result[12]=dm_rejected;',[96,96,0,1,0,1,0,0,96,64,0,0,0],inc='#include "danmaku.c"\n#pragma bank 0')
case('gb','bullet-collision','danmaku_reset();dm_player_x=42;dm_player_y=42;dm_invulnerable=0;danmaku_spawn(40,40,0,0);danmaku_clear_map();danmaku_step();result[0]=dm_hit;result[1]=dm_graze;result[2]=dm_map[165];danmaku_step();result[3]=dm_graze;dm_invulnerable=1;danmaku_step();result[4]=dm_hit;danmaku_clear();dm_invulnerable=0;dm_player_x=50;danmaku_spawn(40,40,0,0);danmaku_step();result[5]=dm_graze;result[6]=dm_hit;dm_player_x=51;danmaku_clear();danmaku_spawn(40,40,0,0);danmaku_step();result[7]=dm_graze;danmaku_clear();dm_map[165]=100;danmaku_spawn(40,40,0,0);danmaku_spawn(44,40,0,0);danmaku_step();result[8]=dm_map[165];',[1,1,1,0,0,1,0,0,3],inc='#include "danmaku.c"\n#pragma bank 0')
case('gb','save-maximum','for(i=0;i<255;i++)payload[i]=i;payload[505]=99;result[0]=save_write(2,payload,506);payload[505]=0;result[1]=save_load(2,payload,506);result[2]=payload[505];result[3]=payload[254];result[4]=save_write(2,payload,507);result[5]=save_exists(2);save_clear(255);result[6]=save_exists(2);save_clear(2);result[7]=save_exists(2);',[1,1,99,254,0,1,1,0],inc='#include "save.c"',glob='u8 payload[506];')
case('gb','path-boundaries','level.width=4;level.height=3;level.bank_tiles=0;level.tiles=cells;level.collision_bits=0;level.events=0;map_load(0,&level);costs[0]=77;range_fill_move(4,0,3,costs);result[0]=costs[0];range_fill_move(0,0,0,costs);result[1]=costs[0];result[2]=costs[1];route[0]=66;result[3]=path_find_bfs(0,0,3,2,route,4);result[4]=route[0];result[5]=path_find_bfs(0,0,0,0,route,10);result[6]=path_find_bfs(4,0,0,0,route,10);result[7]=map_is_blocked(3,2);result[8]=map_trigger_at(3,2);',[77,0,255,0,66,0,0,0,0],inc='#include "map.c"\n#include "slg_path.c"',glob='map_t level;u8 cells[12];u8 costs[12];u8 route[10];')
case('gb','camera-clamp','level.width=32;level.height=24;level.bank_tiles=0;level.tiles=cells;level.collision_bits=0;level.events=0;map_load(0,&level);camera_center(31,23);result[0]=*((u8*)0xFF43);result[1]=*((u8*)0xFF42);camera_center(0,0);result[2]=*((u8*)0xFF43);result[3]=*((u8*)0xFF42);',[96,48,0,0],inc='#include "map.c"',glob='map_t level;__prg_rom u8 cells[768]={0};')
inc='#include "runtime.h"\n#include "nametable_asset.c"\n#include "attribute.c"'
case('fc','attribute-bounds','nes_attr_shadow_clear(0);nes_attr_shadow_fill_rect(31,29,1,1,7);result[0]=nes_attr_shadow[63];nes_attr_shadow_fill_rect(31,29,2,1,1);nes_attr_shadow_fill_rect(255,255,1,1,1);nes_attr_shadow_fill_rect(0,0,0,1,1);result[1]=nes_attr_shadow[63];nes_vram_queue_clear();result[2]=nes_attr_queue_rect(0x2000,31,29,1,1);result[3]=nes_vram_queue_used;result[4]=nes_attr_queue_rect(0x2000,31,29,2,1);result[5]=nes_attr_queue_rect(0x2000,255,255,0,0);result[6]=nes_vram_queue_used;nes_attr_shadow_clear(0);nes_attr_shadow_fill_rect(1,1,1,1,2);result[7]=nes_attr_shadow[0];',[12,12,1,4,0,1,4,2],inc=inc,runtime=True)
case('fc','queue-partial','nes_vram_queue_clear();nes_vram_queue_try_write(0x2000,payload,127);nes_vram_queue_try_write(0x2100,payload,50);result[0]=nes_vram_queue_used;result[1]=nes_nt_queue_rect(0x2000,0,0,4,2,4,payload);result[2]=nes_vram_queue_used;result[3]=nes_vram_queue_overflow;nes_vram_queue_clear();result[4]=nes_attr_queue_rect(0x2000,0,0,32,30);result[5]=nes_vram_queue_used;result[6]=nes_nt_queue_fill_rect(0x2000,0,0,2,0,1);result[7]=nes_vram_queue_used;',[183,0,190,1,1,88,1,88],inc=inc,glob='u8 payload[127];',runtime=True)
case('fc','actor-wrapping','nes_actor_set_world(&a,0,260);nes_actor_update_screen(&a,1,0);result[0]=a.screen_x;result[1]=a.screen_y;a.width=8;a.height=8;b.width=8;b.height=8;nes_actor_set_world(&a,100,100);nes_actor_set_world(&b,108,100);result[2]=nes_actor_collide(&a,&b);nes_actor_set_world(&b,107,107);result[3]=nes_actor_collide(&a,&b);nes_actor_set_world(&b,99,99);result[4]=nes_actor_collide(&a,&b);',[255,4,0,1,1],inc='#include "runtime.h"\n#include "metasprite.c"\n#include "actor.c"',glob='struct NesActor a;struct NesActor b;',runtime=True)
if not all(r['passed'] for r in rows):raise SystemExit(1)
