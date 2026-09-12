"""Exercise documented CLI workflows on the original manual ROMs."""
from collect import ROOT,SITE,WORK,TOOLS
import subprocess,json,shutil,wave,math,array
D=SITE/'verification';W=WORK/'workflow';W.mkdir(exist_ok=True)
records=[]
def run(name,key,args,ok=(0,)):
 p=subprocess.run([str(TOOLS[key]),*map(str,args)],cwd=W,capture_output=True,timeout=120)
 text=(p.stdout+p.stderr).decode('utf-8',errors='replace').replace(str(ROOT),'[WORKSPACE]')
 (D/(name+'.txt')).write_text(text[:18000],encoding='utf-8')
 records.append({'id':name,'tool':key,'arguments':[str(x).replace(str(ROOT),'[WORKSPACE]') for x in args],'exit_code':p.returncode,'expected_exit_codes':list(ok),'status':'passed' if p.returncode in ok else 'failed'})
 (D/'workflow.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
 print(name,p.returncode,flush=True)
 return p.returncode
def main():
 for p in ['gb','fc']:
  dst=SITE/'samples/sarakura'/p;dst.mkdir(parents=True,exist_ok=True)
  metadata=ROOT/'sarakura/examples'/p/('kitaqgb_build_metadata.json' if p=='gb' else 'kitaqfc_build_metadata.json')
  events=ROOT/'sarakura/examples'/p/('kokura_diagnostic_events.jsonl' if p=='gb' else 'kurosaki_diagnostic_events.jsonl')
  shutil.copyfile(metadata,dst/'build.json')
  lines=[]
  for line in events.read_text(encoding='utf-8-sig').splitlines():
   e=json.loads(line);e.pop('snapshot_ref',None);e.pop('trace_window_ref',None);lines.append(json.dumps(e,ensure_ascii=False))
  (dst/'events.jsonl').write_text('\n'.join(lines)+'\n',encoding='utf-8')
  out=W/('synthetic-'+p)
  run('sarakura-'+p+'-synthetic','sarakura',[p,'analyze','--metadata',dst/'build.json','--events',dst/'events.jsonl','--out',out,'--fail-on','never','--no-repro-bundle'])
  shutil.copyfile(out/'report.html',D/('sarakura-'+p+'-synthetic.html'))
  run('sarakura-'+p+'-validate','sarakura',['validate',out/'ai_diagnostics.json','--strict'])
  run('sarakura-'+p+'-ci','sarakura',['ci-summary','--diagnostics',out,'--fail-on','error','--enforce'],ok=(1,))
  run('sarakura-'+p+'-real','sarakura',[p,'analyze','--metadata',WORK/(p+'_hello')/'build.json','--events',WORK/(p+'_hello')/('diag' if p=='gb' else 'events.jsonl'),'--out',W/('real-'+p),'--fail-on','never','--no-repro-bundle'])
 rom=WORK/'fc_hello/program.nes'
 run('kurosaki-inspect','kurosaki',['inspect-rom',rom,'--json',W/'rom.json'])
 run('kurosaki-disasm','kurosaki',['disasm',rom,'--bytes','64','--text',W/'reset.txt'])
 run('kurosaki-decompile','kurosaki',['decompile',rom,'--max-instructions','64','--format','markdown','--out',W/'decompile.md'])
 run('kurosaki-trace','kurosaki',['trace',rom,'--frames','2','--cpu','--out',W/'trace.jsonl'])
 run('kurosaki-snapshot-save','kurosaki',['snapshot-save',rom,'--frames','60','--out',W/'state.json'])
 run('kurosaki-snapshot-load','kurosaki',['snapshot-load',W/'state.json','--json',W/'loaded.json'])
 run('kurosaki-snapshot-resume','kurosaki',['snapshot-resume',rom,W/'state.json','--frames','2','--json',W/'resumed.json'])
 run('kurosaki-replay-record','kurosaki',['replay-record',rom,'--frames','60','--out',W/'replay.json'])
 run('kurosaki-replay-run','kurosaki',['replay-run',rom,W/'replay.json','--verify','--json',W/'replay-result.json'])
 run('kurosaki-mapper-test','kurosaki',['mapper-test',rom,'--json',W/'mapper-test.json'])
 run('kurosaki-pad','kurosaki',['run',WORK/'fc_input/program.nes','--frames','120','--pad1','1','--png',D/'fc_input_pressed.png','--json',W/'pad.json'])
 run('kokura-pad','kokura',[WORK/'gb_input/program.gb','--run-frames','120','--input-script','NONE:30;A:2;NONE:88','--png',D/'gb_input_pressed.png','--dump-report',W/'gb-pad.json'])
 run('kurosaki-audio','kurosaki',['audio-export',WORK/'fc_sound/program.nes','--frames','120','--wav',W/'fc-audio.wav','--json',W/'fc-audio.json'])
 for p,path in [('gb',WORK/'gb_sound/audio.wav'),('fc',W/'fc-audio.wav')]:
  with wave.open(str(path),'rb') as wav:
   assert wav.getsampwidth()==2
   samples=array.array('h',wav.readframes(wav.getnframes()))
   peak=max(abs(s) for s in samples);rms=math.sqrt(sum(s*s for s in samples)/len(samples))
   rec={'id':p+'-audio-pcm','frames':wav.getnframes(),'sample_rate':wav.getframerate(),'channels':wav.getnchannels(),'peak':peak,'rms':round(rms,3),'nonzero_samples':sum(s!=0 for s in samples),'status':'passed' if peak>0 else 'failed','scope':'PCM generated and non-silent; no subjective timbre or hardware claim'}
   records.append(rec)
 (D/'workflow.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
