"""Check original FDS load/call lessons with an independent LoadFiles ABI fixture.

This exercises compiled CPU code, RAM transfers and full display pixels. It does
not emulate the real BIOS, disk mechanics, CRC, write behavior or hardware boot.
"""
from pathlib import Path
import hashlib,json,os,subprocess,sys
from check_api_tile_examples import read_png
from check_batch200 import dependencies
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.is_dir():REPOS=SITE.parent
sys.path.insert(0,str(REPOS/'kitaqfc/scripts'))
from fds_abi_fixture import disk_files,loadfiles_firmware
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
OUT=SITE/'verification/api-fds-load/example';OUT.mkdir(parents=True,exist_ok=True)
compiler=Path(os.environ.get('KITAQFC_TEST_COMPILER',str(REPOS/'kitaqfc/kitaqfc.exe')))
emulator=REPOS/'kurosaki/kurosaki.exe';lib=REPOS/'kitaqfc/lib'
fontpath=SITE/'samples/font.chr';font=fontpath.read_bytes();records=[]

def scene(labels):
    pixels=set()
    for tx,ty,label in labels:
        for n,c in enumerate(label):
            for y in range(8):
                bits=font[ord(c)*16+y]|font[ord(c)*16+y+8]
                for x in range(8):
                    if bits & (128>>x):pixels.add(((tx+n)*8+x,ty*8+y))
    return pixels

for lesson,values in [('overlay_call',[42,1,1,2,1]),('farcall',[42,1,1,2,1]),
                      ('call_alias',[42,1,1,2,1]),('bank_load',[0,2,0,11,44,0,1,0,255,255]),
                      ('raw_overlay',[0,255,0,11,44,0,1])]:
    for variant,flags in [('default',[]),('unoptimized',['-O0'])]:
        mode=lesson+'-'+variant;folder=OUT/mode;folder.mkdir(exist_ok=True)
        source=SITE/('samples/api-examples/fc/fds_'+lesson+'.c')
        rom=folder/'example.fds';image=folder/'screen.png';statepath=folder/'state.json'
        fixture=folder/'loadfiles-fixture.bin'
        cmd=[str(compiler),str(source),'-I',str(lib),'-I',str(SITE/'samples'),'-o',str(rom),
             '--mapper=fds','--fds-layout=fds32','--fds-no-license-bypass','--fds-overlay-trim',
             '--nes-chr='+str(fontpath),'--no-cache','--no-disasm']+flags
        inputs=dependencies(source,lib);inputs['samples/font.chr']=sha(fontpath)
        inputs['kitaqfc/scripts/fds_abi_fixture.py']=sha(REPOS/'kitaqfc/scripts/fds_abi_fixture.py')
        p=subprocess.run(cmd,capture_output=True,cwd=folder,timeout=90)
        if p.returncode:raise RuntimeError(mode+': '+(p.stdout+p.stderr).decode(errors='replace')[-4000:])
        fixture.write_bytes(loadfiles_firmware(disk_files(rom)))
        p=subprocess.run([str(emulator),'run',str(rom),'--frames','120','--snapshot',str(statepath),'--png',str(image)],
                         capture_output=True,cwd=folder,env={**os.environ,'KUROSAKI_DISKSYS_ROM':str(fixture)},timeout=90)
        if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace')[-2000:])
        state=json.loads(statepath.read_text());ram=state['bus']['ram']
        actual=ram[0x600:0x600+len(values)]+[ram[0x60F],ram[0x701]];expected=values+[165,0]
        ids=ram[0x780:0x780+ram[0x700]]
        if lesson in ['overlay_call','farcall','call_alias']:
            labels=[(2,2,'FDS CALL AND RETURN'),(2,5,'RETURN VALUE'),(25,5,'042'),(2,7,'CALLBACK COUNT'),(25,7,'001'),
                    (2,9,'BANK EXPR COUNT'),(25,9,'001'),(2,11,'BANK IN CALLBACK'),(25,11,'002'),
                    (2,13,'BANK AFTER RETURN'),(25,13,'001'),(2,16,'CALL BANK 2 / RESTORE BANK 1')]
        elif lesson=='bank_load':
            labels=[(2,2,'FDS DATA WINDOW'),(2,5,'LOAD BANK 2 STATUS'),(25,5,'000'),(2,7,'FIRST / LAST BYTE'),
                    (21,7,'011'),(25,7,'044'),(2,9,'REQUIRE SAME BANK'),(25,9,'000'),(2,11,'RESTORE BANK 1'),(25,11,'000'),
                    (2,13,'RESIDENT BANK'),(25,13,'001'),(2,16,'INVALID BANKS 0 / 255'),(2,18,'255'),(8,18,'255')]
        else:
            labels=[(2,2,'FDS RAW FILE-ID LOAD'),(2,5,'FILE 32 LOAD STATUS'),(25,5,'000'),(2,7,'FIRST / LAST BYTE'),
                    (21,7,'011'),(25,7,'044'),(2,9,'UNKNOWN BANK RECORD'),(25,9,'255'),(2,11,'IS BANK 1 RESIDENT'),
                    (25,11,'000'),(2,13,'REQUIRE BANK 1'),(25,13,'000'),(2,15,'RESIDENT AFTER RELOAD'),(25,15,'001')]
        pixels=scene(labels);w,h,ch,rows=read_png(image);assert (w,h)==(256,240)
        bad=[(x,y) for y in range(h) for x in range(w) if (sum(rows[y][x*ch:x*ch+3])>384)!=((x,y) in pixels)]
        row=dict(platform='fc',mode=mode,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),
                 rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),
                 compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),input_sha256=inputs,fixture_sha256=sha(fixture),
                 actual=actual,expected=expected,load_ids=ids,expected_load_ids=[32,0],pixel_mismatches=len(bad),first_mismatches=bad[:10],
                 passed=actual==expected and ids==[32,0] and not bad)
        records.append(row);print(mode,'PASS' if row['passed'] else 'FAIL',actual,'ids',ids,'pixels',len(bad),flush=True)
        (OUT/'results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),records=records),indent=2),encoding='utf-8')
        if row['passed']:
            statepath.unlink();fixture.unlink();cleanup_build_outputs(folder)
raise SystemExit(0 if all(r['passed'] for r in records) else 1)
