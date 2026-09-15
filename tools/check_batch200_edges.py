"""Exercise boundaries and controller paths independently of the teaching screenshots."""
from pathlib import Path
import subprocess,json,hashlib,argparse
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUT=SITE/'verification/api-batch200/state';OUT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument("--platform",choices=["gb","fc"]);parser.add_argument("--only");options=parser.parse_args()
rows=[]
def execute(platform,name,body,expected,include='',glob='',cpu_mask=None,compiler=None,ppu=None,vram=None):
 if options.platform and platform!=options.platform:return
 if options.only and name!=options.only:return
 folder=OUT/(platform+'-'+name);folder.mkdir(exist_ok=True)
 source=folder/'case.c';rom=folder/('case.gb' if platform=='gb' else 'case.nes')
 source.write_text(include+'\n__location('+('0xC700' if platform=='gb' else '0x0700')+') u16 result[64];\n'+glob+'\nvoid main(){u8 i;for(i=0;i<64;i++)result[i]=0;'+body+'result[63]=0xA55A;while(1){}}',encoding='utf-8')
 lib=REPOS/('kitaq'+platform)/'lib';compiler=compiler or lib.parent/('kitaq'+platform+'.exe')
 command=[str(compiler),str(source),'-I',str(lib),'-o',str(rom),'--no-cache','--no-disasm']
 if platform=='fc' and ('scene.c' in include or 'palette.c' in include):command.insert(1,str(lib/'runtime.c'))
 if platform=='gb':command+=['--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb']
 build=subprocess.run(command,cwd=folder,capture_output=True,timeout=120);(folder/'build.txt').write_bytes(build.stdout+build.stderr)
 if build.returncode:raise RuntimeError('Build failed '+name)
 for mode in (['dmg','cgb'] if platform=='gb' else ['nrom']):
  report=folder/(mode+'.json');exe=REPOS/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe')
  if platform=='gb':
   command=[str(exe),str(rom),'--hardware',mode,'--run-frames','90','--dump-report',str(report),'--report-sections','cpu,meta,watched_memory','--watch-fields','preview']
   for offset in range(0,128,16):command+=['--watch-window',f'r{offset}:{0xC700+offset}:16']
  else:command=[str(exe),'run',str(rom),'--frames','90','--headless','--snapshot',str(report)]
  run=subprocess.run(command,cwd=folder,capture_output=True,timeout=120)
  if run.returncode:raise RuntimeError('Run failed '+name)
  state=json.loads(report.read_text(encoding='utf-8'))
  if platform=='gb':
   watches={w['name']:w['preview_bytes'] for w in state['watched_memory']};raw=sum([watches['r'+str(i)] for i in range(0,128,16)],[])
  else:raw=state['bus']['ram'][0x700:0x780]
  actual=[raw[i]+raw[i+1]*256 for i in range(0,128,2)];want=[v&65535 for v in expected]+[0]*(63-len(expected))+[0xA55A]
  row={'platform':platform,'name':name,'mode':mode,'source':source.relative_to(SITE).as_posix(),'source_sha256':sha(source),'rom':rom.relative_to(SITE).as_posix(),'rom_sha256':sha(rom),'compiler_sha256':sha(compiler),'emulator_sha256':sha(exe),'actual':actual,'expected':want,'passed':actual==want}
  if cpu_mask is not None:
   cpu=state['cpu'];mask=bool(cpu.get('ime')) if platform=='gb' else not bool(cpu['p']&4)
   row.update(interrupts_enabled=mask,expected_interrupts_enabled=cpu_mask);row['passed'] &= mask==cpu_mask
  if ppu is not None:
   measured={k:state['bus']['ppu'][k] for k in ppu};row.update(ppu=measured,expected_ppu=ppu);row['passed'] &= measured==ppu
  if vram is not None:
   measured={str(k):state['bus']['ppu']['vram'][k] for k in vram};want_vram={str(k):v for k,v in vram.items()};row.update(vram=measured,expected_vram=want_vram);row['passed'] &= measured==want_vram
  rows.append(row);print(platform,name,mode,'PASS' if row['passed'] else 'FAIL',flush=True)
  (OUT.parent/(('edge_'+str(options.platform)+'_'+str(options.only)+'.json') if options.platform or options.only else 'edge_checks.json')).write_text(json.dumps({'records':rows,'script_sha256':sha(Path(__file__))},indent=2),encoding='utf-8')

def main():
 inc='#include "camera.c"\n#include "scroll.c"';glob='Camera8_8 cam;'
 execute('gb','camera-negative','Camera_Init(&cam);Camera_Set(&cam,-384,-1);result[0]=Camera_WorldToScreenX(&cam,0);result[1]=Camera_WorldToScreenY(&cam,0);result[2]=Camera_ScreenToWorldX(&cam,0);result[3]=Camera_ScreenToWorldY(&cam,0);',[2,1,-2,-1],inc,glob)
 execute('gb','camera-quantization','Camera_Init(&cam);Camera_SetTarget(&cam,1,-1);Camera_StepTowardTarget(&cam,7);result[0]=cam.fx;result[1]=cam.fy;result[2]=cam.use_target;Camera_StepTowardTarget(&cam,0);result[3]=cam.fx;result[4]=cam.fy;result[5]=cam.use_target;',[0,-1,1,1,-1,0],inc,glob)
 execute('gb','camera-shift-limit','Camera_Init(&cam);Camera_SetTarget(&cam,256,-256);Camera_StepTowardTarget(&cam,255);result[0]=cam.fx;result[1]=cam.fy;',[2,-2],inc,glob)
 execute('gb','camera-outside-target','Camera_Init(&cam);Camera_SetBounds(&cam,0,0,256,256);Camera_SetTarget(&cam,512,512);Camera_StepTowardTarget(&cam,1);result[0]=cam.fx;result[1]=cam.use_target;Camera_StepTowardTarget(&cam,1);result[2]=cam.fx;result[3]=cam.use_target;Camera_StepTowardTarget(&cam,0);result[4]=cam.fx;result[5]=cam.use_target;',[256,1,256,1,256,0],inc,glob)
 execute('gb','camera-small-world','Camera_Init(&cam);Camera_Set(&cam,256,512);Camera_ClampToSize(&cam,100,100,160,144);result[0]=cam.fx;result[1]=cam.fy;result[2]=cam.max_fx;result[3]=cam.max_fy;Camera_ClearBounds(&cam);Camera_SetTarget(&cam,10,20);Camera_ClearTarget(&cam);Camera_StepTowardTarget(&cam,0);result[4]=cam.fx;result[5]=cam.target_fx;',[0,0,0,0,0,10],inc,glob)
 inc='#include "slg_board.c"';glob='SLGBoard b;u8 cells[300];SLGMoveList list;SLGUndoStack undo;SLGMove records[2];SLGMove out;'
 execute('gb','board-offset-299','slg_board_init(&b,20,15,cells);slg_board_clear(&b,3);slg_board_set(&b,19,14,9);result[0]=cells[0];result[1]=cells[298];result[2]=cells[299];result[3]=slg_board_get(&b,19,14);slg_board_set(&b,20,14,8);result[4]=cells[299];',[3,3,9,9,9],inc,glob)
 execute('gb','board-null-empty','slg_board_clear(0,9);slg_board_set(0,0,0,9);result[0]=slg_board_get(0,0,0);cells[0]=42;slg_board_init(&b,0,0,cells);slg_board_clear(&b,9);result[1]=cells[0];result[2]=slg_board_get(&b,0,0);',[0,42,0],inc,glob)
 execute('gb','move-null-zero','result[0]=slg_move_list_push(0,1,2,3);slg_move_list_clear(0);slg_move_list_init(&list,records,0);result[1]=slg_move_list_push(&list,1,2,3);result[2]=list.count;',[0,0,0],inc,glob)
 execute('gb','undo-discard-lifo','slg_undo_init(&undo,records,2);slg_undo_push(&undo,1,2,3);slg_undo_push(&undo,4,5,6);result[0]=slg_undo_pop(&undo,0);result[1]=undo.count;result[2]=slg_undo_pop(&undo,&out);result[3]=out.x;result[4]=out.y;result[5]=out.value;result[6]=slg_undo_pop(&undo,&out);result[7]=out.value;result[8]=slg_undo_pop(0,&out);result[9]=slg_undo_push(0,1,2,3);',[1,1,1,1,2,3,0,3,0,0],inc,glob)
 inc='#include "scroll.c"';glob='__location(0xFF40)u8 lcd;__location(0xFF43)u8 sx;__location(0xFF42)u8 sy;__location(0xFF4B)u8 wx;__location(0xFF4A)u8 wy;'
 for kind in ['bg','win']:
  set2='__scroll_'+kind+'_set';gx='__scroll_'+kind+'_x_get';gy='__scroll_'+kind+'_y_get';px='sx' if kind=='bg' else 'wx';py='sy' if kind=='bg' else 'wy'
  execute('gb',kind+'-tracked-getter',f'lcd=0;{set2}(10,20);{px}=99;{py}=88;result[0]={gx}();result[1]={gy}();result[2]={px};result[3]={py};',[10,20,99,88],inc,glob)
  execute('gb',kind+'-cancel-pending',f'lcd=0;{set2}(10,20);{set2}_buffered(30,40);__scroll_{kind}_x_set(50);__scroll_flush();result[0]={px};result[1]={py};{set2}_buffered(60,70);__scroll_{kind}_y_set(80);__scroll_flush();result[2]={px};result[3]={py};',[50,20,50,80],inc,glob)
  execute('gb',kind+'-partial-buffer',f'lcd=0;{set2}(10,20);__scroll_{kind}_x_set_buffered(30);__scroll_flush();result[0]={px};result[1]={py};__scroll_{kind}_y_set_buffered(40);__scroll_flush();result[2]={px};result[3]={py};',[30,20,30,40],inc,glob)
  execute('gb',kind+'-add-wrap',f'lcd=0;{set2}(0,255);{set2}_buffered(8,9);__scroll_{kind}_add(-1,1);__scroll_flush();result[0]={px};result[1]={py};',[255,0],inc,glob)
 inc='#include "scroll.c"';glob='__location(0xFF40)u8 lcd;__location(0xFF41)u8 stat;__location(0xFF45)u8 lyc;__location(0xFFFF)u8 ie;'
 execute('gb','split-empty','lcd=0;ie=0;Scroll_SplitReset();Scroll_SplitCommit();result[0]=ie;result[1]=stat&64;',[0,0],inc,glob)
 execute('gb','split-arm-reset','lcd=0;ie=4;Scroll_SplitReset();Scroll_SplitPush(32,8,0);Scroll_SplitCommit();result[0]=ie;result[1]=stat&64;result[2]=lyc;Scroll_SplitReset();result[3]=stat&64;result[4]=ie;',[7,64,32,0,7],inc,glob)
 glob+='__location(0xFF43)u8 sx;__location(0xFF42)u8 sy;__location(0xFF4B)u8 wx;__location(0xFF4A)u8 wy;'
 execute('gb','split-eight-capacity','lcd=0;ie=0;Scroll_Init();Scroll_WindowHide();Scroll_SplitReset();for(i=0;i<9;i++)Scroll_SplitPush(i*16,i*8,0);lcd=0x91;Scroll_SplitCommit();__wait_ly(144);__wait_ly(136);result[0]=sx;result[1]=Scroll_GetBgX();',[56,0],inc,glob)
 execute('gb','split-zero-show-priority','lcd=0;ie=0;Scroll_Init();Scroll_WindowHide();Scroll_SplitReset();Scroll_SplitPushEx(0,20,30,47,40,15);lcd=0x91;Scroll_SplitCommit();__wait_ly(144);__wait_ly(32);result[0]=sx;result[1]=sy;result[2]=wx;result[3]=wy;result[4]=lcd&32;result[5]=Scroll_GetBgX();result[6]=Scroll_GetWindowX();',[20,30,47,40,32,0,7],inc,glob)
 execute('gb','split-unknown-flags','lcd=0;ie=0;Scroll_Init();Scroll_SplitReset();Scroll_SplitPushEx(0,20,30,47,40,224);lcd=0x91;Scroll_SplitCommit();__wait_ly(144);__wait_ly(32);result[0]=sx;result[1]=sy;result[2]=wx;result[3]=wy;',[0,0,7,0],inc,glob)
 inc='#include "tilemap.c"';glob='struct NesTilemap map;u8 tiles[9];'
 execute('fc','tilemap-limits','for(i=0;i<9;i++)tiles[i]=0;tiles[4]=5;tiles[8]=255;map.tiles=tiles;map.width=3;map.height=3;map.solid_from=5;result[0]=nes_tilemap_get(&map,3,0);result[1]=nes_tilemap_point_solid(&map,2,2);result[2]=nes_tilemap_world_box_solid(&map,0,0,24,24);tiles[8]=0;result[3]=nes_tilemap_world_box_solid(&map,0,0,24,24);result[4]=nes_world_to_tile8_x(2047);result[5]=nes_world_to_tile8_x(2048);result[6]=nes_world_to_tile8_y(65535);result[7]=nes_tilemap_world_box_solid(&map,8,8,1,1);',[255,1,1,0,255,0,255,1],inc,glob)
 inc='#include "intrinsics.h"\n#include "scroll.c"'
 # Capture actual PPU register state after each complete scroll operation.
 for n,x,y,ctrl in [('origin',0,0,0),('cross-x',264,16,1),('cross-y',8,272,2),('wrap512',520,528,0)]:
  execute('fc','scroll-'+n,f'__ppu_off();nes_scroll_set_base_ctrl(3);nes_scroll_set({x},{y});nes_scroll_apply();',[],inc,ppu={'ctrl':ctrl,'scroll_x':x&255,'scroll_y':y&255})
 execute('fc','scroll-underflow','__ppu_off();nes_camera_follow_center(0,0,128,120);result[0]=nes_scroll_camera_x;result[1]=nes_scroll_camera_y;',[65408,65416],inc)
 inc='#include "palette.c"\n#include "runtime.h"';glob='__location(0x0400)u8 src[192];u8 four[4];'
 setup='__ppu_off();__ppu_ctrl_set(0);nes_vram_queue_clear();for(i=0;i<192;i++)src[i]=15;four[0]=15;four[1]=22;four[2]=18;four[3]=26;'
 execute('fc','palette-copy-only',setup+'src[5]=22;nes_palette_copy(src);src[5]=26;result[0]=nes_palette_shadow[5];',[22],inc,glob,ppu={'data_writes':0})
 execute('fc','palette-queue-full',setup+'nes_vram_queue_try_write(0x2000,src,127);nes_vram_queue_try_write(0x2080,src,59);src[5]=26;result[0]=nes_palette_queue_all(src);result[1]=nes_palette_shadow[5];result[2]=nes_vram_queue_used;result[3]=nes_palette_queue_bg4(1,four);result[4]=nes_palette_shadow[5];result[5]=nes_palette_queue_sprite4(2,four);result[6]=nes_palette_shadow[25];',[0,26,192,0,22,0,22],inc,glob,ppu={'data_writes':0})
 for palidx in [0,3]:
  colors=[0]*32;colors[palidx*4:palidx*4+4]=[15,22,18,26]
  execute('fc','palette-bg-'+str(palidx),setup+f'result[0]=nes_palette_queue_bg4({palidx},four);four[1]=1;result[1]=nes_vram_queue_used;nes_vram_queue_nmi_flush();result[2]=nes_palette_shadow[{palidx*4+1}];',[1,7,22],inc,glob,ppu={'data_writes':4,'palette':colors})
  colors=[0]*32;colors[palidx*4]=15;colors[16+palidx*4+1:16+palidx*4+4]=[22,18,26]
  execute('fc','palette-sp-'+str(palidx),setup+f'result[0]=nes_palette_queue_sprite4({palidx},four);result[1]=nes_vram_queue_used;nes_vram_queue_nmi_flush();result[2]=nes_palette_shadow[{16+palidx*4+1}];',[1,7,22],inc,glob,ppu={'data_writes':4,'palette':colors})
 for mode in ['apply','shadow','queue']:
  colors=[15]*32
  for index in [16,20,24,28]:colors[index]=0
  colors[0]=18;colors[5]=22
  call={'apply':'nes_palette_apply_now(src);','shadow':'nes_palette_copy(src);nes_palette_apply_shadow_now();','queue':'result[0]=nes_palette_queue_all(src);src[5]=1;nes_vram_queue_nmi_flush();'}[mode]
  execute('fc','palette-full-'+mode,setup+'src[0]=22;src[16]=18;src[5]=22;'+call+'result[1]=nes_palette_shadow[0];result[2]=nes_palette_shadow[16];',[1 if mode=='queue' else 0,22,18],inc,glob,ppu={'data_writes':32,'palette':colors})
 inc='#include "scene.c"\n#include "runtime.h"';glob='__location(0x0400)u8 src[192];'
 setup='__ppu_off();__ppu_ctrl_set(0);nes_vram_queue_clear();for(i=0;i<192;i++)src[i]=i;'
 for chunk,length,used in [(0,33,39),(1,3,12),(255,128,134),(32,0,0)]:
  body=setup+f'nes_scene_stream_begin(0x2100,src,{length},{chunk});result[0]=nes_scene_stream_step();result[1]=nes_scene_stream_state.remaining;result[2]=nes_vram_queue_used;result[3]=nes_scene_stream_state.active;nes_vram_queue_nmi_flush();'
  execute('fc',f'stream-chunk-{chunk}-len-{length}',body,[0,0,used,0],inc,glob,ppu={'data_writes':length},vram={0x2100+i:i for i in range(length)})
 execute('fc','stream-retry',setup+'nes_vram_queue_try_write(0x2000,src,127);nes_vram_queue_try_write(0x2080,src,59);nes_scene_stream_begin(0x2200,src,4,2);result[0]=nes_scene_stream_step();result[1]=nes_scene_stream_state.remaining;result[2]=nes_scene_stream_state.ppu_addr;nes_vram_queue_nmi_flush();result[3]=nes_scene_stream_step();result[4]=nes_scene_stream_state.remaining;nes_vram_queue_nmi_flush();',[1,4,0x2200,0,0],inc,glob,vram={0x2200+i:i for i in range(4)})
 execute('fc','stream-replace',setup+'nes_scene_stream_begin(0x2100,src,4,4);nes_scene_stream_step();nes_scene_stream_begin(0x2200,src+4,4,4);nes_scene_stream_step();src[0]=99;nes_vram_queue_nmi_flush();',[ ],inc,glob,vram={**{0x2100+i:i for i in range(4)},**{0x2200+i:i+4 for i in range(4)}})
 if not all(r['passed'] for r in rows):raise SystemExit(1)
if __name__=='__main__':main()
