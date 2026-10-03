"""Run the actual KITAQGB library machine code in KOKURA, not a host port."""
import argparse
import hashlib
import json
import math
import struct
import subprocess
from pathlib import Path
import sys
def make_game(rom,capi,bridge):
    sys.path.insert(0,str(bridge))
    from kokura_bridge import Core,KokuraLibrary
    class Game:
        def __init__(self):
            self.sym={}
            for line in rom.with_suffix('.map').read_text(encoding='utf-8').splitlines():
                p=line.split()
                if len(p)==6 and p[3]=='S':self.sym[p[5]]=(int(p[0],16),int(p[1]))
            self.core=Core(KokuraLibrary(capi))
            self.core.load_rom_path(rom)
        def read(self,name):return self.core.peek8(self.sym[name][0])
        def write(self,name,value):self.core.write_block(self.sym[name][0],bytes([value]))
    return Game()



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--compiler", type=Path, required=True)
    parser.add_argument("--capi", type=Path, required=True)
    parser.add_argument("--bridge", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve(); ROOT=Path(__file__).resolve().parent; lib=ROOT/"sources/lib"
    out.mkdir(parents=True, exist_ok=True)
    rom = out / "physics_surface.gb"
    command = [str(args.compiler.resolve()), str(lib/"fixed.c"), str(lib/"physics2d.c"),
               str(ROOT/"sources/surface.c"), "-I", str(lib), "-o", str(rom),
               "--no-cache", "--profile=dev", "-O1", "--no-disasm", "--rst-disable", "--stack-bank=fixed",
               f"--debug-out={out/'debug'}"]
    with (out/"build.log").open("w") as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True, cwd=out)
    game = make_game(rom,args.capi.resolve(),args.bridge.resolve())
    game.core.run_frames(20)
    assert game.read("test_ready") == 165
    rows = []

    def run(cmd, vx, vy, nx=0, ny=-256, sx=0, sy=0, e=96, friction=0, threshold=24, kick=0, limit=640):
        values = [vx,vy,nx,ny,sx,sy,e,friction,threshold,kick,limit,0]
        game.core.write_block(game.sym["test_input"][0],struct.pack("<12h",*values))
        game.write("test_command",cmd)
        for _ in range(10):
            game.core.run_frame()
            game.core.drain_audio_frames()
            if game.read("test_command") == 0: break
        assert game.read("test_command") == 0, values
        actual = struct.unpack("<3h",game.core.read_block(game.sym["test_output"][0],6))
        rows.append(dict(command=cmd,inputs=values,outputs=actual))
        return actual

    heading_max = 0
    speed_error_max = 0
    values = [-16000,-4096,-1024,-640,-129,-1,0,1,129,640,1024,4096,16000]
    for x in values:
        for y in values:
            vx,vy,_ = run(1,x,y)
            length = math.hypot(x,y)
            speed = math.hypot(vx,vy)
            assert speed <= 640.01, (x,y,vx,vy,speed)
            if length > 640:
                error = abs(math.atan2(vy,vx)-math.atan2(y,x))
                error = min(error,math.tau-error)
                heading_max=max(heading_max,math.degrees(error))
                # Very large inputs have Q8 scale quantization; directions still hold.
                if length < 2000: speed_error_max=max(speed_error_max,1-speed/640)
                assert error < math.radians(0.3),(x,y,vx,vy,error)
            elif x+y==0 or abs(x)+abs(y)<=640:
                assert (vx,vy)==(x,y),(x,y,vx,vy)
    assert speed_error_max < 0.016,speed_error_max
    contact_error = 0
    energy_gain_raw = 0
    for angle in range(0,256,8):
        nx,ny=int(256*math.cos(angle*math.tau/256)),int(256*math.sin(angle*math.tau/256))
        for e,mu in [(96,6),(144,24),(160,28),(64,16),(104,36)]:
            for speed in [12,96,384,640]:
                tx,ty=-ny/256,nx/256
                x=round(-speed*nx/256+180*tx)
                y=round(-speed*ny/256+180*ty)
                vx,vy,closing=run(2,x,y,nx,ny,e=e,friction=mu)
                n=(x*nx+y*ny)/256
                tangent=(y*nx-x*ny)/256
                impulse=-n*(1+(e/256 if -n>24 else 0))
                friction=min(abs(tangent),impulse*mu/256)*math.copysign(1,tangent)
                expected=(x+impulse*nx/256+friction*ny/256,y+impulse*ny/256-friction*nx/256)
                error=math.hypot(vx-expected[0],vy-expected[1])
                contact_error=max(contact_error,error)
                assert error <= 7,(rows[-1],expected,error)
                gain=math.hypot(vx,vy)-math.hypot(x,y)
                energy_gain_raw=max(energy_gain_raw,gain)
                assert gain <= 1,(rows[-1],"passive speed gain exceeds one fixed-point unit")
                assert closing>=0
    assert run(2,0,12,e=160)[:2]==(0,0),"low-speed contact must settle"
    assert run(2,0,-128)[:2]==(0,-128),"separating velocity must not bounce"
    assert run(2,0,0,sy=-256,e=128)[:2]==(0,-384),"relative surface velocity"
    assert run(2,128,256,kick=384)[:2]==(128,-384),"powered kick"
    reference=run(2,84,182,nx=-181,ny=-181,e=96,friction=0)
    assert abs(reference[0]-(-99))<=2 and abs(reference[1]-(-1))<=2,reference
    assert run(3,12,-15)==(12,-15,0),"null safety"
    assert run(4,638,-100)[:2]==(640,-89),"legacy gravity unchanged"
    assert run(1,128,64,limit=0)[:2]==(0,0)
    for value in (-32768,-16000,-1024,-640,-257,-129,-1,0,1,129,257,640,1024,16000,32767):
        for coefficient in range(-256,257):
            expected = math.trunc(value*coefficient/256)
            expected = (expected+32768)%65536-32768
            assert run(5,value,0,nx=coefficient)[0] == expected, (value,coefficient)
    for start in (-8191,-1,0,1,2,7,16,127,128,255,1024,4096,8191):
        for end in (-8191,-1024,-128,-7,-1,0,1,8191):
            expected = 0 if start <= 0 else 256 if end >= 0 else (start*256)//(start-end)
            assert run(6,start,end)[0] == expected, (start,end)
    max_rest_normal = 0
    for angle in range(256):
        nx,ny=round(256*math.cos(angle*math.tau/256)),round(256*math.sin(angle*math.tau/256))
        x,y=round(-6*nx/256-24*ny/256),round(-6*ny/256+24*nx/256)
        vx,vy,_=run(2,x,y,nx,ny,friction=6)
        normal=abs((vx*nx+vy*ny)/256)
        max_rest_normal=max(max_rest_normal,normal)
        assert normal <= 1, (angle,vx,vy,normal)
    result=dict(passed=True,cases=len(rows),max_heading_error_deg=heading_max,
                max_rest_normal_raw=max_rest_normal,
                max_speed_loss_near_game_range=speed_error_max,max_contact_error_raw=contact_error,
                max_passive_speed_gain_raw=energy_gain_raw,
                rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest())
    (out/"cases.json").write_text(json.dumps(rows,indent=2))
    (out/"summary.json").write_text(json.dumps(result,indent=2))
    print(json.dumps(result),flush=True)
    game.core.close()


if __name__ == "__main__":
    main()
