"""Check hit prerequisites and the split helper's deferred vertical scroll."""
from pathlib import Path
import hashlib,json,subprocess
from check_batch200 import dependencies
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.is_dir():REPOS=SITE.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
OUT=SITE/'verification/api-sprite0/state';OUT.mkdir(parents=True,exist_ok=True)
compiler=REPOS/'kitaqfc/kitaqfc.exe';emulator=REPOS/'kurosaki/kurosaki.exe';lib=REPOS/'kitaqfc/lib'
cases=[
 ('behind','',0x1E,True),
 ('hidden','__sprite_hide(0);',0x1E,False),
 ('transparent-bg','__nametable_rect(0,12,32,1,0);',0x1E,False),
 ('sprites-off','',0x0A,False),
 ('background-off','',0x14,False),
 ('x255','__sprite_set(0,255,95,242,0x20);',0x1E,False),
 ('left-clipped','__sprite_set(0,0,95,242,0x20);',0x18,False),
 ('left-enabled','__sprite_set(0,0,95,242,0x20);',0x1E,True),
 ('vertical-latch','',0x1E,True)]
rows=[]
for variant,flags in [('default',[]),('unoptimized',['-O0'])]:
 for name,setup,mask,expect_hit in cases:
  folder=OUT/(variant+'-'+name);folder.mkdir(exist_ok=True)
  source=folder/'case.c';rom=folder/'case.nes';snapshot=folder/'snapshot.json';image=folder/'screen.png'
  operation='__split_scroll_sprite0(32,64);' if name=='vertical-latch' else '__sprite0_wait_hit();'
  source.write_text('#include "fc_sprite0_scene.h"\nvoid main(void){s0_prepare();__ppu_off();'+setup+'__oam_dma();__scroll_set(0,0);__ppu_mask_set('+str(mask)+');s0_completed=0;while(1){s0_frame();'+operation+'s0_completed++;}}',encoding='ascii')
  cmd=[str(compiler),str(source),'-I',str(lib),'-I',str(SITE/'samples'),'-o',str(rom),'--mapper=nrom','--nes-chr='+str(SITE/'samples/sprite0_scene.chr'),'--no-cache','--no-disasm']+flags
  p=subprocess.run(cmd,capture_output=True,cwd=folder,timeout=90)
  if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace')[-2500:])
  p=subprocess.run([str(emulator),'run',str(rom),'--frames','120','--snapshot',str(snapshot),'--png',str(image)],capture_output=True,cwd=folder,timeout=90);assert p.returncode==0
  state=json.loads(snapshot.read_text());completed=state['bus']['ram'][0x600]
  actual=[int(80<completed<120) if expect_hit else int(completed==0)];expected=[1]
  if name=='vertical-latch':
   reference=SITE/('verification/api-sprite0/example/split-'+variant+'/screen.png')
   actual.append(int(sha(image)==sha(reference)));expected.append(1)
  inputs=dependencies(source,lib);inputs['samples/sprite0_scene.chr']=sha(SITE/'samples/sprite0_scene.chr')
  row=dict(platform='fc',name=name,mode=variant,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),input_sha256=inputs,actual=actual,expected=expected,completed=completed,passed=actual==expected)
  if name=='vertical-latch':row.update(image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),reference_image=reference.relative_to(SITE).as_posix(),reference_image_sha256=sha(reference))
  rows.append(row);print(name,variant,'PASS' if row['passed'] else 'FAIL','completed',completed,'checks',actual,flush=True)
  if row['passed']:
   snapshot.unlink();cleanup_build_outputs(folder)
   if name!='vertical-latch':image.unlink()
  (OUT/'results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),records=rows),indent=2),encoding='utf-8')
raise SystemExit(0 if all(r['passed'] for r in rows) else 1)
