## 1. Conocer KITAQGB
KITAQGB es un compilador de la familia C para GB/CGB desarrollado a partir de NORCAL, de Zachtronics.

{{ORIGIN}}

Lee archivos C, genera instrucciones de CPU y las empaqueta en una ROM. Su lenguaje, bibliotecas y convenciones de llamada difieren de los de un compilador de escritorio.

GB tiene una CPU de 8 bits y poca memoria. La mayoría de los gráficos usan tiles de 8×8 píxeles. Los sprites son imágenes pequeñas que pueden colocarse de forma independiente. El texto también necesita tiles: no hay que dar por sentado un sistema universal de impresión de caracteres. Los ejemplos reordenan los glifos de `ascii.c` según ASCII para GB sin cambiar sus bits; la edición FC conserva las mismas formas en disposición NES CHR.

## 2. Requisitos y compilación del compilador
Instala un entorno Visual Studio/MSBuild con soporte para .NET Framework 4.8. Usa Developer PowerShell, con `MSBuild.exe` disponible.

{{CODE:0}}

Mantén juntos el ejecutable y sus archivos de configuración. Indica la ruta del compilador en los comandos para identificar con claridad cuál se utiliza. Al compilar el proyecto, el ejecutable se copia a la raíz del repositorio `kitaqgb`.

## 3. Tu primer programa
`samples/gb_hello.c` utiliza las funciones auxiliares de pantalla y texto de `gb_common.h`. Mantén ese encabezado junto a los archivos de la fuente. `#include` incorpora declaraciones o definiciones de otro archivo.

{{CODE:1}}

{{CODE:2}}

El resultado esperado es HELLO WORLD y 042 en pantalla. Los nombres que empiezan por `m_` pertenecen a las funciones didácticas del encabezado común; no son comandos estándar de KITAQGB. Entre las operaciones intrínsecas están `__wait_vblank` y `__vram_copy`.

## 4. Sintaxis básica y tipos
Termina las sentencias con `;` y agrúpalas con `{ }`. `//` inicia un comentario de línea y `/* ... */` delimita uno de bloque. Las mayúsculas y minúsculas importan. Usa `void main()` como entrada. **En esta versión GB, `void main(void)` produce un error de sintaxis**: no copies sin cambios la declaración de entrada de FC.

| Tipo | Significado y rango |
| --- | --- |
| `u8` | Entero de 8 bits sin signo, de 0 a 255 |
| `s8` | Entero de 8 bits con signo, de -128 a 127 |
| `u16` | Entero de 16 bits sin signo, de 0 a 65535 |
| `s16` | Entero de 16 bits con signo, de -32768 a 32767 |
| `void` | Sin valor de retorno |
| `T*` | Puntero a datos de tipo T |

Empieza usando estos nombres cortos. No supongas que `int`, `long`, `float`, `double` o los encabezados estándar funcionan como en un ordenador de escritorio. Aquí `char` representa 8 bits sin signo; usa `s8` o `s16` explícitamente para operaciones con signo.

{{CODE:3}}

`(u16)` es una conversión de tipo. Asignar un valor pequeño que ya se desbordó a una variable mayor no recupera los bits perdidos: amplía los operandos antes de calcular. Para movimientos fraccionarios, usa la biblioteca de punto fijo.

## 5. Expresiones y operadores
| Grupo | Operadores | Ejemplo o significado |
| --- | --- | --- |
| Aritmética | `+ - * / %` | `n / 10` obtiene el cociente entero; `n % 10`, el resto |
| Comparación | `== != < <= > >=` | `lives == 0` comprueba igualdad |
| Lógica | `! &&` / `||` | Negación, ambas condiciones, cualquiera de ellas |
| Bits | `&` / `|` / `^ ~ << >>` | Máscaras de botones y conjuntos de bits |
| Asignación | `= += -=` y formas relacionadas | `x += 1` actualiza un valor |
| Incremento | `++ --` | `i++` suma uno |
| Selección | `condition ? A : B` | Elige un valor según la condición |
| Punteros | `&variable` / `*p` | Obtiene una dirección o accede a su contenido |

No confundas `=` con `==`. Usa paréntesis en expresiones complejas y evita acumular llamadas y efectos secundarios en una sola sentencia. No dividas por cero ni accedas fuera de un array. `sizeof` da el tamaño en bytes y `offsetof` el desplazamiento de un miembro.

<!-- common-language-kitaqgb:start -->
### Resultados de las expresiones y evaluación

Los operadores de comparación `==`, `!=`, `<`, `<=`, `>`, `>=` y los operadores lógicos `!`, `&&`, `||` devuelven 0 para falso y 1 para verdadero. Puedes guardar el resultado en un `u16`, pasarlo como argumento, devolverlo o usarlo en operaciones aritméticas. Por ejemplo, `score = 500 + (lives != 0);` produce 501 si queda alguna vida y 500 en caso contrario.

`&&` omite la evaluación del operando derecho cuando el izquierdo es cero. `||` la omite cuando el izquierdo no es cero. En `pointer != 0 && pointer->active != 0`, un puntero nulo impide el acceso al miembro. Los dos bytes de un valor de 16 bits intervienen en la comprobación lógica, por lo que 256 es verdadero. Los operadores de bits `&` y `|` no realizan evaluación en cortocircuito.

`++value` devuelve el valor actualizado; `value++`, el valor original. Estos operadores también admiten elementos de arrays, punteros desreferenciados y miembros de estructuras. `buffer[index()]++` llama a `index()` una sola vez. Para `u16 *p`, `p++` avanza dos bytes hasta el siguiente elemento, mientras que `(*p)++` incrementa el valor apuntado.

`sizeof(array)` da el tamaño en bytes del array completo; `sizeof(pointer)` es 2. Para `u16 values[9];`, `sizeof(values)` es 18. Esto incluye arrays en ROM, arrays locales y miembros de tipo array. `sizeof(function())` examina el tipo de retorno sin llamar a la función.

La declaración y la definición de una función deben coincidir en los tipos y el orden de los parámetros. Sus nombres pueden ser distintos; el cuerpo usa los de la definición. Por ejemplo, `u8 next(u8 input);` puede definirse como `u8 next(u8 value) { return (u8)(value + 1); }`. Los parámetros y las variables locales ocultan las variables globales con el mismo nombre.

Seleccionar arrays o cadenas con `?:` produce un puntero al tipo de elemento seleccionado. Puedes pasarlo directamente, como en `show(ready ? "READY" : "WAIT");`. Para los arrays `u16` llamados `a` y `b`, `(ready ? a : b) + 1` avanza dos bytes hasta el segundo elemento del array elegido. No copia el array.

`condition ? yes : no` evalúa la condición y después solo la rama seleccionada. La condición y las ramas pueden incluir desplazamientos con cantidades de bits variables. Por ejemplo, `on = (pattern & (0x80 >> bit)) != 0 ? 4 : 2;` elige cuatro o dos según el bit indicado. Tampoco se ejecutan las llamadas a funciones de un operando derecho omitido por `&&` o `||`. Un `continue` en un bucle `for` ejecuta una vez la expresión de actualización antes de reevaluar la condición; en `while` y `do ... while`, pasa a la condición.

<!-- common-language-kitaqgb:end -->

## 6. Condiciones y bucles
{{CODE:4}}

`break` sale de un bucle o switch, `continue` pasa a la siguiente iteración y `return` termina una función. Para continuar deliberadamente desde un caso de switch al siguiente, escribe `fallthrough;`. La continuación implícita genera un diagnóstico. `gb_control.c` contiene un programa completo.

## 7. Funciones, arrays y estructuras
{{CODE:5}}

Los índices empiezan en cero: un array de cuatro elementos admite del 0 al 3. `player.x` accede a un miembro y `pointer->x` lo hace mediante un puntero. El analizador admite estructuras, uniones y enumeraciones, pero su disposición depende de los tipos y de `__packed` / `__aligned`. Comprueba `sizeof` antes de compartir datos con hardware o formatos binarios.

La ABI Legacy predeterminada coloca los argumentos y el almacenamiento local en posiciones fijas. No presupongas recursión ni reentrada desde interrupciones como en un equipo de escritorio. `__stackcall` y `--abi=stack` son opciones avanzadas de convención de llamada. Si combinas convenciones, examina los informes de ABI y verifica la ejecución. `--abi=stack` no admite llamadas a callbacks mediante punteros a función. Compila los ejemplos completos de callbacks de sistema y escenas con la ABI Legacy predeterminada, tal como indican sus comandos de compilación.

## 8. Varios archivos y preprocesador
Pon tipos, constantes y declaraciones en encabezados, y los cuerpos de funciones en archivos `.c`. Usa `#pragma once` o guardas de inclusión para evitar duplicados. La compilación condicional admite `#define`, `#undef`, `#if`, `#ifdef`, `#ifndef`, `#elif`, `#else` y `#endif`.

{{CODE:6}}

`-I` añade un directorio de búsqueda. Incluir un encabezado no enlaza su implementación: enumera los `.c` necesarios en el comando. Añadir todas las fuentes sin seleccionar puede duplicar registros o manejadores de interrupción.

## 9. ROM, memoria y bancos
ROM almacena código y constantes; WRAM, variables; VRAM, gráficos; OAM, descripciones de sprites. Cambiar de banco modifica la memoria física visible en una dirección de CPU. Un puntero de 16 bits por sí solo no identifica datos de otro banco.

{{CODE:7}}

`__prg_rom` sitúa datos en ROM. `__location(0xFF40)` selecciona una dirección fija, y `__wram` / `__hram`, regiones de memoria. Con `#pragma bank` o `#pragma fixed_bank`, revisa el mapa y garantiza el acceso al código y los datos usados por interrupciones.

{{CODE:8}}

`--cgb=dmg` declara software para DMG, `--cgb=cgb` para ambos modos y `--cgb=cgb_only` exclusivo de CGB. Un juego de modo dual debe detectar la máquina antes de usar funciones exclusivas de CGB. Un indicador en el encabezado no implementa esa lógica dentro del juego.

## 10. Actualizar gráficos con seguridad
VBlank es el intervalo entre fotogramas. Escribir en VRAM u OAM en un momento inadecuado puede corromper la imagen o perder actualizaciones. Carga los recursos iniciales con la pantalla apagada; después usa operaciones seguras o la cola de VRAM. Las funciones `_unsafe` y `_fast` exigen que el llamador garantice un intervalo de transferencia válido.

Alinea el búfer de OAM DMA a un límite de 256 bytes. En GB, `__oam_dma` recibe la dirección de origen; la operación de FC con el mismo nombre no recibe argumentos.

## 11. Opciones y archivos generados
`-o` elige la salida, `-O0` / `-O1` la optimización y `--profile=dev|release|test` un conjunto de ajustes. `--no-disasm` evita la salida desensamblada. `--debug-out=...` y `--trace-out=...` seleccionan destinos de investigación. Adapta la cantidad de salida a una compilación rápida o a un análisis detallado.

{{CODE:9}}

`.map` registra nombres y ubicación; `.funcsizes.txt`, tamaños de funciones; `.dbg2.json` / `.source_map.txt`, la relación entre ejecución y fuentes; `.build_report.json`, el resumen. Generar JSON con `--emit-ai-metadata` hace más clara la conexión con SARAKURA.

## 12. Leer el primer error
Empieza por el archivo, la línea y el número KQ del primer error. Los siguientes pueden ser consecuencias del mismo fallo de sintaxis. Ante un símbolo indefinido, comprueba declaración, implementación e inclusión en la compilación. Si la ROM no cabe, revisa tamaños de recursos y funciones y la distribución por bancos.

{{CODE:10}}

## 13. Ensamblador en línea
`__asm { ... }` acepta los nombres de instrucciones de KITAQGB, no cualquier fuente escrita para otro ensamblador de GB. Algunas grafías internas son del tipo `LD_A_IMM`. Antes de usarlo, comprende los argumentos, retornos, registros preservados y efectos sobre la pila. El apéndice enumera instrucciones y formatos de operandos.

{{CODE:11}}

## Ubicación del código fuente
El código fuente del compilador y el archivo de proyecto están en el subdirectorio que lleva el nombre del repositorio. El ejecutable está en la raíz y las bibliotecas, en `lib/`. Consulta la [estructura de directorios](../GITHUB_SETUP.md) para conocer las rutas y los requisitos de compilación.
