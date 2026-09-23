"""Run original mapper lessons and check observed bytes and displayed results."""
from pathlib import Path
import argparse, hashlib, json, subprocess
from check_batch200 import dependencies
from check_entity_callbacks import check_pixels
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.is_dir():REPOS=SITE.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--only');opt=ap.parse_args()
out=SITE/'verification/api-mapper/example';out.mkdir(parents=True,exist_ok=True)
chrfile=SITE/'samples/mapper_banks.chr'
data=bytearray(32768);font=(SITE/'samples/font.chr').read_bytes();data[:len(font)]=font
for bank in range(32):data[bank*1024+1023]=17+bank
chrfile.write_bytes(data)
compiler=REPOS/'kitaqfc/kitaqfc.exe';emulator=REPOS/'kurosaki/kurosaki.exe';lib=REPOS/'kitaqfc/lib'
layouts={'mmc1':['AAAA','BBBB','ABAB','AABB'],'mmc3':['ABAB','AABB','ABAB','AABB'],
         'mmc5':['AABB','ABAB','AAAA','BBBB'],'axrom':['AAAA','BBBB','AAAA','BBBB'],
         'fme7':['ABAB','AABB','AAAA','BBBB']}
cases=[('controls','mmc3'),('chr-cnrom','cnrom')]+[('mirroring',m) for m in layouts]
rows=[]
for variant,flags in [('default',[]),('unoptimized',['-O0'])]:
 for family,mapper in cases:
  if opt.only and opt.only not in family:continue
  source=SITE/'samples/api-examples/fc'/('mapper_'+{'controls':'controls','chr-cnrom':'chr_cnrom','mirroring':'mirroring'}[family]+'.c')
  folder=out/(family+'-'+mapper+'-'+variant);folder.mkdir(exist_ok=True)
  rom=folder/'example.nes';image=folder/'screen.png';snapshot=folder/'snapshot.json'
  chrin=SITE/'samples/font.chr' if family=='mirroring' else chrfile
  cmd=[str(compiler),str(source),'-I',str(lib),'-I',str(SITE/'samples'),'-o',str(rom),'--mapper='+mapper,'--nes-chr='+str(chrin),'--no-cache','--no-disasm']+flags
  p=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=90)
  if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace')[-3500:])
  p=subprocess.run([str(emulator),'run',str(rom),'--frames','150','--snapshot',str(snapshot),'--png',str(image)],capture_output=True,cwd=folder,timeout=90)
  if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace')[-2500:])
  state=json.loads(snapshot.read_text());ram=state['bus']['ram']
  if family=='controls':
   expected=[4,19,20,21,22,23,24,17,34,17,34,17,17,34,34,1,2,3,3]
   actual=ram[0x600:0x613];done=ram[0x61F]
   labels=[(1,1,'MMC3 / CHR AND IRQ'),(1,3,'MAPPER'),(24,3,'04'),(1,5,'CHR SET 2'),(20,5,'19'),(24,5,'20'),(1,7,'CHR SET0 4'),(20,7,'21'),(24,7,'22'),(1,9,'CHR SET1 6'),(20,9,'23'),(24,9,'24'),(1,12,'CIRAM: A=17 / B=34'),(1,14,'VERTICAL'),(19,14,'A B A B'),(1,16,'HORIZONTAL'),(19,16,'A A B B'),(1,19,'IRQ COUNTS'),(16,19,'01 02 03 03'),(1,22,'ONE IRQ PER ENABLE'),(1,24,'ACK LEAVES IRQ DISABLED')]
  elif family=='chr-cnrom':
   expected=[33,25,41];actual=ram[0x600:0x603];done=ram[0x60F]
   labels=[(1,1,'CNROM / 8 KIB CHR BANKS'),(1,5,'SET 2 / MARKER'),(24,5,'33'),(1,8,'SET0 1 / MARKER'),(24,8,'25'),(1,11,'SET1 3 / MARKER'),(24,11,'41'),(1,16,'ALL THREE NAMES SELECT'),(1,18,'THE WHOLE PATTERN TABLE')]
  else:
   expected=[{'mmc1':1,'mmc3':4,'mmc5':5,'axrom':7,'fme7':69}[mapper]]+[17 if c=='A' else 34 for pattern in layouts[mapper] for c in pattern]
   actual=ram[0x600:0x611];done=ram[0x61F]
   labels=[(1,1,'NAMETABLE MAPPING'),(1,4,'A=LOW RAM / B=HIGH RAM'),(1,7,'PPU 2000 2400 2800 2C00'),(1,24,'SAME LETTER = SHARED RAM')]
   for i,pattern in enumerate(layouts[mapper]):
    labels.extend([(1,10+i*3,'MODE'),(6,10+i*3,str(i)),(10,10+i*3,'   '.join(pattern))])
  errors=check_pixels(image,labels,'fc')
  inputs=dependencies(source,lib);inputs[chrin.relative_to(SITE).as_posix()]=sha(chrin)
  row=dict(platform='fc',family=family,mode=mapper+'-'+variant,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),input_sha256=inputs,actual=actual,expected=expected,done=done,label_pixel_mismatches=errors,passed=actual==expected and done==165 and errors==0)
  rows.append(row);print(family,mapper,variant,'PASS' if row['passed'] else 'FAIL',actual,'done',done,'pixels',errors,flush=True)
  if row['passed']:snapshot.unlink();cleanup_build_outputs(folder)
  (out/('results.json' if not opt.only else opt.only+'-results.json')).write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),records=rows),indent=2),encoding='utf-8')
raise SystemExit(0 if rows and all(r['passed'] for r in rows) else 1)
