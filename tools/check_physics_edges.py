"""Exercise boundaries and controller paths independently of the teaching screenshots."""
from pathlib import Path
import subprocess,json,hashlib,argparse
from check_batch200 import dependencies
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUT=SITE/'verification/api-physics/state';OUT.mkdir(parents=True,exist_ok=True)
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
 if platform=='gb':command+=['--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb','--cart=mbc5','--romsize=128k']
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
  row={'platform':platform,'name':name,'mode':mode,'source':source.relative_to(SITE).as_posix(),'source_sha256':sha(source),'rom':rom.relative_to(SITE).as_posix(),'rom_sha256':sha(rom),'compiler_sha256':sha(compiler),'emulator_sha256':sha(exe),'input_sha256':dependencies(source,lib),'actual':actual,'expected':want,'passed':actual==want}
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
 inc='#include "fixed.c"\n#include "physics2d.c"\n#pragma bank 0'
 glob='KQWorld2D w; KQBody2D b[2]; KQSurface2D s; KQRect r; KQRect q;'
 coefficients=[-256,-128,-1,0,1,127,128,255,256];values=[-257,-1,0,1,257]
 expressions=[f'result[{i}]=kq2d_scale_q8({v},{c});' for i,(v,c) in enumerate((v,c) for v in values for c in coefficients)]
 execute('gb','signed-scale-grid',''.join(expressions),[int(v*c/256) for v in values for c in coefficients],inc,glob)
 execute('gb','speed-limit','kq2d_body_init(&b[0],0,0,4,4);b[0].vx=-300;b[0].vy=-400;b[0].active=0;b[0].inv_mass_q8=0;kq2d_body_limit_speed(&b[0],250);result[0]=b[0].vx;result[1]=b[0].vy;b[0].vx=100;b[0].vy=0;kq2d_body_limit_speed(&b[0],200);result[2]=b[0].vx;kq2d_body_limit_speed(&b[0],-1);result[3]=b[0].vx;result[4]=b[0].vy;kq2d_body_limit_speed(0,5);',[-147,-196,100,0,0],inc,glob)
 setup='kq2d_body_init(&b[0],24,40,4,4);s.nx_q8=0;s.ny_q8=-256;s.vx=0;s.vy=0;s.bounce_threshold=2;s.kick=0;s.restitution_q8=0;s.friction_q8=64;'
 body=setup+'b[0].vx=8;b[0].vy=16;result[0]=kq2d_body_resolve_surface(&b[0],&s);result[1]=b[0].vx;result[2]=b[0].vy;'
 body+='b[0].vx=8;b[0].vy=16;s.kick=4;s.friction_q8=0;result[3]=kq2d_body_resolve_surface(&b[0],&s);result[4]=b[0].vx;result[5]=b[0].vy;'
 body+='b[0].vx=8;b[0].vy=16;s.kick=0;s.restitution_q8=255;s.bounce_threshold=16;result[6]=kq2d_body_resolve_surface(&b[0],&s);result[7]=b[0].vy;'
 body+='b[0].vy=-5;result[8]=kq2d_body_resolve_surface(&b[0],&s);result[9]=b[0].vy;result[10]=kq2d_body_resolve_surface(0,&s);result[11]=kq2d_body_resolve_surface(&b[0],0);'
 body+='b[0].vx=3;b[0].vy=10;s.vx=3;s.vy=2;s.restitution_q8=128;s.bounce_threshold=0;result[12]=kq2d_body_resolve_surface(&b[0],&s);result[13]=b[0].vx;result[14]=b[0].vy;'
 execute('gb','surface-rest-kick-threshold',body,[16,4,0,16,8,-4,16,0,0,-5,0,0,8,3,-2],inc,glob)
 gaps=[(6,-2),(1,-8191),(8191,-8191),(0,10),(-1,-2),(6,0),(6,2)]
 execute('gb','surface-time',''.join(f'result[{i}]=kq2d_surface_toi_q8({a},{b});' for i,(a,b) in enumerate(gaps)),[192,0,128,0,0,256,256],inc,glob)
 execute('gb','inactive-static-null','kq2d_world_init(&w,b,1);kq2d_body_init(&b[0],10,20,4,4);b[0].vx=3;b[0].vy=4;b[0].active=0;kq2d_integrate_body(&w,&b[0]);result[0]=b[0].x;result[1]=b[0].vy;b[0].active=1;b[0].inv_mass_q8=0;kq2d_body_apply_gravity(&b[0],20,20,30);result[2]=b[0].vx;result[3]=b[0].vy;kq2d_body_set_velocity(&b[0],9,10);result[4]=b[0].vx;kq2d_body_init(0,0,0,1,1);kq2d_world_init(0,b,1);kq2d_step(0);w.bodies=0;kq2d_step(&w);kq2d_integrate_body(0,&b[0]);kq2d_integrate_body(&w,0);kq2d_body_set_pos(0,1,2);kq2d_body_set_velocity(0,1,2);kq2d_body_apply_gravity(0,1,2,3);kq2d_body_apply_friction(0,64);',[10,4,3,4,9],inc,glob)
 execute('gb','friction-signed-byte','kq2d_body_init(&b[0],0,0,1,1);b[0].vx=256;b[0].vy=-256;kq2d_body_apply_friction(&b[0],128);result[0]=b[0].vx;result[1]=b[0].vy;b[0].vx=256;b[0].vy=-257;kq2d_body_apply_friction(&b[0],255);result[2]=b[0].vx;result[3]=b[0].vy;',[-128,128,-1,1],inc,glob)
 execute('gb','rect-boundaries','r.x=-8;r.y=-8;r.w=16;r.h=16;q.x=8;q.y=-8;q.w=8;q.h=8;result[0]=kq2d_rect_intersect(r,q);q.x=7;result[1]=kq2d_rect_intersect(r,q);result[2]=kq2d_point_in_rect(-8,-8,r);result[3]=kq2d_point_in_rect(8,0,r);result[4]=kq2d_point_in_rect(0,8,r);kq2d_body_init(&b[0],0,0,4,4);kq2d_body_init(&b[1],7,0,4,4);b[0].active=0;result[5]=kq2d_overlap_aabb(&b[0],&b[1]);b[1].x=8;result[6]=kq2d_overlap_aabb(&b[0],&b[1]);',[0,1,1,0,0,1,0],inc,glob)
 setup='kq2d_world_init(&w,b,2);w.gravity_y=0;w.solver_iterations=0;kq2d_body_init(&b[0],16,16,8,8);kq2d_body_init(&b[1],28,16,8,8);b[0].inv_mass_q8=64;b[1].inv_mass_q8=64;b[0].vx=4;'
 execute('gb','box-pair-tie',setup+'kq2d_step(&w);result[0]=b[0].x;result[1]=b[1].x;result[2]=b[0].vx;result[3]=b[1].vx;kq2d_body_set_pos(&b[0],16,16);kq2d_body_set_pos(&b[1],24,24);b[0].vx=0;b[1].vx=0;kq2d_step(&w);result[4]=b[0].x;result[5]=b[0].y;result[6]=b[1].x;result[7]=b[1].y;',[16,32,2,2,16,12,24,28],inc,glob)
 inc='#include "physics2d_circle.c"\n#pragma bank 0';glob='KQCircleWorld2D w; KQCircleBody2D b[2];'
 body='b[0].x=0;b[0].y=0;b[0].radius=8;b[1].radius=8;'
 for i,(x,y) in enumerate([(15,0),(16,0),(11,11),(12,12),(15,5),(16,1),(0,0)]):body+=f'b[1].x={x};b[1].y={y};result[{i}]=kq2dc_overlap_circle(&b[0],&b[1]);'
 execute('gb','circle-distance',body,[1,0,1,0,1,0,1],inc,glob)
 execute('gb','circle-static-bounds','kq2dc_world_init(&w,b,1);kq2dc_set_bounds(&w,4,4,60,60);w.wall_restitution_q8=128;w.wall_friction_q8=0;b[0].x=0;b[0].y=24;b[0].radius=6;b[0].active=1;b[0].inv_mass_q8=0;b[0].vx=-8;b[0].vy=0;kq2dc_step(&w);result[0]=b[0].x;result[1]=b[0].vx;b[0].active=0;b[0].x=0;kq2dc_step(&w);result[2]=b[0].x;kq2dc_world_init(0,b,1);kq2dc_set_bounds(0,0,0,1,1);kq2dc_step(0);w.bodies=0;kq2dc_step(&w);',[10,4,0],inc,glob)
 body='kq2dc_world_init(&w,b,1);w.linear_damping_q8=255;b[0].radius=4;b[0].active=1;b[0].inv_mass_q8=64;b[0].vy=0;'
 for i,v in enumerate([-2,-1,0,1,2,256,-256]):body+=f'b[0].x=0;b[0].vx={v};kq2dc_step(&w);result[{i}]=b[0].vx;'
 execute('gb','circle-damping',body,[0,0,0,0,0,255,-255],inc,glob)
 body='kq2dc_world_init(&w,b,2);w.solver_iterations=1;w.linear_damping_q8=255;for(i=0;i<2;i++){b[i].x=16+i*16;b[i].y=24;b[i].radius=8;b[i].inv_mass_q8=64;b[i].active=1;b[i].vx=0;b[i].vy=0;b[i].restitution_q8=128;b[i].friction_q8=0;}b[0].vx=8;kq2dc_step(&w);result[0]=b[0].x;result[1]=b[1].x;result[2]=b[0].vx;result[3]=b[1].vx;result[4]=kq2dc_overlap_circle(&b[0],&b[1]);b[0].x=16;b[1].x=20;b[0].vx=0;b[1].vx=0;kq2dc_step(&w);result[5]=b[0].x;result[6]=b[1].x;'
 execute('gb','circle-pair-resting',body,[22,34,5,0,1,16,20],inc,glob)
 inc='#include "physics3d.c"\n#pragma bank 0';glob='KQWorld3D w; KQBody3D b[2];'
 body=''
 masses=[-1,0,1,63,64,65,256,512,32767]
 for i,m in enumerate(masses):body+=f'kq3d_body_set_mass(&b[0],{m});result[{i*2}]=b[0].mass_q8;result[{i*2+1}]=b[0].inv_mass_q8;'
 expected=[]
 for m in masses:expected += [m,0 if m<=0 else max(1,32767//max(m,64))]
 execute('gb','mass-weights',body,expected,inc,glob)
 execute('gb','acceleration-impact-flags','kq3d_world_init(&w,b,1);w.gravity_y=0;kq3d_body_init(&b[0],0,0,0,4,4,4,256);b[0].ax=1;b[0].last_impact_speed=99;b[0].flags=1;b[0].break_speed=1;kq3d_integrate_body(&w,&b[0]);kq3d_integrate_body(&w,&b[0]);result[0]=b[0].x;result[1]=b[0].vx;result[2]=b[0].ax;result[3]=b[0].last_impact_speed;result[4]=b[0].flags;b[0].inv_mass_q8=0;b[0].last_impact_speed=77;kq3d_step(&w);result[5]=b[0].last_impact_speed;result[6]=b[0].x;kq3d_world_init(0,b,1);kq3d_body_init(0,0,0,0,1,1,1,256);kq3d_body_set_mass(0,256);kq3d_integrate_body(0,&b[0]);kq3d_integrate_body(&w,0);kq3d_step(0);w.bodies=0;kq3d_step(&w);',[3,2,1,0,1,77,3],inc,glob)
 for axis in ['x','y','z']:
  body='kq3d_world_init(&w,b,2);w.gravity_y=0;w.solver_iterations=1;kq3d_body_init(&b[0],16,16,16,8,8,8,256);kq3d_body_init(&b[1],16,16,16,8,8,8,0);'
  body+=f'b[0].{axis}=8;b[1].{axis}=20;b[0].v{axis}=8;b[0].restitution_q8=256;b[1].restitution_q8=256;kq3d_step(&w);result[0]=b[0].{axis};result[1]=b[0].v{axis};result[2]=b[0].last_impact_speed;result[3]=b[1].last_impact_speed;'
  execute('gb','box3d-axis-'+axis,body,[4,-8,8,8],inc,glob)
 execute('gb','box3d-weighted','kq3d_world_init(&w,b,2);w.gravity_y=0;w.solver_iterations=1;kq3d_body_init(&b[0],16,16,16,8,8,8,256);kq3d_body_init(&b[1],28,16,16,8,8,8,512);b[0].vx=4;b[0].restitution_q8=256;b[1].restitution_q8=256;kq3d_step(&w);result[0]=b[0].x;result[1]=b[1].x;result[2]=b[0].vx;result[3]=b[1].vx;', [15,31,-1,3],inc,glob)
 execute('gb','dot-rounding','result[0]=kq3d_dot_q8_8(-257,257,1,64,-64,127);result[1]=kq3d_dot_q8_8(0,0,0,-128,127,1);result[2]=kq3d_dot_q8_8(256,256,256,127,127,127);',[-128,0,381],inc,glob)
 if not rows or not all(row['passed'] for row in rows):raise SystemExit(1)
if __name__=='__main__':main()
