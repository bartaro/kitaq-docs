from pathlib import Path
import argparse,json,subprocess,hashlib,time
from datetime import datetime, timezone
from collect import ROOT,SITE,WORK,TOOLS
def main():
 # Write fresh checks separately so historical logs/screenshots retain their provenance.
 ap=argparse.ArgumentParser();ap.add_argument('--only',default='');ap.add_argument('--runtime',action='store_true')
 ap.add_argument('--output',type=Path,default=SITE/'verification/current');args=ap.parse_args()
 dest=args.output.resolve();dest.mkdir(parents=True,exist_ok=True)
 results_path=dest/'samples.json'
 previous=json.loads(results_path.read_text(encoding='utf-8')) if results_path.exists() else []
 results={r['id']:r for r in previous} if args.only else {}
 manifest=json.loads((SITE/'samples/manifest.json').read_text(encoding='utf-8'))
 selected=set(args.only.split(',')) if args.only else {row['id'] for row in manifest}
 unknown=selected-{row['id'] for row in manifest}
 if unknown:ap.error('Unknown sample IDs: '+', '.join(sorted(unknown)))
 for item in manifest:
  ident=item['id']
  if args.only and ident not in args.only.split(','): continue
  p=item['platform'];out=WORK/'verification-current'/ident;out.mkdir(parents=True,exist_ok=True)
  lib=ROOT/('kitaqgb/lib' if p=='gb' else 'kitaqfc/lib')
  rom=out/('program.gb' if p=='gb' else 'program.nes')
  # A stale ROM cannot stand in for a missing output of this compilation.
  if rom.exists():rom.unlink()
  inputs=[SITE/'samples'/item['file'],SITE/'samples'/(p+'_common.h'),SITE/'samples/font_gb.h',SITE/'samples/font.chr',
          *sorted(path for path in lib.iterdir() if path.suffix in ('.c','.h','.inc'))]
  source_hashes={path.relative_to(ROOT).as_posix():hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs}
  compiler=TOOLS['kitaq'+p];emulator=TOOLS['kokura' if p=='gb' else 'kurosaki']
  argv=[str(TOOLS['kitaqgb' if p=='gb' else 'kitaqfc']),*[str(lib/f) for f in item['libs']],str(SITE/'samples'/item['file']),'-I',str(lib),'-I',str(SITE/'samples'),'-o',str(rom),'--no-disasm',*item['options']]
  if p=='gb':argv+=['--profile=dev','--rst-disable','--stack-bank=fixed','--emit-ai-metadata='+str(out/'build.json')]
  else:argv+=['--mapper=nrom','--nes-chr='+str(SITE/'samples/font.chr'),'--kurosaki-metadata='+str(out/'debug.json'),'--emit-ai-metadata='+str(out/'build.json')]
  start=time.time()
  try:
   proc=subprocess.run(argv,cwd=out,capture_output=True,timeout=90)
   txt=(proc.stdout+proc.stderr).decode('utf-8',errors='replace').replace(str(ROOT),'[WORKSPACE]')
   (dest/(ident+'-build.txt')).write_text(txt,encoding='utf-8')
   rec={'id':ident,'checked_at':datetime.now(timezone.utc).isoformat(),'build_exit':proc.returncode,'build_seconds':round(time.time()-start,2),'runtime':'not run','expected':item['expected'],
        'source_sha256':source_hashes,'compiler_sha256':hashlib.sha256(compiler.read_bytes()).hexdigest(),
        'build_argv':[arg.replace(str(ROOT),'[WORKSPACE]') for arg in argv]}
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
     rec['emulator_sha256']=hashlib.sha256(emulator.read_bytes()).hexdigest()
     rec['runtime_argv']=[arg.replace(str(ROOT),'[WORKSPACE]') for arg in run]
   elif proc.returncode==0:
    rec['build_exit']=1;rec['error']='Compiler returned success without creating the ROM.'
   results[ident]=rec
   print(ident,rec['build_exit'],rec['runtime'],flush=True)
  except subprocess.TimeoutExpired:
   results[ident]={'id':ident,'build_exit':None,'runtime':'timeout'};print(ident,'TIMEOUT',flush=True)
  results_path.write_text(json.dumps(list(results.values()),ensure_ascii=False,indent=2),encoding='utf-8')
 # Propagate failures to automation even when other samples succeeded.
 if any(results[key].get('build_exit')!=0 or (args.runtime and results[key].get('runtime')!='executed') for key in selected):
  raise SystemExit(1)
if __name__=='__main__':main()
