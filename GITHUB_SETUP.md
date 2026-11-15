# Working with the repositories

Clone only the repositories you need into sibling directories. The manual examples use this layout:

```powershell
git clone https://github.com/bartaro/kitaqgb.git
git clone https://github.com/bartaro/kitaqfc.git
git clone https://github.com/bartaro/kokura.git
git clone https://github.com/bartaro/kurosaki.git
git clone https://github.com/bartaro/sarakura.git
git clone https://github.com/bartaro/kitaq-docs.git
```

Use KITAQGB and KOKURA for GB/CGB, or KITAQFC and KUROSAKI for NES/Famicom/FDS. SARAKURA reads compiler metadata and emulator diagnostic events. See each repository's README for installation and the first example.

## Compilers, libraries and samples

The compilers and host tools are written in Rust; the `lib/` libraries are C code linked into your ROM. Windows executables are at each repository root, with Linux and macOS versions under `bin/`. Running the supplied executables does not require Rust or .NET. Keep the libraries and license notices with the tools.

To rebuild, use the repository's `scripts/build.ps1` or `scripts/build.sh`. Compiler sources are under `src/`, with dependencies in `Cargo.toml` and `Cargo.lock`.

Run `./kitaq-docs/samples/build.ps1` from the parent of the sibling directories to build the manual samples. The generated HTML is committed for offline reading. Open `kitaq-docs/index.html`, keeping the images, samples and styles in place. GitHub Pages serves the `main` branch root with `.nojekyll`.

## 日本語

必要なリポジトリを同じ親フォルダーの下に配置してください。GB/CGB開発にはKITAQGBとKOKURA、FC/NES/FDS開発にはKITAQFCとKUROSAKIを使用します。SARAKURAはコンパイラのメタデータとエミュレータの診断イベントを読み込みます。

コンパイラとPC側の補助ツールはRust製、ROMに組み込む`lib/`はC製です。Windows用実行ファイルは各リポジトリ直下、Linux・macOS用は`bin/`にあります。配布実行ファイルの利用にRustや.NETは不要です。導入・ビルド手順は各READMEを参照してください。

マニュアルはフォルダー一式を保持し、`kitaq-docs/index.html`から読めます。サンプルのビルドは、各リポジトリを配置した親フォルダーから`./kitaq-docs/samples/build.ps1`で実行します。
