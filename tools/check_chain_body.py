"""Verify articulated-chain fixtures against the original game source and boundary expectations.

Only the explicit result address and target build options differ. Expected
values are independent fixture data, never copied from the other compiler.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess

SITE = Path(__file__).resolve().parents[1]
REPOS = SITE.parents[1] / 'publish/github_20260912'
if not REPOS.exists():
    REPOS = SITE.parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--fixtures', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--platform', choices=['gb', 'fc'])
    ap.add_argument('--only')
    ap.add_argument('--gb-compiler', type=Path)
    ap.add_argument('--fc-compiler', type=Path)
    ap.add_argument('--fc-mapper', default='nrom', choices=['nrom','mmc3'])
    a = ap.parse_args()
    base = a.output.resolve(); base.mkdir(parents=True, exist_ok=True)
    fixtures = json.loads(a.fixtures.read_text(encoding='utf-8'))
    rows = []
    for platform in ([a.platform] if a.platform else ['gb', 'fc']):
        compiler = (a.gb_compiler if platform=='gb' else a.fc_compiler) or REPOS / ('kitaq'+platform) / ('kitaq'+platform+'.exe')
        compiler = compiler.resolve(strict=True)
        emulator = REPOS / ('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe')
        variants = [('default', []), ('unoptimized', ['-O0'])]
        variants += [('stack', ['--abi=stack'])] if platform=='gb' else [('no-inline', ['--no-small-inline']), ('fastcall', ['--fastcall-v2'])]
        for fixture in fixtures:
            if a.only and a.only not in fixture['name']: continue
            for variant, flags in variants:
                folder = base/platform/fixture['name']/variant; folder.mkdir(parents=True, exist_ok=True)
                source = folder/'case.c'; rom = folder/('case.gb' if platform=='gb' else 'case.nes')
                source.write_text(fixture['source'].replace('0xC600', '0x0600') if platform=='fc' else fixture['source'], encoding='utf-8')
                cmd = [str(compiler), str(source), '-o', str(rom), '--no-cache', '--no-disasm', '-I', str(REPOS/('kitaq'+platform)/'lib')] + flags
                cmd += ['--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb'] if platform=='gb' else ['--mapper='+a.fc_mapper]
                build = subprocess.run(cmd, cwd=folder, capture_output=True, timeout=120)
                (folder/'build.txt').write_bytes(build.stdout+build.stderr)
                common = dict(platform=platform, name=fixture['name'], variant=variant, compiler_sha256=sha(compiler), emulator_sha256=sha(emulator), source_sha256=sha(source), build_exit=build.returncode)
                if build.returncode:
                    rows.append(dict(common, passed=False)); print(platform, fixture['name'], variant, 'BUILD FAIL', flush=True)
                else:
                    expected=fixture['expected']; count=len(expected)*2
                    for mode in (['dmg','cgb'] if platform=='gb' else ['ntsc']):
                        state=folder/(mode+'.json')
                        if platform=='gb':
                            cmd=[str(emulator),str(rom),'--hardware',mode,'--run-frames','600','--dump-report',str(state),'--report-sections','meta,watched_memory','--watch-fields','preview']
                            for n in range(0,count,16): cmd+=['--watch-window',f'r{n}:{0xC600+n}:{min(16,count-n)}']
                        else:
                            cmd=[str(emulator),'run',str(rom),'--frames','600','--headless','--snapshot',str(state)]
                        run=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=120)
                        (folder/(mode+'-run.txt')).write_bytes(run.stdout+run.stderr)
                        actual=[]
                        if run.returncode==0:
                            data=json.loads(state.read_text(encoding='utf-8'))
                            if platform=='gb':
                                watches={w['name']:w['preview_bytes'] for w in data['watched_memory']}
                                raw=sum((watches['r'+str(n)] for n in range(0,count,16)),[])
                            else: raw=data['bus']['ram'][0x600:0x600+count]
                            actual=[raw[n]+256*raw[n+1] for n in range(0,count,2)]
                        passed=actual==expected and run.returncode==0
                        rows.append(dict(common,mode=mode,rom_sha256=sha(rom),run_exit=run.returncode,actual=actual,expected=expected,passed=passed))
                        print(platform,fixture['name'],variant,mode,'PASS' if passed else 'FAIL',[(i,x,y) for i,(x,y) in enumerate(zip(actual,expected)) if x!=y],flush=True)
                report=dict(script_sha256=sha(Path(__file__)),fixtures_sha256=sha(a.fixtures),records=rows,passed=bool(rows) and all(r['passed'] for r in rows))
                (base/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    raise SystemExit(0 if rows and all(r['passed'] for r in rows) else 1)

if __name__=='__main__':main()
