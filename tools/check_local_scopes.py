"""Check sibling/nested storage, parameter shadowing and for-init lifetime on GB/FC."""
from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'publish/library_docs_20260914/fc-effects/local-scopes'
fixtures=[
 ('sibling','u16 f(){u16 answer=0;{u8 mid=7;answer=mid;}{u16 mid=300;answer+=mid;}return answer;}','result[0]=f();',[307]),
 ('nested','u16 f(u16 value){u16 answer=value;{u8 value=9;answer+=value;}return answer+value;}','result[0]=f(300);',[609]),
 ('loop-init','','u16 i=19;u16 sum=0;for(u8 i=0;i<3;i++){sum+=i;}result[0]=sum;result[1]=i;for(u16 i=300;i<302;i++){sum+=i;}result[2]=sum;result[3]=i;',[3,19,604,19]),
 ('pointer-array','','u16 a[2];u16 *p;a[0]=300;a[1]=400;p=a;{u8 a[3];u8 *p;a[0]=8;a[1]=9;a[2]=10;p=a;result[0]=p[1];result[1]=sizeof(a);}result[2]=p[1];result[3]=sizeof(a);',[9,3,400,4]),
 ('branch-types','u16 f(u8 pick){if(pick){u8 v=7;return v;}else{u16 v=511;return v;}}','result[0]=f(0);result[1]=f(1);',[511,7]),
]
OUT.mkdir(parents=True,exist_ok=True)
records=[dict(name=name,source='__location(0xC600) u16 result[8];\n'+helper+'\nvoid main(){'+body+'result['+str(len(expected))+']=0xA55A;while(1){}}',expected=expected+[0xA55A]) for name,helper,body,expected in fixtures]
p=OUT/'fixtures.json';p.write_text(json.dumps(records,indent=2),encoding='utf-8')
raise SystemExit(subprocess.run([sys.executable,str(Path(__file__).with_name('check_compiler_parity.py')),'--fixtures',str(p),'--output',str(OUT/'state')]).returncode)
