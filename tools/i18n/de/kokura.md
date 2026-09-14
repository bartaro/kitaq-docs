## Fertige Windows-Version
Im Hauptverzeichnis des Repositorys liegt `kokura-cli.exe`. Laden Sie das Repository als ZIP herunter und bewahren Sie die Lizenzhinweise zusammen mit der ausführbaren Datei auf. Für diese Windows-x64-Version müssen weder Rust noch Python oder .NET installiert sein. Die folgenden Build-Schritte benötigen Sie nur, wenn Sie das Programm selbst aus den Quellen erstellen möchten. Der eigenständige Projektcode steht unter der MIT-Lizenz von DAISUKE OBA; die Lizenzbedingungen der Abhängigkeiten finden Sie in BINARY_NOTICES.md und licenses/.

## 1. Was KOKURA macht
KOKURA emuliert GB- und CGB-Software und zeichnet Bild, Ton, CPU-Ausführung, Speicher, Banken, Eingaben und Diagnoseereignisse auf. Die ausführbare Datei für die Kommandozeile heißt `kokura-cli.exe`.

## 2. Kompilieren und die erste ROM starten
{{CODE:0}}

Installieren Sie Rust und Cargo. Wenn Sie nur die Kommandozeilenversion benötigen, bauen Sie gezielt das angegebene Crate. Verwenden Sie zunächst die Hello-ROM aus Band 1. Standardmäßig wird ein Frame ausgeführt; mit `--run-frames` erreichen Sie die gewünschte Szene. Gemeint sind emulierte Frames, keine Sekunden Wartezeit.

## 3. DMG oder CGB auswählen
`--hardware auto` ist die Voreinstellung. Mit `dmg` oder `cgb` wählen Sie die Hardware ausdrücklich aus. Testen Sie ROMs, die beide Modi unterstützen, in beiden Einstellungen. Wenn eine reine CGB-ROM im DMG-Modus nicht startet, ist das allein noch kein Fehler des Emulators.

{{CODE:1}}

## 4. Eingaben vorgeben
`--input` hält eine Kombination gleichzeitig gedrückter Tasten. Mit `--input-seq` geben Sie dagegen einen zeitlichen Ablauf vor. Die Tastennamen lauten `A,B,START,SELECT,UP,DOWN,LEFT,RIGHT`; `NONE` steht für einen Abschnitt ohne gedrückte Tasten. Setzen Sie Folgen mit Semikolons in PowerShell in Anführungszeichen.

{{CODE:2}}

Planen Sie einen Abschnitt mit losgelassenen Tasten ein, wenn Sie neue Tastendrücke testen. A für 120 Frames gedrückt zu halten ist etwas anderes, als A 120-mal zu drücken. Beim Beispiel mit dem Eingabezähler sollte die obige Folge den Zähler einmal erhöhen.

## 5. Bilder, Video und Ton aufnehmen
`--png` speichert das letzte Bild. `--screenshot` zusammen mit `--screenshot-frames` nimmt ausgewählte Frames auf. `--record-video` zeichnet Video auf, `--record-wav` den Ton. Eine lautlose WAV-Datei ist bei einem Hello-Programm ohne APU-Nutzung zu erwarten.

{{CODE:3}}

Bereiche werden als `start:end` angegeben. Bewahren Sie den Bericht auf, damit Sie den fortlaufenden Frame-Zähler eines geladenen Zustands von den Positionen innerhalb des aktuellen Laufs unterscheiden können. Prüfen Sie Hörbarkeit, Tonhöhe, Unterbrechungen und Übersteuerung getrennt. Eine Emulatoraufnahme belegt keine Übereinstimmung jedes einzelnen Samples mit echter Hardware.

## 6. Zustand speichern und fortsetzen
{{CODE:4}}

Verwenden Sie normalerweise dieselbe ROM und dieselbe Emulatorversion. Ein Emulatorzustand ist etwas anderes als der Spielstand, den ein Spiel selbst speichert. Die KQS-Dateien der CLI und die JSON-Zustände der C-API haben unterschiedliche Formate. Durch Umbenennen der Dateiendung werden sie nicht austauschbar.

## 7. Symbole und Speicher beobachten
Begleitdateien mit den Endungen `.map`, `.source_map.txt`, `.dbg2.json` und `.build_report.json` können neben der ROM automatisch erkannt werden. Halten Sie eine ROM und ihre zugehörigen Begleitdateien zusammen. Dateien aus einem anderen Build können zu irreführenden Beobachtungen führen.

{{CODE:5}}

`wram` ist hier der Name des Beobachtungsfensters, 0xC000 seine Startadresse und 0x40 seine Länge. Kleine Fenster erleichtern es, veränderte Variablen zu erkennen. `--watch-baseline-mode` legt fest, ob mit den Anfangswerten, dem vorherigen Frame oder einer benannten Referenz verglichen wird.

## 8. Stoppbedingungen, Wiedergabe und Rückanalyse
`--breakpoint`, `--watchpoint`, `--run-until` und `--snapshot-at` halten bei bestimmten Bedingungen an oder speichern einen Zustand. Die jeweiligen Argumentformate unterscheiden sich. Nutzen Sie die Referenz und die unten wiedergegebene Hilfe.

{{CODE:6}}

Suchen Sie zunächst die erste Abweichung und untersuchen Sie anschließend ein kleineres Zeitfenster darum herum. `--decompile-out` erzeugt Pseudocode und Informationen zum Kontrollfluss, `--disassemble-out` zeigt CPU-Befehle. Eine Dekompilierung stellt weder den ursprünglichen C-Code noch die ursprünglichen Variablennamen vollständig wieder her.

## 9. Diagnosen an SARAKURA übergeben
{{CODE:7}}

KOKURAs `--emit-diagnostics` erwartet einen **JSONL-Dateinamen**, zum Beispiel `out/gb_events.jsonl`. Ein gewöhnlicher Laufbericht im JSON-Format und eine CPU-Trace-Datei im JSONL-Format sind keine gleichwertigen Eingaben für Diagnoseereignisse.

## 10. Kommunikationsaufträge
`pair` bildet zwei Geräte ab. `four_player_adapter` beschreibt eine logische Anordnung, in der der Host den Kommunikationspartner auswählt. `dmg07` bildet das Protokoll des physischen DMG-07 ab. Übergeben Sie einen Auftrag als JSON mit `--link-job` oder richten Sie Sitzungen mit `--link-topology` und `--link-session` ein.

{{CODE:8}}

Jede ROM muss die Kommunikation selbst implementieren. Zwei gewöhnliche Hello-Programme testen die Link-Bibliothek nicht. Halten Sie für jede Sitzung ROM, Steckplatz, Eingaben und Zustand fest und benennen Sie, welches Verhalten des realen Geräts noch nicht getestet wurde.

## 11. Einbindung in andere Anwendungen
Die veröffentlichte C-ABI liegt in `kokura-capi`. Für Python stehen die mitgelieferte Bridge und das Python-Crate bereit. Stellen Sie zuerst einen minimalen reproduzierbaren CLI-Aufruf her, bevor Sie ein Problem bei der Einbindung untersuchen.

## 12. Berichte sinnvoll lesen
Prüfen Sie zuerst die ausgeführten Frames und den Grund für das Anhalten. Danach folgen Bild, Eingabeergebnis, Ton, Fehler und Warnungen sowie das Profil. Ein lange beobachteter Titelbildschirm ohne Eingaben kann durchaus Warnungen über ein unverändertes Bild oder einen wiederholten Programmzähler auslösen. Beurteilen Sie solche Meldungen anhand der vorgesehenen Szene.
