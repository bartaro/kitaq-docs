"""A wireframe refresh must preserve adjacent library content and all anchors."""
from pathlib import Path
import json,re
from fc_wireframe_presentation import overview
SITE=Path(__file__).resolve().parents[1]
rows=[]
for language in ['ja','en']:
    path=SITE/('en' if language=='en' else '')/'fc-library.html'
    before=path.read_bytes().decode('utf-8')
    after=overview(before,language)
    # Idempotence also detects accidental movement, duplication or accumulation.
    assert after==before,(language,'non-idempotent refresh')
    assert re.findall(r'\bid="([^"]+)"',after)==re.findall(r'\bid="([^"]+)"',before)
    marker='<p id="unrelated-fixture">An independently inserted library note.</p>'
    inserted=before.replace('<h3 id="module-wire3d">',marker+'<h3 id="module-wire3d">',1)
    assert marker in overview(inserted,language)
    for name in ['zx0_decompress','zx0_decompress_vram','asset_decompress']:
        assert after.count('id="api-'+name+'"')==1,(language,name)
    rows.append(dict(language=language,passed=True,preserved_zx0_apis=3))
(SITE/'verification/api-wireframe-fc/presentation-checks.json').write_text(json.dumps(dict(passed=True,records=rows),indent=2),encoding='utf-8')
print('PASS: JA/EN refresh is idempotent and preserves unrelated modules and anchors')
