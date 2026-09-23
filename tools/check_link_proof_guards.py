"""Require actual linked results and complete boundary matrices for link cards."""
from pathlib import Path
from unittest.mock import patch
import copy,json
import api_contracts
import api_link_proofs as link
import api_dmg07_proofs as dmg07
SITE=Path(__file__).resolve().parents[1]
contracts=api_contracts.load()[2]
assert len(link.verified_examples(contracts))==37
assert len(dmg07.verified_examples(contracts))==25
read_text=Path.read_text;rows=[]
def reject(name,module,relative,mutate):
    target=SITE/'verification'/relative
    data=copy.deepcopy(json.loads(read_text(target,encoding='utf-8')));mutate(data)
    def fake_read(path,*args,**kwargs):return json.dumps(data) if path==target else read_text(path,*args,**kwargs)
    caught=False
    with patch.object(Path,'read_text',fake_read):
        try:module.verified_examples(contracts)
        except (AssertionError,ValueError,KeyError):caught=True
    assert caught,'Invalid link evidence accepted: '+name
    rows.append(dict(name=name,rejected=True))
for module,stem in [(link,'api-link'),(dmg07,'api-dmg07')]:
    report=stem+'/results.json';edges=stem+'/edge_checks.json'
    reject(stem+'-missing-console',module,report,lambda d:d['records'].pop())
    reject(stem+'-duplicate-console',module,report,lambda d:d['records'].__setitem__(1,copy.deepcopy(d['records'][0])))
    reject(stem+'-current-ROM',module,report,lambda d:d['records'][0].update(rom_sha256='stale'))
    reject(stem+'-linked-data',module,report,lambda d:d['records'][0]['linked_actual'].__setitem__(0,65535))
    reject(stem+'-link-stopped',module,report,lambda d:d['links'][0]['summary'].update(stopped_session='fixture'))
    reject(stem+'-no-exchanges',module,report,lambda d:d['links'][0]['summary'].update(exchange_count=0))
    reject(stem+'-edge-duplicate',module,edges,lambda d:d['records'].__setitem__(1,copy.deepcopy(d['records'][0])))
    reject(stem+'-edge-unknown-group',module,edges,lambda d:d['records'][0].update(group='unverified'))
    reject(stem+'-edge-data',module,edges,lambda d:d['records'][0]['actual'].__setitem__(0,65535))
    reject(stem+'-edge-emulator',module,edges,lambda d:d['records'][0].update(emulator_sha256='stale'))
reject('link4-dynamic-routing',link,'api-link/results.json',lambda d:next(r for r in d['links'] if r['group']=='four')['summary'].update(dynamic_peer_selection_observed=False))
reject('dmg07-color',dmg07,'api-dmg07/results.json',lambda d:next(r for r in d['records'] if r['mode']=='cgb').update(colored_pixels=0))
report=dict(passed=True,valid_families=2,rejected=len(rows),records=rows)
(SITE/'verification/api-link/proof-guards.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PASS: 62 current contracts accepted;',len(rows),'invalid fixtures rejected')
