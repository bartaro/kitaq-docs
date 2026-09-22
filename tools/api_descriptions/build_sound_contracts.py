"""Individually authored Japanese/English sound contracts, bound to source and audio lessons."""
from pathlib import Path
import hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sys.path.insert(0,str(SITE/'tools'));import catalog
catalog.ROOT=REPOS
texts={};contracts={};reviews={};sources={};modules={}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def msg(key,ja,en):
    key='sound_'+key;texts[key]={'ja':ja,'en':en};return key
void=msg('void','戻り値はありません。音源レジスターまたはドライバーの状態を変更します。','No return value. Changes sound registers or driver state.')
gb_note=msg('gb_note','noteは0～67の音程表の番号です。0はC2、33はA4です。68以上は67に制限し、60～67は48～55と同じ周波数を使います。CH3は同じ番号のパルス音より1オクターブ低くなります。ノートオン関数は無効化・一時停止フラグを確認せず直接発音します。','note indexes a 0..67 pitch table: 0 is C2 and 33 is A4. Values above 67 clamp to 67; 60..67 use the frequencies of 48..55. CH3 sounds one octave below a pulse channel at the same index. Note-on functions trigger hardware directly without checking enable or pause gates.')
gb_setup=msg('gb_setup','audio_hwregs_gb.c、audio.cの順で読み込み、起動時にAudio_Initを呼びます。Audio_Updateは約59.7Hzで1フレームに1回だけ呼びます。ストリームの読み込み中はROMバンクを一時変更するため、同じ処理を割り込みから重ねて呼ばないでください。','Include audio_hwregs_gb.c before audio.c and call Audio_Init at startup. Call Audio_Update exactly once per frame, about 59.7 Hz. Stream reads temporarily change the ROM mapping; do not re-enter this driver from an interrupt.')
sfx_format=msg('sfx_format','効果音は「note,値」の組を1更新につき1組読み、note=0で終わります。パルス音の値はNR12、CH3の値はNR32です。CH3用には先頭に0xFFを置きます。配列は再生終了まで保持します。優先度は同じスロット内で比較し、同値でも置き換えます。','An effect consumes one (note,value) pair per update and ends at note=0. The value is NR12 for pulse effects or NR32 for CH3. Prefix CH3 data with 0xFF. Keep storage alive until completion. Priorities compete within a slot; equal priority can replace its owner.')
sfx_restore=msg('sfx_restore','通常構成では、終了時にCH3を止めます。CH1は音楽が停止中なら止め、音楽再生中は以前の音楽ノートを自動的に再発音しません。VBlank構成のAUDIO_VBLANK_SFX_RESTOREはISRへ復帰を依頼します。','In the ordinary configuration, effect release turns CH3 off. It silences CH1 when music is stopped, but does not automatically replay an earlier music note while music is playing. With AUDIO_VBLANK_SFX_RESTORE, release requests recovery from the ISR.')
vb_setup=msg('vb_setup','audio_vblank.cが__kq_vblank_vectorを実装します。他のVBlank処理とベクターを重複させないでください。サンプルはAudio_NoiseEffectActiveを定義し、通常の音楽デコーダーを除外して、Audio_Updateを効果音・フェードの更新にだけ使います。曲のポインタや共有状態を変更する間は割り込みを止めます。','audio_vblank.c implements __kq_vblank_vector; do not also install a competing VBlank vector. The sample defines Audio_NoiseEffectActive, excludes the ordinary music decoder, and uses Audio_Update only for effects and fades. Mask interrupts while changing song pointers or shared state.')
vb_format=msg('vb_format','直接参照する曲は固定ROMなどISRが常に読める場所に置きます。レコードはdelay,CH1,CH2,CH3,CH4の5バイトです。ノートの0xFFは保持、0xFDは停止です。delay位置の0xFFは終端、0xFEはループです。これはチャンネルIDではなく、レコード内の配置順です。WRAMキューは別モードで、AudioVBlank_QueueRefillで完全な5バイトレコードを補充します。','Keep direct song data in fixed ROM or another area always visible to the ISR. A record is five bytes: delay, CH1, CH2, CH3, CH4. In note fields, 0xFF holds the current voice and 0xFD stops it. In the delay field, 0xFF ends playback and 0xFE loops. This is the record layout, not the channel-ID numbering. WRAM queue playback is a separate mode; submit complete five-byte records with AudioVBlank_QueueRefill.')
fc_voices=msg('fc_voices','このヘルパーはAPU_STATUSへ単一チャンネルのマスクを書き、ほかのチャンネルを無効化します。複数音を同時に鳴らすミキサーではありません。periodはパルス・三角波のタイマー値で、小さいほど高い音です。サンプルの周波数と時間はNTSC設定で確認しています。','This helper writes a single-channel APU_STATUS mask, disabling other voices. It is not a multivoice mixer. For pulse/triangle voices, period is a timer value: smaller values give higher pitches. Sample pitches and durations were checked with NTSC timing.')
fc_dmc=msg('fc_dmc','DMCは$C000～$FFC0の64バイト境界からROMを読みます。長さは16×n+1バイト（1～4081）です。ヘルパーは境界・範囲を検査せず、バンクも切り替えません。サンプルは固定バンク0に独自データを__aligned(64)で置き、配置を実行時にも検査します。','DMC reads ROM from a 64-byte boundary in $C000..$FFC0. Length is 16*n+1 bytes, 1..4081. These helpers neither validate alignment/ranges nor switch banks. The sample puts original data in fixed bank 0 with __aligned(64) and checks its placement at runtime.')
vrc6=msg('vrc6','このレジスター配線には--mapper=vrc6（mapper 24）を使います。VRC6を搭載しないカートリッジでは発音しません。periodの下位12ビットだけを使い、周波数制御レジスター$9003は設定しません。','Use --mapper=vrc6 (mapper 24) for this register wiring. A cartridge without VRC6 cannot produce these voices. Only the low 12 period bits are used; these helpers do not configure frequency-control register $9003.')
vrc7=msg('vrc7','--mapper=vrc7（mapper 85）用です。レジスター選択とデータ書き込みの組を割り込みと競合させないでください。書き込み待ち時間はヘルパーに含まれていません。録音はKUROSAKIのFMモデルの出力で、実機の音色・待ち時間の検証ではありません。','For --mapper=vrc7 (mapper 85). Serialize register-select/data pairs against interrupt writers. The helpers insert no device settling delay. Recordings capture KUROSAKI’s FM model; they do not verify hardware timbre or write timing.')
fds=msg('fds','--mapper=fdsで.fdsを生成します。サンプルはディスク入出力を使わず音源を操作します。録音はKUROSAKIのRAM直接起動と音源モデルで確認しました。検証用の空のファームウェア領域はBIOS機能を提供せず、配布物にも含みません。通常のディスク起動や実機では別途適切な起動環境が必要です。','Build a .fds image with --mapper=fds. This lesson operates sound without disk I/O. The recording uses KUROSAKI’s direct RAM boot and audio model. Its empty test firmware backing implements no BIOS routines and is not distributed. Normal disk boot and physical hardware require an appropriate boot environment.')
args={}
for name,ja,en in [
('on','0で無効、0以外で有効にします。音を止めるか、更新だけを止めるかは、この関数の説明を確認してください。','Zero disables; nonzero enables. Read this function’s description to distinguish muting from gating updates.'),
('bank','ストリームを格納したROMバンク番号。データの配置と一致させます。','ROM bank containing the stream; must match its placement.'),
('song','曲データの先頭。コピーしないため、再生中ずっと読み取れる配列を渡します。','Song start address; the driver borrows the array, which must remain readable throughout playback.'),
('sfx','効果音バイト列の先頭。パルス用とCH3用の形式は制約欄を参照してください。','Effect byte-stream start. See the notes for pulse and CH3 formats.'),
('priority','0～255。値が大きいほど優先し、同値も現在の効果音を置き換えられます。','Priority 0..255. Larger values win; equal values may also replace the current effect.'),
('pan','0=中央、1=左、2=右、3=無音。効果音APIでは0xFFなど3を超える値で基本定位を継承します。','0=center, 1=left, 2=right, 3=mute. Effect APIs treat values above 3, including 0xFF, as inherited base pan.'),
('ch','チャンネル番号：0=CH1、1=CH2、2=CH3、3=CH4。直接操作APIと音楽ストリームで同じ番号を使います。','Channel ID: 0=CH1, 1=CH2, 2=CH3, 3=CH4. Direct APIs and music streams use the same IDs.'),
('left','左出力のマスター音量0～7。7より大きい値は7へ制限します。0も完全な無音ではありません。','Left master level, 0..7; larger values clamp to 7. Zero is not complete silence.'),
('right','右出力のマスター音量0～7。7より大きい値は7へ制限します。','Right master level, 0..7; larger values clamp to 7.'),
('step_frames','各音量を1段階動かすAudio_Update呼び出し間隔。0なら目標を即時適用します。','Number of Audio_Update calls per one-level step. Zero applies the target immediately.'),
('packed','各物理チャンネルに2ビット。CH1がbit0～1、CH2が2～3、CH3が4～5、CH4が6～7で、各値はpanと同じです。','Two bits per physical channel: CH1 bits 0..1, CH2 2..3, CH3 4..5, CH4 6..7. Each field uses the pan values.'),
('wave_id','AUDIO_WAVE_*の0～7。7は保存した独自波形です。8以上は何もしません。','AUDIO_WAVE_* ID 0..7; 7 selects the cached custom wave. Values above 7 do nothing.'),
('wave16','読み取り可能な16バイト。各バイトの上位・下位4ビットが順に1サンプルを表します。NULLは無視します。','Sixteen readable bytes; high and low nibbles encode successive samples. NULL is ignored.'),
('duty','パルス波のデューティ比番号。下位2ビットを保存します。0=12.5%、1=25%、2=50%、3=75%。','Pulse duty index; the low two bits are stored. 0=12.5%, 1=25%, 2=50%, 3=75%.'),
('duty2','0=12.5%、1=25%、3=75%、それ以外は50%のパルス波です。','Pulse duty: 0=12.5%, 1=25%, 3=75%; all other values select 50%.'),
('level','NR32形式：0x00=無音、0x20=100%、0x40=50%、0x60=25%。','NR32 encoding: 0x00=mute, 0x20=100%, 0x40=50%, 0x60=25%.'),
('param','NR43の生の値。bit7～4=クロックシフト、bit3=短いLFSR、bit2～0=分周比番号です。','Raw NR43: bits 7..4 clock shift, bit 3 short LFSR, bits 2..0 divisor code.'),
('note','0～67の音程表番号。詳しい音域とCH3のオクターブ差は制約欄を参照してください。','Pitch-table index 0..67. See the notes for range folding and CH3’s octave difference.'),
('vol_env','NR12/NR22/NR42形式。上位4ビットが初期音量、bit3が増加方向、下位3ビットが変化間隔です。例0xC0は音量12を保持します。','NR12/NR22/NR42 encoding: upper nibble initial volume, bit 3 increasing envelope, low three bits envelope period. 0xC0 holds volume 12.'),
('mask','APU_STATUSへ書く完全な有効化マスク。bit0～4はpulse1、pulse2、triangle、noise、DMCで、上位3ビットは捨てます。','Complete APU_STATUS enable mask. Bits 0..4 select pulse1, pulse2, triangle, noise and DMC; upper bits are discarded.'),
('duty_volume','パルス制御レジスターの生値。bit7～6=デューティ、bit5=長さ停止、bit4=固定音量、bit3～0=音量またはエンベロープ間隔。','Raw pulse control: bits 7..6 duty, bit 5 length halt, bit 4 constant volume, low nibble volume or envelope period.'),
('length_index','長さテーブル番号0～31。フレーム数そのものではなく、値の下位5ビットをレジスターへ格納します。','Length-table index 0..31, not a frame count. Only the low five bits reach the register.'),
('linear','三角波の線形カウンター。bit7=制御・長さ停止、下位7ビット=リロード値。','Triangle linear counter: bit 7 control/length halt, low seven bits reload value.'),
('period_mode','ノイズのbit7=短周期モード、bit3～0=周期テーブル番号。','Noise register: bit 7 short mode, low nibble period-table index.'),
('flags_rate','DMCのbit7=IRQ、bit6=ループ、bit3～0=レート番号。サンプルではIRQを使いません。','DMC bit 7 IRQ, bit 6 looping, low nibble rate index. The sample does not enable IRQ.'),
('output_level','DMC出力カウンターの初期値0～127。下位7ビットだけを書き込みます。','Initial DMC output counter, 0..127; only the low seven bits are written.'),
('sample_addr','DMCデータ先頭のCPUアドレス。$C000～$FFC0の64バイト境界です。','DMC data CPU address: a 64-byte boundary in $C000..$FFC0.'),
('sample_len','16×n+1のバイト数、1～4081。0や未対応の長さは渡さないでください。','Byte length 16*n+1 in 1..4081. Do not pass zero or an unrepresentable length.'),
('control','VRC6パルス制御。bit7=ゲート、bit6～4=デューティコード、bit3～0=音量0～15。','VRC6 pulse control: bit 7 gate, bits 6..4 duty code, low nibble volume 0..15.'),
('rate','ノコギリ波の加算値0～63。下位6ビットを使用します。','Saw accumulator increment 0..63; only the low six bits are used.'),
('reg','VRC7レジスター番号。チャンネル0では0x10=周波数下位、0x20=上位・ブロック・キー、0x30=楽器・減衰です。','VRC7 register number. For channel 0: 0x10 frequency low, 0x20 high/block/key, 0x30 instrument/attenuation.'),
('value','選択したVRC7レジスターへ書く1バイト。','Byte to write to the selected VRC7 register.'),
('patch8','楽器0の設定となる8バイト配列。NULLは検査しません。読み込み中にバンクを切り替えないでください。','Eight bytes defining instrument 0. NULL is not checked. Keep the source bank mapped during the call.'),
('channel','VRC7チャンネル0～5。6以上は何もしません。','VRC7 channel 0..5; larger values do nothing.'),
('instrument','楽器番号0～15。0は独自パッチ、1～15はプリセットです。下位4ビットを使います。','Instrument 0..15: 0=user patch, 1..15=presets. Only the low nibble is used.'),
('fnum','周波数番号0～511。ブロックと組み合わせて音程を決めます。下位9ビットを使います。','Frequency number 0..511; combined with block to determine pitch. Only nine bits are used.'),
('block','オクターブのブロック番号0～7。下位3ビットを使います。','Octave block 0..7; only the low three bits are used.'),
('key_flags','0x10でキーオン、0x20でサステイン指定。ほかのビットは捨てます。','0x10 key-on, 0x20 sustain flag; other bits are discarded.'),
('wave64','FDS波形の64バイト配列。各値は0～63の6ビット振幅です。NULLは検査しません。','Sixty-four FDS wave bytes, each a 6-bit amplitude 0..63. NULL is not checked.'),
('mod32','FDS変調テーブルへ書く32バイト。各値は0～7の制御コードです。書き込み前に変調を停止します。','Thirty-two bytes for the FDS modulation table, each a control code 0..7. Halt modulation before loading.'),
('freq','FDS周波数レジスター値0～4095。上位制御ビットは0になります。','FDS frequency register value 0..4095. Upper control bits are cleared.'),
('vol','FDSの直接音量0～63。下位6ビットを使うため64は0に折り返します。','FDS direct volume 0..63; masking to six bits makes 64 wrap to zero.'),
('speed','名前にかかわらず$4080へ書く生値です。bit7で直接音量、bit6で増加方向を指定します。','Despite the parameter name, this is the raw $4080 value: bit 7 direct volume, bit 6 increasing envelope.'),
('gain','$4084へ書く生の変調エンベロープ値です。','Raw modulation-envelope value written to $4084.'),
('mode','$408Aへ書くエンベロープのマスター速度です。','Envelope master speed written to $408A.')]:args[name]=msg('arg_'+name,ja,en)

specs={s['group']:s for s in json.loads((HERE/'sound_examples.json').read_text(encoding='utf-8'))}
expect={}
for group,ja,en in [
('gb-channels','約0.5秒の無音のあと、CH1のA4、CH2のA4、CH3のA3、ノイズを順に鳴らします。各音は30フレーム、音間は15フレームです。最後のSEQUENCE COMPLETEは処理終了を表し、音の検証には録音を使います。','After about half a second of silence, hear CH1 A4, CH2 A4, CH3 A3 and noise. Each voice lasts 30 frames, with 15-frame gaps. SEQUENCE COMPLETE marks program completion; use the recording to assess the sound.'),
('gb-mix','A4が左、右、中央へ移動します。中央では音量7から1へ下がり、次に4まで上がって固定されます。最後に音量0でも小さく鳴り、チャンネル停止で無音になります。定位切り替え後にはフィルターの過渡音が残ることがあります。','A4 moves left, right and center. In the center it fades from level 7 to 1, then rises to 4 and stays there. Level 0 is still quietly audible; stopping the channel produces silence. Routing changes can leave a decaying filter transient.'),
('gb-wave','三角波、独自の矩形波、キャッシュから再読込した同じ矩形波を順に鳴らします。各音は45フレーム、音間は15フレームです。3音とも音程は約220Hzですが、最初だけ音色が異なります。','Hear the triangle preset, an original pulse wave and the same pulse wave reloaded from the cache. Each lasts 45 frames with 15-frame gaps. All three are about 220 Hz; only the first has a different timbre.'),
('gb-music','発音、一時停止の無音、再開、無効化しても残る音、チャンネル停止の無音、再有効化後の次の音、曲停止の順です。一時停止の30更新では待ちカウンターが変わらず、無効化中は30へ進むこともRAMで確認します。','Hear a note, paused silence, resume, a note retained while music is disabled, explicit channel silence, the next note after re-enabling, then stop. RAM also verifies that 30 paused updates preserve the delay, while the disabled gate still advances it to 30.'),
('gb-sfx','バンク2に置いた短い上昇音を、左パルス、右の波形音、中央パルスの順で鳴らします。その後は右パルスを途中停止し、無効化で止める例と再有効化の例を示します。優先度5に対する4の要求は採用されません。','Bank-2 data plays a short rising pulse on the left, a wave effect on the right and a centered pulse. Later examples stop a right pulse early, disable an effect and re-enable playback. A priority-4 request cannot replace priority 5.'),
('gb-vblank','2音の曲をISRで再生し、音楽更新の無効化では鳴っている音が続くこと、Stopでは止まること、再開後にIRQだけを止めても音が続くことを聞き比べます。コールバックは音楽無効時も動き、IRQ無効時は止まることをRAMで確認します。','The ISR plays a two-note song. Compare gating music updates, which retains the current sound; Stop, which silences it; and gating IRQ after restart, which also retains sound. RAM verifies that the hook runs while music is disabled and stops when IRQ is disabled.'),
('gb-recovery','パルスの復帰、無音、波形音の復帰、無音を各30フレームで示します。保留値1は復帰要求を追加しても維持され、保留なしからの要求は発音し直さない値2になります。このサンプルでは割り込みを使わず呼び出し側が所有権を管理します。','Hear pulse recovery, silence, wave recovery and silence, each for 30 frames. A release request preserves pending value 1; requesting with no pending event produces release-only value 2. Here IRQ is disabled and the caller explicitly manages ownership.'),
('fc-channels','pulse1、pulse2、三角波、ノイズ、tick、moveの順です。タイマー253はNTSCでパルス約440Hz、三角波約220Hzになります。tickは約111Hz、moveは約174Hzで、moveの方が短く終わります。最後は無音です。','Hear pulse1, pulse2, triangle, noise, tick and move. Timer 253 gives roughly 440 Hz pulses and 220 Hz triangle under NTSC. Tick is about 111 Hz; move is about 174 Hz and ends sooner. The final interval is silent.'),
('fc-dmc','独自のデルタ列をレート10、無音区間、より速いレート12の順で再生します。途中のDMC停止後は出力カウンターが保持されるため、録音では過渡成分が残る場合があります。最後はAPU全停止です。','An original delta pattern plays at rate 10, pauses, then plays faster at rate 12. DMC stop retains its output counter, so the gap may contain a transient. The final operation silences the whole APU.'),
('fc-vrc6','VRC6のパルス1、デューティの異なるパルス2、ノコギリ波を各45フレーム鳴らし、15フレームずつ休みます。3音の音程はおよそ440Hzで、最後は3音源とも停止します。','Hear VRC6 pulse 1, pulse 2 with a different duty, and saw, each for 45 frames with 15-frame gaps. The three pitches are approximately 440 Hz; all three voices stop at the end.'),
('fc-vrc7','プリセット楽器1と、サステインを有効にした独自の楽器0を各60フレーム鳴らします。音程を揃えて音色を比較し、最後にキーオフと最大減衰で止めます。','Compare preset instrument 1 with an original sustained user instrument 0, each for 60 frames at the same pitch. The sequence ends with key-off and maximum attenuation.'),
('fc-fds','独自の64段階三角波で約440Hz、無音、約660Hz、無音の順です。2回目はnes_fds_wave_loadと生のエンベロープ設定を使います。これは音源モデルと直接起動の検証であり、BIOS経由のディスク起動の検証ではありません。','An original 64-step triangle plays at about 440 Hz, pauses, plays at about 660 Hz, then stops. The second note uses nes_fds_wave_load and raw envelope settings. This verifies the audio model and direct boot, not BIOS-driven disk startup.')]:expect[group]=msg('expected_'+group,ja,en)

datasets={p:json.loads((SITE/'reference'/f'{p}-api.json').read_text(encoding='utf-8')) for p in ['gb','fc']}
bykey={p+':'+r['name']:r for p,d in datasets.items() for r in d['records']}
def add(platform,name,group,ja,en,notes=(),overrides=None):
    key=platform+':'+name;r=bykey[key];files=[REPOS/r['path']]
    if name.startswith(('__fds_','__midi_')):
        compiler=REPOS/'kitaqfc/kitaqfc/CodeGenerator.cs';body=compiler.read_text(encoding='utf-8')
        start=body.index('case "'+name+'":');end=body.index('\n                case ',start+1)
        excerpt=body[start:end]
        marker='EmitHelperStart("'+name+'");'
        if marker in body:
            a=body.index(marker);b=body.index('EmitAsm("RTS");',a)+len('EmitAsm("RTS");')
            excerpt+='\n\n'+body[a:b]
        if name.startswith('__midi_'):
            a=body.index('EmitHelperStart("__kq_midi_out_a");');b=body.index('EmitHelperStart("__midi_note_on");',a)
            excerpt+='\n\n'+body[a:b]
        r['implementation_excerpt']=excerpt
        r['implementation_source']={'path':compiler.relative_to(REPOS).as_posix(),'line':body.count('\n',0,start)+1}
    elif name=='nes_fds_wave_load':
        body=files[0].read_text(encoding='utf-8');line=next(s for s in body.splitlines() if s.startswith('#define nes_fds_wave_load('))
        r['kind']='macro';r['implementation_excerpt']=line
    # Refresh concrete declarations and bodies from the published source tree.
    if r.get('kind')!='macro':
        decl={d['name']:d for d in catalog.definitions(files[0])}.get(name)
        if decl:
            for field in ['ret','args','signature','path','line','comment','body']:r[field]=decl[field]
    if r.get('definition'):
        source=REPOS/r['definition']['path'];found={d['name']:d for d in catalog.definitions(source)}.get(name)
        if found:r['definition']=found
        files.append(source)
    if r.get('implementation_source'):files.append(REPOS/r['implementation_source']['path'])
    fingerprint=hashlib.sha256(json.dumps({k:r.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
    params=[re.search(r'(\w+)\s*$',a).group(1) for a in r['args'].split(',') if a.strip() not in ('','void')]
    mapping={**args,**(overrides or {})};assert all(p in mapping for p in params),(name,params)
    spec=specs[group];program=spec['source'];code=(SITE/program).read_text(encoding='utf-8')
    if name not in code and name not in (SITE/'samples'/('gb_sound_example.h' if platform=='gb' else 'fc_sound_example.h')).read_text(encoding='utf-8'):raise ValueError('Missing sample call '+name)
    extension=spec.get('container','gb' if platform=='gb' else 'nes')
    flags=' '.join(spec['build_flags']).replace('{SITE}/samples/font.chr','.\\kitaq-docs\\samples\\font.chr')
    build='New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaq'+platform+'\\kitaq'+platform+'.exe .\\kitaq-docs\\'+program.replace('/','\\')+' -I .\\kitaq'+platform+'\\lib -I .\\kitaq-docs\\samples -o .\\out\\'+group+'.'+extension+' '+flags
    contracts[key]={'review':'sound-source-20260916','record_sha256':fingerprint,'purpose':[msg(name,ja,en)],'args':[[p,[mapping[p]]] for p in params],
        'returns':[void],'notes':list(notes),'example':{'program':program,'code':code,'standalone':True,'expected':[expect[group]],'build':build}}
    reviews[key]={'record_sha256':fingerprint,'header_line':r['line']}
    for source in files:sources[source.relative_to(REPOS).as_posix()]=sha(source)

def gb(name,group,ja,en,notes=(),overrides=None):add('gb',name,'gb-'+group,ja,en,notes,overrides)
gb('Audio_Init','channels','APUを有効にし、音楽・効果音・一時停止・音量・波形の状態を初期化して全チャンネルを無音にします。','Enable the APU, initialize music/effects/pause/mix/wave state and leave all channels silent.',[gb_setup])
gb('Audio_Update','music','音量フェードを1刻み進め、一時停止中でなければ効果音、音楽の順で処理します。','Advance the volume fade once; unless paused, service effects then music.',[gb_setup,msg('update_pause','一時停止中もフェードは進みます。WAIT nを読む呼び出しのあとn回を待つため、次のコマンドまでの間隔はn+1更新です。','Fades continue while paused. Reading WAIT n is followed by n waiting calls, so the next command occurs after n+1 updates.')])
gb('Audio_PlayMusic','music','指定バンクの曲を先頭から再生するよう設定し、楽器・定位・待ち状態をリセットします。','Arm the song in the specified bank from its beginning and reset instruments, pan and delay.',[gb_setup,msg('music_start','データを読むのは後のAudio_Updateです。NULLは検査しません。既存の効果音は残ります。','The next Audio_Update reads the data. NULL is not checked. Existing effects remain active.')])
gb('Audio_StopMusic','music','曲の再生フラグと復帰ノートのマスクを消し、4音源を即座に止めます。','Clear song playback and its resume mask, then immediately silence all four voices.',[msg('stopmusic_effects','効果音のポインタは残るため、次のAudio_Updateで効果音が鳴る場合があります。全停止にはAudio_StopSfxも呼びます。','Effect pointers remain, so a later Audio_Update may sound an effect. Also call Audio_StopSfx when stopping everything.')])
gb('Audio_SetPaused','music','一時停止時に音を止め、曲・効果音の位置を保持します。再開時は条件を満たすCH1・CH2・CH4を再発音します。','Silence on pause while preserving music/effect positions. Resume retriggers eligible CH1, CH2 and CH4 notes.',[gb_setup,msg('pause_ch3','CH3はここでは再発音しません。効果音は次の更新から再開します。直接ノートオン関数を呼ぶと一時停止中でも鳴ります。','This routine does not retrigger CH3. Effects continue on a later update. Direct note-on calls can still sound while paused.')])
for name,ja,en in [
('Audio_PlaySFX','現在のROMバンクを記憶し、基本定位を継承する効果音を要求します。','Capture the current ROM bank and request an effect with inherited base pan.'),
('Audio_PlaySFXBanked','指定バンクから効果音の種類を判定し、基本定位を継承して再生を要求します。','Classify an effect in its explicit source bank and request playback with inherited base pan.'),
('Audio_PlaySFXPanned','現在のROMバンクを記憶し、定位を指定した効果音を要求します。','Capture the current ROM bank and request an effect with a pan override.'),
('Audio_PlaySFXPannedBanked','指定バンク・優先度・定位で、パルスまたはCH3の効果音スロットを取得します。','Acquire a pulse or CH3 effect slot with an explicit bank, priority and pan.'),
('Audio_StopSfx','2つの効果音ストリームと定位の上書きを解除し、借りていたチャンネルの解放処理を行います。','Clear both effect streams and their pan overrides, then release the borrowed channels.')]:gb(name,'sfx',ja,en,[sfx_format,sfx_restore])
gb('Audio_StopChannel','channels','指定した物理チャンネルを止め、その音楽ノートを再開対象から外します。','Stop one physical voice and remove its music note from the resume mask.',[msg('stopchannel','CH1/CH3では対応する効果音スロットも消します。0～3以外は何もしません。VBlank版のラッチ済みノートは別管理です。','CH1/CH3 also clear their effect slot. Values outside 0..3 do nothing. VBlank latched notes are managed separately.')])
gb('Audio_SetMusicEnabled','music','通常の音楽デコーダーが新しいノートを書き込むかを切り替えます。','Control whether the ordinary music decoder writes new notes.',[msg('gate','無効化しても曲の読み取り位置は進み、楽器・定位などの制御命令も処理します。鳴っている音は止めません。一時停止にはAudio_SetPausedを使います。','Disabling still advances the stream and processes instrument/pan controls. It does not silence the current note. Use Audio_SetPaused to pause playback.')])
gb('Audio_SetSfxEnabled','sfx','効果音のノート書き込みを切り替え、無効化時には効果音スロットを解放します。','Gate effect note writes; disabling also releases the effect slots.',[sfx_restore,msg('sfx_disabled_request','無効化後に開始APIを呼ぶとストリームは登録されますが、更新時に音は書き込まれません。再生したいときは先に有効化します。','Starting while disabled can register a stream, but updates suppress its note writes. Enable effects before requesting audible playback.')])
gb('Audio_SetMasterVolume','mix','左右のマスター音量を0～7へ制限して即時設定し、進行中のフェードを取り消します。','Clamp left/right master levels to 0..7, write them immediately and cancel an active fade.')
gb('Audio_FadeToMasterVolume','mix','左右それぞれの音量を、指定更新間隔ごとに目標へ1段階ずつ近づけます。','Move each output level one step toward its target at the requested update interval.',[gb_setup])
gb('Audio_CancelMasterVolumeFade','mix','フェードの進行を止め、現在の音量とレジスター値を保持します。','Stop further fade steps while retaining the current levels and registers.')
gb('Audio_SetPan','mix','1つの物理チャンネルの基本定位を変え、実行中の効果音の定位を再適用します。','Change one physical voice’s base pan, then reapply active effect overrides.',[msg('pan_invalid','未知のチャンネル番号はCH4を選びます。このAPIでは0～3以外のpanは無音であり、効果音APIの継承指定とは異なります。','An unknown channel selects CH4. Here pan outside 0..3 mutes; it is not the effect API’s inherit setting.')])
gb('Audio_SetPanPacked','mix','4音源の基本定位を1バイトから展開し、NR51を1回更新します。','Unpack four base pan settings from one byte and update NR51 once.')
gb('Audio_LoadWave','wave','プリセットまたはキャッシュした独自波形をCH3の波形RAMへ設定します。','Install a preset or cached custom waveform in CH3 wave RAM.',[msg('wave_trigger','波形をロードしてもノートは開始せず、Audio_Ch3Waveの選択値も変更しません。三角波プリセットは独自波形キャッシュも三角波へ戻します。必要ならAudio_Ch3NoteOnで発音します。','Loading neither starts a note nor changes Audio_Ch3Wave. The triangle preset also resets the custom cache to a triangle. Call Audio_Ch3NoteOn to trigger the voice.')])
gb('Audio_LoadCustomWave','wave','16バイトを独自波形キャッシュとCH3の波形RAMへコピーします。','Copy sixteen bytes into the custom-wave cache and CH3 wave RAM.',[msg('wave_lifetime','コピー後は入力配列を再利用できます。関数内部でDACを停止して書き込み、ノートの再トリガーは呼び出し側で行います。','The caller may reuse the source after copying. The function disables the DAC for writing; the caller retriggers a note.')])
for name,ja,en in [('Audio_SetCh1Duty','次のCH1ノートに使うデューティ番号を保存します。','Cache the duty index for the next CH1 note.'),('Audio_SetCh2Duty','次のCH2ノートに使うデューティ番号を保存します。','Cache the duty index for the next CH2 note.'),('Audio_SetCh3Level','次のCH3ノートに使うNR32形式の音量を保存します。','Cache the NR32 output level for the next CH3 note.'),('Audio_SetCh4Param','次のCH4ノートに使うNR43形式のノイズ設定を保存します。','Cache the NR43 noise parameters for the next CH4 note.')]:gb(name,'channels',ja,en,[msg('cache_only','この呼び出しだけでは現在の音源レジスターを書き換えません。ノートオンの引数へ保存値を渡すか、対応するストリームを再生して反映します。','This call alone does not change the active sound registers. Pass the cached value to note-on or use the corresponding stream to apply it.')])
gb('Audio_Ch1NoteOn','channels','CH1のスイープ・デューティ・エンベロープ・音程を設定してパルス波を開始します。','Program CH1 sweep, duty, envelope and pitch, then trigger the pulse.',[gb_note])
gb('Audio_Ch2NoteOn','channels','CH2のデューティ・エンベロープ・音程を設定してパルス波を開始します。','Program CH2 duty, envelope and pitch, then trigger the pulse.',[gb_note])
gb('Audio_Ch3NoteOn','channels','ロード済みの波形を、指定音程とNR32音量でCH3から再生します。','Trigger the loaded CH3 waveform at the requested pitch and NR32 level.',[gb_note])
gb('Audio_Ch4NoteOn','channels','ノイズ設定を保存し、エンベロープと多項式カウンターを設定してCH4を開始します。','Cache the noise parameters, program envelope/polynomial registers and trigger CH4.',[msg('noise_length','長さによる自動停止は有効にしません。エンベロープまたは明示的停止で音を終えます。','Length-based automatic stop is not enabled. Use the envelope or an explicit stop to end the sound.')])
for name,ja,en in [
('AudioVBlank_Init','VBlank音楽のソフトウェア状態・キュー・楽器・コールバックを初期化します。APU初期化と割り込み禁止は行いません。','Initialize VBlank music state, queue, instruments and hook. This neither initializes the APU nor masks interrupts.'),
('AudioVBlank_SetMusic','直接参照する曲を選び、読み取り位置をリセットします。再生中フラグは変更しません。','Select a direct song and reset its cursors without changing the playing flag.'),
('AudioVBlank_Play','選択済みの曲を先頭から再生し、キューモードを解除します。曲がNULLなら停止します。','Restart the selected song from its beginning and leave queue mode. A NULL song stops playback.'),
('AudioVBlank_PlayMusic','直接参照する曲を選択し、先頭からの再生を開始します。','Select a direct song and arm playback from its beginning.'),
('AudioVBlank_Stop','再生・待ち・復帰状態を消し、パルス・ノイズ・波形音を即座に止めます。IRQは無効化しません。','Clear playback/delay/recovery state and immediately silence pulse, noise and wave voices. IRQ remains enabled.'),
('AudioVBlank_SetEnabled','VBlank音楽処理を切り替え、無効化時に復帰要求を消します。鳴っている音とIRQは保持します。','Gate VBlank music and clear recovery requests on disable. Current sound and IRQ remain unchanged.'),
('AudioVBlank_EnableIrq','IEのVBlankビットを立て、EIでCPU割り込みを全体として有効化します。','Set IE’s VBlank bit and execute EI to enable CPU interrupts globally.'),
('AudioVBlank_DisableIrq','IEのVBlankビットだけを消します。ほかの割り込み源や音源は変更しません。','Clear only IE’s VBlank bit, leaving other interrupt sources and sound unchanged.')]:gb(name,'vblank',ja,en,[vb_setup,vb_format])
for name,ja,en in [
('AudioVBlank_RestoreCh1','効果音が借りたCH1またはCH2へラッチ済み音楽ノートを戻すか、解放だけを行います。','Restore a latched music note to the pulse voice borrowed by an effect (CH1 or CH2), or release it silently.'),
('AudioVBlank_RestoreCh3','効果音終了後にCH3のラッチ済みノートを戻すか、DACを無効化します。','Restore CH3’s latched note after effect release, or disable its DAC.'),
('AudioVBlank_RequestRestoreCh1','パルス音の保留要求がなければ解放要求2を設定し、既存の復帰要求1を保持します。','Set pulse release-only request 2 if nothing is pending, preserving an existing recovery request 1.'),
('AudioVBlank_RequestRestoreCh3','波形音の保留要求がなければ解放要求2を設定し、既存の復帰要求1を保持します。','Set wave release-only request 2 if nothing is pending, preserving an existing recovery request 1.')]:gb(name,'recovery',ja,en,[vb_setup,msg('recover_owner','復帰関数を直接呼ぶ場合、効果音がチャンネルを解放済みであることを呼び出し側が保証し、保留値も自分で消します。要求関数だけではレジスターを変更しません。','When calling recovery directly, the caller ensures the effect has released the voice and clears the pending flag afterward. Request functions alone do not write sound registers.')])

period_apu=msg('period_apu','11ビットタイマー値0～2047。パルスはCPU周波数/[16×(period+1)]、三角波はCPU周波数/[32×(period+1)]です。','11-bit timer 0..2047. Pulse frequency is CPU clock/[16*(period+1)]; triangle is CPU clock/[32*(period+1)].')
period_vrc=msg('period_vrc','12ビットタイマー値0～4095。上位4ビットは捨てます。サンプルではパルス253、ノコギリ波289を使います。','12-bit timer 0..4095; upper bits are discarded. The sample uses pulse 253 and saw 289.')
noisevolume=msg('noisevolume','ノイズ制御の生値。bit5=長さ停止、bit4=固定音量、bit3～0=音量またはエンベロープ間隔です。','Raw noise control: bit 5 length halt, bit 4 constant volume, low nibble volume or envelope period.')
fmvolume=msg('fmvolume','VRC7の減衰量0～15。0が最大音量で、15が最大減衰です。下位4ビットを使います。','VRC7 attenuation 0..15: 0 is loudest, 15 greatest attenuation. Only the low nibble is used.')
def fc(name,group,ja,en,notes=(),overrides=None):add('fc',name,'fc-'+group,ja,en,notes,overrides)
fc('nes_apu_init','channels','フレームIRQを無効にして4音源を有効化し、無音の制御値を設定します。DMCは無効です。','Disable frame IRQ, enable four voices and install quiet controls. DMC remains disabled.')
fc('nes_apu_channel_enable','channels','APUの5チャンネルの有効化状態を、指定マスクで丸ごと置き換えます。','Replace the enable state of all five APU channels with the supplied mask.')
fc('nes_apu_silence_all','channels','全チャンネルを無効化し、パルス・ノイズの音量とDMC出力を消します。','Disable all channels and clear pulse/noise volume and DMC output.')
fc('nes_sfx_square1','channels','パルス1だけを有効にし、スイープを止め、制御値・タイマー・長さ番号を書き込みます。','Enable only pulse 1, disable sweep and write control, timer and length index.',[fc_voices],{'period':period_apu})
fc('nes_sfx_square2','channels','パルス2だけを有効にし、スイープを止め、制御値・タイマー・長さ番号を書き込みます。','Enable only pulse 2, disable sweep and write control, timer and length index.',[fc_voices],{'period':period_apu})
fc('nes_sfx_triangle','channels','三角波だけを有効にし、線形カウンター・タイマー・長さ番号を書き込みます。','Enable only triangle and write linear counter, timer and length index.',[fc_voices],{'period':period_apu})
fc('nes_sfx_noise','channels','ノイズだけを有効にし、エンベロープ・周期モード・長さ番号を書き込みます。','Enable only noise and write envelope, period/mode and length index.',[fc_voices],{'volume':noisevolume})
fc('nes_sfx_tick_blip','channels','パルス1を0x9A・タイマー0x03F0・長さ番号4で鳴らし、短い低音のtickを作ります。','Trigger pulse 1 with control 0x9A, timer 0x03F0 and length index 4 for a short low tick.',[fc_voices])
fc('nes_sfx_move_blip','channels','パルス1を0x5A・タイマー0x0280・長さ番号2で鳴らし、tickより高く短いmove音を作ります。','Trigger pulse 1 with control 0x5A, timer 0x0280 and length index 2 for a higher, shorter movement blip.',[fc_voices])
fc('nes_dmc_config','dmc','DMCの制御・出力初期値・開始アドレス・長さをレジスター単位へ変換して設定します。','Configure DMC control/output and convert its sample address and length into register units.',[fc_dmc])
fc('nes_dmc_start','dmc','APU_STATUS=0x1FとしてDMCとほかの4音源を有効化します。','Write APU_STATUS=0x1F, enabling DMC and all four other voices.',[fc_dmc])
fc('nes_dmc_stop','dmc','APU_STATUS=0x0FとしてDMCを止め、ほかの4音源の有効化ビットを立てます。','Write APU_STATUS=0x0F, stopping DMC while setting all four other voice-enable bits.',[fc_dmc])
fc('nes_dmc_play','dmc','サンプルのDMC設定を行い、直後にDMCを開始します。','Configure the DMC sample and immediately start playback.',[fc_dmc])
for name,ja,en in [
('nes_vrc6_silence_all','VRC6の3音源を無効化し、パルス制御とノコギリ波の加算値を0にします。','Disable all three VRC6 voices and clear pulse controls and saw rate.'),
('nes_vrc6_pulse1_set','VRC6パルス1の制御値と12ビットタイマーを書き、発音を有効にします。','Write VRC6 pulse 1 control and its 12-bit timer, then enable the voice.'),
('nes_vrc6_pulse2_set','VRC6パルス2の制御値と12ビットタイマーを書き、発音を有効にします。','Write VRC6 pulse 2 control and its 12-bit timer, then enable the voice.'),
('nes_vrc6_pulse1_off','VRC6パルス1の上位タイマー・有効化レジスターを0にして停止します。','Stop VRC6 pulse 1 by clearing its high-timer/enable register.'),
('nes_vrc6_pulse2_off','VRC6パルス2の上位タイマー・有効化レジスターを0にして停止します。','Stop VRC6 pulse 2 by clearing its high-timer/enable register.'),
('nes_vrc6_saw_set','VRC6ノコギリ波の6ビット加算値と12ビットタイマーを書き、発音を有効にします。','Write the VRC6 saw’s 6-bit accumulator rate and 12-bit timer, then enable it.'),
('nes_vrc6_saw_off','VRC6ノコギリ波の上位タイマー・有効化レジスターを0にして停止します。','Stop the VRC6 saw by clearing its high-timer/enable register.')]:fc(name,'vrc6',ja,en,[vrc6],{'period':period_vrc})
for name,ja,en in [
('nes_vrc7_write','VRC7のレジスター選択ポートへ番号を書き、続いてデータポートへ値を書きます。','Write a register number to VRC7’s select port, then its value to the data port.'),
('nes_vrc7_set_user_patch','8バイトをVRC7の楽器0レジスターへ順番に書き込みます。','Write eight bytes in order to VRC7’s user-instrument registers.'),
('nes_vrc7_channel_set','1つのFM音源の周波数・ブロック・キー・楽器・減衰を設定します。','Configure one FM voice’s frequency, block, key flags, instrument and attenuation.'),
('nes_vrc7_key_off','指定チャンネルの周波数上位・ブロック・キーのレジスター全体を0にします。','Clear the selected voice’s entire frequency-high/block/key register.'),
('nes_vrc7_silence_all','6音源すべてをキーオフし、楽器0・最大減衰に設定します。','Key off all six voices and select instrument 0 with maximum attenuation.')]:fc(name,'vrc7',ja,en,[vrc7,msg('vrc7_shared','楽器0は全チャンネルで共有します。channel_setはキー・周波数上位を楽器・減衰より先に書きます。key_off後の次の音は周波数上位とブロックも設定し直します。','Instrument 0 is shared by all voices. channel_set writes key/frequency-high before instrument/attenuation. After key_off, the next note must restore frequency-high and block too.')],{'volume':fmvolume})
for name,ja,en in [
('__fds_sound_enable','ディスク・音源ゲート$4023へ0x83を書き、波形制御$4089と速度$408Aを0にします。','Write 0x83 to disk/sound gate $4023 and zero wave control $4089 and speed $408A.'),
('__fds_wave_load','波形書き込みを有効にして64バイトを$4040～$407Fへコピーし、$4089を0へ戻します。','Enable wave writes, copy 64 bytes to $4040..$407F and reset $4089 to zero.'),
('__fds_mod_load','32バイトを変調テーブルの書き込みポート$4088へ順に送ります。','Send 32 bytes in order to modulation-table write port $4088.'),
('__fds_freq_set','12ビット周波数を$4082・$4083へ書き、$4083の上位制御ビットを消します。','Write the 12-bit frequency to $4082/$4083 and clear $4083’s upper control bits.'),
('__fds_volume_set','音量の下位6ビットに0x80を加えて$4080へ書き、直接音量を設定します。','Write the low six volume bits with 0x80 to $4080 for direct volume control.'),
('__fds_env_set','3引数を加工せず$4080、$4084、$408Aへ順番に書きます。','Write the three raw arguments to $4080, $4084 and $408A, in that order.'),
('nes_fds_wave_load','__fds_wave_loadへ配列を渡すマクロです。64バイトの波形をロードします。','Macro forwarding its array to __fds_wave_load to load a 64-byte wave.')]:fc(name,'fds',ja,en,[fds])

modules['gb:audio']=[msg('module_audio','4音源の直接発音、バンク付き音楽・効果音、左右定位、音量フェード、独自波形を扱います。音楽ストリームのチャンネル番号はCH1=0・CH2=1・CH3=2・CH4=3で、直接操作APIと共通です。CH3は波形、CH4はノイズです。','Provides direct access to four voices, banked music/effects, stereo routing, volume fades and custom waves. Music-stream and direct API channel IDs are CH1=0, CH2=1, CH3=2, CH4=3. CH3 plays waveforms; CH4 generates noise.'),gb_setup,sfx_format]
modules['gb:audio_vblank']=[msg('module_vblank','音楽をVBlank割り込みで更新し、効果音との所有権調整とフレームコールバックを提供します。通常の音楽デコーダーと同時に同じ曲を処理しないでください。','Services music in VBlank, coordinates effect ownership and provides a frame hook. Do not also advance the same song through the ordinary music decoder.'),vb_setup,vb_format]
modules['fc:audio']=[msg('module_fc','標準APUの2パルス・三角波・ノイズ・DMCを直接設定します。音楽シーケンサーや自動ミキサーではなく、ゲーム側が発音タイミングと音源の所有権を管理します。','Direct controls for the standard APU’s two pulses, triangle, noise and DMC. This is not a music sequencer or automatic mixer; the game manages timing and voice ownership.'),fc_voices,fc_dmc]
modules['fc:vrc6_sound']=[vrc6,msg('vrc6_duty_names','VRC6_PULSE_DUTY_12/25/50/75は値0x00/0x10/0x20/0x30の名前です。接尾辞を実測デューティ比と解釈しないでください。KUROSAKIではコードdの比率は(d+1)/16です。','VRC6_PULSE_DUTY_12/25/50/75 name values 0x00/0x10/0x20/0x30. Their suffixes are not measured duty percentages. KUROSAKI models code d as (d+1)/16.')]
modules['fc:vrc7_sound']=[vrc7]
modules['fc:fds_sound']=[msg('module_fds','64段階の波形、変調テーブル、周波数、音量、エンベロープを操作する組み込み関数の宣言です。実装はKITAQFCコンパイラが生成します。','Declares compiler intrinsics for the 64-step waveform, modulation table, pitch, volume and envelopes. KITAQFC generates their implementations.'),fds]
expect['fc-midi']=msg('expected_fc-midi','画面はEXTERNAL PORT DATAと表示し、内蔵音源は鳴りません。送信列（16進数）は7E、C2 05、B2 07 64、92 45 60、82 45 00、F8 FA FB FCです。NTSCの送信間隔57サイクル、受信データの読み取り間隔57サイクルを検査します。受信データはエミュレータの未接続入力による00で、実際の外部機器との通信成功を意味しません。','The screen says EXTERNAL PORT DATA and no internal voice sounds. Transmitted bytes in hexadecimal are 7E; C2 05; B2 07 64; 92 45 60; 82 45 00; F8 FA FB FC. The check requires 57-cycle NTSC transmit cells and 57-cycle data-read spacing. Received 00 comes from the emulator’s unconnected input and does not prove communication with an external device.')
midi=msg('midi_notes','外付け回路が$4016のD0を送信、$4017のD4を受信へ接続する構成です。標準コントローラーだけではMIDI通信できず、内蔵APUも鳴りません。処理中はDMC再生・DMAとNMI・IRQを止め、同じポートや共有作業領域をほかの処理から触らないでください。NTSCの57サイクル/bitは約31,400bps（標準31,250bpsに対して約+0.5%）です。PAL向けのタイミング調整、実アダプターとの往復通信は未検証です。','Requires an external circuit connecting $4016 D0 to TX and $4017 D4 to RX. A standard controller does not provide MIDI and these calls do not play the internal APU. Stop DMC playback/DMA and mask NMI and IRQ during transfers; avoid concurrent port/shared-scratch access. NTSC’s 57 cycles/bit give about 31,400 bps, roughly +0.5% from 31,250. PAL timing and round-trip communication with a physical adapter are unverified.')
midi_ch=msg('midi_ch','MIDIチャンネル0～15。下位4ビットをステータスへ入れます。0が一般的な表示のチャンネル1です。','MIDI channel 0..15; the low nibble enters the status byte. Zero corresponds to displayed MIDI channel 1.')
midi_note=msg('midi_note','MIDIノート番号0～127。69はA4です。値を7ビットへ制限しないため、範囲は呼び出し側で保証します。','MIDI note 0..127; 69 is A4. The helper does not mask to seven bits, so the caller enforces the range.')
for n,ja,en in [('byte','送信する1バイト。生のステータスやデータを含め、0～255をそのまま送ります。','Raw byte 0..255, including status or data bytes.'),('velocity','ベロシティ0～127。7ビットに自動制限しません。','Velocity 0..127; not automatically masked to seven bits.'),('cc','コントローラー番号0～127。7は一般的なチャンネル音量です。','Controller number 0..127; 7 is channel volume.'),('program','プログラム番号0～127。受信機によって楽器への対応が異なります。','Program 0..127; instrument mapping depends on the receiver.')]:args[n]=msg('arg_midi_'+n,ja,en)
for name,ja,en in [
('__midi_out_byte','スタート0、下位ビットから8データビット、ストップ1の順で1バイトを同期送信します。','Synchronously transmit one 8N1 byte: low start, eight data bits least-significant first, high stop.'),
('__midi_in_byte','受信入力が0になるまで待ち、8ビットを時間間隔を空けて読み取ります。','Wait for a low receive input, then sample eight bits at timed intervals.'),
('__midi_note_on','0x90 | (ch & 0x0F)、note、velocityの3バイトでノートオンを送ります。','Send note-on as three bytes: 0x90 | (ch & 0x0F), note, velocity.'),
('__midi_note_off','0x80 | (ch & 0x0F)、note、velocityの3バイトでノートオフを送ります。','Send note-off as three bytes: 0x80 | (ch & 0x0F), note, velocity.'),
('__midi_control_change','0xB0 | (ch & 0x0F)、コントローラー番号、値の3バイトを送ります。','Send control change as 0xB0 | (ch & 0x0F), controller number and value.'),
('__midi_program_change','0xC0 | (ch & 0x0F)とプログラム番号の2バイトを送ります。','Send program change as 0xC0 | (ch & 0x0F) followed by the program number.'),
('__midi_clock','タイミングクロックF8を1回送信します。一定間隔で繰り返す処理は呼び出し側で行います。','Send one timing-clock byte F8. The caller schedules repeated ticks.'),
('__midi_start','リアルタイムStartのFAを1回送ります。ゲーム内の曲ポインタは変更しません。','Send one realtime Start byte FA without changing the game’s song pointers.'),
('__midi_continue','リアルタイムContinueのFBを1回送ります。内部の音楽ドライバーは操作しません。','Send one realtime Continue byte FB without operating the internal music driver.'),
('__midi_stop','リアルタイムStopのFCを1回送ります。内蔵APUや送信済みノートを直接止める関数ではありません。','Send one realtime Stop byte FC. This does not directly silence the APU or previously sent notes.')]:fc(name,'midi',ja,en,[midi],{'ch':midi_ch,'note':midi_note,'value':msg('midi_value','コントローラーの値0～127。上位ビットは自動で消しません。','Controller value 0..127; upper bits are not automatically cleared.')})
contracts['fc:__midi_in_byte']['returns']=[msg('midi_return','読み取ったu8を返します。タイムアウト・フレーミング検査・受信バッファはありません。入力が高いままだと戻らず、低いままだと0を読み取ります。','Returns the received u8. There is no timeout, framing validation or receive buffer. An input held high blocks indefinitely; one held low reads as zero.')]
assert len(contracts)==82,len(contracts)
for platform,data in datasets.items():(SITE/'reference'/f'{platform}-api.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
for name,data in [('sound_contracts.json',contracts),('sound_texts.json',texts),('sound_modules.json',modules),('sound_review_sources.json',{'source_sha256':sources,'records':reviews})]:
    (HERE/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('82 individual sound contracts authored; runtime binding is checked separately.')
