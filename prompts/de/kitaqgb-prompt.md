# Spieleentwicklung mit KITAQGB, KOKURA und SARAKURA

Tragen Sie die Anforderungen ein und geben Sie dieses gesamte Dokument an die KI weiter. Die Befehle setzen voraus, dass die Repositories `kitaqgb`, `kitaqfc`, `kokura`, `kurosaki`, `sarakura` und `kitaq-docs` sowie das Projekt `game-gb` oder `game-fc` im selben übergeordneten Ordner liegen. Führen Sie die Befehle dort aus und passen Sie die Pfade an die tatsächliche Umgebung an.

## Anforderungen

- Spieltitel: <ausfüllen>
- Genre und zentrale Spielmechanik: <ausfüllen>
- Steuerung sowie Erfolgs- und Misserfolgsbedingungen: <ausfüllen>
- Erforderliche Bildschirme, Level, Gegner und Gegenstände: <ausfüllen>
- Grafikstil, Musik und Geräusche: <ausfüllen; bereitgestellte Dateien angeben>
- Speichern, Kommunikation, Zusatzgeräte und weitere Anforderungen: <ausfüllen oder keine>
- Projektordner: <ausfüllen>
- Bedingungen für die Weitergabe: <etwa eigener Code und eigene Medien, die unter MIT veröffentlicht werden können>

- Zielgerät: <ursprünglicher Game Boy / GB und CGB / nur CGB>
- Leistungsziel: <etwa 60 Aktualisierungen der Spiellogik pro Sekunde im normalen Spiel; akzeptables Verhalten in aufwendigen Szenen festlegen>

## Arbeitsauftrag

Setzen Sie das Spiel mit KITAQGB und seinen Bibliotheken um. Verwenden Sie KOKURA zum Ausführen und Debuggen und SARAKURA zum Auswerten der Diagnosen sowie zum Vergleich vor und nach einer Korrektur.

Wiederholen Sie diesen Ablauf, bis die Abnahmekriterien erfüllt sind: Spezifikation konkretisieren → kleine Änderung umsetzen → bauen → Eingaben ausführen und beobachten → Ursache untersuchen → korrigieren → unter gleichen Bedingungen erneut testen. Ein Plan, ausgegebener Quellcode oder ein erfolgreicher Compilerlauf allein schließen den Auftrag nicht ab.

### Umgebung und Abnahmekriterien klären

1. Lesen Sie die Anweisungen im Arbeitsverzeichnis, READMEs, HTML-Handbücher sowie Header und Implementierungen der verwendeten Bibliotheken. Erfassen Sie die Pfade der Programme und ihre Versionen oder SHA-256-Werte. Prüfen Sie Befehle anhand der tatsächlichen `--help`-Ausgabe und APIs anhand des Quellcodes.
2. Legen Sie überprüfbare Kriterien für Eingaben, Bild, Ton, Spielverlauf und Aktualisierungsrate fest. Beispiele: START drücken und loslassen beginnt das Spiel; eine Kollision kostet ein Leben; die Pause schaltet die vorgesehenen Töne stumm, Fortsetzen nimmt die Wiedergabe wieder auf.
3. Fragen Sie nur bei wesentlichen Unklarheiten nach. Treffen Sie übliche, rückgängig zu machende Implementierungsentscheidungen selbstständig. Schwächen Sie Anforderungen und Abnahmekriterien nicht ab.
4. Führen Sie zunächst ein kleines mitgeliefertes Beispiel durch Compiler, Emulator und SARAKURA. Das prüft deren Zusammenspiel, nicht die Fertigstellung des beauftragten Spiels.

### Eine kleine spielbare Fassung umsetzen

- Verwenden Sie den C-Dialekt von KITAQGB und `void main()`. Setzen Sie Desktop-C- oder GBDK-APIs nicht als verfügbar voraus. Binden Sie die benötigten `.c`-Implementierungen ein, nicht nur Deklarationen; prüfen Sie Initialisierung, Einheiten, Vorzeichen, Wertebereiche, Pufferlebensdauer und ROM-Bänke.
- Planen Sie VRAM/OAM-Aktualisierungen, VBlank, Interrupts, Stack, ROM/WRAM-Bänke sowie Grenzen für Tiles und Sprites. Gesamt- und Restkapazität der Übertragungswarteschlange sind etwas anderes als Kapazität und freier Platz des physischen VRAM.
- Ein DMG-Spiel darf nicht von CGB-exklusiven Funktionen abhängen. Bei Unterstützung beider Geräte sind beide Hardwaremodi zu prüfen.
- Verwenden Sie für Buchstaben, Ziffern und Symbole die bereitgestellte eigene Schrift aus `ascii.c` und prüfen Sie die Zuordnung von Zeichen zu Tiles.

- Verbinden Sie zunächst Start, Titelbild, steuerbare Spielfigur, Erfolg oder Misserfolg und Neustart. Erweitern Sie danach den Inhalt.
- Bewahren Sie bearbeitbare Originale von Grafik, Musik und Geräuschen sowie deren Erzeugungsschritte auf. Prüfen Sie, dass der Build tatsächlich die exportierten Daten verwendet.
- Schreiben Sie Codekommentare auf Englisch und Fortschrittsberichte auf Deutsch. Lassen Sie die Standardberichte von SARAKURA auf Englisch.

### Jeden Build seiner Ausführung zuordnen

Trennen Sie Ausgaben nach Iteration, etwa mit `out/iter-001`. Protokollieren Sie Befehle, Rückgabecodes und Hashes von Quellcode, Medien, Werkzeugen, ROM und Metadaten. Führen Sie nach einem fehlgeschlagenen Build niemals eine alte ROM aus. Speicherbelegungspläne, Quellcodezuordnungen und Debuginformationen müssen aus demselben Build wie die ROM stammen.

Das folgende Beispiel ist eine grundlegende DMG-Prüfung. Stellen Sie `main.c` und alle erforderlichen Bibliotheksimplementierungen bereit und passen Sie Optionen und Eingabefolge an das Spiel an.

```powershell
$iteration = '.\game-gb\out\iter-001'
New-Item -ItemType Directory -Force $iteration | Out-Null

# Include all additional implementation units required by the game.
& '.\kitaqgb\kitaqgb.exe' '.\game-gb\src\main.c' `
  -I '.\kitaqgb\lib' -o "$iteration\game.gb" `
  --profile=dev --rst-disable --stack-bank=fixed --no-disasm `
  "--emit-ai-metadata=$iteration\build.json"
if ($LASTEXITCODE -ne 0) { throw 'Build failed; inspect the build log.' }

# This sequence presses START once, with released intervals on both sides.
& '.\kokura\kokura-cli.exe' "$iteration\game.gb" `
  --hardware dmg --run-frames 300 `
  --input-seq 'NONE:60;START:1;NONE:239' `
  --png "$iteration\frame.png" --record-wav "$iteration\audio.wav" `
  --dump-report "$iteration\run.json" `
  --emit-diagnostics "$iteration\events.jsonl"
if ($LASTEXITCODE -ne 0) { throw 'Emulator run failed; inspect the run log.' }

& '.\sarakura\sarakura.exe' gb analyze `
  --metadata "$iteration\build.json" --events "$iteration\events.jsonl" `
  --frames 300 --out "$iteration\analysis" --fail-on error
if ($LASTEXITCODE -ne 0) { throw 'Inspect the analysis report and fix the cause.' }
```


`--hardware dmg` wählt den ursprünglichen Game Boy. Stimmen Sie bei CGB oder Unterstützung beider Geräte den ROM-Header und den Hardwaremodus des Emulators aufeinander ab. Die Eingabefolge drückt START einmal zwischen Abschnitten mit losgelassenen Tasten. 300 Frames prüfen nicht das gesamte Spiel.

### Bild, Ton, Zustand und Leistung prüfen

- Speichern Sie Eingabeszenarien mit getrenntem Drücken, Halten und Loslassen. Durchlaufen Sie alle vorgesehenen Wege: Start, Spielbeginn, Bewegung, Aktionen, Kollisionen, Scrolling, Levelwechsel, Spielende, Neustart, Pause und gegebenenfalls Speichern oder Kommunikation.
- Bewahren Sie PNGs relevanter Frames, Eingaben, Laufberichte, Diagnose-JSONL, WAVs und nötige Zustands- oder Speicherbeobachtungen auf. Prüfen Sie erreichte Frames und Abbruchgrund. Öffnen Sie die Bilder tatsächlich; ein einzelner Screenshot belegt weder Bewegung noch Eingabereaktion. Vergleichen Sie Zähler, Positionen und Zustandswechsel mit Sollwerten; prüfen Sie Bildschirmränder, Tile- und Attributgrenzen und Szenen mit vielen Sprites.
- Prüfen Sie Musik, Geräusche, gleichzeitige Wiedergabe, Aussetzer, Pause und Fortsetzen. Eine erzeugte WAV-Datei allein belegt keinen korrekten Klang. Ist Anhören nicht möglich, trennen Sie ausgeführte Wellenform- und Zahlenprüfungen von unbestätigten Höreigenschaften.
- Messen Sie aufwendige Szenen, Arbeit der Ziel-CPU, Spielaktualisierungen und Transfers; auf FC auch die NMI-Arbeit. Emulatordurchsatz auf dem Host ist weder Spielaktualisierungsrate noch Nachweis für reale Hardwaregeschwindigkeit. Fortsetzen mit `--allow-unimplemented` belegt keine Unterstützung der fehlenden Funktion.

### Analysieren, korrigieren und erneut testen

- Übergeben Sie SARAKURA die Buildmetadaten der geprüften ROM und Diagnose-JSONL aus dem zugehörigen Lauf. Ein CPU-Trace oder gewöhnlicher Laufbericht ersetzt dies nicht. `--frames` legt Analysebedingungen fest; SARAKURA führt weder ROMs aus noch ändert es automatisch Quellcode.
- Lesen Sie `report.html`, `ai_diagnostics.json`, `repair_prompt.md` und `retest_plan.json`. Gleichen Sie Diagnosen mit Reproduktionsschritten, Bildern, Ton und Quellcode ab. Trennen Sie vermutete Quellstellen oder Ursachen von bestätigten Tatsachen und normale Warteschleifen von Hängern. Bewerten Sie Warnungen einzeln und dokumentieren Sie nicht unterstützte Ereignisse sowie Analysegrenzen. Verbergen Sie Warnungen nicht durch Filter und verkürzen Sie Tests nicht, um ein Bestehen zu erreichen.
- Reduzieren Sie Fehler auf minimale Reproduktionen, beheben Sie die Ursache und bauen Sie neu. Liegt der Fehler im Compiler oder Emulator, grenzen Sie ihn vom Spielcode ab und ergänzen Sie eine Regressionsprüfung für die Werkzeugkorrektur.
- Wiederholen Sie Tests mit gleichen Eingaben, Zufallsstartwerten, Hardware- und Videomodi, Mappern, Beobachtungsframes und Diagnoseeinstellungen. Nutzen Sie für jede ROM passende Metadaten; verwenden Sie nach Änderungen an Code oder RAM-Belegung nicht blind alte Speicherzustände weiter.

```powershell
& '.\sarakura\sarakura.exe' baseline-delta `
  --baseline '.\game-gb\out\iter-001\analysis' `
  --current '.\game-gb\out\iter-002\analysis' `
  --out '.\game-gb\out\delta.json' --markdown '.\game-gb\out\delta.md' `
  --fail-on-new error --fail-on-regression error --enforce
```


Nutzen Sie Diagnosedifferenzen gemeinsam mit den Abnahmekriterien für Steuerung, Grafik und Ton. Wiederholt sich derselbe Fehler, überprüfen Sie Belege und Hypothese, statt beliebige weitere Änderungen vorzunehmen.

### Abschlusskriterien und Lieferumfang

Führen Sie alle Pflichtszenarien erneut mit der finalen ROM aus, die aus den gelieferten Quellen und Einstellungen gebaut wurde. Unverwundbarkeit, automatische Testeingaben oder ein anderer Mapper allein prüfen kein normales Spiel in der Endfassung. Liefern Sie eine Zuordnung von Anforderungen zu Tests, Gründe für verbleibende Warnungen und klare Angaben zu ungeprüften oder nicht unterstützten Punkten. Kennzeichnen Sie ausdrücklich, wenn nicht auf physischer Hardware getestet wurde.

Liefern Sie Quellcode, Kennungen von Werkzeugen und Bibliotheken, bearbeitbare Medien, reproduzierbare Build- und Testskripte, ROM, abschließende Nachweise und eine README mit Einrichtung, Steuerung und bekannten Grenzen. Fügen Sie bei Bedarf Replays und das Testprogramm hinzu. Veröffentlichen oder versenden Sie Dateien nur im ausdrücklich erlaubten Umfang. Entfernen Sie unnötige Zwischenbuilds und temporäre Traces nach der Prüfung, bewahren Sie jedoch Quellen, Medien, Endergebnisse und erforderliche Regressionsnachweise auf.

Verhindern Umgebung oder Berechtigungen eine Pflichtprüfung, nennen Sie die genauen Reproduktionsschritte und die nötige Maßnahme. Kennzeichnen Sie die Arbeit nicht als abgeschlossen.
