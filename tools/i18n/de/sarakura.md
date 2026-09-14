## Fertige Windows-Version
Im Hauptverzeichnis des Repositorys liegt `sarakura.exe`. Laden Sie das Repository als ZIP herunter und bewahren Sie die Lizenzhinweise zusammen mit der ausführbaren Datei auf. Für diese Windows-x64-Version müssen weder Rust noch Python oder .NET installiert sein. Die folgenden Build-Schritte dienen dem Neubau aus den Quellen. Der eigenständige Projektcode steht unter der MIT-Lizenz von DAISUKE OBA; die Bedingungen der Abhängigkeiten finden Sie in BINARY_NOTICES.md und licenses/.

## 1. Die Aufgabe von SARAKURA
SARAKURA führt Build-Informationen des Compilers und Diagnoseereignisse des Emulators zusammen. Die Ergebnisse sollen bei der Fehlersuche, bei Korrekturen und bei erneuten Tests helfen. SARAKURA führt selbst keine ROM aus und verändert Ihren C-Code nicht automatisch.

## 2. Das Werkzeug kompilieren
{{CODE:0}}

Die kurzen Aufrufe mit `sarakura` setzen voraus, dass das Programm im PATH erreichbar ist. Geben Sie andernfalls den Pfad zur ausführbaren Datei an. Verwenden Sie `gb analyze` für GB und `fc analyze` für FC.

## 3. Die erste Analyse
Zwei Eingaben sind erforderlich: `--metadata` bezeichnet die JSON-Datei mit Build-Daten, `--events` die JSONL-Datei mit Laufzeitdiagnosen. JSONL enthält pro Zeile ein JSON-Objekt.

{{CODE:1}}

Öffnen Sie die erzeugte `report.html` im Browser. Prüfen Sie Zielplattform, beobachtete Frames sowie Fehler- und Warnungszahlen, bevor Sie einzelne Diagnosen lesen. `--frames` beschreibt die Analysebedingungen. Es veranlasst SARAKURA nicht, eine ROM entsprechend lange auszuführen.

## 4. Zuerst die Eingaben prüfen
{{CODE:2}}

Klären Sie zunächst, ob Dateien lesbar sind, die Plattformen zueinander passen und die Ereignistypen unterstützt werden. Erst danach lässt sich das Spielverhalten sinnvoll untersuchen. Ein gewöhnlicher Emulatorbericht wird nicht dadurch zu einer gültigen Ereignisdatei, dass Sie ihn als solche übergeben.

## 5. Diagnosen einordnen
Fehler verdienen Vorrang. Warnungen können je nach Situation auf ein Problem hinweisen, während Informationsmeldungen zusätzlichen Kontext liefern. Der Schweregrad hilft bei der Priorisierung, kennt aber nicht die vollständige Absicht des Spiels. Ein wiederholter Programmzähler kann sowohl zu einer normalen Warteschleife auf dem Titelbildschirm als auch zu einem hängenden Programm gehören.

Vergleichen Sie ROM-Hash, Eingabefolge, Szene, Bild, Ton und Quellposition. Halten Sie die Bedingungen vor und nach einer Korrektur gleich. Weniger Diagnosen könnten sonst lediglich bedeuten, dass eine andere Szene ausgeführt wurde.

## 6. Ausgabedateien
Die eingebauten Erklärungen, Diagnosehinweise und Anweisungen zur Fehlersuche sind auf Englisch. Die HTML-Berichte deklarieren `lang="en"`. Texte aus Benutzereingaben und Ereignis-IDs werden nicht automatisch übersetzt. Standardmäßig werden bestimmte Projektbezeichnungen und Pfade ersetzt; diese Bereinigung anonymisiert jedoch nicht jede Adresse oder Beobachtung. Prüfen Sie Berichte, bevor Sie Analysen privater Eingaben veröffentlichen.

| Datei | Zweck |
| --- | --- |
| ai_diagnostics.json | Normalisierte Diagnosen zur automatisierten Verarbeitung |
| diagnostic_summary.json | Zählwerte und Zusammenfassung |
| report.html | Lesbarer Bericht |
| repair_prompt.md | Ausgangsinformationen für die Fehlersuche |
| repair_plan.json / .md | Reihenfolge und Ziele der Korrekturen |
| automation_plan.json / .md | Arbeitsplan auf Grundlage der Werkzeugfunktionen |
| retest_plan.json | Plan für erneute Prüfungen |
| repro_bundle.zip | Paket mit Informationen zur Reproduktion |

Einen Plan zu erzeugen heißt noch nicht, ihn auszuführen. Nach Änderungen an C-Quellen oder einer ROM müssen Compiler, Emulator und SARAKURA erneut laufen.

## 7. Kataloge, Filter und Abdeckung
{{CODE:3}}

`catalog` listet Diagnoseregeln auf. `pack-plan` ordnet sie Bereichen zu. `coverage` untersucht, welche zugehörigen Ereignisse beobachtet wurden. Ein Eintrag im Katalog garantiert nicht, dass der aktuelle Emulator das betreffende Ereignis ausgibt.

{{CODE:4}}

`--diagnostic-rule` wählt einen Ereignisnamen oder eine Katalog-ID aus, `--phase` eine Phase und `--diagnostic-pack` einen Bereich. Eine Diagnose auszublenden behebt ihre Ursache nicht.

## 8. Vorher und nachher vergleichen
{{CODE:5}}

Die Ergebnisse werden als neu, behoben, verbessert, weiterhin vorhanden oder verschlechtert eingeordnet. Unterscheiden Sie bestehende Probleme von neu hinzugekommenen. Lassen Sie bei Vergleichen Eingaben, Frame-Zahlen und Diagnosefilter unverändert.

## 9. Validierung und kontinuierliche Integration
{{CODE:6}}

Kontinuierliche Integration automatisiert wiederholbare Prüfungen. `ci-summary` beeinflusst den Exitcode des Prozesses nur mit `--enforce`; ohne diese Option müssen Sie das Urteil in der JSON-Ausgabe auswerten. Bei analyze sorgt `--fail-on error` für einen von null verschiedenen Exitcode, wenn Fehler auftreten. Die Voreinstellung `never` lässt den Prozess wegen Diagnosen nicht fehlschlagen. Wählen Sie deshalb für CI ausdrücklich eine passende Regel. Mit `warn` führen auch Warnungen zum Fehlschlag.

```powershell
sarakura ci-summary --diagnostics .\out\report --fail-on error --enforce
if ($LASTEXITCODE -ne 0) { throw "The diagnostic failure condition was met" }
```

Eine erfolgreiche Schemavalidierung bestätigt das Datenformat. Ob das Spiel wie vorgesehen funktioniert, erfordert zusätzlich Tests von Eingaben, Bild und Ton.

## 10. Reproduktionsdateien handhaben
`normalize-events` vereinheitlicht Ereignisdatensätze, `inspect-repro` untersucht ein Reproduktionspaket. Prüfen Sie vor der Weitergabe, ob die Informationen zur vorgesehenen ROM gehören und die nötigen Eingabeschritte enthalten. Mit `--allow-project-labels` bleiben aus dem Projekt stammende Bezeichnungen und Kennungen ausdrücklich erhalten.

## 11. Kleine Übungseingaben
Das Handbuch enthält kleine Beispiele für Build-Metadaten und Ereignisse für GB und FC. Öffnen Sie den [synthetischen GB-Bericht](verification/sarakura-gb-synthetic.html) oder den [synthetischen FC-Bericht](verification/sarakura-fc-synthetic.html). `samples/sarakura_demo.ps1` zeigt die Analyse dieser Daten. Es handelt sich um künstliche Übungseingaben zum Erlernen des Formats, nicht um Aufzeichnungen einer tatsächlichen ROM. Für reale ROM-Tests verwenden Sie Ereignisse von KOKURA oder KUROSAKI.

## 12. Ein Korrektur- und Testdurchlauf
1. Reproduzieren Sie das Problem mit derselben ROM und denselben Eingaben und bewahren Sie Protokolle und Bilder auf.
2. Ordnen Sie mit SARAKURA mögliche Ursachen ein und untersuchen Sie den betreffenden Quelltext.
3. Nehmen Sie eine gezielte Änderung an der Ursache vor.
4. Kompilieren Sie erneut und wiederholen Sie dieselben Aktionen.
5. Vergleichen Sie baseline-delta mit Bildern, Ton und Spielverhalten.

Halten Sie die Durchläufe überschaubar, damit Änderung und Wirkung nachvollziehbar bleiben.
