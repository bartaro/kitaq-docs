"""Bind the six GB repeat-state intrinsics to their reviewed implementations."""
from pathlib import Path
import json,hashlib,re
SITE=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
program='samples/api-examples/gb/pad_repeat_state.c'
source=(SITE/program).read_text(encoding='utf-8')
records={r['name']:r for r in json.loads((SITE/'reference/gb-api.json').read_text(encoding='utf-8'))['records']}
returns=[
 'Zero when no action pulse is due; otherwise one of {bits}. The nonzero result is a button bit, not a normalized Boolean or a count of repeats.',
 '操作のパルスが発生しない場合は0、それ以外は{bits}のいずれかです。0以外の値はボタンのビットであり、0か1に正規化した真偽値やリピート回数ではありません。',
 '동작 펄스가 없으면 0, 있으면 {bits} 중 하나입니다. 0이 아닌 값은 버튼 비트이며, 0과 1로 정규화된 논리값이나 반복 횟수가 아닙니다.',
 '没有操作脉冲时返回0，否则返回{bits}之一。非零结果是按钮位，不是归一化布尔值，也不是连发次数。',
 '沒有操作脈衝時回傳0，否則回傳{bits}之一。非零結果是按鈕位元，不是正規化布林值，也不是連發次數。',
 'Cero si no corresponde emitir un pulso; en caso contrario, uno de estos valores: {bits}. El resultado distinto de cero es un bit de botón, no un booleano normalizado ni un recuento de repeticiones.',
 'Zero quando não há pulso de ação; caso contrário, um destes valores: {bits}. O resultado diferente de zero é um bit de botão, não um booleano normalizado nem uma contagem de repetições.',
 'Zéro si aucune impulsion n’est due ; sinon, une des valeurs suivantes : {bits}. Le résultat non nul est un bit de bouton, pas un booléen normalisé ni un nombre de répétitions.',
 'Null, wenn kein Aktionsimpuls fällig ist, andernfalls einer der Werte {bits}. Ein Wert ungleich null ist ein Tastenbit, kein normalisierter Wahrheitswert und keine Anzahl von Wiederholungen.'
]
messages={};contracts={}
for name,purpose,bits in [('__padrep_init','pr_init',None),('__padrep_reset','pr_reset',None),('__padrep_lr','pr_lr','1, 2'),('__padrep_down','pr_down','8'),('__padrep','pr_mask','1, 2, 4, 8, 16, 32, 64, 128'),('__padrep_mask','pr_alias','1, 2, 4, 8, 16, 32, 64, 128')]:
    args=[['state',['pr_state']]]
    syntax='void '+name+'(u8* state);'
    result=['none'];notes=[]
    if name=='__padrep_init':
        args += [['das',['pr_das']],['arr',['pr_arr']]]
        syntax='void __padrep_init(u8* state, u8 das, u8 arr);'
    if bits:
        args += [['keys',['pr_keys']],['trigger',['pr_trigger']]]
        notes=['input_logical_layout','pr_das','pr_arr','pr_update_note']
        syntax='u8 '+name+'(u8* state, u8 keys, u8 trigger'
        if name in ['__padrep','__padrep_mask']:
            args += [['mask',['pr_filter']]]; syntax+=', u8 mask'
        syntax+=');'
        key='pr_result_'+name;messages[key]=[text.format(bits=bits) for text in returns];result=[key]
    snippet=re.search(r'// example:'+name+r':start\n(.*?)\s*// example:'+name+r':end',source,re.S)[1]
    snippet='\n'.join(line[4:] if line.startswith('    ') else line for line in snippet.strip().splitlines())
    contract={'review':'padrepeat-source-20260915','purpose':[purpose]+(['pr_mask'] if name=='__padrep_mask' else []),'syntax':syntax,'args':args,'returns':result,'notes':notes,
      'record_sha256':hashlib.sha256(json.dumps({k:records[name].get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest(),
      'example':{'code':snippet,'program':program,'expected':['pr_example'],
      'build':'New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqgb\\kitaqgb.exe .\\kitaq-docs\\samples\\api-examples\\gb\\pad_repeat_state.c -I .\\kitaq-docs\\samples -I .\\kitaqgb\\lib -o .\\out\\pad_repeat_state.gb --profile=dev --rst-disable --stack-bank=fixed --cgb=cgb --no-cache --no-disasm'}}
    contracts['gb:'+name]=contract
(HERE/'padrepeat_return_texts.json').write_text(json.dumps(messages,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'padrepeat_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
print('Six GB repeat-state contracts written.')
