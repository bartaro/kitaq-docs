"""Bind peripheral descriptions to unmodified captures and scoped unit evidence."""
from pathlib import Path
import hashlib,html,json,re
from api_physics_proofs import verify_row
from api_mapper_proofs import write_page
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.is_dir():REPOS=SITE.parent
REVIEW='peripheral-source-20260923';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def verified_examples(contracts):
    selected={k:v for k,v in contracts.items() if v['review']==REVIEW}
    if not selected:return {}
    assert len(selected)==13
    for p,h in read(SITE/'tools/api_descriptions/peripheral_review_sources.json')['source_sha256'].items():assert sha(REPOS/p)==h
    folder=SITE/'verification/api-peripheral'
    for name,script,count in [('keyboard','test-keyboard-row-selection.py',4),('masks','test-peripheral-bit-masks.py',8)]:
        report=read(folder/('state/'+name+'.json'))
        assert report['script_sha256']==sha(REPOS/'kitaqfc/scripts'/script)
        assert report['compiler_sha256']==sha(REPOS/'kitaqfc/kitaqfc.exe') and report['emulator_sha256']==sha(REPOS/'kurosaki/kurosaki.exe')
        assert len(report['records'])==count and all(r['passed'] for r in report['records'])
        for r in report['records']:
            if name=='keyboard':
                assert r['selected']=={'1':[[row,col,True] for row in range(9) for col in range(2)],'2':[[row,col,True] for row in range(10) for col in range(2)],'3':[[9,0,True]]}
                assert r['final_outputs']==[0,0,0] and min(r['reset_delays'])>=16 and min(r['read_delays'])>=50
                assert r['scan_bytes']==[0]*18 and r['ram']==[165,0,85,170]
            else:assert r['actual']==r['expected'] and r['patches']
    report=read(folder/'example/results.json');assert report['script_sha256']==sha(SITE/'tools/check_peripheral_examples.py')
    rows=report['records'];assert len(rows)==6
    values=dict(keyboard=[0]*21,zapper=[0,0,1,0,0,1,0,1],serial=[0])
    assert {r['mode'] for r in rows}=={m+'-'+v for m in values for v in ['default','unoptimized']}
    for r in rows:
        verify_row(r);assert r['actual']==values[r['mode'].rsplit('-',1)[0]]+[165]
        assert r['port_writes']==r['expected_writes'] and r['port_reads']==r['expected_reads']
    result={}
    for key,c in selected.items():
        ex=c['example'];source=(SITE/ex['program']).read_text(encoding='utf-8')
        assert ex['code'] in source and re.search(r'\b'+key.split(':')[1]+r'\s*\(',ex['code'])
        runs=[r for r in rows if r['source']==ex['program'] and r['mode'].endswith('-default')];assert len(runs)==1
        result[key]=dict(api=key.split(':')[1],kind='peripheral',runs=runs)
    return result
def overview(text,language,library=False):
    import api_contracts as api
    messages,ui,contracts=api.load();proofs=verified_examples(contracts)
    selected={k:contracts[k] for k in proofs};api.attach_verified_images(selected,proofs)
    records={r['name']:r for r in read(SITE/'reference/fc-api.json')['records']}
    for name,start,end in reversed(api.CardRanges(text).ranges):
        key='fc:'+name
        if key not in selected:continue
        r=records[name];c=selected[key]
        fp=hashlib.sha256(json.dumps({k:r.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest();assert fp==c['record_sha256']
        text=text[:start]+api.render(r,c,language,messages,ui)+text[end:]
    if library:
        groups=[('keyboard.h','キーボードの行列入力','Keyboard matrix input',
                 '接続パターンの検査、18バイトへの全行走査、1行・1列群の読み取りを提供します。文字の変換やキーリピートは行いません。',
                 'Provides a presence-pattern probe, a complete 18-byte scan, and one-row/group reads. It does not convert characters or implement key repeat.',
                 ['__fkb_detect','__fkb_scan','__fkb_read_row_col']),
                ('zapper.h','光線銃の入力線','Light-gun input lines',
                 '各ポートの生ビット、トリガー、受光線を読みます。番号なし関数はポート2です。照準座標や命中判定はゲーム側で組み立てます。',
                 'Reads raw bits, trigger and light lines on each port. Unsuffixed functions select port 2. Aim coordinates and hit testing belong to game code.',
                 ['__zapper_raw1','__zapper_raw2','__zapper_trigger1','__zapper_trigger2','__zapper_light1','__zapper_light2','__zapper_trigger','__zapper_light']),
                ('intrinsics.h','シリアルの1ビット入出力','Single-bit serial I/O',
                 '外部アダプター向けにOUT0出力とD4入力を扱います。1回の操作は1ビットだけで、通信速度やバイトの枠組みは呼び出し側が管理します。',
                 'Provides OUT0 output and D4 input for an external adapter. Each operation handles one bit; the caller controls timing and byte framing.',
                 ['__serial_tx_bit','__serial_rx_bit'])]
        block='<!-- peripheral-guide:start --><section id="peripheral-input-guide">'
        for i,(header,ja,en,jp,ep,names) in enumerate(groups):
            block+='<h3 id="peripheral-group-'+str(i)+'">'+html.escape(header+' — '+(ja if language=='ja' else en))+'</h3><p>'+html.escape(jp if language=='ja' else ep)+'</p><p>'
            block+=' · '.join('<a href="kitaqfc.html#api-'+name+'"><code>'+name+'</code></a>' for name in names)+'</p>'
        index=api.ORDER.index(language);block+='<p>'+api.inline(messages['peripheral_baseline'][index])+'</p></section><!-- peripheral-guide:end -->'
        text=re.sub(r'<!-- peripheral-guide:start -->.*?<!-- peripheral-guide:end -->','',text,flags=re.S)
        anchor=re.search(r'<h2 id="6-[^"]+">',text);assert anchor
        text=text[:anchor.start()]+block+text[anchor.start():]
    return text
if __name__=='__main__':
    import api_contracts as api
    for language in ['ja','en']:
        for name in ['kitaqfc','fc-library']:
            path=(SITE if language=='ja' else SITE/language)/(name+'.html');write_page(path,overview(path.read_text(encoding='utf-8'),language,name=='fc-library'))
    contracts=api.load()[2];keys={p+':'+r['name'] for p in ['gb','fc'] for r in read(SITE/('reference/'+p+'-api.json'))['records']}
    assert set(contracts)<=keys
    report=dict(active_languages=['ja','en'],reviewed=len(contracts),remaining=len(keys-set(contracts)),missing=sorted(keys-set(contracts)))
    (SITE/'tools/api_descriptions/coverage.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('13 peripheral APIs rendered;',report['reviewed'],'reviewed;',report['remaining'],'remaining')
