## 1. Die Bibliothek verwenden
Die Bibliothek besteht aus wiederverwendbaren C-Quelldateien, die auf den `__`-Intrinsics von KITAQGB aufbauen. Sie umfasst Bildschirmsteuerung, Physik, 3D-Darstellung und Kommunikation.

{{CODE:0}}

{{CODE:1}}

Jeder API-Eintrag nennt Deklaration, Header, Implementierung und ein Anwendungsbeispiel. Wo bisher ein Beispiel fehlte, wurde ein Aufruffragment ergänzt. Die dort verwendeten Puffer und Objekte müssen Sie im aufrufenden Programm bereitstellen. Direkt zu einer ROM kompilierbare Beispiele finden Sie im Abschnitt mit vollständigen Programmen.

## 2. Ein Spielbild vorbereiten
`system_init` initialisiert die Bildverwaltung. `system_wait_vblank` wartet auf VBlank und erhöht den Software-Bildzähler. Auf dem GB ruft diese Wartefunktion den VBlank-Callback kooperativ auf. Das Registrieren eines Callbacks richtet keinen Hardware-Interrupt-Handler ein.

1. Aktualisieren Sie den Eingabezustand einmal.
2. Berechnen Sie Bewegung, Kollisionen und Spielzustand.
3. Bereiten Sie Zeichenbefehle und OAM-Daten vor.
4. Übertragen Sie die Änderungen während VBlank.
5. Lassen Sie die Musik entsprechend dem gewählten Treiber weiterlaufen.

Wenn Sie mehrere wartende Funktionen wie `vram_flush` und `sprite_flush_oam` kombinieren, kann eine einzige Spielaktualisierung zwei Bildwechsel abwarten. Haben Sie bereits selbst gewartet, kann die entsprechende `_now`-Funktion geeignet sein. Dabei müssen Sie deren Anforderungen an den Zugriffszeitpunkt selbst sicherstellen.

## 3. Eingaben und Tastenwiederholung
`input_down(mask)` prüft gehaltene Tasten, `input_pressed(mask)` neu gedrückte Tasten und `input_released(mask)` gerade losgelassene Tasten. `input_repeat(mask)` liefert die für Menüs übliche Tastenwiederholung. Diese Zustände ändern sich bei `input_update()`. Mehrere Aktualisierungen innerhalb desselben Spielbildes können ein gerade erkanntes Drücken wieder überschreiben.

| Tasten | Masken |
| --- | --- |
| Rechts, Links, Oben, Unten | 0x01 / 0x02 / 0x04 / 0x08 |
| A, B, SELECT, START | 0x10 / 0x20 / 0x40 / 0x80 |

`gb_input.c` zählt das Drücken von A. Prüfen Sie zunächst, dass das Gedrückthalten den Zähler nicht fortlaufend erhöht. Ersetzen Sie anschließend `input_pressed` durch `input_down`, um den Unterschied zu sehen.

## 4. Hintergrund, Text und VRAM
`vram_queue_bg_tile` stellt eine Kachel in die Warteschlange, `vram_queue_bg_rect` ein Rechteck und `vram_queue_bg_block` die Übertragung eines Arrays. Prüfen Sie die Rückgabewerte und `vram_get_overflowed()`, um einen Überlauf zu erkennen. Behält ein Auftrag einen Quellzeiger, müssen die Quelldaten bis zum Ende der Übertragung unverändert bleiben. Der Speicher muss gültig und seine Bank zugänglich sein.

`text.c` und `menu.c` implementieren die in `rpg.h` deklarierten Funktionen für Text, Auswahlmenüs und Fenster. Stimmen Sie die Zuordnung von Zeichen zu Kacheln auf die Schrift ab, die Sie ins VRAM laden. Diese Zuordnung entspricht nicht automatisch der des Handbuchhelfers `m_text`.

## 5. Sprites und Animation
Beginnen Sie mit `sprite_init`, `sprite_alloc`, `sprite_set_tile` und `sprite_set_pos`. Der GB unterstützt insgesamt 40 Sprites und höchstens 10 pro Bildschirmzeile. Achten Sie deshalb auch darauf, wie viele Sprites sich auf gleicher Höhe befinden. `sprite_warn_scanline_overflow` und `sprite_max_scanline_count` helfen bei der Prüfung.

`MetaSpritePart` beschreibt die relative Anordnung von OBJ-Teilen. `SpriteAnim` beschreibt die Kacheln einer Animation und deren Wechselintervalle. Die von `metasprite_draw` gezeichneten Teile müssen zu den reservierten OBJ-Plätzen passen. Das A in `gb_sprite.c` zeigt, wie eine Zeichenkachel als Sprite verwendet wird.

## 6. Farbe, Scrollen, Rastereffekte und Kamera
Die RGB-Argumente von `cgb_bg_rgb` und `cgb_obj_rgb` liegen zwischen 0 und 31, nicht zwischen 0 und 255. `CGB_RGB15` fasst diese Komponenten in einem 16-Bit-Wert zusammen. Die übergeordneten CGB-Palettenfunktionen sind so ausgelegt, dass sie auf dem DMG keine Wirkung haben.

`Scroll_SetBg` positioniert den Hintergrund und `Scroll_SetWindow` das Fenster. Das Kameramodul berechnet aus Weltkoordinaten einen sichtbaren Ausschnitt. Unterscheiden Sie dabei zwischen den Festkommaeinheiten der Kamera und ganzzahligen Bildschirmpixeln.

`raster.c` erstellt Scrolltabellen für Bildstreifen und horizontale Verzerrungen pro Zeile. Die Operationen von `Scroll_SplitCommit` verwenden die VBlank- und STAT-Vektoren. Musik- und Scrollroutinen dürfen denselben Vektor nicht unabhängig voneinander belegen. Führen Sie ihre Aufrufe bei Bedarf in einem gemeinsamen Interrupt-Handler zusammen.

## 7. Musik und Soundeffekte
Kompilieren Sie zuerst `audio_hwregs_gb.c`, danach `audio.c` und zuletzt den Spielquelltext. Definiert das Spiel die Register NR10–NR52 bereits, dürfen Sie diese Definitionen nicht doppelt einbinden. Nach `Audio_Init` wird `Audio_Update` üblicherweise einmal pro Bild aufgerufen.

`Audio_PlayMusic(bank,song)` gibt die Musikbank ausdrücklich an. `Audio_PlaySFXBanked` spielt einen Effekt aus einer anderen Bank ab. Prioritäten entscheiden darüber, welcher Effekt einen gemeinsam genutzten Hardwarekanal erhält. Der GB besitzt vier Hardware-Soundkanäle: CH1, CH2, CH3 und CH4.

Die Musikbefehle `AUDIO_CMD_NOTE` und `AUDIO_CMD_SET_INST` verwenden aus historischen Gründen die Reihenfolge **0=CH1, 1=CH2, 2=CH4, 3=CH3**. Verwechseln Sie diese nicht mit den üblichen Kanalkonstanten der API. Im Header ist derzeit `AUDIO_NOTE_MAX=67` definiert.

Der einfache CH1-Effektstrom liest pro Bild ein Paar aus Note und Lautstärke und endet bei Note 0. CH3 verwendet ein anderes Format und eine andere Endmarkierung. Ein Beispiel finden Sie in `gb_sound.c`. Überblendungen schreiten bei `Audio_Update` fort; ohne weitere Aktualisierungen bleibt auch die Überblendung stehen.

## 8. Musik im VBlank-Interrupt
`audio_vblank.c` verwendet ein eigenes Wiedergabeformat. Zeitgesteuerte Datensätze bestehen aus fünf Bytes: `delay, ch2_note, ch1_note, ch3_note, ch4_noise_param`. Der Treiber liest direkt adressierbare Musikdaten oder verarbeitet eine WRAM-Warteschlange. Die öffentliche Bibliothek enthält keine Routine zum Nachfüllen dieser Warteschlange. Ihr Spiel muss die Daten bereitstellen und Schreibzugriffe mit der ISR abstimmen. `LOOP` wird nur in direkten Datenströmen erkannt, `IMMEDIATE` nur im Warteschlangenmodus. Datenströme für `audio.c` lassen sich nicht unverändert übergeben.

{{CODE:2}}

Der Patch setzt den VBlank-Vektor bei 0x0040 und aktualisiert die Prüfsumme. Wenden Sie ihn nur auf eine für diesen Treiber vorbereitete ROM an. Prüfen Sie mögliche Konflikte mit eigenen VBlank-ISRs und geteiltem Scrollen. Eine erfolgreiche Kompilierung belegt noch keine hörbare Wiedergabe. Nehmen Sie den Ton mit KOKURA auf und prüfen Sie, ob das Musikstück tatsächlich fortschreitet.

## 9. Festkomma, Physik und 3D
Bei der Q8.8-Arithmetik aus `fixed.h` steht 256 für 1,0 und 128 für 0,5. `gb_fixed.c` zeigt `fix_from_int`, `fix_mul` und `fix_to_int`. Legen Sie die Wertebereiche vor der Implementierung fest, um Überläufe zu vermeiden.

`physics2d` verarbeitet Rechtecke, `physics2d_circle` Kreise und `physics3d` achsenparallele 3D-Quader (AABBs). Initialisieren Sie die vom Aufrufer bereitgestellten Welt- und Körperarrays, setzen Sie Geschwindigkeit oder Schwerkraft und führen Sie dann einen Simulationsschritt aus. Verwenden Sie einheitliche Einheiten für Positionen und Geschwindigkeiten pro Schritt; die Bibliothek rechnet nicht automatisch in Pixel um. Das Kreisbeispiel verwendet Position 40 und Geschwindigkeit 2. Eine inverse Masse von null kennzeichnet einen statischen Körper. Beachten Sie die in den Headern angegebenen Bereiche für Koeffizienten und Zwischenrechnungen. Besonders wichtig ist die ältere Funktion `kq2d_body_apply_friction`: Sie wandelt ihren Koeffizienten in ein vorzeichenbehaftetes Byte um. Werte von 128 bis 255 werden dadurch negativ und sind keine gewöhnlichen vorzeichenlosen Q8-Dämpfungsfaktoren. `gb_circle.c` enthält ein vollständiges Beispiel für einen Simulationsschritt.

`wire3d_dmg` ist eine Bibliothek für monochrome Drahtgittergrafik auf dem Game Boy. Kompilieren Sie `wire3d_dmg_96.c` für 128 × 96 oder `wire3d_dmg.c` für 128 × 120 und verwenden Sie die Funktionen `Wire3DDMG_*`. Die bisherigen Dateien `wire3d` und `dmg3d` bleiben als kompatible Einstiegspunkte für das jeweilige Profil erhalten. Kompilieren Sie nur einen Einstiegspunkt. Der separate Farbrenderer heißt weiterhin `wire3d_cgb`. Reservieren Sie die RAM-, VRAM- und Bildschirmbereiche für jeden Renderer ausdrücklich. Die beiden monochromen Renderer verwerfen Kanten, die den zulässigen Tiefenbereich überschreiten, anstatt sie an dessen Grenzen abzuschneiden. Ihre Verdeckungsprüfung verwendet umschließende Rechtecke von Flächen und fünf Prüfpunkte je Linie. Sie ist daher eine Näherung und kein Tiefentest für jedes Pixel. Der CGB-Pfad nutzt doppelte Taktrate und DMA und benötigt `--cgb=cgb_only`.

`Wire3DDMG_BeginFrame` (`WIRE3D_DMG_HEIGHT=96`) leert den Zeichenpuffer. `Wire3DDMG_BeginFrame` (`WIRE3D_DMG_HEIGHT=120`) setzt lediglich den Verdeckungszustand zurück: DMG3D überträgt die vorgemerkten Bytes und löscht sie dabei. Bei der Übertragung geänderter Kacheln werden auch die Kacheln des vorherigen Bildes berücksichtigt, damit alte Pixel verschwinden. Die zusätzliche Übertragung nutzt einen Teil des Hauptpuffers gemeinsam; sie besitzt keinen unabhängigen Puffer. Passen Sie deshalb die Reihenfolge der Aufrufe an den verwendeten Renderer an.

Verwenden Sie für CGB-Linien die Farben 1, 2 und 3. Der normale Modus mit 128 × 96 kombiniert die Farbbits: Überlagern sich Farbe 1 und Farbe 2, entsteht Farbe 3. Farbe 0 löscht keine Linie. Löschen Sie stattdessen das Bild oder verwenden Sie die dafür vorgesehenen Löschfunktionen. Im normalen Modus erfassen `Wire3DCGB_DrawLine2D` und die Modelldarstellung nicht den Bereich für eine Teilübertragung. Verwenden Sie `Wire3DCGB_DrawLineClipped2D`, wenn beim Linienzeichnen auch dieser Bereich erfasst werden soll. Mit `Wire3DCGB_InvalidateFrameHistory` nehmen Sie den gesamten Zeichenbereich in die nächste Teilübertragung auf.

Der Modus mit 160 × 144 reserviert höchstens 127 Kacheln pro Bild. Kann der schnelle Linienzeichner keine weitere Kachel reservieren oder trifft er auf eine Koordinate außerhalb des Bildschirms, liefert `Wire3DCGB_GetFullScreenOverflow()` einen Wert ungleich null. Weitere Pixelschreibzugriffe unterbleiben bis zur Initialisierung des nächsten Bildes. Halten Sie die Eckpunkte innerhalb des gewählten Zeichenbereichs. Der rechte Sicherheitsrand der Dreiecksmaske reicht im Modus 128 × 96 höchstens bis X=127, im Vollbildmodus bis X=159. Beachten Sie die bei den APIs beschriebene WRAM-Bankzuordnung, insbesondere bei Vollbild- und FastMap-Funktionen.

## 10. Szenen, Objektpools und Geschossmuster
`scene` verwaltet Zustände wie Titelbild, Spiel und Pause. `entity` stellt einen Objektpool mit fester Kapazität bereit. `chain` speichert einen Koordinatenverlauf für Schlangen, Züge oder Seile. Prüfen Sie Fehlerwerte der Reservierung wie 0xFF, bevor Sie den von `entity_get` gelieferten Zeiger verwenden.

`danmaku` bietet Geschosspools mit Festkommaarithmetik, gerichtetes und fächerförmiges Erzeugen von Geschossen sowie Treffer- und Streiferkennung. Sein CGB-Pfad setzt Geschosse in den Hintergrund ein und umgeht damit die übliche OBJ-Anzahlbegrenzung. Rechenzeit pro Bild und Bandbreite für Hintergrundübertragungen bleiben jedoch begrenzt. Messen Sie die Verarbeitungszeit, statt allein eine hohe Geschosszahl anzustreben.

## 11. Rollenspiele, Adventures, Strategiespiele und Speichern
`rpg.h` bündelt Deklarationen für Zufallszahlen, Flags, Aufgaben, Kompression, Text, Menüs, Skripte, Karten, Spielstände und Wegsuche. Die Implementierungen verteilen sich auf Dateien wie `rng.c`, `flags.c`, `rle.c` und `text.c`. Wählen Sie anhand der API-Referenz die benötigten Implementierungsdateien aus.

Ein fester Wert für `rng_seed` erzeugt eine wiederholbare Folge für Tests. Prüfen Sie bei jeder Bereichsfunktion, ob die obere Grenze eingeschlossen ist. `flag_get` und `flag_set` arbeiten mit Bitmengen. `save.c` greift nach dem MBC5-Schema auf SRAM zu. Die im ROM-Header angegebene RAM-Kapazität muss zum Speicherbereich des Spiels passen.

Trennen Sie die Brett-, Zuglisten- und Rücknahmefunktionen aus `slg.h` sowie die Wegsuche aus `slg_path.c` von Ihren eigenen Spielregeln und Bewertungsfunktionen. Breite, Höhe und Arbeitsarrays müssen sowohl die Bibliotheksgrenzen als auch die Anforderungen der einzelnen Argumente einhalten.

## 12. Kommunikation
`link.c` stellt serielle Byteübertragungen bereit. `link_packet.c` ergänzt bei Bedarf eine Paketschicht. Binden Sie `link_hwregs_gb.c` zuerst ein. Polling- und Interrupt-Modus benötigen unterschiedliche Aufrufe. Im Interrupt-Modus muss das Spiel den Vektor 0x0058 mit der passenden Routine verbinden.

Die logischen `Link4_*`-Operationen und die Operationen für den physischen Nintendo-DMG-07-Adapter unter `LinkDmg07_*` sind getrennte Systeme. DMG-07 arbeitet mit einem externen Takt: Rufen Sie `LinkDmg07_Poll` häufig und `LinkDmg07_TickFrame` einmal pro Bild auf. Nur einmal pro Bild zu pollen kann zeitlich unzureichend sein. Prüfen Sie mit den KOKURA-Aufträgen für pair/dmg07 das Verbinden, den Start, das Trennen und das erneute Verbinden jeweils gesondert.

## 13. Banken, Ressourcen und Fehlersuche
`BankPtr` verbindet eine Banknummer mit einem Zeiger. `far_data_read` liest Ressourcen aus einer anderen Bank ins RAM. Das Ressourcenmodul ordnet IDs den entsprechenden Beschreibungen zu. Für Gültigkeitsdauer, Bankzugriff und Größen bleibt das Spiel verantwortlich.

`debug_trace_u8` und `debug_trace_u16` protokollieren Werte im RAM; `debug_assert_fail` speichert einen Diagnosecode. Diese Funktionen geben keinen `printf`-Text auf einer PC-Konsole aus. Untersuchen Sie die Einträge über die Speicheransicht des Emulators. `gb_debug.c` protokolliert HP=42.

`vram_get_queue_capacity()` liefert die Gesamtzahl der Befehlsplätze, standardmäßig 32. `vram_get_queue_free()` liefert die Zahl der freien Plätze, `vram_get_queue_used()` die Zahl der belegten Plätze. Jeder vorgemerkte Auftrag benötigt unabhängig von seiner Übertragungsgröße genau einen Platz. Diese Abfragen beschreiben die Übertragungswarteschlange, nicht den ungenutzten Teil des Hardware-VRAMs.
