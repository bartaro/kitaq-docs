"""Bind the FC physics port to individual contracts and executed teaching calls."""
from pathlib import Path
import copy,hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
sys.path.insert(0,str(SITE/'tools'));import catalog
catalog.ROOT=REPOS
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
texts={}
def msg(key,ja,en):
    key='fc_phys_'+key;texts[key]={'ja':ja,'en':en};return key
link=msg('link','使用するヘッダーに加え、実装の.cもコンパイルしてください。2Dはfixed.cとphysics2d.c、3Dはこれらにphysics3d.cを加えます。サンプルはMMC3、CHR RAM、描画用のPRG RAM $6800～$6FFFを使います。この描画領域は物理ライブラリ自体の要件ではありません。','Compile implementation files as well as including headers. For 2D use fixed.c and physics2d.c; for 3D also include physics3d.c. The examples use MMC3, CHR RAM and drawing storage at PRG RAM $6800–$6FFF. That drawing buffer is not a requirement of the physics library itself.')
expected={
'body2d':msg('body2d','左が衝突前、右が1刻み後です。赤い16×16の箱は中心(24,24)・速度(4,16)から中心(28,36)へ進み、青い床でY速度が0になります。各図の原点は画面(8,48)と(88,48)です。初期値、設定、積分、矩形・点判定、符号付き倍率もRAMの期待値と照合します。','Left shows the initial state; right shows one tick later. A red 16×16 box with center (24,24) and velocity (4,16) reaches (28,36), with Y velocity zero on the blue floor. Panel origins are screen (8,48) and (88,48). RAM checks also cover initialization, setters, integration, rectangle/point queries and signed scaling.'),
'surface':msg('surface','赤い物体の位置は変わりません。緑の速度線が左の(8,16)から右の(2,−8)へ変わり、青い面に対する反発と接線摩擦を表します。図の原点は画面(8,48)と(88,48)、物体の中心は図内(24,40)です。接近速度は16、交差時刻の例は192/256です。速度制限の別の呼び出しでは(300,400)が(147,196)になります。','The red body stays in place. Its green velocity line changes from (8,16) on the left to (2,−8) on the right, showing bounce and tangential friction against the blue surface. Panel origins are screen (8,48) and (88,48); the body center is local (24,40). Incoming speed is 16 and the crossing-time example returns 192/256. A separate speed-limit call reduces (300,400) to (147,196).'),
'body3d':msg('body3d','左はX/Y正面図、右はX/Z上面図です。緑の枠が初期位置(24,24,16)、赤い箱が1刻み後の(36,24,24)、青い領域が固定障害物です。X速度16は−14へ反発し、Z速度8は保持します。衝撃値は16ですが、break_speed=1でもflagsは0です。図の原点は画面(8,48)と(88,48)です。','Left is the X/Y front view; right is the X/Z top view. Green outlines mark the initial (24,24,16), red boxes show (36,24,24) after one tick, and blue regions are the static obstacle. X velocity changes from 16 to −14 while Z velocity stays 8. Impact is 16, but flags remain zero even with break_speed=1. Panel origins are screen (8,48) and (88,48).')}
data=read(SITE/'reference/fc-api.json');contracts={};sources={}
gb=read(HERE/'physics_contracts.json')
for module in ['physics2d','physics3d']:
    header=REPOS/f'kitaqfc/lib/{module}.h';impl=header.with_suffix('.c')
    declarations={r['name']:r for r in catalog.definitions(header)}
    definitions={r['name']:r for r in catalog.definitions(impl)}
    for name,decl in declarations.items():
        if 'gb:'+name not in gb:continue
        c=copy.deepcopy(gb['gb:'+name]);group=Path(c['example']['program']).stem.removeprefix('physics_')
        program=c['example']['program'].replace('/gb/','/fc/');source=(SITE/program).read_text(encoding='utf-8')
        match=re.search(r'// example:'+name+r':start\s*\n(.*?)\s*// example:'+name+r':end',source,re.S);assert match,name
        r=dict(decl);r.update(module=module,availability='implementation',definition=definitions[name],example={'source':program,'calls':[name]})
        data['records']=[old for old in data['records'] if old['name']!=name]+[r]
        c['review']='fc-physics-source-20260922';c['notes']=[k for k in c['notes'] if k!='phys_bank3']+[link]
        c['record_sha256']=hashlib.sha256(json.dumps({k:r.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
        c['example']=dict(program=program,code=match[1],expected=[expected[group]],build='New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqfc\\kitaqfc.exe .\\kitaq-docs\\'+program.replace('/','\\')+' -I .\\kitaqfc\\lib -I .\\kitaq-docs\\samples --mapper=mmc3 --nes-chr-ram -o .\\out\\physics_'+group+'.nes --no-cache --no-disasm')
        contracts['fc:'+name]=c
    data['headers']=sorted(set(data['headers']+[header.relative_to(REPOS).as_posix()]))
    for p in [header,impl]:sources[p.relative_to(REPOS).as_posix()]=sha(p)
assert len(contracts)==22,len(contracts)
modules={'fc:physics2d':['phys_module2','phys_units','phys_storage',link],'fc:physics3d':['phys_module3','phys_units','phys_impact',link]}
data['records'].sort(key=lambda r:(r['module'],r['name']))
(SITE/'reference/fc-api.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
for filename,value in [('fc_physics_contracts.json',contracts),('fc_physics_texts.json',texts),('fc_physics_modules.json',modules),('fc_physics_review_sources.json',dict(source_sha256=sources))]:
    (HERE/filename).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
print('22 FC physics contracts bound to source and individual teaching calls.')
