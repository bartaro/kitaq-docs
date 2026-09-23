"""Reject stale, incomplete or mismatched wireframe/bullet proof documents.

All mutations use mocked JSON reads; recorded runtime evidence stays intact.
"""
from pathlib import Path
from unittest.mock import patch
import copy, json
import api_contracts
import api_wireframe_proofs as gb
import api_fc_wireframe_proofs as fc
import api_fc_danmaku_proofs as bullet

SITE=Path(__file__).resolve().parents[1]
PRIVATE=SITE.parents[1]/'publish/library_docs_20260914/fc-effects'
contracts=api_contracts.load()[2]
for module,count in [(gb,124),(fc,8),(bullet,6)]:
    assert len(module.verified_examples(contracts))==count
read_text=Path.read_text
results=[]
def reject(name,module,relative,mutate,private=False):
    target=(PRIVATE if private else SITE)/relative
    data=copy.deepcopy(json.loads(read_text(target,encoding='utf-8')))
    mutate(data)
    def fake_read(path,*args,**kwargs):
        return json.dumps(data) if path==target else read_text(path,*args,**kwargs)
    caught=False
    with patch.object(Path,'read_text',fake_read):
        try:module.verified_examples(contracts)
        except (AssertionError,ValueError,KeyError):caught=True
    assert caught,'Invalid evidence accepted: '+name
    results.append(dict(name=name,rejected=True))

gbpath='verification/api-wireframe/results.json'
reject('gb-missing-mode',gb,gbpath,lambda d:d['records'].pop())
reject('gb-duplicate-mode',gb,gbpath,lambda d:d['records'].__setitem__(1,copy.deepcopy(d['records'][0])))
reject('gb-stale-compiler',gb,gbpath,lambda d:d['records'][0].update(compiler_sha256='stale'))
reject('gb-pixel-mismatch',gb,gbpath,lambda d:d['records'][0].update(pixel_mismatches=1))
state='verification/api-wireframe-fc/state/results.json'
reject('fc-state-checker',fc,state,lambda d:d.update(script_sha256='stale'))
reject('fc-state-missing-variant',fc,state,lambda d:d['records'].pop())
reject('fc-state-duplicate-variant',fc,state,lambda d:d['records'].__setitem__(1,copy.deepcopy(d['records'][0])))
reject('fc-state-exact-result',fc,state,lambda d:d['records'][0]['actual'].__setitem__(0,99))
reject('fc-state-guard',fc,state,lambda d:d['records'][0]['guards'].__setitem__(0,0))
reject('fc-state-staged-pixels',fc,state,lambda d:d['records'][0].update(pixel_buffer_sha256='wrong'))
reject('fc-state-current-rom',fc,state,lambda d:d['records'][0].update(rom_sha256='stale'))
drawing='wire3d/proofs/results.json'
reject('fc-drawing-missing-case',fc,drawing,lambda d:d.pop(),True)
reject('fc-drawing-duplicate-case',fc,drawing,lambda d:d.__setitem__(1,copy.deepcopy(d[0])),True)
reject('fc-drawing-ppu-safety',fc,drawing,lambda d:d[0].update(unsafe_vram_writes=1),True)
reject('fc-drawing-current-input',fc,drawing,lambda d:d[0]['input_sha256'].update({'manual/latest/tools/check_fc_wireframe.py':'stale'}),True)
visual='verification/api-fc-danmaku/results.json'
reject('bullet-oam',bullet,visual,lambda d:d['records'][0].update(oam_matches_expected=False))
reject('bullet-current-image',bullet,visual,lambda d:d['records'][0].update(image_sha256='stale'))
reject('bullet-state-duplicate-variant',bullet,'danmaku/state/report.json',lambda d:d['records'].__setitem__(1,copy.deepcopy(d['records'][0])),True)
reject('bullet-state-exact-result',bullet,'danmaku/state/report.json',lambda d:d['records'][0]['actual'].__setitem__(0,99),True)
report=dict(passed=True,valid_families=3,rejected=len(results),records=results)
(SITE/'verification/api-wireframe/proof-guards.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PASS: 3 current families accepted;',len(results),'invalid fixtures rejected')
