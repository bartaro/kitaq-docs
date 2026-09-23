"""Check the signed-distance lesson's computed RAM and rendered font pixels."""
from pathlib import Path
import hashlib,json,subprocess
from check_batch200 import dependencies
from check_entity_callbacks import check_pixels
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUT=SITE/'verification/api-chain-wrap/example';OUT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
labels=[(0,0,'WRAPPED DISTANCE'),(0,2,'FIELD: 160 PIXELS'),(0,4,'159 -> 1'),(15,4,'+02'),(0,6,'1 -> 159'),(15,6,'-02'),(0,8,'TIE 0 -> 80'),(15,8,'+80'),(0,10,'TIE 80 -> 0'),(15,10,'-80'),(0,12,'FIELD: 1 PIXEL'),(0,14,'0 -> 0'),(15,14,'+00'),(0,16,'SIGNED PIXEL DELTA')]
expected=[2,65534,80,65456,0];records=[]
for platform in ['gb','fc']:
    compiler=REPOS/f'kitaq{platform}/kitaq{platform}.exe';emulator=REPOS/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe')
    folder=OUT/platform;folder.mkdir(exist_ok=True)
    source=SITE/f'samples/api-examples/{platform}/chain_wrap.c';rom=folder/('example.gb' if platform=='gb' else 'example.nes')
    command=[compiler,source,'-I',compiler.parent/'lib','-I',SITE/'samples','-o',rom,'--no-cache','--no-disasm']
    command+=['--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb','--cart=mbc5','--romsize=128k'] if platform=='gb' else ['--mapper=nrom','--nes-chr='+str(SITE/'samples/font.chr')]
    run=subprocess.run(list(map(str,command)),capture_output=True,cwd=folder,timeout=120);assert run.returncode==0,(run.stdout+run.stderr).decode(errors='replace')
    for mode in (['dmg','cgb'] if platform=='gb' else ['ntsc']):
        image=folder/(mode+'.png');state=folder/(mode+'.json')
        command=[emulator,rom,'--hardware',mode,'--run-frames','120','--png',image,'--dump-report',state,'--report-sections','meta,watched_memory','--watch-fields','preview','--watch-window','delta:0xC600:10'] if platform=='gb' else [emulator,'run',rom,'--frames','120','--png',image,'--snapshot',state]
        run=subprocess.run(list(map(str,command)),capture_output=True,cwd=folder,timeout=120);assert run.returncode==0,run.stderr
        data=json.loads(state.read_text());raw=data['watched_memory'][0]['preview_bytes'] if platform=='gb' else data['bus']['ram'][0x600:0x60a]
        actual=[raw[i]+256*raw[i+1] for i in range(0,10,2)];errors=check_pixels(image,labels,platform)
        inputs=dependencies(source,compiler.parent/'lib')
        if platform=='fc':inputs['samples/font.chr']=sha(SITE/'samples/font.chr')
        row=dict(platform=platform,mode=mode,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),input_sha256=inputs,actual=actual,expected=expected,label_pixel_mismatches=errors,passed=actual==expected and not errors)
        records.append(row);print(platform,mode,row['passed'],actual,'label mismatches',errors,flush=True)
        if row['passed']:state.unlink()
        (OUT/'results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),records=records),indent=2),encoding='utf-8')
    if all(r['passed'] for r in records if r['platform']==platform):cleanup_build_outputs(folder)
raise SystemExit(0 if all(r['passed'] for r in records) else 1)
