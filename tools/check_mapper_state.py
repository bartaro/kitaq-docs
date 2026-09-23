"""Execute mapper contracts using PPU readback and MMC3 register traces.

All CHR bytes are generated here. No commercial cartridge assets are used.
The state-only fixtures and their logs stay in the private state directory.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess

SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.is_dir():REPOS=SITE.parent
COMPILER=REPOS/'kitaqfc/kitaqfc.exe'
EMULATOR=REPOS/'kurosaki/kurosaki.exe'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--only');opt=ap.parse_args()
OUT=SITE/'verification/api-mapper/state';OUT.mkdir(parents=True,exist_ok=True)
chrfile=OUT/'bank-markers.chr'
chrfile.write_bytes(b''.join(bytes([i+17])*1024 for i in range(32)))
prefix='''#include "nes_game.h"
__location(0x2007) u8 data_port;
__location(0x0600) u8 result[192];
u8 read_ppu(u16 address) {
    u8 ignored;
    __ppu_addr(address); ignored=data_port; return data_port;
}
void write_ppu(u16 address,u8 value) { __ppu_addr(address);data_port=value; }
void main(){u8 i;u8 j;u8 k;__irq_disable();__ppu_mask_set(0);__ppu_ctrl_set(0);
'''
suffix='result[191]=165;while(1){}}'
cases=[]
def add(name,mapper,body,expected,trace=None):
    cases.append(dict(name=name,mapper=mapper,body=body,expected=expected,trace=trace))

for mapper,number in [('nrom',0),('mmc1',1),('uxrom',2),('cnrom',3),('mmc3',4),('mmc5',5),('axrom',7),('vrc6',24),('vrc7',85),('fme7',69)]:
    add('identity-'+mapper,mapper,'result[0]=__mapper_id();',[number])
for mapper in ['cnrom','mmc3']:
    for api in ['__chr_bank_set','__chr_bank_set0','__chr_bank_set1']:
        # Read four 1 KiB pages after every selection. The oracle uses distinct
        # bytes from the generated ROM, not the emulator's reported bank state.
        body='k=0;for(i=0;i<8;i++){'+api+'(i);for(j=0;j<4;j++){result[k]=read_ppu((u16)j*1024);k++;}}'
        expected=[]
        for bank in range(8):
            if mapper=='cnrom':expected += [17+(bank%4)*8+j for j in range(4)]
            elif api=='__chr_bank_set1':expected += [17,18,17+(bank&254),18+(bank&254)]
            else:expected += [17+(bank&254),18+(bank&254),17,18]
        add('chr-'+mapper+'-'+api,mapper,body,expected)

vertical=[17,34,17,34];horizontal=[17,17,34,34]
lower=[17]*4;upper=[34]*4
for mapper,seed,modes in [
    ('axrom','__mirroring_set(0);write_ppu(0x2000,17);__mirroring_set(1);write_ppu(0x2000,34);',[lower,upper]),
    ('mmc1','__mirroring_set(0);write_ppu(0x2000,17);__mirroring_set(1);write_ppu(0x2000,34);',[lower,upper,vertical,horizontal]),
    ('mmc3','__mirroring_set(0);write_ppu(0x2000,17);write_ppu(0x2400,34);',[vertical,horizontal]),
    ('mmc5','__mirroring_set(2);write_ppu(0x2000,17);__mirroring_set(3);write_ppu(0x2000,34);',[horizontal,vertical,lower,upper]),
    ('fme7','__mirroring_set(2);write_ppu(0x2000,17);__mirroring_set(3);write_ppu(0x2000,34);',[vertical,horizontal,lower,upper]),
]:
    body=seed+'k=0;for(i=0;i<8;i++){__mirroring_set(i);for(j=0;j<4;j++){result[k]=read_ppu(0x2000+(u16)j*1024);k++;}}'
    add('mirror-'+mapper,mapper,body,[v for i in range(8) for v in modes[i%len(modes)]])

for label,setter,enable,disable,ack in [
    ('intrinsics','__mapper_irq_set','__mapper_irq_enable','__mapper_irq_disable','__mapper_irq_ack'),
    ('scanline','__irq_scanline_set','__mapper_irq_enable','__mapper_irq_disable','__mapper_irq_ack'),
    ('wrappers','nes_mapper_irq_set','nes_mapper_irq_enable','nes_mapper_irq_disable','nes_mapper_irq_ack'),
]:
    body=disable+'();'+setter+'(37);'+enable+'();'+ack+'();'+enable+'();'+disable+'();'+setter+'(0);'+setter+'(255);result[0]=__mapper_id();'
    # Values for E000/E001 are ignored by hardware. Check only their addresses.
    sequence=[(0xE000,None),(0xC000,37),(0xC001,37),(0xE001,None),(0xE000,None),(0xE001,None),(0xE000,None),(0xC000,0),(0xC001,0),(0xC000,255),(0xC001,255)]
    add('irq-'+label,'mmc3',body,[4],sequence)

rows=[]
for variant,flags in [('default',[]),('unoptimized',['-O0'])]:
    for case in cases:
        if opt.only and opt.only not in case['name']:continue
        folder=OUT/(variant+'-'+case['name']);folder.mkdir(exist_ok=True)
        source=folder/'case.c';rom=folder/'case.nes';snapshot=folder/'snapshot.json'
        source.write_text(prefix+case['body']+suffix,encoding='ascii')
        command=[str(COMPILER),str(source),'-I',str(REPOS/'kitaqfc/lib'),'-o',str(rom),'--mapper='+case['mapper'],'--nes-chr='+str(chrfile),'--no-cache','--no-disasm']+flags
        p=subprocess.run(command,capture_output=True,timeout=90,cwd=folder)
        row=dict(name=case['name'],variant=variant,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),build_exit=p.returncode,expected=case['expected'],passed=False)
        if p.returncode:row['error']=(p.stdout+p.stderr).decode(errors='replace')[-1800:]
        else:
            p=subprocess.run([str(EMULATOR),'run',str(rom),'--frames','40','--headless','--snapshot',str(snapshot)],capture_output=True,timeout=90,cwd=folder)
            row['run_exit']=p.returncode
            if not p.returncode:
                state=json.loads(snapshot.read_text());ram=state['bus']['ram']
                row.update(actual=ram[0x600:0x600+len(case['expected'])],done=ram[0x6BF],rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom))
                row['passed']=row['actual']==row['expected'] and row['done']==165
                if case['trace']:
                    trace=folder/'trace.jsonl'
                    p=subprocess.run([str(EMULATOR),'trace',str(rom),'--frames','2','--out',str(trace),'--mapper'],capture_output=True,timeout=90,cwd=folder)
                    events=[json.loads(line) for line in trace.read_text().splitlines()]
                    writes=[(e['addr'],e['value']) for e in events if e.get('kind')=='mapper.mmc3_write' and e.get('addr',0)>=0xC000]
                    # Startup may disable MMC3 IRQs; require the complete final
                    # call sequence, with no extra writes after the first latch.
                    first=next((i for i,e in enumerate(writes) if e==(0xC000,37)),None)
                    got=writes[first-1:] if first is not None and first>0 else []
                    matches=len(got)==len(case['trace']) and all(a==c and (d is None or b==d) for (a,b),(c,d) in zip(got,case['trace']))
                    row.update(trace_exit=p.returncode,mapper_writes=got,expected_writes=case['trace'],trace_matches=matches)
                    row['passed'] &= matches and p.returncode==0
                    if row['passed']:trace.unlink()
                if row['passed']:snapshot.unlink()
        rows.append(row)
        print(variant,case['name'],'PASS' if row['passed'] else 'FAIL',row.get('actual',row.get('error','')),flush=True)
        report=dict(script_sha256=sha(Path(__file__)),compiler_sha256=sha(COMPILER),emulator_sha256=sha(EMULATOR),chr_sha256=sha(chrfile),header_sha256={n:sha(REPOS/'kitaqfc/lib'/n) for n in ['intrinsics.h','nes_game.h']},records=rows)
        (OUT/('results.json' if not opt.only else opt.only+'-results.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
raise SystemExit(0 if all(r['passed'] for r in rows) and rows else 1)
