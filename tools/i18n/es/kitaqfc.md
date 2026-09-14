## 1. KITAQFC y el compilador de GB
KITAQFC utiliza el front-end de KITAQGB para generar código para la CPU de la familia 6502 de NES/Famicom. No convierte una ROM de GB en una de NES. El programa debe diseñarse para la pantalla, el sonido, la memoria y el mapper de su destino.

Las pruebas registradas ejecutaron ejemplos con copias de estructuras y llamadas normales. Sin embargo, **do-while y switch produjeron errores de generación de código no compatible en NES**. Que una construcción aparezca en el analizador no demuestra que pueda utilizarse en este destino.

## 2. Requisitos y compilación
{{CODE:0}}

Instala .NET Framework 4.8 Developer Pack y Visual Studio Build Tools, y usa Developer PowerShell. Los comandos siguientes emplean el ejecutable copiado al repositorio `kitaqfc`; ajusta la ruta si utilizas otra ubicación. Los gráficos CHR y el código C son entradas distintas. `font.chr` es una conversión de 8 KiB del `ascii.c` del autor.

## 3. Tu primer programa
{{CODE:1}}

{{CODE:2}}

El programa muestra HELLO WORLD y 042. `m_wait` confirma la cola de VRAM, espera la NMI y restaura el desplazamiento de pantalla. Las transferencias mediante PPUADDR alteran el estado interno de desplazamiento; no restaurarlo puede mover el texto hacia un borde. Aprende esta secuencia: apagar la imagen, preparar recursos, encenderla y sincronizar con NMI.

## 4. Introducción al lenguaje
Las sentencias y expresiones del volumen GB son una base común. FC acepta `unsigned char` y `unsigned short`; `core.h` define `u8`, `u16`, `s8` y `s16`. `fc.h` reúne los encabezados. Aquí sí puedes declarar una entrada sin argumentos como `void main(void)`.

{{CODE:3}}

Mantén los enteros dentro de sus rangos de 8 o 16 bits. Los índices empiezan en cero. `fc_aggregate.c` enseña funciones, punteros y estructuras; `fc_arithmetic.c`, aritmética; `fc_control.c`, bucles. No incluyas registros CGB ni operaciones exclusivas de GB.

## 5. Sustituir construcciones no compatibles
{{CODE:4}}

Para reemplazar do-while, ejecuta el cuerpo una vez antes de comprobar la condición de salida. Un switch sencillo puede convertirse en una cadena if/else. Son fragmentos explicativos: debes proporcionar `update` y las funciones de estado. Para una ROM completa, utiliza `fc_control.c`.

No des por hecho el soporte de recursión, llamadas indirectas o funciones variádicas propio de un compilador de escritorio. Algunas API de scene/entity guardan punteros a callbacks, pero no los invocan indirectamente.

## 6. Memoria y PPU
La RAM interna de CPU ocupa 0x0000–0x07FF. Sus réplicas por encima de 0x0800 no son RAM adicional. La pila del 6502 usa la página 1; el OAM en RAM y las colas reservan otras zonas. `--nes-local-ram=START:LENGTH` y `--nes-temp-ram=START:LENGTH` son ajustes avanzados que requieren revisar el mapa.

La PPU tiene su propio espacio de direcciones. CHR contiene patrones; las nametables colocan tiles; las tablas de atributos eligen grupos de paletas; las paletas contienen códigos de color. Los atributos de fondo suelen aplicarse a zonas de 16×16 píxeles, no como los atributos de tile de GB.

## 7. NMI y cola de VRAM
La NMI es la interrupción asociada al límite de cada fotograma. Las escrituras directas grandes en PPU durante el renderizado pueden corromper la pantalla. Inicializa directamente con la imagen apagada; para actualizaciones normales usa `__vramq_put`, `__vramq_copy`, `__vramq_fill` y la confirmación de la cola.

{{CODE:5}}

Comprueba la capacidad y la vida útil de los datos de origen. La NMI predeterminada procesa la cola. Un `__nes_nmi` propio debe conservar la ejecución de cola necesaria, el trabajo de OAM y los registros requeridos.

## 8. Mappers y distribución de ROM
| Selección | Uso inicial habitual |
| --- | --- |
| nrom | Lecciones pequeñas con ROM fija |
| uxrom / cnrom / axrom | Cambio sencillo de PRG o CHR |
| mmc1 / mmc3 / mmc5 | Programas mayores y funciones propias del mapper |
| vrc6 / vrc7 / fme7 | Bancos y expansiones correspondientes |
| fds | Salida de imagen de disco |

Son selecciones del compilador, no una tabla de compatibilidad completa de hardware o emuladores. `--board=surom512` elige una configuración concreta de placa MMC1. Rellenar un archivo hasta 512 KiB no establece esa configuración. Acompáñalo de la auditoría de placa de KUROSAKI.

{{CODE:6}}

Revisa los requisitos de `--battery` / `--no-battery`, capacidad CHR, distribución PRG y llamadas entre bancos. Tras cambiar de mapper o modo de mirroring, prueba el arranque, el desplazamiento y el acceso a bancos, además de generar la ROM.

## 9. FDS, sonido de expansión y periféricos
FDS requiere distribuir archivos de disco y planificar arranque, overlays y guardado. Consulta `fds_manifest_sample.json` y los encabezados FDS. Si necesitas una BIOS, debes disponer de ella en tu entorno de ejecución: no se incluye en la distribución pública.

Llamar a una operación de sonido VRC6 o VRC7 no cambia el mapper de la ROM. Ambos deben corresponderse. Para periféricos, prueba por separado la entrada legible, la conexión y sus efectos sobre la lectura del mando normal.

## 10. Diagnósticos y resultados
Los diagnósticos KQ y comandos como `symfind`, `src2asm` y `romdiff` se parecen a los de GB. Algunas opciones heredadas de su ayuda pueden no estar implementadas para NES. El diccionario FC se extrae de sus propias fuentes y encabezados.

Avisos de acceso directo a PPU, como KQ2421, pueden aparecer incluso al inicializar con la pantalla apagada. No rompas una inicialización segura solo para eliminar un aviso: revisa tiempos de renderizado y registros. Cero errores y cero avisos son resultados distintos.

## Ubicación de las fuentes
Las fuentes del compilador están en el subdirectorio que comparte el nombre del repositorio. La referencia conserva rutas históricas del 12 de septiembre. Consulta la [reorganización](../GITHUB_SETUP.md); las rutas del ejecutable raíz y de las bibliotecas no han cambiado.
