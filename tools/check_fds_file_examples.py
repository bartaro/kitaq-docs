"""Verify the FDS save-buffer lesson with original CPU ABI fixture code.

The fixture models memory transfers and a save slot, not a physical disk/BIOS.
"""
from pathlib import Path
import hashlib,json,os,subprocess,sys
from check_api_tile_examples import read_png
from check_batch200 import dependencies
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.is_dir():REPOS=SITE.parent
sys.path.insert(0,str(REPOS/'kitaqfc/scripts'))
from fds_abi_fixture import disk_files
from fds_fileio_fixture import fileio_firmware
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
OUT=SITE/'verification/api-fds-file/example';OUT.mkdir(parents=True,exist_ok=True)
compiler=Path(os.environ.get('KITAQFC_TEST_COMPILER',str(REPOS/'kitaqfc/kitaqfc.exe')))
emulator=REPOS/'kurosaki/kurosaki.exe';lib=REPOS/'kitaqfc/lib'
fontpath=SITE/'samples/font.chr';font=fontpath.read_bytes();records=[]
source=SITE/'samples/api-examples/fc/fds_file_io.c';manifest=source.with_name('fds_file_io_manifest.json');payload=source.with_name('fds_file_io_payload.bin')
labels=[(2,2,'FDS LOAD / SAVE BUFFER'),(2,5,'LOAD TO 8500 STATUS'),(25,5,'000'),(2,7,'INITIAL FIRST/LAST'),(21,7,'011'),(25,7,'044'),(2,9,'SAVE FILE 73 STATUS'),(25,9,'000'),(2,11,'RELOAD TO 8600 STATUS'),(25,11,'000'),(2,13,'SAVED FIRST / LAST'),(21,13,'007'),(25,13,'028'),(2,15,'BYTE CHECK ERRORS'),(25,15,'000'),(2,18,'STAGING 8000 / SIZE 4')]
pixels=set()
for tx,ty,label in labels:
 for n,c in enumerate(label):
  for y in range(8):
   bits=font[ord(c)*16+y]|font[ord(c)*16+y+8]
   for x in range(8):
    if bits & (128>>x):pixels.add(((tx+n)*8+x,ty*8+y))
for variant,flags in [('default',[]),('unoptimized',['-O0'])]:
 folder=OUT/variant;folder.mkdir(exist_ok=True);rom=folder/'example.fds';image=folder/'screen.png';statepath=folder/'state.json';fixture=folder/'fileio-fixture.bin'
 cmd=[str(compiler),str(source),'-I',str(lib),'-I',str(SITE/'samples'),'-o',str(rom),'--mapper=fds','--fds-layout=fds32','--fds-no-license-bypass','--fds-meta='+str(manifest),'--nes-chr='+str(fontpath),'--no-cache','--no-disasm']+flags
 inputs=dependencies(source,lib)
 for path in [fontpath,manifest,payload]:inputs[path.relative_to(SITE).as_posix()]=sha(path)
 for name in ['fds_abi_fixture.py','fds_fileio_fixture.py']:inputs['kitaqfc/scripts/'+name]=sha(REPOS/'kitaqfc/scripts'/name)
 p=subprocess.run(cmd,capture_output=True,cwd=folder,timeout=90)
 if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace')[-4000:])
 file=next(f for f in disk_files(rom) if f['id']==73);assert file['ordinal']==3 and file['number']==200
 fixture.write_bytes(fileio_firmware(file))
 p=subprocess.run([str(emulator),'run',str(rom),'--frames','120','--snapshot',str(statepath),'--png',str(image)],capture_output=True,cwd=folder,env={**os.environ,'KUROSAKI_DISKSYS_ROM':str(fixture)},timeout=90)
 if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace')[-2000:])
 ram=json.loads(statepath.read_text())['bus']['ram'];actual=ram[0x600:0x608]+[ram[0x60f],ram[0x700],ram[0x701],ram[0x704]];expected=[0,11,44,0,0,7,28,0,165,2,3,1]
 w,h,ch,rows=read_png(image);assert (w,h)==(256,240)
 bad=[(x,y) for y in range(h) for x in range(w) if (sum(rows[y][x*ch:x*ch+3])>384)!=((x,y) in pixels)]
 row=dict(platform='fc',mode=variant,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),input_sha256=inputs,fixture_sha256=sha(fixture),actual=actual,expected=expected,pixel_mismatches=len(bad),passed=actual==expected and not bad)
 records.append(row);print(variant,'PASS' if row['passed'] else 'FAIL',actual,'pixels',len(bad),flush=True)
 (OUT/'results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),records=records),indent=2))
 if row['passed']:statepath.unlink();fixture.unlink();cleanup_build_outputs(folder)
raise SystemExit(0 if all(r['passed'] for r in records) else 1)
