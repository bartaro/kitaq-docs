## Bienvenido
KITAQGB nació como una **bifurcación de NORCAL**, el compilador de C para NES vinculado a Zachtronics. A partir de esa base se desarrolló un compilador de la familia C para Game Boy y Game Boy Color, adaptando la generación de código, la memoria, el vídeo, el audio y los bancos de ROM. Conservamos el aviso de derechos de autor de Keith Holman y reconocemos su trabajo original.

{{ORIGIN}}

NORCAL se desarrolló en relación con la versión de HACK*MATCH para NES. Puedes consultar las presentaciones de su autor: [NORCAL: A C Compiler for the NES](https://keithholman.net/nes-compiler.html) y [HACK*MATCH para NES](https://trashworldnews.com/hack-match/).

## Cómo usar estos manuales
Como los manuales de los primeros ordenadores, esta colección empieza con programas breves que puedes escribir, compilar y ejecutar. Primero verás un resultado; después podrás aprender cómo funciona la máquina. No hace falta memorizar todos los términos de antemano.

1. Para GB, empieza por el primer programa del volumen 1; para FC, por el del volumen 4.
2. Añade controles, gráficos y sonido con los volúmenes 2 y 5.
3. Observa la ejecución con KOKURA o KUROSAKI y organiza los diagnósticos con SARAKURA.
4. Si ya conoces el nombre de una función, utiliza la búsqueda del volumen o su diccionario de API.

La sintaxis del lenguaje, las funciones intrínsecas del compilador, las funciones de biblioteca y los comandos se documentan por separado. Los volúmenes de compiladores incluyen también índices de instrucciones de CPU. Un mismo nombre en GB y FC no garantiza los mismos argumentos ni el mismo comportamiento.

## Los siete volúmenes
| Volumen | Entrada | Salida o finalidad |
| --- | --- | --- |
| KITAQGB | Código C y recursos | ROM de GB/CGB, mapas e información de compilación |
| Biblioteca KITAQGB | Llamadas desde el juego | Gráficos, sonido, entrada, comunicación y servicios de juego |
| KOKURA | ROM de GB/CGB | Ejecución, imágenes, audio, estados y observaciones |
| KITAQFC | Código C y recursos CHR | Imágenes NES/FDS e información de compilación |
| Biblioteca KITAQFC | Llamadas desde el juego | Gráficos, sonido y dispositivos de NES |
| KUROSAKI | Imágenes NES/FDS | Ejecución, grabación y análisis |
| SARAKURA | Información de compilación y eventos de diagnóstico | Informes, planes de corrección y de repetición de pruebas |

## La fuente incluida
Las 26 mayúsculas, 10 cifras, 26 minúsculas y 30 símbolos proceden del archivo [ascii.c](samples/assets/ascii.c) del autor. No se han añadido formas nuevas: se conservan los 92 glifos originales. Consulta el [mapa de conversión](verification/font_conversion.json) y el [atlas de tiles](verification/font_source_atlas.png). El espacio utiliza un tile vacío. La barra inversa y la barra vertical no están incluidas y aparecen en blanco. `gb_font.c` y `fc_font.c` muestran todos los glifos disponibles.

## Edición y alcance de las comprobaciones
Este manual describe el **código fuente del 14 de septiembre de 2026**. El inventario de referencia registra los hashes de los fuentes y los ejecutables. Consulta los registros de verificación para conocer las entradas, las condiciones y el alcance de cada prueba.

Una compilación correcta significa que se generó una ROM. Una prueba de ejecución significa que el emulador avanzó los fotogramas indicados. Las comparaciones de píxeles, los controles y el sonido se comprueban por separado. Esto no garantiza compatibilidad con todos los periféricos o consolas reales; los avisos se conservan en los registros.

La publicación actual no incluye KOKURA-GUI, KUROSAKI-GUI ni PLITA. Utiliza los núcleos, las CLI y las API de integración publicados.

## Preparar el directorio de trabajo
Los ejemplos usan **Windows PowerShell**. Guarda los archivos C como texto UTF-8. El directorio actual es aquel desde el que ejecutas el comando. Encierra entre comillas las rutas con espacios y, cuando sea necesario, invoca el ejecutable con `& "ruta"`. Clona los repositorios uno junto a otro siguiendo la [guía de GitHub](../GITHUB_SETUP.md). Ejecuta los comandos que combinan proyectos desde su directorio padre.

{{CODE:0}}

Sustituye `game.c`, `game.gb` y `game.nes` por tus archivos. Los corchetes angulares de `<ROM>` indican un valor que debes sustituir; no los escribas. Los comandos suelen ocupar una sola línea. La continuación con barra inversa de Bash no es sintaxis de PowerShell.

## Correcciones del compilador utilizadas
Los ejemplos revelaron una colisión de etiquetas locales internas en KITAQGB y problemas de KITAQFC al conservar valores intermedios y de retorno entre llamadas. Las comprobaciones registradas usaron los compiladores corregidos, incluido el ejemplo de reserva de objetos de GB y los de funciones y estructuras de FC. Esto no demuestra compatibilidad con todas las construcciones de C. Consulta la [verificación de cada ejemplo](verification.html).

## Leer, imprimir y publicar el HTML
Abre `index.html` desde la carpeta descargada para leer sin conexión. Los estilos, la búsqueda, los ejemplos y las imágenes son locales; no hace falta una CDN. Mantén la estructura completa de directorios. El botón de impresión aplica un diseño sin la columna de navegación.

El sitio de los manuales se aloja en `kitaq-docs`. La vista del repositorio de GitHub suele mostrar el código HTML; GitHub Pages muestra las páginas renderizadas. El README explica cómo publicarlas y distribuir el código. Todas las ediciones comparten los siete volúmenes, las API, los ejemplos y las referencias de verificación. Los fragmentos de código y las respuestas capturadas de las herramientas se mantienen en su redacción original para poder cotejarlos con exactitud.
