"""Check all authored input cards and exercise evidence navigation in a real browser."""
import argparse
import json
from pathlib import Path
import sys
import re
from html.parser import HTMLParser
import api_contracts

SITE=Path(__file__).resolve().parents[1]

class Text(HTMLParser):
    def __init__(self,source):
        super().__init__();self.parts=[];self.feed(source)
    def handle_data(self,data):self.parts.append(data)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--browser',action='store_true')
    parser.add_argument('--suite',choices=['all','rng','bit-intrinsics','memory-intrinsics','interrupt-intrinsics','input','padrepeat','expansion','vram','vram-memory','vramq','cgb-palette','cgb-dma-wram','asset','bank','sprite','oam','fc-oam','oam-library','vram-macros','runtime-queue','runtime-ppu','ppu-declarations','ppu-intrinsics'],default='input');args=parser.parse_args()
    messages,ui,contracts=api_contracts.load()
    inputs={key:value for key,value in contracts.items() if args.suite=='all' or value['review']==args.suite+'-source-20260915'}
    results=[]
    for language in api_contracts.ACTIVE_LANGUAGES:
        index=api_contracts.ORDER.index(language)
        folder=SITE if language=='ja' else SITE/language
        for platform in ['gb','fc']:
            for volume in ['kitaq'+platform,platform+'-library']:
                text=(folder/(volume+'.html')).read_text(encoding='utf-8')
                for name,start,end in api_contracts.CardRanges(text).ranges:
                    key=platform+':'+name
                    if key not in inputs:continue
                    contract=inputs[key];card=text[start:end]
                    content=''.join(Text(card).parts)
                    for message in contract['purpose']+contract['returns']+contract['notes']+contract['example']['expected']:
                        expected=(messages if message in messages else ui)[message][index].replace('`','')
                        assert expected in content,(language,key,message)
                    for parameter,keys in contract['args']:
                        assert parameter in content,(language,key,parameter)
                        for message in keys:assert messages[message][index].replace('`','') in content,(language,key,message)
                    for reference in contract.get('references',[]):assert 'href="'+reference['url']+'"' in card,(language,key,'reference')
                    assert contract['example']['code'].strip() in content,(language,key,'sample')
                    for additional in contract['example'].get('additional',[]):
                        assert additional['code'].strip() in content,(language,key,'additional sample')
                        assert additional['program'] in card,(language,key,'additional source')
                        for message in additional['expected']:assert messages[message][index].replace('`','') in content,(language,key,message)
                    assert 'class="example-result"' in card,(language,key,'inline screen')
                    assert 'verification.html#api-' not in card,(language,key,'external proof link')
                    assert not re.search(r'href="[^"]*verification/[^"#]*\.(?:txt|json|log)',card),(language,key,'raw log link')
                    results.append({'language':language,'api':key,'card':'passed'})
    assert len(results)==len(inputs)*len(api_contracts.ACTIVE_LANGUAGES) and len(inputs)=={'all':len(contracts),'rng':13,'bit-intrinsics':8,'memory-intrinsics':12,'interrupt-intrinsics':8,'input':35,'padrepeat':6,'expansion':6,'vram':30,'vram-memory':9,'vramq':10,'cgb-palette':28,'cgb-dma-wram':8,'asset':17,'bank':32,'sprite':28,'oam':1,'fc-oam':9,'oam-library':8,'vram-macros':5,'runtime-queue':4,'runtime-ppu':7,'ppu-declarations':4,'ppu-intrinsics':21}[args.suite], len(results)
    modules=json.loads((api_contracts.SOURCE/(args.suite+'_modules.json')).read_text(encoding='utf-8')) if args.suite in ['rng','input','vram','cgb-palette','asset','bank','sprite','oam-library','runtime-queue','runtime-ppu'] else {}
    module_count=0
    for language in api_contracts.ACTIVE_LANGUAGES:
        index=api_contracts.ORDER.index(language)
        folder=SITE if language=='ja' else SITE/language
        for key,keys in modules.items():
            platform,name=key.split(':')
            text=(folder/(platform+'-library.html')).read_text(encoding='utf-8')
            block=re.search(r'<h3[^>]*id="module-'+name+r'".*?<!-- api-module:end -->',text,re.S)
            assert block,(language,key)
            for message in keys:assert api_contracts.inline(messages[message][index]) in block[0],(language,key,message)
            module_count+=1
    browser_results=[]
    if args.browser:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(executable_path='C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless=True)
            page=browser.new_page(viewport={'width':1100,'height':850})
            for language in api_contracts.ACTIVE_LANGUAGES:
                folder=SITE if language=='ja' else SITE/language
                cases=[('gb','kitaqgb','__readpadex'),('fc','kitaqfc','__pad_dirs'),('fc','fc-library','input_repeat'),('fc','fc-library','nes_pad_repeat_step')] if args.suite=='input' else [('gb','kitaqgb','__padrep_lr'),('gb','kitaqgb','__padrep_mask')]
                if args.suite=='expansion':cases=[('fc','kitaqfc',name) for name in ['__pad_read1_d1','__exp_pad_read2','__mic_read2p']]
                if args.suite=='vram':cases=[('gb','gb-library','vram_queue_bg_rect'),('fc','fc-library','vram_queue_bg_block'),('fc','fc-library','vram_flush_now')]
                if args.suite=='vram-memory':cases=[('gb','kitaqgb',name) for name in ['__vram_copy_dma','__fill_tilemap','__vram_memset_unsafe']]
                if args.suite=='vramq':cases=[('fc','kitaqfc',name) for name in ['__vramq_copy','__vramq_clear','__vramq_clear_overflow']]
                if args.suite=='cgb-palette':cases=[('gb','gb-library','cgb_bg_colors_raw'),('gb','gb-library','KQ_CGB_ATTR_PRIORITY_IF'),('gb','kitaqgb','__cgb_safe_set_bgpd')]
                if args.suite=='cgb-dma-wram':cases=[('gb','kitaqgb',name) for name in ['__cgb_safe_set_hdma5','__svbk_set','__cgb_safe_set_svbk']]
                if args.suite=='asset':cases=[('gb','gb-library','asset_load_tiles'),('fc','fc-library','asset_load_raw'),('fc','kitaqfc','__far_memcpy')]
                if args.suite=='bank':cases=[('gb','gb-library','far_call'),('gb','kitaqgb','__farcall_ptr'),('fc','fc-library','farptr_read16'),('fc','kitaqfc','__prg_bank_set')]
                if args.suite=='sprite':cases=[('gb','gb-library','sprite_set_flags'),('gb','gb-library','metasprite_draw'),('fc','fc-library','sprite_set_pos'),('fc','fc-library','sprite_max_scanline_count')]
                if args.suite=='oam':cases=[('gb','kitaqgb','__oam_dma')]
                if args.suite=='rng':cases=[(k.split(':')[0],('kitaq'+k.split(':')[0]) if k.split(':')[1].startswith('__') else k.split(':')[0]+'-library',k.split(':')[1]) for k in inputs]
                if args.suite=='bit-intrinsics':cases=[(p,'kitaq'+p,n) for p in ['gb','fc'] for n in ['__bit_test','__bit_set','__bit_clear','__bit_toggle']]
                if args.suite=='memory-intrinsics':cases=[(p,'kitaq'+p,n) for p in ['gb','fc'] for n in ['__memcpy','__memset_small','__copy32']]
                if args.suite=='interrupt-intrinsics':cases=[('fc','kitaqfc',name) for name in ['__nmi_ready','__nmi_wait','__irq_save','__irq_restore']]
                if args.suite=='ppu-intrinsics':cases=[('fc','kitaqfc',name) for name in ['__ppu_off','__scroll_x_set','__attr_set_nt','__palette_sp_load']]
                if args.suite=='ppu-declarations':cases=[('fc','fc-library',name) for name in ['nes_ppu_screen_on','nes_ppu_load_palette','nes_ppu_clear_nt']]
                if args.suite=='runtime-ppu':cases=[('fc','fc-library',name) for name in ['nes_ppu_seek','nes_ppu_write_bytes','nes_wait_nmi']]
                if args.suite=='runtime-queue':cases=[('fc','fc-library',name) for name in ['nes_vram_queue_clear','nes_vram_queue_try_write','nes_vram_queue_nmi_flush']]
                if args.suite=='vram-macros':cases=[('fc','fc-library',name) for name in ['nes_vram_copy','nes_vram_commit','nes_vram_clear_queue']]
                if args.suite=='oam-library':cases=[('fc','fc-library',name) for name in ['nes_oam_dma','nes_metasprite_draw','OAM_FairDraw']]
                if args.suite=='fc-oam':cases=[('fc','kitaqfc',name) for name in ['__sprite_set','__metasprite_draw','__oam_dma_page']]
                if args.suite=='all':cases=[('gb','kitaqgb','__settile'),('gb','gb-library','entity_update_all'),('gb','kitaqgb','__cgb_safe_set_bgpd'),('fc','fc-library','nes_ppu_seek'),('fc','kitaqfc','__palette_sp_load'),('fc','fc-library','nes_ppu_clear_nt')]
                for platform,volume,name in cases:
                    url=(folder/(volume+'.html')).as_uri()+'#api-'+name
                    page.goto(url)
                    card=page.locator('#api-'+name)
                    assert card.get_attribute('open') is not None
                    shots=card.locator('figure.example-result img')
                    assert shots.count()>0
                    for img in shots.all():
                        img.scroll_into_view_if_needed()
                        img.evaluate('(img) => img.decode()')
                        assert img.evaluate('(img) => img.naturalWidth > 0')
                    assert page.url==url,(page.url,url)
                    page.locator('#api-'+name+'[open]').wait_for(state='visible')
                    browser_results.append({'language':language,'api':platform+':'+name,'inline_images':'passed'})
            browser.close()
    report={'languages':api_contracts.ACTIVE_LANGUAGES,'cards':results,'module_introductions':module_count,'browser':browser_results,'status':'passed'}
    report_name='document_checks.json' if args.browser else 'static_document_checks.json'
    evidence_folder={'all':'.','rng':'api-rng','bit-intrinsics':'api-bit-intrinsics','memory-intrinsics':'api-memory-intrinsics','interrupt-intrinsics':'api-interrupt-intrinsics','input':'api-input','padrepeat':'api-pad-repeat','expansion':'api-expansion-input','vram':'api-vram','vram-memory':'api-vram-memory','vramq':'api-vramq','cgb-palette':'api-cgb-palette','cgb-dma-wram':'api-cgb-dma-wram','asset':'api-asset','bank':'api-bank','sprite':'api-sprite','oam':'api-oam','fc-oam':'api-fc-oam','oam-library':'api-oam-library','vram-macros':'api-vram-macros','runtime-queue':'api-runtime-queue','runtime-ppu':'api-runtime-ppu','ppu-declarations':'api-ppu-declarations','ppu-intrinsics':'api-ppu-intrinsics'}[args.suite]
    (SITE/'verification'/evidence_folder/report_name).write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(str(len(results))+' localized cards; '+str(len(browser_results))+' browser inline-image checks passed.')

if __name__=='__main__':main()
