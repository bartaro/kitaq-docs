### 8.1 CHR-RAM für veränderbare Grafik

`--nes-chr-ram` erzeugt eine Cartridge-ROM, die 8 KiB beschreibbaren CHR-RAM nutzt. Die ROM-Datei enthält keine CHR-Daten; deshalb muss das Programm die Tile-Muster während der Initialisierung an die PPU übertragen. Der Renderer `wire3d.c` verwendet diesen Modus.

{{BUILD}}

`--nes-chr=tiles.chr` oder `--chr-rom=tiles.chr` bindet vorbereitete Muster als CHR-ROM ein. Keine der beiden Optionen lässt sich mit `--nes-chr-ram` kombinieren. Auch das CNROM-Profil unterstützt den CHR-RAM-Modus nicht. Prüfen Sie, ob der gewählte Mapper und die Platine den benötigten CHR-RAM bereitstellen.

Ohne CHR-Optionen bindet der Compiler einen leeren CHR-ROM mit 8 KiB ein. Wählen Sie für Beispiele, die Muster zur Laufzeit übertragen, ausdrücklich `--nes-chr-ram`. CHR-RAM ist vom CPU-seitigen PRG-RAM getrennt; der Vorbereitungspuffer für die Drahtgitterdarstellung benötigt zusätzlich einen eigenen PRG-RAM-Bereich.
