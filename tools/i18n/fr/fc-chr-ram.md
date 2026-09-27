### 8.1 RAM CHR pour des graphismes modifiables

`--nes-chr-ram` produit une ROM de cartouche utilisant 8 KiB de RAM CHR accessible en écriture. Le fichier ROM ne contient aucune donnée CHR : le programme doit donc transférer les motifs des tuiles vers le PPU à l’initialisation. Le moteur de rendu `wire3d.c` utilise ce mode.

{{BUILD}}

`--nes-chr=tiles.chr` ou `--chr-rom=tiles.chr` intègre des motifs préparés dans une ROM CHR. Aucun de ces deux paramètres ne peut être combiné avec `--nes-chr-ram`. Le profil CNROM refuse également le mode RAM CHR. Vérifiez que le mapper et la carte ciblés disposent de la RAM CHR nécessaire.

Sans option CHR, le compilateur intègre une ROM CHR vide de 8 KiB. Sélectionnez explicitement `--nes-chr-ram` pour les exemples qui transfèrent des motifs pendant l’exécution. La RAM CHR est distincte de la RAM PRG côté CPU ; le tampon de préparation du rendu filaire nécessite aussi sa propre allocation de RAM PRG.
