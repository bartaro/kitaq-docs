## 1. Benötigte Bausteine auswählen
`fc.h` sammelt Deklarationen, `core.h` definiert Typen und `intrinsics.h` die Compiler-Operationen. Gewöhnliche C-Bibliotheksfunktionen benötigen die zugehörige `.c`-Implementierung. Reine Header-Makros und Intrinsics brauchen nicht unbedingt eine gleichnamige Quelldatei.

{{CODE:0}}

Richten Sie `-I` nicht auf die ähnlich benannte GB-Bibliothek. Beispielsweise hat NES `__oam_dma()` kein Argument, während die GB-Operation einen Zeiger erhält.

## 2. Laufzeit und System
`runtime.c` bietet C-Hilfen für PPU-Register, OAM-Schattenpuffer und VRAM-Warteschlangen. Daneben gibt es Intrinsics wie `__vramq_*`. Prüfen Sie, welche Daten der NMI-Handler verarbeitet, statt getrennte Warteschlangen mit ähnlichen Namen zu vermischen.

`system_init` initialisiert den Frame-Zustand und aktiviert NMI. `system_wait_vblank` wartet auf NMI und erhöht den Software-Frame-Zähler. **FC `system_set_vblank_callback` speichert den Wert, aber die aktuelle Wartefunktion führt den Callback nicht aus.** Verlegen Sie nicht sämtliche Spielaktualisierungen dorthin in der Annahme, es gelte das GB-Verhalten.

## 3. PPU, Kacheln, Attribute und Paletten
`ppu_direct.h` bietet direkte PPU-Operationen, `vram_queue.h` Aktualisierungen über NMI. `tilemap` / `nametable_asset` bearbeiten Tabellen und Ressourcen, `attribute` die Attribute und `palette` die Paletten. Trennen Sie das anfängliche Laden von der Arbeit pro Frame.

Hintergrund- und Sprite-Paletten belegen jeweils eine Gruppe von 16 Bytes. Die Werte sind NES-Farbcodes, keine RGB-Komponenten. Attribute wählen Farben für Kachelgruppen. Eine scheinbar einzelne Palettenänderung kann daher benachbarte Kacheln beeinflussen.

Einige Deklarationen in `ppu.h` stimmen nicht mit Implementierungsnamen in `ppu.c` überein. Bei Einträgen mit **nur deklariert** wurde im erfassten Bereich keine Implementierung gefunden; die Einsteigerbeispiele rufen sie nicht direkt auf. Die ausführbaren Übungen verwenden geprüfte Intrinsics. Eine Deklaration allein belegt keine fertige, linkbare Funktion.

## 4. OAM, Metasprites und abwechselnde Darstellung
Das NES unterstützt bis zu 64 Sprites, gewöhnlich acht pro Scanline. Neun oder mehr Gegner oder Geschosse auf einer Zeile können nicht alle gleichzeitig erscheinen. Metasprites kombinieren mehrere OBJs zu einem Bild. Prüfen Sie dafür Reservierungsgrenzen und Abschlussmarkierungen.

`oam_fair.h` und `oam_fair_impl.h` wechseln die Reihenfolge der Kandidaten unter Wahrung ihrer Prioritäten. So können Spieler oder HUD bevorzugt und weniger wichtige Objekte abwechselnd angezeigt werden. Eine andere OAM-Reihenfolge ändert die Hardwaregrenze pro Scanline nicht.

## 5. Eingaben, Wiederholung und Zubehör
`input.c` übersetzt rohe NES-Tastenwerte in `BTN_*`-Masken im GB-Stil. **Der rohe NES-Wert für A ist 0x01, BTN_A der Bibliothek ist 0x10.** Übergeben Sie BTN_A daher nicht direkt an KUROSAKIs `--pad1`.

`pad` liest grundlegende Eingaben, `input_repeat` sorgt für Wiederholung bei gehaltenen Tasten. `zapper`, `keyboard`, `rob`, `mic` und `midi` bieten hardwarenahe Geräteschnittstellen. Ein Nullwert von einem nicht angeschlossenen Gerät belegt keinen erfolgreichen Betrieb. Prüfen Sie die jeweiligen Anschlussbedingungen.

## 6. Ton
Nach `nes_apu_init` verwenden Sie `nes_sfx_square1`, `nes_sfx_square2`, `nes_sfx_triangle` oder `nes_sfx_noise` für die eingebaute Soundhardware. Ein Periodenargument bezeichnet die Hardware-Timerperiode, keine Frequenz in Hertz. `fc_sound.c` ist ein minimales Beispiel für einen Pulston.

DMC-Samples unterliegen Anforderungen an Adresse, Länge, Ausrichtung und Rate. Prüfen Sie die Map, bevor Sie einen Zeiger übergeben. DMC-DMA kann außerdem Controller-Lesezugriffe stören. Kombinieren Sie sichere Leseverfahren mit KUROSAKI-Diagnosen.

VRC6 bietet zusätzliche Puls- und Sägezahnkanäle, VRC7 FM-Register und FDS Wavetable-Sound. Wählen Sie einen passenden Mapper und zeichnen Sie das Ergebnis auf. Diese APIs sind vom GB-Treiber `Audio_*` getrennt.

## 7. Szenen, Akteure und Entities
`actor` und `entity` verwalten Spielobjekte in festen Arrays, `scene` den Szenenzustand. Erkennen Sie erschöpfte Kapazitäten und verwenden Sie freigegebene IDs nicht weiter. Einige FC-APIs registrieren derzeit Callbacks, ohne sie aufzurufen. In Einsteigerprogrammen rufen Sie die Update-Funktion des jeweiligen Zustands ausdrücklich aus der Hauptschleife auf.

`chain` speichert einen Koordinatenverlauf, `collision` prüft Berührungen zwischen Formen wie Rechtecken. Eine feste Reihenfolge aus Bewegung, Kollision und Zeichnen verhindert Kollisionsentscheidungen, die einen Frame hinterherhinken.

## 8. Mathematik und Physik
`fixed.h` bietet Q8.8-Arithmetik, `math_fast` / `math_fixed` numerische Operationen und `math_lut` tabellenbasierte Berechnungen. Die aktuelle `physics2d.h` liefert **Q5.3-Typen und -Konstanten**, keine Implementierung von Integrationsfunktionen oder Update-Makros. Sie ist nicht die world/body-Physik-API der GB-Bibliothek.

Q5.3-Bruchteile stellen Achtelpixel dar. Halten Sie ganzzahlige Koordinaten, Bruchteile, Geschwindigkeit und Richtung getrennt und bearbeiten Sie Addition und Übertrag im Spielcode. `fc_subpixel.c` addiert achtmal 2/8 Pixel und bewegt sich von Pixel 40 zu Pixel 42. Übernehmen Sie die Q8.8-Darstellung 256 nicht unverändert als Q5.3.

## 9. Ressourcen, Mapper und FDS
`bank` und `asset` beschreiben PRG-Banken und Ressourcen. Ob eine Operation aus `mapper.h` wirksam ist, hängt vom beim Build gewählten Mapper ab. Planen Sie Konfiguration, Aktivierung, Quittierung und Deaktivierung von Scroll-IRQs als zusammenhängenden Ablauf.

FDS-Dienste verteilen sich auf `fds_file`, `fds_overlay`, `fds_save` und `fds_sound`. Ein geladenes Overlay ersetzt Code an einer bestehenden Adresse. Beachten Sie deshalb Rücksprungziele und die Gültigkeitsdauer von Daten. Gehen Sie nicht vom gewöhnlichen Far-Call-Verhalten eines Moduls aus.

## 10. Referenzeinträge und Beispiele
Das folgende Verzeichnis orientiert sich an den öffentlichen Headern und unterscheidet Funktionen, funktionsartige Makros und Aliase. Die vollständigen Header enthalten auch Strukturen und Konstanten. Nur deklarierte APIs, lediglich gespeicherte Callbacks und spezielle Geräteschnittstellen werden von gewöhnlichen geprüften Operationen unterschieden. Quellkommentare bleiben zum genauen Vergleich mit der Implementierung unverändert.

`vram_get_queue_capacity()` liefert die Gesamtkapazität des Befehlspuffers von 128 Bytes. `vram_get_queue_free()` liefert die freien Bytes: Gesamtkapazität minus `vram_get_queue_used()`. Gemeint sind codierte Befehle einschließlich Verwaltungsdaten, kein freier Hardware-VRAM. Ein einzelner Kachelschreibzugriff benötigt 4 Bytes, Füllen 5 und eine zeigerbasierte Kopie 6 Bytes. Prüfen Sie den Platz vor der Freigabe; NMI kann eine freigegebene Warteschlange asynchron abarbeiten.
