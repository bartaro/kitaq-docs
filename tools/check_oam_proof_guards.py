"""Ensure stale or incomplete OAM evidence is rejected without editing evidence files."""
from pathlib import Path
from unittest.mock import patch
import copy,json
from api_oam_current_proofs import verify_oam_inputs

site=Path(__file__).resolve().parents[1];source=site/'tools/api_descriptions'
original_loads=json.loads
count=0
for library in [False,True]:
    family='api-oam-library' if library else 'api-fc-oam'
    review='oam-library-source-20260915' if library else 'fc-oam-source-20260915'
    contracts={'test':{'review':review}}
    verify_oam_inputs(site,source,contracts,library)
    state=(site/'verification'/family/'state_checks.json').read_text(encoding='utf-8')
    runs=(site/'verification'/family/'results.json').read_text(encoding='utf-8')
    mutations=[
        (state,lambda d:d['cases'][0].update(compiler_sha256='0'*64),'stale state executable'),
        (state,lambda d:d['cases'].pop(),'incomplete state matrix'),
        (state,lambda d:d['cases'][0]['shadow'].__setitem__(0,d['cases'][0]['shadow'][0]^1),'shadow bytes differ'),
        (state,lambda d:d.update(script_sha256='0'*64),'state checker changed'),
        (state,lambda d:d['cases'][0].update(source_sha256='0'*64),'state fixture changed'),
        (runs,lambda d:d['records'][0].update(emulator_sha256='0'*64),'stale teaching executable'),
        (runs,lambda d:d['records'][0].update(rom_sha256='0'*64),'teaching ROM changed'),
    ]
    for target,mutate,expected_error in mutations:
        changed=copy.deepcopy(original_loads(target));mutate(changed)
        def decoded(text,*args,**kwargs):
            return copy.deepcopy(changed) if text==target else original_loads(text,*args,**kwargs)
        with patch('api_oam_current_proofs.json.loads',side_effect=decoded):
            try:verify_oam_inputs(site,source,contracts,library)
            except ValueError as error:assert expected_error in str(error),str(error)
            else:raise AssertionError('Invalid evidence accepted: '+expected_error)
        count+=1
print('PASS: two current OAM evidence sets accepted;',count,'stale/incomplete variants rejected')
