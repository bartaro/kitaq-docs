## 1. KITAQFC und der GB-Compiler
KITAQFC nutzt das Frontend von KITAQGB, um Code für die 6502-CPU-Familie des NES/Famicom zu erzeugen. Es wandelt keine GB-ROM in eine NES-ROM um. Schreiben Sie Ihr Programm passend zu Grafik, Ton, Speicher und Mapper des Zielgeräts.

In den aufgezeichneten Tests liefen Beispiele mit Strukturkopien und gewöhnlichen Funktionsaufrufen. **do-while und switch führten auf NES jedoch zu Fehlern wegen nicht unterstützter Codeerzeugung.** Dass der Parser ein Konstrukt erkennt, belegt noch nicht seine Verwendbarkeit auf diesem Ziel.

## 2. Voraussetzungen und Build
{{CODE:0}}

Installieren Sie das .NET Framework 4.8 Developer Pack und Visual Studio Build Tools und verwenden Sie Developer PowerShell. Die folgenden Befehle nutzen die ausführbare Datei im `kitaqfc`-Checkout. Passen Sie den Pfad an, wenn Sie einen anderen Build-Ort verwenden. CHR-Grafik und C-Quelltext sind getrennte Eingaben. Die `font.chr` des Handbuchs ist eine 8-KiB-Umwandlung der `ascii.c` des Autors.

## 3. Das erste Programm
{{CODE:1}}

{{CODE:2}}

Das Beispiel zeigt HELLO WORLD und 042. Seine Hilfsfunktion `m_wait` gibt die VRAM-Warteschlange zur Ausführung frei, wartet auf NMI und stellt das Scrolling wieder her. Zugriffe über PPUADDR verändern den internen Scrollzustand. Ohne dessen Wiederherstellung kann Text an einen Bildschirmrand verschoben erscheinen. Merken Sie sich die Reihenfolge: Anzeige aus, Ressourcen vorbereiten, Anzeige ein, mit NMI synchronisieren.

## 4. Einführung in die Sprache
Die Anweisungen und Ausdrücke des GB-Bands bilden einen gemeinsamen Ausgangspunkt. FC akzeptiert `unsigned char` und `unsigned short`; `core.h` definiert `u8`, `u16`, `s8` und `s16`. `fc.h` ist ein Sammelheader. Funktionen ohne Argumente dürfen hier `void main(void)` verwenden.

{{CODE:3}}

Halten Sie Ganzzahlen innerhalb ihrer 8- oder 16-Bit-Wertebereiche. Array-Indizes beginnen bei null. `fc_aggregate.c` zeigt Funktionen, Zeiger und Strukturen, `fc_arithmetic.c` die Arithmetik und `fc_control.c` Schleifen. CGB-Register und reine GB-Intrinsics gehören nicht in ein FC-Programm.

## 5. Nicht unterstützte Konstrukte umschreiben
{{CODE:4}}

Um do-while zu ersetzen, führen Sie den Schleifenkörper einmal vor der Prüfung der Abbruchbedingung aus. Eine einfache switch-Auswahl lässt sich als if/else-Kette schreiben. Dies sind erklärende Fragmente; `update` und die Zustandsfunktionen müssen Sie selbst bereitstellen. Ein vollständiges ROM-Beispiel ist `fc_control.c`.

Setzen Sie keine Desktop-übliche Unterstützung für Rekursion, indirekte Funktionsaufrufe oder variadische Funktionen voraus. Einige scene-/entity-Callback-APIs speichern derzeit Funktionszeiger, ohne sie indirekt aufzurufen.

## 6. Speicher und PPU
Der interne CPU-RAM des NES liegt bei 0x0000–0x07FF. Seine Spiegelungen oberhalb von 0x0800 sind kein zusätzlicher RAM. Der 6502-Stack belegt Seite 1; OAM-Schattenpuffer und Warteschlangen reservieren weitere Bereiche. `--nes-local-ram=START:LENGTH` und `--nes-temp-ram=START:LENGTH` sind fortgeschrittene Einstellungen, die eine Prüfung der Map erfordern.

Die PPU besitzt einen eigenen Adressraum. CHR liefert die Pixelmuster, Nametables platzieren Kacheln, Attributtabellen wählen Palettengruppen aus und Paletten enthalten Farbcodes. Hintergrundattribute gelten gewöhnlich für 16 × 16 Pixel große Bereiche. Sie verhalten sich deshalb anders als GB-Kachelattribute.

## 7. NMI und VRAM-Warteschlange
NMI ist der Interrupt an der Grenze eines Bildzyklus. Große direkte PPU-Schreibzugriffe während der Darstellung können das Bild stören. Initialisieren Sie direkt bei ausgeschalteter Darstellung. Für normale Aktualisierungen verwenden Sie `__vramq_put`, `__vramq_copy`, `__vramq_fill` und die Freigabe der Warteschlange.

{{CODE:5}}

Prüfen Sie freie Kapazität und Gültigkeitsdauer der Quelldaten. Der Standard-NMI verarbeitet die Warteschlange. Ein eigener `__nes_nmi` muss die nötige Warteschlangenausführung, OAM-Arbeit und Registersicherung beibehalten.

## 8. Mapper und ROM-Anordnung
| Auswahl | Typischer Einstieg |
| --- | --- |
| nrom | Kleine Übungen mit fester ROM-Belegung |
| uxrom / cnrom / axrom | Einfache PRG- oder CHR-Umschaltung |
| mmc1 / mmc3 / mmc5 | Größere Programme und Mapper-Funktionen |
| vrc6 / vrc7 / fme7 | Banking und zugehörige Erweiterungen |
| fds | Ausgabe eines Diskettenabbilds |

Dies sind Compiler-Auswahlmöglichkeiten, keine Tabelle vollständiger Hardware- oder Emulatorunterstützung. `--board=surom512` wählt eine bestimmte MMC1-Platinenanordnung. Eine Datei lediglich auf 512 KiB aufzufüllen stellt diese Anordnung nicht her. Nutzen Sie ergänzend KUROSAKIs Platinenprüfung.

{{CODE:6}}

Prüfen Sie die Platinenanforderungen für `--battery` / `--no-battery`, CHR-Kapazität, PRG-Belegung und bankübergreifende Aufrufe. Testen Sie nach Änderungen an Mapper oder Spiegelungsmodus auch Start, Scrolling und Datenumschaltung.

## 9. FDS, Erweiterungssound und Zubehör
FDS umfasst Dateiplatzierung auf Diskette, Startvorgang, Overlays und Speichern. Lesen Sie `fds_manifest_sample.json` und die FDS-Header. Ein benötigtes BIOS müssen Sie in Ihrer eigenen Laufzeitumgebung bereitstellen; die öffentliche Distribution enthält keines.

Ein VRC6- oder VRC7-Soundaufruf ändert nicht die Mapper-Einstellung der ROM. Wählen Sie den zur Sounderweiterung passenden Mapper. Prüfen Sie bei Zubehör getrennt, ob Eingaben gelesen werden, die Verbindung besteht und der gewöhnliche Controllerpfad beeinflusst wird.

## 10. Diagnosen und Build-Ergebnisse
KQ-Diagnosen und Entwicklerbefehle wie `symfind`, `src2asm` und `romdiff` ähneln ihren GB-Gegenstücken. Einige geerbte GB-Hilfeoptionen stehen möglicherweise nicht für implementierte NES-Funktionen. Das FC-Verzeichnis wird deshalb getrennt aus FC-Quellen und Headern erstellt.

Warnungen wie KQ2421 für direkte PPU-Operationen können auch während der Initialisierung bei ausgeschalteter Anzeige auftreten. Ändern Sie eine sichere Initialisierung nicht allein, um eine Warnung zu beseitigen. Prüfen Sie den Darstellungszeitpunkt und die Ausführungsprotokolle. Keine Fehler und keine Warnungen sind unterschiedliche Ergebnisse.

## Quellpfade
Die Compilerquellen und die Projektdatei liegen im gleichnamigen Unterverzeichnis des Repositorys. Die ausführbare Datei liegt im Hauptverzeichnis, die Bibliotheken liegen in `lib/`. Die [Verzeichnisübersicht](../GITHUB_SETUP.md) nennt die Projektpfade und Build-Voraussetzungen.
