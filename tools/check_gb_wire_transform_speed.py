"""Compare independent Q6 rotation expectations and bounded emulator timings."""
from pathlib import Path
import hashlib,json,subprocess,re
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'publish/library_docs_20260914/wire-speed'
REPOS=ROOT/'publish/github_20260912'
SIN=[0,24,45,59,64,59,45,24,0,-24,-45,-59,-64,-59,-45,-24]

def main():
    rows=[]
    for profile,height in [('dmg',96),('dmg',120),('cgb',96)]:
        prefix='w3ddmg' if profile=='dmg' else 'w3dcgb'
        expected=[]
        for axis in ['y','x','z']:
            for angle in range(16):
                a,b=-220,187;s,c=SIN[angle],SIN[(angle+4)&15]
                pair=((a*c+b*s)>>6,(b*c-a*s)>>6) if axis=='y' else ((a*c-b*s)>>6,(a*s+b*c)>>6)
                expected.extend(v&65535 for v in pair)
        for version in ['baseline','optimized']:
            folder=OUT/(profile+str(height)+'-'+version);folder.mkdir(exist_ok=True)
            library=(OUT if version=='baseline' else REPOS/'kitaqgb/lib')/('wire3d_'+profile+'.c')
            source=folder/'case.c';rom=folder/'case.gb'
            text='#pragma bank 0\n#define WIRE3D_DMG_HEIGHT '+str(height)+'\n__location(0xC110) u16 results[8];\n__location(0xC120) u8 done;\n'
            text+='__prg_rom const u16 expected[96]={'+','.join(map(str,expected))+'};\n'
            body=library.read_text(encoding='utf-8')
            if profile=='dmg':
                # Use identical helper placement in both benchmark versions;
                # the additional test harness must not crowd fixed transfer code.
                for axis in ['y','x','z']:
                    start=re.search(r'static void w3ddmg_rotate_'+axis+r'\([^;\n]+\)\n',body).start()
                    pos=body.rfind('#pragma bank ',0,start)
                    end=body.index('\n',pos)
                    body=body[:pos]+'#pragma bank 2'+body[end:]
            text+=body+'\n#pragma bank 0\nvoid main(){u8 i;s16 a,b;'
            for k,axis in enumerate(['y','x','z']):
                text+='results['+str(k)+']=0;for(i=0;i<16;i++){a=-300;b=187;'+prefix+'_rotate_'+axis+'(&a,&b,i);if((u16)a!=expected['+str(k*32)+'+i*2])results['+str(k)+']++;if((u16)b!=expected['+str(k*32+1)+'+i*2])results['+str(k)+']++;}'
            text+='results[3]=96;results[4]=0xA55A;done=165;while(1){}}\n';source.write_text(text,encoding='utf-8')
            cmd=[str(REPOS/'kitaqgb/kitaqgb.exe'),str(source),'-I',str(REPOS/'kitaqgb/lib'),'-o',str(rom),'--profile=dev','--stack-bank=fixed','--rst-disable','--cgb=cgb','--cart=mbc5','--romsize=256k','--no-cache','--no-disasm']
            result=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=180);(folder/'build.txt').write_bytes(result.stdout+result.stderr)
            if result.returncode:raise RuntimeError(str(folder)+' build failed')
            report=folder/'run.json'
            cmd=[str(REPOS/'kokura/kokura-cli.exe'),str(rom),'--hardware',profile,'--run-frames','240','--watchpoint','0xC120','--dump-report',str(report),'--report-sections','meta,watched_memory','--watch-fields','preview']
            for offset in range(0,16,16):cmd+=['--watch-window',f'r{offset}:{0xC110+offset}:16']
            result=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=180);(folder/'run.txt').write_bytes(result.stdout+result.stderr)
            if result.returncode:raise RuntimeError(str(folder)+' run failed')
            data=json.loads(report.read_text());watch={w['name']:w['preview_bytes'] for w in data['watched_memory']};raw=sum([watch['r'+str(offset)] for offset in range(0,16,16)],[])
            actual=[raw[i]+256*raw[i+1] for i in range(0,16,2)]
            row=dict(profile=profile,height=height,version=version,cycles_to_done=data['meta']['observation_cycle'],actual=actual,expected=expected,passed=actual==[0,0,0,96,0xA55A,0,0,0],library_sha256=hashlib.sha256(library.read_bytes()).hexdigest(),rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest())
            rows.append(row);print(profile,height,version,row['passed'],row['cycles_to_done'],[(i,a,b) for i,(a,b) in enumerate(zip(actual,[0,0,0,96,0xA55A,0,0,0])) if a!=b][:6],flush=True)
            (OUT/'rotation-results.json').write_text(json.dumps(rows,indent=2))
    assert all(r['passed'] for r in rows)

if __name__=='__main__':main()
