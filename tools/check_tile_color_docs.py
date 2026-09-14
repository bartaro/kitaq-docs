"""Check authored color captions, sample dependencies and proof links in nine languages."""
from pathlib import Path
import hashlib,json,sys
site=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(site/'tools'))
import api_contracts
from check_input_docs import Text
messages,ui,contracts=api_contracts.load()
selected={k:c for k,c in contracts.items() if 'tile_default_blue' in c['example'].get('expected',[])}
assert len(selected)==18
tiles=json.loads((site/'verification/api-tiles/results.json').read_text(encoding='utf-8'))
assert tiles['passed']==tiles['tested']==40
for row in tiles['examples']:
    assert row['passed'] and len(row['runs'])==2
    contract=contracts['gb:'+row['api']]
    assert row['source_sha256']==hashlib.sha256((site/contract['example']['program']).read_bytes()).hexdigest()
    for run in row['runs']:
        assert run['frames_executed']==90
        assert all(run[k]==0 for k in ['result_text_pixel_mismatches','drawn_pattern_pixel_mismatches','drawn_pattern_color_mismatches'])
results=[]
for index,language in enumerate(api_contracts.ORDER):
    folder=site if language=='ja' else site/language
    pages=[(folder/(name+'.html')).read_text(encoding='utf-8') for name in ['kitaqgb','gb-library']]
    cards={name:page[start:end] for page in pages for name,start,end in api_contracts.CardRanges(page).ranges}
    proof=(folder/'verification.html').read_text(encoding='utf-8')
    for key,contract in selected.items():
        name=key.split(':')[1];card=cards[name]
        assert messages['tile_default_blue'][index] in ''.join(Text(card).parts)
        assert 'verification.html#api-gb-'+name in card
        assert 'id="api-gb-'+name+'"' in proof
        assert name+'-cgb.png' in proof and name+'-dmg.png' in proof
        assert 'assets/manual.js' in proof
        assert contract['example']['image']['cgb_colors']==[2]
        results.append({'language':language,'api':key,'passed':True})
from playwright.sync_api import sync_playwright
browser_results=[]
with sync_playwright() as playwright:
    browser=playwright.chromium.launch(executable_path='C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless=True)
    page=browser.new_page(viewport={'width':1100,'height':850})
    for language in api_contracts.ORDER:
        folder=site if language=='ja' else site/language
        name='__settilebg16_flush'
        url=(folder/'kitaqgb.html').as_uri()+'#api-'+name
        page.goto(url)
        card=page.locator('#api-'+name)
        assert card.get_attribute('open') is not None
        card.locator('a[href*="verification.html"]').click()
        section=page.locator('#api-gb-'+name)
        section.scroll_into_view_if_needed()
        for image in section.locator('img').all():
            image.scroll_into_view_if_needed();image.evaluate('(img)=>img.decode()')
            assert image.evaluate('(img)=>img.naturalWidth===160')
        section.locator('.verification-return a').click()
        page.wait_for_load_state('load')
        assert page.url==url
        page.locator('#api-'+name+'[open]').wait_for(state='visible')
        browser_results.append({'language':language,'api':name,'images_and_return':'passed'})
    browser.close()
record={'tiles':40,'changed_color_samples':18,'localized_cards':len(results),'checks':results,'browser':browser_results,
        'scope':'40 recorded tile examples; 18 changed samples rerun in DMG and CGB. Source hashes, authored color captions and return links checked.'}
(site/'verification/api-tiles/color_document_checks.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print('PASS:',len(results),'localized blue tile cards; 40 tile example records valid.')
