"""Reject stale peripheral captures and incomplete input/optimization matrices."""
from pathlib import Path
from unittest.mock import patch
import copy,json
import api_contracts
import api_peripheral_proofs as module
SITE=Path(__file__).resolve().parents[1]
contracts=api_contracts.load()[2];assert len(module.verified_examples(contracts))==13
read_text=Path.read_text;rows=[]
def reject(name,relative,mutate):
    target=SITE/'verification/api-peripheral'/relative
    data=copy.deepcopy(json.loads(read_text(target,encoding='utf-8')));mutate(data)
    def fake_read(path,*args,**kwargs):return json.dumps(data) if path==target else read_text(path,*args,**kwargs)
    caught=False
    with patch.object(Path,'read_text',fake_read):
        try:module.verified_examples(contracts)
        except (AssertionError,ValueError,KeyError):caught=True
    assert caught,'Invalid peripheral evidence accepted: '+name
    rows.append(dict(name=name,rejected=True))
for kind in ['keyboard','masks']:
    path='state/'+kind+'.json'
    reject(kind+'-missing',path,lambda d:d['records'].pop())
    reject(kind+'-duplicate',path,lambda d:d['records'].__setitem__(1,copy.deepcopy(d['records'][0])))
    reject(kind+'-compiler',path,lambda d:d.update(compiler_sha256='stale'))
reject('keyboard-row','state/keyboard.json',lambda d:d['records'][0]['selected']['2'][0].__setitem__(0,9))
reject('keyboard-delay','state/keyboard.json',lambda d:d['records'][0]['read_delays'].__setitem__(0,1))
reject('mask-scope','state/masks.json',lambda d:d['records'][0]['patches'][0].update(fixture_address=0x800))
reject('mask-input','state/masks.json',lambda d:d['records'][0]['inputs'].__setitem__(0,0))
reject('mask-original','state/masks.json',lambda d:d['records'][0].update(original_rom_sha256=d['records'][0]['substituted_rom_sha256']))
reject('visual-missing','example/results.json',lambda d:d['records'].pop())
reject('visual-pixels','example/results.json',lambda d:d['records'][0].update(pixel_mismatches=1))
reject('visual-port','example/results.json',lambda d:d['records'][0]['port_writes'].__setitem__(0,0))
reject('visual-ROM','example/results.json',lambda d:d['records'][0].update(rom_sha256='stale'))
(SITE/'verification/api-peripheral/proof-guards.json').write_text(json.dumps(dict(passed=True,apis=13,rejected=len(rows),records=rows),indent=2),encoding='utf-8')
print('PASS: 13 peripheral contracts accepted;',len(rows),'invalid fixtures rejected')
