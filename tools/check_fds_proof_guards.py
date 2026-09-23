"""Reject incomplete FDS evidence without mistaking ABI fixtures for real disk tests."""
from pathlib import Path
from unittest.mock import patch
import copy,json
import api_contracts
import api_fds_query_proofs as query
import api_fds_file_proofs as fileio
import api_fds_load_proofs as load
SITE=Path(__file__).resolve().parents[1];contracts=api_contracts.load()[2]
assert len(query.verified_examples(contracts))==11
assert len(fileio.verified_examples(contracts))==2
assert len(load.verified_examples(contracts))==7
read_text=Path.read_text;rows=[]
def reject(name,module,relative,mutate):
    target=SITE/'verification'/relative
    data=copy.deepcopy(json.loads(read_text(target,encoding='utf-8')));mutate(data)
    def fake_read(path,*args,**kwargs):return json.dumps(data) if path==target else read_text(path,*args,**kwargs)
    caught=False
    with patch.object(Path,'read_text',fake_read):
        try:module.verified_examples(contracts)
        except (AssertionError,ValueError,KeyError):caught=True
    assert caught,'Invalid FDS evidence accepted: '+name
    rows.append(dict(name=name,rejected=True))
for kind,module in [('query',query),('file',fileio),('load',load)]:
    path='api-fds-'+kind+'/example/results.json'
    reject(kind+'-missing',module,path,lambda d:d['records'].pop())
    reject(kind+'-duplicate',module,path,lambda d:d['records'].__setitem__(1,copy.deepcopy(d['records'][0])))
    reject(kind+'-ROM',module,path,lambda d:d['records'][0].update(rom_sha256='stale'))
    reject(kind+'-pixels',module,path,lambda d:d['records'][0].update(pixel_mismatches=1))
    reject(kind+'-values',module,path,lambda d:d['records'][0]['actual'].__setitem__(0,254))
reject('load-order',load,'api-fds-load/example/results.json',lambda d:d['records'][0].update(load_ids=[0,32]))
path='api-fds-file/state/file_io.json'
reject('file-state-missing',fileio,path,lambda d:d['records'].pop())
reject('file-state-duplicate',fileio,path,lambda d:d['records'].__setitem__(1,copy.deepcopy(d['records'][0])))
reject('file-state-unknown',fileio,path,lambda d:d['records'][0].update(name='unknown-default'))
reject('file-state-compiler',fileio,path,lambda d:d.update(compiler_sha256='stale'))
reject('file-state-fixture',fileio,path,lambda d:d.update(fixture_sha256='stale'))
reject('file-state-load-status',fileio,path,lambda d:d['records'][0]['actual'].__setitem__(0,255))
reject('file-state-save-call',fileio,path,lambda d:d['records'][0].update(save_calls=0))
reject('file-state-ordinal',fileio,path,lambda d:d['records'][0].update(ordinal=73))
(SITE/'verification/api-fds-file/proof-guards.json').write_text(json.dumps(dict(passed=True,apis=20,rejected=len(rows),records=rows),indent=2),encoding='utf-8')
print('PASS: 20 FDS contracts accepted;',len(rows),'invalid fixtures rejected')
