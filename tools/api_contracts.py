"""Render reviewed per-API contracts without guessing meaning from function names.

Each contract names authored multilingual messages and an exact platform/API key.
Only reviewed entries are replaced while authoring is in progress. The coverage
report exposes every outstanding entry; --require-complete rejects partial work.
"""
import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from publication_languages import ORDER, ACTIVE_LANGUAGES, authored_translations

SITE = Path(__file__).resolve().parents[1]
SOURCE = SITE / 'tools/api_descriptions'


def load():
    messages = {}
    for path in sorted(SOURCE.glob('*texts.json')):
        for key, value in json.loads(path.read_text(encoding='utf-8')).items():
            if key in messages:
                raise ValueError('Duplicate authored message: ' + key)
            messages[key] = authored_translations(value, key)
    ui = json.loads((SOURCE / 'ui.json').read_text(encoding='utf-8'))
    contracts = {}
    for path in sorted(SOURCE.glob('*contracts.json')):
        for key, value in json.loads(path.read_text(encoding='utf-8')).items():
            if key in contracts:
                raise ValueError('Duplicate API contract: ' + key)
            contracts[key] = value
    return messages, ui, contracts


def inline(text):
    return ''.join('<code>' + html.escape(part[1:-1]) + '</code>' if part.startswith('`')
                   else html.escape(part) for part in re.split(r'(`[^`]+`)', text))


def render(record, contract, language, messages, ui):
    index = ORDER.index(language)
    def label(key): return html.escape(ui[key][index])
    def prose(key): return inline((messages if key in messages else ui)[key][index])
    def paragraphs(keys): return ''.join('<p>' + prose(key) + '</p>' for key in keys)
    def code(text, kind='c'):
        return '<div class="codebox"><span class="lang">' + kind + '</span><button class="copy" type="button">' + label('copy') + '</button><pre><code>' + html.escape(text.strip()) + '</code></pre></div>'
    def images(example):
        result = []
        for shot in example.get('verified_images', []):
            caption = shot['caption']
            result.append('<figure class="example-result"><img class="screen" loading="lazy" src="' + prefix + html.escape(shot['image'], quote=True) + '" alt="' + html.escape(name + ': ' + caption, quote=True) + '"><figcaption>' + html.escape(caption) + '</figcaption></figure>')
        return ''.join(result)
    prefix = '' if language == 'ja' else '../'
    name = record['name']
    out = ['<details class="api searchable" id="api-' + name + '" data-api-contract="' + contract['review'] + '"><summary><code>' + html.escape(name) + '</code></summary>']
    out += [paragraphs(contract['purpose']), '<h4>' + label('syntax') + '</h4>', code(contract.get('syntax', record['signature']))]
    if record.get('arity_only'):
        out.append(paragraphs(['syntax_names']))
    if contract.get('args'):
        out.append('<h4>' + label('parameters') + '</h4><dl class="api-parameters">')
        for arg, keys in contract['args']:
            out.append('<dt><code>' + html.escape(arg) + '</code></dt><dd>' + paragraphs(keys) + '</dd>')
        out.append('</dl>')
    out += ['<h4>' + label('returns') + '</h4>', paragraphs(contract['returns'])]
    if contract.get('notes'):
        out += ['<h4>' + label('notes') + '</h4>', paragraphs(contract['notes'])]
    for reference in contract.get('references', []):
        out.append('<p><a href="' + html.escape(reference['url'], quote=True) + '">' + html.escape(reference['title']) + '</a></p>')
    example = contract['example']
    out += ['<h4>' + label('example') + '</h4>', code(example['code'])]
    if not example.get('standalone'):
        out.append(paragraphs(['fragment']))
    if example.get('expected'):
        out += ['<h4>' + label('expected') + '</h4>', paragraphs(example['expected'])]
    if example.get('image'):
        diagram = example['image']
        caption = messages['tile_image_layout'][index].format(x=diagram['x'],y=diagram['y'],px=diagram['x']*8,py=diagram['y']*8)
        out += ['<p>' + inline(caption) + '</p>', code('\n'.join(diagram['rows']), 'text')]
    out.append(images(example))
    if example.get('program'):
        out.append('<p><a href="' + prefix + example['program'] + '">' + label('download') + '</a></p>')
    if example.get('build'):
        out += ['<h4>' + label('build') + '</h4>', code(example['build'], 'powershell')]
    for additional in example.get('additional', []):
        out += ['<h4>' + label('example') + '</h4>', code(additional['code']), paragraphs(['fragment'])]
        out += ['<h4>' + label('expected') + '</h4>', paragraphs(additional['expected'])]
        out.append(images(additional))
        out.append('<p><a href="' + prefix + additional['program'] + '">' + label('download') + '</a></p>')
        out += ['<h4>' + label('build') + '</h4>', code(additional['build'], 'powershell')]
    out.append('<details class="api-source"><summary>' + label('implementation') + '</summary>')
    out.append('<p class="source">' + html.escape(record['path']) + ':' + str(record['line']) + '</p>')
    if record.get('comment'):
        comment = '\n'.join(line.rstrip() for line in record['comment'].splitlines())
        out += ['<div class="original"><b>' + label('original') + '</b><pre>' + html.escape(comment) + '</pre></div>']
    if record.get('definition'):
        source = record['definition']
        out += ['<p class="source">' + html.escape(source['path']) + ':' + str(source['line']) + '</p>', code(source['body'])]
    elif record.get('implementation_excerpt'):
        if record.get('implementation_source'):
            origin = record['implementation_source']
            out.append('<p class="source">'+html.escape(origin['path'])+':'+str(origin['line'])+'</p>')
        out.append(code(record['implementation_excerpt'], 'c' if record.get('kind') == 'macro' else 'csharp'))
    if record.get('alternative_definition'):
        source = record['alternative_definition']
        out += ['<p class="source">' + html.escape(source['path']) + ':' + str(source['line']) + '</p>', code(source['body'])]
    out.append('</details></details>')
    return ''.join(out)


class CardRanges(HTMLParser):
    """Find complete API details blocks, respecting nested source-code details."""
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.offsets = [0]
        for line in source.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1] + len(line))
        self.depth = 0
        self.current = None
        self.ranges = []
        self.feed(source)

    def position(self):
        line, column = self.getpos()
        return self.offsets[line - 1] + column

    def handle_starttag(self, tag, attrs):
        if tag != 'details': return
        attrs = dict(attrs)
        if self.current is None and 'api' in attrs.get('class', '').split():
            self.current = (attrs['id'][4:], self.position())
            self.depth = 0
        if self.current is not None: self.depth += 1

    def handle_endtag(self, tag):
        if tag == 'details' and self.current is not None:
            self.depth -= 1
            if self.depth == 0:
                self.ranges.append((*self.current, self.position() + len('</details>')))
                self.current = None


def publish(language, require_complete=False):
    if language not in ACTIVE_LANGUAGES:
        raise ValueError('Updates are paused for this edition: ' + language)
    messages, ui, contracts = load()
    folder = SITE if language == 'ja' else SITE / language
    proofs = verified_tile_examples(contracts)
    proofs.update(verified_entity_examples(contracts))
    proofs.update(verified_input_examples(contracts))
    proofs.update(verified_padrepeat_examples(contracts))
    proofs.update(verified_expansion_examples(contracts))
    proofs.update(verified_vram_examples(contracts))
    proofs.update(verified_vram_examples(contracts, 'vram-memory', {'gb': {'dmg', 'cgb'}}))
    proofs.update(verified_vram_examples(contracts, 'vramq', {'fc': {'nrom'}}))
    proofs.update(verified_vram_examples(contracts, 'vram-macros', {'fc': {'nrom'}}))
    proofs.update(verified_runtime_queue_examples(contracts))
    proofs.update(verified_runtime_ppu_examples(contracts))
    proofs.update(verified_ppu_declaration_examples(contracts))
    proofs.update(verified_ppu_intrinsic_examples(contracts))
    proofs.update(verified_interrupt_intrinsic_examples(contracts))
    proofs.update(verified_memory_intrinsic_examples(contracts))
    proofs.update(verified_bit_intrinsic_examples(contracts))
    proofs.update(verified_rng_examples(contracts))
    proofs.update(verified_flags_examples(contracts))
    proofs.update(verified_rle_examples(contracts))
    proofs.update(verified_cgb_palette_examples(contracts))
    proofs.update(verified_cgb_dma_wram_examples(contracts))
    proofs.update(verified_asset_examples(contracts))
    proofs.update(verified_bank_examples(contracts))
    proofs.update(verified_sprite_examples(contracts))
    proofs.update(verified_oam_examples(contracts))
    proofs.update(verified_fc_oam_examples(contracts))
    proofs.update(verified_oam_library_examples(contracts))
    attach_verified_images(contracts, proofs)
    coverage = []
    for platform, volumes in [('gb', ('kitaqgb', 'gb-library')), ('fc', ('kitaqfc', 'fc-library'))]:
        records = json.loads((SITE / 'reference' / (platform + '-api.json')).read_text(encoding='utf-8'))['records']
        by_name = {r['name']: r for r in records}
        missing = [platform + ':' + r['name'] for r in records if platform + ':' + r['name'] not in contracts]
        if require_complete and missing:
            raise ValueError('Unreviewed APIs remain: ' + str(len(missing)))
        coverage += missing
        for volume in volumes:
            path = folder / (volume + '.html')
            original = path.read_bytes()
            text = original.decode('utf-8').replace('\r\n', '\n')
            edits = []
            for name, start, end in CardRanges(text).ranges:
                key = platform + ':' + name
                if key not in contracts: continue
                record = by_name[name]
                fingerprint = hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
                if contracts[key].get('record_sha256') != fingerprint:
                    raise ValueError('Source inventory changed; review this API again: ' + key)
                edits.append((start, end, render(by_name[name], contracts[key], language, messages, ui)))
            for start, end, replacement in reversed(edits):
                text = text[:start] + replacement + text[end:]
            text = render_modules(text, platform, language, messages)
            path.write_text(text, encoding='utf-8', newline='\r\n' if b'\r\n' in original else '\n')
    publish_verification(language, contracts, proofs, messages, ui)
    from public_presentation import normalize
    normalize(language)
    return {'active_languages': ACTIVE_LANGUAGES, 'reviewed': len(contracts), 'remaining': len(coverage), 'missing': coverage}


def render_modules(text, platform, language, messages):
    """Place reviewed library introductions directly below their module headings."""
    text = re.sub(r'<!-- api-module:start -->.*?<!-- api-module:end -->','',text,flags=re.S)
    index = ORDER.index(language)
    for path in sorted(SOURCE.glob('*modules.json')):
        for key, paragraphs in json.loads(path.read_text(encoding='utf-8')).items():
            owner, module = key.split(':')
            if owner != platform: continue
            pattern = r'(<h3\b[^>]*id="module-' + re.escape(module) + r'"[^>]*>.*?</h3>)'
            block = '<!-- api-module:start --><div data-module-contract="' + html.escape(path.stem.removesuffix('_modules'), quote=True) + '-source-20260915">'
            block += ''.join('<p>'+inline(messages[item][index])+'</p>' for item in paragraphs)
            block += '</div><!-- api-module:end -->'
            text = re.sub(pattern,lambda m:m[1]+block,text,count=1,flags=re.S)
    return text


def verified_input_examples(contracts):
    path = SITE/'verification/api-input/results.json'
    if not path.exists(): return {}
    runs = json.loads(path.read_text(encoding='utf-8'))['records']
    if len(runs)!=7 or not all(r['passed'] for r in runs): return {}
    verified = {}
    for key, contract in contracts.items():
        if contract['review'] != 'input-source-20260915': continue
        program = contract['example']['program']
        selected = [r for r in runs if r['program']==program]
        if len(selected)!=(2 if key.startswith('gb:') else 1):
            raise ValueError('Missing input run: '+key)
        for run in selected:
            for file, expected in [(SITE/program,run['source_sha256']),(SITE/run['image'],run['image_sha256'])]:
                if hashlib.sha256(file.read_bytes()).hexdigest()!=expected:
                    raise ValueError('Input evidence changed: '+str(file))
        verified[key] = {'api':key.split(':')[1],'kind':'input','runs':selected}
    return verified


def verified_padrepeat_examples(contracts):
    path = SITE/'verification/api-pad-repeat/results.json'
    if not path.exists(): return {}
    runs = json.loads(path.read_text(encoding='utf-8'))['records']
    if {r['mode'] for r in runs}!={'dmg','cgb'} or not all(r['passed'] for r in runs): return {}
    verified = {}
    for key,contract in contracts.items():
        if contract['review']!='padrepeat-source-20260915': continue
        for run in runs:
            if run['source']!=contract['example']['program']:
                raise ValueError('Repeat example source mismatch: '+key)
            for file,expected in [(run['source'],run['source_sha256']),(run['image'],run['image_sha256'])]:
                if hashlib.sha256((SITE/file).read_bytes()).hexdigest()!=expected:
                    raise ValueError('Repeat example evidence changed: '+file)
        verified[key]={'api':key.split(':')[1],'kind':'pad-repeat','runs':runs}
    return verified


def verified_expansion_examples(contracts):
    path = SITE/'verification/api-expansion-input/results.json'
    if not path.exists(): return {}
    run = json.loads(path.read_text(encoding='utf-8'))
    if not run['passed']: return {}
    verified = {}
    for key,contract in contracts.items():
        if contract['review']!='expansion-source-20260915': continue
        if run['source']!=contract['example']['program']:
            raise ValueError('Expansion example source mismatch: '+key)
        for file,expected in [(run['source'],run['source_sha256']),(run['image'],run['image_sha256'])]:
            if hashlib.sha256((SITE/file).read_bytes()).hexdigest()!=expected:
                raise ValueError('Expansion example evidence changed: '+file)
        verified[key]={'api':key.split(':')[1],'kind':'expansion-input','runs':[run]}
    return verified


def verified_vram_examples(contracts, family='vram', modes=None):
    """Attach only complete, unchanged GB/FC queue geometry evidence."""
    modes = modes or {'gb': {'dmg', 'cgb'}, 'fc': {'nrom'}}
    path = SITE/('verification/api-'+family+'/results.json')
    if not path.exists(): return {}
    runs = json.loads(path.read_text(encoding='utf-8'))['records']
    if len(runs)!=sum(len(values) for values in modes.values()) or not all(r['passed'] for r in runs): return {}
    if family in ['vram-macros','runtime-queue','runtime-ppu','ppu-declarations','ppu-intrinsics']:
        repos=SITE.parents[1]/'publish/github_20260912'
        if not repos.exists():repos=SITE.parent
        for run in runs:
            if run['frames']!=240 or any(run[key]!=0 for key in ['label_pixel_mismatches','geometry_pixel_mismatches','geometry_color_mismatches']):return {}
            for name,expected in run['library_sha256'].items():
                source=repos/'kitaqfc/lib'/name
                if source.exists() and hashlib.sha256(source.read_bytes()).hexdigest()!=expected:raise ValueError('VRAM macro source changed: '+name)
    verified = {}
    for key,contract in contracts.items():
        if contract['review']!=family+'-source-20260915': continue
        selected = [r for r in runs if r['platform']==key.split(':')[0]]
        if {r['mode'] for r in selected} != modes[key.split(':')[0]]:
            raise ValueError('Missing VRAM hardware mode: '+key)
        for run in selected:
            if run['source']!=contract['example']['program']:
                raise ValueError('VRAM example source mismatch: '+key)
            files = {run['source']:run['source_sha256'],run['image']:run['image_sha256']}
            files.update(run['support_sha256'])
            for file,expected in files.items():
                if hashlib.sha256((SITE/file).read_bytes()).hexdigest()!=expected:
                    raise ValueError('VRAM example evidence changed: '+file)
        verified[key]={'api':key.split(':')[1],'kind':family,'runs':selected}
    return verified


def verified_runtime_queue_examples(contracts):
    """Bind copied-payload queue images to boundary, memory and NMI state tests."""
    results=verified_vram_examples(contracts,'runtime-queue',{'fc':{'nrom'}})
    path=SITE/'verification/api-runtime-queue/state_checks.json'
    if not path.exists():return {}
    state=json.loads(path.read_text(encoding='utf-8'))
    if len(state['cases'])!=13 or not all(r['passed'] and r['result']==r['expected_result'] and r['vram']==r['expected_vram'] and r['data_writes']==r['expected_writes'] for r in state['cases']):return {}
    repos=SITE.parents[1]/'publish/github_20260912'
    if not repos.exists():repos=SITE.parent
    for name,expected in state['library_sha256'].items():
        source=repos/'kitaqfc/lib'/name
        if source.exists() and hashlib.sha256(source.read_bytes()).hexdigest()!=expected:raise ValueError('Runtime queue state-test source changed: '+name)
    script=repos/'kitaqfc/scripts/test-runtime-queue.py'
    if script.exists() and hashlib.sha256(script.read_bytes()).hexdigest()!=state['script_sha256']:raise ValueError('Runtime queue state-test script changed')
    for result in results.values():
        if not all(r['compiler_sha256']==state['compiler_sha256'] and r['ppu_writes_while_rendering']==0 and r['geometry_pixels_checked']==18432 for r in result['runs']):return {}
        result.update(state_path=path.relative_to(SITE).as_posix(),state_count=13)
    return results


def verified_runtime_ppu_examples(contracts):
    """Require real state/pixel evidence for each separately linked PPU API form."""
    folder=SITE/'verification/api-runtime-ppu'
    if not (folder/'results.json').exists() or not (folder/'state_checks.json').exists():return {}
    runs=json.loads((folder/'results.json').read_text(encoding='utf-8'))['records']
    state=json.loads((folder/'state_checks.json').read_text(encoding='utf-8'))
    if len(runs)!=2 or {r['mode'] for r in runs}!={'runtime','pair'}:return {}
    if len(state['cases'])!=14 or not all(r['passed'] and r['result']==r['expected_result'] and r['vram']==r['expected_vram'] and r['data_writes']==r['expected_writes'] for r in state['cases']):return {}
    repos=SITE.parents[1]/'publish/github_20260912'
    if not repos.exists():repos=SITE.parent
    for name,expected in state['library_sha256'].items():
        source=repos/'kitaqfc/lib'/name
        if source.exists() and hashlib.sha256(source.read_bytes()).hexdigest()!=expected:raise ValueError('PPU state-test source changed: '+name)
    script=repos/'kitaqfc/scripts/test-runtime-ppu.py'
    if script.exists() and hashlib.sha256(script.read_bytes()).hexdigest()!=state['script_sha256']:raise ValueError('PPU state-test script changed')
    for run in runs:
        if not run['passed'] or run['frames']!=240 or run['geometry_pixels_checked']!=34816:return {}
        if any(run[k]!=0 for k in ['label_pixel_mismatches','geometry_pixel_mismatches','geometry_color_mismatches','ppu_writes_while_rendering']):return {}
        if run['compiler_sha256']!=state['compiler_sha256'] or run['emulator_sha256']!=state['emulator_sha256'] or run['library_sha256']!=state['library_sha256']:return {}
        files={run['source']:run['source_sha256'],run['image']:run['image_sha256'],**run['support_sha256']}
        for file,expected in files.items():
            if hashlib.sha256((SITE/file).read_bytes()).hexdigest()!=expected:raise ValueError('PPU example evidence changed: '+file)
    result={}
    for key,contract in contracts.items():
        if contract['review']!='runtime-ppu-source-20260915':continue
        programs={e['program'] for e in [contract['example']]+contract['example'].get('additional',[])}
        selected=[r for r in runs if r['source'] in programs]
        if len(selected)!=len(programs):raise ValueError('Missing PPU API form: '+key)
        result[key]=dict(api=key.split(':')[1],kind='runtime-ppu',runs=selected,state_path='verification/api-runtime-ppu/state_checks.json',state_count=14)
    return result


def verified_ppu_declaration_examples(contracts):
    """Separate expected unresolved symbols from successful alternative execution."""
    folder=SITE/'verification/api-ppu-declarations'
    if not (folder/'results.json').exists() or not (folder/'state_checks.json').exists():return {}
    runs=json.loads((folder/'results.json').read_text(encoding='utf-8'))['records']
    state=json.loads((folder/'state_checks.json').read_text(encoding='utf-8'))
    if len(runs)!=1 or not runs[0]['passed']:return {}
    if len(state['declarations'])!=4 or len(state['alternatives'])!=4:return {}
    for row in state['declarations']:
        if not row['passed'] or row['build_exit']==0 or not row['diagnostic_present'] or row['rom_created']:return {}
        case=folder/'declarations'/row['name']
        if row['expected_diagnostic'] not in (case/'build.txt').read_text(encoding='utf-8',errors='replace'):return {}
        if hashlib.sha256((case/'case.c').read_bytes()).hexdigest()!=row['source_sha256']:raise ValueError('Declaration build source changed')
    if not all(r['passed'] and r['actual']==r['expected'] for r in state['alternatives']):return {}
    repos=SITE.parents[1]/'publish/github_20260912'
    if not repos.exists():repos=SITE.parent
    for name,expected in state['library_sha256'].items():
        source=repos/'kitaqfc/lib'/name
        if source.exists() and hashlib.sha256(source.read_bytes()).hexdigest()!=expected:raise ValueError('PPU declaration source changed: '+name)
    script=repos/'kitaqfc/scripts/test-ppu-declarations.py'
    if script.exists() and hashlib.sha256(script.read_bytes()).hexdigest()!=state['script_sha256']:raise ValueError('Declaration test script changed')
    run=runs[0]
    if run['frames']!=240 or run['geometry_pixels_checked']!=34816 or any(run[k]!=0 for k in ['label_pixel_mismatches','geometry_pixel_mismatches','geometry_color_mismatches','ppu_writes_while_rendering']):return {}
    if run['compiler_sha256']!=state['compiler_sha256'] or run['emulator_sha256']!=state['emulator_sha256'] or run['library_sha256']!=state['library_sha256']:return {}
    for name,expected in {run['source']:run['source_sha256'],run['image']:run['image_sha256'],**run['support_sha256']}.items():
        if hashlib.sha256((SITE/name).read_bytes()).hexdigest()!=expected:raise ValueError('Alternative image/source changed: '+name)
    result={}
    for key,contract in contracts.items():
        if contract['review']!='ppu-declarations-source-20260915':continue
        if contract['example']['program']!=run['source']:raise ValueError('Alternative program mismatch')
        name=key.split(':')[1]
        result[key]=dict(api=name,kind='ppu-declarations',runs=runs,state_path='verification/api-ppu-declarations/state_checks.json',state_count=8,declaration_path='verification/api-ppu-declarations/declarations/'+name+'/build.txt')
    return result


def verified_ppu_intrinsic_examples(contracts):
    """Require compiler-bound register tests and both BG/sprite color evidence."""
    folder=SITE/'verification/api-ppu-intrinsics'
    if not (folder/'results.json').exists() or not (folder/'state_checks.json').exists():return {}
    runs=json.loads((folder/'results.json').read_text(encoding='utf-8'))['records']
    state=json.loads((folder/'state_checks.json').read_text(encoding='utf-8'))
    if len(runs)!=1 or not runs[0]['passed'] or len(state['cases'])!=31:return {}
    if not all(r['passed'] and r['ppu']==r['expected_ppu'] and r['result']==r['expected_result'] and r['vram']==r['expected_vram'] for r in state['cases']):return {}
    repos=SITE.parents[1]/'publish/github_20260912'
    if not repos.exists():repos=SITE.parent
    review=json.loads((SOURCE/'ppu_intrinsic_review_sources.json').read_text(encoding='utf-8'))
    for name,expected in review['source_sha256'].items():
        source=repos/name
        if source.exists() and hashlib.sha256(source.read_bytes()).hexdigest()!=expected:raise ValueError('PPU compiler source changed: '+name)
    script=repos/'kitaqfc/scripts/test-ppu-intrinsics.py'
    if script.exists() and hashlib.sha256(script.read_bytes()).hexdigest()!=state['script_sha256']:raise ValueError('PPU intrinsic test script changed')
    run=runs[0]
    if run['frames']!=240 or run['geometry_pixels_checked']!=16384 or any(run[k]!=0 for k in ['label_pixel_mismatches','geometry_pixel_mismatches','geometry_color_mismatches','ppu_writes_while_rendering']):return {}
    if run['compiler_sha256']!=state['compiler_sha256'] or run['emulator_sha256']!=state['emulator_sha256'] or run['library_sha256']['intrinsics.h']!=state['header_sha256']:return {}
    for name,expected in {run['source']:run['source_sha256'],run['image']:run['image_sha256'],**run['support_sha256']}.items():
        if hashlib.sha256((SITE/name).read_bytes()).hexdigest()!=expected:raise ValueError('PPU intrinsic sample changed: '+name)
    result={}
    for key,contract in contracts.items():
        if contract['review']!='ppu-intrinsics-source-20260915':continue
        if contract['example']['program']!=run['source']:raise ValueError('PPU intrinsic program mismatch')
        result[key]=dict(api=key.split(':')[1],kind='ppu-intrinsics',runs=runs,state_path='verification/api-ppu-intrinsics/state_checks.json',state_count=31)
    return result


def verified_oam_library_examples(contracts):
    """Require a matching source/image for every separately compiled API form."""
    path=SITE/'verification/api-oam-library/results.json'
    if not path.exists():return {}
    runs=json.loads(path.read_text(encoding='utf-8'))['records']
    if len(runs)!=3 or {r['mode'] for r in runs}!={'aliases','c-runtime','fair-pool'}:return {}
    if not all(r['passed'] and r['frames']==240 and r['label_pixel_mismatches']==0 and r['sprite_pixel_mismatches']==0 and r['sprite_pixels_checked']==8704 and r['oam_matches_source'] and len(r['oam'])==256 and r['oam']==r['source_bytes'] for r in runs):return {}
    result={};repos=SITE.parents[1]/'publish/github_20260912'
    if not repos.exists():repos=SITE.parent
    state_path=SITE/'verification/api-oam-library/state_checks.json'
    if not state_path.exists():return {}
    state=json.loads(state_path.read_text(encoding='utf-8'))
    if len(state['cases'])!=17 or not all(r['passed'] for r in state['cases']):return {}
    if {r['compiler_sha256'] for r in state['cases']}!={r['compiler_sha256'] for r in runs}:return {}
    for name,expected in state['library_sha256'].items():
        source=repos/'kitaqfc/lib'/name
        if source.exists() and hashlib.sha256(source.read_bytes()).hexdigest()!=expected:raise ValueError('OAM state-test source changed: '+name)
    script=repos/'kitaqfc/scripts/test-oam-library.py'
    if script.exists() and hashlib.sha256(script.read_bytes()).hexdigest()!=state['script_sha256']:raise ValueError('OAM state-test script changed')
    for key,contract in contracts.items():
        if contract['review']!='oam-library-source-20260915':continue
        examples=[contract['example']]+contract['example'].get('additional',[])
        selected=[]
        for example in examples:
            matching=[r for r in runs if r['source']==example['program']]
            if len(matching)!=1:raise ValueError('OAM library example mismatch: '+key)
            run=matching[0];selected.append(run)
            runtime=(Path(run['image']).parent/'runtime.json').as_posix()
            files={run['source']:run['source_sha256'],run['image']:run['image_sha256'],runtime:run['runtime_sha256'],**run['support_sha256']}
            for name,expected in files.items():
                if hashlib.sha256((SITE/name).read_bytes()).hexdigest()!=expected:raise ValueError('OAM library evidence changed: '+name)
            for name,expected in run['library_sha256'].items():
                source=repos/'kitaqfc/lib'/name
                if source.exists() and hashlib.sha256(source.read_bytes()).hexdigest()!=expected:raise ValueError('OAM library source changed: '+name)
        result[key]={'api':key.split(':')[1],'kind':'oam-library','runs':selected,'state_path':state_path.relative_to(SITE).as_posix(),'state_count':17}
    return result


def verified_fc_oam_examples(contracts):
    """Bind each FC OAM intrinsic to its executed page and exact colored image."""
    path=SITE/'verification/api-fc-oam/results.json'
    if not path.exists():return {}
    runs=json.loads(path.read_text(encoding='utf-8'))['records']
    if len(runs)!=2 or {r['mode'] for r in runs}!={'page02','page04'}:return {}
    if not all(r['passed'] and r['frames']==240 and r['label_pixel_mismatches']==0 and r['sprite_pixel_mismatches']==0 and r['sprite_pixels_checked']==8704 and r['oam_matches_source'] and len(r['oam'])==256 and r['oam']==r['source_bytes'] for r in runs):return {}
    result={};repos=SITE.parents[1]/'publish/github_20260912'
    if not repos.exists():repos=SITE.parent
    for key,contract in contracts.items():
        if contract['review']!='fc-oam-source-20260915':continue
        selected=[r for r in runs if r['source']==contract['example']['program']]
        if len(selected)!=1:raise ValueError('FC OAM example mismatch: '+key)
        for run in selected:
            runtime=(Path(run['image']).parent/'runtime.json').as_posix()
            files={run['source']:run['source_sha256'],run['image']:run['image_sha256'],runtime:run['runtime_sha256'],**run['support_sha256']}
            for name,expected in files.items():
                if hashlib.sha256((SITE/name).read_bytes()).hexdigest()!=expected:raise ValueError('FC OAM evidence changed: '+name)
            for name,expected in run['library_sha256'].items():
                source=repos/'kitaqfc/lib'/name
                if source.exists() and hashlib.sha256(source.read_bytes()).hexdigest()!=expected:raise ValueError('FC OAM declaration changed: '+name)
        result[key]={'api':key.split(':')[1],'kind':'fc-oam','runs':selected}
    return result


def verified_oam_examples(contracts):
    """Require real OAM DMA geometry/color evidence and exact source identities."""
    path=SITE/'verification/api-oam/results.json'
    if not path.exists():return {}
    runs=json.loads(path.read_text(encoding='utf-8'))['records']
    if len(runs)!=2 or {(r['platform'],r['mode']) for r in runs}!={('gb','dmg'),('gb','cgb')}:return {}
    if not all(r['passed'] and r['frames']==240 and r['label_pixel_mismatches']==0 and r['sprite_pixel_mismatches']==0 and r['sprite_pixels_checked']==3456 for r in runs):return {}
    result={};repos=SITE.parents[1]/'publish/github_20260912'
    if not repos.exists():repos=SITE.parent
    for key,contract in contracts.items():
        if contract['review']!='oam-source-20260915':continue
        selected=[r for r in runs if r['platform']==key.split(':')[0]]
        for run in selected:
            if run['source']!=contract['example']['program']:raise ValueError('OAM example mismatch: '+key)
            runtime=(Path(run['image']).parent/'runtime.json').as_posix()
            files={run['source']:run['source_sha256'],run['image']:run['image_sha256'],runtime:run['runtime_sha256'],**run['support_sha256']}
            for name,expected in files.items():
                if hashlib.sha256((SITE/name).read_bytes()).hexdigest()!=expected:raise ValueError('OAM evidence changed: '+name)
            for name,expected in run['library_sha256'].items():
                source=repos/('kitaq'+run['platform'])/'lib'/name
                if source.exists() and hashlib.sha256(source.read_bytes()).hexdigest()!=expected:raise ValueError('OAM library changed: '+str(source))
        result[key]={'api':key.split(':')[1],'kind':'oam','runs':selected}
    return result


def verified_sprite_examples(contracts):
    """Require real sprite geometry/color evidence and exact source identities."""
    path=SITE/'verification/api-sprite/results.json'
    if not path.exists():return {}
    runs=json.loads(path.read_text(encoding='utf-8'))['records']
    if len(runs)!=3 or {(r['platform'],r['mode']) for r in runs}!={('gb','dmg'),('gb','cgb'),('fc','ntsc')}:return {}
    if not all(r['passed'] and r['frames']==240 and r['label_pixel_mismatches']==0 and r['sprite_pixel_mismatches']==0 and r['sprite_pixels_checked']==4096 for r in runs):return {}
    result={};repos=SITE.parents[1]/'publish/github_20260912'
    if not repos.exists():repos=SITE.parent
    for key,contract in contracts.items():
        if contract['review']!='sprite-source-20260915':continue
        selected=[r for r in runs if r['platform']==key.split(':')[0]]
        for run in selected:
            if run['source']!=contract['example']['program']:raise ValueError('Sprite example mismatch: '+key)
            runtime=(Path(run['image']).parent/'runtime.json').as_posix()
            files={run['source']:run['source_sha256'],run['image']:run['image_sha256'],runtime:run['runtime_sha256'],**run['support_sha256']}
            for name,expected in files.items():
                if hashlib.sha256((SITE/name).read_bytes()).hexdigest()!=expected:raise ValueError('Sprite evidence changed: '+name)
            for name,expected in run['library_sha256'].items():
                source=repos/('kitaq'+run['platform'])/'lib'/name
                if source.exists() and hashlib.sha256(source.read_bytes()).hexdigest()!=expected:raise ValueError('Sprite library changed: '+str(source))
        result[key]={'api':key.split(':')[1],'kind':'sprite','runs':selected}
    return result


def verified_bank_examples(contracts):
    """Require the complete byte/word/callback/restoration matrix and unchanged inputs."""
    path = SITE/'verification/api-bank/results.json'
    if not path.exists(): return {}
    runs = json.loads(path.read_text(encoding='utf-8'))['records']
    if len(runs)!=3 or {(r['platform'],r['mode']) for r in runs}!={('gb','dmg'),('gb','cgb'),('fc','mmc3')}: return {}
    if not all(r['passed'] and r['frames']==240 and r['label_pixel_mismatches']==0 and r['color_pixel_mismatches']==0 for r in runs):return {}
    result={}
    for key,contract in contracts.items():
        if contract['review']!='bank-source-20260915':continue
        selected=[r for r in runs if r['platform']==key.split(':')[0]]
        for run in selected:
            if run['source']!=contract['example']['program']:raise ValueError('Bank example mismatch: '+key)
            runtime=str(Path(run['image']).parent/'runtime.json').replace('\\','/')
            files={run['source']:run['source_sha256'],run['image']:run['image_sha256'],runtime:run['runtime_sha256'],**run['support_sha256']}
            for name,expected in files.items():
                if hashlib.sha256((SITE/name).read_bytes()).hexdigest()!=expected:raise ValueError('Bank evidence changed: '+name)
            repos=SITE.parents[1]/'publish/github_20260912'
            if not repos.exists():repos=SITE.parent
            for name,expected in run['library_sha256'].items():
                source=repos/('kitaq'+run['platform'])/'lib'/name
                if source.exists() and hashlib.sha256(source.read_bytes()).hexdigest()!=expected:raise ValueError('Bank library changed: '+str(source))
        result[key]={'api':key.split(':')[1],'kind':'bank','runs':selected}
    return result


def verified_asset_examples(contracts):
    """Require bank-separated, colored uploads on both targets and their exact source files."""
    path = SITE/'verification/api-asset/results.json'
    if not path.exists(): return {}
    runs = json.loads(path.read_text(encoding='utf-8'))['records']
    expected = {('gb','dmg'),('gb','cgb'),('fc','surom512')}
    if len(runs)!=3 or {(r['platform'],r['mode']) for r in runs}!=expected: return {}
    if not all(r['passed'] and r.get('frames')==300 and r['label_pixel_mismatches']==0 and
               r['geometry_pixel_mismatches']==0 and r['geometry_color_mismatches']==0 for r in runs): return {}
    result = {}
    for key,contract in contracts.items():
        if contract['review']!='asset-source-20260915': continue
        selected = [r for r in runs if r['platform']==key.split(':')[0]]
        for run in selected:
            if run['source']!=contract['example']['program']: raise ValueError('Asset sample mismatch: '+key)
            folder = str(Path(run['image']).parent).replace('\\','/')
            files = {run['source']:run['source_sha256'],run['image']:run['image_sha256'],
                     folder+'/runtime.json':run['runtime_sha256'],**run['support_sha256']}
            for file,expected_hash in files.items():
                if hashlib.sha256((SITE/file).read_bytes()).hexdigest()!=expected_hash:
                    raise ValueError('Asset example evidence changed: '+file)
        result[key] = {'api':key.split(':')[1],'kind':'asset','runs':selected}
    return result


def verified_cgb_dma_wram_examples(contracts):
    """Require the complete DMA/WRAM execution matrix and negative diagnostics."""
    folder = SITE/'verification/api-cgb-dma-wram'
    if not (folder/'results.json').exists() or not (folder/'diagnostics/results.json').exists(): return {}
    runs = json.loads((folder/'results.json').read_text(encoding='utf-8'))['records']
    expected = {('cgb_dma_shapes','cgb','dmg'),('cgb_dma_shapes','cgb','cgb'),('cgb_dma_shapes','cgb_only','cgb'),('cgb_wram_banks','cgb_only','cgb')}
    if len(runs)!=4 or {(r['id'],r['target'],r['mode']) for r in runs}!=expected or not all(r['passed'] for r in runs): return {}
    diagnostics = json.loads((folder/'diagnostics/results.json').read_text(encoding='utf-8'))
    if len(diagnostics['records'])!=6 or not all(r['passed'] for r in diagnostics['records']): return {}
    if any(run['compiler_sha256']!=diagnostics['compiler_sha256'] for run in runs):
        raise ValueError('DMA/WRAM runtime and diagnostics use different compilers')
    for run in diagnostics['records']:
        if hashlib.sha256((SITE/run['source']).read_bytes()).hexdigest()!=run['source_sha256']:
            raise ValueError('WRAM diagnostic source changed: '+run['source'])
    result = {}
    for key,contract in contracts.items():
        if contract['review']!='cgb-dma-wram-source-20260915': continue
        selected = [r for r in runs if r['source']==contract['example']['program']]
        if not selected: raise ValueError('No DMA/WRAM evidence for '+key)
        for run in selected:
            files = {run['source']:run['source_sha256'],run['image']:run['image_sha256'],**run['support_sha256']}
            for file,expected_hash in files.items():
                if hashlib.sha256((SITE/file).read_bytes()).hexdigest()!=expected_hash:
                    raise ValueError('DMA/WRAM example changed: '+file)
        result[key] = {'api':key.split(':')[1],'kind':'cgb-dma-wram','runs':selected}
        if key in ['gb:__svbk_get','gb:__svbk_set']:
            result[key]['diagnostics_path'] = 'verification/api-cgb-dma-wram/diagnostics/results.json'
    return result


def verified_cgb_palette_examples(contracts):
    """Require all four target/hardware cases and their unchanged source evidence."""
    path = SITE/'verification/api-cgb-palette/results.json'
    if not path.exists(): return {}
    runs = json.loads(path.read_text(encoding='utf-8'))['records']
    expected_cases = {('cgb','dmg'),('cgb','cgb'),('dmg','dmg'),('cgb_only','cgb')}
    if len(runs)!=4 or {(r['target'],r['mode']) for r in runs}!=expected_cases or not all(r['passed'] for r in runs):
        return {}
    repos = SITE.parents[1]/'publish/github_20260912'
    if not repos.exists(): repos = SITE.parent
    result = {}
    for key,contract in contracts.items():
        if contract['review']!='cgb-palette-source-20260915': continue
        for run in runs:
            if run['source']!=contract['example']['program']:
                raise ValueError('CGB palette example source mismatch: '+key)
            files = {run['source']:run['source_sha256'],run['image']:run['image_sha256'],**run['support_sha256']}
            for file,expected in files.items():
                if hashlib.sha256((SITE/file).read_bytes()).hexdigest()!=expected:
                    raise ValueError('CGB palette evidence changed: '+file)
            for file,expected in run['library_sha256'].items():
                source = repos/'kitaqgb/lib'/file
                if not source.exists() or hashlib.sha256(source.read_bytes()).hexdigest()!=expected:
                    raise ValueError('CGB palette library changed: '+str(source))
        result[key] = {'api':key.split(':')[1],'kind':'cgb-palette','runs':runs}
    return result


def verified_interrupt_intrinsic_examples(contracts):
    """Require observed mask/counter states and the matching 360-frame screen."""
    folder = SITE / 'verification/api-interrupt-intrinsics'
    if not (folder / 'results.json').exists(): return {}
    state = json.loads((folder / 'state_checks.json').read_text(encoding='utf-8'))
    if len(state['cases']) != 21 or not all(row['passed'] and row['actual'] == row['expected'] for row in state['cases']):
        raise ValueError('IRQ/NMI state verification is incomplete')
    repos = SITE.parents[1] / 'publish/github_20260912'
    if not repos.exists(): repos = SITE.parent
    files = {
        'kitaqfc/scripts/test-interrupt-intrinsics.py': state['script_sha256'],
        'kitaqfc/kitaqfc.exe': state['compiler_sha256'],
        'kurosaki/kurosaki.exe': state['emulator_sha256'],
        'kitaqfc/lib/intrinsics.h': state['header_sha256'],
    }
    review = json.loads((SOURCE / 'interrupt_intrinsic_review_sources.json').read_text(encoding='utf-8'))
    files.update(review['source_sha256'])
    for name, expected in files.items():
        path = repos / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('IRQ/NMI verification source changed: ' + name)
    runs = json.loads((folder / 'results.json').read_text(encoding='utf-8'))['records']
    if len(runs) != 1: raise ValueError('IRQ/NMI sample run missing')
    run = runs[0]
    if not (run['passed'] and run['frames'] == 360 and run['label_pixel_mismatches'] == 0 and run['color_mismatches'] == 0 and run['colored_pixels'] == 4118 and run['ppu_writes_while_rendering'] == 0):
        raise ValueError('IRQ/NMI sample screen failed verification')
    for name, expected in {run['source']: run['source_sha256'], run['image']: run['image_sha256'], **run['support_sha256']}.items():
        if hashlib.sha256((SITE / name).read_bytes()).hexdigest() != expected:
            raise ValueError('IRQ/NMI sample evidence changed: ' + name)
    if run['compiler_sha256'] != state['compiler_sha256'] or run['emulator_sha256'] != state['emulator_sha256'] or run['header_sha256'] != state['header_sha256']:
        raise ValueError('IRQ/NMI sample and state checks use different tools')
    result = {}
    for key, contract in contracts.items():
        if contract['review'] != 'interrupt-intrinsics-source-20260915': continue
        if contract['example']['program'] != run['source']: raise ValueError('IRQ/NMI sample mismatch: ' + key)
        result[key] = {'api': key.split(':')[1], 'kind': 'interrupt-intrinsics', 'runs': runs}
    return result


def verified_memory_intrinsic_examples(contracts):
    return verified_buffer_intrinsic_examples(contracts, 'memory', 88)


def verified_bit_intrinsic_examples(contracts):
    return verified_buffer_intrinsic_examples(contracts, 'bit', 136)


def verified_rle_examples(contracts):
    """Require decoded bytes, guards, bank restoration and matching tile pictures."""
    selected_contracts={k:c for k,c in contracts.items() if c['review']=='rle-source-20260915'}
    if not selected_contracts:return {}
    folder=SITE/'verification/api-rle';repos=SITE.parents[1]/'publish/github_20260912'
    if not repos.exists():repos=SITE.parent
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    review=json.loads((SOURCE/'rle_review_sources.json').read_text(encoding='utf-8'))
    for name,expected in review['source_sha256'].items():
        if sha(repos/name)!=expected:raise ValueError('RLE implementation changed: '+name)
    state=json.loads((folder/'state/results.json').read_text(encoding='utf-8'))
    if len(state['cases'])!=42 or len({r['name'] for r in state['cases']})!=42:raise ValueError('RLE verification matrix incomplete')
    for path,key in [(repos/'kitaqgb/kitaqgb.exe','compiler_sha256'),(repos/'kokura/kokura-cli.exe','emulator_sha256'),(SITE/'tools/check_rle_state.py','script_sha256')]:
        if sha(path)!=state[key]:raise ValueError('RLE verification tool changed')
    for name,expected in state['source_sha256'].items():
        if sha(repos/name)!=expected:raise ValueError('RLE state source changed')
    for row in state['cases']:
        if not(row['passed'] and row['build_exit']==0 and row['runtime_exit']==0 and len(row['actual'])==528 and row['actual']==row['expected'] and row['result']==row['expected_result']):raise ValueError('RLE byte/state verification failed: '+row['name'])
        case=folder/'state'/row['name']
        if sha(case/'case.c')!=row['source_sha256'] or sha(case/'case.gb')!=row['rom_sha256']:raise ValueError('RLE fixture changed')
    runs=json.loads((folder/'results.json').read_text(encoding='utf-8'))['records']
    if len(runs)!=2 or {(r['platform'],r['mode']) for r in runs}!={('gb','dmg'),('gb','cgb')}:raise ValueError('RLE sample variants missing')
    for run in runs:
        if not(run['passed'] and run['frames']==240 and run['label_pixel_mismatches']==0 and run['geometry_pixel_mismatches']==0 and run['color_mismatches']==0 and run['colored_pixels']>0):raise ValueError('RLE sample screen failed')
        if any(run[k]!=state[k] for k in ['compiler_sha256','emulator_sha256']):raise ValueError('RLE sample tool mismatch')
        if run['header_sha256']!=review['source_sha256']['kitaqgb/lib/rpg.h'] or run['library_sha256']!=review['source_sha256']['kitaqgb/lib/rle.c']:raise ValueError('RLE sample source mismatch')
        for name,expected in {run['source']:run['source_sha256'],run['image']:run['image_sha256'],**run['support_sha256']}.items():
            if sha(SITE/name)!=expected:raise ValueError('RLE sample changed: '+name)
        if sha((SITE/run['image']).with_name('example.gb'))!=run['rom_sha256']:raise ValueError('RLE teaching ROM changed')
    result={}
    for key,contract in selected_contracts.items():
        if any(r['source']!=contract['example']['program'] for r in runs):raise ValueError('RLE teaching program mismatch')
        result[key]={'api':key.split(':')[1],'kind':'rle','runs':runs}
    return result


def verified_flags_examples(contracts):
    """Require exhaustive valid-ID checks and exact flag/quest teaching screens."""
    selected_contracts={k:c for k,c in contracts.items() if c['review']=='flags-source-20260915'}
    if not selected_contracts:return {}
    folder=SITE/'verification/api-flags';repos=SITE.parents[1]/'publish/github_20260912'
    if not repos.exists():repos=SITE.parent
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    review=json.loads((SOURCE/'flags_review_sources.json').read_text(encoding='utf-8'))
    state=json.loads((folder/'state/results.json').read_text(encoding='utf-8'))
    if not(state['passed'] and state['build_exit']==0 and state['runtime_exit']==0 and state['flag_ids']==2048 and state['quest_ids']==64 and state['quest_values_per_id']==256 and state['frames']==1200 and len(state['actual'])==336 and state['actual']==state['expected']):raise ValueError('Flag/quest exhaustive check failed')
    if state['source_files']!=review['source_sha256']:raise ValueError('Flag/quest source binding mismatch')
    for name,expected in review['source_sha256'].items():
        if sha(repos/name)!=expected:raise ValueError('Flag/quest library changed: '+name)
    for path,key in [(repos/'kitaqgb/kitaqgb.exe','compiler_sha256'),(repos/'kokura/kokura-cli.exe','emulator_sha256'),(folder/'state/case.c','source_sha256'),(folder/'state/case.gb','rom_sha256'),(SITE/'tools/check_flags_state.py','script_sha256')]:
        if sha(path)!=state[key]:raise ValueError('Flag/quest state proof changed: '+str(path))
    runs=json.loads((folder/'results.json').read_text(encoding='utf-8'))['records']
    if len(runs)!=2 or {(r['platform'],r['mode']) for r in runs}!={('gb','dmg'),('gb','cgb')}:raise ValueError('Flag/quest screen variants missing')
    for run in runs:
        if not(run['passed'] and run['build_exit']==0 and run['runtime_exit']==0 and run['frames']==240 and run['label_pixel_mismatches']==0 and run['color_mismatches']==0 and run['colored_pixels']>0):raise ValueError('Flag/quest teaching screen failed')
        if any(run[k]!=state[k] for k in ['compiler_sha256','emulator_sha256']):raise ValueError('Flag/quest screen tools changed')
        if run['header_sha256']!=review['source_sha256']['kitaqgb/lib/rpg.h'] or run['library_sha256']!=review['source_sha256']['kitaqgb/lib/flags.c']:raise ValueError('Flag/quest screen library changed')
        for name,expected in {run['source']:run['source_sha256'],run['image']:run['image_sha256'],**run['support_sha256']}.items():
            if sha(SITE/name)!=expected:raise ValueError('Flag/quest screen proof changed: '+name)
        if sha((SITE/run['image']).with_name('example.gb'))!=run['rom_sha256']:raise ValueError('Flag/quest teaching ROM changed')
    result={}
    for key,contract in selected_contracts.items():
        if any(r['source']!=contract['example']['program'] for r in runs):raise ValueError('Flag/quest program mismatch')
        result[key]={'api':key.split(':')[1],'kind':'flags','runs':runs}
    return result


def verified_rng_examples(contracts):
    """Bind RNG documentation to exact sequences, draw counts and teaching screens."""
    folder=SITE/'verification/api-rng'
    selected_contracts={k:c for k,c in contracts.items() if c['review']=='rng-source-20260915'}
    if not selected_contracts:return {}
    repos=SITE.parents[1]/'publish/github_20260912'
    if not repos.exists():repos=SITE.parent
    review=json.loads((SOURCE/'rng_review_sources.json').read_text(encoding='utf-8'))
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    for name,expected in review['source_sha256'].items():
        if sha(repos/name)!=expected:raise ValueError('RNG implementation changed: '+name)
    runs=json.loads((folder/'results.json').read_text(encoding='utf-8'))['records']
    expected_variants={('rng_values','dmg'),('rng_values','cgb'),('rng_choices','dmg'),('rng_choices','cgb'),('rng_core','nrom')}
    if len(runs)!=5 or {(r['sample'],r['mode']) for r in runs}!=expected_variants:raise ValueError('RNG screens missing')
    states={}
    for platform,count in [('gb',93),('fc',18)]:
        state=json.loads((folder/platform/'state_checks.json').read_text(encoding='utf-8'));states[platform]=state
        if len(state['cases'])!=count or not all(r['passed'] and len(r['actual'])==80 and r['actual']==r['expected'] for r in state['cases']):raise ValueError('RNG state comparison failed')
        if sha(SITE/'tools/check_rng_state.py')!=state['script_sha256']:raise ValueError('RNG state checker changed')
        for row in state['cases']:
            case=folder/platform/row['name']
            for name,expected in [('case.c',row['source_sha256']),('case.'+('gb' if platform=='gb' else 'nes'),row['rom_sha256'])]:
                if sha(case/name)!=expected:raise ValueError('RNG state fixture changed: '+str(case/name))
        for name,expected in state['library_sha256'].items():
            if sha(repos/name)!=expected:raise ValueError('RNG state library changed: '+name)
        for path,key in [(repos/('kitaq'+platform)/('kitaq'+platform+'.exe'),'compiler_sha256'),(repos/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe'),'emulator_sha256')]:
            if sha(path)!=state[key]:raise ValueError('RNG verification executable changed')
    for run in runs:
        if not (run['passed'] and run['build_exit']==0 and run['runtime_exit']==0 and run['frames']==240 and run['label_pixel_mismatches']==0 and run['color_mismatches']==0 and run['colored_pixels']>0 and run['ppu_writes_while_rendering']==0):raise ValueError('RNG screen check failed')
        platform=run['platform'];state=states[platform]
        if any(run[k]!=state[k] for k in ['compiler_sha256','emulator_sha256']):raise ValueError('RNG sample executable mismatch')
        header='kitaq'+platform+'/lib/'+('rpg.h' if platform=='gb' else 'intrinsics.h')
        if run['header_sha256']!=review['source_sha256'][header]:raise ValueError('RNG sample header mismatch')
        if platform=='gb' and run['library_sha256']!=review['source_sha256']['kitaqgb/lib/rng.c']:raise ValueError('RNG sample library mismatch')
        files={run['source']:run['source_sha256'],run['image']:run['image_sha256'],**run['support_sha256']}
        rom=(SITE/run['image']).with_name('example.'+('gb' if platform=='gb' else 'nes'))
        if sha(rom)!=run['rom_sha256']:raise ValueError('RNG teaching ROM changed')
        for name,expected in files.items():
            if sha(SITE/name)!=expected:raise ValueError('RNG sample changed: '+name)
    result={}
    for key,contract in selected_contracts.items():
        selected=[r for r in runs if r['source']==contract['example']['program'] and r['platform']==key.split(':')[0]]
        if len(selected)!=(2 if key.startswith('gb:') else 1):raise ValueError('RNG sample variants missing: '+key)
        result[key]={'api':key.split(':')[1],'kind':'rng','runs':selected}
    return result


def verified_buffer_intrinsic_examples(contracts, family, state_count):
    """Require full RAM comparisons and matching source, tool and screen hashes."""
    folder=SITE/('verification/api-'+family+'-intrinsics')
    if not (folder/'results.json').exists():return {}
    repos=SITE.parents[1]/'publish/github_20260912'
    if not repos.exists():repos=SITE.parent
    review=json.loads((SOURCE/(family+'_intrinsic_review_sources.json')).read_text(encoding='utf-8'))
    for name,expected in review['source_sha256'].items():
        if hashlib.sha256((repos/name).read_bytes()).hexdigest()!=expected:
            raise ValueError('Memory intrinsic source changed: '+name)
    runs=json.loads((folder/'results.json').read_text(encoding='utf-8'))['records']
    if {(r['platform'],r['mode']) for r in runs}!={('gb','dmg'),('gb','cgb'),('fc','nrom')} or len(runs)!=3:
        raise ValueError('Memory intrinsic screen variants missing')
    result={}
    for platform in ['gb','fc']:
        state=json.loads((folder/platform/'state_checks.json').read_text(encoding='utf-8'))
        if len(state['cases'])!=state_count or not all(r['passed'] and r['actual']==r['expected'] for r in state['cases']):
            raise ValueError('Memory range/state checks failed')
        if hashlib.sha256((SITE/('tools/check_'+family+'_intrinsic_state.py')).read_bytes()).hexdigest()!=state['script_sha256']:
            raise ValueError('Memory state checker changed')
        for row in state['cases']:
            case=folder/platform/row['name']
            for name,expected in [('case.c',row['source_sha256']),('case.'+('gb' if platform=='gb' else 'nes'),row['rom_sha256'])]:
                if hashlib.sha256((case/name).read_bytes()).hexdigest()!=expected:
                    raise ValueError('Memory state fixture changed: '+str(case/name))
        compiler=repos/('kitaq'+platform)/('kitaq'+platform+'.exe')
        emulator=repos/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe')
        for path,key in [(compiler,'compiler_sha256'),(emulator,'emulator_sha256')]:
            if hashlib.sha256(path.read_bytes()).hexdigest()!=state[key]:raise ValueError('Memory verification tool changed')
        selected=[r for r in runs if r['platform']==platform]
        for run in selected:
            if not (run['passed'] and run['frames']==240 and run['label_pixel_mismatches']==0 and run['color_mismatches']==0 and run['colored_pixels']>0 and run['ppu_writes_while_rendering']==0):
                raise ValueError('Memory sample screen failed verification')
            if any(run[key]!=state[key] for key in ['compiler_sha256','emulator_sha256']):raise ValueError('Memory sample uses different tools')
            header='kitaq'+platform+'/lib/'+('rpg.h' if platform=='gb' else 'intrinsics.h')
            if run['header_sha256']!=review['source_sha256'][header]:raise ValueError('Memory sample header changed')
            for name,expected in {run['source']:run['source_sha256'],run['image']:run['image_sha256'],**run['support_sha256']}.items():
                if hashlib.sha256((SITE/name).read_bytes()).hexdigest()!=expected:raise ValueError('Memory sample changed: '+name)
        for key,contract in contracts.items():
            if not key.startswith(platform+':') or contract['review']!=family+'-intrinsics-source-20260915':continue
            if any(contract['example']['program']!=run['source'] for run in selected):raise ValueError('Memory sample mismatch')
            result[key]={'api':key.split(':')[1],'kind':family+'-intrinsics','runs':selected}
    return result


def verified_tile_examples(contracts):
    path = SITE / 'verification/api-tiles/results.json'
    if not path.exists(): return {}
    report = json.loads(path.read_text(encoding='utf-8'))
    for name, expected in report['shared_source_sha256'].items():
        if hashlib.sha256((SITE/'samples'/name).read_bytes()).hexdigest() != expected:
            raise ValueError('Tile example support changed; rerun the affected examples: ' + name)
    verified = {}
    for result in report['examples']:
        key = 'gb:' + result['api']
        if key not in contracts or not result['passed']: continue
        sample = SITE / contracts[key]['example']['program']
        if hashlib.sha256(sample.read_bytes()).hexdigest() != result['source_sha256']:
            raise ValueError('Example source changed after verification: ' + key)
        verified[key] = result
    return verified


def verified_entity_examples(contracts):
    path = SITE/'verification/api-entity/results.json'
    if not path.exists(): return {}
    report = json.loads(path.read_text(encoding='utf-8'))
    runs = report['records']
    if not runs or not all(r['passed'] for r in runs): return {}
    result = {}
    for key, contract in contracts.items():
        if not key.split(':')[1].startswith('entity_'): continue
        platform = key.split(':')[0]
        selected = [r for r in runs if r['platform']==platform and r['id'].startswith('entity_pool')]
        if len(selected)!=(2 if platform=='gb' else 1): continue
        for row in selected:
            for file, expected in [(SITE/row['source'],row['source_sha256']),
                                   (SITE/row['image'],row['image_sha256'])]:
                if hashlib.sha256(file.read_bytes()).hexdigest()!=expected:
                    raise ValueError('Entity evidence changed: '+str(file))
        result[key] = {'api':key.split(':')[1], 'kind':'entity', 'runs':selected}
    return result


def attach_verified_images(contracts, proofs):
    """Bind captured screens to the exact complete program that produced them."""
    for key, result in proofs.items():
        example = contracts[key]['example']
        examples = [example] + example.get('additional', [])
        for item in examples:
            item['verified_images'] = []
        if not result.get('kind'):
            for hardware in ['dmg', 'cgb']:
                image = 'verification/api-tiles/' + result['api'] + '-' + hardware + '.png'
                if not (SITE / image).is_file():
                    raise ValueError('Missing captured screen: ' + image)
                example['verified_images'].append({'image': image, 'caption': hardware.upper()})
            continue
        for run in result['runs']:
            program = run.get('source', run.get('program'))
            matching = [item for item in examples if item['program'] == program]
            if len(matching) != 1:
                raise ValueError('Screen does not identify exactly one sample: ' + key)
            caption = ('--cgb=' + run['target'] + ' / ' if result.get('kind') in ['cgb-palette', 'cgb-dma-wram'] else '') + run['mode'].upper()
            matching[0]['verified_images'].append({'image': run['image'], 'caption': caption})
        if not all(item['verified_images'] for item in examples):
            raise ValueError('Missing sample screen: ' + key)


def publish_verification(language, contracts, proofs, messages, ui):
    """API screens are rendered with their explanations, without raw run records."""
    path = (SITE if language == 'ja' else SITE / language) / 'verification.html'
    original = path.read_bytes()
    text = original.decode('utf-8').replace('\r\n', '\n')
    text = re.sub(r'<!-- api-verification:start -->.*?<!-- api-verification:end -->', '', text, flags=re.S)
    path.write_text(text, encoding='utf-8', newline='\r\n' if b'\r\n' in original else '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language', choices=ACTIVE_LANGUAGES)
    parser.add_argument('--require-complete', action='store_true')
    args = parser.parse_args()
    for language in ([args.language] if args.language else ACTIVE_LANGUAGES):
        report = publish(language, args.require_complete)
        print(language + ': ' + str(report['reviewed']) + ' reviewed; ' + str(report['remaining']) + ' remaining')
    (SOURCE / 'coverage.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
