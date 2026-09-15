"""Execute constant/runtime fixed-point multiplication and dot-product regressions."""
from pathlib import Path
import json
import check_physics_edges as runner
runner.OUT=runner.SITE/'verification/api-physics/multiply/state'
runner.OUT.mkdir(parents=True,exist_ok=True)

def trunc(n):
    """Mathematical signed division, avoiding Python's negative floor division."""
    return (1 if n>=0 else -1)*(abs(n)//256)

values=[-32768,-257,-129,-3,-1,0,1,3,129,257,32767]
coefficients=[-128,-127,-64,-32,-16,-8,-4,-2,-1,0,1,2,4,8,16,32,64,127]
for q17 in [False,True]:
    name='__smul16x8'+('_q1_7' if q17 else '')
    for c in coefficients:
        body='';expected=[]
        for i,v in enumerate(values):
            body+=f'a={v};c={c};result[{2*i}]={name}(a,{c});result[{2*i+1}]={name}(a,c);'
            expected.extend([trunc(v*c)*(2 if q17 else 1)]*2)
        runner.execute('gb',('q17' if q17 else 'q08')+'-'+str(c),body,expected,glob='s16 a; s8 c;')

# Dot products quantize each term separately; they do not divide the final sum.
for q17 in [False,True]:
    suffix='q1_7' if q17 else 'q8_8';factor=2 if q17 else 1
    body='';expected=[]
    for i,(x,y,z,ax,ay,az) in enumerate([(-257,257,1,64,-64,127),(-3,-129,257,127,-128,1),(32767,-32768,256,-128,127,64),(257,-257,1,0,0,0)]):
        body+=f'x={x};y={y};z={z};ax={ax};ay={ay};az={az};'
        body+=f'result[{4*i}]=__sdot2_{suffix}(x,y,{ax},{ay});result[{4*i+1}]=__sdot2_{suffix}(x,y,ax,ay);'
        body+=f'result[{4*i+2}]=__sdot3_{suffix}(x,y,z,{ax},{ay},{az});result[{4*i+3}]=__sdot3_{suffix}(x,y,z,ax,ay,az);'
        d2=(trunc(x*ax)+trunc(y*ay))*factor;d3=d2+trunc(z*az)*factor
        expected += [d2,d2,d3,d3]
    runner.execute('gb','dot-'+suffix,body,expected,glob='s16 x; s16 y; s16 z; s8 ax; s8 ay; s8 az;')

# Calls are observable even when the coefficient is zero. Check each input once.
calls=[('__smul16x8(tick(),0)',1,0),('__smul16x8_q1_7(tick(),0)',1,0),
       ('__sdot2_q8_8(tick(),tick(),0,0)',2,0),('__sdot2_q8_8(tick(),tick(),0,64)',2,64),
       ('__sdot2_q8_8(tick(),tick(),64,0)',2,64),('__dot2_q8_8(tick(),tick(),0,0)',2,0),
       ('__dot2_q8_8(tick(),tick(),0,64)',2,64),('__dot2_q8_8(tick(),tick(),64,0)',2,64),
       ('__sdot3_q1_7(tick(),tick(),tick(),0,0,0)',3,0)]
body='';expected=[]
for i,(call,count,value) in enumerate(calls):
    body+=f'calls=0;result[{2*i}]={call};result[{2*i+1}]=calls;';expected += [value,count]
runner.execute('gb','zero-evaluation',body,expected,glob='u8 calls; s16 tick(){calls=calls+1;return 256;}')

report={'records':runner.rows,'script_sha256':runner.sha(Path(__file__)),
        'runner_sha256':runner.sha(Path(runner.__file__)),'passed':all(r['passed'] for r in runner.rows)}
(runner.OUT.parent/'results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
raise SystemExit(0 if report['passed'] else 1)
