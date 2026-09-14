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

## Compiler sources and executables

KITAQGB and KITAQFC store build sources in a same-named subdirectory.
From the parent of the sibling repositories, the GB project is
`kitaqgb/kitaqgb/kitaqgb.csproj` and the executable is `kitaqgb/kitaqgb.exe`.
The FC project is `kitaqfc/kitaqfc/kitaqfc.csproj` and the executable is
`kitaqfc/kitaqfc.exe`. Each compiler repository has `lib/`, example sources,
a Release executable and its `.exe.config`. Windows with .NET Framework 4.8
is required. Build instructions are in each README.

日本語：コンパイラのビルド用ソースは各リポジトリ内の同名フォルダーにあります。
ビルド済みEXEと設定ファイルはリポジトリ直下、ライブラリは `lib/` にあります。
ビルド手順は各READMEを参照してください。

## Windows CLI executables

The sarakura, kokura and kurosaki repositories include root-level `sarakura.exe`,
`kokura-cli.exe` and `kurosaki.exe` for Windows x64. No Rust/Python/.NET runtime
is needed to execute these CLIs. Preserve the accompanying license notices.
The independent code in all three projects is licensed by DAISUKE OBA.
Run each `scripts/build.ps1` to build its CLI and copy the EXE to the root.

## Verification

See [publication checks](PUBLICATION_CHECKS.md) for the tested sources,
executables and conditions. Sample run records are in `verification/current/`.
They cover bounded emulator runs and specified pixel checks; physical hardware
is not covered by these records.
