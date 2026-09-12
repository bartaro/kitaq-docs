# GitHub checkout layout

Clone the repositories into sibling directories:

```powershell
git clone https://github.com/bartaro/kitaqgb.git
git clone https://github.com/bartaro/kitaqfc.git
git clone https://github.com/bartaro/kokura.git
git clone https://github.com/bartaro/kurosaki.git
git clone https://github.com/bartaro/sarakura.git
git clone https://github.com/bartaro/kitaq-docs.git
```

Build the tools using each README, then run `./kitaq-docs/samples/build.ps1`
from their parent directory. The generated HTML is committed for offline use.
GitHub Pages can publish the `main` branch root with `.nojekyll`.

The verification screenshots and logs describe the recorded September 12
manual checks. The GitHub packaging build is documented separately in
`PUBLICATION_CHECKS.md`; it is not a claim of new physical-hardware testing.

GUI frontends and PLITA are deferred for this publication.

## Compiler layout update — 2026-09-13

KITAQGB and KITAQFC now put build sources inside a same-named subdirectory.
For example, from the parent of the sibling repositories the project is
`kitaqgb/kitaqgb/kitaqgb.csproj`; the ready-to-run compiler remains
`kitaqgb/kitaqgb.exe`. The same convention applies to KITAQFC. Each compiler
repository includes a Release executable and its `.exe.config`, plus the
library and license notices. Windows with .NET Framework 4.8 is required.

Build commands in both editions use the new layout. Historical source-location
labels and fingerprints still describe the September 12 snapshot: a recorded
`kitaqgb/Program.cs` is now `kitaqgb/kitaqgb/Program.cs`, and likewise for KITAQFC.
The relocation did not change those C# source contents.

日本語: コンパイラのビルド用ソースを各リポジトリ内の同名フォルダーへ移しました。
ビルド済みEXEは各リポジトリの直下にあります。日英本文のビルドコマンドは更新済みです。
過去の検証記録にあるC#ソースの場所には、同名フォルダーを一段追加して読み替えてください。
ライブラリと教材の配置は変わりません。
