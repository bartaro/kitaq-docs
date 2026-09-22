"""Compare mask construction, masked raster and complete overlapping scenes.

The baseline already includes the unmasked raster/rotation optimizations. Stops
surround CPU work only; uploads and initialization are excluded from timings.
Full captured images must remain identical, including covered/rejected lines.
"""
from pathlib import Path
import hashlib,json,random,subprocess
from check_api_tile_examples import read_png

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'publish/library_docs_20260914/wire-speed'
REPOS=ROOT/'publish/github_20260912'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def program(profile,height,color,scene):
    api='Wire3DDMG' if profile=='dmg' else 'Wire3DCGB'
    internal='w3ddmg' if profile=='dmg' else 'w3dcgb'
    # Define markers before library globals to reserve the observation bytes.
    prefix=f'''#pragma bank 0
#define WIRE3D_DMG_HEIGHT {height}
#include "wire3d_{profile}.h"
__location(0xC110) u8 start;
__location(0xC111) u8 mask_ready;
__location(0xC112) u8 done;
__location(0xC113) u8 visible;
__location(0xFF40) u8 bench_lcdc;
__location(0xFF44) u8 bench_ly;
'''
    declarations=''
    setup=''
    if scene:
        declarations=f'''
__prg_rom {api}_Vec3 points[4]={{{{-24,-24,0}},{{24,-24,0}},{{24,24,0}},{{-24,24,0}}}};
__prg_rom {api}_Edge edges[5]={{{{0,1}},{{1,2}},{{2,3}},{{3,0}},{{0,2}}}};
__prg_rom {api}_Face faces[2]={{{{0,2,1}},{{0,3,2}}}};
__prg_rom {api}_EdgeFaces adjacent[5]={{{{0,255}},{{0,255}},{{1,255}},{{1,255}},{{0,1}}}};
{api}_Model model;
{api}_Object objects[3];
'''
        setup='model.vertices=points;model.edges=edges;model.faces=faces;model.edge_faces=adjacent;model.vertex_count=4;model.edge_count=5;model.face_count=2;model.flags=1;'
        if profile=='dmg' and height==96:setup+='model.edge_masks=0;model.edge_mask_count=0;'
        # Input deliberately far-to-near; near and far faces overlap on screen.
        setup+='for(i=0;i<3;i++){objects[i].model=&model;objects[i].x=(s16)i*16-16;objects[i].y=0;objects[i].z=160-(s16)i*48;objects[i].rx=0;objects[i].ry=i;objects[i].rz=0;objects[i].scale_q8=256;objects[i].visible=1;'
        if profile=='cgb':setup+='objects[i].color=i+1;'
        setup+='}'
    main=f'#pragma bank 0\n{declarations}\nvoid main(){{u8 i;{api}_Init();'
    if profile=='cgb':
        main+='while(bench_ly>=144){}while(bench_ly<144){}bench_lcdc=0;Wire3DCGB_SetPaletteRGB15(0,31,31744,992);bench_lcdc=0x81;'
    else:main+='Wire3DDMG_SetPalette(0xFC);'
    main+=f'{api}_BeginFrame();'+setup
    if scene:
        main+=f'start=1;mask_ready=1;{api}_DrawScene(objects,3);'
    else:
        if profile=='cgb':main+=f'{api}_SetLineColor({color});'
        main+=f'start=1;{internal}_clear_occlusion_mask();'
        # Different byte alignments, triangle windings and sizes.
        for x,y,bx,by,cx,cy in [(24,18,83,25,43,76),(96,32,119,58,97,77)]:
            main+=f'{internal}_mark_triangle({x},{y},{bx},{by},{cx},{cy});'
        main+=f'mask_ready=1;{internal}_occlusion_active=1;'
        rng=random.Random(6510)
        lines=[tuple(rng.randrange(n) for n in (128,height,128,height)) for _ in range(32)]
        # Explicit point/axis/edge and fully covered lines exercise early exits.
        lines += [(40,40,40,40),(40,40,50,40),(0,0,127,0),(127,height-1,0,height-1),(0,height-1,0,0),(127,0,127,height-1)]
        for x,y,bx,by in lines:main+=f'{api}_DrawLine2D({x},{y},{bx},{by});'
        main+=f'{internal}_occlusion_active=0;'
    main+=f'done=1;{api}_EndFrame();__wait_vblank();__wait_vblank();visible=1;while(1){{}}}}'
    return prefix,main

def main():
    records=[]
    result_path=OUT/'hidden-speed-results.json'
    previous=json.loads(result_path.read_text())['records'] if result_path.exists() else []
    configurations=[('dmg',96,3),('dmg',120,3),('cgb',96,0),('cgb',96,1),('cgb',96,2),('cgb',96,3)]
    for scene in [False,True]:
        for profile,height,color in configurations:
            if scene and profile=='cgb' and color!=3:continue
            reference=None
            for version in ['baseline','optimized']:
                folder=OUT/f'hidden-{profile}{height}-{color}-{"scene" if scene else "lines"}-{version}'
                folder.mkdir(exist_ok=True)
                library=(OUT/'hidden-baseline' if version=='baseline' else REPOS/'kitaqgb/lib')/f'wire3d_{profile}.c'
                source=folder/'case.c';rom=folder/'case.gb'
                prefix,body=program(profile,height,color,scene)
                combined=prefix+library.read_text()+body
                image=folder/'screen.png'
                cached=next((r for r in previous if (r['profile'],r['height'],r['color'],r['workload'],r['version'])==(profile,height,color,'scene' if scene else 'masked-lines',version)),None)
                # Reuse only an identical compiled translation unit and matching
                # tool/ROM/image hashes. Library CRLF/LF normalization cannot
                # change this generated source; changed C code forces execution.
                if cached and source.exists() and source.read_text()==combined and all(p.exists() and sha(p)==cached[k] for p,k in [(source,'source_sha256'),(rom,'rom_sha256'),(image,'image_sha256'),(REPOS/'kitaqgb/kitaqgb.exe','compiler_sha256'),(REPOS/'kokura/kokura-cli.exe','emulator_sha256')]):
                    pixels=read_png(image)
                    if reference is None:reference=pixels
                    assert pixels==reference
                    cached['library_sha256']=sha(library)
                    records.append(cached)
                    print(profile,height,color,cached['workload'],version,'verified cached execution',flush=True)
                    continue
                source.write_text(combined)
                cmd=[str(REPOS/'kitaqgb/kitaqgb.exe'),str(source),'-I',str(REPOS/'kitaqgb/lib'),'-o',str(rom),'--profile=dev','--stack-bank=fixed','--rst-disable','--cgb=cgb','--cart=mbc5','--romsize=256k','--no-cache','--no-disasm']
                p=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=180);(folder/'build.txt').write_bytes(p.stdout+p.stderr)
                if p.returncode:raise RuntimeError(str(folder)+' build failed')
                times=[]
                for index,name in enumerate(['start','mask_ready','done','visible']):
                    report=folder/(name+'.json');image=folder/'screen.png'
                    cmd=[str(REPOS/'kokura/kokura-cli.exe'),str(rom),'--hardware',profile,'--run-frames','500','--watchpoint',hex(0xC110+index),'--watch-window','marks:49424:4','--dump-report',str(report),'--report-sections','meta,watched_memory','--watch-fields','preview']
                    if name=='visible':cmd+=['--png',str(image)]
                    p=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=180);(folder/(name+'.txt')).write_bytes(p.stdout+p.stderr)
                    data=json.loads(report.read_text())
                    assert p.returncode==0 and data['watched_memory'][0]['preview_bytes'][:index+1]==[1]*(index+1),str(folder)
                    times.append(data['meta']['observation_cycle'])
                pixels=read_png(image)
                if reference is None:reference=pixels
                row=dict(profile=profile,height=height,color=color,workload='scene' if scene else 'masked-lines',version=version,mask_cycles=times[1]-times[0],draw_cycles=times[2]-times[1],total_cycles=times[2]-times[0],pixels_equal_to_baseline=pixels==reference,source_sha256=sha(source),library_sha256=sha(library),rom_sha256=sha(rom),image_sha256=sha(image),compiler_sha256=sha(REPOS/'kitaqgb/kitaqgb.exe'),emulator_sha256=sha(REPOS/'kokura/kokura-cli.exe'))
                records.append(row);print(profile,height,color,row['workload'],version,row['mask_cycles'],row['draw_cycles'],row['pixels_equal_to_baseline'],flush=True)
                (OUT/'hidden-speed-results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),records=records),indent=2))
                assert pixels==reference,'masked pixels changed'
    result_path.write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),records=records),indent=2))

if __name__=='__main__':main()
