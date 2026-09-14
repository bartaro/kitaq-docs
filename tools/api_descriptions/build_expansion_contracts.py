"""Author the exact D1-channel and digital-microphone contracts; expose the emulator boundary."""
from pathlib import Path
import json,hashlib,re
SITE=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
templates=json.loads((HERE/'expansion_templates.json').read_text(encoding='utf-8'))
records={r['name']:r for r in json.loads((SITE/'reference/fc-api.json').read_text(encoding='utf-8'))['records']}
program='samples/api-examples/fc/expansion_input.c'
source=(SITE/program).read_text(encoding='utf-8')
messages={};entries=[];contracts={}
for port,address in [(1,'$4016'),(2,'$4017')]:
    for name,template in [('__pad_read'+str(port)+'_d1','read'),('__exp_pad_read'+str(port),'alias')]:
        key='ex_purpose_'+name
        messages[key]=[value.format(port=port,address=address) for value in templates[template]]
        entries.append((name,[key],['pad_raw_result'],['pad_raw_layout','ex_protocol','ex_limit']))
entries += [('__joypad2p_voice',['ex_voice_alias','ex_mic'],['ex_mic_result'],['ex_mic_reads','ex_limit']),
            ('__mic_read2p',['ex_mic'],['ex_mic_result'],['ex_mic_reads','ex_limit'])]
for name,purpose,returns,notes in entries:
    snippet=re.search(r'// example:'+name+r':start\n(.*?)\s*// example:'+name+r':end',source,re.S)[1]
    snippet='\n'.join(line[4:] if line.startswith('    ') else line for line in snippet.strip('\n').splitlines())
    contracts['fc:'+name]={'review':'expansion-source-20260915','purpose':purpose,'args':[],'returns':returns,'notes':notes,
      'record_sha256':hashlib.sha256(json.dumps({k:records[name].get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest(),
      'example':{'code':snippet,'program':program,'expected':['ex_example','ex_limit'],
      'build':'New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqfc\\kitaqfc.exe .\\kitaq-docs\\samples\\api-examples\\fc\\expansion_input.c -I .\\kitaq-docs\\samples -I .\\kitaqfc\\lib -o .\\out\\expansion_input.nes --mapper=nrom --nes-chr=.\\kitaq-docs\\samples\\font.chr --no-cache --no-disasm'}}
(HERE/'expansion_purpose_texts.json').write_text(json.dumps(messages,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'expansion_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
print('Six expansion-input and microphone contracts written.')
