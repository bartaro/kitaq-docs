"""Bind eight IRQ/NMI intrinsics to exact compiler dispatch/helpers and executed color samples."""
from pathlib import Path
import hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sys.path.insert(0,str(SITE/'tools'));import catalog;catalog.ROOT=REPOS
header=REPOS/'kitaqfc/lib/intrinsics.h';compiler=REPOS/'kitaqfc/kitaqfc/CodeGenerator.cs';source=compiler.read_text(encoding='utf-8')
declarations={r['name']:r for r in catalog.definitions(header)}
p=SITE/'reference/fc-api.json';data=json.loads(p.read_text(encoding='utf-8'));records={r['name']:r for r in data['records']}
shared=''

rows={
 '__nmi_enable':('ni_enable',[],'none',['ni_nmi_timing']),
 '__nmi_disable':('ni_disable',[],'none',['ni_nmi_timing']),
 '__nmi_wait':('ni_wait',[],'none',['ni_handler']),
 '__nmi_ready':('ni_ready',[],'ni_counter_byte',['ni_handler']),
 '__irq_disable':('ni_irq_disable',[],'none',['ni_irq_scope']),
 '__irq_enable':('ni_irq_enable',[],'none',['ni_irq_scope']),
 '__irq_save':('ni_save',[],'ni_status_byte',['ni_irq_scope']),
 '__irq_restore':('ni_restore',[('state','ni_status_byte')],'none',['ni_irq_scope'])}
helpers={'__nmi_wait':'EmitHelperNmiWait'}
masked=catalog.clean(source)
def method(name):
 match=re.search(r'(?m)^ *void '+name+r'\([^\n]*\)\s*\{',masked);assert match,name
 depth=1;i=match.end()
 while depth:
  if masked[i]=='{':depth+=1
  elif masked[i]=='}':depth-=1
  i+=1
 return source[match.start():i].strip(),source.count('\n',0,match.start())+1
contracts={};evidence={}
for name,(purpose,args,returns,notes) in rows.items():
 record=records[name]
 for key in ['ret','args','signature','path','line','comment','body']:record[key]=declarations[name][key]
 match=re.search(r'case "'+name+r'":.*?(?=\n *case ")',source,re.S);assert match,name
 excerpt=match[0].strip();line=source.count('\n',0,match.start())+1
 if name in helpers:
  body,helper_line=method(helpers[name]);excerpt+='\n\n'+body
  if name.startswith('__palette_'):
   call=next(t.strip() for t in source.splitlines() if 'EmitHelperPalette("'+name+'"' in t);excerpt+='\n\n'+call
 if name in ['__nmi_wait','__nmi_ready']:
  a=source.index('            // The default NMI executes')
  b=source.index('            if (!_functions.ContainsKey("__nes_irq"))',a)
  excerpt+='\n\n'+source[a:b].strip()
 record['arity_only']=False
 record['definition']=None
 record['implementation_source']={'path':compiler.relative_to(REPOS).as_posix(),'line':line}
 record['implementation_excerpt']=excerpt
 fingerprint=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
 program='samples/api-examples/fc/interrupt_intrinsics.c'
 text=shared+'\n'+(SITE/program).read_text(encoding='utf-8')
 match=re.search(r'// example:'+name+r':start\s*\n(.*?)\s*// example:'+name+r':end',text,re.S);assert match,name
 snippet='\n'.join(line.strip() for line in match[1].splitlines())
 build='New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqfc\\kitaqfc.exe .\\kitaq-docs\\'+program.replace('/','\\')+' -I .\\kitaqfc\\lib -I .\\kitaq-docs\\samples --nes-chr=.\\kitaq-docs\\samples\\font.chr -o .\\out\\'+Path(program).stem+'.nes --no-cache --no-disasm'
 contracts['fc:'+name]={'review':'interrupt-intrinsics-source-20260915','purpose':[purpose],'args':[[arg,[key]] for arg,key in args],'returns':[returns],'notes':notes,'record_sha256':fingerprint,'example':{'program':program,'code':snippet,'build':build,'expected':['ni_demo_irq','ni_demo_nmi']}}
 contracts['fc:'+name]['references']=[{'title':'NESdev: NMI','url':'https://www.nesdev.org/wiki/NMI'},{'title':'NESdev: CPU interrupts','url':'https://www.nesdev.org/wiki/Interrupts'}]
 evidence[name]={'record_sha256':fingerprint,'header_line':record['line']}
(HERE/'interrupt_intrinsic_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'interrupt_intrinsic_review_sources.json').write_text(json.dumps({'source_sha256':{p.relative_to(REPOS).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [header,compiler,REPOS/'kitaqfc/kitaqfc/Lowerer.cs']},'records':evidence},indent=2),encoding='utf-8')
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');print('8 IRQ/NMI intrinsic contracts bound to compiler source and the executed scene.')
