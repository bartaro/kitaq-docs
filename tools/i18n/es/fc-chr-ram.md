### 8.1 CHR RAM para gráficos modificables

`--nes-chr-ram` genera una ROM de cartucho que utiliza 8 KiB de CHR RAM escribible. El archivo ROM no almacena datos CHR, por lo que el programa debe cargar los patrones de los tiles en PPU durante la inicialización. El renderizador `wire3d.c` utiliza este modo.

{{BUILD}}

`--nes-chr=tiles.chr` o `--chr-rom=tiles.chr` incorpora patrones preparados como CHR ROM. Ninguna de estas dos opciones puede combinarse con `--nes-chr-ram`. El perfil CNROM tampoco admite el modo CHR RAM. Compruebe que el mapper y la placa de destino dispongan de la CHR RAM necesaria.

Si omite todas las opciones CHR, el compilador incorpora una CHR ROM vacía de 8 KiB. Seleccione explícitamente `--nes-chr-ram` en los ejemplos que cargan patrones durante la ejecución. CHR RAM es independiente de la PRG RAM de CPU; el búfer de preparación de gráficos alámbricos también necesita su propia asignación de PRG RAM.
