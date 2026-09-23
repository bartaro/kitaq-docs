"""Compile each declared alias spelling and verify input/frame-service behavior."""
from pathlib import Path
import hashlib,json,re,subprocess
from check_entity_callbacks import check_pixels
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUT=SITE/'verification/api-header-aliases'
CASE_FILE=SITE/'tools/api_descriptions/header_alias_cases.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
VARIANTS={'gb':[('default',[]),('O0',['-O0']),('stack',['--abi=stack'])],
          'fc':[('default',[]),('O0',['-O0']),('no-inline',['--no-small-inline']),('fastcall',['--fastcall-v2'])]}

def dependencies(paths,lib):
 """Bind every quoted include, including headers used in conditional branches."""
 seen=set();pending=list(paths)
 while pending:
  p=pending.pop().resolve()
  if p in seen:continue
  seen.add(p)
  if p.suffix not in ('.c','.h','.inc'):continue
  for name in re.findall(r'(?m)^\s*#include\s+"([^"]+)"',p.read_text(encoding='utf-8')):
   found=next((q for q in [p.parent/name,lib/name,SITE/'samples'/name] if q.is_file()),None)
   assert found is not None,(p,name)
   pending.append(found)
 site={p.relative_to(SITE).as_posix():sha(p) for p in seen if p.is_relative_to(SITE)}
 repo={p.relative_to(REPOS).as_posix():sha(p) for p in seen if p.is_relative_to(REPOS)}
 assert len(site)+len(repo)==len(seen)
 return site,repo

def main():
 cases=json.loads(CASE_FILE.read_text(encoding='utf-8'))
 service_specs={s['platform']:s for s in json.loads((SITE/'tools/api_descriptions/batch100_examples.json').read_text(encoding='utf-8')) if s['group']=='services'}
 records=[];rejected=[];site_sources={};repo_sources={};tools={}
 for key,case in cases.items():
  platform=case['platform'];is_input=case['group']=='input';lib=REPOS/('kitaq'+platform)/'lib'
  compiler=lib.parent/('kitaq'+platform+'.exe');emulator=REPOS/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe')
  for p in [compiler,emulator,lib.parent/('kitaq'+platform)/'CodeGenerator.cs']:tools[p.relative_to(REPOS).as_posix()]=sha(p)
  libraries=[lib/'input.c'] if is_input else [lib/'runtime.c'] if platform=='fc' else []
  source=SITE/case['source'];canonical=SITE/case['canonical']
  a,b=dependencies([source,canonical,*libraries]+([SITE/'samples/font.chr'] if platform=='fc' else []),lib)
  site_sources.update(a);repo_sources.update(b)
  for variant,flags in VARIANTS[platform]:
   folder=OUT/key/variant;folder.mkdir(parents=True,exist_ok=True)
   suffix='.gb' if platform=='gb' else '.nes';rom=folder/('example'+suffix);baseline=folder/('canonical'+suffix)
   target_flags=['--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb'] if platform=='gb' else ['--mapper=nrom','--nes-chr='+str(SITE/'samples/font.chr')]
   if platform=='gb' and not is_input:target_flags+=['--cart=mbc5','--romsize=64k']
   unsupported=key=='gb-system' and variant=='stack'
   diagnostics=[]
   for src,dest in [(canonical,baseline),(source,rom)]:
    command=[str(compiler),*map(str,libraries),str(src),'-I',str(lib),'-I',str(SITE/'samples'),'-o',str(dest),'--no-cache','--no-disasm',*target_flags,*flags]
    built=subprocess.run(command,cwd=folder,capture_output=True,timeout=120)
    output=(built.stdout+built.stderr).decode(errors='replace')
    if unsupported:
     errors=re.findall(r'error KQ\d+: ([^\r\n]+)',output)
     diagnostic='Indirect calls are not supported with --abi=stack yet'
     assert built.returncode!=0 and errors and set(errors)=={diagnostic},(key,variant,output)
     diagnostics.append(dict(source=src.relative_to(SITE).as_posix(),source_sha256=sha(src),diagnostic=diagnostic,count=len(errors)))
    else:assert built.returncode==0,(key,variant,output)
   if unsupported:
    assert diagnostics[0]['count']==diagnostics[1]['count']
    rejected.append(dict(case=key,variant=variant,diagnostics=diagnostics,passed=True))
    cleanup_build_outputs(folder)
    print(key,variant,'EXPECTED DIAGNOSTIC',flush=True)
    continue
   assert rom.read_bytes()==baseline.read_bytes(),(key,variant,'alias changes generated ROM')
   canonical_hash=sha(baseline);baseline.unlink();cleanup_build_outputs(folder)
   for mode in (['dmg','cgb'] if platform=='gb' else ['nrom']):
    sub=folder/mode;sub.mkdir(exist_ok=True);state=sub/'runtime.json';png=sub/'screen.png'
    if platform=='gb':
     command=[str(emulator),str(rom),'--hardware',mode,'--run-frames','180','--dump-report',str(state),'--png',str(png),'--report-sections','meta,watched_memory','--watch-fields','preview']
     if is_input:command+=['--input-seq','NONE:30;A:40;NONE:110']
     else:
      for offset in range(0,160,16):command+=['--watch-window',f'result{offset}:{0xC600+offset}:16']
    elif is_input:
     timeline=[dict(frame=start,duration=duration,pad1=button,pad2=0,reset=False,disk_side=None,expected_frame_hash=None) for start,duration,button in [(0,30,0),(30,40,1),(70,110,0)]]
     replay=sub/'input.json';replay.write_text(json.dumps(dict(format='kurosaki-replay-v1',rom_sha256=sha(rom),emulator_version='0.1.0',region='ntsc',frames=timeline,expected_final_state_hash=None)))
     command=[str(emulator),'replay-run',str(rom),str(replay),'--frames','180','--png',str(png),'--json',str(state)]
    else:command=[str(emulator),'run',str(rom),'--frames','180','--headless','--snapshot',str(state),'--png',str(png)]
    run=subprocess.run(command,cwd=sub,capture_output=True,timeout=120);assert run.returncode==0,(key,variant,mode)
    data=json.loads(state.read_text(encoding='utf-8'));actual=[];expected=[]
    if is_input:
     labels=[(1,0,'INPUT EDGES')]+[(1,y,t) for y,t in [(2,'FIRST DOWN'),(3,'FIRST PRESS'),(4,'FIRST REPEAT'),(5,'FIRST CURRENT'),(6,'HELD TICKS'),(7,'PRESS COUNT'),(8,'REPEAT COUNT'),(9,'RELEASE'),(10,'LAST CURRENT'),(11,'LAST PREVIOUS'),(13,'FAILED CHECKS')]]
     labels += [(16,y,v) for y,v in [(2,'001'),(3,'001'),(4,'001'),(5,'016'),(6,'040'),(7,'001'),(8,'005'),(9,'001'),(10,'000'),(11,'016'),(13,'000')]]
     summary=data.get('summary',data);frames=summary.get('frames',summary.get('meta',{}).get('frames_executed'));assert frames==180
    else:
     spec=service_specs[platform];expected=spec['expected']+[0]*(79-len(spec['expected']))+[0xA55A]
     if platform=='gb':
      watches={w['name']:w['preview_bytes'] for w in data['watched_memory']};raw=sum((watches['result'+str(n)] for n in range(0,160,16)),[])
     else:raw=data['bus']['ram'][0x600:0x6A0]
     actual=[raw[n]+256*raw[n+1] for n in range(0,160,2)]
     labels=[]
     for y,label,index in spec['labels']:
      labels.append((1,y,label))
      if index is not None:labels.append((13,y,str(expected[index]).zfill(5)))
    errors=check_pixels(png,labels,platform)
    row=dict(case=key,platform=platform,variant=variant,mode=mode,source=case['source'],source_sha256=sha(source),
      rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),canonical_rom_sha256=canonical_hash,
      image=png.relative_to(SITE).as_posix(),image_sha256=sha(png),frames_requested=180,
      expected_labels=labels,pixel_mismatches=errors,actual=actual,expected=expected,
      passed=errors==0 and actual==expected)
    records.append(row)
    assert all(sha(SITE/n)==h for n,h in site_sources.items())
    assert all(sha(REPOS/n)==h for n,h in repo_sources.items())
    report=dict(records=records,rejected=rejected,passed=all(r['passed'] for r in records),site_sources=site_sources,repo_sources=repo_sources,tools=tools,
      checker_sha256=sha(Path(__file__)),cases_sha256=sha(CASE_FILE),service_specs_sha256=sha(SITE/'tools/api_descriptions/batch100_examples.json'))
    (OUT/'results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(key,variant,mode,'PASS' if row['passed'] else 'FAIL',errors,flush=True)
    assert row['passed'],(key,variant,mode,actual,expected)
    state.unlink()
    if platform=='fc' and is_input:replay.unlink()
 assert len(records)==22 and len(rejected)==1

if __name__=='__main__':main()
