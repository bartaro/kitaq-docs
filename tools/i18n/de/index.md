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
Die Beispiele verwenden die vom Autor gezeichnete Schrift [ascii.c](samples/assets/ascii.c): 26 Großbuchstaben, 10 Ziffern, 26 Kleinbuchstaben und 30 Sonderzeichen, insgesamt 92 Glyphen. Die [Kachelübersicht](verification/font_source_atlas.png) zeigt alle Zeichen. Das Leerzeichen verwendet eine leere Kachel. Rückstrich und senkrechter Strich fehlen in dieser Schrift und erscheinen ebenfalls als Leerstellen. `gb_font.c` und `fc_font.c` zeigen sämtliche Glyphen.

## Ausgabe und Prüfstand
Dieses Handbuch beschreibt den **Quellenstand vom 14. September 2026**. Das Referenzinventar enthält die Prüfsummen der Quellen und ausführbaren Dateien. Eingaben, Bedingungen und Umfang der einzelnen Tests entnehmen Sie den Prüfprotokollen.

Ein erfolgreicher Build bedeutet, dass eine ROM erzeugt wurde. Ein Ausführungstest bedeutet, dass ein Emulator die angegebene Zahl von Frames durchlaufen hat. Pixelvergleiche, Eingabeverhalten und Tonprüfungen werden getrennt dokumentiert. Daraus folgt keine Garantie für jedes Zubehör oder jede reale Konsole; Warnungen bleiben in den Protokollen sichtbar.

## Ein Arbeitsverzeichnis vorbereiten
Die Beispiele verwenden **Windows PowerShell**. Speichern Sie C-Dateien als UTF-8-Text. Das aktuelle Verzeichnis ist der Ordner, in dem Sie einen Befehl ausführen. Setzen Sie Pfade mit Leerzeichen in Anführungszeichen und starten Sie Programme bei Bedarf mit `& "Pfad"`. Für Beispiele mit mehreren Werkzeugen liegen deren Repositorys und das Spielprojekt im selben übergeordneten Ordner; führen Sie die Befehle dort aus.

{{CODE:0}}

Ersetzen Sie `game.c`, `game.gb` und `game.nes` durch Ihre Dateinamen. Angaben wie `<ROM>` sind Platzhalter; die spitzen Klammern werden nicht mit eingegeben. Befehle stehen meist in einer Zeile. Der Rückstrich zur Zeilenfortsetzung in Bash ist keine PowerShell-Syntax.

## HTML-Handbücher lesen und drucken
Öffnen Sie die heruntergeladene `index.html`, um offline zu lesen. Gestaltung, Suche, Beispiele und Prüfbilder verwenden lokale Dateien; ein externes CDN ist nicht erforderlich. Bewahren Sie das gesamte Verzeichnis zusammen auf. Die Druckfunktion erzeugt eine Ansicht ohne Navigationsspalte.

Quellauszüge und tatsächliche Werkzeugausgaben bleiben im Original, damit Sie sie unmittelbar mit Dateien und Befehlsergebnissen vergleichen können.
