"""Source-backed reference inventory. No network or third-party Python packages."""
from pathlib import Path
import re, json, html
from collect import ROOT,SITE,read

def clean(t):
 return re.sub(r'/\*.*?\*/|//[^\n]*',lambda m: re.sub(r'[^\n]',' ',m[0]),t,flags=re.S)
DECL=re.compile(r'(?m)^[ \t]*((?:(?:[A-Za-z_]\w*)[ \t*]+)+)([A-Za-z_]\w*)[ \t]*\(([^;{}]*)\)\s*(;|\{)')
def definitions(p):
 t=read(p);ct=clean(t);out=[]
 for m in DECL.finditer(ct):
  ret,name,args,end=m.groups()
  if ret.strip().startswith(('return','typedef','if','else','while','for')):continue
  pos=m.start();line=t.count('\n',0,pos)+1
  proto=re.sub(r'\s+',' ',t[m.start():m.end()]).strip().rstrip(';{').strip()
  before=t[max(0,pos-1600):pos]
  comment=re.search(r'((?:(?://[^\n]*\n)|(?:/\*.*?\*/\s*))+)[ \t\n]*$',before,re.S)
  desc=comment[1] if comment else ''
  desc=re.sub(r'^\s*// ?|/\*|\*/|^\s*\* ?','',desc,flags=re.M).strip()
  body=''
  if end=='{':
   depth=1;i=m.end()
   while i<len(ct) and depth:
    if ct[i]=='{':depth+=1
    if ct[i]=='}':depth-=1
    i+=1
   body=t[m.start():i]
  out.append(dict(name=name,ret=ret.strip(),args=re.sub(r'\s+',' ',args).strip(),signature=proto+';',path=p.relative_to(ROOT).as_posix(),line=line,comment=desc[-1800:],body=body,kind='function'))
 return out
def collect(platform):
 lib=ROOT/('kitaqgb/lib' if platform=='gb' else 'kitaqfc/lib')
 comp=ROOT/('kitaqgb' if platform=='gb' else 'kitaqfc')
 headers=list(sorted(lib.glob('*.h')))
 impl={}
 for f in [*lib.glob('*.c'),*headers]:
  for r in definitions(f):
   if r['body']:impl.setdefault(r['name'],r)
 records={}
 for f in headers:
  text=read(f)
  for r in definitions(f):
   if r['name'] in records:continue
   r['module']=f.stem
   r['definition']=impl.get(r['name'])
   r['availability']='compiler' if r['name'].startswith('__') else ('implementation' if r['definition'] else 'declaration')
   records[r['name']]=r
  # Function-like macros, including multiline macro bodies.
  for m in re.finditer(r'(?m)^#define[ \t]+(\w+)\(([^\n)]*)\)[ \t]*([^\n]*(?:\\\n[^\n]*)*)',text):
   name,args,body=m.groups()
   if name in records:continue
   records[name]=dict(name=name,ret='macro',args=args,signature=m[0],path=f.relative_to(ROOT).as_posix(),line=text.count('\n',0,m.start())+1,comment='',body='',kind='macro',module=f.stem,definition=None,availability='macro')
 source=read(comp/'CodeGenerator.cs')
 if platform=='gb':
  names=set(re.findall(r'funcName\s*==\s*"(__\w+)"',source))
 else:
  names={n for n in records if n.startswith('__')}
 for name in names:
  if name in records:continue
  records[name]=dict(name=name,ret='',args='',signature='',path=(comp/'CodeGenerator.cs').relative_to(ROOT).as_posix(),line=source[:source.find('"'+name+'"')].count('\n')+1,comment='',body='',kind='intrinsic',module='intrinsics',definition=None,availability='compiler')
 # Prefer original manual programs, then small repository examples and regression fixtures.
 candidates=list((SITE/'samples').glob(platform+'_*.c'))
 if platform=='gb':
  candidates+=list((ROOT/'examples').glob('*.c'))+list((ROOT/'tests/fixtures').glob('*.c'))+list((ROOT/'examples/beginner_samples').glob('*.c'))
 else:candidates+=list(comp.glob('*smoke.c'))+list((comp/'tests').rglob('*.c'))
 candidates+=list(lib.glob('*.c'))
 candidates=list(dict.fromkeys(candidates))
 texts=[]
 for f in candidates:
  t=read(f)
  if len(t)>250000:continue
  texts.append((f,t,clean(t)))
 for r in records.values():
  name=r['name'];examples=[]
  for f,t,ct in texts:
   pat=re.compile(r'\b'+re.escape(name)+r'\s*\(')
   for m in pat.finditer(ct):
    start=t.rfind('\n',0,m.start())+1
    prefix=ct[start:m.start()].strip()
    # Exclude a declaration/definition rather than falsely presenting it as a call.
    if re.match(r'^(?:(?:static|extern|inline|void|u8|u16|s8|s16|unsigned|char|short|int|const|__stackcall|[A-Z]\w*)\s+|\*)+$',prefix):continue
    line=t.count('\n',0,m.start())+1
    lines=t.splitlines();excerpt='\n'.join(lines[max(0,line-3):min(len(lines),line+4)])
    examples.append(dict(path=f.relative_to(ROOT).as_posix(),line=line,code=excerpt))
    break
   if examples:break
  r['example']=examples[0] if examples else None
  # Prototypes for GB intrinsics can be declared in their actual source call sites.
  if not r['signature']:
   for f,t,ct in texts:
    ds=[d for d in definitions(f) if d['name']==name and not d['body']]
    if ds:
     r.update({k:ds[0][k] for k in ('signature','ret','args')});break
  if not r['signature']:
   match=re.search(r'if\s*\([^\n]*funcName\s*==\s*"'+re.escape(name)+r'"[^\n]*\)',source)
   block=source[match.end():match.end()+1600] if match else ''
   cnt=re.search(r'args\.Length\s*!=\s*(\d+)',block)
   if cnt:
    r['args']=', '.join('arg'+str(i) for i in range(int(cnt[1])))
    r['signature']=name+'('+r['args']+');'
    r['arity_only']=True
   else:r['signature']=name+'(/* 書式は実装と呼び出し例を参照 */);';r['arity_only']=True
   r['implementation_excerpt']=block[:1600]
  # Every exposed callable gets a usage fragment, including APIs without a repository caller.
  if not r['example'] and r['args'] not in ('','void'):
   if r['kind']=='macro':args=[s.strip() for s in r['args'].split(',')]
   else:
    args=[]
    for a in r['args'].split(','):
     m=re.search(r'(\w+)\s*(?:\[[^]]*\])?$',a.strip());args.append(m[1] if m else 'value')
   if not r.get('arity_only') and r['kind']!='macro':
    ret=re.sub(r'\b(?:extern|static|inline|__stackcall)\b','',r['ret']).strip()
    code=ret+' example_'+name.lstrip('_')+'('+r['args']+') {\n    '+('' if ret=='void' else 'return ')+name+'('+', '.join(args)+');\n}'
   else:code=name+'('+', '.join(args)+');'
   r['new_example']=code
  elif not r['example']:r['new_example']=name+'();'
 data={'platform':platform,'headers':[p.relative_to(ROOT).as_posix() for p in headers],'records':list(records.values())}
 (SITE/'reference'/(platform+'-api.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 print(platform,'records',len(records),'callsites',sum(bool(r['example']) for r in records.values()),'declaration_only',sum(r['availability']=='declaration' for r in records.values()))
 return data
if __name__=='__main__':
 collect('gb');collect('fc')
