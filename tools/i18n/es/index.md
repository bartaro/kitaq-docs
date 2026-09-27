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
Los ejemplos utilizan la fuente [ascii.c](samples/assets/ascii.c), creada por el autor: 26 mayúsculas, 10 cifras, 26 minúsculas y 30 símbolos, para un total de 92 glifos. Puedes verlos en el [atlas de tiles](verification/font_source_atlas.png). El espacio utiliza un tile vacío. La barra inversa y la barra vertical no están incluidas y se muestran en blanco. `gb_font.c` y `fc_font.c` muestran todos los glifos.

## Edición y alcance de las comprobaciones
Este manual describe el **código fuente del 14 de septiembre de 2026**. El inventario de referencia registra los hashes de los fuentes y los ejecutables. Consulta los registros de verificación para conocer las entradas, las condiciones y el alcance de cada prueba.

Una compilación correcta significa que se generó una ROM. Una prueba de ejecución significa que el emulador avanzó los fotogramas indicados. Las comparaciones de píxeles, los controles y el sonido se comprueban por separado. Esto no garantiza compatibilidad con todos los periféricos o consolas reales; los avisos se conservan en los registros.

## Preparar el directorio de trabajo
Los ejemplos usan **Windows PowerShell**. Guarda los archivos C como texto UTF-8. El directorio actual es aquel desde el que ejecutas el comando. Encierra entre comillas las rutas con espacios y, cuando sea necesario, invoca el ejecutable con `& "ruta"`. En los ejemplos que combinan herramientas, coloca sus repositorios y el proyecto del juego dentro de un mismo directorio padre y ejecuta los comandos desde él.

{{CODE:0}}

Sustituye `game.c`, `game.gb` y `game.nes` por tus archivos. Los corchetes angulares de `<ROM>` indican un valor que debes sustituir; no los escribas. Los comandos suelen ocupar una sola línea. La continuación con barra inversa de Bash no es sintaxis de PowerShell.

## Leer e imprimir los manuales HTML
Abre `index.html` desde la carpeta descargada para leer sin conexión. Los estilos, la búsqueda, los ejemplos y las imágenes son locales; no hace falta una CDN. Mantén la estructura completa de directorios. El botón de impresión aplica un diseño sin la columna de navegación.

Los fragmentos de código y las salidas reales de las herramientas mantienen su redacción original para poder cotejarlos directamente con los archivos y los resultados de los comandos.
