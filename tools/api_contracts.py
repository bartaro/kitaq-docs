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

SITE = Path(__file__).resolve().parents[1]
SOURCE = SITE / 'tools/api_descriptions'
ORDER = ['en', 'ja', 'ko', 'zh-CN', 'zh-TW', 'es', 'pt', 'fr', 'de']


def load():
    messages = {}
    for path in sorted(SOURCE.glob('*texts.json')):
        for key, value in json.loads(path.read_text(encoding='utf-8')).items():
            if key in messages:
                raise ValueError('Duplicate authored message: ' + key)
            if len(value) != len(ORDER) or not all(isinstance(v, str) and v.strip() for v in value):
                raise ValueError('Nine authored translations required: ' + key)
            messages[key] = value
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
    if example.get('program'):
        out.append('<p><a href="' + prefix + example['program'] + '">' + label('download') + '</a></p>')
    if example.get('build'):
        out += ['<h4>' + label('build') + '</h4>', code(example['build'], 'powershell')]
    if example.get('verification'):
        out.append('<p><a href="verification.html#' + example['verification'] + '">' + label('verification') + '</a></p>')
    out.append('<details class="api-source"><summary>' + label('implementation') + '</summary>')
    out.append('<p class="source">' + html.escape(record['path']) + ':' + str(record['line']) + '</p>')
    if record.get('comment'):
        out += ['<div class="original"><b>' + label('original') + '</b><pre>' + html.escape(record['comment']) + '</pre></div>']
    if record.get('definition'):
        source = record['definition']
        out += ['<p class="source">' + html.escape(source['path']) + ':' + str(source['line']) + '</p>', code(source['body'])]
    elif record.get('implementation_excerpt'):
        out.append(code(record['implementation_excerpt'], 'csharp'))
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
    messages, ui, contracts = load()
    folder = SITE if language == 'ja' else SITE / language
    proofs = verified_tile_examples(contracts)
    proofs.update(verified_entity_examples(contracts))
    proofs.update(verified_input_examples(contracts))
    for key in proofs:
        contracts[key]['example']['verification'] = 'api-' + key.replace(':','-')
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
    return {'reviewed': len(contracts), 'remaining': len(coverage), 'missing': coverage}


def render_modules(text, platform, language, messages):
    """Place reviewed library introductions directly below their module headings."""
    text = re.sub(r'<!-- api-module:start -->.*?<!-- api-module:end -->','',text,flags=re.S)
    index = ORDER.index(language)
    for path in sorted(SOURCE.glob('*modules.json')):
        for key, paragraphs in json.loads(path.read_text(encoding='utf-8')).items():
            owner, module = key.split(':')
            if owner != platform: continue
            pattern = r'(<h3\b[^>]*id="module-' + re.escape(module) + r'"[^>]*>.*?</h3>)'
            block = '<!-- api-module:start --><div data-module-contract="input-source-20260915">'
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


def publish_verification(language, contracts, proofs, messages, ui):
    path = (SITE if language=='ja' else SITE/language)/'verification.html'
    original = path.read_bytes()
    text = original.decode('utf-8').replace('\r\n','\n')
    text = re.sub(r'<!-- api-verification:start -->.*?<!-- api-verification:end -->','',text,flags=re.S)
    if proofs:
        index = ORDER.index(language)
        prefix = '' if language=='ja' else '../'
        title = messages['api_verification_title'][index]
        block = ['<!-- api-verification:start --><h2 id="api-verification">' + html.escape(title) + '</h2>']
        block += ['<p>' + inline(messages['tile_verification_method'][index]) + '</p>']
        for key, result in proofs.items():
            name = result['api']
            example = contracts[key]['example']
            block.append('<section id="api-' + key.replace(':','-') + '"><h3><code>' + html.escape(name) + '</code></h3>')
            block += ['<p>' + inline(messages[item][index]) + '</p>' for item in contracts[key]['purpose'][:2]]
            if result.get('kind') in ['entity','input']:
                block += ['<p>' + inline(messages[item][index]) + '</p>' for item in example['expected']]
                for run in result['runs']:
                    block.append('<figure><img class="screen" loading="lazy" src="'+prefix+run['image']+'" alt="'+html.escape(name+': '+run['mode'].upper(),quote=True)+'"><figcaption>'+run['mode'].upper()+'</figcaption></figure>')
                    log = str(Path(run['image']).parent/'build.txt').replace('\\','/')
                    block.append('<p><a href="'+prefix+log+'">'+html.escape(ui['build_log'][index])+'</a></p>')
                records_path = 'verification/api-'+result['kind']+'/results.json'
                block.append('<p><a href="'+prefix+example['program']+'">'+html.escape(ui['download'][index])+'</a> · <a href="'+prefix+records_path+'">'+html.escape(messages['verification_records'][index])+'</a></p></section>')
                continue
            diagram = example['image']
            caption = messages['tile_image_layout'][index].format(x=diagram['x'],y=diagram['y'],px=diagram['x']*8,py=diagram['y']*8)
            block.append('<p>' + inline(caption) + '</p><pre>' + html.escape('\n'.join(diagram['rows'])) + '</pre>')
            block += ['<p>' + inline(messages[item][index]) + '</p>' for item in example['expected'] if item != 'tile_test_expected']
            for hardware in ['dmg','cgb']:
                url = prefix + 'verification/api-tiles/' + name + '-' + hardware + '.png'
                block.append('<figure><img class="screen" loading="lazy" src="' + url + '" alt="' + html.escape(name+' — '+hardware.upper()+': '+caption,quote=True) + '"><figcaption>' + hardware.upper() + '</figcaption></figure>')
            block.append('<p><a href="' + prefix + example['program'] + '">' + html.escape(ui['download'][index]) + '</a> · <a href="' + prefix + 'verification/api-tiles/' + name + '-build.txt">' + html.escape(ui['build_log'][index]) + '</a></p>')
            block.append('<details><summary>' + html.escape(messages['verification_records'][index]) + '</summary><pre>' + html.escape(json.dumps(result,indent=2)) + '</pre></details></section>')
        block.append('<!-- api-verification:end -->')
        footer = text.index('<footer',text.index('<main'))
        text = text[:footer] + ''.join(block) + text[footer:]
        entry = '<!-- api-verification:start --><a href="#api-verification">' + html.escape(title) + '</a><!-- api-verification:end -->'
        text = re.sub(r'(<nav\b[^>]*class="toc"[^>]*>.*?)(</nav>)',lambda m:m[1]+entry+m[2],text,count=1,flags=re.S)
    path.write_text(text,encoding='utf-8',newline='\r\n' if b'\r\n' in original else '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language', choices=ORDER)
    parser.add_argument('--require-complete', action='store_true')
    args = parser.parse_args()
    for language in ([args.language] if args.language else ORDER):
        report = publish(language, args.require_complete)
        print(language + ': ' + str(report['reviewed']) + ' reviewed; ' + str(report['remaining']) + ' remaining')
    (SOURCE / 'coverage.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
