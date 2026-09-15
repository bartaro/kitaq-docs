"""Bind 21 PPU intrinsics to exact compiler dispatch/helpers and executed color samples."""
from pathlib import Path
import hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sys.path.insert(0,str(SITE/'tools'));import catalog;catalog.ROOT=REPOS
header=REPOS/'kitaqfc/lib/intrinsics.h';compiler=REPOS/'kitaqfc/kitaqfc/CodeGenerator.cs';source=compiler.read_text(encoding='utf-8')
declarations={r['name']:r for r in catalog.definitions(header)}
p=SITE/'reference/fc-api.json';data=json.loads(p.read_text(encoding='utf-8'));records={r['name']:r for r in data['records']}
shared=''

rows={
 '__ppu_on':('pi_on',[],'none',[]),
 '__ppu_off':('pi_off',[],'none',[]),
 '__ppu_mask_set':('pi_mask',[('value','pi_byte')],'none',[]),
 '__ppu_ctrl_set':('pi_ctrl',[('value','pi_byte')],'none',[]),
 '__ppu_addr':('pi_addr',[('ppu_addr','vq_dst_fc')],'none',['rp_timing']),
 '__ppu_data':('pi_data',[('value','pi_byte')],'none',['rp_timing']),
 '__ppu_read_status':('pi_status',[],'pi_status_return',['pi_status_note']),
 '__scroll_latch_reset':('pi_latch',[],'none',['pi_status_note']),
 '__scroll_set':('pi_scroll',[('x / y','pi_scroll_limits')],'none',['pi_status_note']),
 '__scroll_x_set':('pi_scroll_x',[('x','pi_scroll_limits')],'none',['pi_status_note']),
 '__scroll_y_set':('pi_scroll_y',[('y','pi_scroll_limits')],'none',['pi_status_note']),
 '__vram_write':('pi_write',[('ppu_addr','vq_dst_fc'),('src','rp_source'),('len','pi_length')],'none',['rp_timing']),
 '__vram_fill':('rp_fill',[('ppu_addr','vq_dst_fc'),('value','vq_fill_value'),('len','pi_length')],'none',['rp_timing']),
 '__nametable_put':('pi_put',[('x / y','pi_xy'),('tile','pi_tile')],'none',['rp_timing']),
 '__nametable_put_nt':('pi_put_nt',[('nt','pi_nt'),('x / y','pi_xy'),('tile','pi_tile')],'none',['rp_timing']),
 '__nametable_rect':('pi_rect',[('x / y','pi_xy'),('w / h','pi_extent'),('tile','pi_tile')],'none',['rp_timing']),
 '__nametable_rect_nt':('pi_rect_nt',[('nt','pi_nt'),('x / y','pi_xy'),('w / h','pi_extent'),('tile','pi_tile')],'none',['rp_timing']),
 '__attr_set':('pi_attr',[('x / y','pi_xy'),('attr','pi_attr_value')],'none',['rp_timing']),
 '__attr_set_nt':('pi_attr_nt',[('nt','pi_nt'),('x / y','pi_xy'),('attr','pi_attr_value')],'none',['rp_timing']),
 '__palette_bg_load':('pi_palette_bg',[('pal16','pi_palette_source')],'none',['pi_palette_alias','rp_timing']),
 '__palette_sp_load':('pi_palette_sp',[('pal16','pi_palette_source')],'none',['pi_palette_alias','rp_timing'])}
helpers={'__vram_write':'EmitHelperVramWrite','__vram_fill':'EmitHelperVramFill','__nametable_put':'EmitHelperNametablePut','__nametable_put_nt':'EmitHelperNametablePutNt','__nametable_rect':'EmitHelperNametableRect','__nametable_rect_nt':'EmitHelperNametableRectNt','__attr_set':'EmitHelperAttrSet','__attr_set_nt':'EmitHelperAttrSetNt','__palette_bg_load':'EmitHelperPalette','__palette_sp_load':'EmitHelperPalette','__ppu_addr':'PpuAddr'}
masked=catalog.clean(source)
def method(name):
 match=re.search(r'(?m)^ *void '+name+r'\([^\n]*\)\s*\{',masked);assert match,name
 depth=1;i=match.end()
 while depth:
  if masked[i]=='{':depth+=1
  elif masked[i]=='}':depth-=1
  i+=1
 return source[match.start():i].strip(),source.count('\n',0,match.start())+1
contracts={};evidence={}
for name,(purpose,args,returns,notes) in rows.items():
 record=records[name]
 for key in ['ret','args','signature','path','line','comment','body']:record[key]=declarations[name][key]
 match=re.search(r'case "'+name+r'":.*?(?=\n *case ")',source,re.S);assert match,name
 excerpt=match[0].strip();line=source.count('\n',0,match.start())+1
 if name in helpers:
  body,helper_line=method(helpers[name]);excerpt+='\n\n'+body
  if name.startswith('__palette_'):
   call=next(t.strip() for t in source.splitlines() if 'EmitHelperPalette("'+name+'"' in t);excerpt+='\n\n'+call
 record['definition']=None
 record['implementation_source']={'path':compiler.relative_to(REPOS).as_posix(),'line':line}
 record['implementation_excerpt']=excerpt
 fingerprint=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
 program='samples/api-examples/fc/ppu_intrinsics.c'
 text=shared+'\n'+(SITE/program).read_text(encoding='utf-8')
 match=re.search(r'// example:'+name+r':start\s*\n(.*?)\s*// example:'+name+r':end',text,re.S);assert match,name
 snippet='\n'.join(line.strip() for line in match[1].splitlines())
 build='New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqfc\\kitaqfc.exe .\\kitaq-docs\\'+program.replace('/','\\')+' -I .\\kitaqfc\\lib -I .\\kitaq-docs\\samples --nes-chr=.\\kitaq-docs\\samples\\api-examples\\fc\\vram_shapes.chr -o .\\out\\'+Path(program).stem+'.nes --no-cache --no-disasm'
 contracts['fc:'+name]={'review':'ppu-intrinsics-source-20260915','purpose':[purpose],'args':[[arg,[key]] for arg,key in args],'returns':[returns],'notes':notes,'record_sha256':fingerprint,'example':{'program':program,'code':snippet,'build':build,'expected':['pi_scene_bg','pi_scene_markers','pi_evidence']}}
 contracts['fc:'+name]['references']=[{'title':'NESdev: PPU registers','url':'https://www.nesdev.org/wiki/PPU_registers'},{'title':'NESdev: PPU scrolling','url':'https://www.nesdev.org/wiki/PPU_scrolling'}]
 evidence[name]={'record_sha256':fingerprint,'header_line':record['line']}
(HERE/'ppu_intrinsic_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'ppu_intrinsic_review_sources.json').write_text(json.dumps({'source_sha256':{p.relative_to(REPOS).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [header,compiler,REPOS/'kitaqfc/kitaqfc/Lowerer.cs']},'records':evidence},indent=2),encoding='utf-8')
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');print('21 PPU intrinsic contracts bound to compiler source and the executed scene.')
