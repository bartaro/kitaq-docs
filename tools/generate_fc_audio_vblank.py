"""Generate NTSC tables inside the reviewed original MIT NMI driver template."""
from pathlib import Path
SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
out=REPOS/'kitaqfc/lib/audio_vblank.c'
code=(SITE/'tools/templates/fc_audio_vblank.c').read_text(encoding='ascii')
assert code.count('{{NTSC_TIMER_TABLES}}')==1
tables=[]
for channel,divisor in [('pulse',16),('triangle',32)]:
    # MIDI 36..107 is C2..B7. Round the NTSC APU divider to an integer timer.
    periods=[max(0,round(1789773/(divisor*(440*2**((note-69)/12)))-1)) for note in range(36,108)]
    for part in ['lo','hi']:
        values=[n&255 if part=='lo' else n>>8 for n in periods]
        tables.append('__prg_rom const u8 nav_'+channel+'_'+part+'[72]={'+','.join(map(str,values))+'};')
out.write_bytes(code.replace('{{NTSC_TIMER_TABLES}}','\n'.join(tables)).encode('ascii'))
print(out)
