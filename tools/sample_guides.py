"""Individually reviewed introductions to the complete beginner programs.

The text describes the checked-in source, not an assertion of runtime coverage.
Shared lessons have the same explanation only when their GB/FC logic is identical.
"""
from pathlib import Path
import hashlib, html, json, re

SITE = Path(__file__).resolve().parents[1]
# title, purpose, processing, expected observation (Japanese and English)
GUIDES = {}

def add(name, ja, en, platforms=('gb', 'fc')):
    for platform in platforms:
        GUIDES[platform+'_'+name] = {'ja': ja, 'en': en}

add('font',
 ['英数字・記号の一覧表示', '同梱の自作フォントで使える文字と、その表示方法を確認します。', 'm_initで画面とフォントを準備し、m_textで文字列を行ごとに表示します。二重引用符は文字コード34をm_putへ渡して描きます。', '大文字26字、小文字26字、数字10字、記号30字が並びます。各文字が欠けずに表示されるか確認してください。操作は不要です。'],
 ['Display the supplied character set', 'See which letters, digits and punctuation marks the supplied original font contains and how to draw them.', 'm_init prepares the display and font. m_text draws each row; m_put draws the double quote using character code 34.', 'Look for 26 uppercase letters, 26 lowercase letters, 10 digits and 30 punctuation marks. Check that every glyph is legible. No input is required.'])
add('hello',
 ['最初の文字表示', 'ROMを起動し、文字列と数値を背景に表示する最小の流れを学びます。', 'm_initの後にm_textで挨拶を描き、m_numberに42を渡します。最後のループは画面を保ったままフレームを待ちます。', 'HELLO WORLDと042が表示されます。042は3桁にそろえた十進数42です。'],
 ['Your first text display', 'Learn the basic sequence for starting a ROM and drawing text and a number on the background.', 'After m_init, m_text draws the greeting and m_number formats 42. The final loop waits for frames while leaving the screen visible.', 'The screen shows HELLO WORLD and 042. The leading zero is three-digit decimal formatting.'])
add('arithmetic',
 ['桁あふれを避ける算術', '8ビットに収まらない途中結果を16ビットで扱う方法を学びます。', '(u16)200 + 100で300を作り、10で割ってから表示用にu8へ変換します。足し算の前の型変換に注目してください。', '030、つまり計算結果30が表示されます。'],
 ['Arithmetic with a wider intermediate', 'Learn to keep an intermediate result that does not fit in eight bits.', '(u16)200 + 100 produces 300. The program divides it by 10, then converts the result to u8 for display. Notice that the widening cast precedes the addition.', '030 represents the calculated result, 30.'])
add('control',
 ['条件分岐と繰り返し', 'for、continue、while、do/while、switchを小さな計算で試します。', '0～7を加算しますが3はcontinueで飛ばすため合計は25です。whileで30、do/whileで32まで増やし、switchのcase 32で42に置き換えます。', '042が表示されます。各ループと分岐を順番に通った計算結果です。'],
 ['Branches and loops', 'Try for, continue, while, do/while and switch in a small calculation.', 'Adding 0 through 7 while skipping 3 gives 25. The while loop advances to 30, do/while advances to 32, and switch selects case 32 to assign 42.', '042 is the final result of these loops and branches.'], ('gb',))
add('control',
 ['条件分岐と繰り返し', 'for、continue、while、if/elseを小さな計算で試します。', '0～7のうち3を飛ばして合計25を作り、whileで32まで増やします。ifで32との一致を判定し、成功側で42を代入します。', '042が表示されます。このプログラムで使う分岐はif/elseです。'],
 ['Branches and loops', 'Try for, continue, while and if/else in a small calculation.', 'The for loop skips 3 while adding 0 through 7, producing 25. The while loop advances to 32; the following if assigns 42 when that value matches.', '042 is the final result. This program uses an if/else branch.'], ('fc',))
add('aggregate',
 ['関数・配列・構造体・ポインタ', '複数の値をまとめ、関数やポインタを通して扱う方法を学びます。', 'Pointの(10,20)を別の構造体へコピーし、ポインタから配列に1～4を書きます。addの戻り値30に配列の1、2、4と定数5を加えます。', '合計42が042と表示されます。構造体コピー、ptr[i]による書き込み、関数の戻り値を順に追ってください。'],
 ['Functions, arrays, structures and pointers', 'Learn to group values and access them through functions and pointers.', 'The program copies a Point containing (10,20), then writes 1 through 4 into an array through a pointer. It adds the function result 30 to array values 1, 2 and 4 and the constant 5.', 'The sum is displayed as 042. Follow the structure copy, the ptr[i] writes and the function return value.'])
add('bits_memory',
 ['ビット操作とバッファのコピー', '複数のフラグを1バイトにまとめ、バッファを別の領域へコピーします。', '__memsetで4バイトを0にし、ビット3を立て、ビット1を反転します。__memcpyで4バイトすべてを別配列にコピーします。', 'コピー先の先頭バイトが010になります。ビット3の8とビット1の2を合わせた十進数10です。'],
 ['Bit flags and buffer copying', 'Pack flags into a byte and copy a buffer into separate storage.', '__memset clears four bytes. The program sets bit 3, toggles bit 1, then copies all four bytes with __memcpy.', 'The first destination byte is displayed as 010: bit 3 contributes 8 and bit 1 contributes 2.'])
add('input',
 ['押した瞬間だけを数える', 'ボタンを押し続ける状態と、新しく押した瞬間を区別します。', '毎フレームinput_updateを呼び、input_pressed(BTN_A)が真のときだけカウンターを増やします。', '最初は000です。Aを押すと001になり、押し続けても増えません。離して押し直すと002になります。255の次は000に戻ります。'],
 ['Count new button presses', 'Distinguish a newly pressed button from one that remains held.', 'Each frame calls input_update. The counter advances only when input_pressed(BTN_A) is true.', 'The initial count is 000. Press A to get 001; holding it does not add more. Release and press again for 002. The byte counter wraps from 255 to 000.'])
add('fixed',
 ['Q8.8固定小数点の掛け算', '整数とQ8.8固定小数点の相互変換、および掛け算の基本を学びます。', '3と4をfix_from_intでQ8.8へ変換し、fix_mulで掛け、fix_to_intで整数へ戻します。', '3×4の結果12が012と表示されます。画面に出るのは内部の256倍された値ではなく、整数へ戻した値です。'],
 ['Multiply Q8.8 fixed-point values', 'Learn integer-to-Q8.8 conversion, multiplication and conversion back to an integer.', 'fix_from_int converts 3 and 4 to Q8.8. fix_mul multiplies them, and fix_to_int converts the product back.', '012 means 3 × 4 = 12. It is the converted integer, not the internal value scaled by 256.'])
add('entity',
 ['固定長プールからの生成', '動的メモリ確保を使わず、決まった個数の領域からオブジェクトを作ります。', 'entity_initで初期化し、種類1のオブジェクトを(20,30)に作ります。IDが失敗値0xFFでないことを確認してvxへ2を設定します。', '001は使用中オブジェクトの個数です。IDや座標ではありません。この例は更新・描画を行わないので、動くキャラクターは表示されません。'],
 ['Allocate from a fixed object pool', 'Create an object from a fixed set of slots without dynamic allocation.', 'entity_init resets the pool. entity_create creates type 1 at (20,30); the program checks for the failure ID 0xFF before setting vx to 2.', '001 is the active object count, not an ID or coordinate. This example does not update or draw the object, so no moving character appears.'])
add('debug',
 ['診断値をRAMへ記録する', '画面表示とは別に、ゲーム中の変数を診断用バッファへ残します。', 'debug_initで初期化し、フレームタグ1を設定してHPという名前で42を記録します。', '画面の001は記録件数です。HP=42という値そのものは画面ではなく診断バッファにあります。画面だけでは記録内容までは確認できません。'],
 ['Record a diagnostic value in RAM', 'Keep a named game value in a diagnostic buffer separately from the screen display.', 'The program initializes debugging, sets frame tag 1 and records the value 42 under the name HP.', '001 is the number of trace entries. HP=42 is stored in the diagnostic buffer; the screen alone does not show or verify that payload.'])
add('chain',
 ['座標履歴のリングバッファ', 'キャラクターの軌跡などに使う座標履歴の格納方法を学びます。', '4点分の配列をchain_initに渡し、chain_push_headで(20,30)を1点追加します。', '042は処理後に表示する固定の目印です。保存した座標や件数を表していません。履歴の内容を確かめるにはtrailとpointsを観察します。追従する胴体の描画例ではありません。'],
 ['Store a position history', 'Learn how to store a trail of positions in a ring buffer.', 'chain_init attaches an array with room for four points. chain_push_head then records (20,30).', '042 is a fixed completion marker, not a coordinate or count. Inspect trail and points to check the stored history. This program does not draw a following body.'])
add('system',
 ['ライブラリのフレームカウンター', 'フレーム待機とライブラリが管理する経過フレーム数の関係を確認します。', 'system_initの後にsystem_wait_vblankを2回呼び、system_get_frame8の値を表示します。', '002が表示されます。その後のループは本書のm_waitを使うため、この表示値は増え続けません。'],
 ['Read the library frame counter', 'See how counted frame waits affect the library frame counter.', 'After system_init, the program calls system_wait_vblank twice and displays system_get_frame8.', 'The result is 002. The idle loop uses the manual helper m_wait, so the displayed value does not keep increasing.'])
add('scene',
 ['現在のシーンIDを選ぶ', 'タイトル画面やゲーム本編などを区別するシーン番号の選択方法を学びます。', '0で初期化された2件のSceneDefを登録し、scene_change(1)でID 1を選択します。', '001はscene_get_currentが返す現在のIDです。この例にはシーンのコールバックや画面切り替えの描画は登録していません。'],
 ['Select the current scene ID', 'Learn to select an ID that can distinguish scenes such as a title screen and gameplay.', 'The program registers two zero-initialized SceneDef entries and selects ID 1 with scene_change.', '001 is the current ID returned by scene_get_current. No scene callbacks or transition drawing are registered in this example.'])
add('camera',
 ['世界座標から画面座標へ', 'カメラ位置を引いて、ゲーム世界の位置を画面内の位置へ変換します。', 'Camera_SetにQ8.8の2560、つまりX=10ピクセルを渡します。世界座標X=52をCamera_WorldToScreenXで変換します。', '52−10=42なので042と表示されます。このプログラムは座標変換の例で、背景を動かすものではありません。'],
 ['Convert world coordinates to screen coordinates', 'Subtract the camera position to find where a world position belongs on screen.', 'Camera_Set receives Q8.8 value 2560, or X=10 pixels. Camera_WorldToScreenX then converts world X=52.', '052 minus 010 gives the displayed 042. This is a coordinate calculation; it does not scroll a background.'], ('gb',))
add('rle',
 ['RLEデータをRAMへ展開する', '同じ値の繰り返しを、個数と値の組で保存する簡単な圧縮形式を試します。', 'packedの{3,42,0}は「42を3回、0の個数で終了」です。rle_decodeへ3バイトの展開先を渡します。', '最後のバイトout[2]が042と表示されます。展開先の3バイトはすべて42になる想定です。'],
 ['Decode RLE into RAM', 'Try a compact count/value representation of repeated bytes.', 'The packed bytes {3,42,0} mean three copies of 42 followed by a zero-count terminator. rle_decode writes into a three-byte destination.', 'The last byte, out[2], is displayed as 042. All three decoded bytes are expected to contain 42.'], ('gb',))
add('board',
 ['盤面のセルを読み書きする', 'マス目のゲームで使う2次元座標と、保存用配列の関係を学びます。', '16バイトの配列を4×4の盤面として登録し、0でクリアしてからセル(2,1)へ42を書きます。同じ座標を読み返します。', '読み出した42が042と表示されます。4×4の盤面そのものを描画する例ではありません。'],
 ['Read and write a board cell', 'Learn how grid coordinates map to storage for a board game.', 'A 16-byte array backs a 4 × 4 board. The program clears it, writes 42 at cell (2,1), then reads the same cell.', '042 is the value read back. The program does not draw the 4 × 4 board itself.'], ('gb',))
add('physics',
 ['矩形ボディを1ステップ進める', 'ワールドと矩形ボディを初期化し、速度から位置を更新する最小の例です。', 'X=40、Y=40にボディを作り、速度を(2,0)、重力を0にしてkq2d_stepを1回呼びます。', '更新後のX=42が042と表示されます。この例の位置は整数ピクセルです。箱の形や連続したアニメーションを描く例ではありません。'],
 ['Advance a box by one physics step', 'Initialize a world and box body, then update position from velocity.', 'The body starts at (40,40), with velocity (2,0) and zero gravity. The program calls kq2d_step once.', '042 is the resulting X coordinate, measured in integer pixels in this example. No box shape or continuous animation is drawn.'], ('gb',))
add('link',
 ['通信の完了とタイムアウト', 'シリアル転送が完了した場合と、制限時間内に完了しない場合を分けて扱います。', 'マスターとして42を送信し、Link_WaitByteで待ちます。成功すれば受信値、タイムアウトならLink_Cancelの後に0を表示します。', '未接続で転送が完了すれば255、待機がタイムアウトすれば000、相手が接続されていれば受信した値が表示されます。042固定の例ではありません。'],
 ['Handle serial completion and timeout', 'Distinguish a completed transfer from one that does not finish within the wait limit.', 'The master sends 42 and waits with Link_WaitByte. Completion displays the received byte; timeout cancels the transfer and displays zero.', 'An unconnected transfer that completes can return 255. A timeout displays 000; with a connected peer, the display shows its received byte. The result is not always 042.'], ('gb',))
add('bank',
 ['バンクを指定してROMを読む', 'ROMのデータをRAMへコピーするAPIの引数を学びます。', '値7と42の2バイトをfar_data_readでcopiedへ読み込みます。バンク引数は0、コピー長は2です。', 'コピー先の2バイト目が042と表示されます。この例は固定ROMの読み出しで、異なる切替バンク間の転送を実証するものではありません。'],
 ['Read ROM data with a bank argument', 'Learn the arguments for copying ROM data into RAM.', 'far_data_read copies the two bytes 7 and 42 into copied, using bank argument 0 and a length of 2.', 'The second destination byte is displayed as 042. This example reads fixed ROM; it does not demonstrate transfer between different switchable banks.'], ('gb',))
add('asset',
 ['素材IDからデータを読み込む', '素材の位置と長さを表へ登録し、IDで参照する仕組みを学びます。', 'ID 0に種類RAW、バンク0、{7,42}のポインタ、長さ2を登録します。asset_load_rawで2バイトのRAMへ読み込みます。', 'コピー先の2バイト目が042と表示されます。画像表示ではなく、生のバイト列を素材IDで取得する例です。'],
 ['Load data by asset ID', 'Register an asset location and length, then retrieve the bytes by ID.', 'Asset 0 has type RAW, bank 0, a pointer to {7,42} and length 2. asset_load_raw copies it into a two-byte RAM buffer.', 'The second byte is displayed as 042. This demonstrates asset lookup and copying, not image rendering.'], ('gb',))
add('danmaku',
 ['弾をプールへ1個登録する', '弾の管理領域を初期化し、発射後の使用数を調べます。', 'danmaku_resetの後にdanmaku_spawn(40,40,16,0)を呼び、dm_countを表示します。', '001は登録された弾の個数です。この例には更新ループや背景への弾描画処理がないため、画面に弾が飛ぶ様子は表示されません。'],
 ['Allocate one bullet', 'Initialize the bullet pool and inspect its occupancy after spawning.', 'After danmaku_reset, the program calls danmaku_spawn(40,40,16,0) and displays dm_count.', '001 is the number of allocated bullets. There is no bullet update loop or background compositor here, so no moving bullet is drawn.'], ('gb',))
add('cgb_palette',
 ['CGB背景パレットの色を設定する', 'Game Boy ColorのRGB値で、背景と文字の色を指定します。', 'VBlank中にLCDを止め、パレット0の色0を白(31,31,31)、色3を紫(12,0,22)へ設定してから表示を再開します。', 'CGBモードで実行すると白い背景に紫色の文字と042が表示されます。DMGの白黒表示では色の結果を確認できません。'],
 ['Set a CGB background palette', 'Choose background and text colors using Game Boy Color RGB components.', 'The program disables the LCD during VBlank, sets palette 0 color 0 to white (31,31,31) and color 3 to purple (12,0,22), then enables the display.', 'Run in CGB mode to see purple text and 042 on white. DMG monochrome output cannot demonstrate these colors.'], ('gb',))
add('scroll',
 ['背景を横へスクロールする', '背景の内容を書き換えず、表示開始位置を動かす方法を学びます。', '毎フレームphaseを1増やし、Scroll_SetBgへ渡します。8ビット値なので255の次は0になります。', 'SCROLLという文字が左へ動きます。画面の数字ではなく、時間を追って文字の位置が変わることを確認してください。'],
 ['Scroll the background horizontally', 'Move the viewing position without redrawing the background contents.', 'Each frame increments phase and passes it to Scroll_SetBg. The eight-bit position wraps after 255.', 'The word SCROLL moves left. Observe its position over time; a single screenshot cannot show the motion.'], ('gb',))
add('scroll',
 ['NES背景を横へスクロールする', 'PPUのスクロール位置を更新して背景を動かします。', '__scroll_set(0,0)で開始し、フレームごとにphaseを1増やして横位置へ設定します。', 'SCROLLという文字の横位置が変わります。phaseは255から0へ戻ります。複数のネームテーブルを使う広いマップの例ではありません。'],
 ['Scroll the NES background', 'Move the background by updating the PPU scroll position.', 'Starting at __scroll_set(0,0), the program increments phase once per frame and uses it as the horizontal position.', 'The word SCROLL changes horizontal position. phase wraps from 255 to 0. This is not a wide-map example spanning multiple nametables.'], ('fc',))
add('vram_queue',
 ['タイル更新をキューへ積む', '描画の要求と、VRAMへ実際に書き込むタイミングを分けます。', 'vram_queue_bg_tileでタイル座標(3,8)へ番号52を予約し、vram_flushで転送します。同梱フォントの番号52は数字4です。', '背景のタイル座標(3,8)に数字4が表示されます。全画面の数値カウンターではなく、1マスへの描画結果です。'],
 ['Queue a tile update', 'Separate a drawing request from the VRAM transfer that applies it.', 'vram_queue_bg_tile queues tile 52 at tile coordinate (3,8), and vram_flush transfers it. In the supplied font, tile 52 is the digit 4.', 'Look for a single 4 at background tile coordinate (3,8). It is a tile update, not a numeric counter.'], ('gb',))
add('vram_queue',
 ['NMIでタイル更新を反映する', 'メイン処理からPPU更新をキューへ送り、NMI側で反映する流れを学びます。', '__vramq_putでネームテーブルの0x2103へタイル52を予約し、__vramq_commitで送信します。0x2103はタイル座標(3,8)です。', '背景の(3,8)に数字4が表示されます。番号52は同梱フォントの数字4に対応します。'],
 ['Apply a tile update through NMI', 'Submit a PPU update from the main program for the NMI path to apply.', '__vramq_put queues tile 52 at nametable address 0x2103, and __vramq_commit submits it. That address corresponds to tile coordinate (3,8).', 'A single 4 appears at background coordinate (3,8). Tile 52 is the digit 4 in the supplied font.'], ('fc',))
add('sprite',
 ['OAM DMAでスプライトを表示する', '背景とは別に動かせるスプライトの割り当てと表示を学びます。', '空のプールから最初のスロット0を確保し、タイル65と位置(70,80)を設定します。OBJ表示を有効にして、毎フレームシャドーOAMを転送します。', '指定位置に文字Aのスプライトが表示されます。位置は固定です。実際のゲームでは割り当て失敗値を確認してからIDを使います。'],
 ['Display a sprite with OAM DMA', 'Allocate and display a sprite independently of the background.', 'The fresh pool supplies slot 0. The program selects tile 65, sets position (70,80), enables OBJ display and transfers shadow OAM each frame.', 'A stationary letter A appears at the specified sprite position. In a game, check allocation failure before using the returned ID.'], ('gb',))
add('sprite',
 ['NESのOAMスプライト', 'スプライト用の色とOAM情報を準備して、背景とは別の画像を表示します。', 'スプライトパレットを読み込み、スロット0へ位置(70,80)、タイル65、属性0を設定します。表示を有効にしてOAM DMAを繰り返します。', '文字Aのスプライトが固定位置に表示されます。動く画像ではなく、OAM設定と転送の基本例です。'],
 ['Display an NES OAM sprite', 'Prepare sprite colors and OAM data to draw an image independently of the background.', 'The program loads the sprite palette, sets slot 0 to position (70,80), tile 65 and attributes 0, enables rendering and repeats OAM DMA.', 'A stationary letter A appears as a sprite. The example demonstrates OAM setup and transfer, not animation.'], ('fc',))
add('rng',
 ['シード付き疑似乱数', '同じ初期値から同じ乱数列を再現する方法を学びます。', 'rng_seed(1234)で初期化し、rng_range(10)を1回呼びます。上限10は結果に含まれません。', '000～009のいずれかが表示されます。同じプログラムを同じシードで起動すれば同じ値になります。毎フレーム変化する例ではありません。'],
 ['Generate a repeatable random value', 'Use a seed to reproduce a pseudorandom sequence.', 'rng_seed(1234) initializes the generator, then rng_range(10) is called once. Its upper bound, 10, is excluded.', 'The screen shows a value from 000 to 009. Restarting the same program with the same seed reproduces it; the value does not change every frame.'], ('gb',))
add('flags',
 ['ゲーム進行フラグ', 'イベントを達成したかなどの真偽値を、フラグ番号で管理します。', 'フラグ12をクリアしてから立て、flag_getで読み返します。', '001はフラグ12が真であることを示します。この例はRAM上のフラグ操作で、電源を切っても残るセーブ処理は行いません。'],
 ['Store a game-state flag', 'Represent a Boolean state, such as whether an event is complete, using a flag number.', 'The program clears flag 12, sets it and reads it back with flag_get.', '001 means flag 12 is true. This example operates on RAM flags and does not save them across power cycles.'], ('gb',))
add('circle',
 ['円形ボディを1ステップ進める', '円の物理ワールドへボディを登録し、速度による位置更新を試します。', '半径4、位置(40,40)、速度(2,0)の円を有効にします。重力0、linear_damping_q8=255でkq2dc_stepを1回呼びます。', '更新後のX=42が042と表示されます。円の輪郭や衝突アニメーションを描画する例ではなく、整数座標の更新例です。'],
 ['Advance a circle by one physics step', 'Set up a circular body and update its position from velocity.', 'The active circle has radius 4, position (40,40) and velocity (2,0). Gravity is zero and linear_damping_q8 is 255; kq2dc_step runs once.', '042 is the resulting integer X coordinate. This example does not draw a circle outline or collision animation.'], ('gb',))
add('subpixel',
 ['Q5.3で端数の移動を積み重ねる', '1ピクセル未満の移動を端数として保持し、整数座標へ繰り上げる方法を学びます。', 'X=40から、2/8ピクセルの移動を8回加算します。右シフトで整数部分を取り出し、マスクで端数を残します。', '合計2ピクセル進み、X=42が042と表示されます。これは正方向の手動積算例です。負方向には対応する繰り下げ処理が必要です。'],
 ['Accumulate fractional Q5.3 motion', 'Keep subpixel motion as a remainder and carry whole pixels into the position.', 'Starting at X=40, the loop adds 2/8 pixel eight times. A right shift extracts whole pixels; a mask retains the remainder.', 'The total motion is two pixels, so the screen shows X=42 as 042. This manual integration example handles positive motion; negative motion needs a matching borrow path.'], ('fc',))
add('sound',
 ['フレーム更新で効果音を再生する', '効果音データを開始し、毎フレームの更新で最後まで進める方法を学びます。', 'Audio_Initの後、Audio_PlaySFXへtoneとチャンネルID 1を渡します。メインループからAudio_Updateを1フレームに1回呼びます。', '042を表示しながら短いパルス波の効果音が鳴ります。042は固定の目印で、音量や再生位置ではありません。音の確認には音声出力または録音を使ってください。'],
 ['Service a sound effect each frame', 'Start a sound-effect stream and advance it through regular frame updates.', 'After Audio_Init, Audio_PlaySFX starts tone on channel ID 1. The main loop calls Audio_Update once per frame.', 'A short pulse effect plays while 042 remains visible. That number is a fixed marker, not volume or playback position. Use audio output or a recording to assess the sound.'], ('gb',))
add('sound',
 ['APUのパルス音を鳴らす', 'NES本体のパルスチャンネルへ音量・タイマー・長さを設定します。', 'nes_apu_initの後にnes_sfx_square1(0xBF,400,20)を呼びます。0xBFは一定音量と長さカウンター停止を指定するため、音は持続します。20は長さテーブルの番号で、20フレームという意味ではありません。', '042を表示しながらパルス音が鳴り続けます。音を止めるにはnes_apu_silence_allを呼びます。042自体は発音確認の結果ではありません。'],
 ['Play an APU pulse tone', 'Set the built-in NES pulse channel control, timer and length values.', 'After nes_apu_init, the program calls nes_sfx_square1(0xBF,400,20). Control 0xBF selects constant volume and halts the length counter, so the tone sustains. The value 20 is a length-table index, not 20 frames.', 'A sustained pulse tone plays while 042 is displayed. Call nes_apu_silence_all to stop it. The displayed marker alone does not verify sound output.'], ('fc',))

def render(sample_id, language):
    title, purpose, processing, expected = GUIDES[sample_id][language]
    labels = ('目的', '処理の流れ', '操作と期待する結果') if language == 'ja' else ('Purpose', 'How it works', 'Controls and expected result')
    return '<div class="sample-guide">'+''.join('<p><b>'+label+'：</b>'+html.escape(text)+'</p>' if language=='ja' else '<p><b>'+label+': </b>'+html.escape(text)+'</p>' for label,text in zip(labels,(purpose,processing,expected)))+'</div>'


def screen(sample_id, language):
    """Place the captured screen beside its specific expected visual result."""
    if not (SITE/'verification'/(sample_id+'.png')).is_file():
        return ''
    prefix = '' if language == 'ja' else '../'
    caption = ('表示例：' if language == 'ja' else 'Display example: ')+GUIDES[sample_id][language][3]
    alt = GUIDES[sample_id][language][0]+': '+GUIDES[sample_id][language][3]
    return '<figure class="example-result"><img class="screen" loading="lazy" src="'+prefix+'verification/'+sample_id+'.png" alt="'+html.escape(alt,quote=True)+'"><figcaption>'+html.escape(caption)+'</figcaption></figure>'


def gallery(language):
    """Render a portable result gallery without exposing local execution logs."""
    from public_presentation import INTRO, LANGUAGES
    manifest = json.loads((SITE/'samples/manifest.json').read_text(encoding='utf-8'))
    title = '確認した実行画面' if language == 'ja' else 'Captured screens'
    out = ['<div data-public-gallery="true"><h2 id="scope">'+title+'</h2><p>'+html.escape(INTRO[LANGUAGES.index(language)])+'</p>']
    for item in manifest:
        sid = item['id']
        platform = item['platform']
        caption = GUIDES[sid][language][0]
        links = [('kitaq'+platform, 'コンパイラ説明書のサンプルに戻る' if language == 'ja' else 'Return to the compiler manual example'),
                 (platform+'-library', 'ライブラリ説明書のサンプルに戻る' if language == 'ja' else 'Return to the library manual example')]
        out.append('<section id="'+sid+'"><h2 id="result-'+sid+'">'+html.escape(caption)+' <code>'+sid+'</code></h2>'+render(sid,language)+screen(sid,language)+'<p class="sample-return">'+' / '.join('<a href="'+page+'.html#sample-'+sid+'">'+label+'</a>' for page,label in links)+'</p></section>')
    return ''.join(out)+'</div>'

def update_existing():
    manifest=json.loads((SITE/'samples/manifest.json').read_text(encoding='utf-8'))
    assert {x['id'] for x in manifest} == set(GUIDES)
    records=[]
    for language in ('ja','en'):
        for platform in ('gb','fc'):
            path=SITE/('en' if language=='en' else '')/(platform+'-library.html')
            text=path.read_bytes().decode('utf-8')
            for item in manifest:
                if item['platform']!=platform:continue
                sid=item['id'];title=GUIDES[sid][language][0]
                pattern=r'(<details class="sample searchable" id="sample-'+re.escape(sid)+r'">)(.*?)(</details>)'
                match=re.search(pattern,text,re.S);assert match,sid
                body=match[2]
                body=re.sub(r'<summary>.*?</summary>', '<summary>'+html.escape(title)+' <code>'+item['file']+'</code></summary>',body,count=1,flags=re.S)
                body=re.sub(r'<div class="sample-guide">.*?</div>', '',body,flags=re.S)
                body=re.sub(r'<p>(?:期待結果：|Expected result: ).*?</p>','',body,count=1,flags=re.S)
                body=body.replace('</summary>','</summary>'+render(sid,language),1)
                # Keep the existing captured image and links; explain what to look for.
                caption=('表示例：' if language=='ja' else 'Display example: ')+GUIDES[sid][language][3]
                body=re.sub(r'<figcaption>.*?</figcaption>','<figcaption>'+html.escape(caption)+'</figcaption>',body,flags=re.S)
                text=text[:match.start()]+match[1]+body+match[3]+text[match.end():]
                source=SITE/'samples'/item['file']
                records.append(dict(language=language,id=sid,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
            path.write_bytes(text.encode('utf-8'))
    return records

if __name__ == '__main__':
    print(json.dumps({'explained':len(update_existing()),'programs':len(GUIDES)}))
