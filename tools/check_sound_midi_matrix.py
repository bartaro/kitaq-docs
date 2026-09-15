"""Measure actual serial instructions with both zero-page allocation settings."""
from pathlib import Path
import hashlib,json,subprocess
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUT=SITE/'verification/api-sound/state/midi';compiler=REPOS/'kitaqfc/kitaqfc.exe';emulator=REPOS/'kurosaki/kurosaki.exe'
source=SITE/'samples/api-examples/fc/sound_midi.c';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected=[126,194,5,178,7,100,146,69,96,130,69,0,248,250,251,252]
rows=[]
for flag in ['--no-zp-alloc','--zp-alloc']:
    folder=OUT/flag[2:];folder.mkdir(parents=True,exist_ok=True);rom=folder/'case.nes';trace=folder/'trace.jsonl'
    run=subprocess.run([str(compiler),str(source),'-I',str(REPOS/'kitaqfc/lib'),'-I',str(SITE/'samples'),'-o',str(rom),
        '--mapper=nrom','--nes-chr='+str(SITE/'samples/font.chr'),flag,'--no-cache','--no-disasm'],cwd=folder,capture_output=True,timeout=120)
    (folder/'build.txt').write_bytes(run.stdout+run.stderr);assert run.returncode==0
    run=subprocess.run([str(emulator),'trace',str(rom),'--frames','50','--mem-read','--mem-write','--out',str(trace)],cwd=folder,capture_output=True,timeout=120);assert run.returncode==0
    events=[json.loads(line) for line in trace.read_text(encoding='utf-8').splitlines()]
    writes=[e for e in events if e['kind']=='mem.write' and e['addr']==0x4016]
    frames=[writes[i:i+10] for i in range(0,len(writes),10)]
    values=[sum(f[j+1]['value']<<j for j in range(8)) for f in frames if len(f)==10]
    cells=[b['cpu_cycle']-a['cpu_cycle'] for f in frames for a,b in zip(f,f[1:])]
    gaps=[b[0]['cpu_cycle']-a[-1]['cpu_cycle'] for a,b in zip(frames,frames[1:])]
    reads=[e for e in events if e['kind']=='mem.read' and e['addr']==0x4017]
    receive=[b['cpu_cycle']-a['cpu_cycle'] for a,b in zip(reads,reads[1:])]
    framing=all(len(f)==10 and f[0]['value']==0 and f[-1]['value']==1 for f in frames)
    row=dict(flag=flag,rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),values=values,expected=expected,cells=cells,gaps=gaps,receive=receive,
        passed=values==expected and set(cells)=={57} and min(gaps)>=57 and receive==[81]+[57]*7 and framing)
    rows.append(row);cleanup_build_outputs(folder);print(flag,'PASS' if row['passed'] else 'FAIL',sorted(set(cells)),receive,flush=True)
report=dict(source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),script_sha256=sha(Path(__file__)),records=rows)
(OUT/'results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
raise SystemExit(0 if all(r['passed'] for r in rows) else 1)
