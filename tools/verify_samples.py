from pathlib import Path
import argparse,json,subprocess,hashlib,time
from collect import ROOT,SITE,WORK,TOOLS
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--only',default='');ap.add_argument('--runtime',action='store_true');args=ap.parse_args()
 dest=SITE/'verification';dest.mkdir(exist_ok=True)
 results_path=dest/'samples.json'
 previous=json.loads(results_path.read_text(encoding='utf-8')) if results_path.exists() else []
 results={r['id']:r for r in previous}
 for item in json.loads((SITE/'samples/manifest.json').read_text(encoding='utf-8')):
  ident=item['id']
  if args.only and ident not in args.only.split(','): continue
  p=item['platform'];out=WORK/ident;out.mkdir(exist_ok=True)
  lib=ROOT/('kitaqgb/lib' if p=='gb' else 'kitaqfc/lib')
  rom=out/('program.gb' if p=='gb' else 'program.nes')
  argv=[str(TOOLS['kitaqgb' if p=='gb' else 'kitaqfc']),*[str(kitaqgb/lib/f) for f in item['libs']],str(SITE/'samples'/item['file']),'-I',str(lib),'-I',str(SITE/'samples'),'-o',str(rom),'--no-disasm',*item['options']]
  if p=='gb':argv+=['--profile=dev','--rst-disable','--stack-bank=fixed','--emit-ai-metadata='+str(out/'build.json')]
  else:argv+=['--mapper=nrom','--nes-chr='+str(SITE/'samples/font.chr'),'--kurosaki-metadata='+str(out/'debug.json'),'--emit-ai-metadata='+str(out/'build.json')]
  start=time.time()
  try:
   proc=subprocess.run(argv,cwd=out,capture_output=True,timeout=90)
   txt=(proc.stdout+proc.stderr).decode('utf-8',errors='replace').replace(str(ROOT),'[WORKSPACE]')
   (dest/(ident+'-build.txt')).write_text(txt,encoding='utf-8')
   rec={'id':ident,'build_exit':proc.returncode,'build_seconds':round(time.time()-start,2),'runtime':'not run','expected':item['expected']}
   if proc.returncode==0 and rom.exists():
    rec['rom_sha256']=hashlib.sha256(rom.read_bytes()).hexdigest()
    if args.runtime:
     if p=='gb':run=[str(TOOLS['kokura']),str(rom),'--run-frames','120','--png',str(dest/(ident+'.png')),'--dump-report',str(out/'run.json'),'--emit-diagnostics',str(out/'diag')]
     else:run=[str(TOOLS['kurosaki']),'run',str(rom),'--frames','120','--png',str(dest/(ident+'.png')),'--json',str(out/'run.json'),'--emit-diagnostics',str(out/'events.jsonl')]
     if 'sound' in ident and p=='gb': run+=['--record-wav',str(out/'audio.wav')]
     rp=subprocess.run(run,cwd=out,capture_output=True,timeout=90)
     rt=(rp.stdout+rp.stderr).decode('utf-8',errors='replace').replace(str(ROOT),'[WORKSPACE]')
     (dest/(ident+'-runtime.txt')).write_text(rt,encoding='utf-8')
     rec['runtime']='executed' if rp.returncode==0 else 'failed'
     rec['runtime_exit']=rp.returncode
   results[ident]=rec
   print(ident,rec['build_exit'],rec['runtime'],flush=True)
  except subprocess.TimeoutExpired:
   results[ident]={'id':ident,'build_exit':None,'runtime':'timeout'};print(ident,'TIMEOUT',flush=True)
  results_path.write_text(json.dumps(list(results.values()),ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
