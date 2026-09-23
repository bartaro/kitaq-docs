"""Check unmodified peripheral lesson ROMs, port operations and complete images.

The current KUROSAKI input bus has no keyboard, light-gun or serial adapter
model. Captures are explicitly the no-device-model baseline, not hardware proof.
"""
from pathlib import Path
import hashlib,json,os,subprocess
from check_api_tile_examples import read_png
from check_batch200 import dependencies
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.is_dir():REPOS=SITE.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
OUT=SITE/'verification/api-peripheral/example';OUT.mkdir(parents=True,exist_ok=True)
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
                    if bits&(128>>x):pixels.add(((tx+n)*8+x,ty*8+y))
    return pixels
for lesson,values in [('keyboard',[0,0,0]+[0]*18),('zapper',[0,0,1,0,0,1,0,1]),('serial',[0])]:
    for variant,flags in [('default',[]),('unoptimized',['-O0'])]:
        mode=lesson+'-'+variant;folder=OUT/mode;folder.mkdir(exist_ok=True)
        source=SITE/('samples/api-examples/fc/peripheral_'+lesson+'.c')
        rom=folder/'example.nes';image=folder/'screen.png';statepath=folder/'state.json';trace=folder/'trace.jsonl'
        cmd=[str(compiler),str(source),'-I',str(lib),'-I',str(SITE/'samples'),'-o',str(rom),'--mapper=nrom',
             '--nes-chr='+str(fontpath),'--no-cache','--no-disasm']+flags
        inputs=dependencies(source,lib);inputs['samples/font.chr']=sha(fontpath)
        p=subprocess.run(cmd,capture_output=True,cwd=folder,timeout=90)
        if p.returncode:raise RuntimeError(mode+': '+(p.stdout+p.stderr).decode(errors='replace')[-4000:])
        p=subprocess.run([str(emulator),'run',str(rom),'--frames','120','--snapshot',str(statepath),'--png',str(image)],capture_output=True,cwd=folder,timeout=90);assert p.returncode==0
        state=json.loads(statepath.read_text());ram=state['bus']['ram']
        actual=(ram[0x600:0x603]+ram[0x640:0x652] if lesson=='keyboard' else ram[0x600:0x600+len(values)])+[ram[0x61F]];expected=values+[165]
        p=subprocess.run([str(emulator),'trace',str(rom),'--frames','6','--mem-read','--mem-write','--out',str(trace)],capture_output=True,cwd=folder,timeout=90);assert p.returncode==0
        active=False;operations=[]
        with trace.open(encoding='utf-8') as stream:
            for line in stream:
                e=json.loads(line)
                if e['kind']=='mem.write' and e.get('addr')==0x700:active=e['value']==1
                if active and e['kind'] in ['mem.write','mem.read'] and e.get('addr') in [0x4016,0x4017]:operations.append([e['kind'],e['addr'],e['value']])
        writes=[v for k,a,v in operations if k=='mem.write'];reads=[a for k,a,v in operations if k=='mem.read']
        if lesson=='keyboard':
            expected_writes=[5,4]+[6,4]*9+[0]+[5]+[4,6]*9+[0]+[5,4]+[6,4]*6+[0]
            expected_reads=[0x4017]*20
            labels=[(2,2,'KEYBOARD STARTUP SNAPSHOT'),(2,4,'DEVICE DETECT'),(25,4,'000'),(2,6,'ROW 6 COL 0'),(25,6,'000'),
                    (2,8,'A KEY - GUARDED'),(25,8,'000'),(2,10,'ROW   COL0  COL1  (HEX)'),(2,23,'RAW MATRIX - NOT ASCII')]
            for row in range(9):labels.extend([(3,12+row,str(row)),(9,12+row,'00'),(15,12+row,'00')])
        elif lesson=='zapper':
            expected_writes=[];expected_reads=[0x4016]*3+[0x4017]*5
            labels=[(2,2,'LIGHT-GUN INPUT SNAPSHOT'),(2,5,'PORT   RAW  TRIGGER  LIGHT'),(3,8,'1'),(9,8,'00'),(15,8,'000'),(24,8,'001'),
                    (3,10,'2'),(9,10,'00'),(15,10,'000'),(24,10,'001'),(2,13,'DEFAULT = PORT 2'),(2,15,'TRIGGER'),(15,15,'000'),
                    (2,17,'LIGHT'),(15,17,'001'),(2,21,'LIGHT 1 IS NOT A HIT TEST')]
        else:
            expected_writes=[0,1,0,1,0,1,1];expected_reads=[0x4017]
            labels=[(2,2,'SERIAL BIT PRIMITIVES'),(2,5,'VALUE       EXPECTED OUT0'),(2,20,'RX SAMPLE'),(23,20,'000'),(2,23,'NO BYTE FRAMING OR CLOCK')]
            for i,v in enumerate([0,1,2,3,254,255]):labels.extend([(3,7+i*2,f'{v:03}'),(23,7+i*2,str(v&1))])
        pixels=scene(labels);w,h,ch,rows=read_png(image);assert (w,h)==(256,240)
        bad=[(x,y) for y in range(h) for x in range(w) if (sum(rows[y][x*ch:x*ch+3])>384)!=((x,y) in pixels)]
        row=dict(platform='fc',mode=mode,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),
                 image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),input_sha256=inputs,
                 actual=actual,expected=expected,port_writes=writes,expected_writes=expected_writes,port_reads=reads,expected_reads=expected_reads,
                 pixel_mismatches=len(bad),first_mismatches=bad[:10],passed=actual==expected and writes==expected_writes and reads==expected_reads and not bad)
        records.append(row);print(mode,'PASS' if row['passed'] else 'FAIL',actual,'pixels',len(bad),'writes',len(writes),'reads',len(reads),flush=True)
        (OUT/'results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),records=records),indent=2),encoding='utf-8')
        if row['passed']:statepath.unlink();trace.unlink();cleanup_build_outputs(folder)
raise SystemExit(0 if all(r['passed'] for r in records) else 1)
