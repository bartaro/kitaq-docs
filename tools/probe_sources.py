from pathlib import Path
import re,json
R=Path(__file__).resolve().parents[3]
for platform,base in [('gb',R/'kitaqgb'),('fc',R/'kitaqfc')]:
 t=(base/'CodeGenerator.cs').read_text(encoding='utf-8-sig')
 names=sorted(set(re.findall(r'(?:funcName|name)\s*==\s*"(__\w+)"',t)))
 print(platform,len(names),' '.join(names))
for d in ['kitaqgb/lib','kitaqfc/lib']:
 print(d)
 for p in (R/d).glob('*.h'):
  t=p.read_text(encoding='utf-8-sig')
  t=re.sub(r'/\*.*?\*/|//[^\n]*','',t,flags=re.S)
  n=re.findall(r'(?m)^\s*(?:extern\s+)?(?:[\w]+[ \t*]+)+([A-Za-z_]\w*)\s*\([^;{}]*\)\s*;',t)
  print(p.name,len(n))
