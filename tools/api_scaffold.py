"""Create API anchors for the required, evidence-checked contract renderer."""
import html
import json
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]


def section(platform, intrinsic, language, modules):
    from api_contracts import load
    contracts = load()[2]
    records = json.loads((SITE/'reference'/(platform+'-api.json')).read_text(encoding='utf-8'))['records']
    records = [r for r in records if r['name'].startswith('__') == intrinsic]
    missing = [r['name'] for r in records if platform+':'+r['name'] not in contracts]
    if missing:
        raise ValueError('Individual API explanations are required: '+', '.join(missing))
    title = ('組み込み命令' if intrinsic else 'ライブラリAPI')+'辞典' if language == 'ja' else ('Compiler intrinsic' if intrinsic else 'Library API')+' dictionary'
    intro = ('全'+str(len(records))+'項目。各項目では、機能、引数、戻り値、制約、使用例と期待する結果を説明します。') if language == 'ja' else (str(len(records))+' entries. Each entry explains the operation, arguments, return value, constraints, usage example and expected result.')
    out = ['<h2 id="api">'+title+'</h2><p>'+intro+'</p>']
    for module in sorted({r['module'] for r in records}):
        # Headerless compiler records use a category name, not a fictitious include.
        suffix = '' if platform == 'gb' and module == 'intrinsics' else '.h'
        out.append('<h3 id="module-'+html.escape(module,quote=True)+'">'+html.escape(module+suffix+' — '+modules.get(module,module))+'</h3>')
        for record in sorted((r for r in records if r['module']==module),key=lambda r:r['name'].lower()):
            name = html.escape(record['name'],quote=True)
            # publish(require_complete=True) must replace every placeholder. No
            # purpose is guessed from a function name or a legacy example schema.
            out.append('<details class="api searchable" id="api-'+name+'"><summary><code>'+name+'</code></summary></details>')
    return ''.join(out)
