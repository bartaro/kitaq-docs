"""Render reviewed Wire3D feedback in every active manual edition.
Run after API-card rendering. Numeric evidence is from original examples only.
"""
from pathlib import Path
import json,re,html
import api_contracts as api
from publication_languages import ACTIVE_LANGUAGES,ORDER
S=Path(__file__).resolve().parents[1]
repos=S.parents[1]/"publish/github_20260912"
if not repos.exists():repos=S.parent
LIB=repos/"kitaqgb/lib"
A=S/"tools/api_descriptions"
texts=json.loads((A/"wire3d_feedback_texts.json").read_text(encoding="utf-8"))
data=json.loads((S/"reference/gb-api.json").read_text(encoding="utf-8"));byname={r["name"]:r for r in data["records"]}
contracts=json.loads((A/"wire3d_feedback_contracts.json").read_text(encoding="utf-8"))
new_names=["Wire3DDMG_ProjectCameraPoint","Wire3DCGB_ProjectCameraPoint","Wire3DDMG_EndFrameNow"]
# Preserve the separately reviewed physics extension already in the public HTML.
validation_records=data["records"]+[{"name":"kq3d_overlap_sphere_aabb"}]
rows=json.loads((S/"verification/wire3d-feedback-20261009/results.json").read_text(encoding="utf-8"))["runtime"]
messages,ui,allcontracts=api.load()
for language in ACTIVE_LANGUAGES:
 f=S/('' if language=='ja' else language)/'gb-library.html';text=f.read_text(encoding='utf-8');index=ORDER.index(language);prefix='' if language=='ja' else '../'
 replacements=[]
 for name,start,end in api.CardRanges(text).ranges:
  r=byname.get(name)
  if r and r['module'] in ['wire3d_dmg','wire3d_cgb']:
   replacements.append((start,end,api.render(r,allcontracts['gb:'+name],language,messages,ui)))
 for start,end,value in reversed(replacements):text=text[:start]+value+text[end:]
 title=texts['wf_feedback_title'][language]
 block='<section id="wire3d-feedback-20261009"><h3>'+html.escape(title)+'</h3>'
 for key in ['profile','bytes','projection','transfer','startup','clock','metrics','validation','diagnostics','provenance']:block+='<p>'+api.inline(texts['wf_feedback_'+key][language])+'</p>'
 block+='<p><a href="'+prefix+'verification/wire3d-feedback-20261009/results.json">'+html.escape(texts['wf_feedback_evidence'][language])+'</a> · <a href="'+prefix+'samples/wire3d_clocked/README.md">C / BGM / HUD</a></p>'
 labels={'ja':['設定','中央値 / 最悪（PPUフレーム）','期限超過 / 47'],'en':['Profile','Median / worst (PPU frames)','Deadline misses / 47'],'ko':['설정','중앙값 / 최악 (PPU 프레임)','기한 초과 / 47'],'zh-CN':['配置','中位数 / 最差（PPU帧）','期限超限 / 47'],'zh-TW':['設定','中位數 / 最差（PPU幀）','期限超過 / 47'],'fr':['Profil','Médiane / maximum (images PPU)','Dépassements / 47'],'es':['Perfil','Mediana / peor (fotogramas PPU)','Plazos excedidos / 47'],'de':['Profil','Median / Maximum (PPU-Bilder)','Fristüberschreitungen / 47']}[language]
 block+='<table><thead><tr><th>'+labels[0]+'</th><th>fps</th><th>'+labels[1]+'</th><th>'+labels[2]+'</th></tr></thead><tbody>'
 for row in rows:
  interval=row['interval_ppu_frames'];block+=f'<tr><td><code>{row["profile"]}</code></td><td>{row["completed_upload_fps"]:.3f}</td><td>{interval["median"]:.3f} / {interval["worst"]:.3f}</td><td>{row["deadline_misses"]}</td></tr>'
 block+='</tbody></table>'
 for kind in ['dmg','cgb']:block+=f'<figure class="example-result"><img class="screen" loading="lazy" src="{prefix}verification/wire3d-feedback-20261009/{kind}-88.png" alt="Original {kind.upper()} box and bar gauge"><figcaption>{kind.upper()} 128×88 · '+html.escape(texts['wf_feedback_provenance'][language])+'</figcaption></figure>'
 for name in new_names:block+=api.render(byname[name],contracts['gb:'+name],language,messages,ui)
 block+='</section>'
 text=re.sub(r'<section id="wire3d-feedback-20261009">.*?</section>','',text,flags=re.S)
 anchor='<h3 id="module-wire3d_dmg"';assert anchor in text;text=text.replace(anchor,block+anchor,1)
 # Update the three full-header appendix entries with current source.
 for kind in ['dmg','cgb']:
  name=f'wire3d_{kind}.h';pattern=r'(<details class="searchable"(?: id="[^"]+")?><summary><code>'+name+r'</code>.*?</summary><div class="codebox">.*?<pre><code>)(.*?)(</code></pre>.*?<p class="source">kitaqgb/lib/'+name+r'</p></details>)'
  text,n=re.subn(pattern,lambda m:m[1]+html.escape((LIB/name).read_text(encoding='utf-8').strip())+m[3],text,count=1,flags=re.S);assert n==1,(language,name)
 api.validate_rendered_volume(text,validation_records,'gb-library');f.write_bytes(text.encode('utf-8'));print('RENDER',language,flush=True)
print('All active editions updated')
