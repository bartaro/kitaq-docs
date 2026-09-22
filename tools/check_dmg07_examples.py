"""Run real linked console instances with KOKURA's DMG-07 protocol model."""
from pathlib import Path
import argparse,hashlib,json,stat
from check_link_examples import command,values,compiler,emu,lib,SITE,dependencies
from check_entity_callbacks import check_pixels
from check_api_tile_examples import read_png
from api_build_cleanup import cleanup_build_outputs
OUT=SITE/'verification/api-dmg07';OUT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
LABELS={'exchange':[[1,0,'DMG07 EXCHANGE'],[1,2,'PLAYER'],[1,4,'PLAYERS MASK'],[1,6,'SENT SEQ'],[1,8,'PACKET SEQ'],[1,10,'PLAYER 1'],[1,11,'PLAYER 2'],[1,12,'PLAYER 3'],[1,13,'PLAYER 4'],[1,15,'ERROR']], 'absent':[[1,0,'DMG07 NO ADAPTER'],[1,2,'PLAYER'],[1,4,'START ERROR'],[1,6,'SILENT FRAME'],[1,8,'TIMEOUTS'],[1,10,'DISCONNECTS'],[1,12,'ERROR'],[1,14,'EMPTY BUFFER'],[1,16,'CLEARED']]}
DISPLAY={'exchange':[(2,0),(4,1),(6,6),(8,7),(10,11),(11,12),(12,13),(13,14),(15,20)],'absent':[(2,1),(4,3),(6,6),(8,7),(10,8),(12,9),(14,14),(16,17)]}
LABELS['overflow']=[list(x) for x in LABELS['exchange']]+[[1,16,'CLEAR ERROR']];LABELS['overflow'][0][2]='DMG07 OVERFLOW'
DISPLAY['overflow']=DISPLAY['exchange']+[(16,21)]
LABELS['restart']=[[1,0,'DMG07 RESTART']]+[[1,y,t] for y,t in [(2,'PLAYER'),(4,'DATA VALID'),(6,'PENDING'),(8,'SENT FF'),(10,'RESET PHASE'),(12,'SLOT AFTER'),(14,'RESET PRIME'),(16,'ERROR')]]
DISPLAY['restart']=[(2,0),(4,2),(6,4),(8,5),(10,6),(12,7),(14,9),(16,14)]
def expectation(lesson,slot):
    if lesson=='restart':return [slot,1,1,0,int(slot==2),int(slot==2),0,0,0,0,0,0,0,0,0]
    if lesson=='overflow':return [slot,15,240+slot,1,0,0,3,2,3,1,1,33,34,35,36,0,36,0,0,1,6,0,1]
    return [slot,15,240+slot,1,0,0,2,1,3,1,1,33,34,35,36,0,36,0,0,0,0] if lesson=='exchange' else [0,0,0,2,1,0,12,1,0,4,1,0,0,0,77,0,0,0,1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['dmg','cgb']);ap.add_argument('--lesson',choices=['exchange','absent','restart','overflow']);args=ap.parse_args();records=[];links=[];deleted=[]
    for mode in ([args.mode] if args.mode else ['dmg','cgb']):
      for lesson in ([args.lesson] if args.lesson else ['exchange','absent','restart','overflow']):
        root=OUT/mode/lesson;root.mkdir(parents=True,exist_ok=True);source=SITE/'samples/api-examples/gb'/('dmg07_'+lesson+'.c');rom=root/'example.gb'
        command([compiler,source,'-I',lib,'-I',SITE/'samples','-o',rom,'--profile=dev','--rst-disable','--stack-bank=fixed','--cgb='+mode,'--cart=mbc5','--romsize=128k','--no-cache','--no-disasm'],root,'build.txt')
        count=1 if lesson=='absent' else 4
        if count==4:
            cmd=[emu,'--link-topology','dmg07','--run-frames','90','--dump-report',root/'link.json']
            for slot in range(1,5):
                folder=root/('player'+str(slot));folder.mkdir(exist_ok=True)
                windows=','.join(f'r{n}:{0xC600+n}:16' for n in range(0,160,16))
                # CLI runner slots are zero-based; the library exposes players 1..4.
                cmd+=['--link-session',f'name=player{slot}|slot={slot-1}|rom={rom}|save_state={folder / "final.kqs"}|watch_window={windows}']
            command(cmd,root,'link.txt',240);linked=json.loads((root/'link.json').read_text(encoding='utf-8'));links.append({'mode':mode,'lesson':lesson,'summary':linked['runner_summary']})
            linked={'runner_summary':linked['runner_summary'],'sessions':[{'slot':r['slot'],'report':{'watched_memory':r['report']['watched_memory']}} for r in linked['sessions']]}
            (root/'link.json').write_text(json.dumps(linked,indent=2),encoding='utf-8')
        for slot in range(1,count+1):
            folder=root/('player'+str(slot));folder.mkdir(exist_ok=True);png=folder/'screen.png';report=folder/'runtime.json'
            cmd=[emu,rom,'--hardware',mode,'--run-frames','2' if count==4 else '90','--png',png,'--dump-report',report,'--report-sections','meta,cpu,watched_memory','--watch-fields','preview']
            if count==4:cmd+=['--load-state',folder/'final.kqs']
            for n in range(0,160,16):cmd+=['--watch-window',f'r{n}:{0xC600+n}:16']
            command(cmd,folder,'capture.txt');actual=values(json.loads(report.read_text(encoding='utf-8')));want=expectation(lesson,slot);expected=want+[0]*(79-len(want))+[0xA55A]
            labels=LABELS[lesson]+[[13,y,str(expected[i]).zfill(5)] for y,i in DISPLAY[lesson]];pixels=check_pixels(png,labels,'gb');wire=values(linked['sessions'][slot-1]['report']) if count==4 else actual
            row={'platform':'gb','mode':mode,'lesson':lesson,'slot':slot,'source':source.relative_to(SITE).as_posix(),'source_sha256':sha(source),'rom':rom.relative_to(SITE).as_posix(),'rom_sha256':sha(rom),'image':png.relative_to(SITE).as_posix(),'image_sha256':sha(png),'compiler_sha256':sha(compiler),'emulator_sha256':sha(emu),'input_sha256':dependencies(source,lib),'actual':actual,'expected':expected,'linked_actual':wire,'pixel_mismatches':pixels,'passed':actual==wire==expected and pixels==0}
            w,h,ch,pixels_rgb=read_png(png);colored=sum(1 for scan in pixels_rgb for x in range(0,w*ch,ch) if len(set(scan[x:x+3]))>1);row['colored_pixels']=colored;row['passed'] &= colored>0 if mode=='cgb' else colored==0
            records.append(row);print(mode,lesson,slot,'PASS' if row['passed'] else 'FAIL',[(i,a,b) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b][:12],'pixels',pixels,flush=True)
            # Delete only an already captured, verified snapshot in this exact case folder.
            state=folder/'final.kqs'
            if row['passed'] and state.exists():
                assert state.resolve().is_relative_to(OUT.resolve()) and not state.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT
                deleted.append({'path':state.relative_to(SITE).as_posix(),'bytes':state.stat().st_size,'sha256':sha(state)});state.unlink()
        cleanup_build_outputs(root)
        data={'records':records,'links':links,'script_sha256':sha(Path(__file__)),'discarded_verified_snapshots':deleted}
        (OUT/'partial_results.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    path=OUT/(('-'.join(x for x in [args.mode,args.lesson] if x)+'-results.json') if args.mode or args.lesson else 'results.json');path.write_text(json.dumps(data,indent=2),encoding='utf-8')
    raise SystemExit(0 if all(r['passed'] for r in records) else 1)
if __name__=='__main__':main()
