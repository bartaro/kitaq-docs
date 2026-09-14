## Willkommen
KITAQGB entstand als **Fork von NORCAL**, dem NES-C-Compiler im Umfeld von Zachtronics. Auf dieser Grundlage wurde ein Compiler der C-Sprachfamilie für Game Boy und Game Boy Color entwickelt. Codeerzeugung, Speicherverwaltung, Grafik, Ton und ROM-Banking wurden an diese Geräte angepasst. Wir würdigen das ursprüngliche Projekt und seinen Autor Keith Holman.

{{ORIGIN}}

NORCAL wurde im Zusammenhang mit der NES-Version von HACK*MATCH entwickelt. Hintergrundinformationen des Autors finden Sie unter [NORCAL: A C Compiler for the NES](https://keithholman.net/nes-compiler.html) und [HACK*MATCH for the NES](https://trashworldnews.com/hack-match/). Projektgeschichte und Namenserklärung folgen der vom Autor bereitgestellten README.

## So verwenden Sie die Handbücher
Wie ein frühes Computerhandbuch beginnt diese Sammlung mit kurzen Programmen, die Sie abtippen, kompilieren und ausführen können. Lernen Sie die Technik anhand sichtbarer Ergebnisse kennen; Sie müssen nicht zuerst jeden Begriff auswendig lernen.

1. Beginnen Sie mit dem ersten Programm in Band 1 für GB oder Band 4 für FC.
2. Ergänzen Sie Eingaben, Grafik und Ton mithilfe von Band 2 oder Band 5.
3. Beobachten Sie den Ablauf mit KOKURA oder KUROSAKI und ordnen Sie die Diagnosen mit SARAKURA ein.
4. Suchen Sie im jeweiligen Band oder im API-Verzeichnis, wenn Sie bereits einen Funktionsnamen kennen.

Sprachsyntax, Compiler-Intrinsics, Bibliotheksfunktionen und Kommandozeilenoperationen sind verschiedene Arten von Referenzeinträgen. Die Compiler-Bände enthalten außerdem Verzeichnisse der CPU-Befehle. Ähnliche Namen auf GB und FC garantieren weder gleiche Argumente noch gleiches Verhalten.

## Die sieben Bände
| Band | Eingabe | Ausgabe oder Aufgabe |
| --- | --- | --- |
| KITAQGB | C-Quellen und Ressourcen | GB/CGB-ROMs, Maps und Build-Informationen |
| KITAQGB-Bibliothek | Aufrufe aus dem Spielcode | Grafik, Ton, Eingaben, Kommunikation und Spielfunktionen |
| KOKURA | GB/CGB-ROMs | Ausführung, Bild, Ton, Zustände und Beobachtungen |
| KITAQFC | C-Quellen und CHR-Ressourcen | NES/FDS-Ausgaben und Build-Informationen |
| KITAQFC-Bibliothek | Aufrufe aus dem Spielcode | NES-Grafik, Ton und Geräteschnittstellen |
| KUROSAKI | NES/FDS-Abbilder | Ausführung, Aufzeichnung und Analyse |
| SARAKURA | Build-Informationen und Diagnoseereignisse | Berichte sowie Korrektur- und Testpläne |

## Die mitgelieferte Schrift
Die 26 Großbuchstaben, 10 Ziffern, 26 Kleinbuchstaben und 30 Sonderzeichen stammen aus der [ascii.c des Autors](samples/assets/ascii.c). Es wurden keine weiteren Zeichenformen erfunden. Die ursprünglichen 92 Glyphen sind erhalten; siehe [Zuordnung der Umwandlung](verification/font_conversion.json) und [Kachelübersicht](verification/font_source_atlas.png). Das Leerzeichen verwendet eine leere Kachel. Rückstrich und senkrechter Strich fehlen in der gelieferten Schrift und erscheinen als Leerstellen. `gb_font.c` und `fc_font.c` zeigen alle gelieferten Glyphen.

## Ausgabe und Prüfstand
Dieses Handbuch beschreibt den **Quellenstand vom 14. September 2026**. Das Referenzinventar enthält die Prüfsummen der Quellen und ausführbaren Dateien. Eingaben, Bedingungen und Umfang der einzelnen Tests entnehmen Sie den Prüfprotokollen.

Ein erfolgreicher Build bedeutet, dass eine ROM erzeugt wurde. Ein Ausführungstest bedeutet, dass ein Emulator die angegebene Zahl von Frames durchlaufen hat. Pixelvergleiche, Eingabeverhalten und Tonprüfungen werden getrennt dokumentiert. Daraus folgt keine Garantie für jedes Zubehör oder jede reale Konsole; Warnungen bleiben in den Protokollen sichtbar.

Die aktuelle öffentliche Quellausgabe enthält weder KOKURA-GUI-Oberflächen noch KUROSAKI-GUI oder PLITA. Verfügbar sind die veröffentlichten Kerne, Kommandozeilenprogramme und Integrationsschnittstellen.

## Ein Arbeitsverzeichnis vorbereiten
Die Beispiele verwenden **Windows PowerShell**. Speichern Sie C-Dateien als UTF-8-Text. Das aktuelle Verzeichnis ist der Ordner, in dem Sie einen Befehl ausführen. Setzen Sie Pfade mit Leerzeichen in Anführungszeichen und starten Sie Programme bei Bedarf mit `& "Pfad"`. Klonen Sie die Repositorys als benachbarte Ordner gemäß der [GitHub-Einrichtung](../GITHUB_SETUP.md). Projektübergreifende Befehle führen Sie im gemeinsamen übergeordneten Ordner aus.

{{CODE:0}}

Ersetzen Sie `game.c`, `game.gb` und `game.nes` durch Ihre Dateinamen. Angaben wie `<ROM>` sind Platzhalter; die spitzen Klammern werden nicht mit eingegeben. Befehle stehen meist in einer Zeile. Der Rückstrich zur Zeilenfortsetzung in Bash ist keine PowerShell-Syntax.

## Compiler-Korrekturen dieser Ausgabe
Beim Bauen der Beispiele wurden eine interne Kollision lokaler Labels in KITAQGB sowie KITAQFC-Probleme beim Erhalten von Zwischen- und Rückgabewerten über Funktionsaufrufe hinweg gefunden. Die dokumentierten Handbuchtests nutzten die korrigierten Compiler, auch für den GB-Objektpool und die FC-Beispiele mit Funktionen und Strukturen. Diese Korrekturen belegen nicht die Unterstützung sämtlicher C-Konstrukte. Beachten Sie die [Prüfaufzeichnungen der Beispiele](verification.html).

## HTML lesen, drucken und veröffentlichen
Öffnen Sie die heruntergeladene `index.html`, um offline zu lesen. Gestaltung, Suche, Beispiele und Prüfbilder verwenden lokale Dateien; ein externes CDN ist nicht erforderlich. Bewahren Sie das gesamte Verzeichnis zusammen auf. Die Druckfunktion erzeugt eine Ansicht ohne Navigationsspalte.

Das Repository `kitaq-docs` enthält die Handbuch-Website. Im GitHub-Dateibrowser wird normalerweise der HTML-Quelltext angezeigt; GitHub Pages stellt die gerenderte Website bereit. Hinweise zur Veröffentlichung und zum Auschecken stehen in der README. Die deutsche Ausgabe enthält dieselben sieben Bände, API-Einträge, Beispielprogramme und Prüfverweise wie die japanische und englische Fassung. Quellauszüge und aufgezeichnete Werkzeugausgaben bleiben im Original, damit sie sich genau mit den Quellen und tatsächlichen Antworten vergleichen lassen.
