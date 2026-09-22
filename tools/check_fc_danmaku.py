"""Check the FC bullet pool against explicit movement/collision expectations."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'publish/library_docs_20260914/fc-effects/danmaku'
SOURCE=r'''
#include "@LIB@/danmaku.c"
__location(0x0600) u16 result[40];
__location(0x02FC) u8 last_oam[4];
void main(void) {
    u8 i;
    dm_player_x=0;dm_player_y=0;dm_invulnerable=0;
    danmaku_reset();
    result[0]=danmaku_spawn(100,100,8,-8);
    for(i=0;i<16;i++)danmaku_step();
    result[1]=dm_x[0];result[2]=dm_y[0];result[3]=dm_count;
    danmaku_reset();danmaku_fan(100,100,0,8,4,16);danmaku_step();
    result[4]=dm_count;
    for(i=0;i<4;i++){result[5+i*2]=dm_x[i];result[6+i*2]=dm_y[i];}
    danmaku_reset();dm_player_x=100;dm_player_y=100;
    danmaku_spawn(101,100,0,0);danmaku_step();
    result[13]=dm_hit;result[14]=dm_count;
    danmaku_spawn(110,100,0,0);danmaku_step();result[15]=dm_graze;
    danmaku_step();result[16]=dm_graze;
    danmaku_clear();dm_invulnerable=1;
    danmaku_spawn(100,100,0,0);danmaku_step();result[17]=dm_hit;result[18]=dm_count;
    danmaku_reset();dm_player_x=0;dm_player_y=0;
    for(i=0;i<64;i++)danmaku_spawn(100,100,0,0);
    result[19]=dm_count;result[20]=danmaku_spawn(100,100,0,0);
    result[21]=dm_rejected;result[22]=dm_spawned;
    danmaku_clear();result[23]=dm_count;result[24]=dm_peak;
    result[25]=danmaku_spawn(7,100,0,0);result[26]=dm_rejected;
    danmaku_spawn(247,100,127,0);danmaku_step();result[27]=dm_count;
    danmaku_spawn(8,100,-128,0);danmaku_step();result[28]=dm_count;
    danmaku_reset();
    for(i=0;i<64;i++)danmaku_spawn(100,100,0,0);
    __oam_clear();
    result[29]=danmaku_draw(63,255,7,195);
    result[30]=last_oam[0];result[31]=last_oam[1];
    result[32]=last_oam[2];result[33]=last_oam[3];
    result[34]=danmaku_draw(64,255,1,0);
    result[35]=danmaku_draw(0,0,1,0);
    result[36]=last_oam[0];result[37]=dm_count;result[38]=dm_spawned;
    result[39]=0xA55A;
    while(1){}
}
'''
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    lib=(ROOT/'publish/github_20260912/kitaqfc/lib').as_posix()
    expected=[1,108,92,1,4,101,100,100,101,99,100,100,99,1,0,1,0,0,1,64,0,1,64,0,64,0,2,0,0,1,95,7,195,96,0,0,95,64,64,0xA55A]
    fixtures=OUT/'fixtures.json'
    fixtures.write_text(json.dumps([dict(name='danmaku',source=SOURCE.replace('@LIB@',lib),expected=expected)],indent=2),encoding='utf-8')
    result=subprocess.run([sys.executable,str(Path(__file__).with_name('check_compiler_parity.py')),'--platform','fc','--fixtures',str(fixtures),'--output',str(OUT/'state')])
    if result.returncode==0:
        report=OUT/'state/report.json';data=json.loads(report.read_text())
        data['library_sha256']={('kitaqfc/lib/'+name):hashlib.sha256((Path(lib)/name).read_bytes()).hexdigest() for name in ['danmaku.c','danmaku.h','core.h','intrinsics.h']}
        data['danmaku_checker_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        report.write_text(json.dumps(data,indent=2))
    raise SystemExit(result.returncode)
if __name__=='__main__':main()
