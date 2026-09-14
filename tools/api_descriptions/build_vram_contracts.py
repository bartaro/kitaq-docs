"""Bind all 30 VRAM library APIs to reviewed source contracts and complete samples."""
from pathlib import Path
import json, hashlib, re
HERE=Path(__file__).resolve().parent
SITE=HERE.parents[1]
cost_templates=[
 'This call needs {cost} command-buffer bytes for the complete operation. The formula counts encoded records, including metadata, not transferred payload bytes. Reserve enough free capacity before a multi-record operation.',
 'この呼び出しを全て登録するには、コマンドバッファーに{cost}バイト必要です。式は管理情報を含む記録のサイズであり、転送するデータの量ではありません。複数記録の処理では、先に十分な空き容量があるか確認してください。',
 '이 호출 전체를 등록하려면 명령 버퍼에 {cost}바이트가 필요합니다. 수식은 관리 정보를 포함한 레코드 크기이며 전송 데이터 크기가 아닙니다. 여러 레코드 작업 전에는 여유 용량이 충분한지 확인하세요.',
 '完整加入本次操作需要{cost}字节的命令缓冲区。公式计算的是包含管理信息的编码记录，不是传输数据量。多记录操作前应确认空闲容量足够。',
 '完整加入本次操作需要{cost}位元組的命令緩衝區。公式計算的是包含管理資訊的編碼記錄，不是傳輸資料量。多記錄操作前應確認可用容量足夠。',
 'Esta llamada necesita {cost} bytes de búfer para registrar toda la operación. La fórmula cuenta registros codificados, incluidos sus metadatos, no los datos transferidos. Comprueba el espacio libre antes de una operación de varios registros.',
 'Esta chamada precisa de {cost} bytes de buffer para registrar toda a operação. A fórmula conta registros codificados, incluindo metadados, não os dados transferidos. Confira o espaço livre antes de uma operação com vários registros.',
 'Cet appel nécessite {cost} octets de tampon pour enregistrer toute l’opération. La formule compte les enregistrements codés, métadonnées comprises, pas les données transférées. Vérifiez la place libre avant une opération à plusieurs enregistrements.',
 'Dieser Aufruf benötigt {cost} Befehlspuffer-Bytes für die vollständige Operation. Die Formel zählt codierte Einträge einschließlich Metadaten, nicht die übertragenen Nutzdaten. Prüfen Sie vor mehrteiligen Operationen den freien Platz.'
]
zero_rows=[
 'Each row is one record. A height of 0 adds none; width 0 still adds one record per row but writes no bytes. Row coordinates are cast to u8, so y + row wraps at 256. No clipping or rollback is provided.',
 '1行が1記録になります。高さ0なら追加しませんが、幅0でも各行に1記録を使い、書き込みは行いません。行座標はu8に変換されるので、y + rowは256で折り返します。クリッピングや部分登録の取り消しは行いません。',
 '행마다 레코드 하나를 사용합니다. 높이 0은 추가하지 않지만 너비 0은 행마다 레코드를 추가하고 바이트는 쓰지 않습니다. 행 좌표는 u8로 변환되어 y + row가 256에서 순환합니다. 클리핑이나 부분 등록 취소는 제공하지 않습니다.',
 '每行使用一条记录。高度0不添加记录；宽度0仍为每行添加记录，但不写入字节。行坐标转换为u8，因此y + row到256会回绕。不提供裁剪或部分入队回滚。',
 '每列使用一筆記錄。高度0不加入記錄；寬度0仍為每列加入記錄，但不寫入位元組。列座標轉換為u8，因此y + row到256會回繞。不提供裁切或部分加入復原。',
 'Cada fila usa un registro. La altura 0 no añade ninguno; la anchura 0 aún añade uno por fila, sin escribir bytes. La coordenada se convierte a u8: y + row vuelve a cero al llegar a 256. No hay recorte ni anulación de inserciones parciales.',
 'Cada linha usa um registro. Altura 0 não adiciona nenhum; largura 0 ainda adiciona um por linha, sem escrever bytes. A coordenada é convertida para u8: y + row volta a zero ao chegar a 256. Não há recorte nem cancelamento de inserções parciais.',
 'Chaque ligne utilise un enregistrement. Une hauteur nulle n’en ajoute aucun ; une largeur nulle en ajoute encore un par ligne, sans écrire d’octets. La coordonnée est convertie en u8 : y + row reboucle à 256. Aucun recadrage ni annulation des ajouts partiels.',
 'Jede Zeile verwendet einen Eintrag. Höhe 0 fügt keinen hinzu; Breite 0 fügt weiterhin einen je Zeile hinzu, schreibt aber keine Bytes. Zeilenkoordinaten werden in u8 umgewandelt; y + row läuft bei 256 um. Begrenzung und Rücknahme teilweiser Einträge erfolgen nicht.'
]
chunks=[
 'Split len into chunks of at most 127 bytes; ceil means rounding up. len=0 adds no record. This 127-byte division belongs to this library wrapper; the underlying intrinsic accepts an unsigned 8-bit count. Attempts continue after overflow, without undoing earlier records.',
 'lenを最大127バイトずつに分割します。ceilは切り上げです。len=0なら記録を追加しません。127バイトへの分割はこのライブラリ関数の処理であり、下位の組み込み関数は符号なし8ビットの個数を受け付けます。オーバーフロー後も登録を試み、先に登録した記録は取り消しません。',
 'len을 최대 127바이트씩 나눕니다. ceil은 올림입니다. len=0이면 레코드를 추가하지 않습니다. 127바이트 분할은 이 라이브러리 래퍼의 처리이며 하위 내장 함수는 부호 없는 8비트 개수를 받습니다. 오버플로 뒤에도 등록을 시도하고 앞선 레코드는 취소하지 않습니다.',
 '将len拆成最多127字节一段；ceil表示向上取整。len=0不添加记录。127字节分段是本库包装函数的处理，下层内置函数接受无符号8位计数。溢出后仍继续尝试添加，不撤销此前记录。',
 '將len拆成最多127位元組一段；ceil表示無條件進位。len=0不加入記錄。127位元組分段是本函式庫包裝函式的處理，下層內建函式接受無號8位元計數。溢位後仍繼續嘗試加入，不撤銷先前記錄。',
 'Divide len en tramos de hasta 127 bytes; ceil indica redondeo hacia arriba. len=0 no añade registros. Esta división es propia del wrapper de biblioteca; la intrínseca acepta un recuento de 8 bits sin signo. Los intentos continúan tras el desbordamiento, sin deshacer registros previos.',
 'Divide len em trechos de até 127 bytes; ceil indica arredondamento para cima. len=0 não adiciona registros. Essa divisão pertence ao wrapper da biblioteca; a intrínseca aceita uma contagem de 8 bits sem sinal. As tentativas continuam após o estouro, sem desfazer registros anteriores.',
 'Divise len en morceaux de 127 octets au plus ; ceil arrondit à l’entier supérieur. len=0 n’ajoute rien. Cette division appartient à la fonction de bibliothèque ; l’intrinsèque accepte un compte sur 8 bits non signés. Les tentatives continuent après débordement, sans annuler les enregistrements précédents.',
 'Teilt len in Abschnitte von höchstens 127 Bytes; ceil bedeutet Aufrunden. len=0 fügt keinen Eintrag hinzu. Diese Teilung gehört zur Bibliotheksfunktion; das darunterliegende Intrinsic akzeptiert einen vorzeichenlosen 8-Bit-Zähler. Nach Überlauf folgen weitere Einfügeversuche, ohne frühere Einträge zurückzunehmen.'
]
purposes={
 'vram_init':'vq_init','vram_clear_queue':'vram_clear_queue',
 'vram_queue_bg_tile':'vq_tile','vram_queue_tile':'vq_tile_alias',
 'vram_queue_bg_rect':'vq_rect','vram_queue_bg_block':'vq_block',
 'vram_queue_memcpy':'vq_copy','vram_queue_tiles':'vq_tiles_alias','vram_queue_memset':'vq_fill',
 'vram_get_queue_used':'vq_used','vram_get_queue_free':'vq_free','vram_get_queue_capacity':'vq_capacity',
 'vram_get_overflowed':'vram_get_overflowed','vram_flush_now':None,'vram_flush':None}
costs={'vram_queue_bg_tile':'4','vram_queue_tile':'4','vram_queue_bg_rect':'5 * h','vram_queue_bg_block':'6 * h',
 'vram_queue_memcpy':'6 * ceil(len / 127)','vram_queue_tiles':'6 * ceil(len / 127)','vram_queue_memset':'5 * ceil(len / 127)'}
messages={'vq_zero_rows_fc':zero_rows,'vq_chunks_fc':chunks}
contracts={};modules={}
for platform in ['gb','fc']:
 records={r['name']:r for r in json.loads((SITE/'reference'/ (platform+'-api.json')).read_text(encoding='utf-8'))['records']}
 program='samples/api-examples/'+platform+'/vram_queue_shapes.c'
 source=(SITE/program).read_text(encoding='utf-8')
 modules[platform+':vram']=['vq_init','vq_units_'+platform,'vq_flush_'+platform,'vq_serialize']
 for name,purpose in purposes.items():
  if purpose is None: purpose=('vq_now_' if name=='vram_flush_now' else 'vq_flush_')+platform
  notes=['vq_units_'+platform];args=[];returns=['none']
  if name in costs:
   returns=['vq_success_'+platform]
   if platform=='fc':
    key='vq_cost_'+name
    messages[key]=[t.format(cost='`'+costs[name]+'`') for t in cost_templates]
    notes += [key]
   if name in ['vram_queue_bg_tile','vram_queue_tile','vram_queue_bg_rect','vram_queue_bg_block']:
    args += [['x, y',['vq_xy']]]
    notes += ['vq_map_'+platform]
    if name in ['vram_queue_bg_rect','vram_queue_bg_block']:
     args += [['w, h',['vq_wh']]]
     if platform=='fc':notes+=['vq_zero_rows_fc']
    if name=='vram_queue_bg_block':
     args.insert(0,['base',['vq_map_'+platform]])
     args += [['src',['vq_source']]]
    else:args += [['tile',['vq_tile_value']]]
   else:
    args += [['dst',['vq_dst_'+platform]]]
    args += [['value',['vq_fill_value']]] if name=='vram_queue_memset' else [['src',['vq_source']]]
    args += [['len',['vq_length']]]
    if platform=='fc':notes+=['vq_chunks_fc']
  if name in ['vram_get_queue_used','vram_get_queue_free','vram_get_queue_capacity']:returns=['vq_count_result']
  if name=='vram_get_overflowed':returns=['vq_overflow_result']
  notes+=['vq_serialize']
  if name in ['vram_flush','vram_flush_now']:notes+=['vq_dst_'+platform]
  match=re.search(r'// example:'+name+r':start\n(.*?)\s*// example:'+name+r':end',source,re.S)
  assert match,name
  snippet='\n'.join(line[4:] if line.startswith('    ') else line for line in match[1].strip().splitlines())
  build='New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaq'+platform+'\\kitaq'+platform+'.exe .\\kitaq'+platform+'\\lib\\vram.c .\\kitaq-docs\\samples\\api-examples\\'+platform+'\\vram_queue_shapes.c -I .\\kitaq'+platform+'\\lib -I .\\kitaq-docs\\samples -o .\\out\\vram_queue_shapes.'
  build += 'gb --profile=dev --rst-disable --stack-bank=fixed --cgb=cgb' if platform=='gb' else 'nes --mapper=nrom --nes-chr=.\\kitaq-docs\\samples\\api-examples\\fc\\vram_shapes.chr'
  build+=' --no-cache --no-disasm'
  contracts[platform+':'+name]={'review':'vram-source-20260915','purpose':[purpose],'args':args,'returns':returns,'notes':notes,
   'record_sha256':hashlib.sha256(json.dumps({k:records[name].get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest(),
   'example':{'code':snippet,'program':program,'build':build,'expected':['vq_sample_checks','vq_sample_geometry','vq_sample_patterns']}}
for filename,data in [('vram_cost_texts.json',messages),('vram_contracts.json',contracts),('vram_modules.json',modules)]:
 (HERE/filename).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('30 reviewed VRAM contracts and 2 module introductions written.')
