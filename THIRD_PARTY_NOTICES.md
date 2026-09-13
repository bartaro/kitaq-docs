# 出典と権利表記

KITAQGBはZachtronicsのNORCALを出発点とするフォークです。
NORCALを開発したKeith Holman氏と原プロジェクトに謝意を表します。

- [NORCAL: A C Compiler for the NES](https://keithholman.net/nes-compiler.html)
- [HACK*MATCH for the NES](https://trashworldnews.com/hack-match/)

API宣言・実装抜粋・既存使用例・診断用fixtureは、各項目の出典パスに示したローカルソースから採取しました。
現在のKITAQGBに付属するMITライセンスを [reference/KITAQGB-LICENSE.txt](reference/KITAQGB-LICENSE.txt) に同梱しています。

作者提供のREADMEにある追加の権利表記も保持します。

```
MIT License
Copyright (c) 2019 Keith Holman
Copyright (c) 2026 DAISUKE OBA
```

MITライセンスの許諾条項・免責条項は上記同梱ファイルに収録しています。
各構成プロジェクトの配布には、そのプロジェクトの原ライセンス・NOTICEも引き継いでください。

`samples/assets/ascii.c` は作者指定の92字形と配列定義を保持したものです。
`font_gb.h` と `font.chr` はその配置・形式を変換した素材で、新たに字形を描いたものではありません。
変換対応と現在のファイルのハッシュを `verification/font_conversion.json` に記録しています。

2026-09-12、作者DAISUKE OBA氏から、この92字形は自作でMIT公開を許諾するとの確認を得ました。
字形とその形式変換物のMIT表記は [samples/assets/LICENSE.ascii.txt](samples/assets/LICENSE.ascii.txt) にあります。

このマニュアルの独自本文・追加サンプル・生成ツールは [LICENSE](LICENSE) のMIT条件で提供します。
API抜粋等には原プロジェクトの著作権表示も適用されます。参照用に各MIT本文を同梱します。

- [KITAQFCとそのライブラリ](reference/KITAQFC-LICENSE.txt)
- [GBライブラリ](reference/GB-LIBRARY-LICENSE.txt)
- [FCライブラリ](reference/FC-LIBRARY-LICENSE.txt)
- [KOKURA](reference/KOKURA-LICENSE.txt)
- [KUROSAKI](reference/KUROSAKI-LICENSE.txt)
- [SARAKURA](reference/SARAKURA-LICENSE.txt)

日本語参考訳も同梱しています。英語原文を正本とし、相違がある場合は英語原文を優先します。
日本語訳は許諾条件を変更しません。再配布時は英語原文と第三者の原ライセンス本文も保持してください。

- [マニュアル](LICENSE.ja)
- [KITAQGB](reference/KITAQGB-LICENSE.ja.txt)
- [GBライブラリ](reference/GB-LIBRARY-LICENSE.ja.txt)
- [KITAQFC](reference/KITAQFC-LICENSE.ja.txt)
- [FCライブラリ](reference/FC-LIBRARY-LICENSE.ja.txt)
- [KOKURA](reference/KOKURA-LICENSE.ja.txt)
- [KUROSAKI](reference/KUROSAKI-LICENSE.ja.txt)
- [SARAKURA](reference/SARAKURA-LICENSE.ja.txt)
- [自作ASCIIフォント](samples/assets/LICENSE.ascii.ja.txt)

各ソフトのバイナリを配布する場合、Rustクレート等の第三者条件は別途引き継ぐ必要があります。
本体のMIT表記によって第三者の依存物がMITへ変更されることはありません。
このHTML配布物にはコンパイラ・エミュレータ本体を同梱していません。

各ソフトのLICENSEには、自作ASCIIフォントの適用範囲を記載しています。
KITAQGBのLICENSEには、MIT対象のコードと任天堂のロゴ・商標の権利を区別する注記もあります。
参照用LICENSE内のパスは各ソフトの配布ディレクトリを基準とします。


OSにインストールされたフォントや、入力ROM・スクリーンショット等に含まれる別の字形は、
今回確認された自作92字形のMIT許諾には含まれません。

`samples/gb_*.c` と `samples/fc_*.c` は本書のために追加した小さな教材です。
`samples/sarakura` はSARAKURAの既存fixtureに基づく合成診断入力で、実ROMの観測データではありません。
存在しないsnapshot/trace参照だけを取り除いています。
