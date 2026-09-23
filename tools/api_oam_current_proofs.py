"""Require FC OAM evidence to match the current tools, sources and executed ROMs."""
from pathlib import Path
import hashlib,json

INTRINSIC_CASES={
    'clear','set','move','tile','attr','hide','set-arguments-once','index-wrap',
    'meta-page-cross','meta-empty','meta-last-slot','dma-default','dma-selected',
    'dma-argument-side-effect','dma-raw-offset',
}
LIBRARY_CASES={
    'alias-clear','alias-set','alias-move','alias-hide',
    'meta-macro-two','meta-macro-empty','meta-macro-wrap',
    'meta-c-two','meta-c-empty','meta-c-wrap','c-hide-range',
    'fair-center','fair-limit-zero','fair-append-two','fair-last-usable-slot',
    'fair-full-cursor','fair-cycle-64',
}

def verify_oam_inputs(site,source,contracts,library=False):
    review_name='oam-library-source-20260915' if library else 'fc-oam-source-20260915'
    if not any(c['review']==review_name for c in contracts.values()):return
    folder=site/'verification'/('api-oam-library' if library else 'api-fc-oam')
    repos=site.parents[1]/'publish/github_20260912'
    if not repos.exists():repos=site.parent
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    def require(condition,message):
        if not condition:raise ValueError('OAM verification: '+message)
    compiler=sha(repos/'kitaqfc/kitaqfc.exe');emulator=sha(repos/'kurosaki/kurosaki.exe')
    review=json.loads((source/('oam_library_review_sources.json' if library else 'fc_oam_review_sources.json')).read_text(encoding='utf-8'))
    for name,expected in review['source_sha256'].items():
        file=repos/('kitaqfc/lib/'+name if library else name)
        require(sha(file)==expected,'reviewed source changed: '+name)
    state=json.loads((folder/'state_checks.json').read_text(encoding='utf-8'))
    script=repos/'kitaqfc/scripts'/('test-oam-library.py' if library else 'test-oam-intrinsics.py')
    require(sha(script)==state['script_sha256'],'state checker changed')
    for name,expected in state['library_sha256'].items():
        require(sha(repos/'kitaqfc/lib'/name)==expected,'state library changed: '+name)
    cases=state['cases'];names=LIBRARY_CASES if library else INTRINSIC_CASES
    require(len(cases)==len(names) and {r['name'] for r in cases}==names,'incomplete state matrix')
    for row in cases:
        require(row['passed'] and row['build_exit']==row['run_exit']==0,'failed state run: '+row['name'])
        require(row['compiler_sha256']==compiler and row['emulator_sha256']==emulator,'stale state executable: '+row['name'])
        require(len(row['shadow'])==256 and row['shadow']==row['expected_shadow'],'shadow bytes differ')
        require(len(row['result'])==16 and row['result']==row['expected_result'],'result bytes differ')
        expected=row['expected_shadow'] if library else row['expected_oam']
        if expected is not None:require(row['oam']==expected,'hardware OAM differs')
        if row.get('expected_oam_addr') is not None:require(row['oam_addr']==row['expected_oam_addr'],'OAMADDR differs')
        case=folder/'state'/row['name']
        for name,key in [('case.c','source_sha256'),('case.nes','rom_sha256')]:
            require(sha(case/name)==row[key],'state fixture changed: '+row['name']+'/'+name)
    report=json.loads((folder/'results.json').read_text(encoding='utf-8'))
    modes={'aliases','c-runtime','fair-pool'} if library else {'page02','page04'}
    runs=report['records'];require(len(runs)==len(modes) and {r['mode'] for r in runs}==modes,'missing teaching scenes')
    for row in runs:
        require(row['passed'] and row['build_exit']==row['run_exit']==0 and row['frames']==240,'failed teaching run')
        require(row['compiler_sha256']==compiler and row['emulator_sha256']==emulator,'stale teaching executable')
        require(row['label_pixel_mismatches']==row['sprite_pixel_mismatches']==0 and row['sprite_pixels_checked']==8704,'colored pixels differ')
        require(row['oam_matches_source'] and len(row['oam'])==256 and row['oam']==row['source_bytes'],'DMA source mismatch')
        for name,expected in row['library_sha256'].items():
            require(sha(repos/'kitaqfc/lib'/name)==expected,'teaching library changed: '+name)
        files={row['source']:row['source_sha256'],row['image']:row['image_sha256'],**row['support_sha256']}
        for name,expected in files.items():require(sha(site/name)==expected,'teaching input changed: '+name)
        require(sha((site/row['image']).with_name('example.nes'))==row['rom_sha256'],'teaching ROM changed')
