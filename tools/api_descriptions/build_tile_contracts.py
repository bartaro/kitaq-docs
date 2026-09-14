"""Authored exact-name tile-operation contracts and executable teaching examples.

The matrix is a reviewed mapping, not a guess based on substrings. Each row
selects an actual VRAM addressing mode and data operation from CodeGenerator.cs.
"""
import hashlib
import json
import textwrap
from pathlib import Path

SITE = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
REPOS = SITE.parents[1] / 'publish/github_20260912'
REVIEW = 'tile-source-20260914'
contracts = {}
english = {}
for message_file in OUT.glob('*texts.json'):
    english.update({key: value[0] for key, value in json.loads(message_file.read_text(encoding='utf-8')).items()})


def add(name, purpose, args, notes, operation, assertions, map1, declarations='', image_rows=None, colors=None, image_origin=(2,3)):
    # Each file contains one demonstrated call; shared setup is documented.
    path = 'samples/api-examples/gb/' + name + '.c'
    explanation = ' '.join(english[key] for key in purpose[:2])
    program = ('// ' + name + '\n' + '\n'.join('// ' + line for line in textwrap.wrap(explanation, width=86)) + '\n'
               '// Expected: FAILED CHECKS 000, with the written tile data in the selected map.\n'
               '#include "gb_tile_example.h"\n' + declarations + '\nvoid main() {\n'
               '    u8 failures;\n    failures = 0;\n    tile_example_begin();\n'
               + '\n'.join('    ' + line for line in operation.splitlines()) + '\n'
               + '\n'.join('    if (' + test + ') { failures++; }' for test in assertions) + '\n'
               + '    tile_example_finish(failures, ' + str(int(map1)) + ');\n}\n')
    destination = SITE / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(program, encoding='utf-8', newline='\n')
    build = ('New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqgb\\kitaqgb.exe .\\kitaq-docs\\' + path.replace('/', '\\')
             + ' -I .\\kitaqgb\\lib -I .\\kitaq-docs\\samples -o .\\out\\' + name
             + '.gb --profile=dev --rst-disable --stack-bank=fixed --cgb=cgb --no-disasm')
    contracts['gb:' + name] = {'review': REVIEW, 'purpose': purpose, 'args': args,
        'returns': ['none'], 'notes': notes + ['tile_example_setup'],
        'example': {'code': program, 'standalone': True, 'program': path,
                    'build': build, 'expected': ['tile_test_expected'],
                    'image': {'x':image_origin[0],'y':image_origin[1],'rows':image_rows or ['A'], 'cgb_colors': colors or [0]}}}


# Exact dispatch names, selected map, and data operation from the compiler.
scalar = [
    ('__settile', 'map_fixed', 'tile', False),
    ('__settile_unsafe', 'map_fixed', 'tile', True),
    ('__settile_fast', 'map_fixed', 'tile', True),
    ('__settileat', 'map_explicit', 'tile', False),
    ('__settileat_unsafe', 'map_explicit', 'tile', True),
    ('__settilebg', 'map_bg', 'tile', False),
    ('__settile_xy', 'map_bg', 'tile', False),
    ('__settilebg_unsafe', 'map_bg', 'tile', True),
    ('__settilewin', 'map_win', 'tile', False),
    ('__settilewin_unsafe', 'map_win', 'tile', True),
    ('__settileattr', 'map_fixed', 'attr', False),
    ('__settileattr_unsafe', 'map_fixed', 'attr', True),
    ('__settileatattr', 'map_explicit', 'attr', False),
    ('__settileatattr_unsafe', 'map_explicit', 'attr', True),
    ('__settilebgattr', 'map_bg', 'attr', False),
    ('__settilebgattr_unsafe', 'map_bg', 'attr', True),
    ('__settilewinattr', 'map_win', 'attr', False),
    ('__settilewinattr_unsafe', 'map_win', 'attr', True),
    ('__settilecgb', 'map_fixed', 'both', False),
    ('__settilecgb_unsafe', 'map_fixed', 'both', True),
    ('__settileatcgb', 'map_explicit', 'both', False),
    ('__settileatcgb_unsafe', 'map_explicit', 'both', True),
    ('__settilebgcgb', 'map_bg', 'both', False),
    ('__settilebgcgb_unsafe', 'map_bg', 'both', True),
    ('__settilewincgb', 'map_win', 'both', False),
    ('__settilewincgb_unsafe', 'map_win', 'both', True),
]
for name, mode, kind, fast in scalar:
    dest = '0x9862' if mode == 'map_fixed' else '0x9C62'
    other = '0x9C62' if mode == 'map_fixed' else '0x9862'
    args = [['x, y', ['tile_xy']]]
    values = ['2', '3']
    if mode == 'map_explicit':
        args.insert(0, ['base', ['map_explicit']])
        values.insert(0, '0x9C00')
    if kind in ('tile', 'both'):
        args.append(['tile', ['tile_id']]); values.append("'A'")
    if kind in ('attr', 'both'):
        args.append(['attr', ['tile_attribute']]); values.append('KQ_CGB_ATTR(2, 0, 0, 0, 0)')
    preparation = '' if kind != 'attr' else '__settileat(' + ('0x9800' if mode == 'map_fixed' else '0x9C00') + ", 2, 3, 'A');\n"
    checks = ["tile_example_read(" + dest + ", 0) != 'A'", 'tile_example_read(' + other + ', 0) != 0']
    if kind in ('attr', 'both'):
        checks += ['__cgb_is_cgb() && tile_example_read(' + dest + ', 1) != 2', '__cgb_is_cgb() && tile_example_read(' + other + ', 1) != 0']
    notes = ['bank_current'] if kind == 'tile' else ['attr_mode'] if kind == 'attr' else []
    declaration = 'void __settile_fast(u8 x, u8 y, u8 tile);\n' if name == '__settile_fast' else ''
    add(name, [{'tile':'write_tile','attr':'write_attr','both':'write_both'}[kind], mode, 'unsafe' if fast else 'safe'], args, notes,
        preparation + name + '(' + ', '.join(values) + ');', checks, mode != 'map_fixed', declaration, colors=[2] if kind != 'tile' else [0])
    if kind != 'tile': contracts['gb:' + name]['example']['expected'].append('tile_example_blue')
    if name == '__settile_fast': contracts['gb:' + name]['syntax'] = '__settile_fast(x, y, tile);'

bulk = [('__settile_bulk','tile',False), ('__settile_bulk_fast','tile',True),
        ('__settileattr_bulk','attr',False), ('__settileattr_bulk_fast','attr',True),
        ('__settilecgb_bulk','both',False), ('__settilecgb_bulk_fast','both',True)]
for name, kind, fast in bulk:
    declarations = "const u8 example_tiles[] = {'A','B','C'};\nconst u8 example_attrs[] = {1,2,3};\n"
    args = [['dest', ['tile_dest']]]
    if kind == 'both':
        args += [['tile_src, attr_src', ['tile_sources']]]
        call = name + '(0x9862, example_tiles, example_attrs, 3);'
    else:
        args += [['src', ['tile_sources']]]
        call = name + '(0x9862, ' + ('example_tiles' if kind == 'tile' else 'example_attrs') + ', 3);'
    if kind == 'attr': call = '__settile_bulk(0x9862, example_tiles, 3);\n' + call
    args += [['count', ['tile_count']]]
    checks = ["tile_example_read(0x9862, 0) != 'A'", "tile_example_read(0x9863, 0) != 'B'", "tile_example_read(0x9864, 0) != 'C'", 'tile_example_read(0x9865, 0) != 0']
    if kind != 'tile': checks += ['__cgb_is_cgb() && tile_example_read(0x9862, 1) != 1', '__cgb_is_cgb() && tile_example_read(0x9864, 1) != 3']
    notes = ['bank_current'] if kind == 'tile' else ['attr_mode'] if kind == 'attr' else ['write_both']
    add(name, [{'tile':'bulk_tiles','attr':'bulk_attrs','both':'bulk_both'}[kind], 'unsafe' if fast else 'safe'], args, notes + ['source_lifetime'], call, checks, False, declarations, image_rows=['ABC'], colors=[1,2,3] if kind != 'tile' else [0,0,0])
    if kind != 'tile': contracts['gb:' + name]['example']['expected'].append('tile_example_rgb')

rectangles = [
    ('__settile_rect', 'tile_rect_fill', "__settile_rect(2, 3, 3, 2, 'A');", [['x, y',['tile_xy']], ['w, h',['tile_rect_size']], ['tile',['tile_id']]], '', ["tile_example_read(0x9C62, 0) != 'A'", "tile_example_read(0x9C84, 0) != 'A'", 'tile_example_read(0x9C65, 0) != 0']),
    ('__settile_row', 'tile_row', '__settile_row(2, 3, example_tiles, 3);', [['x, y',['tile_xy']], ['src',['tile_sources']], ['len',['tile_count']]], "const u8 example_tiles[] = {'A','B','C'};\n", ["tile_example_read(0x9C62, 0) != 'A'", "tile_example_read(0x9C64, 0) != 'C'", 'tile_example_read(0x9C82, 0) != 0']),
    ('__settile_col', 'tile_col', '__settile_col(2, 3, example_tiles, 3);', [['x, y',['tile_xy']], ['src',['tile_sources']], ['len',['tile_count']]], "const u8 example_tiles[] = {'A','B','C'};\n", ["tile_example_read(0x9C62, 0) != 'A'", "tile_example_read(0x9CA2, 0) != 'C'", 'tile_example_read(0x9C63, 0) != 0']),
    ('__settilemap_rect', 'tile_map_rect', '__settilemap_rect(0x9C00, 2, 3, 3, 2, example_tiles);', [['base',['map_explicit']], ['x, y',['tile_xy']], ['w, h',['tile_rect_size']], ['src',['tile_sources']]], "const u8 example_tiles[] = {'A','B','C','D','E','F'};\n", ["tile_example_read(0x9C62, 0) != 'A'", "tile_example_read(0x9C84, 0) != 'F'", 'tile_example_read(0x9C65, 0) != 0'])
]
for name, purpose, call, args, declarations, checks in rectangles:
    notes = ['bank_current'] + (['tile_source_row_limit'] if name in ('__settile_row','__settile_col') else [])
    rows = {'__settile_rect':['AAA','AAA'], '__settile_row':['ABC'], '__settile_col':['A','B','C'], '__settilemap_rect':['ABC','DEF']}[name]
    add(name, [purpose,'safe'], args, notes, call, checks, True, declarations, image_rows=rows)

buffer_declarations = '''u8 example_tiles[1024];
u8 example_attrs[1024];
void __memset(void* dest, u8 value, u16 len);
void __settilebg16_buf(u8* buf, u8 x, u8 y, u8 tile);
void __settilebg16cgb_buf(u8* tilebuf, u8* attrbuf, u8 x, u8 y, u8 tile, u8 attr);
void __settilebg16_flush(const u8* buf, u8 y, u8 x, u8 count);
void __settilebg16cgb_flush(const u8* tilebuf, const u8* attrbuf, u8 y, u8 x, u8 count);
'''
buffer_rows = [('__settilebg16_buf',False,False), ('__settilebg16cgb_buf',True,False),
               ('__settilebg16_flush',False,True), ('__settilebg16cgb_flush',True,True)]
for name, attributes, flush in buffer_rows:
    setup = '__memset(example_tiles, 0, 1024);\n__memset(example_attrs, 0, 1024);\n'
    if flush:
        setup += "example_tiles[66]='A'; example_tiles[67]='B';\nexample_tiles[98]='C'; example_tiles[99]='D';\n"
        if attributes: setup += 'example_attrs[66]=2; example_attrs[67]=2;\nexample_attrs[98]=2; example_attrs[99]=2;\n'
        setup += name + '(' + ('example_tiles, example_attrs' if attributes else 'example_tiles') + ', 1, 2, 2);'
        purpose = ['tile_quad_flush'] + (['write_both'] if attributes else []) + ['safe']
        args = [[('tilebuf, attrbuf' if attributes else 'buf'),['tile_buffer_storage']], ['y, x, count',['tile_quad_flush_xy']]]
        syntax = name + '(' + ('tilebuf, attrbuf' if attributes else 'buf') + ', y, x, count);'
    else:
        setup += name + '(' + ('example_tiles, example_attrs' if attributes else 'example_tiles') + ", 1, 1, 'A'" + (', 2' if attributes else '') + ');\n'
        setup += '// The buffer operation must not write to VRAM yet.\nif (tile_example_read(0x9C42, 0) != 0) { failures++; }\n'
        setup += '// Transfer the prepared cell so its four characters can be seen.\n'
        setup += ('__settilebg16cgb_flush(example_tiles, example_attrs' if attributes else '__settilebg16_flush(example_tiles') + ', 1, 2, 2);'
        purpose = ['tile_quad'] + (['tile_quad_attr'] if attributes else [])
        args = [[('tilebuf, attrbuf' if attributes else 'buf'),['tile_quad_buffer']], ['x, y',['tile_quad_xy']], ['tile',['tile_id']]]
        if attributes: args.append(['attr',['tile_attribute']])
        syntax = name + '(' + ('tilebuf, attrbuf' if attributes else 'buf') + ', x, y, tile' + (', attr' if attributes else '') + ');'
    checks = ["tile_example_read(" + address + ", 0) != '" + char + "'" for address,char in [('0x9C42','A'),('0x9C43','B'),('0x9C62','C'),('0x9C63','D')]]
    checks += ["example_tiles[66] != 'A'", "example_tiles[99] != 'D'", 'tile_example_read(0x9C44, 0) != 0']
    if attributes: checks += ['example_attrs[66] != 2', 'example_attrs[99] != 2', '__cgb_is_cgb() && tile_example_read(0x9C42, 1) != 2', '__cgb_is_cgb() && tile_example_read(0x9C63, 1) != 2']
    add(name, purpose, args, ['bank_current'] if not attributes and flush else [], setup, checks, True,
        buffer_declarations, image_rows=['AB','CD'], colors=[2] if attributes else [0], image_origin=(2,2))
    contracts['gb:' + name]['syntax'] = syntax
    contracts['gb:' + name]['example']['expected'] = ['tile_test_expected', 'tile_quad_example']
    if attributes: contracts['gb:' + name]['example']['expected'].append('tile_quad_blue')

# Preserve the exact inventory fingerprint and the source files reviewed for this batch.
records = json.loads((SITE/'reference/gb-api.json').read_text(encoding='utf-8'))['records']
for record in records:
    key = 'gb:' + record['name']
    if key in contracts:
        contracts[key]['record_sha256'] = hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
(OUT/'tile_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
sources = {str(p.relative_to(REPOS)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [REPOS/'kitaqgb/kitaqgb/CodeGenerator.cs',REPOS/'kitaqgb/lib/cgb_tile.h']}
(OUT/'tile_review_sources.json').write_text(json.dumps(sources,indent=2),encoding='utf-8')
print(str(len(contracts)) + ' exact-name tile contracts and complete examples written.')
