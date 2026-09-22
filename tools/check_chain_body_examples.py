"""Verify the three body poses as RAM values and actual emulator sprite pixels."""
from pathlib import Path
import hashlib,json,subprocess
from check_batch200 import dependencies
from check_entity_callbacks import check_pixels
from check_api_tile_examples import read_png
from api_vram_colors import matches_color
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
OUT=SITE/'verification/api-chain-body/example';OUT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Explicit measured geometry of the teaching sequence; no library code is executed here.
poses=[[(48-4*i,16,0) for i in range(8)]]
def step(p,x,y,h):
    offsets=[(4,0),(4,1),(3,3),(1,4),(0,4),(-1,4),(-3,3),(-4,1),(-4,0),(-4,-1),(-3,-3),(-1,-4),(0,-4),(1,-4),(3,-3),(4,-1)]
    out=[(x,y,h)];pull=h
    for cx,cy,old in p[1:]:
        prev=out[-1];delta=[]
        for target,current,size in [(prev[0]-offsets[pull][0],cx,160),(prev[1]-offsets[pull][1],cy,144)]:
            d=target%size-current
            if d>size//2:d-=size
            if d<-(size//2):d+=size
            delta.append((1 if d>0 else -1 if d<0 else 0)*(2 if abs(d)>4 else 1))
        out.append(((cx+delta[0])%160,(cy+delta[1])%144,pull));pull=old
    return out
poses.append(step(poses[0],48,20,4));p=poses[1]
for y in [21,22,23]:p=step(p,48,y,4)
poses.append(p)
expected=[v for point in poses[-1] for v in point]+[0,165]
labels=[(0,0,'JOINT FOLLOWING'),(0,2,'STRAIGHT'),(0,7,'TURN: TICK 1'),(0,11,'TURN: TICK 4'),(0,17,'HEAD=FRONT TAIL=END')]
records=[]
for platform in ['gb','fc']:
    compiler=REPOS/f'kitaq{platform}/kitaq{platform}.exe'
    emulator=REPOS/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe')
    folder=OUT/platform;folder.mkdir(exist_ok=True)
    source=SITE/f'samples/api-examples/{platform}/chain_body.c';rom=folder/('example.gb' if platform=='gb' else 'example.nes')
    cmd=[compiler,source,'-I',compiler.parent/'lib','-I',SITE/'samples','-o',rom,'--no-cache','--no-disasm']
    cmd+=['--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb','--cart=mbc5','--romsize=128k'] if platform=='gb' else ['--mapper=nrom','--nes-chr='+str(SITE/'samples/api-examples/fc/chain_body.chr')]
    run=subprocess.run(list(map(str,cmd)),capture_output=True,cwd=folder,timeout=120)
    assert run.returncode==0,(run.stdout+run.stderr).decode(errors='replace')
    for mode in (['dmg','cgb'] if platform=='gb' else ['ntsc']):
        image=folder/(mode+'.png');state=folder/(mode+'.json')
        cmd=[emulator,rom,'--hardware',mode,'--run-frames','120','--png',image,'--dump-report',state,'--report-sections','meta,watched_memory','--watch-fields','preview','--watch-window','pose:50688:16','--watch-window','tail:50704:10'] if platform=='gb' else [emulator,'run',rom,'--frames','120','--png',image,'--snapshot',state]
        run=subprocess.run(list(map(str,cmd)),capture_output=True,cwd=folder,timeout=120);assert run.returncode==0,run.stderr
        data=json.loads(state.read_text());actual=sum((w['preview_bytes'] for w in data['watched_memory']),[]) if platform=='gb' else data['bus']['ram'][0x600:0x61A]
        label_errors=check_pixels(image,labels,platform)
        w,h,ch,pixels=read_png(image);errors=[];count=0
        # Check entire diagram bands, including empty background, to catch missing or extra dots.
        for band,(pose,offset) in enumerate(zip(poses,[8,34,72])):
            expected_pixels={}
            for i,(x,y,_) in reversed(list(enumerate(pose))):
                color='black' if mode=='dmg' else 'red' if i==0 else 'green' if i==7 else 'blue'
                for yy in range(y*2+offset,y*2+offset+4):
                    for xx in range(x*2,x*2+4):expected_pixels[xx,yy]=color
            top=[32,64,96][band]
            for y in range(top,top+(32 if band==2 else 24)):
                for x in range(32,112):
                    color=expected_pixels.get((x,y),'white' if platform=='gb' else 'black')
                    rgb=pixels[y][x*ch:x*ch+3];count+=1
                    if not matches_color(rgb,color):errors.append([x,y,color,list(rgb)])
        inputs=dependencies(source,compiler.parent/'lib')
        if platform=='fc':inputs['samples/api-examples/fc/chain_body.chr']=sha(SITE/'samples/api-examples/fc/chain_body.chr')
        row=dict(platform=platform,mode=mode,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),input_sha256=inputs,actual=actual,expected=expected,poses=poses,pixel_mismatches=len(errors),label_pixel_mismatches=label_errors,diagram_pixels=count,first_errors=errors[:12],passed=actual==expected and not errors and not label_errors)
        records.append(row);print(platform,mode,row['passed'],'state',actual==expected,'pixels',len(errors),'labels',label_errors,errors[:2],flush=True)
        if row['passed']:state.unlink()
        (OUT/'results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),records=records),indent=2),encoding='utf-8')
    if all(r['passed'] for r in records if r['platform']==platform):cleanup_build_outputs(folder)
raise SystemExit(0 if all(r['passed'] for r in records) else 1)
