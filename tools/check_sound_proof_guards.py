"""Reject incomplete or mismatched sound evidence without changing stored proof."""
from pathlib import Path
from unittest.mock import patch
import copy,json
import api_contracts
import api_sound_proofs as sound
SITE=Path(__file__).resolve().parents[1]
contracts=api_contracts.load()[2]
assert len(sound.verified_examples(contracts))==82
read_text=Path.read_text;rows=[]
def reject(name,relative,mutate):
    target=SITE/'verification/api-sound'/relative
    data=copy.deepcopy(json.loads(read_text(target,encoding='utf-8')));mutate(data)
    def fake_read(path,*args,**kwargs):
        return json.dumps(data) if path==target else read_text(path,*args,**kwargs)
    caught=False
    with patch.object(Path,'read_text',fake_read):
        try:sound.verified_examples(contracts)
        except (ValueError,AssertionError,KeyError):caught=True
    assert caught,'Invalid sound evidence accepted: '+name
    rows.append(dict(name=name,rejected=True))
routes='channel-routes/results.json'
reject('all-route-paths-required',routes,lambda d:d['records'].pop())
reject('no-duplicate-route',routes,lambda d:d['records'].__setitem__(1,copy.deepcopy(d['records'][0])))
reject('physical-channel-mask',routes,lambda d:d['records'][0]['registers'].__setitem__(0,8))
reject('stereo-routing',routes,lambda d:d['records'][0]['registers'].__setitem__(1,255))
reject('active-PCM',routes,lambda d:d['records'][0]['active'][0].update(ac_rms=0))
reject('stopped-PCM',routes,lambda d:d['records'][0]['silent'][0].update(ac_rms=1000))
reject('current-route-audio',routes,lambda d:d['records'][0].update(audio_sha256='stale'))
alignment='state/alignment/current-results.json'
reject('alignment-unique-matrix',alignment,lambda d:d['records'].__setitem__(1,copy.deepcopy(d['records'][0])))
reject('alignment-exact-data',alignment,lambda d:d['records'][0]['actual'].__setitem__(1,255))
reject('alignment-source-binding',alignment,lambda d:d['records'][0].update(source_sha256='stale'))
midi='state/midi/results.json'
reject('midi-unique-matrix',midi,lambda d:d['records'].__setitem__(1,copy.deepcopy(d['records'][0])))
reject('midi-exact-byte',midi,lambda d:d['records'][0]['values'].__setitem__(0,0))
reject('midi-transmit-timing',midi,lambda d:d['records'][0]['cells'].__setitem__(0,56))
reject('midi-receive-timing',midi,lambda d:d['records'][0]['receive'].__setitem__(0,57))
reject('midi-source-binding',midi,lambda d:d.update(source_sha256='stale'))
reject('lesson-unique-matrix','results.json',lambda d:d['records'].__setitem__(1,copy.deepcopy(d['records'][0])))
reject('lesson-active-tone','results.json',lambda d:d['records'][0]['segments'][0]['metrics'][0].update(ac_rms=0))
reject('lesson-pitch','results.json',lambda d:d['records'][0]['segments'][0]['metrics'][0].update(positive_crossings=0))
reject('lesson-exact-RAM','results.json',lambda d:d['records'][0]['actual'].__setitem__(0,255))
reject('lesson-current-compiler','results.json',lambda d:d['records'][0].update(compiler_sha256='stale'))
report=dict(passed=True,valid_families=1,rejected=len(rows),records=rows)
(SITE/'verification/api-sound/proof-guards.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PASS: 82 current sound contracts accepted;',len(rows),'invalid fixtures rejected')
