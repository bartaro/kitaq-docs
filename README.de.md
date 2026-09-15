# Handbücher der KITAQ-Serie

[English](README.md#english) | [日本語](README.md#japanese) | **Deutsch**

<!-- ai-prompts:start -->
## Prompts zur Spieleentwicklung mit KI

Tragen Sie die Anforderungen ein und geben Sie den vollständigen Prompt an Ihre KI weiter. Er umfasst die Implementierung, Emulator-Tests, die Analyse mit SARAKURA und die erneute Prüfung nach Korrekturen.

[KITAQGB](https://bartaro.github.io/kitaq-docs/de/loop-engineering.html#gb) · [KITAQFC](https://bartaro.github.io/kitaq-docs/de/loop-engineering.html#fc)
<!-- ai-prompts:end -->

## Direkt zum deutschen Handbuch

- [KITAQGB](https://bartaro.github.io/kitaq-docs/de/kitaqgb.html)
- [KITAQGB-Bibliothek](https://bartaro.github.io/kitaq-docs/de/gb-library.html)
- [KOKURA](https://bartaro.github.io/kitaq-docs/de/kokura.html)
- [KITAQFC](https://bartaro.github.io/kitaq-docs/de/kitaqfc.html)
- [KITAQFC-Bibliothek](https://bartaro.github.io/kitaq-docs/de/fc-library.html)
- [KUROSAKI](https://bartaro.github.io/kitaq-docs/de/kurosaki.html)
- [SARAKURA](https://bartaro.github.io/kitaq-docs/de/sarakura.html)

[Japanische Ausgabe](https://bartaro.github.io/kitaq-docs/) / [Englische Ausgabe](https://bartaro.github.io/kitaq-docs/en/) / [Repositorys beziehen und anordnen](GITHUB_SETUP.md)

## HTML-Handbücher

Die sieben Bände sind in neun Sprachen verfügbar und beschreiben den Quellenstand vom 14. September 2026. Alle Ausgaben enthalten dieselben 1.055 API-Einträge und 47 vollständigen Beispielprogramme. Öffnen Sie `de/index.html` für Deutsch, `en/index.html` für Englisch oder `index.html` für Japanisch. In jedem Band können Sie die Sprache wechseln. Die Prüfprotokolle nennen die getesteten Quellen, ausführbaren Dateien und Testbedingungen.

Originale Quellcodeauszüge und aufgezeichnete Werkzeugausgaben bleiben unverändert. Die HTML-Dateien lassen sich offline lesen, innerhalb eines Bandes durchsuchen und ausdrucken; Code kann direkt kopiert werden. Beachten Sie die [GitHub-Einrichtung](GITHUB_SETUP.md) und die [Veröffentlichungsprüfungen](PUBLICATION_CHECKS.md).

| Datei | Inhalt |
| --- | --- |
| kitaqgb.html | C-Syntax, Compiler-Intrinsics und Builds mit KITAQGB |
| gb-library.html | KITAQGB-Bibliotheken |
| kokura.html | Ausführung, Eingaben, Beobachtung und Aufzeichnung mit KOKURA |
| kitaqfc.html | C-Syntax, Compiler-Intrinsics und Builds mit KITAQFC |
| fc-library.html | KITAQFC-Bibliotheken |
| kurosaki.html | Ausführen, Speichern und Analysieren mit KUROSAKI |
| sarakura.html | Diagnosen und erneute Tests mit SARAKURA |
| verification.html | Bildschirmaufnahmen der Beispiele |

Die Inhaltsseite und der Anfang des ersten Bandes erklären die doppelte Bedeutung des Namens und würdigen NORCAL. Buchstaben, Ziffern und Sonderzeichen stammen aus der mitgelieferten `samples/assets/ascii.c`. Die GB-Ressourcen sind in ASCII-Reihenfolge angeordnet; für FC werden sie in NES-Bitplanes umgewandelt. Die Zeichenformen bleiben erhalten.

Texte, ergänzte Beispiele und Erzeugungswerkzeuge stehen unter MIT. Am 12. September 2026 bestätigte der Autor, dass er die 92 gelieferten Glyphen selbst erstellt hat und sie unter MIT veröffentlichen darf. Auszüge aus der Originalsoftware behalten ihre Copyright-Vermerke. Geben Sie die [Drittanbieterhinweise](THIRD_PARTY_NOTICES.md) und die jeweils gültigen Lizenzen zusammen mit den Dateien weiter.

Die Sammlung enthält den [englischen Lizenztext](LICENSE) und eine [japanische Übersetzung zur Orientierung](LICENSE.ja). Die [Drittanbieterhinweise](THIRD_PARTY_NOTICES.md) verweisen außerdem auf japanische Lizenzfassungen der einzelnen Werkzeuge. Bei Abweichungen ist das englische Original maßgeblich. Für ausführbare Softwarepakete gelten zusätzlich die Lizenzen ihrer Abhängigkeiten. Die Erlaubnis zur Veröffentlichung dieser Handbücher bedeutet nicht, dass jedes Werkzeug und jede Abhängigkeit allein unter MIT weiterverteilt werden darf.

## Beispiele kompilieren

Klonen Sie die Repositorys als benachbarte Ordner und führen Sie die folgenden Befehle in deren gemeinsamem übergeordneten Ordner aus. Die Anordnung ist in [GITHUB_SETUP.md](GITHUB_SETUP.md) beschrieben. Verwenden Sie die bereitgestellten Compiler oder bauen Sie sie gemäß Handbuch neu; diese Ausgabe enthält Compilerkorrekturen.

```powershell
.\kitaq-docs\samples\build.ps1 -Only gb_hello,fc_hello
.\kitaq-docs\samples\build.ps1
```

Mit `-Root "absoluter Pfad zum Quellverzeichnis"` wählen Sie einen anderen Quellenstand. `-GbCompiler` und `-FcCompiler` geben abweichende Compilerpfade an. ROMs und Protokolle werden standardmäßig unter `samples/out/<sample-id>` abgelegt. Dieses Handbuchpaket enthält keine Compilerprogramme, kommerziellen ROMs oder BIOS-Dateien.

Die Fragmente in `samples/api-fragments` benötigen Initialisierung und gültige Argumente im umgebenden Programm. Der Sammelbuild erzeugt die ROMs der 47 Programme aus `samples/manifest.json`. Die Bände unterscheiden zwischen nur deklarierten APIs, nicht ausgeführten Fragmenten und Funktionen ohne Nachweis auf realer Hardware.

## Auf GitHub veröffentlichen

1. Legen Sie den Inhalt dieses Ordners im Repository-Stammverzeichnis oder in einem Ordner `docs` ab.
2. Laden Sie `index.html`, alle sieben Bände, `verification.html`, `loop-engineering.html`, `prompts`, die Sprachordner, `assets`, `samples`, `reference`, `verification`, die README-Dateien und Lizenzhinweise gemeinsam hoch. Nehmen Sie `.nojekyll` mit auf.
3. Wählen Sie unter GitHub **Settings → Pages → Build and deployment** als Quelle **Deploy from a branch**.
4. Wählen Sie den hochgeladenen Branch sowie `/ (root)` oder `/docs` und speichern Sie.
5. Öffnen Sie nach Abschluss der Veröffentlichung die unter Pages angezeigte Adresse und prüfen Sie Inhalts- und Bandverweise.

Siehe auch [GitHubs Anleitung zur Veröffentlichungsquelle](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site). `manual/_manual_work` ist ein lokales Build- und Prüfverzeichnis und wird nicht veröffentlicht.

## Bearbeiten und aktualisieren

Die japanischen Texte stehen in `tools/chapters.py`, die englischen in `tools/en/*.md`. Deutsche und weitere übersetzte Texte liegen unter `tools/i18n/`; sie werden mit `tools/generate_i18n.py` verarbeitet. Für die englische Erzeugung dient `tools/generate_en.py`, für API-Verzeichnisse und die japanischen Seiten `tools/generate.py`. Das Erscheinungsbild legt `assets/manual.css` fest. Zur Aktualisierung verwenden Sie Python:

```powershell
python -B kitaq-docs/tools/collect.py
python -B kitaq-docs/tools/make_samples.py
python -B kitaq-docs/tools/catalog.py
python -B kitaq-docs/tools/generate.py
python -B kitaq-docs/tools/generate_en.py
foreach ($language in @('ko','zh-CN','zh-TW','es','pt','fr','de')) {
    python -B kitaq-docs/tools/generate_i18n.py --language $language
    if ($LASTEXITCODE -ne 0) { throw "Manual generation failed: $language" }
}
python -B kitaq-docs/tools/check_site.py
python -B kitaq-docs/tools/check_bilingual.py
```

Die aufgenommenen Bilder stehen bei den Erläuterungen der Beispiele. Build- und Ausführungsprotokolle sowie lokale Prüfaufzeichnungen gehören nicht zu den veröffentlichten Dateien. Exportieren Sie das Handbuch vor dem Hochladen mit `tools/export_public.py` in ein separates Git-Arbeitsverzeichnis. Beachten Sie die [Drittanbieterhinweise](THIRD_PARTY_NOTICES.md).

## Umfang der veröffentlichten Quellen

KOKURA-GUI, KUROSAKI-GUI und PLITA sind von dieser Veröffentlichung ausgenommen. Die öffentlichen Quellen und Handbücher behandeln Kommandozeilenprogramme, Kerne und Integrations-APIs.
