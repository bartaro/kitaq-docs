"""Explain the explicit CHR RAM build mode next to mapper configuration."""
from pathlib import Path
import re
from generate import md
SITE=Path(__file__).resolve().parents[1]
TEXT={
'ja':'''### 8.1　描画を書き換えるCHR RAM

`--nes-chr-ram` は、実行中にパターンを書き換える8 KiBのCHR RAMを使うカートリッジROMを生成します。ROMファイルへCHRデータは格納しないため、プログラムが初期化時にタイルをPPUへ書き込みます。`wire3d.c` はこの方式を使います。

```powershell
New-Item -ItemType Directory -Force .\\out | Out-Null
.\\kitaqfc\\kitaqfc.exe .\\kitaq-docs\\samples\\api-examples\\fc\\wire3d_projection.c -I .\\kitaqfc\\lib --mapper=nrom --nes-chr-ram -o .\\out\\wire3d_projection.nes
```

`--nes-chr=tiles.chr` または `--chr-rom=tiles.chr` は、用意したパターンをCHR ROMとして組み込む指定です。`--nes-chr-ram` と同時には指定できません。CNROMの選択とも併用できません。対象マッパー・基板が必要なCHR RAMを備えることを確認してください。

CHRの指定をどれも省略すると、コンパイラは空の8 KiB CHR ROMを組み込みます。実行中にパターンを書き込むサンプルでは、`--nes-chr-ram` を明示してください。CHR RAMはCPU側のPRG RAMとは別のメモリーで、ワイヤーフレームのステージ用PRG RAMも別途必要です。
''',
'en':'''### 8.1  CHR RAM for writable graphics

`--nes-chr-ram` builds a cartridge ROM that uses 8 KiB of writable CHR RAM. No CHR data is stored in the ROM file, so the program must upload tile patterns to the PPU during initialization. The `wire3d.c` renderer uses this mode.

```powershell
New-Item -ItemType Directory -Force .\\out | Out-Null
.\\kitaqfc\\kitaqfc.exe .\\kitaq-docs\\samples\\api-examples\\fc\\wire3d_projection.c -I .\\kitaqfc\\lib --mapper=nrom --nes-chr-ram -o .\\out\\wire3d_projection.nes
```

`--nes-chr=tiles.chr` or `--chr-rom=tiles.chr` embeds prepared patterns as CHR ROM. Neither can be combined with `--nes-chr-ram`. The CNROM profile also rejects CHR RAM mode. Check that the target mapper and board provide the required CHR RAM.

Omitting all CHR options embeds a blank 8 KiB CHR ROM. Explicitly select `--nes-chr-ram` for examples that upload patterns at runtime. CHR RAM is separate from CPU-side PRG RAM; the wireframe staging buffer also needs its own PRG RAM allocation.
'''}

def overview(text,language):
    text=re.sub(r'<!-- fc-chr-ram:start -->.*?<!-- fc-chr-ram:end -->','',text,flags=re.S)
    block='<!-- fc-chr-ram:start --><section id="chr-ram-build">'+md(TEXT[language])+'</section><!-- fc-chr-ram:end -->'
    text,count=re.subn(r'(?=<h2[^>]*>9[ .　])',lambda m:block,text,count=1)
    assert count==1
    return text

def main():
    for language in ['ja','en']:
        file=(SITE if language=='ja' else SITE/'en')/'kitaqfc.html'
        file.write_text(overview(file.read_text(encoding='utf-8'),language),encoding='utf-8')
    print('JA/EN CHR RAM build instructions added')

if __name__=='__main__':main()
