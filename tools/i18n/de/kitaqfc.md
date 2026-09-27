## 1. KITAQFC und der GB-Compiler
KITAQFC nutzt das Frontend von KITAQGB, um Code für die 6502-CPU-Familie des NES/Famicom zu erzeugen. Es wandelt keine GB-ROM in eine NES-ROM um. Schreiben Sie Ihr Programm passend zu Grafik, Ton, Speicher und Mapper des Zielgeräts.

KITAQFC unterstützt Strukturkopien, gewöhnliche Funktionsaufrufe sowie for-, while- und do-while-Schleifen. Eine do-while-Schleife führt ihren Rumpf mindestens einmal aus und prüft danach die Bedingung. continue springt zu dieser abschließenden Prüfung; break verlässt die Schleife. Ein switch wählt eine case-Konstante im Bereich 0 bis 255 oder den default-Zweig, wenn kein case passt. Der Auswahlwert wird genau einmal ausgewertet. break verlässt die innerste Schleife oder das innerste switch; continue innerhalb eines switch setzt die umgebende Schleife mit ihrer nächsten Iteration fort.

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

<!-- common-language-kitaqfc:start -->
### Ergebnisse und Auswertung von Ausdrücken

Die Vergleichsoperatoren `==`, `!=`, `<`, `<=`, `>`, `>=` und die logischen Operatoren `!`, `&&`, `||` liefern 0 für falsch und 1 für wahr. Das Ergebnis lässt sich in einem `u16` speichern, als Argument übergeben, zurückgeben oder in Berechnungen verwenden. Beispielsweise ergibt `score = 500 + (lives != 0);` den Wert 501, wenn noch ein Leben vorhanden ist, andernfalls 500.

`&&` wertet den rechten Operanden nicht aus, wenn der linke null ist. `||` überspringt den rechten Operanden, wenn der linke ungleich null ist. Bei `pointer != 0 && pointer->active != 0` verhindert ein Nullpointer den Memberzugriff. Beide Bytes eines 16-Bit-Werts gehen in die Wahrheitsprüfung ein; 256 ist daher wahr. Die bitweisen Operatoren `&` und `|` haben keine Kurzschlussauswertung.

`++value` liefert den aktualisierten Wert, `value++` den ursprünglichen. Diese Operatoren sind auch auf Arrayelemente, dereferenzierte Pointer und Strukturmember anwendbar. `buffer[index()]++` ruft `index()` genau einmal auf. Bei `u16 *p` rückt `p++` um zwei Bytes zum nächsten Element vor; `(*p)++` erhöht dagegen den Wert am Ziel des Pointers.

`sizeof(array)` liefert die Größe des gesamten Arrays in Bytes; `sizeof(pointer)` ist 2. Für `u16 values[9];` ist `sizeof(values)` gleich 18. Das gilt auch für ROM-Arrays, lokale Arrays und Arraymember. `sizeof(function())` untersucht den Rückgabetyp, ohne die Funktion aufzurufen.

Deklaration und Definition einer Funktion müssen in Parametertypen und Reihenfolge übereinstimmen. Die Parameternamen dürfen verschieden sein; im Funktionsrumpf gelten die Namen der Definition. Beispielsweise kann `u8 next(u8 input);` als `u8 next(u8 value) { return (u8)(value + 1); }` definiert werden. Parameter und lokale Variablen verdecken gleichnamige globale Variablen.

Die Auswahl von Arrays oder Zeichenketten mit `?:` ergibt einen Pointer auf den gewählten Elementtyp. Dieser lässt sich direkt übergeben, etwa mit `show(ready ? "READY" : "WAIT");`. Bei den `u16`-Arrays `a` und `b` rückt `(ready ? a : b) + 1` um zwei Bytes zum zweiten Element des gewählten Arrays vor. Das Array wird dabei nicht kopiert.

`condition ? yes : no` wertet zuerst die Bedingung und danach nur den gewählten Zweig aus. Bedingung und Zweige dürfen Schiebeoperationen mit variabler Bitanzahl enthalten. Beispielsweise wählt `on = (pattern & (0x80 >> bit)) != 0 ? 4 : 2;` abhängig vom bezeichneten Bit vier oder zwei. Funktionsaufrufe in einem durch `&&` oder `||` übersprungenen rechten Operanden werden ebenfalls nicht ausgeführt. Ein `continue` in einer `for`-Schleife führt vor der erneuten Bedingungsprüfung den Aktualisierungsausdruck einmal aus; bei `while` und `do ... while` springt es zur Bedingung.

<!-- common-language-kitaqfc:end -->

## 5. Schleifen und Zustandssteuerung
{{CODE:4}}

Diese Fragmente zeigen eine Schleife mit mindestens einer Aktualisierung und eine Verzweigung, die den Handler des aktuellen Zustands auswählt. Definieren Sie update, condition, state und die Zustandshandler in Ihrem Programm. fc_control.c enthält ein vollständiges Schleifenbeispiel; das Frame- und Szenenbeispiel der Bibliothek zeigt ein vollständiges ROM zur Szenenverwaltung.

Registrieren Sie Szenen-, Entity- und System-Callbacks mit den in ihren Deklarationen geforderten Argument- und Rückgabetypen. Die Bibliotheken rufen die registrierten Handler bei den entsprechenden Aktualisierungs-, Zeichen- oder Frame-Warteoperationen auf. Beachten Sie die ROM-Bank- und Mapping-Vorgaben jeder API. Setzen Sie keine Unterstützung für Rekursion oder variadische Funktionen wie auf einem Desktop voraus.

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

Normale indizierte Lesezugriffe und C-Pointerreferenzen auf ROM-Arrays platzieren diese Arrays in der gemeinsamen Bank 0, sofern `#pragma fixed_bank` ihre Lage nicht ausdrücklich festlegt. Dadurch bleiben die Daten sichtbar, wenn der Aufrufer in einer umschaltbaren Bank läuft. Übergeben Sie für explizite Fernzugriffe im selben Aufruf den unveränderten Arraynamen und `__bankof` für genau diesen Namen, etwa `__farpeek8(__bankof(table), table)`. Eine Abfrage der Banknummer allein fordert keine Platzierung in der gemeinsamen Bank an. Bei ausdrücklich festgelegten Bankdaten und Referenzen innerhalb von Assemblercode müssen Sie das korrekte Mapping selbst sicherstellen. Diese Regel prüft die Platzierung anhand der Syntax; sie führt keine Pointerflussanalyse durch. Die Kapazitätsgrenze der gemeinsamen Bank gilt weiterhin.

## 9. FDS, Erweiterungssound und Zubehör
FDS umfasst Dateiplatzierung auf Diskette, Startvorgang, Overlays und Speichern. Lesen Sie `fds_manifest_sample.json` und die FDS-Header. Ein benötigtes BIOS müssen Sie in Ihrer eigenen Laufzeitumgebung bereitstellen; die öffentliche Distribution enthält keines.

Ein VRC6- oder VRC7-Soundaufruf ändert nicht die Mapper-Einstellung der ROM. Wählen Sie den zur Sounderweiterung passenden Mapper. Prüfen Sie bei Zubehör getrennt, ob Eingaben gelesen werden, die Verbindung besteht und der gewöhnliche Controllerpfad beeinflusst wird.

## 10. Diagnosen und Build-Ergebnisse
KQ-Diagnosen und Entwicklerbefehle wie `symfind`, `src2asm` und `romdiff` ähneln ihren GB-Gegenstücken. Einige geerbte GB-Hilfeoptionen stehen möglicherweise nicht für implementierte NES-Funktionen. Das FC-Verzeichnis wird deshalb getrennt aus FC-Quellen und Headern erstellt.

Warnungen wie KQ2421 für direkte PPU-Operationen können auch während der Initialisierung bei ausgeschalteter Anzeige auftreten. Ändern Sie eine sichere Initialisierung nicht allein, um eine Warnung zu beseitigen. Prüfen Sie den Darstellungszeitpunkt und die Ausführungsprotokolle. Keine Fehler und keine Warnungen sind unterschiedliche Ergebnisse.

## Quellpfade
Die Compilerquellen und die Projektdatei liegen im gleichnamigen Unterverzeichnis des Repositorys. Die ausführbare Datei liegt im Hauptverzeichnis, die Bibliotheken liegen in `lib/`. Die [Verzeichnisübersicht](../GITHUB_SETUP.md) nennt die Projektpfade und Build-Voraussetzungen.
