"""Create a static GitHub-ready bundle without build products or Python caches."""
from pathlib import Path
import zipfile,hashlib,json
S=Path(__file__).resolve().parents[1]
out=S.parent/'kitaq_manuals_ja_en_20260913.zip'
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(S.rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(S)
  if '.git' in rel.parts:continue
  if '__pycache__' in rel.parts or p.suffix.lower() in ('.pyc','.exe','.pdb','.dll','.gb','.gbc','.nes','.fds','.rom','.sav','.srm','.kqs','.wav'):continue
  if rel.parts[:2] in [('samples','out'),('samples','sarakura-out')]:continue
  z.write(p,rel.as_posix())
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 assert all(n in z.namelist() for n in ['index.html','.nojekyll','samples/assets/ascii.c','README.md','reference/compiler-fixes.patch'])
 assert len([n for n in z.namelist() if '/' not in n and n.endswith('.html')])==9
 assert len([n for n in z.namelist() if n.startswith('en/') and n.endswith('.html')])==9
 count=len(z.namelist())
sha=hashlib.sha256(out.read_bytes()).hexdigest()
out.with_suffix('.zip.sha256').write_text(sha+'  '+out.name+'\n',encoding='ascii')
print(json.dumps({'zip':str(out),'files':count,'bytes':out.stat().st_size,'sha256':sha}))
