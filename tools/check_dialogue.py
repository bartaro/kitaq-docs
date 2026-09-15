"""Replay dialogue controls and choices, including frame-by-frame blocking checks."""
from pathlib import Path
import hashlib,json,re,subprocess
from check_text_layout import FRAME,window,fill,put
from check_api_tile_examples import read_png
from api_vram_colors import matches_color
from api_build_cleanup import cleanup_build_outputs

SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUT=SITE/'verification/api-dialogue';LIB=REPOS/'kitaqgb/lib'
COMPILER=REPOS/'kitaqgb/kitaqgb.exe';EMULATOR=REPOS/'kokura/kokura-cli.exe'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
compiled={}

def build(source):
    if str(source) in compiled:return compiled[str(source)]
    folder=OUT/'state/build'/source.stem;folder.mkdir(parents=True,exist_ok=True)
    rom=folder/'example.gb';rom.unlink(missing_ok=True)
    cmd=[str(COMPILER),str(source),'-I',str(LIB),'-I',str(SITE/'samples'),'-o',str(rom),
         '--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb','--cart=mbc5',
         '--romsize=64k','--no-cache','--no-disasm']
    result=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=90)
    (folder/'build.txt').write_bytes(result.stdout+result.stderr)
    if result.returncode:raise RuntimeError('Build failed: '+str(source))
    cleanup_build_outputs(folder);compiled[str(source)]=rom
    return rom

def run(source,name,mode,expected,returned=None,sequence='NONE:180',timeline=False,picture=False,frames=180):
    built=build(source);folder=OUT/(name+'-'+mode) if picture else OUT/'state'/(name+'-'+mode)
    folder.mkdir(parents=True,exist_ok=True);rom=folder/'example.gb';rom.write_bytes(built.read_bytes())
    runtime=folder/'runtime.json';png=folder/'screen.png';trace=folder/'timeline.jsonl'
    for p in [runtime,png,trace]:p.unlink(missing_ok=True)
    cmd=[str(EMULATOR),str(rom),'--hardware',mode,'--run-frames',str(frames),
         '--dump-report',str(runtime),'--report-sections','meta,watched_memory','--watch-fields','preview',
         '--watch-window','result:50688:8']
    cmd += ['--input',sequence.split(':')[0]] if timeline else ['--input-seq',sequence]
    for offset in range(0,1024,16):cmd+=['--watch-window',f'map{offset}:{0x9800+offset}:16']
    if picture:cmd+=['--png',str(png)]
    if timeline:cmd+=['--trace-point','frame_end','--timeline-out',str(trace)]
    result=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=120)
    (folder/'runtime.txt').write_bytes(result.stdout+result.stderr)
    if result.returncode:raise RuntimeError('Run failed: '+name+' '+mode)
    state=json.loads(runtime.read_text(encoding='utf-8'))
    watches={w['name']:w for w in state['watched_memory']};actual=[]
    for offset in range(0,1024,16):
        w=watches['map'+str(offset)];assert w['addr']==0x9800+offset and not w.get('preview_truncated',False)
        actual+=w['preview_bytes']
    observed=watches['result']['preview_bytes']
    row={'name':name,'platform':'gb','mode':mode,'source':source.relative_to(SITE).as_posix(),
         'source_sha256':sha(source),'rom':rom.relative_to(SITE).as_posix(),'rom_sha256':sha(rom),
         'frames':state['meta']['frames_executed'],'input_sequence':sequence,'actual':actual,'expected':expected,
         'observed':observed,'expected_result':returned,'passed':actual==expected and (returned is None or observed==returned) and state['meta']['frames_executed']==frames}
    if timeline:
        frames=[]
        for line in trace.read_text(encoding='utf-8').splitlines():
            entry=json.loads(line);w={x['name']:x for x in entry['watched_memory']}
            frames.append({'frame':entry['completed_frames'],'result':w['result']['preview_bytes'],
                           'row2':w['map64']['preview_bytes'],'row3':w['map96']['preview_bytes'],
                           'row4':w['map128']['preview_bytes']})
        row['timeline']=frames
        # Keep only the bounded observations needed for the assertions.
        trace.write_text('\n'.join(json.dumps(f) for f in frames),encoding='utf-8')
    if picture:
        font_text=(SITE/'samples/font_gb.h').read_text(encoding='utf-8')
        font=[int(n,0) for n in re.findall(r'0x[0-9a-fA-F]+|\d+',font_text[font_text.index('{')+1:font_text.index('}')])]
        masks=[[font[t*16+y*2]|font[t*16+y*2+1] for y in range(8)] for t in range(128)]
        masks[1:9]=FRAME+[[0,16,24,28,24,16,0,0],[0,0,0,0,254,124,56,16]]
        width,height,channels,rows=read_png(png);assert (width,height)==(160,144)
        background=rows[-1][:3];pixels=colors=ink_count=0
        for y in range(height):
            for x in range(width):
                tx,ty=x//8,y//8;ink=bool(masks[expected[ty*32+tx]][y%8]&(1<<(7-x%8)))
                rgb=rows[y][x*channels:x*channels+3];pixels+=ink!=(rgb!=background)
                if ink:
                    color=('blue' if name=='dialogue_flow' else 'green') if mode=='cgb' and 1<=tx<19 and 2<=ty<7 else 'black'
                    colors+=not matches_color(rgb,color);ink_count+=1
        row.update(image=png.relative_to(SITE).as_posix(),image_sha256=sha(png),pixel_mismatches=pixels,color_mismatches=colors,ink_pixels=ink_count)
        row['passed'] &= pixels==colors==0 and ink_count>0
    print(name,mode,'PASS' if row['passed'] else 'FAIL',flush=True)
    return row

PREFIX='''#pragma bank 0
#include "text.c"
__location(0xFF40) u8 lcd;
__location(0xC600) u8 result[8];
'''
START='__wait_vblank();lcd=0;__vram_fill(0x9800,0,1024);lcd=0x91;'
END='result[7]=165;while(1){}'

def fixture(name,body,extra=''):
    path=OUT/'state/sources'/(name+'.c');path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(PREFIX+extra+'\nvoid main(){'+START+body+END+'}\n',encoding='utf-8')
    return path

def main():
    OUT.mkdir(parents=True,exist_ok=True);records=[];cases=[]
    grid=[0]*1024;put(grid,1,0,'DIALOGUE FLOW');window(grid,1,2,18,5)
    for y,text in [(3,'NEAR'),(4,'READY'),(5,'BANK 2')]:put(grid,2,y,text)
    put(grid,1,8,'CLOSED AREA');put(grid,1,14,'BANK RESTORED');put(grid,16,14,'161');put(grid,1,16,'SPEED 2 / WAIT 12')
    for mode in ['dmg','cgb']:records.append(run(SITE/'samples/api-examples/gb/dialogue_flow.c','dialogue_flow',mode,grid,picture=True))
    grid=[0]*1024;put(grid,1,0,'CHOOSE AN ITEM');window(grid,1,2,18,5)
    for i,text in enumerate(['SWORD','SHIELD','POTION']):put(grid,3,3+i,text)
    grid[4*32+2]=7;put(grid,1,9,'SELECTED');put(grid,12,9,'1');put(grid,1,12,'UP/DOWN: MOVE');put(grid,1,14,'A: OK  B: CANCEL')
    for mode in ['dmg','cgb']:records.append(run(SITE/'samples/api-examples/gb/dialogue_choice.c','dialogue_choice',mode,grid,sequence='NONE:30;DOWN:10;NONE:20;A:10;NONE:110',picture=True))

    grid=[0]*1024;window(grid,1,1,8,4);put(grid,2,2,'AB');put(grid,2,3,'CD');window(grid,12,1,8,4);put(grid,13,2,'EF');put(grid,13,3,'GH')
    extra='const u8 near_text[]={65,66,10,67,1,0,68,0,88};\n#pragma bank 1\nconst u8 marker=161;\n#pragma bank 2\nconst u8 far_text[]={69,70,10,71,1,2,72,0,88};\n#pragma bank 0\n'
    src=fixture('controls','text_open(1,1,8,4);text_print(near_text);text_open(12,1,8,4);__bankswitch(1);text_print_far(2,far_text);result[0]=marker;',extra)
    for mode in ['dmg','cgb']:cases.append(run(src,'controls',mode,grid,[161,0,0,0,0,0,0,165]))

    grid=[0]*1024;window(grid,1,1,6,4);put(grid,2,2,'AB')
    src=fixture('lifecycle','text_open(1,1,6,4);text_print("AB");text_open(10,1,6,4);text_print("C");text_close();text_close();text_print("D");text_open(20,1,0,3);text_print("E");')
    for mode in ['dmg','cgb']:cases.append(run(src,'lifecycle',mode,grid,[0,0,0,0,0,0,0,165]))

    src=fixture('timing','text_set_speed(3);text_open(1,1,8,4);__wait_vblank();result[0]=1;text_print("AB");result[0]=2;text_set_speed(0);text_print(wait_open);result[0]=3;text_close();text_print(wait_closed);result[0]=4;',
                'const u8 wait_open[]={1,5,90,0};const u8 wait_closed[]={1,4,0};')
    for mode in ['dmg','cgb']:
        row=run(src,'timing',mode,[0]*1024,[4,0,0,0,0,0,0,165],timeline=True)
        first=lambda predicate:next(f['frame'] for f in row['timeline'] if predicate(f))
        a=first(lambda f:f['row2'][2]==65);b=first(lambda f:f['row2'][3]==66)
        done_text=first(lambda f:f['result'][0]>=2);done_wait=first(lambda f:f['result'][0]>=3);done_closed=first(lambda f:f['result'][0]>=4)
        row['timing']={'a_frame':a,'b_frame':b,'text_done':done_text,'wait_done':done_wait,'closed_wait_done':done_closed,
                       'deltas':[b-a,done_text-b,done_wait-done_text,done_closed-done_wait]}
        row['passed'] &= row['timing']['deltas']==[3,3,5,4]
        print('timing deltas',mode,row['timing']['deltas'],flush=True);cases.append(row)

    grid=[0]*1024;window(grid,1,1,8,4);put(grid,2,2,'A')
    src=fixture('lcd_off_wait','lcd=0;text_set_speed(255);text_open(1,1,8,4);text_print(off_wait);','const u8 off_wait[]={1,255,65,0};')
    for mode in ['dmg','cgb']:cases.append(run(src,'lcd_off_wait',mode,grid,[0,0,0,0,0,0,0,165],sequence='NONE:5',frames=5))

    for kind in ['explicit','auto','far']:
        grid=[0]*1024;window(grid,1,1,4,3);put(grid,2,2,'C' if kind=='auto' else 'B')
        stream='65,66,67,0' if kind=='auto' else '65,2,66,0'
        extra=('#pragma bank 2\n' if kind=='far' else '')+'const u8 page[]={'+stream+'};\n#pragma bank 0\n'
        src=fixture('page_'+kind,'text_open(1,1,4,3);'+('text_print_far(2,page);' if kind=='far' else 'text_print(page);'),extra)
        sequences=[('A','NONE:30;A:10;NONE:140')]
        if kind=='explicit':sequences += [('B','NONE:30;B:10;NONE:140'),('START','NONE:30;START:10;NONE:140'),('held','A:180')]
        for key,seq in sequences:
            for mode in ['dmg','cgb']:
                row=run(src,'page_'+kind+'_'+key,mode,grid,[0,0,0,0,0,0,0,165],sequence=seq,timeline=key=='held')
                if key=='held':
                    row['completed_frame']=next(f['frame'] for f in row['timeline'] if f['result'][7]==165)
                    row['passed'] &= row['completed_frame']<30
                else:
                    waiting=[0]*1024;window(waiting,1,1,4,3);put(waiting,2,2,'A')
                    if kind=='auto':waiting[2*32+3]=8
                    before=run(src,'page_'+kind+'_'+key+'_before',mode,waiting,[0]*8,sequence='NONE:29',frames=29)
                    after=run(src,'page_'+kind+'_'+key+'_after',mode,grid,[0,0,0,0,0,0,0,165],sequence='NONE:30;'+key+':3',frames=33)
                    cases.extend([before,after]);row['input_checkpoints']=[29,33]
                cases.append(row)

    choices='const u8 * const choices[]={"ONE","TWO","THREE"};'
    src=fixture('choice','text_open(1,1,10,5);result[0]=text_choice(choices,3);',choices)
    variants=[('accept','NONE:30;A:10;NONE:140',0,0),('cancel','NONE:30;B:10;NONE:140',255,0),
              ('up_wrap','NONE:30;UP:10;NONE:10;A:10;NONE:120',2,2),
              ('down_wrap','NONE:20;DOWN:5;NONE:5;DOWN:5;NONE:5;DOWN:5;NONE:5;A:5;NONE:125',0,0),
              ('hold_down','NONE:20;DOWN:60;NONE:5;A:5;NONE:90',1,1),
              ('held_a','A:180',0,0),('both_accept_cancel','NONE:30;A,B:10;NONE:140',0,0),
              ('down_accept','NONE:30;DOWN,A:10;NONE:140',1,0),
              ('opposite','NONE:30;UP,DOWN:10;NONE:10;A:10;NONE:120',0,0)]
    for name,seq,value,cursor in variants:
        grid=[0]*1024;window(grid,1,1,10,5)
        for i,text in enumerate(['ONE','TWO','THREE']):put(grid,3,2+i,text)
        grid[(2+cursor)*32+2]=7
        for mode in ['dmg','cgb']:
            row=run(src,'choice_'+name,mode,grid,[value,0,0,0,0,0,0,165],sequence=seq)
            cases.append(row)
    grid=[0]*1024;window(grid,1,1,10,5)
    for i,text in enumerate(['ONE','TWO','THREE']):put(grid,3,2+i,text)
    grid[3*32+2]=7
    for mode in ['dmg','cgb']:
        row=run(src,'choice_hold_only',mode,grid,[0]*8,sequence='DOWN:180',timeline=True)
        held=[f for f in row['timeline'] if 5<=f['frame']<=180]
        row['passed'] &= bool(held) and all(f['row3'][2]==7 and f['result'][7]==0 for f in held)
        cases.append(row)
    src=fixture('choice_empty','result[0]=text_choice(0,0);')
    for mode in ['dmg','cgb']:cases.append(run(src,'choice_empty',mode,[0]*1024,[255,0,0,0,0,0,0,165]))
    sources=[LIB/'rpg.h',LIB/'text.c'];supports=['gb_common.h','gb_tile_example.h','font_gb.h','vram_example_colors.h']
    report={'records':records,'cases':cases,'compiler_sha256':sha(COMPILER),'emulator_sha256':sha(EMULATOR),
            'script_sha256':sha(Path(__file__)),'model_sha256':sha(SITE/'tools/check_text_layout.py'),
            'source_sha256':{p.relative_to(REPOS).as_posix():sha(p) for p in sources},
            'support_sha256':{'samples/'+n:sha(SITE/'samples'/n) for n in supports}}
    (OUT/'results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('Total:',sum(r['passed'] for r in records+cases),'/',len(records+cases),flush=True)
    raise SystemExit(0 if all(r['passed'] for r in records+cases) else 1)

if __name__=='__main__':main()
