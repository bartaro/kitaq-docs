## Fertige Windows-Version
Im Hauptverzeichnis des Repositorys liegt `kurosaki.exe`. Laden Sie das Repository als ZIP herunter und bewahren Sie die Lizenzhinweise zusammen mit der ausführbaren Datei auf. Für diese Windows-x64-Version müssen weder Rust noch Python oder .NET installiert sein. Die folgenden Build-Schritte dienen dem Neubau aus den Quellen. Der eigenständige Projektcode steht unter der MIT-Lizenz von DAISUKE OBA; die Bedingungen der Abhängigkeiten bleiben in BINARY_NOTICES.md und licenses/ erhalten.

## 1. Was KUROSAKI macht
KUROSAKI ist ein Beobachtungsemulator für NES, Famicom und FDS, der Informationen von KITAQFC einlesen kann. Seine CLI untersucht ROMs, führt Programme aus, zeichnet Ton auf, diagnostiziert Verhalten, speichert Snapshots, spielt Eingabefolgen ab und erzeugt Disassemblierungen sowie mögliche Funktionsrekonstruktionen. Der Umfang der Mapper-Implementierungen ist unterschiedlich. Prüfen Sie deshalb zunächst die ROM und die Angaben zur Unterstützung.

## 2. Kompilieren und starten
{{CODE:0}}

Die kurzen Befehle mit `kurosaki` setzen voraus, dass das Programmverzeichnis im PATH steht. Andernfalls ersetzen Sie den Befehlsnamen durch `& "vollständiger Pfad zur ausführbaren Datei"`.

{{CODE:1}}

Prüfen Sie die Textdarstellung mit der Hello-ROM aus Band 4. `inspect-rom` untersucht den Header, während `run` die CPU- und PPU-Ausführung vorantreibt. Eine erfolgreiche Headerprüfung garantiert noch keinen erfolgreichen Programmlauf.

## 3. Mapper und Platine prüfen
`mapper-list` listet die registrierten Mapper-Typen auf. `mapper-info` beschreibt einen Typ, `audit-board` prüft die Anforderungen der Platine. Die Mapper-Nummer verbindet den ROM-Header mit Annahmen über die tatsächliche Beschaltung. Aus einem Namen allein lassen sich Speicherkapazität, CHR-RAM und das Verhalten fester Banken nicht ableiten.

{{CODE:2}}

`--allow-unimplemented` lässt die Beobachtung trotz nicht implementierter Elemente weiterlaufen. Ein solcher Lauf belegt nicht, dass diese Elemente unterstützt werden.

## 4. Controller-Eingaben
`run --pad1` und `--pad2` verwenden rohe NES-Tastenmasken: A=1, B=2, SELECT=4, START=8, UP=16, DOWN=32, LEFT=64 und RIGHT=128. Für gleichzeitig gedrückte Tasten addieren Sie die Werte.

{{CODE:3}}

Dieses Beispiel hält A für 120 Frames gedrückt. Für Abläufe wie Titelbildschirm, Start und Bestätigung verwenden Sie eine Eingabewiedergabe. Das CLI-Beispiel mit `replay-record` zeichnet einen Referenzlauf ohne interaktive Eingaben auf. Es nimmt nicht die Bedienung einer grafischen Oberfläche durch eine Person auf.

## 5. Snapshots und Eingabewiedergabe
{{CODE:4}}

Fortsetzbare Zustände verwenden Snapshots der Version 2. Der SHA-256-Wert der ROM muss zum Zustand passen. `snapshot-resume` setzt einen gespeicherten Zustand fort. `snapshot-rebase` überträgt ihn ausdrücklich auf eine andere kompatible ROM, sofern ein entsprechender Kompatibilitätsvertrag vorliegt. Alte Zustände nach Änderungen am Code oder an der RAM-Belegung ungeprüft weiterzuverwenden ist keine verlässliche Methode. Wiederholen Sie normalerweise dieselben Aktionen ab dem Programmstart.

## 6. Traces, Diagnosen und Profile
{{CODE:5}}

Ein Trace zeigt den zeitlichen Ablauf. Diagnosen kennzeichnen Beobachtungen, auf die eine Regel zutrifft. Ein Profil zeigt, wo sich die Ausführung konzentriert. Einige Frames rund um eine Auffälligkeit lassen sich meist leichter untersuchen als ein sehr langer vollständiger Trace.

Übergeben Sie die passenden Build-Debug-Daten im JSON-Format mit `--kitaqfc-debug`. Eine Beobachtung ohne Quellzeileninformationen ist kein vollständiger Trace auf Quellzeilenebene.

## 7. Ton und Bilder speichern
{{CODE:6}}

Registeränderungen, erzeugte PCM-Daten und korrekt klingender Ton erfordern jeweils eigene Prüfungen. Halten Sie beim Testen der eingebauten oder zusätzlichen Soundhardware auch den Mapper fest. Ein einzelnes PNG belegt weder Bewegung noch Eingabeverhalten. Bewahren Sie dazu ebenfalls die Zustände und Eingaben davor und danach auf.

## 8. Disassemblieren und dekompilieren
{{CODE:7}}

`disasm` gibt Befehlsfolgen aus. `decompile` liefert mögliche Funktionsgrenzen, Kontrollflussgraphen, Referenzen und Pseudocode. Bei umschaltbaren Banken bezeichnet eine CPU-Adresse allein keine eindeutige physische Position in der ROM. Übergeben Sie bei Bedarf den Mapper-Zustand über `--snapshot` und ziehen Sie Ausführungstraces oder Annotationen als weitere Belege heran. Der ursprüngliche Quelltext lässt sich damit nicht vollständig wiederherstellen.

## 9. Verbindung mit SARAKURA
{{CODE:8}}

KUROSAKIs `--emit-diagnostics` erwartet wie bei KOKURA einen **Pfad zu einer JSONL-Datei**. CPU-Traces und Dateien mit Diagnoseereignissen erfüllen unterschiedliche Aufgaben.

## 10. Umfang der Veröffentlichung
KUROSAKI-GUI ist noch nicht veröffentlicht. Dieses Handbuch behandelt die CLI und ihre Schnittstellen zur Einbindung in andere Programme.

## 11. FDS und Spielstand-RAM
`fds-inspect` untersucht die Diskettenstruktur, `export-assets` exportiert Ressourcen. Testen Sie FDS getrennt von NES-Modulen, da sich Startvorgang, BIOS-Anforderungen und Datenträgerzugriffe unterscheiden. Batteriegestützte `.sav`-Dateien und `.kss.json`-Snapshots haben verschiedene Aufgaben. Verwenden Sie ein Speicherlayout, das die Implementierung unterstützt.

{{CODE:9}}

`battery-export` extrahiert die rohen Spielstand-RAM-Daten aus einer passenden ROM und ihrem Snapshot. `battery-run` lädt diese Daten und startet beim Einschalten; der unterbrochene CPU- oder PPU-Ausführungszustand wird dabei nicht wiederhergestellt. Geben Sie die Ausgabedatei mit `--save-out` an. Diese Operationen erfordern eine unterstützte ROM mit Spielstand-RAM und eignen sich nicht für jede Übungs-ROM.
