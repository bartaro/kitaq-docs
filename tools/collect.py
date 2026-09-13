"""Refresh the manual's source/CLI inventory. Run from any directory."""
from pathlib import Path
import hashlib, json, re, subprocess

SITE = Path(__file__).resolve().parents[1]
ROOT = SITE.parent
WORK = SITE.parent / '_manual_work'
WORK.mkdir(exist_ok=True)
TOOLS = {
 'kitaqgb': ROOT/'kitaqgb/kitaqgb.exe',
 'kitaqfc': ROOT/'kitaqfc/kitaqfc.exe',
 'kokura': ROOT/'kokura/kokura-cli.exe',
 'kurosaki': ROOT/'kurosaki/kurosaki.exe',
 'sarakura': ROOT/'sarakura/sarakura.exe',
}
for _name, _path in {'kitaqgb': WORK/'gb_compiler/kitaqgb.exe', 'kitaqfc': WORK/'fc_compiler/kitaqfc.exe', 'kurosaki': WORK/'kurosaki_target/debug/kurosaki.exe'}.items():
 if _path.exists(): TOOLS[_name] = _path
def read(p): return p.read_text(encoding='utf-8-sig', errors='replace')
def cli(name, args):
 p=subprocess.run([str(TOOLS[name]),*args], cwd=WORK, capture_output=True, timeout=45)
 return {'argv':args, 'exit_code':p.returncode, 'text':(p.stdout+p.stderr).decode('utf-8',errors='replace').replace(str(ROOT),'[WORKSPACE]')}
def main():
 data={'date':'2026-09-12','tools':{},'sources':[]}
 for name,path in TOOLS.items():
  if not path.exists(): continue
  first=cli(name,['--help'])
  entry={'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'help':[first]}
  if name in ('kurosaki','sarakura'):
   commands=re.search(r'Commands:\s*\n(.*?)(?:\nOptions:|\Z)',first['text'],re.S)
   if commands:
    for cmd in re.findall(r'^  ([a-z][a-z0-9-]+)\s',commands[1],re.M):
     if cmd=='help': continue
     args=[cmd,'--help']; sub=cli(name,args);entry['help'].append(sub)
     nested=re.search(r'Commands:\s*\n(.*?)(?:\nOptions:|\Z)',sub['text'],re.S)
     if nested:
      for subcmd in re.findall(r'^  ([a-z][a-z0-9-]+)\s',nested[1],re.M):
       if subcmd!='help': entry['help'].append(cli(name,[cmd,subcmd,'--help']))
  data['tools'][name]=entry
  print(name, len(entry['help']), len(first['text']))
 for dirname in ('kitaqgb/kitaqgb','kitaqgb/lib','kokura/crates/kokura-cli/src','kitaqfc/kitaqfc','kitaqfc/lib','kurosaki/crates/kurosaki-cli/src','sarakura/crates/sarakura-cli/src','sarakura/catalogs'):
  for path in sorted((ROOT/dirname).iterdir()):
   if path.is_file() and path.suffix in ('.cs','.c','.h','.rs','.json','.md','.toml'):
    data['sources'].append({'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
 (SITE/'reference/inventory.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 for name,entry in data['tools'].items():
  (WORK/(name+'-help.txt')).write_text('\n\n'.join(' '.join(x['argv'])+'\n'+x['text'] for x in entry['help']),encoding='utf-8')
if __name__=='__main__': main()
