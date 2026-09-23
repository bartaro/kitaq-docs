"""Bind each sound lesson to current source, ROM, screenshot and PCM evidence."""
from pathlib import Path
import hashlib,json
from api_physics_proofs import verify_row
SITE=Path(__file__).resolve().parents[1];SOURCE=SITE/'tools/api_descriptions';FOLDER=SITE/'verification/api-sound'
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def verified_examples(contracts):
    selected={k:v for k,v in contracts.items() if v['review']=='sound-source-20260916'}
    if not selected:return {}
    if len(selected)!=82:raise ValueError('Sound requires 82 individually reviewed APIs')
    routes=read(FOLDER/'channel-routes/results.json')
    if routes['script_sha256']!=sha(SITE/'tools/check_sound_channel_routes.py') or not routes['passed']:
        raise ValueError('Channel-routing checks are stale or failed')
    expected_routes={(d,c,m) for d in ['direct','stream','vblank-direct','vblank-queue'] for c in [1,2,3,4] for m in ['dmg','cgb']}
    if len(routes['records'])!=32 or {(r['driver'],r['channel'],r['mode']) for r in routes['records']}!=expected_routes:
        raise ValueError('All four channels require both hardware models and all four playback paths')
    for row in routes['records']:
        if not row['passed'] or row['registers'][0]!=(1<<(row['channel']-1)) or row['registers'][1]!=0x5A or row['registers'][4]!=0 or row['done']!=[165]:
            raise ValueError('Channel activation, routing or stop mismatch')
        side=0 if row['channel']%2 else 1;other=1-side
        if len(row['active'])!=2 or len(row['silent'])!=2 or row['active'][side]['ac_rms']<=100:
            raise ValueError('Missing active-channel PCM')
        quiet=row['active'][other]['ac_rms']<5 or (row['off_side_monotonic_dc_tail'] and row['active'][other]['positive_crossings']==0)
        if not quiet or any(m['ac_rms']>=5 for m in row['silent']):
            raise ValueError('Channel routing or stop PCM mismatch')
        for key in ['source','rom','image','audio']:
            if sha(SITE/row[key])!=row[key+'_sha256']:raise ValueError('Channel evidence changed: '+row[key])
        for path,digest in row['input_sha256'].items():
            if sha((REPOS if path.startswith('kitaqgb/') else SITE)/path)!=digest:raise ValueError('Channel input changed: '+path)
        if row['compiler_sha256']!=sha(REPOS/'kitaqgb/kitaqgb.exe') or row['emulator_sha256']!=sha(REPOS/'kokura/kokura-cli.exe'):
            raise ValueError('Channel execution tool changed')
    for path,digest in read(SOURCE/'sound_review_sources.json')['source_sha256'].items():
        if sha(REPOS/path)!=digest:raise ValueError('Sound reviewed source changed: '+path)
    for name,script,count in [('alignment/current-results.json','check_sound_alignment.py',4),('midi/results.json','check_sound_midi_matrix.py',2)]:
        state=read(FOLDER/'state'/name)
        if len(state['records'])!=count or not all(r['passed'] for r in state['records']):raise ValueError('Sound compiler checks incomplete')
        if state['compiler_sha256']!=sha(REPOS/'kitaqfc/kitaqfc.exe') or state['emulator_sha256']!=sha(REPOS/'kurosaki/kurosaki.exe') or state['script_sha256']!=sha(SITE/'tools'/script):raise ValueError('Sound compiler check inputs changed')
        if name.startswith('alignment/'):
            matrix={(mapper,zp) for mapper in ['nrom','uxrom'] for zp in ['--no-zp-alloc','--zp-alloc']}
            if {(r['mapper'],r['zp']) for r in state['records']}!=matrix:raise ValueError('Alignment variants missing or duplicated')
        else:
            if {r['flag'] for r in state['records']}!={'--no-zp-alloc','--zp-alloc'}:raise ValueError('MIDI variants missing or duplicated')
            if sha(SITE/state['source'])!=state['source_sha256']:raise ValueError('MIDI matrix source changed')
        for row in state['records']:
            if sha(SITE/row['rom'])!=row['rom_sha256']:raise ValueError('Sound compiler check ROM changed')
            if name.startswith('alignment/'):
                if sha(SITE/row['source'])!=row['source_sha256']:raise ValueError('Alignment source changed')
                expected=[]
                for i in range(6):expected.extend([1,i*19,(i*19+16)&255,1])
                expected.append(0xA5)
                if row['actual']!=expected or row['expected']!=expected:raise ValueError('Aligned array contents or placement mismatch')
            else:
                expected=[126,194,5,178,7,100,146,69,96,130,69,0,248,250,251,252]
                if row['values']!=expected or row['expected']!=expected or len(row['cells'])!=144 or set(row['cells'])!={57} or len(row['gaps'])!=15 or min(row['gaps'])<57 or row['receive']!=[81]+[57]*7:
                    raise ValueError('MIDI bytes or instruction timing mismatch')
    report=read(FOLDER/'results.json');specs=read(SOURCE/'sound_examples.json')
    if report['script_sha256']!=sha(SITE/'tools/check_sound_examples.py'):raise ValueError('Sound checker changed')
    expected={(s['source'],mode) for s in specs for mode in s['modes']}
    rows=report['records']
    if len(rows)!=len(expected) or {(r['source'],r['mode']) for r in rows}!=expected:raise ValueError('Incomplete sound execution matrix')
    for row in rows:
        verify_row(row)
        if sha(SITE/row['audio'])!=row['audio_sha256']:raise ValueError('Captured sound changed')
        spec=next(s for s in specs if s['source']==row['source'])
        if row['expected']!=spec['expected']+[0]*(127-len(spec['expected']))+[0xA5]:raise ValueError('Sound state expectation changed')
        if len(row['segments'])!=len(spec['segments']):raise ValueError('Sound segments missing')
        for got,want in zip(row['segments'],spec['segments']):
            if not got['passed'] or any(got.get(k)!=v for k,v in want.items()):raise ValueError('Sound segment failed or changed')
            metrics=got['metrics'];kind=want['kind']
            if not metrics or any(m['frames']<=0 for m in metrics):raise ValueError('Empty PCM observation')
            if kind=='silent':ok=all(m['peak']<=want.get('max_peak',0) for m in metrics)
            elif kind=='tone':ok=all(m['ac_rms']>100 for m in metrics)
            else:
                side=0 if kind=='left' else 1;other=1-side
                ok=len(metrics)==2 and metrics[side]['ac_rms']>100 and metrics[other]['difference_rms']<metrics[side]['difference_rms']*0.03 and metrics[other]['positive_crossings']<=2
            if 'hz' in want:ok=ok and abs(metrics[0]['positive_crossings']/(want['end']-want['start'])-want['hz'])<=want.get('tolerance_hz',8)
            if not ok:raise ValueError('PCM metrics do not satisfy the lesson')
        if 'midi_bytes' in spec:
            serial=row.get('serial',{})
            if not serial.get('passed') or serial.get('bytes')!=spec['midi_bytes'] or set(serial.get('tx_bit_cycles',[]))!={57} or serial.get('rx_read_cycles')!=[81]+[57]*7:raise ValueError('MIDI timing or bytes changed')
    return {key:{'api':key.split(':')[1],'kind':'sound','runs':[r for r in rows if r['source']==c['example']['program']]} for key,c in selected.items()}
