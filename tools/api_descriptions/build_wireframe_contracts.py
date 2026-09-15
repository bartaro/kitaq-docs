"""Author source-specific DMG/CGB contracts and bind each to an executable example."""
from pathlib import Path
import hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sys.path.insert(0,str(SITE/'tools'))
import catalog
catalog.ROOT=REPOS;catalog.SITE=SITE
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
texts={};contracts={};sources={};review={};modules={}
def msg(key,ja,en):
    key='wire_'+key;texts[key]={'ja':ja,'en':en};return key

# Each row describes one operation. Shared interfaces get a profile-specific
# record, example and source fingerprint rather than a name-based placeholder.
DMG={
'Init':('raster','LCD・タイル・背景マップを初期化し、モノクロのワイヤーフレーム表示領域を用意します。','Initialize the LCD, tiles and background map for a monochrome wireframe viewport.','カメラ、背景書き込みキュー、ステージをリセットし、BGPを0xB4に設定します。描画前にBeginFrameを呼びます。'),
'BeginFrame':('raster','次のフレームの描画を開始し、隠線判定の適用を解除します。','Begin drawing a frame and disable occlusion testing.','96行設定ではステージとマスクを消去します。120行設定ではピクセルを消去せず、転送時にステージを消費します。未転送の描画や背景キューを破棄する操作ではありません。'),
'SetCamera':('raster','後続の投影に使うカメラ位置と姿勢を保存します。','Store the camera position and orientation for subsequent projection.','角度は16段階で1周します。既に描いた線は移動しません。座標差をs16の範囲に収めてください。'),
'DrawModel':('models','頂点・辺のモデルを、指定位置・回転で等倍描画します。','Draw a vertex-and-edge model at the requested position and rotation at unity scale.','倍率256でDrawModelScaledを呼びます。面や隣接情報があるモデルの辺選択にも、その関数の条件が適用されます。'),
'DrawModelScaled':('models','モデルを拡大縮小し、Y・X・Zの順に回転、平行移動、投影して辺を描きます。','Scale a model, rotate it in Y/X/Z order, translate and project its vertices, then draw edges.','倍率256が等倍、0以下も等倍です。頂点は最大24、面は最大16。96行設定は辺も最大16、120行設定はedge_count個を参照します。NULLのモデル・頂点・辺配列は無視します。奥行き範囲をまたぐ辺は切り詰めず省略します。'),
'EraseModelFaces':('faces','モデルの手前向きの三角形面を投影し、ステージ上の線を面の内側から消します。','Project front-facing model triangles and erase staged pixels inside them.','隠線フラグと面データが必要です。頂点24・面16まで処理し、投影できない面は省略します。倍率0以下は256です。投影用の共有作業領域を書き換えますが、画面転送は行いません。'),
'EraseTriangle2D':('faces','画面座標で指定した三角形の内部を、行ごとの塗りつぶしで消去します。','Erase a screen-space triangle from the stage using horizontal scanline spans.','表示領域内の頂点を指定します。面積0の三角形は無視します。マスクや表示済みVRAMは変更しません。'),
'EraseSpan2D':('raster','指定した1行の両端を含む横区間を消去します。','Erase an inclusive horizontal span on one staged row.','Xの左右は自動で並べ替えますが、両端を0～127に収めてください。範囲外のYは無視します。Xのクリッピングは行いません。'),
'DrawScene':('models','最大8個の物体をカメラに近い順に描き、手前の面で後方の辺を隠します。','Draw up to eight objects near to far, using nearer faces to hide later edges.','物体中心の奥行きで順序を決め、面の外接矩形と線上の5点で隠れ方を近似します。ピクセル単位の深度バッファではありません。visibleが有効なモデルを描き、配列自体は並べ替えません。'),
'SelectEdgeMask':('models','物体のY回転に対応する、事前計算済みの辺表示マスクを選びます。','Select a precomputed edge-visibility mask for the object yaw.','96行設定で使います。Y回転の下位4ビットを16・8・4・2区分へ割り当て、その他の正の個数では先頭を使います。X/Z回転とカメラは無視します。表はRAMに置き、未指定なら0xFFFFを返します。'),
'ProjectPoint':('raster','世界座標の点をカメラから見た画面座標へ変換します。','Project a world-space point through the camera to viewport coordinates.','奥行き8～255だけを受理します。範囲外なら0を返し、出力値は保持します。成功時は画面端に制限した座標を書き込みます。座標制限は線の幾何学的クリッピングではありません。'),
'RotatePoint':('models','1点のX・Y・Zを、指定した回転で直接書き換えます。','Rotate one point in place by the supplied angles.','120行設定で使います。16段階の角度でY・X・Zの順に回転し、各軸の回転前に成分を±220へ制限します。いずれかのポインタがNULLなら何もせず、各成分には別々の領域を指定します。'),
'DrawLine3D':('raster','世界座標の両端を投影して、1本の線を描きます。','Project two world-space endpoints and draw a line between them.','両端が奥行き範囲内の場合だけ描きます。近面・遠面との交点を計算する処理はありません。投影後の端点は個別に画面端へ制限されます。'),
'DrawLine2D':('raster','画面座標の両端を含む、ピクセルが上下左右につながる線をステージへ描きます。','Draw an inclusive, four-connected screen-space line into the stage.','端点は表示領域内に指定します。斜線には接続用のピクセルを補います。120行設定でdirty転送を有効にすると外接するタイル範囲を記録します。VRAMへの反映は転送関数で行います。'),
'DrawIndexedEdges':('direct','頂点配列と2バイトずつの辺インデックスから、整数倍率の線モデルを描きます。','Draw an integer-scaled line model from vertices and two-byte edge-index pairs.','120行設定用です。頂点24個まで、辺は128組以下にしてください。倍率0は1として扱い、物体回転や面による辺選択は行いません。NULL配列、不正な頂点番号、投影できない端点は無視します。'),
'PutBgTile':('raster','背景マップの1セルへのタイル番号書き込みを予約します。','Queue one tile-number write to a background-map cell.','座標は32×32マップのタイル単位です。48件まで予約でき、範囲外と超過分は無視します。EndFrameで反映する専用キューであり、一般のvramライブラリのキューとは別です。'),
'SetPalette':('raster','モノクロ背景パレットBGPの4階調の割り当てを直接変更します。','Write the four-shade mapping of the monochrome background palette register BGP.','2ビットずつのハードウェア形式をそのまま渡します。VBlank待ちは行いません。CGBのRGBパレットは別途設定します。サンプルは0xFCで白地に黒線を表示します。'),
'SetAuxTransfer':('aux_gate','EndFrameで補助領域も転送するかどうかを設定します。','Choose whether EndFrame also transfers the auxiliary strips.','120行設定用です。0で無効、それ以外で有効です。この呼び出しだけでは転送・消去を行いません。補助転送の元データはメインステージと重なります。'),
'SetDirtyTransfer':('dirty','120行表示のメイン転送を、変更タイル中心の転送へ切り替えます。','Select dirty-tile transfer for the 120-row main viewport.','値が同じでも現在・過去のdirty記録とステージを消去します。表示中のVRAMは保持します。古い画像が残る状態で有効化すると未登録のタイルが残り得るため、初期化直後など白紙の画面で設定します。'),
'TransferMainNow':('direct','メインステージ全体を直ちに転送し、読み出したステージを消去します。','Immediately upload the whole main stage and clear the consumed source pixels.','120行設定用です。STATでVRAMアクセスを待ちますが、次のVBlank開始は待ちません。転送設定に従わず、dirty記録や背景予約を変更しません。呼び出し側で表示周期を管理します。'),
'TransferAuxNow':('direct','補助用の6本のストリップを直ちに転送し、元データを消去します。','Immediately upload six auxiliary strips and clear their source bytes.','120行設定用です。補助転送の有効設定にかかわらず実行し、VBlank開始・dirty記録・背景予約を扱いません。元領域D518＋256×列から56バイトずつを読みます。メインステージと重なるため転送順に注意します。'),
'EndFrame':('raster','背景予約とステージの描画をVRAMへ反映します。','Submit pending background writes and staged drawing to VRAM.','次のVBlankを待って背景予約を反映します。120行設定では有効な補助転送を先に行い、続いてメインを全体またはdirty転送します。ステージは転送で消費します。STAT待ちにより複数の表示期間にまたがる場合があります。')}

CGB={
'Init':('raster','CGBの128×96ピクセル描画を初期化します。','Initialize the CGB 128x96 pixel renderer.','倍速へ切り替え、LCDを停止して両タイルバンクとマップを設定します。HUD・生成タイル、既定パレット、色2、カメラ0を用意します。描画前にBeginFrameを呼びます。'),
'InitFullScreen':('full','160×144ピクセルの画面を、使用タイルを割り当てる方式で初期化します。','Initialize a 160x144 renderer that allocates tiles as pixels are drawn.','両タイルバンク、マップ9800、カメラ、パレット、割り当て表を設定します。HUDタイルは読み込みません。1フレームの使用上限は127タイルです。描画中はWRAMバンクの対応を保持します。'),
'InitFastMapLite':('fastmap','輪郭タイルを並べるFastMap描画を初期化します。','Initialize FastMap rendering with precomputed outline tiles.','HUDと48個の輪郭タイルを読み込みます。通常のピクセル表示用マップと立方体スタンプは用意しません。FastMap系の関数で描画・転送してください。完全版ランタイムが必要です。'),
'EnableDoubleSpeed':('raster','CGBのCPUを倍速動作へ切り替えます。','Switch the CGB CPU to double-speed operation.','既に倍速なら何もしません。それ以外はKEY1で切り替えを要求しSTOPを実行します。CGB専用であり、DMGへの代替処理はありません。'),
'SetScreenOffset':('raster','表示のスクロールレジスタSCX・SCYを直接設定します。','Set the LCD scroll registers SCX and SCY directly.','画面への表示位置だけを動かし、投影座標やカメラは変更しません。VBlankを待たないため、表示中に変更する時期は呼び出し側で選びます。'),
'SetPaletteRGB15':('raster','線の4色と、スタンプを着色する背景パレットを設定します。','Set the four drawing colors and background palettes used to tint stamps.','パレット0に4色を設定し、パレット1～3は共通の背景色と各線色で構成します。RGB15形式を渡します。LCD停止中などパレットへ安全に書き込める期間に呼びます。'),
'SetLineColor':('raster','以後の線描画に使う色番号を保存します。','Select the color index for subsequent line drawing.','colorの下位2ビットを保存します。通常の線はビット面をOR合成し、色1と2の交点は3になります。全画面の線は置換です。線の色0は3として扱い、消去にはなりません。'),
'GetLineColor':('raster','現在保存されている線の色番号を読み取ります。','Read the currently stored line-color index.','状態を変更しません。通常は0～3です。FastCubesやFastProjectileには有効な色1～3を渡してください。これらの内部処理は渡した値を直接保存する場合があります。'),
'ClearFrameTiles':('sparse','128×96の表示タイルとステージを消去して描画面を空にします。','Clear the displayed 128x96 frame tiles and the stage.','VBlankでLCDを停止し、両タイルバンクと属性をリセットします。sparse範囲の履歴は保持し、full_modeも変えません。全画面モードの再初期化には使いません。'),
'BeginFrame':('raster','現在の描画モードで新しい空のフレームを開始します。','Start a new empty frame in the selected rendering mode.','通常モードではステージとマスクを消し、全体転送を選択します。全画面ではタイル割り当てと区間情報をリセットします。隠線処理を解除しますが背景予約は保持します。'),
'BeginFrameFast':('sparse','画面を消去して開始し、過去のsparse転送範囲を全画面として扱わせます。','Begin a cleared frame and invalidate the previous sparse ranges to cover the whole viewport.','BeginFrame相当の処理に加え、2つの過去範囲を192タイル全体へ広げます。次のsparse転送が古いバンクの狭い範囲を信用するのを防ぎます。'),
'BeginFrameSparse':('sparse','変更範囲を使う転送用のフレームを開始します。','Begin a frame for sparse-range transfer.','通常モードでもステージ全体を消去します。前のフレームの外側へ範囲が広がっても古いピクセルを持ち越しません。隠線設定を解除し、全画面モードでは専用の割り当てリセットを行います。'),
'ClearSparseStageFast':('sparse','ステージ全体を消去し、128×96全体を転送対象として記録します。','Clear the entire stage and mark the whole 128x96 viewport for upload.','部分消去ではありません。ステージ内の全ピクセルを失います。隠線マスクを消したり、転送モードを選んだりする処理はありません。'),
'MarkDirtyRect2D':('sparse','指定したピクセル矩形を、後の転送が必要な範囲へ追加します。','Add a pixel rectangle to the range requiring a later upload.','描画は行いません。最小・最大の順で指定し、上限127/95を超える値は端へ制限します。128×96用のタイル範囲であり、全画面の割り当て表は操作しません。'),
'SetCamera':('models','投影に使うカメラの位置と16段階の姿勢を保存します。','Store camera position and orientation for projection, using 16 angle steps per turn.','角度は下位4ビットを使います。描画済みのピクセルやLCDのスクロール位置を変更しません。'),
'DrawModel':('models','3Dモデルを指定した位置・回転で等倍描画します。','Draw a 3D model at the supplied position and rotation at unity scale.','DrawModelScaledへ倍率256を渡します。通常の128×96ステージ用で、sparse範囲は記録しません。全体転送を使うか、履歴を無効化して転送してください。'),
'DrawModelScaled':('models','モデルを拡大縮小・回転・投影し、選択された辺を現在色で描きます。','Scale, rotate and project a model, then draw its selected edges in the current color.','頂点24・面16まで処理しますがedge_countを64には制限しません。倍率256は等倍、0以下も等倍です。近面をまたぐ辺のクリッピングはありません。共有投影領域を上書きし、通常ステージに色面をORします。'),
'DrawModelColor':('models','等倍モデルを一時的な指定色で描きます。','Draw a unity-scale model in a temporary color.','DrawModelScaledの制限に従います。描画後は呼び出し前の色に戻します。'),
'DrawModelScaledColor':('models','モデルの倍率と一時的な線色を指定して描きます。','Draw a model with a chosen scale and temporary line color.','colorの下位2ビットを使い、描画後は元の色に戻します。通常のモデル描画と同じ頂点・面・転送範囲の条件に従います。'),
'EraseModelFaces':('faces','投影したモデルの手前向きの面から、ステージのピクセルを消去します。','Erase staged pixels inside projected front-facing model faces.','隠線フラグと面データが必要です。頂点24・面16まで処理します。通常のC側ステージ消去を使うため、呼び出し側でWRAMバンク2を選択します。'),
'EraseTriangle2D':('erase','三角形の内部を通常ステージの両色面から消去します。','Erase a triangle from both color planes of the normal stage.','横区間を表示領域へ制限し、触れたタイルをdirtyにします。呼び出し側でステージのWRAMバンク2を選択します。'),
'EraseSpan2D':('erase','1行の横区間を、WRAMバンクを保存・復元しながら消去します。','Erase a horizontal span while saving and restoring the WRAM bank selection.','Xを並べ替え、右端を127へ制限します。行または左端が範囲外なら無視します。該当タイルも転送対象に記録します。'),
'DrawLineClipped2D':('raster','符号付きの画面座標を表示領域へ切り詰め、指定色の線を描きます。','Clip signed screen coordinates to the viewport and draw a line in the requested color.','各入力は±2047以内です。最大8回の交点計算で切り詰めます。通常モードではdirty範囲も記録します。3D投影や奥行き方向のクリッピングは行わず、描画後は元の色へ戻します。'),
'DrawEdgeListClipped2D':('lists','符号付きの投影済み頂点と辺を検証して、画面外の辺を切り詰めて描きます。','Validate signed projected vertices and edges, then clip and draw the edge list.','頂点1～24・辺64以下で、全インデックスとポインタが必要です。各座標と中心は±2047以内。加算後に±2047を超える端点は線クリッパーで拒否される場合があります。色を保持し、共有画面作業領域を書き換えます。'),
'ProjectAxis48':('lists','1成分を奥行きで割り、焦点距離48相当の画面上の変位へ近似変換します。','Approximate one projected offset with a focal length of 48.','カメラや画面中心は加えません。小さい・負のZは4にし、Zが255を超える間は深度と成分を一緒に右シフトします。成分の大きさは160へ制限します。近面・遠面での拒否はありません。'),
'InvalidateFrameHistory':('sparse','現在と過去2つの転送範囲を192タイル全体へ広げます。','Expand current and two previous transfer ranges to all 192 normal-mode tiles.','ピクセルは消しません。範囲を記録しない描画関数の後や、バンクの内容を信用できない場合に、sparse転送へ全域を含めさせます。'),
'EnableAtomicMaps':('sparse','128×96表示を2つの背景マップの切り替えで提示するよう設定します。','Configure 128x96 presentation to alternate between two background maps.','初期化時に1回呼びます。全画面または設定済みなら無視します。LCDを停止して9800を9C00へ複写し、それぞれの属性を別のタイルバンクへ割り当てます。両マップを予約し、HUD予約も両方へ反映します。'),
'EraseRect2D':('erase','矩形内の通常ステージのピクセルを消去します。','Erase a rectangle from the normal stage.','座標を並べ替え128×96へ制限します。高さ全体の左16/24列は専用ASMを使いますが、一般の矩形はC処理なので呼び出し側でWRAMバンク2を選択します。'),
'EraseLeftGuard24Fast':('guard','通常ステージの左24列を一括で消去します。','Clear the leftmost 24 columns of the normal stage.','WRAMバンクを保存・復元します。dirty範囲を記録しないため、sparse転送では消去したタイルを別途含めます。'),
'DrawWhiteBorderFast':('guard','128×96ステージの外周に色番号2の1ピクセル枠を描きます。','Draw a one-pixel color-index-2 border around the 128x96 stage.','実際の色はパレットによって決まります。サンプルでは青です。内部とWRAMバンクを保持し、dirty範囲は記録しません。'),
'ClearOcclusionMask':('mask','隠線判定用のマスクまたは全画面の区間履歴を空にします。','Clear the occlusion bitmap or full-screen span history.','表示中・ステージのピクセルと隠線の有効設定は変更しません。現在モードに対応するマスクを消去します。'),
'SetOcclusionActive':('mask','後続の線に隠線判定を適用するかを設定します。','Enable or disable occlusion testing for subsequent lines.','0を無効、それ以外を1として保存します。マスクの消去や面の登録は別途行います。'),
'MarkTriangle2D':('mask','三角形を、後から描く線を隠す領域として登録します。','Register a triangle as coverage that can hide subsequently drawn lines.','ピクセルは描かず、隠線処理も自動では有効にしません。頂点は表示領域内に指定します。左右に1ピクセルの余裕を加え、通常モードは127、全画面は159で右端を制限します。'),
'MarkPackedSilhouette2D':('mask','圧縮した行別の輪郭を、128×96の隠線マスクへ登録します。','Mark a packed row-by-row silhouette in the 128x96 occlusion bitmap.','最大29行です。上位4ビット−7が中心ずれ、下位4ビットが半幅、0xFFは行を省略します。y+y0から配置し、左右に2ピクセルを加えて切り詰めます。NULLは無視し、隠線設定や全画面区間は変更しません。'),
'ErasePackedSilhouette2D':('erase','圧縮した輪郭の内側を、通常ステージの両色面から消去します。','Erase a packed silhouette from both color planes of the normal stage.','最大29行、配置・2ピクセルの余裕・形式はMarkPackedSilhouette2Dと共通です。ASMがWRAMバンク2を保存・復元します。dirty範囲は記録しないため転送対象を別途確保します。'),
'DrawScene':('scene','最大8物体を近い順に描き、手前のモデルの面で後方の線を隠します。','Draw up to eight objects near to far, using earlier model faces to occlude later lines.','呼び出し側の配列は並べ替えません。通常128×96用です。color=0はその時点の色を引き継ぎます。マスクを消してから描き、終了時に元の色を戻して隠線設定を解除します。モデルの面・頂点番号は有効なものを用意します。'),
'DrawFastCubes':('cubes','最大3個の立方体を、奥行きに応じた大きさの2D輪郭で素早く表現します。','Draw up to three cubes as depth-sized 2D outlines.','生のZで遠い順に描き、カメラと回転は使いません。selectedは元配列の番号です。NULL・0個は無視し、配列を並べ替えません。描画後の色は元に戻しません。'),
'DrawFastStatus':('cubes','選択中の物体と隠線モードを示す、小さな線状の表示を描きます。','Draw small line indicators for object selection and hidden-line mode.','色3で描き、範囲もdirtyへ追加します。文字タイルではありません。selectedは0～2を指定し、値の検査は行いません。元の色は復元しません。'),
'DrawFastCubeFrame':('stamp','立方体スタンプの前フレームを消し、最大3個の配置と状態表示を背景マップへ転送します。','Replace the preceding cube-stamp frame and upload up to three stamps plus status indicators.','32×32スタンプを8ピクセル単位で配置し、生のZで遠い順に並べます。Initで生成タイルを準備し、安定したFastMapのWRAM対応を保ちます。selectedの下位2ビットは状態表示の位置です。NULLは完全に無視、非NULLで0個なら古い表示を消します。'),
'DrawFastProjectile':('lists','投影済みの中心に、奥行きと位相で変わる6辺の弾を描きます。','Draw a six-edge projectile at an already projected center, with size and orientation selected by depth and phase.','中心はX=10～117、Y=10～85です。4段階の大きさと(phase>>3)&3の向きを使います。カメラは適用せず、範囲をdirtyへ記録し、指定色を保持します。'),
'FastMapBegin':('fastmap','FastMapの16×12セルのタイル番号と属性を空にします。','Clear tile numbers and attributes in the 16x12 FastMap viewport.','シャドーマップの16～31列は保持します。ハードウェア初期化と転送は行いません。完全版ランタイムと安定したWRAM対応が必要です。'),
'FastMapBeginTilesOnly':('fastmap','FastMapの16×12セルのタイル番号だけを消去します。','Clear only tile numbers in the 16x12 FastMap viewport.','属性と16～31列は保持します。背景色の設定を残して番号を入れ替える場合に使います。転送は別の操作です。'),
'FastMapCell':('fastmap','1セルへ、指定色の上・下・左・右の輪郭を追加します。','Add selected top, bottom, left and right outline sides to one map cell.','maskの1/2/4/8が上/下/左/右です。同色の辺は合成し、違う色は置換します。mask=0は無視、color=0は2、3超は3です。16×12の範囲に描きます。'),
'FastMapRect':('fastmap','タイル単位の矩形へ、指定した側の輪郭を配置します。','Place selected outline sides around a tile-coordinate rectangle.','座標を並べ替え16×12へ制限します。sidesの1/2/4/8が上/下/左/右です。内部は保持します。角を区別するには縦横2セル以上を使います。重なる角は順に上書きされます。'),
'FastMapFlush':('fastmap','シャドーマップの先頭12行のタイル番号と属性をVRAMへ転送します。','Upload the first twelve complete rows of shadow tile numbers and attributes to VRAM.','1行32列をマップ9800へ送ります。LCD有効時は新しいVBlankを待ち、停止中は直ちに進みます。GDMAに必要な安全な期間とWRAM対応を確保します。'),
'FastMapFlushTilesOnly':('fastmap','シャドーマップの先頭12行のタイル番号だけをVRAMへ転送します。','Upload only tile numbers in the first twelve complete shadow-map rows.','属性は変更しません。LCD有効時は新しいVBlankを待ちます。1行32列を転送し、完全版ランタイムと安全なGDMA期間が必要です。'),
'ProjectPoint':('models','世界座標の点をカメラから128×96の画面座標へ投影します。','Project a world-space point through the camera to the 128x96 viewport.','深度8～255を受理し、失敗時は0で出力を保持します。成功時は画面内へ制限した座標を書きます。全画面160×144用の投影ではありません。完全版ランタイムが必要です。'),
'ProjectPointNoRotation':('models','カメラ位置だけを差し引いて、回転計算なしで点を投影します。','Project a point after subtracting camera position, without camera rotation.','カメラ角度がすべて0の用途に使います。128×96へ投影し、深度拒否時は出力を保持します。カメラに角度を設定してもこの関数は無視します。'),
'DrawLine3D':('models','世界座標の両端をカメラで投影し、現在色の線を描きます。','Project world-space endpoints through the camera and draw a line in the current color.','片方でも深度範囲外なら線全体を省略します。投影は128×96基準です。通常の線はsparse範囲を記録しないため、全体転送か履歴無効化を使います。'),
'DrawLine3DColor':('models','3Dの線を一時的な指定色で描きます。','Draw a 3D line in a temporary color.','colorの下位2ビットを使い、終了時に元の色へ戻します。投影・深度拒否・転送範囲の条件はDrawLine3Dに従います。'),
'DrawPoint2D':('raster','現在色で1ピクセルを書き込みます。','Write one pixel in the current color.','通常モードは128×96を検査し、dirty範囲を記録して色を置換します。色0なら消去できます。全画面では同一点の線として描くため0は色3、不正座標はoverflowを設定します。'),
'DrawTinyModel2D':('lists','向きを示す6ピクセルの小さな記号を描きます。','Draw a six-pixel marker whose nose and tail indicate direction.','中心はX=3～124、Y=3～92です。turnの下位5ビットを3区分で使います。一般の3D回転ではなく通常ステージ専用です。線色を復元します。'),
'DrawLine2D':('raster','画面座標の両端を含む線を、現在のモードで描きます。','Draw an inclusive screen-space line using the active renderer.','端点は表示領域内に用意し、外側の座標にはDrawLineClipped2Dを使います。通常は色面をORし、dirty範囲を記録しません。全画面はタイルを割り当て色を置換します。色0はどちらも3です。'),
'DrawLine2DColor':('raster','画面上の線を、現在色を保持したまま指定色で描きます。','Draw a screen-space line in a temporary color, preserving the selected color.','DrawLine2Dと同じ座標・色合成・転送条件です。color&3を使いますが、0で線を消すことはできません。'),
'DrawMaskedModel2D':('lists','投影済みの頂点と辺マスクから、有効な辺だけを描きます。','Draw enabled model edges from preprojected vertices and an edge bitmask.','1バイト8辺で下位ビットから使います。全ポインタとインデックスを有効にし、0辺でもedge_mask[0]を用意します。個数制限はなく、中心加算後の座標を画面内に保ちます。色を復元します。'),
'DrawEdgeList2D':('lists','投影済みの符号付き8ビットの頂点変位から、最大64辺を描きます。','Draw up to 64 edges from preprojected signed-byte vertex offsets.','NULL配列は無視します。頂点個数は検査せず、番号は呼び出し側で保証します。中心加算後の座標を画面内に収め、バイト変換の巻き戻りを防ぎます。色を保持します。'),
'DrawLineList2DColor':('raster','4バイトで1本を表す画面座標の線リストを、指定色でまとめて描きます。','Draw a list of four-byte screen-space line records in a chosen color.','各レコードはx0,y0,x1,y1です。最大64本、NULLは無視します。端点を表示領域内に指定し、描画後は元の色へ戻します。'),
'PutBgTile':('raster','背景セルのタイル番号変更をEndFrameまで予約します。','Queue a background tile-number change for EndFrame.','32×32マップ・48件までで範囲外や超過分は無視します。属性は予約しません。atomic-map設定では両背景マップへ番号を反映します。全画面EndFrameはHUDキューを処理しません。'),
'EndFrame':('raster','完成したフレームを転送して表示します。','Upload and present the completed frame.','通常モードは背景予約を処理してステージ全体を送ります。全画面では割り当て済みタイルを送り、HUD予約は処理しません。LCD有効状態が必要で、処理が複数フレームにまたがる場合があります。'),
'EndFrameFast':('sparse','背景予約を処理せず、完成したフレーム全体を転送して表示します。','Upload and present a complete frame without flushing queued background writes.','予約したHUD変更はキューに残ります。通常・全画面の各転送条件と完全版ランタイムが必要です。'),
'EndFrameSparse':('sparse','新しいVBlankを待ち、必要範囲を転送して表示します。','Wait for a fresh VBlank, then upload and present the required sparse ranges.','通常モードはEndFrameSparseNowを呼び、全画面では専用の全体転送を使います。LCDを有効にし、1フレーム内で終わるとは仮定しないでください。'),
'EndFrameSparseNow':('sparse','初回のVBlank待ちを省き、背景予約と現在・2回前の範囲を転送して表示します。','Submit background writes and current/N-2 sparse ranges without the initial fresh-VBlank wait.','内部のHUD復元・DMA・表示切り替えでは待つ場合があります。LCDを有効にし、DMA中のSVBK/VBKを外部から変更しないでください。全画面は専用経路へ進みます。'),
'GetFullScreenTileCount':('capacity','現在フレームで割り当てた全画面用タイル数を返します。','Return the number of full-screen tiles allocated in the current frame.','最大127です。バイト数、空きVRAM容量、表示ピクセル数ではありません。完全版ランタイムで使います。'),
'GetFullScreenOverflow':('capacity','全画面描画で座標不正またはタイル不足が起きたかを返します。','Report an invalid coordinate or tile-allocation exhaustion in full-screen drawing.','一度設定されると、そのフレームの後続の高速描画も抑止されます。BeginFrameで解除します。ハードウェア全体の状態ではありません。'),
'RGB15':('raster','赤・緑・青の5ビット成分をCGBの15ビット色へ組み合わせます。','Pack five-bit red, green and blue channels into a CGB 15-bit color.','各引数は1回だけ評価します。下位5ビットを使うので範囲外は飽和せず巻き戻ります。赤がbit0～4、緑が5～9、青が10～14です。')}

PARAMS={
'model':('頂点・辺・面の配列と個数を持つモデル。表は呼び出し中に読み取れる領域に置きます。','Model holding vertex, edge and face arrays and counts; its tables must remain readable during the call.'),
'objects':('位置・回転・倍率・visibleを持つ物体配列。','Object array containing positions, rotations, scales and visibility flags.'),
'cubes':('簡易立方体の位置・角度・色の配列。','Array of positions, angles and colors for fast cube drawing.'),
'count':('渡した配列の要素数。関数固有の処理上限は注意事項を参照してください。','Number of supplied array entries; see the operation-specific processing limit.'),
'vertices':('3D頂点の配列。','Array of 3D vertices.'),
'vertex_count':('頂点配列の要素数。','Number of vertex-array entries.'),
'edges':('辺の両端の頂点番号。構造体またはバイト対という宣言の形式に従います。','Vertex indices for each edge, in the declared struct or byte-pair format.'),
'edge_count':('辺の本数。','Number of edges.'),
'edge_mask':('下位ビットから順に各辺の表示可否を表すバイト配列。','Byte array with one visibility bit per edge, least-significant bit first.'),
'vertex_x':('投影済み頂点のX変位を並べた配列。','Array of preprojected vertex X offsets.'),
'vertex_y':('投影済み頂点のY変位を並べた配列。','Array of preprojected vertex Y offsets.'),
'vx':('クリッピング前の符号付き16ビットX変位配列。','Signed 16-bit X-offset array before clipping.'),
'vy':('クリッピング前の符号付き16ビットY変位配列。','Signed 16-bit Y-offset array before clipping.'),
'scale_q8':('256を等倍とする拡大率。0以下も等倍として扱います。','Scale with 256 as unity; nonpositive values also mean unity.'),
'scale':('整数の拡大率。0は1として扱います。','Integer scale; zero is treated as one.'),
'color':('描画色番号。通常は1=赤、2=青、3=緑をサンプルのパレットで使います。','Drawing color index; sample palettes use 1=red, 2=blue and 3=green.'),
'bgp':('4色の階調を2ビットずつ並べたBGPレジスタ値。','BGP register value containing four two-bit shade assignments.'),
'tile':('背景セルに置く8ビットのタイル番号。','Eight-bit tile number for the background cell.'),
'sx':('投影結果のX座標を書き込む、有効なu8領域へのポインタ。','Valid writable u8 pointer receiving the projected X coordinate.'),
'sy':('投影結果のY座標を書き込む、有効なu8領域へのポインタ。','Valid writable u8 pointer receiving the projected Y coordinate.'),
'profile':('1行1バイトの輪郭配列。0xFFは行を省略します。','One-byte-per-row silhouette array; 0xFF skips a row.'),
'line_xy':('x0,y0,x1,y1を1組とするバイト配列。','Byte array of x0,y0,x1,y1 records.'),
'line_count':('線レコードの個数。最大64本を処理します。','Number of line records; at most 64 are processed.'),
'active':('0で隠線判定を無効、それ以外で有効にします。','Zero disables occlusion testing; any other value enables it.'),
'flag':('0で転送機能を無効、それ以外で有効にします。','Zero disables the transfer feature; any other value enables it.'),
'hidden_enabled':('0なら隠れた辺も表示し、それ以外なら簡易的に隠します。','Zero includes hidden edges; nonzero selects simplified hidden-edge removal.'),
'selected':('選択物体の元配列番号。スタンプ版では状態表示の番号です。','Original array index of the selected object; the stamp API uses it for a status indicator.'),
'turn':('下位5ビットで小さな記号の向きを選ぶ値。','Value whose low five bits select the tiny marker direction.'),
'phase':('8カウントで向きが変わる回転位相。','Rotation phase, advancing one orientation every eight counts.'),
'mask':('セルの辺指定。1=上、2=下、4=左、8=右。','Cell-side mask: 1=top, 2=bottom, 4=left, 8=right.'),
'sides':('矩形の辺指定。1=上、2=下、4=左、8=右。','Rectangle-side mask: 1=top, 2=bottom, 4=left, 8=right.'),
'value':('投影する符号付き16ビットの成分。','Signed 16-bit component to project.')}
for n,axis in [('pitch','X'),('yaw','Y'),('roll','Z'),('rx','X'),('ry','Y'),('rz','Z')]:
    PARAMS[n]=(axis+'軸の回転。16段階で1周します。','Rotation about '+axis+'; sixteen steps make a full turn.')
for n,c in [('r5','赤'),('g5','緑'),('b5','青')]:PARAMS[n]=(c+'の成分（0～31）。',(dict(r5='Red',g5='Green',b5='Blue')[n])+' channel, 0..31.')
for i in range(4):PARAMS['color'+str(i)]=(f'パレット番号{i}のRGB15色。',f'RGB15 color at palette entry {i}.')
for n in ['scx','scy']:PARAMS[n]=(n.upper()+'へ書くスクロール量（ピクセル）。','Pixel scroll offset written to '+n.upper()+'.')
for n in ['tx','ty','tx0','ty0','tx1','ty1']:PARAMS[n]=('タイル単位の'+('X' if 'x' in n else 'Y')+'座標。','Tile-coordinate '+('X' if 'x' in n else 'Y')+' position.')
for n in ['min_x','min_y','max_x','max_y','x0','x1','y0','y1','ax','ay','bx','by','cx','cy','x','y','z','az','bz']:
    axis=n[-1].upper() if n[-1] in 'xyz' else n[0].upper()
    PARAMS[n]=(axis+'座標。文法とこの関数の座標系に従います。',axis+' coordinate in this operation’s coordinate system.')

CAPTIONS={
'raster':('基本の線・点・消去・座標変換を1画面で確認するサンプルです。','This sample demonstrates basic lines, points, erasure and projection in one frame.'),
'models':('上段に等倍と半分のモデル、下段に同じ倍率の物体配列を描き、投影と倍率の関係を比較します。','Unity and half-scale models appear above an object-array scene at the same scales, demonstrating projection and scaling.'),
'faces':('塗った領域から投影した面を消し、線が残る場所と消える場所を確認します。','Projected faces erase a filled region, making the retained and cleared areas visible.'),
'direct':('投影した横線と補助転送の8×8ブロックを表示し、ステージの元バイトが255から0へ消費されることを確認します。','A projected horizontal line and an auxiliary 8x8 block demonstrate direct transfers; a source byte changes from 255 to 0 as it is consumed.'),
'dirty':('左上の古い枠を消し、画面座標(96,88)～(120,112)に新しい枠だけを表示します。','The old upper-left frame disappears, leaving only a new frame at screen coordinates (96,88)..(120,112).'),
'aux_gate':('メインステージの一部を補助転送へ渡し、画面座標(80,24)に8×8の黒いブロックを表示します。','Part of the main stage is consumed by auxiliary transfer, producing a black 8x8 block at screen coordinate (80,24).'),
'full':('画面座標(8,8)～(151,135)の大きな枠を描きます。上と左が赤、下が青、右が緑で、64タイルを使用しoverflowは0です。','A large frame spans (8,8)..(151,135): red top/left, blue bottom and green right. It uses 64 tiles with overflow zero.'),
'capacity':('異なるタイルに1点ずつ、赤い点を127個並べます。128個目の割り当てを試すとタイル数127のままoverflowが1になります。','127 red dots occupy distinct tiles. Attempting a 128th allocation leaves the count at 127 and sets overflow to one.'),
'sparse':('前の赤と青の枠を消し、最後の緑の枠(80,8)～(112,32)だけを表示します。sparse転送と履歴更新を確認する例です。','Earlier red and blue frames disappear, leaving only the final green frame at (80,8)..(112,32), demonstrating sparse upload and history management.'),
'erase':('赤・青・緑の塗りつぶしから、三角形・横一列・矩形・圧縮輪郭を消して黒い穴を作ります。','Triangles, horizontal spans, rectangles and packed silhouettes cut black holes in red, blue and green filled panels.'),
'guard':('左24列の消去と外周描画を比較します。内側の左24列は黒、残る帯は赤、色番号2の外周は青です。','The left 24 columns are cleared, a red strip remains, and the color-index-2 outer border is blue.'),
'mask':('三角形のマスクで赤い横線の中央を隠し、圧縮輪郭のマスクで青い線を隠します。緑の輪郭が遮蔽領域の位置を示します。','A triangle masks the middle of red scanlines; a packed silhouette masks blue lines. Green outlines locate the occluding region.'),
'lists':('赤い上下2辺、青い正方形、左端で切れた緑の枠、緑の6ピクセル記号、赤い弾を描き、各リスト形式を比較します。','Two red horizontal edges, a blue square, a clipped green frame, a green six-pixel marker and a red projectile compare the list formats.'),
'fastmap':('赤い角、青い大きな矩形、緑の1タイルの枠を描きます。最初に置いた左上の赤いセルは消え、属性を保持する更新も確認できます。','A red corner, large blue rectangle and one-tile green frame demonstrate outline cells. The initial upper-left red cell disappears while the tiles-only update retains attributes.'),
'stamp':('古い立方体スタンプを消し、(72,32)を起点とする32×32の赤い立方体と、上端の緑の状態表示を描きます。','The old cube stamp disappears. A red 32x32 cube begins at (72,32), with green status indicators at the top.'),
'cubes':('左の近い赤い立方体を大きく、右の遠い青い立方体を小さく描きます。赤い立方体の中心の緑の十字が選択状態です。','A nearby red cube on the left is larger than a distant blue cube on the right. A green cross marks the selected red cube.'),
'scene':('手前の赤い正方形(46,30)～(82,66)が、後方の青い横線の中央を隠します。青線は左右だけに見えることを期待します。','A near red square at (46,30)..(82,66) hides the middle of a farther blue horizontal line; only the left and right segments remain visible.')}

def argument(name,param,cgb):
    suffix=name.split('_',1)[1] if '_' in name else name
    if param in ['x','y','z'] and suffix=='RotatePoint':return (param.upper()+'成分を読み書きする独立したs16領域へのポインタ。','Distinct writable s16 pointer for the '+param.upper()+' component.')
    if param in ['x','y'] and suffix=='PutBgTile':return ('32×32背景マップ内のタイル単位の'+param.upper()+'座標。',param.upper()+' tile coordinate in the 32x32 background map.')
    if param=='y0' and 'Silhouette' in suffix:return ('中心Yから先頭行までの符号付きずれ。','Signed offset from center Y to the first silhouette row.')
    if param=='y' and suffix=='EraseSpan2D':return ('消去する行のY座標（ピクセル）。','Pixel Y coordinate of the row to erase.')
    if param in ['ax','ay','az','bx','by','bz'] and '3D' in suffix:return ('世界座標の'+('始点' if param[0]=='a' else '終点')+'の'+param[1].upper()+'成分。',('Start' if param[0]=='a' else 'End')+' point’s world-space '+param[1].upper()+' component.')
    if param in ['x','y','z'] and suffix in ['SetCamera','ProjectPoint','ProjectPointNoRotation','DrawModel','DrawModelScaled','DrawModelColor','DrawModelScaledColor','EraseModelFaces','DrawIndexedEdges']:
        return ('世界座標での'+('カメラ' if suffix=='SetCamera' else '点または物体中心')+'の'+param.upper()+'成分。','World-space '+param.upper()+' component of the '+('camera' if suffix=='SetCamera' else 'point or object origin')+'.')
    if param=='z':return ('大きさの選択または投影に使う奥行き。','Depth used to select size or compute projection.')
    if param in ['x','y','cx','cy'] and suffix not in ['EraseTriangle2D','MarkTriangle2D']:
        return ('表示領域内の中心'+param[-1].upper()+'座標（ピクセル）。','Center '+param[-1].upper()+' coordinate in viewport pixels.')
    if param in ['ax','ay','bx','by','cx','cy']:
        return ('頂点'+param[0].upper()+'の'+param[1].upper()+'座標（表示領域内のピクセル）。','Vertex '+param[0].upper()+' '+param[1].upper()+' coordinate in viewport pixels.')
    if param in ['x0','x1','y0','y1','min_x','min_y','max_x','max_y']:
        axis='X' if 'x' in param else 'Y'
        which='最小側' if param.startswith('min') or param.endswith('0') else '最大側'
        return (which+'の'+axis+'端点（表示領域内のピクセル）。',('Lower' if which=='最小側' else 'Upper')+' '+axis+' endpoint in viewport pixels; ordering and clipping follow this operation’s notes.')
    return PARAMS[param]

def refresh_records(records):
    """Refresh only this module family; do not regenerate another repository."""
    lib=REPOS/'kitaqgb/lib'
    headers={h:{r['name']:r for r in catalog.definitions(lib/'wire3d_dmg.h',h)} for h in [96,120]}
    bodies={h:{r['name']:r for r in catalog.definitions(lib/'wire3d_dmg.c',h) if r['body']} for h in [96,120]}
    cgbh={r['name']:r for r in catalog.definitions(lib/'wire3d_cgb.h')}
    cgbc={r['name']:r for r in catalog.definitions(lib/'wire3d_cgb.c') if r['body']}
    for r in records:
        name=r['name'];stem=r['module']
        if stem=='wire3d_cgb' and name in cgbh:
            r.update(cgbh[name]);r['definition']=cgbc[name]
        elif stem in ['wire3d_dmg','wire3d','dmg3d']:
            canonical='Wire3DDMG_'+name.split('_',1)[1]
            heights=[h for h in [96,120] if canonical in headers[h]]
            h=96 if stem=='wire3d' else 120 if stem=='dmg3d' or 120 in heights else 96
            if stem=='wire3d_dmg':
                r.update(headers[h][canonical]);r['profiles']=heights
                r['comment']='\n\n'.join('WIRE3D_DMG_HEIGHT = '+str(v)+'\n'+headers[v][canonical]['signature']+'\n'+headers[v][canonical]['comment'] for v in heights)
                r['definition']=dict(bodies[h][canonical])
                if len(heights)==2:r['definition']['body']='#if WIRE3D_DMG_HEIGHT == 96\n'+bodies[96][canonical]['body']+'\n#else\n'+bodies[120][canonical]['body']+'\n#endif'
            else:
                source=headers[h][canonical]
                for key in ['ret','args']:r[key]=source[key]
                r['signature']=source['signature'].replace(canonical,name)
                r['comment']='WIRE3D_DMG_HEIGHT = '+str(h)+'.\n'+source['comment']
                r['definition']=dict(bodies[h][canonical])

def main():
    inventory=SITE/'reference/gb-api.json';data=json.loads(inventory.read_text(encoding='utf-8'));byname={r['name']:r for r in data['records']}
    refresh_records(data['records'])
    specs=json.loads((HERE/'wireframe_examples.json').read_text(encoding='utf-8'))
    for record in data['records']:
        if record['module'] not in ['wire3d_dmg','wire3d','dmg3d','wire3d_cgb']:continue
        name=record['name'];cgb=record['module']=='wire3d_cgb'
        suffix='RGB15' if name=='WIRE3DCGB_RGB15' else name.split('_',1)[1]
        group,ja,en,ja_note=(CGB if cgb else DMG)[suffix]
        height=96 if record['module']=='wire3d' or suffix=='SelectEdgeMask' else 120
        label='cgb' if cgb else {'wire3d':'wire3d','dmg3d':'dmg3d','wire3d_dmg':'dmg'+str(height)}[record['module']]
        key='gb:'+name;sample_name='wire_'+label+'_'+group;spec=specs[sample_name]
        program=spec['source'];sample=(SITE/program).read_text(encoding='utf-8')
        support=(SITE/'samples/wire_cgb_example.h').read_text(encoding='utf-8') if cgb else ''
        if not re.search(r'\b'+name+r'\s*\(',sample+support):raise ValueError('API absent from teaching program: '+name)
        comments='\n'.join(line.rstrip() for line in record.get('comment','').splitlines()).strip()
        if name=='WIRE3DCGB_RGB15':comments='Pack the low five bits of each channel into RGB15; evaluate each argument once.'
        notes=[msg(name+'_notes',ja_note,comments)]
        if cgb and suffix in ['GetFullScreenTileCount','GetFullScreenOverflow']:
            notes.append(msg('allocation_before_plot','全画面のタイル割り当ては、隠線・overflowによるピクセル書き込みの抑止より先に進みます。そのため、黒いままのタイルも個数に含まれます。異常後の描画呼び出しでも、個数が増える場合があります。','Full-screen allocation runs before occlusion and overflow suppress pixel writes. Allocated tiles may remain black, and drawing after a fault can still increase the tile count.'))
        if cgb:
            notes.append(msg('cgb_memory','CGB専用です。通常ステージはWRAMバンク2のD300～DEFFを予約します。共有状態を使うため割り込みから再入しないでください。サンプルは固定スタックと完全版ランタイムを使います。','CGB only. Normal staging reserves D300..DEFF in WRAM bank 2. Shared state makes these routines non-reentrant; do not call them recursively from interrupts. Samples use a fixed stack and the full runtime.'))
        else:
            notes.append(msg('dmg_profile_'+str(height),f'このサンプルは128×{height}設定です。'+('画面左上が表示領域の原点です。' if height==96 else '表示領域の原点は画面座標(16,8)です。')+'WRAM D000～DFFFを予約し、CGBで使う場合もそのバンク対応を保持します。共有状態を使い、再入はできません。',f'This sample uses the 128x{height} profile. '+('Its viewport starts at screen (0,0). ' if height==96 else 'Its viewport starts at screen (16,8). ')+'Reserve WRAM D000..DFFF and keep its bank mapping stable on CGB too. Shared state is not reentrant.'))
            if record['module']=='wire3d_dmg':notes.append(msg('profile_choice','WIRE3D_DMG_HEIGHTは既定120です。96行設定はwire3d_dmg_96.cと組み合わせます。SelectEdgeMaskは96行、RotatePoint・DrawIndexedEdges・転送設定・直接転送は120行で提供します。','WIRE3D_DMG_HEIGHT defaults to 120. Use wire3d_dmg_96.c for height 96. SelectEdgeMask is available at height 96; RotatePoint, DrawIndexedEdges, transfer gates and direct transfers require height 120.'))
        purpose=msg(name+'_purpose',ja,en)
        arglist=[]
        for a in record['args'].split(','):
            if a.strip() in ['','void']:continue
            param=re.search(r'(\w+)\s*$',a)[1];a_ja,a_en=argument(name,param,cgb)
            arglist.append([param,[msg(name+'_arg_'+param,a_ja,a_en)]])
        returns=('戻り値はありません。作用する状態と画面への反映時期は上記の通りです。','No return value; the state affected and display timing are described above.')
        if suffix in ['ProjectPoint','ProjectPointNoRotation']:returns=('投影成功時は1、深度で拒否した場合は0です。','Returns 1 on successful projection or 0 on depth rejection.')
        if suffix=='SelectEdgeMask':returns=('表示する辺に対応する16ビットマスク。表がなければ0xFFFFです。','A 16-bit edge visibility mask, or 0xFFFF when no table is supplied.')
        if suffix=='ProjectAxis48':returns=('近似投影した符号付き16ビットの変位。','The approximate signed 16-bit projected offset.')
        if suffix=='GetLineColor':returns=('現在保存されている線色の値。','The currently stored line-color value.')
        if suffix=='GetFullScreenTileCount':returns=('割り当て済みタイル数（0～127）。','Allocated tile count, 0..127.')
        if suffix=='GetFullScreenOverflow':returns=('異常なしは0、タイル不足または座標不正の検出後は1。','Zero with no fault, or one after allocation exhaustion or an invalid coordinate.')
        if suffix=='RGB15':returns=('3成分を組み合わせたu16のRGB15値。','The packed RGB15 value as u16.')
        capja,capen=CAPTIONS[group]
        if group=='raster':
            if cgb:capja+=' 赤い枠に青い斜線、緑の点と横線、青いL字、右上に緑の数字0を描きます。';capen+=' A red frame contains a blue diagonal, with a green point and horizontal line, a blue L and a green zero at the upper right.'
            else:capja+=' 左上の枠の上辺の中央が消え、斜線が中央に投影されます。出力拒否時の座標が91・92のままになることも調べます。';capen+=' The middle of the upper-left frame’s top edge is erased and a diagonal is projected near the center. Rejected projection preserves outputs 91 and 92.'
        if cgb and group=='models':capja='赤・青・緑の等倍と縮小モデル、交差する3D線を比較します。カメラ付き投影と回転省略投影もRAMの値で確認します。';capen='Compare unity and scaled models in red, blue and green and crossing 3D lines. RAM values also check camera projection and its no-rotation variant.'
        expectation=msg(sample_name+'_expected',capja,capen)
        fingerprint=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
        command='New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqgb\\kitaqgb.exe .\\kitaq-docs\\'+program.replace('/','\\')+' .\\kitaqgb\\lib\\'+spec['library']+' -I .\\kitaqgb\\lib -I .\\kitaq-docs\\samples -o .\\out\\'+sample_name+'.gb --profile=dev --stack-bank=fixed --rst-disable --cgb=cgb --cart=mbc5 --romsize=256k --no-cache --no-disasm'
        # Include the complete teaching program: initialization and transfer are
        # part of the contract, particularly for the different staging modes.
        contracts[key]={'review':'wireframe-source-20260915','record_sha256':fingerprint,'purpose':[purpose],'args':arglist,'returns':[msg(name+'_return',*returns)],'notes':notes,'example':{'program':program,'code':sample,'standalone':True,'expected':[expectation],'build':command}}
        review[key]={'record_sha256':fingerprint,'header_line':record['line'],'sample':sample_name}
        for path in [record['path'],record.get('definition',{}).get('path') if record.get('definition') else None]:
            if path:sources[path]=sha(REPOS/path)
    for stem in ['wire3d_dmg','wire3d','dmg3d','wire3d_cgb']:
        ja,en=('CGB専用の色付きワイヤーフレームです。128×96のピクセル描画、160×144のタイル割り当て描画、輪郭タイルを並べるFastMapは別の初期化と転送手順を使います。モデルは頂点・辺・三角形面を呼び出し側が保持します。物理計算は行いません。','Color wireframes for CGB. The 128x96 pixel renderer, 160x144 tile allocator and outline-tile FastMap use distinct initialization and transfer sequences. The caller owns model vertices, edges and triangular faces. This module does not simulate physics.') if stem=='wire3d_cgb' else ('モノクロの3D線描画です。モデルの頂点・辺・面と物体の位置・回転・倍率を指定し、初期化→フレーム開始→描画→転送の順で使います。物理計算は別途行います。角度は16段階、モデル倍率は256が等倍です。','Monochrome 3D line drawing. Supply model vertices, edges and faces and object position, rotation and scale. Use initialization, frame start, drawing and upload in that order. Physics is separate. Angles have sixteen steps per turn; model scale 256 is unity.')
        modules['gb:'+stem]=[msg('module_'+stem,ja,en)]
        modules['gb:'+stem].append(msg('model_fields','Vec3はx/y/z、Edgeは頂点番号a/b、Faceは三角形の頂点番号a/b/cを持ちます。Modelのvertices・edges・facesはそれらの配列、各countは要素数です。edge_facesは辺に隣接する面番号f0/f1で、FACE_NONEは面なしを表します。flagsのMODEL_HIDDEN_LINESは面を用いた辺選択を要求します。面の向きは投影後の符号付き面積で判定するため、頂点の並べ方が重要です。','Vec3 holds x/y/z, Edge vertex indices a/b, and Face triangle indices a/b/c. Model vertices, edges and faces point to these arrays; each count gives its length. edge_faces contains adjacent face indices f0/f1, with FACE_NONE for a missing face. MODEL_HIDDEN_LINES in flags requests face-based edge selection. Projected signed area determines face orientation, so vertex order matters.'))
        modules['gb:'+stem].append(msg('object_fields','Objectはmodelへの参照と、位置x/y/z・角度rx/ry/rz・倍率scale_q8・表示可否visibleを保持します。モデルの共有は可能ですが、表をコピーしたりROMバンクを自動で切り替えたりはしません。参照先を描画中に読み取れるように配置します。CGBのObjectには色番号colorもあります。','Object stores a model reference, position x/y/z, angles rx/ry/rz, scale_q8 and visible. Objects may share a model, but drawing neither copies tables nor automatically switches their ROM banks. Keep referenced data readable throughout drawing. CGB Object also has a color index.'))
        if stem in ['wire3d','wire3d_dmg']:
            modules['gb:'+stem].append(msg('yaw_table','96行設定のModelにはedge_masksとedge_mask_countもあります。物体のY回転に対応する16ビットの辺マスクをRAMへ用意します。使わない場合は両方を0にします。','The 96-row Model also contains edge_masks and edge_mask_count. Supply a RAM table of 16-bit edge masks selected by object yaw, or set both fields to zero when unused.'))
        if stem=='wire3d_cgb':
            modules['gb:'+stem].append(msg('fast_cube_fields','FastCubeのx/yは画面中心からの変位、zは大きさや描画順の選択に使います。FastCubesは角度を使わず、FastCubeFrameはrx/ry/rzから4種類のスタンプを選びます。これらの簡易表示を、カメラ投影を行うDrawModelと区別して使ってください。','FastCube x/y are offsets from the screen center; z selects size or drawing order. FastCubes ignores angles, whereas FastCubeFrame uses rx/ry/rz to choose four stamp variants. These simplified displays serve different purposes from camera-projected DrawModel.'))
    assert len(contracts)==124,len(contracts)
    inventory.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    for name,value in [('wireframe_contracts.json',contracts),('wireframe_texts.json',texts),('wireframe_modules.json',modules),('wireframe_review_sources.json',{'source_sha256':sources,'records':review})]:
        (HERE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    print('124 individually authored wireframe contracts bound to source and samples.')
if __name__=='__main__':main()
