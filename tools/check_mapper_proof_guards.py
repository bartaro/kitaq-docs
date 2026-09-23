"""Ensure mapper descriptions reject stale runs and incomplete board matrices."""
from pathlib import Path
from unittest.mock import patch
import copy,json
import api_contracts
import api_mapper_proofs as mapper
SITE=Path(__file__).resolve().parents[1]
contracts=api_contracts.load()[2]
assert len(mapper.verified_examples(contracts))==14
read_text=Path.read_text;rows=[]
def reject(name,relative,mutate):
    target=SITE/'verification/api-mapper'/relative
    data=copy.deepcopy(json.loads(read_text(target,encoding='utf-8')));mutate(data)
    def fake_read(path,*args,**kwargs):return json.dumps(data) if path==target else read_text(path,*args,**kwargs)
    caught=False
    with patch.object(Path,'read_text',fake_read):
        try:mapper.verified_examples(contracts)
        except (AssertionError,ValueError,KeyError):caught=True
    assert caught,'Invalid mapper evidence accepted: '+name
    rows.append(dict(name=name,rejected=True))
reject('missing-state','state/results.json',lambda d:d['records'].pop())
reject('duplicate-state','state/results.json',lambda d:d['records'].__setitem__(1,copy.deepcopy(d['records'][0])))
reject('unknown-board','state/results.json',lambda d:d['records'][0].update(name='identity-unknown'))
reject('stale-compiler','state/results.json',lambda d:d.update(compiler_sha256='stale'))
reject('state-ROM','state/results.json',lambda d:d['records'][0].update(rom_sha256='stale'))
reject('state-readback','state/results.json',lambda d:d['records'][0]['actual'].__setitem__(0,255))
reject('run-failed','state/results.json',lambda d:d['records'][0].update(run_exit=1))
reject('irq-write','state/results.json',lambda d:next(r for r in d['records'] if r['name']=='irq-intrinsics')['mapper_writes'].__setitem__(1,[0xC000,38]))
reject('missing-visual','example/results.json',lambda d:d['records'].pop())
reject('duplicate-visual','example/results.json',lambda d:d['records'].__setitem__(1,copy.deepcopy(d['records'][0])))
reject('screen-pixels','example/results.json',lambda d:d['records'][0].update(label_pixel_mismatches=1))
reject('visual-ROM','example/results.json',lambda d:d['records'][0].update(rom_sha256='stale'))
report=dict(passed=True,apis=14,rejected=len(rows),records=rows)
(SITE/'verification/api-mapper/proof-guards.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PASS: 14 current contracts accepted;',len(rows),'invalid fixtures rejected')
