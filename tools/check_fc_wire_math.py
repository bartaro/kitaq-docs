"""Check all three rotation axes and projection boundaries with exact integer expectations."""
from pathlib import Path
import json,math,subprocess,sys
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'publish/library_docs_20260914/fc-effects/wire3d/math'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    lib=(ROOT/'publish/github_20260912/kitaqfc/lib/wire3d.c').as_posix()
    sine=[round(64*math.sin(2*math.pi*i/32)) for i in range(32)];fixtures=[]
    for w,h in [(64,48),(96,64),(128,96)]:
        source=f'#define WIRE3D_FC_WIDTH {w}\n#define WIRE3D_FC_HEIGHT {h}\n#include "{lib}"\n__location(0x0600) u16 result[224];\nvoid main(){{u8 i;s16 x,y,z;s16 sx,sy;'
        expected=[]
        for axis in range(3):
            args=['0','0','0'];args[axis]='i';first,second=[('y','z'),('x','z'),('x','y')][axis]
            source+=f'for(i=0;i<32;i++){{x=24;y=24;z=24;Wire3DFC_RotatePoint(&x,&y,&z,{",".join(args)});result[{axis*64}+i*2]={first};result[{axis*64+1}+i*2]={second};}}'
            for angle in range(32):
                s,c=sine[angle],sine[(angle+8)&31]
                pair=(int((24*c+24*s)/64),int((24*c-24*s)/64)) if axis==1 else (int((24*c-24*s)/64),int((24*s+24*c)/64))
                expected.extend(v&65535 for v in pair)
        points=[(-127,127,32),(127,-127,255),(24,-24,96),(0,0,31),(0,0,256),(-128,0,96),(0,128,96),(0,0,96)]
        for n,(x,y,z) in enumerate(points):
            k=192+n*3
            source+=f'sx=1234;sy=2345;result[{k}]=Wire3DFC_ProjectPoint({x},{y},{z},&sx,&sy);result[{k+1}]=sx;result[{k+2}]=sy;'
            if -127<=x<=127 and -127<=y<=127 and 32<=z<=255:
                scale=min(255,round(64*w/z));px=w//2+(1 if x>=0 else -1)*(abs(x)*scale//128);py=h//2-(1 if y>=0 else -1)*(abs(y)*scale//128);expected.extend([1,px&65535,py&65535])
            else:expected.extend([0,1234,2345])
        source+='sx=1234;sy=2345;result[216]=Wire3DFC_ProjectPoint(0,0,96,0,&sy);result[217]=sy;result[218]=Wire3DFC_ProjectPoint(0,0,96,&sx,0);result[219]=sx;x=12;y=34;Wire3DFC_RotatePoint(&x,&y,0,1,2,3);result[220]=x;result[221]=y;result[222]=0xA55A;while(1){}}'
        expected.extend([0,2345,0,1234,12,34,0xA55A]);fixtures.append(dict(name=f'wire-math-{w}',source=source,expected=expected))
    path=OUT/'fixtures.json';path.write_text(json.dumps(fixtures,indent=2))
    raise SystemExit(subprocess.run([sys.executable,str(Path(__file__).with_name('check_compiler_parity.py')),'--platform','fc','--fixtures',str(path),'--output',str(OUT/'state')]).returncode)

if __name__=='__main__':main()
