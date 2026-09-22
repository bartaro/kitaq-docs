"""Fail-closed runtime evidence and a separate FC subpixel-data lesson."""
from pathlib import Path
import hashlib,html,json,re
SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
SOURCE=SITE/'tools/api_descriptions';FOLDER=SITE/'verification/api-physics'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))

def verify_row(row):
    if not row['passed'] or row['actual']!=row['expected']:
        raise ValueError('Physics execution mismatch: '+row['source'])
    for key in ['source','rom']+(['image'] if 'image' in row else []):
        if sha(SITE/row[key])!=row[key+'_sha256']:raise ValueError('Physics evidence changed: '+row[key])
    for path,digest in row['input_sha256'].items():
        actual=REPOS/path if path.startswith(('kitaqgb/','kitaqfc/')) else SITE/path
        if sha(actual)!=digest:raise ValueError('Physics build input changed: '+path)
    platform=row['platform']
    if sha(REPOS/('kitaq'+platform)/('kitaq'+platform+'.exe'))!=row['compiler_sha256']:raise ValueError('Physics compiler changed')
    if sha(REPOS/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe'))!=row['emulator_sha256']:raise ValueError('Physics emulator changed')
    if row.get('pixel_mismatches',0) or row.get('label_pixel_mismatches',0):raise ValueError('Physics image mismatch')

def verified_examples(contracts):
    selected={k:v for k,v in contracts.items() if v['review']=='physics-source-20260915'}
    if not selected:return {}
    if len(selected)!=27:raise ValueError('Physics requires 27 individual API contracts')
    review=read(SOURCE/'physics_review_sources.json')
    for path,digest in review['source_sha256'].items():
        if sha(REPOS/path)!=digest:raise ValueError('Physics reviewed source changed: '+path)
    reports=[(FOLDER/'results.json','check_physics_examples.py',8),
             (FOLDER/'edge_checks.json','check_physics_edges.py',38),
             (FOLDER/'multiply/results.json','check_scaled_multiply.py',78)]
    for path,script,count in reports:
        report=read(path)
        if report['script_sha256']!=sha(SITE/'tools'/script):raise ValueError('Physics checker changed: '+script)
        if len(report['records'])!=count:raise ValueError('Physics matrix incomplete: '+script)
        for row in report['records']:verify_row(row)
    multiply=read(FOLDER/'multiply/results.json')
    if multiply['runner_sha256']!=sha(SITE/'tools/check_physics_edges.py'):raise ValueError('Multiply runner changed')
    fc=read(FOLDER/'fc_results.json');verify_row(fc)
    if fc['script_sha256']!=sha(SITE/'tools/check_physics_fc.py'):raise ValueError('FC physics checker changed')
    runs=read(FOLDER/'results.json')['records'];result={}
    for key,contract in selected.items():
        found=[r for r in runs if r['source']==contract['example']['program']]
        if len(found)!=2 or {r['mode'] for r in found}!={'dmg','cgb'}:raise ValueError('Missing physics sample: '+key)
        result[key]={'api':key.split(':',1)[1],'kind':'physics','runs':found}
    return result

def render_fc_module(text,language):
    """Describe the separate Q5.3 data convention beside the world/body APIs."""
    anchor='<h3 id="module-ppu">'
    if anchor not in text:return text
    text=re.sub(r'<!-- fc-physics:start -->.*?<!-- fc-physics:end -->','',text,flags=re.S)
    data=read(SOURCE/'physics_fc_module.json');prefix='' if language=='ja' else '../'
    section=data[language]
    block='<!-- fc-physics:start --><section data-module-contract="physics-source-20260915"><h3 id="physics-subpixel-data">'+html.escape(section['title'])+'</h3>'
    block+=''.join('<p>'+html.escape(p)+'</p>' for p in section['paragraphs'])
    block+='<h4>'+html.escape(section['example_title'])+'</h4><p>'+html.escape(section['expected'])+'</p>'
    block+='<div class="codebox"><span class="lang">c</span><pre><code>'+html.escape(data['code'])+'</code></pre></div>'
    block+='<figure class="example-result"><img class="screen" loading="lazy" src="'+prefix+'verification/api-physics/fc-subpixel/screen.png" alt="'+html.escape(section['expected'],quote=True)+'"><figcaption>'+html.escape(section['caption'])+'</figcaption></figure>'
    block+='<p><a href="'+prefix+'samples/api-examples/fc/physics_subpixel.c">'+html.escape(section['download'])+'</a></p>'
    block+='<h4>'+html.escape(section['build_title'])+'</h4><div class="codebox"><span class="lang">powershell</span><pre><code>'+html.escape(data['build'])+'</code></pre></div>'
    block+='</section><!-- fc-physics:end -->'
    return text.replace(anchor,block+anchor,1)
