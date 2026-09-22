"""Document PPU software-shadow getters, with explicit direct-write limitations."""
from pathlib import Path
import copy,hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
sys.path.insert(0,str(SITE/'tools'));import catalog
catalog.ROOT=REPOS
header=REPOS/'kitaqfc/lib/intrinsics.h';compiler=REPOS/'kitaqfc/kitaqfc/CodeGenerator.cs';code=compiler.read_text(encoding='utf-8')
decls={r['name']:r for r in catalog.definitions(header)}
path=SITE/'reference/fc-api.json';data=json.loads(path.read_text(encoding='utf-8'));contracts={};texts={}
base=json.loads((HERE/'ppu_declaration_contracts.json').read_text(encoding='utf-8'))['fc:nes_ppu_screen_on']
source=(SITE/base['example']['program']).read_text(encoding='utf-8')
for register,ja,en in [('ctrl','PPUCTRLのソフトウェア側の保持値を返します。NMIの有効設定、パターンテーブル、アドレス増分などを保存して一時設定後に戻す用途です。','Return the software shadow of PPUCTRL. Use it to save NMI enable, pattern-table selection and address increment before a temporary change.'),('mask','PPUMASKのソフトウェア側の保持値を返します。背景・スプライトの描画、左端表示、グレースケール、色強調の設定を保存して戻す用途です。','Return the software shadow of PPUMASK. Use it to preserve rendering, left-edge visibility, grayscale and color-emphasis settings.')]:
    name='__ppu_'+register+'_get';r=dict(decls[name]);match=re.search(r'case "'+name+r'":.*?(?=\n *case ")',code,re.S);assert match
    r.update(module='intrinsics',availability='compiler',definition=None,implementation_excerpt=match[0].strip(),implementation_source={'path':compiler.relative_to(REPOS).as_posix(),'line':code.count('\n',0,match.start())+1})
    data['records']=[old for old in data['records'] if old['name']!=name]+[r]
    key='ppu_shadow_'+register;texts[key]={'ja':ja,'en':en}
    c=copy.deepcopy(base);c.update(review='ppu-shadow-source-20260922',purpose=[key],args=[],returns=['ppu_shadow_return'],notes=['ppu_shadow_limits'])
    c['example']['code']=re.search(r'// example:'+name+r':start\s*\n(.*?)\s*// example:'+name+r':end',source,re.S)[1]
    c['record_sha256']=hashlib.sha256(json.dumps({k:r.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest();contracts['fc:'+name]=c
texts['ppu_shadow_return']={'ja':'最後にライブラリまたは組み込み関数が設定した制御値をu8で返します。PPUSTATUSを読みません。','en':'Return the last control value maintained by the library or intrinsic setters as u8. This does not read PPUSTATUS.'}
texts['ppu_shadow_limits']={'ja':'PPUCTRLとPPUMASKは書き込み専用です。この関数はハードウェアを読み戻すものではありません。$2000/$2001への直接書き込みや独自のアセンブリ操作は保持値に反映されません。設定は対応する__ppu_*_setなどを使って揃えてください。読み出しでラッチや割り込み状態は変わりません。','en':'PPUCTRL and PPUMASK are write-only. This getter does not read hardware. Direct writes to $2000/$2001 or custom assembly bypass the shadows. Use the corresponding __ppu_*_set operations consistently. Reading the shadow does not change the latch or interrupt state.'}
data['records'].sort(key=lambda r:(r['module'],r['name']));path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
for name,value in [('ppu_shadow_contracts.json',contracts),('ppu_shadow_texts.json',texts)]:
    (HERE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
print('Two PPU shadow-getter contracts authored.')
