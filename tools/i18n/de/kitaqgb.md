## 1. KITAQGB kennenlernen
KITAQGB ist ein Compiler der C-Sprachfamilie für GB/CGB, der aus Zachtronics’ NORCAL hervorgegangen ist.

{{ORIGIN}}

Er liest C-Dateien, erzeugt CPU-Befehle und verpackt sie in eine ROM. Sprache, Bibliotheken und Aufrufkonventionen unterscheiden sich von einem C-Compiler für Desktop-Computer.

Der GB besitzt eine 8-Bit-CPU und wenig Speicher. Die Bildschirmgrafik besteht überwiegend aus Kacheln mit 8 × 8 Pixeln. Sprites sind kleine Bilder, die sich unabhängig positionieren lassen. Auch Text benötigt Kachelgrafik; eine allgemeine eingebaute Textausgabe wird nicht vorausgesetzt. Die Beispiele verwenden die Glyphen aus der `ascii.c` des Autors, für GB nach ASCII-Codes angeordnet, ohne ihre Bits zu verändern. Die FC-Ausgabe überträgt dieselben Formen in das NES-CHR-Layout.

## 2. Voraussetzungen und Compiler-Build
Installieren Sie eine Visual-Studio-/MSBuild-Umgebung für .NET Framework 4.8. Verwenden Sie Developer PowerShell, in der `MSBuild.exe` verfügbar ist.

{{CODE:0}}

Bewahren Sie die ausführbare Datei zusammen mit ihren Konfigurationsdateien auf. Geben Sie in Build-Befehlen den Compilerpfad ausdrücklich an. Beim Bauen des Projekts wird die ausführbare Datei in das Hauptverzeichnis des Repositorys `kitaqgb` kopiert.

## 3. Das erste Programm
Die mitgelieferte `samples/gb_hello.c` nutzt Bildschirm- und Texthilfen aus `gb_common.h`. Bewahren Sie diesen Header zusammen mit den Schriftdateien auf. `#include` liest Deklarationen oder Definitionen aus einer anderen Datei ein.

{{CODE:1}}

{{CODE:2}}

Auf dem Bildschirm sollen HELLO WORLD und 042 erscheinen. Namen mit `m_` sind Lernhilfen aus dem gemeinsamen Beispielheader, keine Standardbefehle von KITAQGB. Zu den Compiler-Intrinsics gehören dagegen etwa `__wait_vblank` und `__vram_copy`.

## 4. Grundsyntax und Typen
Anweisungen enden mit `;`, Anweisungsblöcke stehen in `{ }`. `//` beginnt einen Zeilenkommentar, `/* ... */` einen Blockkommentar. Groß- und Kleinschreibung werden unterschieden. Verwenden Sie `void main()` als Einstiegspunkt. **In dieser GB-Version führt `void main(void)` zu einem Syntaxfehler.** Übernehmen Sie deshalb die FC-Deklaration nicht unverändert.

| Typ | Bedeutung und Wertebereich |
| --- | --- |
| `u8` | Vorzeichenlose 8-Bit-Ganzzahl, 0 bis 255 |
| `s8` | Vorzeichenbehaftete 8-Bit-Ganzzahl, −128 bis 127 |
| `u16` | Vorzeichenlose 16-Bit-Ganzzahl, 0 bis 65535 |
| `s16` | Vorzeichenbehaftete 16-Bit-Ganzzahl, −32768 bis 32767 |
| `void` | Kein Rückgabewert |
| `T*` | Zeiger auf Daten des Typs T |

Beginnen Sie mit diesen kurzen Typnamen. Setzen Sie die Desktop-Bedeutung von `int`, `long`, `float`, `double` oder Standardheadern nicht voraus. Diese Version behandelt `char` als vorzeichenlose 8-Bit-Daten. Verwenden Sie ausdrücklich `s8` oder `s16`, wenn Sie vorzeichenbehaftete Arithmetik benötigen.

{{CODE:3}}

`(u16)` ist eine Typumwandlung. Wenn ein kleiner Wert bereits übergelaufen ist, stellt die Zuweisung an eine größere Variable die verlorenen Bits nicht wieder her. Erweitern Sie die Operanden vor der Rechnung. Für Bewegungen mit Bruchteilen verwenden Sie die Festkommabibliothek.

## 5. Ausdrücke und Operatoren
| Gruppe | Operatoren | Beispiel oder Bedeutung |
| --- | --- | --- |
| Arithmetik | `+ - * / %` | `n / 10` liefert den ganzzahligen Quotienten, `n % 10` den Rest |
| Vergleich | `== != < <= > >=` | `lives == 0` prüft auf Gleichheit |
| Logik | `! &&` / `||` | Verneinung, beide Bedingungen, mindestens eine Bedingung |
| Bits | `&` / `|` / `^ ~ << >>` | Tastenmasken und andere Bitmengen |
| Zuweisung | `= += -=` und verwandte Formen | `x += 1` verändert einen Wert |
| Inkrement | `++ --` | `i++` erhöht um eins |
| Auswahl | `condition ? A : B` | Je nach Bedingung einen Wert auswählen |
| Zeiger | `&variable` / `*p` | Adresse ermitteln oder auf das Ziel zugreifen |

Unterscheiden Sie `=` und `==`. Klammern machen komplexe Ausdrücke verständlicher. Packen Sie nicht zu viele Aufrufe und Nebenwirkungen in eine Anweisung. Vermeiden Sie Division durch null und Array-Zugriffe außerhalb der Grenzen. `sizeof` liefert eine Größe in Bytes, `offsetof` den Versatz eines Strukturmitglieds.

## 6. Verzweigungen und Schleifen
{{CODE:4}}

`break` verlässt eine Schleife oder switch-Anweisung, `continue` beginnt den nächsten Schleifendurchlauf und `return` verlässt eine Funktion. Wenn ein switch-Zweig ausdrücklich im folgenden Zweig fortgesetzt werden soll, schreiben Sie `fallthrough;`. Unbeabsichtigtes Weiterlaufen wird diagnostiziert. Das vollständige Beispiel finden Sie in `gb_control.c`.

## 7. Funktionen, Arrays und Strukturen
{{CODE:5}}

Array-Indizes beginnen bei null. Ein Array mit vier Elementen hat die Indizes 0 bis 3. `player.x` wählt ein Mitglied aus, `pointer->x` greift über einen Zeiger darauf zu. Strukturen, Unions und Enums werden eingelesen; ihre Speicheranordnung hängt jedoch von den Typen und den Attributen `__packed` / `__aligned` ab. Prüfen Sie `sizeof`, bevor Sie Daten mit Hardware oder binären Formaten austauschen.

Die voreingestellte Legacy-ABI legt Argumente und lokale Variablen an festen Stellen ab. Gehen Sie daher nicht von Desktop-üblicher Rekursion oder Wiedereintrittsfähigkeit bei Interrupts aus. `__stackcall` und `--abi=stack` sind fortgeschrittene Optionen für Aufrufkonventionen. Prüfen Sie bei gemischten Konventionen die ABI-Berichte und die tatsächliche Ausführung.

## 8. Mehrere Dateien und Präprozessor
Schreiben Sie Typen, Konstanten und Deklarationen in Header, Funktionskörper in `.c`-Dateien. `#pragma once` oder Include-Guards verhindern mehrfaches Einlesen. Für bedingte Kompilierung stehen `#define`, `#undef`, `#if`, `#ifdef`, `#ifndef`, `#elif`, `#else` und `#endif` bereit.

{{CODE:6}}

`-I` ergänzt ein Suchverzeichnis für Header. Ein Bibliotheksheader bindet die Implementierung nicht automatisch ein. Nennen Sie die nötigen `.c`-Dateien im Build-Befehl. Wählen Sie die benötigten Einheiten gezielt aus, damit Registerdefinitionen oder Interrupt-Handler nicht doppelt vorkommen.

## 9. ROM, Speicher und Banken
ROM enthält Code und Konstanten, WRAM die Variablen, VRAM die Grafik und OAM die Sprite-Beschreibungen. Banking legt fest, welcher physische Speicher an einer CPU-Adresse sichtbar ist. Ein 16-Bit-Zeiger allein bezeichnet Daten in einer anderen Bank nicht eindeutig.

{{CODE:7}}

`__prg_rom` legt Daten in ROM ab. Attribute wie `__location(0xFF40)` wählen eine feste Adresse, `__wram` / `__hram` einen Speicherbereich. Prüfen Sie bei `#pragma bank` und `#pragma fixed_bank` die Map. Von Interrupts benötigter Code und benötigte Daten müssen erreichbar bleiben.

{{CODE:8}}

`--cgb=dmg` kennzeichnet DMG-Software, `--cgb=cgb` Software für beide Modi und `--cgb=cgb_only` reine CGB-Software. Programme für beide Modi müssen die Hardware erkennen, bevor sie CGB-Funktionen verwenden. Ein Header-Flag implementiert diese Unterscheidung nicht im Spielcode.

## 10. Grafik sicher aktualisieren
VBlank ist die Pause zwischen den dargestellten Frames. Unpassend getaktete VRAM- und OAM-Schreibzugriffe können Daten verfälschen oder verloren gehen. Laden Sie anfängliche Ressourcen bei ausgeschaltetem Display. Verwenden Sie für laufende Aktualisierungen sichere Intrinsics oder die VRAM-Warteschlange. Bei Funktionen mit `_unsafe` oder `_fast` muss der Aufrufer selbst ein zulässiges Übertragungsfenster gewährleisten.

Richten Sie den OAM-DMA-Puffer an einer 256-Byte-Grenze aus. Auf GB erhält `__oam_dma` die Quelladresse. Das gleichnamige FC-Intrinsic hat dagegen kein Argument.

## 11. Build-Befehle und Ausgaben
`-o` wählt die Ausgabedatei, `-O0` / `-O1` die Optimierung und `--profile=dev|release|test` eine Gruppe von Einstellungen. `--no-disasm` unterdrückt die Disassemblierung. `--debug-out=...` und `--trace-out=...` legen Analyseausgaben fest. Wählen Sie den Umfang passend zu einem schnellen Build oder einer ausführlichen Untersuchung.

{{CODE:9}}

`.map` hält Namen und Speicherbelegung fest, `.funcsizes.txt` die Funktionsgrößen. `.dbg2.json` / `.source_map.txt` verknüpfen Ausführungspositionen mit Quellen, `.build_report.json` fasst den Build zusammen. Eine ausdrücklich mit `--emit-ai-metadata` erzeugte JSON-Datei erleichtert die Übergabe an SARAKURA.

## 12. Fehler von Anfang an lesen
Beginnen Sie beim ersten Fehler mit Dateiname, Zeile und KQ-Diagnosenummer. Spätere Meldungen können Folge des ersten Syntaxfehlers sein. Prüfen Sie bei unbekannten Symbolen Deklaration, Implementierung und Einbindung in den Build. Bei ROM-Überlauf helfen Ressourcen- und Funktionsgrößen sowie die Bankbelegung.

{{CODE:10}}

## 13. Inline-Assembler
`__asm { ... }` akzeptiert die Befehlsnamen von KITAQGB. Quelltext für andere GB-Assembler wird nicht beliebig übernommen. Zu den internen Schreibweisen gehört beispielsweise `LD_A_IMM`. Klären Sie Argumente, Rückgabewerte, zu erhaltende Register und Stack-Verhalten, bevor Sie Inline-Assembler einsetzen. Der Anhang listet Befehlsnamen und Operandenformen auf.

{{CODE:11}}

## Quellpfade
Die Compilerquellen und die Projektdatei liegen im gleichnamigen Unterverzeichnis des Repositorys. Die ausführbare Datei liegt im Hauptverzeichnis, die Bibliotheken liegen in `lib/`. Die [Verzeichnisübersicht](../GITHUB_SETUP.md) nennt die Projektpfade und Build-Voraussetzungen.
