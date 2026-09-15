"""Compare RLE decoded buffers, counts, bank restoration and LCD-on/off VRAM writes."""
from pathlib import Path
import argparse,hashlib,json,subprocess
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUT=SITE/'verification/api-rle/state';OUT.mkdir(parents=True,exist_ok=True)
compiler=REPOS/'kitaqgb/kitaqgb.exe';emulator=REPOS/'kokura/kokura-cli.exe';library=REPOS/'kitaqgb/lib'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
streams={'empty':[0,9,99],'single':[1,0x5A,0],'zero_value':[4,0,3,0xA5,0],'max_run':[255,0x12,0],'two_pages':[255,0x12,255,0xA5,0],'source_page':sum(([1,i&255] for i in range(130)),[])+[0]}
def expand(stream):
    result=[];i=0
    while stream[i]:result += [stream[i+1]]*stream[i];i+=2
    return result
cases=[]
for name,stream in streams.items():
    for api in ['rle_decode','rle_decode_far']:cases.append((api,name,stream,'dmg',False,0))
    for mode,lcd,vbk in [('dmg',False,0),('dmg',True,0),('cgb',False,0),('cgb',True,0),('cgb',False,1)]:cases.append(('__rle_decode_vram',name,stream,mode,lcd,vbk))
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--only');args=parser.parse_args()
rows=[]
for api,label,stream,mode,lcd,vbk in cases:
    name=api.lstrip('_')+'-'+label+'-'+mode+('-on' if lcd else '-off')+'-'+str(vbk)
    if args.only and name!=args.only:continue
    folder=OUT/name;folder.mkdir(exist_ok=True);source=folder/'case.c';rom=folder/'case.gb';snapshot=folder/'runtime.json'
    destination=0x9001 if api.startswith('__') else 0xC301
    # Place both implementation and caller in the common bank. Bank 1's marker
    # checks that a bank-2 source read restores the mapping on return.
    text='''#pragma bank 0
#include "rle.c"
void __bankswitch(u8 bank);
__location(0xFF40) u8 lcdc;
__location(0xFF4F) u8 vbk;
__location(0xC600) u8 result[16];
u16 i;
u16 decoded;
u8 ram_source[264];
#pragma fixed_bank 1
__prg_rom u8 marker[1]={0xA1};
#pragma fixed_bank 2
__prg_rom u8 encoded['''+str(len(stream))+']={'+','.join(map(str,stream))+'''};
#pragma fixed_bank 0
void main(){__wait_vblank();lcdc=0;
'''
    if mode=='cgb':text+='vbk='+str(vbk)+';'
    text+='for(i=0;i<528;i++)*((u8*)('+str(destination-1)+'+i))=204;'
    if api=='rle_decode':
        text+='__bankswitch(2);for(i=0;i<'+str(len(stream))+';i++)ram_source[i]=encoded[i];'
    text+='__bankswitch(1);'
    if lcd:text+='lcdc=0x91;'
    call=api+'('+('(void*)' if not api.startswith('__') else '')+str(destination)+','+('ram_source' if api=='rle_decode' else '2,encoded')+')'
    text+='decoded='+call+';'
    # Read VRAM only after disabling the LCD safely; the decoder itself ran with
    # the requested LCD state. RAM cases use the same observation protocol.
    if lcd:text+='__wait_vblank();lcdc=0;'
    text+='result[0]=(u8)decoded;result[1]=(u8)(decoded>>8);result[2]=*marker;result[3]=*((u8*)0xFF82);result[4]=vbk&1;result[15]=165;while(1){}}'
    source.write_text(text,encoding='ascii')
    process=subprocess.run([str(compiler),str(source),'-I',str(library),'-o',str(rom),'--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb','--no-cache','--no-disasm'],cwd=folder,capture_output=True,timeout=90)
    (folder/'build.txt').write_bytes(process.stdout+process.stderr)
    row={'name':name,'api':api,'stream':stream,'mode':mode,'lcd_on':lcd,'vbk':vbk,'source_sha256':sha(source),'build_exit':process.returncode,'passed':False}
    if process.returncode==0:
        command=[str(emulator),str(rom),'--hardware',mode,'--run-frames','240','--dump-report',str(snapshot),'--watch-window','result:50688:16']
        for offset in range(0,528,16):command+=['--watch-window',f'data{offset}:{destination-1+offset}:16']
        process=subprocess.run(command,cwd=folder,capture_output=True,timeout=120);(folder/'runtime.txt').write_bytes(process.stdout+process.stderr);row['runtime_exit']=process.returncode
        if process.returncode==0:
            state=json.loads(snapshot.read_text(encoding='utf-8'));watches={w['name']:w for w in state['watched_memory']};actual=[]
            for offset in range(0,528,16):
                w=watches['data'+str(offset)];assert w['size']==16 and not w.get('preview_truncated',False);actual+=w['preview_bytes']
            decoded=expand(stream);expected=[204]+decoded+[204]*(527-len(decoded));result=watches['result']['preview_bytes']
            expected_result=[len(decoded)&255,len(decoded)>>8,161,1,vbk if mode=='cgb' else 1]+[0]*10+[165]
            row.update(actual=actual,expected=expected,result=result,expected_result=expected_result,rom_sha256=sha(rom),passed=actual==expected and result==expected_result)
            if row['passed']:snapshot.write_text(json.dumps({'actual':actual,'result':result},indent=2),encoding='utf-8');cleanup_build_outputs(folder)
    rows.append(row)
    report={'compiler_sha256':sha(compiler),'emulator_sha256':sha(emulator),'script_sha256':sha(Path(__file__)),'source_sha256':{'kitaqgb/lib/rle.c':sha(library/'rle.c'),'kitaqgb/lib/rpg.h':sha(library/'rpg.h')},'cases':rows}
    (OUT/('selected_results.json' if args.only else 'results.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(name,'PASS' if row['passed'] else 'FAIL',flush=True)
print(sum(r['passed'] for r in rows),'/',len(rows),'passed')
raise SystemExit(0 if all(r['passed'] for r in rows) else 1)
