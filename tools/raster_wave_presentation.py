"""Present captured raster animation and source-bound API cards in JA/EN."""
from pathlib import Path
import html,json,re,struct,zlib
SITE=Path(__file__).resolve().parents[1]

def animation(mode):
    folder=SITE/'verification/api-raster-wave'
    def chunk(kind,data):
        return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xFFFFFFFF)
    output=bytearray(b'\x89PNG\r\n\x1a\n');sequence=0
    for index,frame in enumerate([60,68,76,84,92,100,108,116]):
        source=(folder/(mode+'-'+str(frame)+'.png')).read_bytes();pos=8;compressed=bytearray()
        while pos<len(source):
            size=struct.unpack('>I',source[pos:pos+4])[0];kind=source[pos+4:pos+8];data=source[pos+8:pos+8+size]
            if kind==b'IHDR':header=data
            if kind==b'IDAT':compressed+=data
            pos+=size+12
        width,height=struct.unpack('>II',header[:8]);assert (width,height)==(160,144)
        if index==0:
            output+=chunk(b'IHDR',header);output+=chunk(b'acTL',struct.pack('>II',8,0))
        output+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',sequence,width,height,0,0,8,60,0,0));sequence+=1
        if index==0:output+=chunk(b'IDAT',compressed)
        else:
            output+=chunk(b'fdAT',struct.pack('>I',sequence)+compressed);sequence+=1
    output+=chunk(b'IEND',b'')
    (folder/(mode+'-animation.png')).write_bytes(output)

def overview(text,language):
    text=re.sub(r'<!-- raster-wave:start -->.*?<!-- raster-wave:end -->','',text,flags=re.S)
    prefix='' if language=='ja' else '../'
    title='1ラインずつ波打つ背景とタイトルの登場' if language=='ja' else 'A scanline wave and an animated title entrance'
    intro=('背景の横スクロール値を画面の各行で変えると、縦の柱や文字が波の形に曲がります。転送・ワープの場面、ボスの出現、タイトルの登場などに使える表現です。下の動画は、実行結果の8フレーム分の画像を並べたプレビューです。ROMでは波の位相が毎フレーム進みます。' if language=='ja' else
           'Changing background X on each screen line bends pillars and lettering into a wave. This can introduce a warp, a boss encounter or a title. The preview below cycles through eight captured images; the ROM advances the wave phase on every frame.')
    distinction=('Raster_Push系は最大8本の帯を切り替える機能です。1ラインずつ変形させる演出にはRaster_LineXRunFrameを使います。スプライトとウィンドウは変形しません。処理中は可視144ラインにわたってCPUを専有し、割り込みを止めるため、ゲームや音声の更新は呼び出し間に行います。' if language=='ja' else
                 'Raster_Push operations schedule up to eight bands. Use Raster_LineXRunFrame for a separate horizontal offset on every scanline. Sprites and the window do not bend. The renderer occupies the CPU and masks interrupts during all 144 visible lines, so update game logic and audio between calls.')
    caption=('CGB実行結果：柱の縁が各行で左右に曲がり、64ライン周期の波が移動します。最大変位は±24ピクセルです。' if language=='ja' else
             'CGB capture: each row bends the edges of the pillars. A 64-line wave travels through the scene, with up to 24 pixels of displacement in either direction.')
    pieces=['<!-- raster-wave:start -->','<section id="raster-wave-demo"><h4>'+title+'</h4><p>'+intro+'</p><p>'+distinction+'</p>',
            '<figure><img class="screen" width="320" height="288" style="image-rendering:pixelated" src="'+prefix+'verification/api-raster-wave/cgb-animation.png" alt="'+html.escape(caption)+'"><figcaption>'+caption+'</figcaption></figure>']
    for name,label in [('raster_wave','連続する波のサンプル' if language=='ja' else 'Continuous wave sample'),('raster_title_entry','揺れながら登場するタイトルのサンプル' if language=='ja' else 'Title entrance sample')]:
        pieces.append('<p><a href="'+prefix+'samples/api-examples/gb/'+name+'.c">'+label+'</a></p>')
    pieces.append('<p>'+('タイトル例は強い波で右から入り、小さな揺れを経て静止します。同じフォルダーのraster_wave.cを共有するため、両方のソースファイルを一緒に使ってください。ビルド方法と各関数の使い方は下の項目に掲載しています。' if language=='ja' else 'The title enters from the right with a large wave, changes to a small ripple and then settles. It includes raster_wave.c from the same directory, so keep both source files together. The API entries below include build commands and individual usage notes.')+'</p></section><!-- raster-wave:end -->')
    return re.sub(r'(<h3 id="module-raster">.*?</h3>)',lambda m:m[0]+''.join(pieces),text,count=1,flags=re.S)

def main():
    import api_contracts
    from api_raster_wave_proofs import verified_examples
    messages,ui,all_contracts=api_contracts.load()
    contracts={k:c for k,c in all_contracts.items() if c['review']=='raster-wave-source-20260922'}
    proofs=verified_examples(contracts)
    api_contracts.attach_verified_images(contracts,proofs)
    records={r['name']:r for r in json.loads((SITE/'reference/gb-api.json').read_text(encoding='utf-8'))['records']}
    for mode in ['dmg','cgb']:animation(mode)
    for language in ['ja','en']:
        file=(SITE if language=='ja' else SITE/language)/'gb-library.html'
        value=file.read_text(encoding='utf-8');edits=[]
        for name,start,end in api_contracts.CardRanges(value).ranges:
            if 'gb:'+name in contracts:
                edits.append((start,end,api_contracts.render(records[name],contracts['gb:'+name],language,messages,ui)))
        assert len(edits)==6
        for start,end,replacement in reversed(edits):value=value[:start]+replacement+value[end:]
        value=api_contracts.refresh_complete_headers(value,'gb')
        file.write_text(overview(value,language),encoding='utf-8')
    print('Six raster API cards and illustrated examples rendered in Japanese and English')

if __name__=='__main__':main()
