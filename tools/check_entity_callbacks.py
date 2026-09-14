"""Execute entity examples and check their labeled results and object positions pixel by pixel."""
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone
from check_api_tile_examples import read_png
from api_build_cleanup import cleanup_build_outputs

SITE = Path(__file__).resolve().parents[1]
REPOS = SITE.parents[1] / 'publish/github_20260912'
if not REPOS.is_dir(): REPOS = SITE.parent
OUTPUT = SITE / 'verification/api-entity'

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def check_pixels(path, labels, platform):
    width, height, channels, rows = read_png(path)
    assert (width,height) == ((256,240) if platform=='fc' else (160,144))
    if platform=='fc':
        font=(SITE/'samples/font.chr').read_bytes()
        mask=lambda ch,y:font[ord(ch)*16+y] | font[ord(ch)*16+y+8]
    else:
        import re
        source=(SITE/'samples/font_gb.h').read_text(encoding='utf-8')
        font=[int(n,0) for n in re.findall(r'0x[0-9a-fA-F]+|\d+',source[source.index('{')+1:source.index('}')])]
        mask=lambda ch,y:font[ord(ch)*16+y*2] | font[ord(ch)*16+y*2+1]
    background=rows[-1][:3]
    errors=0
    for tx,ty,text in labels:
        for n,ch in enumerate(text):
            for y in range(8):
                for x in range(8):
                    offset=((tx+n)*8+x)*channels
                    ink=rows[ty*8+y][offset:offset+3]!=background
                    errors += ink != bool(mask(ch,y) & (1<<(7-x)))
    return errors

def main():
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--case');opts=ap.parse_args()
    records=[]
    variants=[('nrom',[]),('nrom_no_inline',['--no-small-inline']),
              ('nrom_fast_lto',['--fastcall-v2','--library-lto-lite']),
              ('mmc3_fast_lto',['--fastcall-v2','--library-lto-lite','--static-frame'])]
    cases=[('fc','callback_check_'+name,'entity_callback_check.c',flags,
            'mmc3' if name.startswith('mmc3') else 'nrom') for name,flags in variants]
    cases += [('fc','entity_pool','entity_pool.c',[],'nrom'),
              ('gb','entity_pool_dmg','entity_pool.c',[],'dmg'),
              ('gb','entity_pool_cgb','entity_pool.c',[],'cgb')]
    for platform,name,source_name,flags,mode in cases:
        if opts.case and name!=opts.case: continue
        folder=OUTPUT/platform/name
        folder.mkdir(parents=True,exist_ok=True)
        compiler=REPOS/('kitaq'+platform)/('kitaq'+platform+'.exe')
        emulator=REPOS/('kurosaki/kurosaki.exe' if platform=='fc' else 'kokura/kokura-cli.exe')
        source=SITE/'samples/api-examples'/platform/source_name
        library=REPOS/('kitaq'+platform)/'lib/entity.c'
        rom=folder/('example.nes' if platform=='fc' else 'example.gb')
        png=folder/'screen.png'; report=folder/'runtime.json'
        # Remove only this case's replaceable outputs so a failed build cannot reuse an old ROM or image.
        for path in [rom,png,report]: path.unlink(missing_ok=True)
        command=[str(compiler),str(library),str(source),'-I',str(library.parent),'-I',str(SITE/'samples'),'-o',str(rom),'--no-disasm','--no-cache']
        if platform=='fc': command += ['--mapper='+mode,'--nes-chr='+str(SITE/'samples/font.chr')]+flags
        else: command += ['--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb']
        build=subprocess.run(command,capture_output=True,timeout=120,cwd=folder)
        (folder/'build.txt').write_bytes(build.stdout+build.stderr)
        row={'id':name,'platform':platform,'mode':mode,'build_exit':build.returncode,
             'command':command,'source':source.relative_to(SITE).as_posix(),'source_sha256':digest(source),
             'library_sha256':digest(library),'compiler_sha256':digest(compiler),'emulator_sha256':digest(emulator),
             'passed':False}
        if build.returncode==0 and rom.exists():
            if platform=='fc': run=[str(emulator),'run',str(rom),'--frames','120','--png',str(png),'--json',str(report)]
            else: run=[str(emulator),str(rom),'--hardware',mode,'--run-frames','120','--png',str(png),'--dump-report',str(report)]
            result=subprocess.run(run,capture_output=True,timeout=120,cwd=folder)
            (folder/'runtime.txt').write_bytes(result.stdout+result.stderr)
            row.update(runtime_exit=result.returncode,run_command=run,rom_sha256=digest(rom))
            if result.returncode==0 and png.exists():
                state=json.loads(report.read_text(encoding='utf-8'))
                if platform=='gb':
                    state={k:state[k] for k in ['meta','cpu','video','stop_reason','unsupported_opcodes'] if k in state}
                    report.write_text(json.dumps(state,indent=2),encoding='utf-8')
                if source_name=='entity_callback_check.c':
                    labels=[(2,0,'CALLBACK CHECK'),(2,7,'FAILED CHECKS'),(3,8,'000'),(2,10,'TOTAL CHECKS'),(3,11,'024'),
                            (3,13,'00 00'),(2,17,'ABC'),(10,17,'FFFF'),(18,17,'P')]
                else:
                    labels=[(2,0,'ENTITY POOL'),(2,2,'CREATED'),(15,2,'002'),(2,3,'AFTER FREE'),(15,3,'001'),
                            (2,4,'REUSED ID'),(15,4,'000'),(2,5,'AFTER CLEAR'),(15,5,'000'),
                            (2,7,'UPDATE CALLS'),(15,7,'002'),(2,8,'DRAW CALLS'),(15,8,'002'),
                            (2,15,'FAILED CHECKS000'),(2,12,' A   B ')]
                errors=check_pixels(png,labels,platform)
                frames=state.get('frames',state.get('meta',{}).get('frames_executed'))
                row.update(pixel_mismatches=errors,expected_labels=labels,frames=frames,
                           image=png.relative_to(SITE).as_posix(),image_sha256=digest(png),
                           passed=(errors==0 and frames==120))
        records.append(row)
        if row['passed']: cleanup_build_outputs(folder)
        print(name, 'PASS' if row['passed'] else 'FAIL',flush=True)
    evidence={'date':datetime.now(timezone.utc).isoformat(),'records':records,
              'scope':'Emulator execution and pixel checks; physical hardware is untested.'}
    (OUTPUT/('results.json' if not opts.case else opts.case+'-results.json')).write_text(json.dumps(evidence,indent=2),encoding='utf-8')
    if not all(r['passed'] for r in records):raise SystemExit(1)

if __name__=='__main__':main()
