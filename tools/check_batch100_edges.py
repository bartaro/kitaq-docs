"""Exercise boundaries and controller paths independently of the teaching screenshots."""
from pathlib import Path
import subprocess,json,hashlib,argparse
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUT=SITE/'verification/api-batch100/state';OUT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument("--platform",choices=["gb","fc"]);parser.add_argument("--only");options=parser.parse_args()
rows=[]
def execute(platform,name,body,expected,include='',glob='',cpu_mask=None,compiler=None):
 if options.platform and platform!=options.platform:return
 if options.only and name!=options.only:return
 folder=OUT/(platform+'-'+name);folder.mkdir(exist_ok=True)
 source=folder/'case.c';rom=folder/('case.gb' if platform=='gb' else 'case.nes')
 source.write_text(include+'\n__location('+('0xC700' if platform=='gb' else '0x0700')+') u16 result[64];\n'+glob+'\nvoid main(){u8 i;for(i=0;i<64;i++)result[i]=0;'+body+'result[63]=0xA55A;while(1){}}',encoding='utf-8')
 lib=REPOS/('kitaq'+platform)/'lib';compiler=compiler or lib.parent/('kitaq'+platform+'.exe')
 command=[str(compiler),str(source),'-I',str(lib),'-o',str(rom),'--no-cache','--no-disasm']
 if platform=='fc' and 'scene.c' in include:command.insert(1,str(lib/'runtime.c'))
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
  rows.append(row);print(platform,name,mode,'PASS' if row['passed'] else 'FAIL',flush=True)
  (OUT.parent/(('edge_'+str(options.platform)+'_'+str(options.only)+'.json') if options.platform or options.only else 'edge_checks.json')).write_text(json.dumps({'records':rows,'script_sha256':sha(Path(__file__))},indent=2),encoding='utf-8')
def main():
 for p in ['gb','fc']:
  # Constant and variable right shifts share an independent signed Python model.
  for signed,bits in [(True,16),(False,16),(True,8),(False,8)]:
   values=([-32768,-513,-1,0,32767] if bits==16 else [-128,-3,-1,0,127]) if signed else ([0,1,0x8000,0xFFFF] if bits==16 else [0,1,128,255])
   kind=('s' if signed else 'u')+str(bits);body='';expected=[]
   for value in values:
    for count in [0,1,4,7,8,15]:
     # Avoid shifts beyond the promoted width ambiguity for signed bytes: compiler uses its byte operand width.
     index=len(expected);body+=f'operand={value};count={count};result[{index}]=operand>>{count};result[{index+1}]=operand>>count;'
     computed=value>>count
     if bits==8 and not signed:computed &=255
     expected += [computed&65535,computed&65535]
   execute(p,'shift-'+kind,body,expected,glob=kind+' operand;u8 count;')
  body='n=0;do{n++;}while(0);result[0]=n;n=0;do{n++;if(n<3)continue;result[1]=result[1]+1;}while(n<4);result[2]=n;n=0;do{n++;if(n==2)break;}while(1);result[3]=n;n=0;tests=0;do{n++;continue;}while(++tests<3);result[4]=n;result[5]=tests;n=0;for(i=0;i<3;i++){do{n++;break;}while(1);}result[6]=n;'
  execute(p,'do-loop',body,[1,2,4,2,3,3,3],glob='u8 n;u8 tests;')
  execute(p,'chain-128','chain_init(&trail,storage,128);for(i=0;i<200;i++)chain_push_head(&trail,i,0-i);result[0]=chain_get_count(&trail);result[1]=chain_get_segment(&trail,0,&point);result[2]=point.x;result[3]=point.y;result[4]=chain_get_segment(&trail,127,&point);result[5]=point.x;result[6]=point.y;result[7]=chain_get_segment(&trail,128,&point);result[8]=point.x;result[9]=point.y;result[10]=chain_get_segment(0,0,&point);result[11]=chain_get_segment(&trail,0,0);',[128,1,199,-199,1,72,-72,0,0,0,0,0],include='#include "chain.c"',glob='Chain trail;ChainPoint storage[128];ChainPoint point;')
  execute(p,'debug-capacity','debug_init();debug_set_frame(65535);debug_trace_u8("A",1);debug_mark_frame("B");debug_assert_fail(0);debug_trace_u8("DROP",99);debug_assert_fail(500);entries=debug_get_trace_log();result[0]=debug_get_trace_count();result[1]=debug_get_last_assert();result[2]=entries[0].value;result[3]=entries[1].value;result[4]=entries[2].value;result[5]=entries[2].frame;result[6]=entries[2].name[0];',[3,500,1,65535,0,65535,65],include='#define DEBUG_TRACE_MAX 3\n#include "debug.c"',glob='const DebugTraceEntry* entries;')
  if p=='fc':execute(p,'signed-byte-widen','value=-5;array[0]=-7;pair.member=-9;ptr=&value;result[0]=value;result[1]=(u16)value;result[2]=(s8)251;result[3]=array[0];result[4]=pair.member;result[5]=*ptr;result[6]=value++;result[7]=++value;result[8]=value--;result[9]=--value;result[10]=(value=-6);result[11]=negative();',[-5,-5,-5,-7,-9,-5,-5,-3,-3,-5,-6,-11],glob='s8 value;s8 array[1];s8* ptr;typedef __packed struct{s8 member;} BytePair;BytePair pair;s8 negative(){return -11;}')
  execute(p,'fixed-negative','result[0]=fix_mul(-384,512);result[1]=fix_div(-768,512);result[2]=fix_div(768,-512);result[3]=fix_lerp(512,-512,128);a.x=-10;a.y=-10;a.w=8;a.h=8;b.x=-5;b.y=-5;b.w=8;b.h=8;result[4]=kq_rect_intersect(a,b);result[5]=kq_point_in_rect(-10,-10,a);result[6]=kq_point_in_rect(-2,-10,a);',[-768,-384,-384,0,1,1,0],include='#include "fixed.c"',glob='KQRect a;KQRect b;')
  execute(p,'frame-callback-replace','system_init();kq_system_frame=254;system_set_vblank_callback(first);system_wait_vblank();result[0]=calls;result[1]=seen;result[2]=system_get_frame8();system_wait_vblank();result[3]=calls;result[4]=system_get_frame();result[5]=system_get_frame8();system_set_vblank_callback(second);system_wait_vblank();result[6]=calls;system_init();result[7]=system_get_frame();system_wait_vblank();result[8]=calls;',[1,255,255,1,256,0,11,0,11],include='#include "system.c"',glob='u8 calls;u16 seen;void first(){calls++;seen=system_get_frame();system_set_vblank_callback(0);}void second(){calls=calls+10;}')
  execute(p,'scene-update-transition','table[0].enter=enter0;table[0].update=update0;table[0].draw=0;table[0].exit=exit0;table[1].enter=enter1;table[1].update=0;table[1].draw=draw1;table[1].exit=0;scene_init(table,2);scene_change(0);scene_update();result[0]=scene_get_current();result[1]=scene_was_changed();scene_draw();result[2]=scene_was_changed();scene_update();result[3]=scene_was_changed();result[4]=count;for(i=0;i<count;i++)result[5+i]=log[i];scene_set_table(table,0);scene_change(0);scene_draw();result[10]=count;',[1,1,1,0,5,1,2,3,4,5,5],include='#include "scene.c"',glob='SceneDef table[2];u8 log[8];u8 count;void add(u8 n){log[count]=n;count++;}void enter0(){add(1);}void update0(){add(2);scene_change(1);}void exit0(){add(3);}void enter1(){add(4);}void draw1(){add(5);}')
  for enabled in [False,True]:
   setup='frame_irq=0x40;dmc_irq=0;' if p=='fc' else ''
   execute(p,'interrupt-'+str(int(enabled)),setup+('system_enable_interrupts();' if enabled else 'system_disable_interrupts();'),[],include='#include "system.c"',glob='__location(0x4017) u8 frame_irq;__location(0x4010) u8 dmc_irq;' if p=='fc' else '',cpu_mask=enabled)
 if not all(r['passed'] for r in rows):raise SystemExit(1)
if __name__=='__main__':main()
