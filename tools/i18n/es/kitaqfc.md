## 1. KITAQFC y el compilador de GB
KITAQFC utiliza el front-end de KITAQGB para generar código para la CPU de la familia 6502 de NES/Famicom. No convierte una ROM de GB en una de NES. El programa debe diseñarse para la pantalla, el sonido, la memoria y el mapper de su destino.

KITAQFC admite copias de estructuras, llamadas normales a funciones y bucles for, while y do-while. Un do-while ejecuta el cuerpo al menos una vez antes de comprobar la condición. continue pasa a esa comprobación final; break sale del bucle. switch selecciona una constante case entre 0 y 255, o el cuerpo de default si no hay coincidencia. La expresión de selección se evalúa una sola vez. break sale del bucle o switch más interno; continue dentro de un switch pasa a la siguiente iteración del bucle que lo contiene.

## 2. Requisitos y compilación
Con Rust 1.85 o posterior puede compilar el compilador y todas las herramientas para Windows, Linux, macOS ARM y macOS Intel. Los ejecutables nativos no necesitan .NET; las herramientas de recursos tampoco requieren Python ni Pillow.

{{CODE:0}}

Los ejecutables de Windows están en la raíz del repositorio; los de Linux y macOS, en los directorios bin/ de la tabla siguiente. Conserve lib/ y los avisos de licencia junto a las herramientas. En Linux/macOS use chmod +x y añada el directorio al PATH, o ejecute mediante la ruta completa.

Los scripts PowerShell usan el ejecutable Windows de la raíz. En Linux/macOS pase las mismas entradas C y opciones al compilador nativo, o use PowerShell 7. Los gráficos CHR y el código C son entradas distintas; font.chr conserva la fuente de los ejemplos.

## 3. Tu primer programa
{{CODE:1}}

{{CODE:2}}

El programa muestra HELLO WORLD y 042. `m_wait` confirma la cola de VRAM, espera la NMI y restaura el desplazamiento de pantalla. Las transferencias mediante PPUADDR alteran el estado interno de desplazamiento; no restaurarlo puede mover el texto hacia un borde. Aprende esta secuencia: apagar la imagen, preparar recursos, encenderla y sincronizar con NMI.

## 4. Introducción al lenguaje
Las sentencias y expresiones del volumen GB son una base común. FC acepta `unsigned char` y `unsigned short`; `core.h` define `u8`, `u16`, `s8` y `s16`. `fc.h` reúne los encabezados. Aquí sí puedes declarar una entrada sin argumentos como `void main(void)`.

{{CODE:3}}

Mantén los enteros dentro de sus rangos de 8 o 16 bits. Los índices empiezan en cero. `fc_aggregate.c` enseña funciones, punteros y estructuras; `fc_arithmetic.c`, aritmética; `fc_control.c`, bucles. No incluyas registros CGB ni operaciones exclusivas de GB.

<!-- common-language-kitaqfc:start -->
### Resultados de las expresiones y evaluación

Los operadores de comparación `==`, `!=`, `<`, `<=`, `>`, `>=` y los operadores lógicos `!`, `&&`, `||` devuelven 0 para falso y 1 para verdadero. Puedes guardar el resultado en un `u16`, pasarlo como argumento, devolverlo o usarlo en operaciones aritméticas. Por ejemplo, `score = 500 + (lives != 0);` produce 501 si queda alguna vida y 500 en caso contrario.

`&&` omite la evaluación del operando derecho cuando el izquierdo es cero. `||` la omite cuando el izquierdo no es cero. En `pointer != 0 && pointer->active != 0`, un puntero nulo impide el acceso al miembro. Los dos bytes de un valor de 16 bits intervienen en la comprobación lógica, por lo que 256 es verdadero. Los operadores de bits `&` y `|` no realizan evaluación en cortocircuito.

`++value` devuelve el valor actualizado; `value++`, el valor original. Estos operadores también admiten elementos de arrays, punteros desreferenciados y miembros de estructuras. `buffer[index()]++` llama a `index()` una sola vez. Para `u16 *p`, `p++` avanza dos bytes hasta el siguiente elemento, mientras que `(*p)++` incrementa el valor apuntado.

`sizeof(array)` da el tamaño en bytes del array completo; `sizeof(pointer)` es 2. Para `u16 values[9];`, `sizeof(values)` es 18. Esto incluye arrays en ROM, arrays locales y miembros de tipo array. `sizeof(function())` examina el tipo de retorno sin llamar a la función.

La declaración y la definición de una función deben coincidir en los tipos y el orden de los parámetros. Sus nombres pueden ser distintos; el cuerpo usa los de la definición. Por ejemplo, `u8 next(u8 input);` puede definirse como `u8 next(u8 value) { return (u8)(value + 1); }`. Los parámetros y las variables locales ocultan las variables globales con el mismo nombre.

Seleccionar arrays o cadenas con `?:` produce un puntero al tipo de elemento seleccionado. Puedes pasarlo directamente, como en `show(ready ? "READY" : "WAIT");`. Para los arrays `u16` llamados `a` y `b`, `(ready ? a : b) + 1` avanza dos bytes hasta el segundo elemento del array elegido. No copia el array.

`condition ? yes : no` evalúa la condición y después solo la rama seleccionada. La condición y las ramas pueden incluir desplazamientos con cantidades de bits variables. Por ejemplo, `on = (pattern & (0x80 >> bit)) != 0 ? 4 : 2;` elige cuatro o dos según el bit indicado. Tampoco se ejecutan las llamadas a funciones de un operando derecho omitido por `&&` o `||`. Un `continue` en un bucle `for` ejecuta una vez la expresión de actualización antes de reevaluar la condición; en `while` y `do ... while`, pasa a la condición.

<!-- common-language-kitaqfc:end -->

## 5. Bucles y selección de acciones según el estado
{{CODE:4}}

Estos fragmentos muestran un bucle que actualiza al menos una vez y una bifurcación que elige el manejador del estado actual. Define update, condition, state y los manejadores de estado en tu programa. Consulta fc_control.c para un ejemplo completo de bucle y el ejemplo de fotogramas y escenas de la biblioteca para una ROM completa de gestión de escenas.

Registra los callbacks de escenas, entidades y sistema con los tipos de argumentos y retorno que exigen sus declaraciones. Las bibliotecas invocan los manejadores registrados desde las operaciones correspondientes de actualización, dibujo o espera de fotograma. Respeta los requisitos de bancos ROM y mapeo de cada API. No presupongas el mismo soporte para recursión o funciones variádicas que en un equipo de escritorio.

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

Las lecturas normales por índice y las referencias mediante punteros de C a arrays en ROM colocan esos arrays en el banco común 0, salvo que `#pragma fixed_bank` fije explícitamente su ubicación. Así, los datos siguen siendo visibles cuando quien los usa se ejecuta en un banco conmutable. Para un acceso lejano explícito, pasa en la misma llamada el nombre del array sin modificar y `__bankof` aplicado a ese mismo nombre, por ejemplo `__farpeek8(__bankof(table), table)`. Consultar únicamente el número de banco no solicita la ubicación en el banco común. Los datos fijados explícitamente a un banco y las referencias dentro de ensamblador requieren que mantengas el mapeo correcto. Esta regla comprueba la ubicación según la sintaxis, no mediante un análisis del flujo de punteros. Sigue aplicándose el límite de capacidad del banco común.

## 9. FDS, sonido de expansión y periféricos
FDS requiere distribuir archivos de disco y planificar arranque, overlays y guardado. Consulta `fds_manifest_sample.json` y los encabezados FDS. Si necesitas una BIOS, debes disponer de ella en tu entorno de ejecución: no se incluye en la distribución pública.

Llamar a una operación de sonido VRC6 o VRC7 no cambia el mapper de la ROM. Ambos deben corresponderse. Para periféricos, prueba por separado la entrada legible, la conexión y sus efectos sobre la lectura del mando normal.

## 10. Diagnósticos y resultados
Los diagnósticos KQ y comandos como `symfind`, `src2asm` y `romdiff` se parecen a los de GB. Algunas opciones heredadas de su ayuda pueden no estar implementadas para NES. El diccionario FC se extrae de sus propias fuentes y encabezados.

Avisos de acceso directo a PPU, como KQ2421, pueden aparecer incluso al inicializar con la pantalla apagada. No rompas una inicialización segura solo para eliminar un aviso: revisa tiempos de renderizado y registros. Cero errores y cero avisos son resultados distintos.

## Ubicación del código fuente
El código fuente del compilador y el archivo de proyecto están en el subdirectorio que lleva el nombre del repositorio. El ejecutable está en la raíz y las bibliotecas, en `lib/`. Consulta la [estructura de directorios](../GITHUB_SETUP.md) para conocer las rutas y los requisitos de compilación.
