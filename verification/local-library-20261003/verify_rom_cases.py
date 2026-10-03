"""Rebuild and replay the saved local-library cases. Python standard library only."""
from pathlib import Path
import argparse,json,subprocess,hashlib

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--compiler',type=Path,required=True)
    parser.add_argument('--kokura',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--only',help='Run one named case for a bounded replay')
    args=parser.parse_args();base=Path(__file__).resolve().parent
    args.compiler=args.compiler.resolve();args.kokura=args.kokura.resolve();args.out=args.out.resolve()
    lib=base/'sources/lib';manifest=json.loads((base/'manifest.json').read_text(encoding='utf-8'))
    for name,digest in manifest['library_sha256'].items():
        assert hashlib.sha256((lib/name).read_bytes()).hexdigest()==digest,name
    records=[]
    for case in manifest['rom_cases']:
        if args.only and case['name']!=args.only:continue
        folder=args.out/case['name'];folder.mkdir(parents=True,exist_ok=True)
        source=base/case['source'];rom=folder/'case.gb'
        assert hashlib.sha256(source.read_bytes()).hexdigest()==case['source_sha256'],case['name']
        command=[str(args.compiler),str(source),'-I',str(lib),'-o',str(rom),'--no-cache','--no-disasm','--rst-disable','--stack-bank=fixed','--cgb=cgb','--cart=mbc5','--romsize=128k']
        result=subprocess.run(command,cwd=folder,capture_output=True,timeout=120)
        (folder/'build.log').write_bytes(result.stdout+result.stderr)
        if result.returncode:raise RuntimeError('Build failed: '+case['name'])
        symbols={}
        for line in rom.with_suffix('.map').read_text(encoding='utf-8').splitlines():
            row=line.split()
            if len(row)==6 and row[3]=='S':symbols[row[5]]=int(row[0],16)
        address=symbols[case['result_symbol']]if 'result_symbol'in case else case['result_address']
        for check in case['checks']:
            mode=check['mode'];report=folder/(mode+'.json');size=len(check['expected'])*2
            command=[str(args.kokura),str(rom),'--hardware',mode,'--run-frames','90','--dump-report',str(report),'--report-sections','cpu,meta,watched_memory','--watch-fields','preview']
            for offset in range(0,size,16):command+=['--watch-window',f'r{offset}:{address+offset}:{min(16,size-offset)}']
            if 'done_symbol'in case:command+=['--watch-window',f'done:{symbols[case["done_symbol"]]}:1']
            result=subprocess.run(command,cwd=folder,capture_output=True,timeout=120)
            (folder/(mode+'.log')).write_bytes(result.stdout+result.stderr)
            if result.returncode:raise RuntimeError('Emulator failed: '+case['name']+' '+mode)
            state=json.loads(report.read_text(encoding='utf-8'));watch={w['name']:w['preview_bytes']for w in state['watched_memory']}
            raw=sum([watch['r'+str(i)]for i in range(0,size,16)],[])
            actual=[raw[i]+raw[i+1]*256 for i in range(0,size,2)]
            passed=actual==check['expected']and('done_symbol'not in case or watch['done']==[165])
            row={'name':case['name'],'mode':mode,'expected':check['expected'],'actual':actual,'passed':passed,'rom_sha256':hashlib.sha256(rom.read_bytes()).hexdigest()}
            records.append(row);print(case['name'],mode,'PASS'if passed else'FAIL',flush=True)
    result={'records':records,'passed':bool(records)and all(r['passed']for r in records)}
    (args.out/'results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    if not result['passed']:raise SystemExit(1)

if __name__=='__main__':main()
