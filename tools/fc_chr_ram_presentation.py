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
''',
'zh-CN':'''### 8.1　使用 CHR RAM 更新图形

`--nes-chr-ram` 生成使用 8 KiB 可写 CHR RAM 的卡带 ROM。ROM 文件中不保存 CHR 数据，因此程序必须在初始化时将图块图案上传到 PPU。`wire3d.c` 渲染器使用此模式。

```powershell
New-Item -ItemType Directory -Force .\\out | Out-Null
.\\kitaqfc\\kitaqfc.exe .\\kitaq-docs\\samples\\api-examples\\fc\\wire3d_projection.c -I .\\kitaqfc\\lib --mapper=nrom --nes-chr-ram -o .\\out\\wire3d_projection.nes
```

`--nes-chr=tiles.chr` 或 `--chr-rom=tiles.chr` 将准备好的图案作为 CHR ROM 嵌入。这两个选项都不能与 `--nes-chr-ram` 同时使用。CNROM 配置也不支持 CHR RAM 模式。请确认目标映射器和电路板具备所需的 CHR RAM。

如果省略所有 CHR 选项，编译器会嵌入空白的 8 KiB CHR ROM。运行时上传图案的示例必须明确指定 `--nes-chr-ram`。CHR RAM 与 CPU 使用的 PRG RAM 是两块不同的内存；线框绘图的暂存缓冲区还需要单独分配 PRG RAM。
'''}

def overview(text,language):
    text=re.sub(r'<!-- fc-chr-ram:start -->.*?<!-- fc-chr-ram:end -->','',text,flags=re.S)
    if language in TEXT:prose=TEXT[language]
    else:
        prose=(SITE/'tools/i18n'/language/'fc-chr-ram.md').read_text(encoding='utf-8')
        assert prose.count('{{BUILD}}')==1
        command=re.search(r'```powershell\n.*?```',TEXT['en'],re.S)[0]
        prose=prose.replace('{{BUILD}}',command)
    block='<!-- fc-chr-ram:start --><section id="chr-ram-build">'+md(prose)+'</section><!-- fc-chr-ram:end -->'
    # Standalone publication must not depend on generate_en's global code
    # renderer override having run earlier in this Python process.
    label={'ja':'コピー','zh-CN':'复制','ko':'복사','zh-TW':'複製','fr':'Copier','es':'Copiar','de':'Kopieren'}.get(language,'Copy')
    block=re.sub(r'(<button class="copy" type="button">)(?:コピー|Copy)(</button>)',lambda m:m[1]+label+m[2],block)
    text,count=re.subn(r'(?=<h2[^>]*>9[ .　])',lambda m:block,text,count=1)
    assert count==1
    return text

def main():
    for language in ['ja','en']:
        file=(SITE if language=='ja' else SITE/'en')/'kitaqfc.html'
        file.write_text(overview(file.read_text(encoding='utf-8'),language),encoding='utf-8')
    print('JA/EN CHR RAM build instructions added')

if __name__=='__main__':main()
