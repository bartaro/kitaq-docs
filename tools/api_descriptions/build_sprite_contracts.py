"""Bind 28 sprite library APIs to source-backed, authored multilingual explanations."""
from pathlib import Path
import hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sys.path.insert(0,str(SITE/'tools'))
import catalog
catalog.ROOT=REPOS
contracts={};evidence={}
shared=(SITE/'samples/sprite_example_checks.h').read_text(encoding='utf-8')
def fragment(name):
    match=re.search(r'// example:'+name+r':start\s*\n(.*?)\s*// example:'+name+r':end',shared,re.S)
    assert match,name
    return '\n'.join(line[4:] if line.startswith('    ') else line for line in match[1].splitlines())
for platform in ['gb','fc']:
    inventory=SITE/'reference'/(platform+'-api.json');data=json.loads(inventory.read_text(encoding='utf-8'))
    records={r['name']:r for r in data['records']};lib=REPOS/('kitaq'+platform)/'lib'
    declarations={r['name']:r for r in catalog.definitions(lib/'sprite.h')}
    definitions={r['name']:r for r in catalog.definitions(lib/'sprite.c') if r['body']}
    shadow=['sp_shadow'];coords=[('id','sp_id'),('x','sp_x'),('y','sp_y_'+platform)]
    rows={
        'sprite_init':('sp_init',[],'none',['sp_init_'+platform+'_note'],'sp_demo_allocation'),
        'sprite_alloc':('sp_alloc',[],'sp_alloc_return',shadow,'sp_demo_allocation'),
        'sprite_free':('sp_free',[('id','sp_id')],'none',shadow,'sp_demo_allocation'),
        'sprite_set_pos':('sp_pos_'+platform,coords,'none',shadow+['sp_wrap'],'sp_demo_geometry'),
        'sprite_set_tile':('sp_tile',[('id','sp_id'),('tile','sp_tile_arg')],'none',shadow,'sp_demo_animation'),
        'sprite_set_flags':('sp_flags',[('id','sp_id'),('flags','sp_flags_arg')],'none',shadow+['sp_flags_'+platform],'sp_demo_geometry'),
        'sprite_hide':('sp_hide',[('id','sp_id')],'none',shadow,'sp_demo_allocation'),
        'sprite_flush_oam_now':('sp_now',[],'none',['sp_dma_'+platform],'sp_demo_geometry'),
        'sprite_flush_oam':('sp_flush_'+platform,[],'none',['sp_dma_'+platform],'sp_demo_geometry'),
        'sprite_count_used':('sp_count',[],'sp_number_return',[],'sp_demo_allocation'),
        'sprite_max_scanline_count':('sp_peak',[],'sp_number_return',['sp_peak_note'],'sp_demo_scan'),
        'sprite_warn_scanline_overflow':('sp_warn',[],'sp_warn_return',['sp_peak_note'],'sp_demo_scan'),
        'metasprite_draw':('sp_meta',[('first_id','sp_id'),('x','sp_x'),('y','sp_y_'+platform),('parts','sp_parts_arg'),('count','sp_count_arg')],'sp_meta_return',shadow+['sp_meta_note'],'sp_demo_allocation'),
        'anim_update':('sp_anim',[('anim','sp_anim_arg')],'sp_anim_return',['sp_anim_note'],'sp_demo_animation')
    }
    snippets={
        'sprite_set_pos':'sprite_set_pos(0,88,SPRITE_EXAMPLE_Y(16)); // Visible top-left: (88,16).',
        'sprite_set_tile':'sprite_set_tile(5,129); // Select the green square beside ANIMATION.',
        'sprite_set_flags':'sprite_set_flags(1,SPRITE_FLAG_XFLIP);\nsprite_set_flags(2,SPRITE_FLAG_YFLIP);',
        'sprite_flush_oam_now':'// Rendering is disabled here; all shadow entries have been prepared.\nsprite_flush_oam_now();',
        'sprite_flush_oam':'while(1) { sprite_flush_oam(); } // Transfer prepared sprites at the next frame boundary.',
        'sprite_count_used':'sprite_example_expect(sprite_count_used()==9); // After hiding, freeing and drawing the pair.'
    }
    program='samples/api-examples/'+platform+'/sprite_shapes.c'
    build='New-Item -ItemType Directory -Force .\\out | Out-Null\n'
    build+='.\\kitaq'+platform+'\\kitaq'+platform+'.exe .\\kitaq-docs\\'+program.replace('/','\\')+' -I .\\kitaq'+platform+'\\lib -I .\\kitaq-docs\\samples -o .\\out\\sprite_shapes.'+('gb' if platform=='gb' else 'nes')
    build+=(' --profile=dev --rst-disable --stack-bank=fixed --cgb=cgb' if platform=='gb' else ' --nes-chr=.\\kitaq-docs\\samples\\sprite_example.chr')+' --no-cache --no-disasm'
    for name,(purpose,args,returns,notes,expected) in rows.items():
        if platform=='gb':notes=notes+['sp_gb_full_build']
        record=records[name];declaration=declarations[name]
        for key in ['ret','args','signature','path','line','comment','body']:record[key]=declaration[key]
        record['definition']=definitions[name]
        fingerprint=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
        contract={'review':'sprite-source-20260915','purpose':[purpose],'args':[[arg,[key]] for arg,key in args],
            'returns':[returns],'notes':notes,'record_sha256':fingerprint,
            'example':{'program':program,'code':snippets[name] if name in snippets else fragment(name),
                       'build':build,'expected':list(dict.fromkeys([expected,'sp_demo_intro','sp_demo_geometry','sp_demo_colors','sp_demo_scan']))}}
        contracts[platform+':'+name]=contract
        evidence[platform+':'+name]={'path':record['path'],'line':record['line'],'record_sha256':fingerprint}
    inventory.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    for suffix in ['c','h']:
        path=lib/('sprite.'+suffix);evidence[path.relative_to(REPOS).as_posix()]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
(HERE/'sprite_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'sprite_review_sources.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
print('28 sprite contracts bound to current public library sources.')
