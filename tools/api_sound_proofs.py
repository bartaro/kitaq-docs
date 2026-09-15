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
    for path,digest in read(SOURCE/'sound_review_sources.json')['source_sha256'].items():
        if sha(REPOS/path)!=digest:raise ValueError('Sound reviewed source changed: '+path)
    for name,script,count in [('alignment/current-results.json','check_sound_alignment.py',4),('midi/results.json','check_sound_midi_matrix.py',2)]:
        state=read(FOLDER/'state'/name)
        if len(state['records'])!=count or not all(r['passed'] for r in state['records']):raise ValueError('Sound compiler checks incomplete')
        if state['compiler_sha256']!=sha(REPOS/'kitaqfc/kitaqfc.exe') or state['emulator_sha256']!=sha(REPOS/'kurosaki/kurosaki.exe') or state['script_sha256']!=sha(SITE/'tools'/script):raise ValueError('Sound compiler check inputs changed')
        for row in state['records']:
            if sha(SITE/row['rom'])!=row['rom_sha256']:raise ValueError('Sound compiler check ROM changed')
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
        if 'midi_bytes' in spec:
            serial=row.get('serial',{})
            if not serial.get('passed') or serial.get('bytes')!=spec['midi_bytes'] or set(serial.get('tx_bit_cycles',[]))!={57} or serial.get('rx_read_cycles')!=[81]+[57]*7:raise ValueError('MIDI timing or bytes changed')
    return {key:{'api':key.split(':')[1],'kind':'sound','runs':[r for r in rows if r['source']==c['example']['program']]} for key,c in selected.items()}
