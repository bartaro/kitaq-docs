"""Execute BIOS-free FDS query lessons and check RAM plus complete text images.

The zero-filled firmware fixture is private test input, not a replacement BIOS.
No disk transfer, write-protection transition, or real-hardware timing is claimed.
"""
from pathlib import Path
import hashlib,json,os,subprocess
from check_api_tile_examples import read_png
from check_batch200 import dependencies
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.is_dir():REPOS=SITE.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
OUT=SITE/'verification/api-fds-query/example';OUT.mkdir(parents=True,exist_ok=True)
compiler=Path(os.environ.get('KITAQFC_TEST_COMPILER',str(REPOS/'kitaqfc/kitaqfc.exe')))
emulator=REPOS/'kurosaki/kurosaki.exe';lib=REPOS/'kitaqfc/lib'
fontpath=SITE/'samples/font.chr';font=fontpath.read_bytes()
records=[]

def scene(labels):
    pixels=set()
    for tx,ty,label in labels:
        for n,c in enumerate(label):
            for y in range(8):
                bits=font[ord(c)*16+y]|font[ord(c)*16+y+8]
                for x in range(8):
                    if bits & (128>>x):pixels.add(((tx+n)*8+x,ty*8+y))
    return pixels

for lesson,mapper,extra,expected in [
    ('available','fds',[],[1]),('available','nrom',[],[0]),
    ('status','fds',[],[1,0,0,2]),
    ('metadata','fds',[],[1,1,0,1,2,0,0,0,0]),
    ('residency','fds',[],[1,1,0,2]),
    ('residency','fds',['--fds-no-overlay-table'],[1,1,0,0])]:
    for variant,flags in [('default',[]),('unoptimized',['-O0'])]:
        mode=lesson+'-'+mapper+('-table-off' if extra else '')+'-'+variant
        folder=OUT/mode;folder.mkdir(exist_ok=True)
        source=SITE/('samples/api-examples/fc/fds_'+lesson+'.c')
        rom=folder/('example.'+('fds' if mapper=='fds' else 'nes'));image=folder/'screen.png';statepath=folder/'state.json'
        cmd=[str(compiler),str(source),'-I',str(lib),'-I',str(SITE/'samples'),'-o',str(rom),'--mapper='+mapper,'--nes-chr='+str(fontpath),'--no-cache','--no-disasm']+extra+flags
        inputs=dependencies(source,lib);inputs['samples/font.chr']=sha(fontpath)
        if mapper=='fds':cmd+=['--fds-no-license-bypass']
        if lesson=='metadata':
            manifest=SITE/'samples/api-examples/fc/fds_metadata.json'
            cmd+=['--fds-meta='+str(manifest)];inputs[manifest.relative_to(SITE).as_posix()]=sha(manifest)
            for entry in json.loads(manifest.read_text())['files']:
                if entry.get('source'):
                    payload=manifest.parent/entry['source']
                    inputs[payload.relative_to(SITE).as_posix()]=sha(payload)
        p=subprocess.run(cmd,capture_output=True,cwd=folder,timeout=90)
        if p.returncode:raise RuntimeError(mode+': '+(p.stdout+p.stderr).decode(errors='replace')[-4000:])
        environment=None
        if mapper=='fds':
            fixture=folder/'empty-firmware-fixture.bin';fixture.write_bytes(bytes(8192))
            environment={**os.environ,'KUROSAKI_DISKSYS_ROM':str(fixture)}
        p=subprocess.run([str(emulator),'run',str(rom),'--frames','120','--snapshot',str(statepath),'--png',str(image)],capture_output=True,cwd=folder,env=environment,timeout=90)
        if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace')[-2000:])
        state=json.loads(statepath.read_text());ram=state['bus']['ram']
        actual=ram[0x600:0x600+len(expected)] if lesson!='metadata' else ram[0x600:0x603]+ram[0x610:0x616]
        if lesson=='available':labels=[(2,2,'FDS BUILD SELECTION'),(2,5,'FDS=1 / CARTRIDGE=0'),(3,8,'%03d'%expected[0])]
        elif lesson=='status':labels=[(2,2,'FDS REGISTER STATUS'),(2,5,'PRESENT / PROTECT / STATUS'),(2,7,'1'),(12,7,'0'),(22,7,'0'),(2,10,'COMPLETED PRESENCE WAITS'),(2,12,'2'),(2,15,'NO FILE TRANSFER TESTED')]
        elif lesson=='metadata':labels=[(2,2,'FDS COMPILED FILE TABLE'),(2,5,'ID    EXISTS    BYTES'),(2,7,'16      1        513'),(2,9,'17      1          0'),(2,11,'18      0          0'),(2,14,'TABLE VALUES MATCH: PASS'),(2,17,'NO DISK DIRECTORY SCAN')]
        else:labels=[(2,2,'FDS OVERLAY RECORDS'),(2,5,'CURRENT BANK'),(25,5,'1'),(2,7,'BANK 1 RESIDENT'),(25,7,'1'),(2,9,'BANK 2 RESIDENT'),(25,9,'0'),(2,11,'OVERLAY FUNCTIONS'),(25,11,str(expected[3])),(2,14,'NO OVERLAY LOAD TESTED')]
        pixels=scene(labels);w,h,ch,rows=read_png(image);assert (w,h)==(256,240)
        bad=[(x,y) for y in range(h) for x in range(w) if (sum(rows[y][x*ch:x*ch+3])>384)!=((x,y) in pixels)]
        row=dict(platform='fc',mode=mode,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),input_sha256=inputs,actual=actual,expected=expected,pixel_mismatches=len(bad),first_mismatches=bad[:10],passed=actual==expected and not bad)
        records.append(row);print(mode,'PASS' if row['passed'] else 'FAIL',actual,'expected',expected,'pixels',len(bad),flush=True)
        (OUT/'results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),records=records),indent=2),encoding='utf-8')
        if row['passed']:
            statepath.unlink()
            if mapper=='fds':fixture.unlink()
            cleanup_build_outputs(folder)
raise SystemExit(0 if all(r['passed'] for r in records) else 1)
