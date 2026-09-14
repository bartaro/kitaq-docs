"""Source-backed reference inventory. No network or third-party Python packages."""
from pathlib import Path
import re, json, html
from collect import ROOT,SITE,read

def clean(t):
 # Preserve offsets while masking comments and literals. Braces and function
 # names inside a string are data, not syntax or a real call site.
 return re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|/\*.*?\*/|//[^\n]*',lambda m: re.sub(r'[^\n]',' ',m[0]),t,flags=re.S)
DECL=re.compile(r'(?m)^[ \t]*((?:(?:[A-Za-z_]\w*)[ \t\r\n*]+)+)([A-Za-z_]\w*)[ \t]*\(([^;{}]*)\)\s*(;|\{)')

def declaration_name_offsets(cleaned):
 return {m.start(2) for m in DECL.finditer(cleaned)
         if not m[1].strip().startswith(('return','typedef','if','else','while','for'))}
def renderer_profile(text, height):
 # Mask inactive profile branches without changing source line numbers. Other
 # preprocessor guards remain intact; this is not a general C preprocessor.
 active=True;stack=[];out=[]
 for line in text.splitlines(keepends=True):
  directive=re.match(r'\s*#(if|ifdef|ifndef|else|endif)\b(.*)',line)
  keep=active
  if directive:
   op,expr=directive.groups()
   if op in ('if','ifdef','ifndef'):
    match=re.fullmatch(r'\s*WIRE3D_DMG_HEIGHT\s*==\s*(96|120)\s*',expr) if op=='if' else None
    condition=height==int(match[1]) if match else True
    stack.append((active,bool(match),condition))
    if match:active=active and condition;keep=False
   elif op=='else':
    parent,handled,condition=stack[-1]
    if handled:active=parent and not condition;keep=False
   elif op=='endif':
    parent,handled,condition=stack.pop()
    if handled:keep=False
    active=parent
  out.append(line if keep else '\n' if line.endswith('\n') else '')
 assert not stack
 return ''.join(out)

def definitions(p, height=None):
 t=read(p)
 if p.name in ('wire3d_dmg.c','wire3d_dmg.h'):
  t=renderer_profile(t,120 if height is None else height)
 ct=clean(t);out=[]
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
 comp=ROOT/('kitaqgb/kitaqgb' if platform=='gb' else 'kitaqfc/kitaqfc')
 headers=list(sorted(lib.glob('*.h')))
 impl={}
 for f in [*lib.glob('*.c'),*lib.glob('*.inc'),*headers]:
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
 if platform=='gb':
  # Expose both compile-time contracts, including the 96-line-only APIs. The
  # primary signature is 120-line where available; original notes identify each
  # profile and the implementation excerpt retains the actual conditional code.
  header=lib/'wire3d_dmg.h';body=lib/'wire3d_dmg.c'
  variants={height:{r['name']:r for r in definitions(header,height)} for height in (96,120)}
  bodies={height:{r['name']:r for r in definitions(body,height) if r['body']} for height in (96,120)}
  for name in variants[96].keys() | variants[120].keys():
   heights=[h for h in (96,120) if name in variants[h]]
   selected=120 if 120 in heights else 96
   r=dict(variants[selected][name]);r.update(module='wire3d_dmg',availability='implementation',definition=bodies[selected].get(name))
   r['comment']='\n\n'.join('WIRE3D_DMG_HEIGHT = '+str(h)+'\n'+variants[h][name]['signature']+'\n'+variants[h][name]['comment'] for h in heights)
   r['profiles']=heights
   if len(heights)==2 and r['definition']:
    d=dict(r['definition'])
    d['body']='#if WIRE3D_DMG_HEIGHT == 96\n'+bodies[96][name]['body']+'\n#else\n'+bodies[120][name]['body']+'\n#endif'
    r['definition']=d
   records[name]=r
  # Legacy object-like macros alias real functions. Resolve these explicitly;
  # otherwise a header-only alias would disappear from the source dictionary.
  for stem,height in [('wire3d',96),('dmg3d',120)]:
   p=lib/(stem+'.h');text=read(p)
   for match in re.finditer(r'(?m)^#define\s+(\w+)\s+(Wire3DDMG_\w+)\s*$',text):
    old,new=match.groups()
    if new not in variants[height]:continue
    r=dict(variants[height][new])
    r.update(name=old,signature=r['signature'].replace(new,old),module=stem,path=p.relative_to(ROOT).as_posix(),
             line=text.count('\n',0,match.start())+1,availability='implementation',definition=bodies[height].get(new),
             comment='Compatibility alias: '+new+'; WIRE3D_DMG_HEIGHT = '+str(height)+'.\n'+r['comment'])
    records[old]=r
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
 # Published examples are siblings of lib, not siblings of all six repositories.
 # Using ROOT/examples silently missed the programs shipped with each compiler.
 repo=lib.parent
 candidates+=list((repo/'examples').glob('*.c'))
 if platform=='gb':
  candidates+=list((repo/'tests/fixtures').glob('*.c'))+list((repo/'examples/beginner_samples').glob('*.c'))
 else:candidates+=list(comp.glob('*smoke.c'))+list((comp/'tests').rglob('*.c'))
 candidates+=list(lib.glob('*.c'))+list(lib.glob('*.inc'))
 candidates=list(dict.fromkeys(candidates))
 texts=[]
 for f in candidates:
  t=read(f)
  if len(t)>250000:continue
  ct=clean(t)
  texts.append((f,t,ct,declaration_name_offsets(ct)))
 for r in records.values():
  name=r['name'];examples=[]
  for f,t,ct,declarations in texts:
   pat=re.compile(r'\b'+re.escape(name)+r'\s*\(')
   for m in pat.finditer(ct):
    # Exclude a declaration/definition rather than falsely presenting it as a call.
    if m.start() in declarations:continue
    line=t.count('\n',0,m.start())+1
    lines=t.splitlines();excerpt='\n'.join(lines[max(0,line-3):min(len(lines),line+4)])
    examples.append(dict(path=f.relative_to(ROOT).as_posix(),line=line,code=excerpt))
    break
   if examples:break
  r['example']=examples[0] if examples else None
  # Prototypes for GB intrinsics can be declared in their actual source call sites.
  if not r['signature']:
   for f,t,ct,declarations in texts:
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
