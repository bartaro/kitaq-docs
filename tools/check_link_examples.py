"""Run actual KOKURA linked machines, then capture their saved final screens."""
from pathlib import Path
import argparse,hashlib,json,subprocess
from check_batch300 import dependencies
from check_entity_callbacks import check_pixels
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUT=SITE/'verification/api-link';AUTHOR=SITE/'tools/api_descriptions'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
compiler=REPOS/'kitaqgb/kitaqgb.exe';emu=REPOS/'kokura/kokura-cli.exe';lib=REPOS/'kitaqgb/lib'
def command(args,folder,log,timeout=180):
    p=subprocess.run(list(map(str,args)),cwd=folder,capture_output=True,timeout=timeout)
    (folder/log).write_bytes(p.stdout+p.stderr)
    if p.returncode:raise RuntimeError(str(args[0])+' failed: '+str(folder/log))
def values(state):
    watches={r['name']:r for r in state['watched_memory']};raw=[]
    for n in range(0,160,16):
        w=watches['r'+str(n)];assert not w.get('preview_truncated',False);raw+=w['preview_bytes']
    return [raw[n]+256*raw[n+1] for n in range(0,160,2)]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['dmg','cgb']);ap.add_argument('--group',choices=['control','raw','packet','four','deadline']);a=ap.parse_args()
    specs={s['name']:s for s in json.loads((AUTHOR/'link_examples.json').read_text())};records=[];links=[]
    groups={'control':['control'],'deadline':['deadline'],'raw':['raw_master','raw_slave'],'packet':['packet_master','packet_slave'],'four':['four_host','four_peer1','four_peer2','four_peer3']}
    for mode in ([a.mode] if a.mode else ['dmg','cgb']):
      for group,names in groups.items():
        if a.group and a.group!=group:continue
        root=OUT/mode/group;root.mkdir(parents=True,exist_ok=True);built={}
        for name in names:
            s=specs[name];folder=root/name;folder.mkdir(exist_ok=True);rom=folder/'example.gb';source=SITE/s['source']
            command([compiler,source,'-I',lib,'-I',SITE/'samples','-o',rom,'--profile=dev','--rst-disable','--stack-bank=fixed','--cgb='+mode,'--cart=mbc5','--romsize=128k','--no-cache','--no-disasm'],folder,'build.txt')
            built[name]=(s,folder,rom,source)
        if group not in ['control','deadline']:
            args=[emu,'--link-topology','link4' if group=='four' else 'pair','--run-frames','360','--dump-report',root/'link.json']
            for slot,name in enumerate(names):
                s,folder,rom,source=built[name]
                watches=','.join('r'+str(n)+':'+str(0xC600+n)+':16' for n in range(0,160,16))
                args+=['--link-session','name='+name+'|slot='+str(slot)+'|rom='+str(rom)+'|save_state='+str(folder/'final.kqs')+'|watch_window='+watches]
            command(args,root,'link.txt',timeout=240)
            linked=json.loads((root/'link.json').read_text(encoding='utf-8'))
            links.append({'mode':mode,'group':group,'summary':linked['runner_summary']})
        for index,name in enumerate(names):
            s,folder,rom,source=built[name];png=folder/'screen.png';runtime=folder/'runtime.json'
            args=[emu,rom,'--hardware',mode,'--run-frames','2' if group not in ['control','deadline'] else '330','--png',png,'--dump-report',runtime,'--report-sections','meta,cpu,watched_memory','--watch-fields','preview']
            if group not in ['control','deadline']:args+=['--load-state',folder/'final.kqs']
            for n in range(0,160,16):args+=['--watch-window','r'+str(n)+':'+str(0xC600+n)+':16']
            command(args,folder,'capture.txt');state=json.loads(runtime.read_text(encoding='utf-8'));actual=values(state);expected=s['expected']+[0]*(79-len(s['expected']))+[0xA55A]
            labels=s['labels']+[[13,y,str(expected[i]).zfill(5)] for y,i in s['values']];pixels=check_pixels(png,labels,'gb')
            link_actual=values(linked['sessions'][index]['report']) if group not in ['control','deadline'] else actual
            row={'platform':'gb','group':group,'lesson':name,'mode':mode,'source':s['source'],'source_sha256':sha(source),'rom':rom.relative_to(SITE).as_posix(),'rom_sha256':sha(rom),'image':png.relative_to(SITE).as_posix(),'image_sha256':sha(png),'compiler_sha256':sha(compiler),'emulator_sha256':sha(emu),'input_sha256':dependencies(source,lib),'actual':actual,'expected':expected,'linked_actual':link_actual,'pixel_mismatches':pixels,'passed':actual==expected==link_actual and pixels==0}
            records.append(row);print(mode,name,'PASS' if row['passed'] else 'FAIL','RAM',[(i,x,y) for i,(x,y) in enumerate(zip(actual,expected)) if x!=y][:12],'pixels',pixels,flush=True)
            # Retain Link4 symbols until the linked run has finished routing peers.
            cleanup_build_outputs(folder)
        result={'records':records,'links':links,'script_sha256':sha(Path(__file__)),'manifest_sha256':sha(AUTHOR/'link_examples.json')}
        (OUT/'partial_results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    report=OUT/((('-'.join(x for x in [a.mode,a.group] if x))+'-results.json') if a.mode or a.group else 'results.json')
    report.write_text(json.dumps(result,indent=2),encoding='utf-8')
    raise SystemExit(0 if all(r['passed'] for r in records) else 1)
if __name__=='__main__':main()
