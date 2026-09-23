"""Verify the FC far-copy alias using byte checks and colored copied tile shapes."""
from pathlib import Path
import hashlib,json,subprocess
from check_api_tile_examples import read_png
from check_entity_callbacks import check_pixels
from api_vram_colors import matches_color
SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUTPUT=SITE/'verification/api-far-copy-alias'
SOURCE='samples/api-examples/fc/far_copy_alias.c'
SUPPORT=['samples/asset_example_checks.h','samples/asset_example_data_fc.h','samples/font_gb.h','samples/fc_common.h']
LIBRARIES=['asset.c','asset.h','bank.c','bank.h','core.h','intrinsics.h','runtime.h']
VARIANTS=[('default',[]),('O0',['-O0']),('no-inline',['--no-small-inline']),('fastcall',['--fastcall-v2'])]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 source=SITE/SOURCE;compiler=REPOS/'kitaqfc/kitaqfc.exe';emulator=REPOS/'kurosaki/kurosaki.exe'
 bindings={SOURCE:sha(source),**{n:sha(SITE/n) for n in SUPPORT}}
 library={n:sha(REPOS/'kitaqfc/lib'/n) for n in LIBRARIES}
 tools={'compiler_sha256':sha(compiler),'emulator_sha256':sha(emulator),
        'compiler_source_sha256':sha(REPOS/'kitaqfc/kitaqfc/CodeGenerator.cs'),
        'checker_sha256':sha(Path(__file__))}
 rows=[]
 for variant,flags in VARIANTS:
  folder=OUTPUT/variant;folder.mkdir(parents=True,exist_ok=True)
  rom=folder/'example.nes';png=folder/'screen.png';state=folder/'runtime.json'
  command=[str(compiler),str(source),'-I',str(REPOS/'kitaqfc/lib'),'-I',str(SITE/'samples'),'-o',str(rom),'--mapper=mmc1','--board=surom512','--no-cache','--no-disasm',*flags]
  result=subprocess.run(command,cwd=folder,capture_output=True,timeout=120)
  assert result.returncode==0,(result.stdout+result.stderr).decode(errors='replace')
  result=subprocess.run([str(emulator),'run',str(rom),'--frames','300','--png',str(png),'--json',str(state)],cwd=folder,capture_output=True,timeout=120)
  assert result.returncode==0
  labels=[(1,0,'ASSET BANKS'),(1,3,'TILE ASSET 144B'),(6,8,'FARMEMCPY'),(6,12,'LOAD RAW'),(1,15,'FAILED CHECKS'),(20,15,'000'),(1,17,'FIRST FAILURE'),(20,17,'00')]
  errors=check_pixels(png,labels,'fc')
  width,height,channels,pixels=read_png(png);assert (width,height)==(256,240)
  background=pixels[-1][:3];shapes=colors=0
  masks=[[128,192,224,240,248,252,254,255],[255,129,129,129,129,129,129,255],[240]*8]
  for top,count,color in [(32,9,'red'),(64,2,'blue'),(96,2,'green')]:
   for y in range(top,top+8):
    for x in range(16,16+count*8):
     ink=bool(masks[((x-16)//8)%3][y-top]&(1<<(7-x%8)))
     pixel=pixels[y][x*channels:x*channels+3]
     shapes+=ink!=(pixel!=background)
     if ink:colors+=not matches_color(pixel,color)
  frames=json.loads(state.read_text())['frames']
  row=dict(variant=variant,mode='surom512',platform='fc',source=SOURCE,
      rom=rom.relative_to(SITE).as_posix(),image=png.relative_to(SITE).as_posix(),
      frames=frames,label_pixel_mismatches=errors,geometry_pixel_mismatches=shapes,
      geometry_color_mismatches=colors,geometry_pixels_checked=832,
      passed=frames==300 and errors==0 and shapes==0 and colors==0,
      source_sha256=sha(source),rom_sha256=sha(rom),image_sha256=sha(png))
  rows.append(row)
  assert all(sha(SITE/n)==h for n,h in bindings.items())
  assert all(sha(REPOS/'kitaqfc/lib'/n)==h for n,h in library.items())
  report=dict(records=rows,passed=all(r['passed'] for r in rows),support_sha256=bindings,
              library_sha256=library,**tools)
  (OUTPUT/'results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
  print(variant,'PASS' if row['passed'] else 'FAIL',flush=True)
  assert row['passed'];state.unlink()

if __name__=='__main__':main()
