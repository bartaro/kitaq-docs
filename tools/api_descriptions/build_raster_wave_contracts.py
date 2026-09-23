"""Author the six scanline-wave operations from their current implementation."""
from pathlib import Path
import hashlib, json, sys
HERE=Path(__file__).resolve().parent; SITE=HERE.parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists(): REPOS=SITE.parent
sys.path.insert(0,str(SITE/'tools'))
import catalog
catalog.ROOT=REPOS
texts={}; contracts={}; reviews={}
def text(key,ja,en):
    key='raster_wave_'+key; texts[key]={'ja':ja,'en':en}; return key
none=text('none','戻り値はありません。','No return value.')
effect=text('effect','初期化済みのRasterLineXへのポインターです。呼び出し中は有効な領域を保持してください。','Pointer to an initialized RasterLineX that remains valid throughout the call.')
profile=text('profile','0（FLAT）は変位なし、1（X_TITLE）は16ライン周期で−4～+3ピクセル、2（TRAVEL_GATE）は64ライン周期で±24ピクセルです。それ以外は変位なしになります。','0 (FLAT) applies no displacement; 1 (X_TITLE) repeats offsets −4..+3 pixels every 16 lines; 2 (TRAVEL_GATE) repeats a ±24-pixel wave every 64 lines. Other values apply no displacement.')
timing=text('timing','対象は背景レイヤーの横スクロールです。スプライトやウィンドウは変形しません。RunFrameは可視144ラインの間CPUを専有し、割り込みを止めます。ゲーム更新や音声更新は呼び出し間に行い、STAT割り込みによる別のラスター処理と併用しないでください。','The effect changes horizontal background scrolling; sprites and the window do not bend. RunFrame owns the CPU and masks interrupts during all 144 visible lines. Update game logic and audio between calls, and do not combine this renderer with a STAT raster interrupt driver.')
wrap=text('wrap','SCXは8ビット値で、背景は256ピクセル幅で折り返します。負の変位は256を法とする値になります。画面外からスクロールしてくる部分も含め、背景マップを用意してください。','SCX is an eight-bit value and the background wraps at 256 pixels. Negative displacements use modulo-256 byte values. Populate the map beyond the visible viewport as well.')
verification=text('verification','掲載画像はKOKURA上のDMG/CGB実行結果です。縦の柱と文字を含む160×144画素を各ラインの期待座標と照合しています。実機でのタイミングは未確認です。','Images come from DMG and CGB runs in KOKURA. Every pixel of the 160×144 scene, including pillars and text, is compared with the expected per-line coordinates. Hardware timing has not been tested.')
wave_expected=text('wave_expected','縦の柱の縁と文字が、横方向に±24ピクセル曲がります。64ラインで波が一周し、波の位相は1フレームごとに1ライン分進みます。CGBでは青い柱と文字になります。画面全体が同じ量だけ動くのではなく、各行の横位置が異なることを見てください。','The pillars and letters bend horizontally by up to 24 pixels. One wave spans 64 scanlines, and its phase advances by one line per frame. CGB uses blue pillars and lettering. Look for a different horizontal offset on each row, rather than uniform movement of the whole screen.')
title_expected=text('title_expected','ORBIT GUARDという独自のタイトルが、強い波を伴って右から入ります。48回描画した後は小さな揺れに切り替わり、96回以降は静止します。160回で演出を繰り返します。掲載画像は登場中、小さな揺れ、静止の順です。','The original title ORBIT GUARD enters from the right with a large wave. After 48 rendered frames it changes to a small ripple; from frame 96 it is stationary. The entrance repeats after 160 frames. The images show arrival, the small ripple and the settled title in that order.')
launch=text('launch','kitaqgb・kokura・kitaq-docsを同じ親フォルダーに置き、その親フォルダーでPowerShellを開いてビルドします。ROMはDMG/CGB両対応です。KOKURAの--hardwareにdmgまたはcgbを指定して確認できます。','Place kitaqgb, kokura and kitaq-docs under one parent directory and open PowerShell there. The ROM supports both DMG and CGB; select dmg or cgb with KOKURA --hardware.')
dataset=json.loads((SITE/'reference/gb-api.json').read_text(encoding='utf-8'))
records={r['name']:r for r in dataset['records']}
definitions={n:{r['name']:r for r in catalog.definitions(REPOS/('kitaqgb/lib/raster.'+n))} for n in ['h','c']}

def add(short,ja,en,args,code,title=False,notes=(),returns=None):
    name='Raster_LineX'+short; record=records[name]
    declaration=definitions['h'][name]
    for k in ['ret','args','signature','path','line','comment','body']: record[k]=declaration[k]
    record['definition']=definitions['c'][name]
    fingerprint=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
    lesson='raster_title_entry' if title else 'raster_wave'
    example=dict(program='samples/api-examples/gb/'+lesson+'.c',code=code,
                 build='New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqgb\\kitaqgb.exe .\\kitaq-docs\\samples\\api-examples\\gb\\'+lesson+'.c -I .\\kitaqgb\\lib -I .\\kitaq-docs\\samples -o .\\out\\'+lesson+'.gb --profile=dev --rst-disable --stack-bank=fixed --cgb=cgb --no-cache --no-disasm\n.\\kokura\\kokura-cli.exe .\\out\\'+lesson+'.gb --hardware cgb --run-frames 120 --png .\\out\\'+lesson+'.png',
                 expected=[title_expected if title else wave_expected],
                 snippet_source='samples/api-examples/gb/raster_wave.c')
    assert code in (SITE/example['snippet_source']).read_text(encoding='utf-8'),name
    contracts['gb:'+name]=dict(review='raster-wave-source-20260922',record_sha256=fingerprint,
        purpose=[text(short+'_purpose',ja,en)],args=args,returns=[returns or none],
        notes=list(notes)+[wrap,timing,verification,launch],example=example)
    reviews['gb:'+name]=dict(record_sha256=fingerprint,header_line=record['line'],definition_line=record['definition']['line'])

add('Init','波形の種類と基準横位置を設定し、位相0・毎フレーム1段階の速度で初期化します。描画やスクロールレジスターの書き込みは行いません。','Initialize the profile and base X, with phase zero and one phase step per frame. This call does not draw or write scroll registers.',
    [['effect',[text('init_effect','書き込み可能なRasterLineXへのポインターです。事前の初期化は不要です。','Pointer to writable RasterLineX storage; no prior initialization is required.')]],['profile',[profile]],['base_x',[text('base','波形変位に加える背景の横位置（0～255ピクセル）です。','Background X added to the wave displacement, in pixels (0..255).')]]],
    'Raster_LineXInit(&wave, KQ_RASTER_LINE_TRAVEL_GATE, 0);')
add('SetProfile','波形の種類を変更し、位相とフレーム分周カウンターを0に戻します。基準横位置と速度は保持します。','Select a profile and reset the phase and frame-divider counter to zero. Preserve base X and speed.',
    [['effect',[effect]],['profile',[profile]]], 'Raster_LineXSetProfile(&wave, KQ_RASTER_LINE_X_TITLE);',title=True)
add('SetSpeed','位相を進める量と、その更新間隔を設定します。分周カウンターは0へ戻りますが、現在の位相は保持します。','Set the phase increment and update interval. Reset the divider counter while preserving the current phase.',
    [['effect',[effect]],['phase_step',[text('step','1回の更新で加える位相（0～255）です。0は波形を停止させます。255は8ビットの折り返しにより1段階ずつ逆方向へ進みます。','Phase increment per update (0..255). Zero freezes the wave. A value of 255 moves backwards by one step through eight-bit wraparound.')]],['frame_divider',[text('divider','何回のRunFrame呼び出しで位相を更新するか（1～255）です。0は1として扱います。LCDがオフで描画しなかった呼び出しは数えません。','Number of rendered RunFrame calls per phase update (1..255). Zero selects one. Calls that return because the LCD is off do not count.')]]],
    'Raster_LineXSetSpeed(&wave, 1, 1);')
add('SetPhase','波の現在位置を直接指定します。基準横位置、速度、分周カウンターは変えません。','Set the wave position directly, preserving base X, speed and the divider counter.',
    [['effect',[effect]],['phase',[text('phase','位相の8ビット値です。実際の波形は種類に応じて16または64で折り返します。','Eight-bit phase value; the selected wave repeats every 16 or 64 steps.')]]],
    'Raster_LineXSetPhase(&wave, 8);')
add('GetOffset','指定ラインで使うSCXを計算します。状態や画面は変更せず、位相も進めません。','Calculate SCX for a requested line without changing state, the display or the phase.',
    [['effect',[effect]],['ly',[text('ly','波形を調べるライン番号（0～255）です。可視画面のラインは0～143です。範囲外エラーは返さず、波形の周期で折り返します。','Line coordinate to query (0..255); visible lines are 0..143. The lookup wraps at the wave period instead of reporting a range error.')]]],
    'wave_lookup = Raster_LineXGetOffset(&wave, 0);',returns=text('offset','基準横位置とその行の波形変位を加えた8ビットのSCXです。サンプルの位相8・行0では17になります。','Eight-bit SCX equal to base X plus that row’s displacement. The sample lookup at phase 8, line 0 returns 17.'))
add('RunFrame','VBlankから次の画面の144ラインを描画し、各ラインの背景横位置を更新します。描画後に分周カウンターを進め、指定間隔で位相を更新します。','Wait for VBlank and render the following 144 visible lines with per-line background X. Afterwards advance the divider counter and update phase at the selected interval.',
    [['effect',[effect]]], 'Raster_LineXRunFrame(&wave);',
    notes=[text('lcd','LCDがオフなら、状態を変えず直ちに戻ります。LCDがオンの場合は144行分のSCX更新が済むまで待ちます。割り込みの許可状態を復元し、最後のSCXをScrollヘルパーの追跡値へ反映します。戻った時点がVBlank内である保証はありません。呼び出し直後にVRAMへ直接書き込まず、VBlankを待つか、書き込みタイミングを管理する転送関数を使ってください。','If the LCD is off, return immediately without changing the effect. Otherwise block until SCX has been updated for all 144 rows, restore the interrupt-enable state and synchronize the Scroll helper with the final SCX. Return does not guarantee that VBlank is active. Before writing directly to VRAM, wait for VBlank or use a transfer routine that manages safe access timing.')])
# The state object's base_x member supplies the common horizontal position.
assert len(contracts)==6
for name,data in [('raster_wave_contracts.json',contracts),('raster_wave_texts.json',texts),('raster_wave_review_sources.json',{'records':reviews,'source_sha256':{'kitaqgb/lib/raster.'+ext:hashlib.sha256((REPOS/('kitaqgb/lib/raster.'+ext)).read_bytes()).hexdigest() for ext in ['h','c']}})]:
    (HERE/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(SITE/'reference/gb-api.json').write_text(json.dumps(dataset,ensure_ascii=False,indent=2),encoding='utf-8')
print(str(len(contracts))+' individually authored scanline-wave contracts')
