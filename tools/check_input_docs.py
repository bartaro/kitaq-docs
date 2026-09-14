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
    parser.add_argument('--suite',choices=['input','padrepeat','expansion'],default='input');args=parser.parse_args()
    messages,ui,contracts=api_contracts.load()
    inputs={key:value for key,value in contracts.items() if value['review']==args.suite+'-source-20260915'}
    results=[]
    for index,language in enumerate(api_contracts.ORDER):
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
                    assert contract['example']['code'].strip() in content,(language,key,'sample')
                    assert 'verification.html#api-'+platform+'-'+name in card,(language,key,'proof link')
                    results.append({'language':language,'api':key,'card':'passed'})
    assert len(results)==len(inputs)*9 and len(inputs)==(35 if args.suite=='input' else 6), len(results)
    modules=json.loads((api_contracts.SOURCE/'input_modules.json').read_text(encoding='utf-8')) if args.suite=='input' else {}
    module_count=0
    for index,language in enumerate(api_contracts.ORDER):
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
            for language in api_contracts.ORDER:
                folder=SITE if language=='ja' else SITE/language
                cases=[('gb','kitaqgb','__readpadex'),('fc','kitaqfc','__pad_dirs'),('fc','fc-library','input_repeat'),('fc','fc-library','nes_pad_repeat_step')] if args.suite=='input' else [('gb','kitaqgb','__padrep_lr'),('gb','kitaqgb','__padrep_mask')]
                if args.suite=='expansion':cases=[('fc','kitaqfc',name) for name in ['__pad_read1_d1','__exp_pad_read2','__mic_read2p']]
                for platform,volume,name in cases:
                    url=(folder/(volume+'.html')).as_uri()+'#api-'+name
                    page.goto(url)
                    card=page.locator('#api-'+name)
                    assert card.get_attribute('open') is not None
                    card.locator('a[href*="verification.html"]').click()
                    section=page.locator('#api-'+platform+'-'+name)
                    section.scroll_into_view_if_needed()
                    for img in section.locator('img').all():
                        img.scroll_into_view_if_needed()
                        img.evaluate('(img) => img.decode()')
                        assert img.evaluate('(img) => img.naturalWidth > 0')
                    section.locator('.verification-return a').click()
                    page.wait_for_load_state('load')
                    assert page.url==url,(page.url,url)
                    page.locator('#api-'+name+'[open]').wait_for(state='visible')
                    browser_results.append({'language':language,'api':platform+':'+name,'images_and_return':'passed'})
            browser.close()
    report={'cards':results,'module_introductions':module_count,'browser':browser_results,'status':'passed'}
    report_name='document_checks.json' if args.browser else 'static_document_checks.json'
    evidence_folder={'input':'api-input','padrepeat':'api-pad-repeat','expansion':'api-expansion-input'}[args.suite]
    (SITE/'verification'/evidence_folder/report_name).write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(str(len(results))+' localized cards; '+str(len(browser_results))+' browser image/return checks passed.')

if __name__=='__main__':main()
