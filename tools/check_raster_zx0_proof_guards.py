"""Verify that stale or incomplete proof cannot authorize documentation rendering.

Mutation fixtures are supplied through mocked reads; real evidence is untouched.
"""
from pathlib import Path
from unittest.mock import patch
import copy, json
import api_contracts
import api_raster_wave_proofs as wave
import api_zx0_proofs as zx0

SITE = Path(__file__).resolve().parents[1]
PRIVATE = SITE.parents[1] / 'publish/library_docs_20260914/fc-effects'
contracts = api_contracts.load()[2]
assert len(wave.verified_examples(contracts)) == 6
assert len(zx0.verified_examples(contracts)) == 6
read_text = Path.read_text
results = []

def reject(name, verifier, relative, mutate, private=False):
    target = (PRIVATE if private else SITE) / relative
    original = json.loads(read_text(target, encoding='utf-8'))
    damaged = copy.deepcopy(original)
    mutate(damaged)
    def fake_read(path, *args, **kwargs):
        if path == target:
            return json.dumps(damaged)
        return read_text(path, *args, **kwargs)
    caught = False
    with patch.object(Path, 'read_text', fake_read):
        try:
            verifier(contracts)
        except (AssertionError, ValueError, KeyError):
            caught = True
    assert caught, 'Invalid evidence accepted: ' + name
    results.append(dict(name=name, rejected=True))

edge = 'verification/api-raster-wave/state/results.json'
visual = 'verification/api-raster-wave/results.json'
reject('wave-current-emulator-required', wave.verified_examples, edge, lambda d: d.update(emulator_sha256='stale'))
reject('wave-state-checker-required', wave.verified_examples, edge, lambda d: d.update(script_sha256='stale'))
reject('wave-all-variants-required', wave.verified_examples, edge, lambda d: d['records'].pop())
reject('wave-duplicate-variant-rejected', wave.verified_examples, edge, lambda d: d['records'].__setitem__(1, copy.deepcopy(d['records'][0])))
reject('wave-exact-result-required', wave.verified_examples, edge, lambda d: d['records'][0]['actual'].__setitem__(0, 99))
reject('wave-current-edge-rom-required', wave.verified_examples, edge, lambda d: d['records'][0].update(rom_sha256='stale'))
reject('wave-current-demo-rom-required', wave.verified_examples, visual, lambda d: d.update(rom_sha256='stale'))
reject('wave-current-title-rom-required', wave.verified_examples, visual, lambda d: d.update(title_rom_sha256='stale'))
target = 'zx0/targets/results.json'
reject('zx0-duplicate-target-rejected', zx0.verified_examples, target, lambda d: d['cases'].__setitem__(1, copy.deepcopy(d['cases'][0])), True)
reject('zx0-exact-target-result-required', zx0.verified_examples, target, lambda d: d['cases'][0]['result'].__setitem__(0, 99), True)
reject('zx0-target-output-required', zx0.verified_examples, target, lambda d: d['cases'][0].update(output_sha256='invalid'), True)
reject('zx0-current-compiler-required', zx0.verified_examples, target, lambda d: d['cases'][0].update(compiler_sha256='stale'), True)
reject('zx0-duplicate-edge-rejected', zx0.verified_examples, 'zx0/edges/results.json', lambda d: d['cases'].__setitem__(1, copy.deepcopy(d['cases'][0])), True)
reject('zx0-exact-vram-result-required', zx0.verified_examples, 'zx0/vram/results.json', lambda d: d['cases'][0]['actual'].__setitem__(0, 99), True)
reject('zx0-host-reference-required', zx0.verified_examples, 'zx0/host-results.json', lambda d: d['reference_sha256'].update({'zx0.exe': 'stale'}), True)
reject('zx0-host-input-required', zx0.verified_examples, 'zx0/host-results.json', lambda d: d['cases'][0].update(input_sha256='stale'), True)
reject('zx0-unique-host-boundaries-required', zx0.verified_examples, 'zx0/host-edges/results.json', lambda d: d['cases'].__setitem__(1, copy.deepcopy(d['cases'][0])), True)
report = dict(passed=True, valid_families=2, rejected=len(results), records=results)
(SITE / 'verification/api-raster-wave/proof-guards.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('PASS: 2 current proof families accepted;', len(results), 'stale/incomplete fixtures rejected')
