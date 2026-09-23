"""Reject incomplete optical timing and sprite-zero execution evidence."""
from pathlib import Path
from unittest.mock import patch
import copy,json
import api_contracts
import api_rob_proofs as rob
import api_sprite0_proofs as sprite0
SITE=Path(__file__).resolve().parents[1]
contracts=api_contracts.load()[2]
assert len(rob.verified_examples(contracts))==3
assert len(sprite0.verified_examples(contracts))==3
read_text=Path.read_text;rows=[]
def reject(name,module,relative,mutate):
    target=SITE/'verification'/relative
    data=copy.deepcopy(json.loads(read_text(target,encoding='utf-8')));mutate(data)
    def fake_read(path,*args,**kwargs):return json.dumps(data) if path==target else read_text(path,*args,**kwargs)
    caught=False
    with patch.object(Path,'read_text',fake_read):
        try:module.verified_examples(contracts)
        except (AssertionError,ValueError,KeyError):caught=True
    assert caught,'Invalid timing evidence accepted: '+name
    rows.append(dict(name=name,rejected=True))
state='api-rob/state/results.json';visual='api-rob/example/results.json'
reject('rob-missing-case',rob,state,lambda d:d['records'].pop())
reject('rob-duplicate-case',rob,state,lambda d:d['records'].__setitem__(1,copy.deepcopy(d['records'][0])))
reject('rob-source-binding',rob,state,lambda d:d.update(codegen_sha256='stale'))
reject('rob-trace-failed',rob,state,lambda d:d['records'][0].update(trace_exit=1))
reject('rob-frame-missing',rob,state,lambda d:d['records'][0].update(write_frames=[]))
reject('rob-frame-gap',rob,state,lambda d:next(r for r in d['records'] if r['name']=='pulse-2-4')['write_frames'].__setitem__(1,999))
reject('rob-masks',rob,state,lambda d:next(r for r in d['records'] if r['name']=='byte-128')['mask_writes'].__setitem__(0,0))
reject('rob-ROM',rob,state,lambda d:d['records'][0].update(rom_sha256='stale'))
reject('rob-diagram',rob,visual,lambda d:d['record'].update(diagram_pixels=1))
reject('rob-pixels',rob,visual,lambda d:d['record'].update(pixel_mismatches=1))
state='api-sprite0/state/results.json';visual='api-sprite0/example/results.json'
reject('sprite0-missing-case',sprite0,state,lambda d:d['records'].pop())
reject('sprite0-duplicate-case',sprite0,state,lambda d:d['records'].__setitem__(1,copy.deepcopy(d['records'][0])))
reject('sprite0-hidden-returned',sprite0,state,lambda d:next(r for r in d['records'] if r['name']=='hidden').update(completed=116))
reject('sprite0-vertical-image',sprite0,state,lambda d:next(r for r in d['records'] if r['name']=='vertical-latch').update(reference_image_sha256='stale'))
reject('sprite0-missing-visual',sprite0,visual,lambda d:d['records'].pop())
reject('sprite0-color',sprite0,visual,lambda d:d['records'][0].update(pixel_mismatches=1))
reject('sprite0-progress',sprite0,visual,lambda d:d['records'][0]['observations'][1].update(completed=116))
reject('sprite0-hit-evidence',sprite0,visual,lambda d:d['records'][0]['observations'][1].update(hit_pixels=0))
reject('sprite0-ROM',sprite0,visual,lambda d:d['records'][0].update(rom_sha256='stale'))
report=dict(passed=True,apis=6,rejected=len(rows),records=rows)
(SITE/'verification/api-rob/proof-guards.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PASS: six timing contracts accepted;',len(rows),'invalid fixtures rejected')
