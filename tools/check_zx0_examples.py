"""Verify the complete teaching screen, original shapes, labels and colors."""
from pathlib import Path
import hashlib,json,re,subprocess
from check_api_tile_examples import read_png
from api_vram_colors import matches_color
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912';OUT=SITE/'verification/api-zx0';OUT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
labels=[(2,0,'ZX0 ASSET DECODE'),(2,3,'RAM MAP'),(2,7,'AUTO RLE MAP'),(2,11,'VRAM TILES'),(2,16,'CHECKS OK')]
rows=[]
for platform,mode in [('gb','dmg'),('gb','cgb'),('fc','ntsc')]:
 folder=OUT/(platform+'-'+mode);folder.mkdir(exist_ok=True)
 compiler=REPOS/('kitaq'+platform)/('kitaq'+platform+'.exe');emulator=REPOS/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe')
 source=SITE/'samples/api-examples'/platform/'zx0_decode.c';rom=folder/('example.gb' if platform=='gb' else 'example.nes');image=folder/'screen.png'
 cmd=[str(compiler),str(source),'-I',str(compiler.parent/'lib'),'-I',str(SITE/'samples'),'-o',str(rom),'--no-cache','--no-disasm']
 cmd+=['--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb'] if platform=='gb' else ['--mapper=nrom','--nes-chr-ram']
 p=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=120)
 assert p.returncode==0,(p.stdout+p.stderr).decode(errors='replace')[-3000:]
 cmd=[str(emulator),str(rom),'--hardware',mode,'--run-frames','180','--png',str(image)] if platform=='gb' else [str(emulator),'run',str(rom),'--frames','180','--png',str(image)]
 p=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=120);assert p.returncode==0,(p.stdout+p.stderr)[-1000:]
 width,height,channels,pixels=read_png(image);assert (width,height)==((160,144) if platform=='gb' else (256,240))
 def rgb(x,y):return tuple(pixels[y][x*channels:x*channels+3])
 # Swatches also have to match independently specified colors or luminance order.
 colors=[rgb(0,height-1),rgb(16,40),rgb(27,43),rgb(32,40)]
 if mode=='dmg':color_ok=all(sum(colors[i])-sum(colors[i+1])>60 for i in range(3))
 else:color_ok=all(matches_color(c,n) for c,n in zip(colors,['black','white','red','blue']))
 fontpath=SITE/'samples'/('font_gb.h' if platform=='gb' else 'physics_font_fc.h');text=fontpath.read_text(encoding='utf-8');font=bytes(int(n,0) for n in re.findall(r'0x[0-9a-fA-F]+|\d+',text[text.index('{')+1:text.index('}')]))
 tiles=font+(source.parent/'zx0_assets/tiles.bin').read_bytes()
 grid=[[0]*32 for _ in range(32)]
 for x,y,label in labels:
  for offset,ch in enumerate(label):grid[y][x+offset]=ord(ch)
 for n in range(16):grid[5][n+2]=128+n%3;grid[9][n+2]=128;grid[13][n+2]=128+n%3
 mismatch=0
 for y in range(height):
  for x in range(width):
   at=grid[y//8][x//8]*16;line=y%8;bit=7-x%8
   lo=tiles[at+line*(2 if platform=='gb' else 1)];hi=tiles[at+(line*2+1 if platform=='gb' else line+8)]
   ink=((lo>>bit)&1)|(((hi>>bit)&1)<<1)
   mismatch+=rgb(x,y)!=colors[ink]
 support=[fontpath,source.parent/'zx0_assets/tiles.bin',*(source.parent/'zx0_assets').glob('*.h')]
 if platform=='gb':support.append(SITE/'samples/gb_common.h')
 row=dict(platform=platform,mode=mode,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),rom_sha256=sha(rom),image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),support_sha256={p.relative_to(SITE).as_posix():sha(p) for p in support},library_sha256={n:sha(compiler.parent/'lib'/n) for n in ['zx0.h','zx0.c']},pixels_checked=width*height,pixel_mismatches=mismatch,colors=colors,colors_passed=color_ok,passed=mismatch==0 and color_ok)
 rows.append(row);print(platform,mode,'PASS' if row['passed'] else 'FAIL',mismatch,colors,flush=True)
 (OUT/'results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),records=rows),indent=2),encoding='utf-8')
raise SystemExit(0 if all(r['passed'] for r in rows) else 1)
