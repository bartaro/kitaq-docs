"""Author the reviewed entity-pool contracts and complete lifecycle demonstrations."""
import hashlib
import json
from pathlib import Path

SITE = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
REPOS = SITE.parents[1]/'publish/github_20260912'
contracts = {}
body = r'''
#include "entity.h"
u8 update_calls;
u8 draw_calls;
// Keep the observations in named state so the FC function's scratch use stays small.
u8 first;
u8 second;
u8 created;
u8 after_free;
u8 reused;
u8 after_clear;
u8 automatic_updates;
u8 automatic_draws;
u8 failures;
Entity* current_entity;

// This example chooses tile coordinates as the game's position unit.
void demo_update(u8 id) {
    Entity* entity;
    entity = entity_get(id);
    if (entity != 0) { entity->x = entity->x + 1; update_calls++; }
}

// The callback places a font character; the pool itself does not draw it.
void demo_draw(u8 id) {
    Entity* entity;
    entity = entity_get(id);
    if (entity != 0) {
        m_put((u8)entity->x, (u8)entity->y, (u8)('A' + entity->type - 1));
        draw_calls++;
    }
}

// Flush each short label/value row so the FC command queue cannot overflow.
void show_count(u8 row, const u8* label, u8 value) {
    m_text(2,row,label);
    m_put(15,row,(u8)('0'+value/100));
    m_put(16,row,(u8)('0'+(value/10)%10));
    m_put(17,row,(u8)('0'+value%10));
    m_wait();
}

void main() {
    failures = 0;
#ifdef ENTITY_EXAMPLE_FC
    m_init();
#else
    tile_example_begin(); M_LCDC = 0x91;
#endif
    // Start with an empty pool, then allocate two logical objects.
    // example:entity_init:start
    entity_init();
    if (entity_count_active() != 0) { failures++; }
    // example:entity_init:end
    // example:entity_create:start
    first = entity_create(1, 2, 12);
    second = entity_create(2, 6, 12);
    if (first == 0xFF || second == 0xFF) { failures++; }
    // example:entity_create:end
    // example:entity_count_active:start
    created = entity_count_active();
    if (created != 2) { failures++; }
    // example:entity_count_active:end
    // example:entity_get:start
    current_entity = entity_get(first);
    if (current_entity != 0) { current_entity->vx = 5; }
    else { failures++; }
    // example:entity_get:end
    // Free the first slot and show that its old ID no longer looks up an object.
    // example:entity_destroy:start
    entity_destroy(first);
    after_free = entity_count_active();
    if (entity_get(first) != 0 || after_free != 1) { failures++; }
    // example:entity_destroy:end
    reused = entity_create(3, 4, 12);
    current_entity = entity_get(reused);
    if (reused != first || current_entity == 0) { failures++; }
    else {
        // Reallocation resets fields; the old object's velocity is not retained.
        if (current_entity->vx != 0 || current_entity->sprite != 0xFF) { failures++; }
    }
    // example:entity_clear_all:start
    entity_clear_all();
    after_clear = entity_count_active();
    if (after_clear != 0 || entity_get(reused) != 0) { failures++; }
    // example:entity_clear_all:end

    // Give the callbacks two objects to process and display.
    first = entity_create(1, 2, 12);
    second = entity_create(2, 6, 12);
    // example:entity_update_all:start
    update_calls = 0;
    entity_update_all(demo_update);
    automatic_updates = update_calls;
    if (automatic_updates != 2) { failures++; }

    // example:entity_update_all:end
    if (update_calls != 2) { failures++; }
    // example:entity_draw_all:start
    draw_calls = 0;
    entity_draw_all(demo_draw);
    automatic_draws = draw_calls;
    if (automatic_draws != 2) { failures++; }

    // example:entity_draw_all:end
    if (draw_calls != 2) { failures++; }
    m_wait();
    m_text(2,0,"ENTITY POOL"); m_wait();
    show_count(2,"CREATED",created);
    show_count(3,"AFTER FREE",after_free);
    show_count(4,"REUSED ID",reused);
    show_count(5,"AFTER CLEAR",after_clear);
    show_count(7,"UPDATE CALLS",automatic_updates);
    show_count(8,"DRAW CALLS",automatic_draws);
    m_text(2,10,"ENTITIES A B"); m_wait();
    show_count(15,"FAILED CHECKS",failures);
    while (1) { m_wait(); }
}
'''

import re
names = ['entity_init','entity_create','entity_destroy','entity_get','entity_update_all','entity_draw_all','entity_count_active','entity_clear_all']
for platform in ['gb','fc']:
    root = 'kitaq' + platform
    header = '#define ENTITY_EXAMPLE_FC 1\n#include "fc_common.h"\n' if platform=='fc' else '#include "gb_tile_example.h"\n'
    full = '// Learn fixed-pool allocation, checked lookup, release, ID reuse and callback dispatch.\n// The labeled counts explain each stage; A and B mark the two active entities.\n' + header + body
    relative = 'samples/api-examples/' + platform + '/entity_pool.c'
    path = SITE/relative
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(full,encoding='utf-8',newline='\n')
    build = 'New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\' + root + '\\' + root + '.exe .\\' + root + '\\lib\\entity.c .\\kitaq-docs\\' + relative.replace('/','\\') + ' -I .\\' + root + '\\lib -I .\\kitaq-docs\\samples -o .\\out\\entity_pool.' + ('gb --profile=dev --rst-disable --stack-bank=fixed --cgb=cgb' if platform=='gb' else 'nes --mapper=nrom --nes-chr=.\\kitaq-docs\\samples\\font.chr') + ' --no-disasm'
    records = {r['name']:r for r in json.loads((SITE/'reference'/(platform+'-api.json')).read_text(encoding='utf-8'))['records']}
    for name in names:
        args = []
        notes = ['entity_capacity']
        returns = ['none']
        purpose = [name]
        if name in ['entity_init','entity_clear_all']: notes += ['entity_defaults']
        if name == 'entity_create':
            args = [['type',['entity_type']],['x, y',['entity_coordinates']]]
            returns = ['entity_id_result']
        if name in ['entity_get','entity_destroy']:
            args = [['id',['entity_slot_id']]]
            notes += ['entity_ownership']
        if name == 'entity_get': returns = ['entity_pointer_result']
        if name == 'entity_count_active': returns = ['entity_count_result']
        if name in ['entity_update_all','entity_draw_all']:
            purpose = [('entity_update_' if name=='entity_update_all' else 'entity_draw_')+platform]
            args = [['fn',['entity_callback_argument' if platform=='gb' else 'entity_fc_callback_argument']]]
            notes += ['entity_callback_order']
            if platform=='fc': notes += ['entity_fc_bank']
        snippet = re.search(r'// example:'+name+r':start\n(.*?)\s*// example:'+name+r':end',body,re.S)[1]
        # Use only the platform's branch in the printed fragment.
        snippet = re.sub(r'#ifdef ENTITY_EXAMPLE_FC\n(.*?)#else\n(.*?)#endif',lambda m:m[1] if platform=='fc' else m[2],snippet,flags=re.S)
        snippet = '\n'.join(line[4:] if line.startswith('    ') else line for line in snippet.strip('\n').splitlines())
        if name in ['entity_update_all','entity_draw_all']:
            callback = 'demo_update' if name=='entity_update_all' else 'demo_draw'
            definition = re.search(r'void '+callback+r'\(u8 id\) \{.*?^\}',body,re.S|re.M)[0]
            snippet = definition + '\n\n// From main(), after creating two entities:\n' + snippet
        record = records[name]
        contracts[platform+':'+name] = {'review':'entity-source-20260914','purpose':purpose,'args':args,'returns':returns,'notes':notes,
            'record_sha256':hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest(),
            'example':{'code':snippet,'program':relative,'build':build,'expected':['entity_example_lifecycle','entity_example_'+platform]}}
(HERE/'entity_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
sources = {}
for platform in ['gb','fc']:
    for suffix in ['h','c']:
        relative = 'kitaq'+platform+'/lib/entity.'+suffix
        sources[relative] = hashlib.sha256((REPOS/relative).read_bytes()).hexdigest()
(HERE/'entity_review_sources.json').write_text(json.dumps(sources,indent=2),encoding='utf-8')
print('16 entity contracts and two complete lifecycle programs written.')
