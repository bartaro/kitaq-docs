## 13. Befehlsbeispiele und genaue Argumentsyntax

Führen Sie diese PowerShell-Befehle im übergeordneten Verzeichnis der nebeneinanderliegenden Repositories aus. Erstellen Sie zuerst mit `New-Item -ItemType Directory -Force out` das Ausgabeverzeichnis. Ersetzen Sie `out/game.gb` durch Ihr eigenes ROM. Bei KOKURA stehen die Optionen hinter dem ROM-Pfad; der KUROSAKI-Unterbefehl `run` wird nicht verwendet. `--help` zeigt die Optionen der installierten Programmdatei.

### 13.1 Operation und Frame-Obergrenze wählen

| Argument | Zweck und Verhalten |
| --- | --- |
| `ROM` | ROM-Datei für einen normalen Lauf. Ein Auftrag oder eine Testmatrix kann stattdessen ein eigenes ROM angeben. |
| `--hardware auto`, `dmg`, `cgb` | Hardwareauswahl. Standard ist `auto`; testen Sie bei Spielen für beide Geräte ausdrücklich beide Modi. |
| `--run-frames 120` | Maximale Framezahl bei direkter Ausführung, standardmäßig 1. Stoppbedingungen können den Lauf früher beenden. Eingabesequenzen haben zusätzlich ihre eigenen Zeitspannen. |
| `--job out/test.json` | Führt einen JSON-Auftrag aus. Seine Frame-Obergrenze steht in `run.frames`; ROM, Zustand, Eingaben und Aufzeichnungseinstellungen stammen aus dem Auftrag. Relative Pfade darin beziehen sich auf die Auftragsdatei. |
| `--dump-report out/run.json` | Speichert den entstandenen JSON-Bericht. Ohne Ausgabepfad schreibt ein normaler Lauf den Bericht auf die Standardausgabe. |
| `--regression-matrix out/matrix.json` | Führt Aufträge mit erwarteten Beobachtungen aus. Prüfen Sie die einzelnen Ergebnisse im JSON: Eine erfolgreich ausgeführte Matrix bedeutet nicht, dass jeder Testfall bestanden wurde. |

Wählen Sie pro Aufruf eine Operation. Die Auswahl erfolgt in dieser Prioritätsreihenfolge: Dekompilierung, Disassemblierung, Regressionsmatrix, Verbindungsauftrag, direkt in der Befehlszeile definierte Verbindungssitzungen, normaler Lauf. Mehrere angegebene Modi werden nicht nacheinander ausgeführt.

{{COMMAND:0}}

Dieser Befehl führt höchstens 120 emulierte Frames aus und speichert das abschließende Bild sowie einen Bericht. Prüfen Sie darin die tatsächliche Framezahl und den Stoppgrund, bevor Sie das Bild bewerten.

### 13.2 Tasten halten oder eine zeitgesteuerte Eingabesequenz angeben

| Option | Syntax und Verwendung |
| --- | --- |
| `--input "A,RIGHT"` | Hält während eines direkten Laufs beide Tasten gedrückt. Groß- und Kleinschreibung ist bei den Namen unerheblich. `NONE` lässt alle Tasten los. |
| `--input-seq "NONE:30;A:1;NONE:89"` | Durch Semikolons getrennte Abschnitte im Format `BUTTONS:FRAMES`, die der Reihe nach ausgeführt werden. Hier: 30 Frames loslassen, A einen Frame drücken, danach 89 Frames loslassen. |
| `--input-script "NONE:30;A:1;NONE:89"` | Akzeptiert denselben Sequenztext, keinen Dateinamen. Sind beide Sequenzoptionen angegeben, hat `--input-script` Vorrang. |

Die Tastennamen lauten `RIGHT,LEFT,UP,DOWN,A,B,SELECT,START`. Die Hexadezimalmasken sind RIGHT=0x01, LEFT=0x02, UP=0x04, DOWN=0x08, A=0x10, B=0x20, SELECT=0x40 und START=0x80. Das sind KOKURAs Eingabemasken; verwenden Sie dafür keine NES-Controller-Masken. Setzen Sie in PowerShell die gesamte Sequenz in Anführungszeichen. Für Tests neuer Tastendrücke müssen auch Abschnitte mit losgelassenen Tasten enthalten sein. Die Sequenz sollte den gesamten vorgesehenen Beobachtungszeitraum abdecken.

{{COMMAND:1}}

Beim Tastenzähler-Beispiel sollte der Zähler dadurch einmal steigen. Ein einzelnes Standbild belegt nicht, ob die Wiederholung beim Halten einer Taste stimmt. Vergleichen Sie einen längeren Tastendruck mit mehreren getrennten Tastendrücken.

### 13.3 Bilder, Bewegung und Ton aufzeichnen

| Option | Syntax und Verwendung |
| --- | --- |
| `--png out/final.png` | Speichert das letzte Bild; hat bei gleichzeitiger Angabe Vorrang vor `--screenshot`. |
| `--screenshot out/frame.png` | Alternatives Ziel für Bildschirmaufnahmen. PNG und BMP werden unterstützt; ohne Dateiendung wird `.png` ergänzt. |
| `--screenshot-frames 30:32` | Speichert jeden gewählten Frame mit seiner Nummer im Dateinamen. Ein Ziel für die Bildschirmaufnahmen muss angegeben sein. |
| `--record-wav out/audio.wav` | Zeichnet Ton als WAV auf. Verwenden Sie ein ROM und einen Zeitraum, in dem tatsächlich Ton gespielt wird. |
| `--record-wav-frames 1:180` | Wählt den Aufnahmebereich einschließlich beider Grenzen. Die Werte sind Framenummern, keine Samplezahlen. |
| `--record-video out/motion.gif` | Zeichnet Bewegung als GIF oder Y4M auf. Ohne Dateiendung wird `.gif` ergänzt; MP4 ist kein unterstütztes Format. |
| `--record-video-frames 30:120` | Wählt den Videobereich einschließlich beider Grenzen. |
| `--audio-buffer-frames 8192` | Legt die Audiopufferkapazität in Stereo-Sampleframes fest, nicht in emulierten Videoframes oder einzelnen Links-/Rechts-Samples. |

Aufnahmebereiche werden dezimal angegeben und beginnen bei 1: `30` wählt einen Frame, `30:32` die Frames 30, 31 und 32. Null und umgekehrte Bereiche werden abgelehnt. Die Indizes beziehen sich auf den aktuellen Lauf. Bewahren Sie beim Fortsetzen eines älteren Zustands daher den Bericht auf. Erstellen Sie die übergeordneten Verzeichnisse vor der Aufnahme.

{{COMMAND:2}}

Bewerten Sie Scrollen und Animation anhand mehrerer Frames. Prüfen Sie den Ton anhand der WAV-Datei: Eine sichtbare Abschlussnummer belegt nicht, dass der vorgesehene Kanal gespielt hat.

### 13.4 Maschinenzustand speichern und fortsetzen

| Option | Zweck und Vorrang |
| --- | --- |
| `--save-state out/checkpoint.kqs` | Speichert den Maschinenzustand am Ende des Laufs. |
| `--snapshot out/checkpoint.kqs` | Gleiche Ausgabefunktion; hat Vorrang vor `--save-state`. |
| `--load-state out/checkpoint.kqs` | Lädt vor der Ausführung einen KQS-Zustand. |
| `--resume-state out/checkpoint.kqs` | Hat Vorrang vor `--load-state` und kann den Eingabezustand eines Auftrags überschreiben. |
| `--snapshot-at "frame=60&&frame_end=>out/frame60.kqs"` | Speichert, sobald eine Beobachtungsbedingung erfüllt ist. Für mehrere Anforderungen wiederholt angeben. Ohne `=>path` wird im aktuellen Verzeichnis aus dem ROM-Namen ein nummerierter Dateiname gebildet. |

Verwenden Sie einen Zustand, der zum ROM und zur Emulatorversion passt. KQS ist ein Maschinenzustand, weder das Speicher-RAM der Spielkassette noch die JSON-Serialisierung der C-API.

{{COMMAND:3}}

### 13.5 Benannte Speicherbereiche beobachten

| Option | Syntax und Verwendung |
| --- | --- |
| `--symbols out/game.map` | Lädt Symbole aus der passenden Compilerausgabe. |
| `--source-map out/game.source_map.txt` | Ordnet der Ausführung Quellcodestellen zu. |
| `--toolchain-metadata out/game.dbg2.json` | Lädt strukturierte Toolchain-Metadaten. Passende Begleitdateien können auch neben dem ROM automatisch erkannt werden. |
| `--watch-window "player:0xC700:16"` | Beobachtet 16 Bytes ab 0xC700 unter dem Namen player. Für weitere Bereiche wiederholt angeben. Diese Option beobachtet Speicher, hält die Ausführung aber nicht selbst an. |
| `--watch-baseline-mode initial` | Vergleicht mit den Anfangswerten. `previous-frame` vergleicht aufeinanderfolgende Frames; `named` wählt eine ausdrücklich aufgezeichnete Referenz. |
| `--watch-baseline-tag ready` | Wählt den Referenznamen bei einem Vergleich mit benannter Referenz. |
| `--capture-watch-baseline "ready=>frame=30&&frame_end"` | Zeichnet bei erfüllter Bedingung eine benannte Referenz auf. Für weitere Referenzen wiederholt angeben. |
| `--watch-fields preview,diff` | Wählt Gruppen von Beobachtungsfeldern: `hash`, `activity`, `preview`, `baseline`, `diff`, `insights` oder `all`. Die Vorschaubytes sind nur ein begrenzter Ausschnitt, kein unbegrenzter Speicherauszug. |
| `--report-sections cpu,watched_memory` | Behält die genannten Berichtsabschnitte bei. `meta` und `schema_version` bleiben stets enthalten. Unbekannte Namen erzeugen keine neuen Abschnitte. |
| `--report-minimal cpu,watched_memory` | Alternative Eingabe der Abschnittsliste mit Vorrang vor `--report-sections`. Erfordert durch Kommas getrennte Werte und ist kein boolescher Schalter. |

Adressen und Größen akzeptieren Dezimalzahlen oder Hexadezimalzahlen mit `0x`. Ermitteln Sie Variablenadressen anhand der Symbole des aktuellen Builds. 0xC700 ist unten nur eine Beispieladresse, kein festgelegter Speicherort für den Spieler.

{{COMMAND:4}}

### 13.6 Bei Ausführungsbedingungen oder Hardwareereignissen anhalten

| Option | Syntax und Zweck |
| --- | --- |
| `--breakpoint "pc:0x0150"` | Hält an einer CPU-Adresse an. `symbol:main` verwendet Symbole; mit angehängtem `@bank:2` wird die Bank eingeschränkt. |
| `--watchpoint "player@0xC700+4"` | Hält bei Schreibzugriffen auf einen vier Byte großen Speicherbereich an. Das optionale Präfix benennt den Watchpoint; ohne `+size` wird ein Byte überwacht. |
| `--stop-on-mmio "scroll@0xFF43"` | Hält bei einem Schreibzugriff auf das angegebene MMIO-Register an, hier SCX. |
| `--stop-on-irq "vblank:serviced"` | Wählt Interruptquelle und Phase: `requested`, `serviced`, `blocked` oder `any`. Eine allein angegebene Phase gilt für jede Quelle. |
| `--stop-on-dma oam_start` | Wählt ein DMA-Ereignis. Gültige Namen: `oam_start`, `oam_complete`, `hdma_start`, `hdma_block`, `hdma_complete`, `hdma_cancel`, `gdma_stall`, `hdma_deferred`, `hdma_ignored`. |
| `--run-until "frame=60&&frame_end"` | Hält an, wenn alle Terme einer Beobachtungsbedingung zutreffen. Für zusätzliche Anforderungen wiederholt angeben. |

Die Breakpoint-Markierungen `pc:`, `symbol:` und `@bank:` unterscheiden Groß- und Kleinschreibung. Speicheradressen und Banken werden dezimal oder hexadezimal mit `0x` angegeben. Behalten Sie eine Frame-Obergrenze bei, auch wenn Sie auf ein Ereignis warten, das möglicherweise nie eintritt.

Beobachtungsbedingungen verwenden `&&` für UND; es sind keine C-Ausdrücke. Unterstützt werden `frame=`, `ly=`, `pc=`, `bank=`, `bank_pc=bank:pc`, `symbol=`, `source=`, `event=`, `ppu_mode=` (oder `mode=`) und `basis=`. Frame- und LY-Werte sind dezimal. Symbol-, Quell- und Ereignisterme vergleichen Text. Zu den basis-Werten gehören `frame_start`, `frame_end`, `step`, `event`, `trace`, `snapshot`, `stop`; auch die alleinstehenden Terme `frame_start`, `frame_end`, `stop` und `vblank` sind zulässig. Vergleiche wie `hp<10` gehören nicht zu dieser Grammatik.

{{COMMAND:5}}

Untersuchen Sie mit dem ersten Befehl den Einsprungpunkt und mit dem zweiten den Code, der das horizontale Scrollen ändert. Prüfen Sie, ob der angeforderte Stopp tatsächlich eingetreten ist.

### 13.7 Beobachtungspunkte aufzeichnen und Läufe vergleichen

| Option | Zweck |
| --- | --- |
| `--trace-point "frame=30&&frame_end"` | Zeichnet bei erfüllter Bedingung eine Beobachtung auf. Für mehrere Punkte wiederholt angeben. |
| `--timeline-out out/timeline.jsonl` | Speichert den zeitlichen Verlauf der Beobachtungen. |
| `--trace-jsonl out/timeline.jsonl` | Alternatives Ziel für den zeitlichen Verlauf mit Vorrang vor `--timeline-out`. Fordert keine lückenlose Aufzeichnung aller ausgeführten Befehle an. |
| `--timeline-format jsonl` | Wählt `jsonl` (Standard) oder `csv`; die passende Dateiendung müssen Sie selbst angeben. |
| `--replay-interval 1` | Aktiviert Replay-Checkpoints und legt das Intervall in Frames fest. |
| `--replay-max-checkpoints 120` | Begrenzt die Anzahl aufbewahrter Checkpoints. Standardmäßig werden 16 bei einem Intervall von 1 gespeichert. |
| `--rewind-on-stop-frames 10` | Fordert nach einem Stopp ein Zurückspulen anhand des aufbewahrten Replay-Verlaufs an. |
| `--stop-on-divergence` | Aktiviert das Anhalten bei Abweichungen im Replay-Controller. |
| `--dump-replay-tape out/baseline.json` | Exportiert aufgezeichnete Replay-Daten. Zu ihrer Erzeugung muss die Replay-Aufzeichnung aktiviert sein. |
| `--compare-replay-tape out/baseline.json` | Vergleicht mit exportierten Replay-Daten. Verwenden Sie für einen deterministischen Vergleich dasselbe ROM, dieselben Eingaben und denselben Anfangszustand. |
| `--compare-replay-watch-only` | Beschränkt den Vergleich auf Beobachtungen überwachter Speicherbereiche; dies ist kein vollständiger Vergleich der Maschine. |
| `--snapshot-on-replay-mismatch out/mismatch` | Legt ein Präfix für Untersuchungsdateien fest, die bei einer festgestellten Abweichung erzeugt werden. |

{{COMMAND:6}}

Prüfen Sie das Vergleichsergebnis und die erste Abweichung im Bericht. Dass beide Dateien erzeugt wurden, bedeutet allein noch keinen bestandenen Vergleich.

### 13.8 Diagnosen und reproduzierbare Untersuchungen

| Option | Tatsächliches Verhalten |
| --- | --- |
| `--emit-diagnostics out/events.jsonl` | Exportiert Diagnoseereignisse für SARAKURA. |
| `--diagnostics-jsonl out/events.jsonl` | Alternatives Diagnoseziel für direkte Läufe; `--emit-diagnostics` hat Vorrang. |
| `--repro-bundle out/repro.zip` | Bündelt einen Bericht, Diagnoseereignisse und ein Manifest. ROM und Metadaten werden per Pfad referenziert, nicht eingebettet. Bildschirmaufnahmen, Zustände und Traces werden nicht automatisch aufgenommen. |
| `--break-on-diagnostic all` | Prüft Diagnosen im abschließenden Bericht, um Untersuchungsdateien aufzunehmen. Dies hält die CPU **nicht** an der ersten problematischen Instruktion an. Bei jedem nicht leeren Filter kann jede abschließende Diagnose den Aufnahmepfad auslösen. |
| `--png-on-diagnostic out/diagnostic-images` | Zielverzeichnis für das abschließende Diagnosebild bei aktivierter Diagnoseaufnahme. Die Datei heißt `diagnostic_000001.png`. |
| `--snapshot-on-diagnostic out/diagnostic-states` | Zielverzeichnis für `diagnostic_000001.kqs`. Diese Aufnahmen zeigen den aktuellen Endzustand, nicht den ursprünglichen Zeitpunkt jedes Ereignisses. |
| `--diagnostic-pack NAME` | Akzeptiertes Argument; der Ausführungspfad wendet kein Diagnosepaket an. |
| `--diagnostic-rule RULE` | Akzeptiertes, wiederholbares Argument; der Ausführungspfad wendet diese Regelauswahl nicht an. |
| `--diagnostic-summary-limit N` | Akzeptiertes Argument; der Ausführungspfad wendet diese Begrenzung der Zusammenfassung nicht an. |

{{COMMAND:7}}

Verwenden Sie für einen Stopp an einer bestimmten Instruktion oder einem Schreibzugriff die Debugger-Optionen aus 13.6. Bewerten Sie Diagnosen im jeweiligen Zusammenhang: Ein absichtlich untätiger Titelbildschirm kann Beobachtungen erzeugen, die keine Spielfehler darstellen.

### 13.9 Instruktionen disassemblieren oder Pseudocode untersuchen

| Option | Syntax und Zweck |
| --- | --- |
| `--disassemble-out out/code.txt` | Dekodiert ROM-Instruktionen, ohne den normalen Emulationslauf auszuführen. |
| `--disassemble-range "0:0100-0150"` | Wählt `BANK:START-END`; für weitere Bereiche wiederholt angeben. **Alle drei Zahlen sind hexadezimal**, auch ohne `0x`. |
| `--disassemble-format text` | `text` (Standard), `markdown` oder `json`. |
| `--decompile-out out/functions.json` | Erzeugt Pseudocode und Informationen zum Kontrollfluss. |
| `--decompile-format json` | `json` (Standard), `markdown` oder `text`. |
| `--decompile-function main` | Wählt eine Funktion; für weitere Funktionen wiederholt angeben. Passende Symbole verbessern die Identifizierung. |
| `--decompile-all` | Schließt alle dem Dekompilierer bekannten benannten Funktionen ein. |
| `--decompile-annotations out/annotations.json` | Liest Annotationen im JSON-Format des Dekompilierers. |
| `--decompile-trace out/trace.json` | Liest Trace-Metadaten des Dekompilierers; ein beliebiges JSONL-Diagnoseprotokoll ist kein Ersatz. |

{{COMMAND:8}}

Disassemblierung hilft beim Prüfen der erzeugten Instruktionen; Pseudocode erleichtert das Nachvollziehen des Kontrollflusses. Beides stellt das ursprüngliche C-Programm nicht exakt wieder her. Bewahren Sie Symbole und Metadaten desselben ROM-Builds auf.

### 13.10 Mehrere verbundene Maschinen ausführen

| Option | Syntax und Zweck |
| --- | --- |
| `--link-job out/pair.json` | Liest Topologie und Sitzungen aus einem JSON-Verbindungsauftrag. Relative Pfade beziehen sich auf dessen Verzeichnis. |
| `--link-topology pair` | Wählt für direkt angegebene Sitzungen `pair`, `four_player_adapter` oder `dmg07`. |
| `--link-session SPEC` | Fügt eine Sitzung hinzu. Mindestens zwei Sitzungen sind erforderlich. Setzen Sie in PowerShell die gesamte, durch senkrechte Striche getrennte Zeichenfolge in Anführungszeichen. |
| `--link-initial-peer-slot 1` | Wählt den anfänglichen Kommunikationspartner, wenn die Topologie eine Partnerauswahl verwendet. |

Zu den Sitzungsfeldern gehören `name`, `slot`, `rom`, `symbols`, `source_map`, `toolchain_metadata`, `load_state`, `save_state`, `input`, `input_sequence`, `audio_buffer_frames` und `watch_window`. `rom` ist erforderlich. Ein Beobachtungsfeld kann mehrere kommagetrennte Bereiche wie `a:0xC700:4,b:0xC710:4` enthalten. Verwenden Sie Programme, die tatsächlich serielle Daten austauschen. Zwei laufende Bildschirme allein belegen keine funktionierende Kommunikation.
