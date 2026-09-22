"""Refresh the tested GB wireframe entries and explain their rendering paths."""
from pathlib import Path
import json,re
import api_contracts
from api_wireframe_proofs import verified_examples
SITE=Path(__file__).resolve().parents[1]

def overview(text,language):
    text=re.sub(r'<!-- wire-speed:(dmg|cgb):start -->.*?<!-- wire-speed:\1:end -->','',text,flags=re.S)
    for platform in ['dmg','cgb']:
        if language=='ja':
            title='描画速度を生かす使い方'
            body=('表示領域内の線は、描画先アドレスとビット位置を逐次更新し、残りの画素数や誤差をCPUのレジスタで管理します。1画素ごとのタイル座標計算を省き、斜線の接続用画素も同じループで描きます。遮蔽を使う場合は、線上の5点をマスクで調べ、描画が必要な線を同じ高速経路へ渡します。マスクの行はバイト単位で埋め、両端の部分的なビットを保持します。面の外接矩形と5点による近似なので、三角形や線を画素ごとに正確に隠す方式ではありません。' if platform=='dmg' else '通常の128×96描画では、描画先アドレスを逐次更新します。遮蔽なしの線は色のビットプレーンを1本ごとに選び、画素数や誤差をCPUのレジスタで管理します。遮蔽を使う線も色のビットプレーンを1本ごとに選び、描画先とマスクのアドレスを逐次更新します。各画素では対応するマスクビットを確認し、覆われていない画素だけを書きます。160×144描画とFastMapは、それぞれ専用の描画経路です。')
            body+=' 0度・90度・180度・270度の回転は、入力の範囲制限を行ってから座標の交換と符号変更で計算します。ゲーム全体の速度にはモデルの頂点数、辺の長さ、遮蔽、VRAM転送も影響します。各関数の所要時間と、1画像を完成させる時間を分けて計測してください。'
        else:
            title='Using the fast rendering paths'
            body=('Lines inside the viewport advance the drawing address and pixel bit incrementally, keeping the remaining pixel count and error in CPU registers. This avoids per-pixel tile-coordinate calculations and also draws bridge pixels for connected diagonals. When occlusion is active, five samples along the line determine whether drawing is needed; accepted lines use the same fast path. Mask rows are filled a byte at a time while preserving partial boundary bits. Face bounding rectangles and five-point rejection are approximations, not exact per-pixel triangle or line occlusion.' if platform=='dmg' else 'The normal 128×96 renderer advances drawing addresses incrementally. For unoccluded lines it selects the color plane once per line and keeps the pixel count and error in CPU registers. Occluded lines also select the color planes once per line and advance both drawing and mask addresses incrementally. Each pixel tests its mask bit and is written only when uncovered. The 160×144 renderer and FastMap each have dedicated paths.')
            body+=' Rotations of 0, 90, 180 and 270 degrees clamp inputs, then use coordinate swaps and sign changes. Overall game performance also depends on vertex count, edge length, occlusion and VRAM transfers. Measure individual operations separately from the time needed to complete a displayed image.'
        block=f'<!-- wire-speed:{platform}:start --><section id="wire-speed-{platform}"><h4>{title}</h4><p>{body}</p></section><!-- wire-speed:{platform}:end -->'
        text,count=re.subn(r'(<h3 id="module-wire3d_'+platform+r'">.*?</h3>)',lambda m:m[0]+block,text,count=1,flags=re.S)
        assert count==1
    return text

def main():
    messages,ui,all_contracts=api_contracts.load()
    contracts={k:c for k,c in all_contracts.items() if c['review']=='wireframe-source-20260915'}
    proofs=verified_examples(contracts);assert len(proofs)==124
    api_contracts.attach_verified_images(contracts,proofs)
    records={r['name']:r for r in json.loads((SITE/'reference/gb-api.json').read_text(encoding='utf-8'))['records']}
    for language in ['ja','en']:
        file=(SITE if language=='ja' else SITE/'en')/'gb-library.html';text=file.read_text(encoding='utf-8');edits=[]
        for name,start,end in api_contracts.CardRanges(text).ranges:
            if 'gb:'+name in contracts:edits.append((start,end,api_contracts.render(records[name],contracts['gb:'+name],language,messages,ui)))
        assert len(edits)==124
        for start,end,value in reversed(edits):text=text[:start]+value+text[end:]
        file.write_text(overview(text,language),encoding='utf-8')
    print('124 wireframe API entries refreshed in JA/EN with 57 pixel-exact runs')

if __name__=='__main__':main()
