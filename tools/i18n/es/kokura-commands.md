## 13. Ejemplos de comandos y sintaxis exacta de los argumentos

Ejecute estos comandos de PowerShell desde el directorio que contiene los repositorios situados al mismo nivel. Cree primero el directorio de salida con `New-Item -ItemType Directory -Force out`. Sustituya `out/game.gb` por su ROM. KOKURA recibe las opciones después de la ruta de la ROM; no utiliza el subcomando `run` de KUROSAKI. `--help` muestra las opciones del ejecutable instalado.

### 13.1 Elegir una operación y un límite de fotogramas

| Argumento | Finalidad y comportamiento |
| --- | --- |
| `ROM` | Archivo ROM para una ejecución normal. Una tarea o una matriz puede proporcionar su propia ROM. |
| `--hardware auto`, `dmg`, `cgb` | Selecciona el hardware. El valor predeterminado es `auto`; pruebe explícitamente ambos modos si el juego admite las dos máquinas. |
| `--run-frames 120` | Máximo de fotogramas para la ejecución directa; el valor predeterminado es 1. Las condiciones de parada pueden terminarla antes. Las secuencias de entrada también tienen sus propias duraciones. |
| `--job out/test.json` | Ejecuta una tarea JSON. Su límite de fotogramas se indica en `run.frames`; la ROM, el estado, las entradas y las capturas proceden de la tarea. Las rutas relativas internas se resuelven con respecto al archivo de la tarea. |
| `--dump-report out/run.json` | Guarda el informe JSON resultante. Sin un destino, la ejecución normal imprime el informe en la salida estándar. |
| `--regression-matrix out/matrix.json` | Ejecuta tareas con observaciones esperadas. Revise los resultados de cada caso en el JSON: que el comando de la matriz se ejecute correctamente no significa que todos los casos hayan pasado. |

Elija una operación por invocación. El orden de prioridad es: descompilación, desensamblado, matriz de regresión, tarea de enlace, sesiones enlazadas definidas en la línea de comandos y, por último, ejecución normal. Combinar modos no hace que se ejecuten uno tras otro.

{{COMMAND:0}}

Este comando avanza hasta 120 fotogramas emulados y guarda la pantalla final y un informe. Compruebe en el informe el número real de fotogramas y el motivo de la parada antes de interpretar la imagen.

### 13.2 Mantener botones pulsados o indicar una secuencia temporizada

| Opción | Sintaxis y uso |
| --- | --- |
| `--input "A,RIGHT"` | Mantiene ambos botones pulsados durante una ejecución directa. Los nombres no distinguen mayúsculas de minúsculas. `NONE` suelta todos los botones. |
| `--input-seq "NONE:30;A:1;NONE:89"` | Intervalos `BUTTONS:FRAMES` separados por punto y coma que se ejecutan en orden. Esta secuencia suelta los botones durante 30 fotogramas, pulsa A durante uno y los suelta durante 89. |
| `--input-script "NONE:30;A:1;NONE:89"` | Acepta el mismo texto de secuencia; no es un nombre de archivo. Si se indican ambas opciones de secuencia, prevalece `--input-script`. |

Los nombres de los botones son `RIGHT,LEFT,UP,DOWN,A,B,SELECT,START`. Las máscaras hexadecimales son RIGHT=0x01, LEFT=0x02, UP=0x04, DOWN=0x08, A=0x10, B=0x20, SELECT=0x40 y START=0x80. Son las máscaras de entrada de KOKURA; no reutilice las del mando de NES. En PowerShell, encierre toda la secuencia entre comillas. Al probar una nueva pulsación, incluya intervalos con los botones sueltos y haga que la secuencia cubra todo el periodo que desea observar.

{{COMMAND:1}}

En el ejemplo del contador de botones, el contador debería aumentar una vez. Una imagen estática no basta para determinar si la repetición de un botón mantenido funciona: compare una pulsación prolongada con varias pulsaciones separadas.

### 13.3 Capturar imágenes, movimiento y sonido

| Opción | Sintaxis y uso |
| --- | --- |
| `--png out/final.png` | Guarda la pantalla final; tiene prioridad sobre `--screenshot` si se indican ambas opciones. |
| `--screenshot out/frame.png` | Otro destino para la captura de pantalla. Admite PNG y BMP; una ruta sin extensión recibe `.png`. |
| `--screenshot-frames 30:32` | Guarda cada fotograma seleccionado e incluye su número en el nombre del archivo. Requiere un destino de captura. |
| `--record-wav out/audio.wav` | Graba audio en WAV. Utilice una ROM y un intervalo que realmente reproduzcan sonido. |
| `--record-wav-frames 1:180` | Selecciona el intervalo de grabación, incluidos ambos extremos. Son números de fotograma, no cantidades de muestras. |
| `--record-video out/motion.gif` | Graba movimiento en GIF o Y4M. Una ruta sin extensión recibe `.gif`; MP4 no es un formato admitido. |
| `--record-video-frames 30:120` | Selecciona el intervalo de vídeo, incluidos ambos extremos. |
| `--audio-buffer-frames 8192` | Fija la capacidad del búfer de audio en tramas de muestras estéreo, no en fotogramas de vídeo emulado ni en muestras individuales de izquierda o derecha. |

Los intervalos de captura usan números decimales a partir de 1: `30` selecciona un fotograma y `30:32` incluye los fotogramas 30, 31 y 32. Se rechazan el cero y los intervalos invertidos. Los índices corresponden a la ejecución actual, por lo que debe conservar el informe al reanudar un estado anterior. Cree los directorios padre antes de capturar.

{{COMMAND:2}}

Use varios fotogramas para evaluar el desplazamiento o la animación. Use el WAV para evaluar el sonido: un número de finalización visible no demuestra que haya sonado el canal previsto.

### 13.4 Guardar y reanudar el estado de la máquina

| Opción | Finalidad y prioridad |
| --- | --- |
| `--save-state out/checkpoint.kqs` | Guarda el estado de la máquina al terminar la ejecución. |
| `--snapshot out/checkpoint.kqs` | Tiene la misma función de salida y prioridad sobre `--save-state`. |
| `--load-state out/checkpoint.kqs` | Carga un estado KQS antes de ejecutar. |
| `--resume-state out/checkpoint.kqs` | Tiene prioridad sobre `--load-state` y puede sustituir el estado de entrada de una tarea. |
| `--snapshot-at "frame=60&&frame_end=>out/frame60.kqs"` | Guarda cuando se cumple una condición de observación. Repita la opción para varias solicitudes. Sin `=>path`, se genera en el directorio actual un nombre numerado a partir del nombre de la ROM. |

Utilice un estado compatible con la ROM y la versión del emulador. KQS representa el estado de la máquina, no la RAM de guardado del cartucho ni la serialización JSON de la API de C.

{{COMMAND:3}}

### 13.5 Observar regiones de memoria con nombre

| Opción | Sintaxis y uso |
| --- | --- |
| `--symbols out/game.map` | Carga los símbolos de la compilación correspondiente. |
| `--source-map out/game.source_map.txt` | Relaciona la ejecución con las ubicaciones del código fuente. |
| `--toolchain-metadata out/game.dbg2.json` | Carga metadatos estructurados de la cadena de herramientas. También pueden detectarse los archivos auxiliares correspondientes junto a la ROM. |
| `--watch-window "player:0xC700:16"` | Observa 16 bytes desde 0xC700 con la etiqueta player. Repita la opción para otras regiones; observa memoria, pero no detiene la ejecución por sí misma. |
| `--watch-baseline-mode initial` | Compara con los valores iniciales. `previous-frame` compara fotogramas consecutivos; `named` selecciona una referencia capturada explícitamente. |
| `--watch-baseline-tag ready` | Selecciona el nombre de la referencia para una comparación con referencia nombrada. |
| `--capture-watch-baseline "ready=>frame=30&&frame_end"` | Captura una referencia con nombre cuando se cumple una condición. Repita la opción para capturar otras referencias. |
| `--watch-fields preview,diff` | Elige grupos de campos de observación: `hash`, `activity`, `preview`, `baseline`, `diff`, `insights` o `all`. Los bytes de vista previa son una muestra limitada, no un volcado de memoria ilimitado. |
| `--report-sections cpu,watched_memory` | Conserva las secciones indicadas del informe. `meta` y `schema_version` siguen presentes. Los nombres desconocidos no crean secciones nuevas. |
| `--report-minimal cpu,watched_memory` | Otra opción para indicar la lista de secciones, con prioridad sobre `--report-sections`. Requiere valores separados por comas; no es un interruptor booleano. |

Las direcciones y los tamaños aceptan decimal o hexadecimal con `0x`. Localice las variables mediante los símbolos de la compilación actual; 0xC700 es solo una dirección de ejemplo, no una ubicación estándar del jugador.

{{COMMAND:4}}

### 13.6 Detenerse por condiciones de ejecución o eventos del hardware

| Opción | Sintaxis y finalidad |
| --- | --- |
| `--breakpoint "pc:0x0150"` | Se detiene en una dirección de CPU. `symbol:main` utiliza símbolos; añada `@bank:2` para limitar el banco. |
| `--watchpoint "player@0xC700+4"` | Se detiene ante escrituras en una región de cuatro bytes. El prefijo opcional da nombre al punto de vigilancia; si se omite `+size`, se vigila un byte. |
| `--stop-on-mmio "scroll@0xFF43"` | Se detiene al escribir en el registro MMIO indicado, SCX en este caso. |
| `--stop-on-irq "vblank:serviced"` | Selecciona una fuente de interrupción y una fase: `requested`, `serviced`, `blocked` o `any`. Una fase sin fuente coincide con cualquier fuente. |
| `--stop-on-dma oam_start` | Selecciona un evento DMA. Nombres admitidos: `oam_start`, `oam_complete`, `hdma_start`, `hdma_block`, `hdma_complete`, `hdma_cancel`, `gdma_stall`, `hdma_deferred`, `hdma_ignored`. |
| `--run-until "frame=60&&frame_end"` | Se detiene cuando coinciden todos los términos de una condición de observación. Repita la opción para añadir solicitudes. |

Los marcadores de punto de interrupción `pc:`, `symbol:` y `@bank:` distinguen mayúsculas de minúsculas. Las direcciones de memoria y los bancos usan decimal o hexadecimal con `0x`. Mantenga un límite de fotogramas aunque solicite una parada cuya condición podría no producirse nunca.

Las condiciones de observación usan `&&` como AND; no son expresiones de C. Los términos admitidos son `frame=`, `ly=`, `pc=`, `bank=`, `bank_pc=bank:pc`, `symbol=`, `source=`, `event=`, `ppu_mode=` (o `mode=`) y `basis=`. Los valores de fotograma y LY son decimales. Los términos de símbolo, origen y evento comparan texto. Los valores de basis incluyen `frame_start`, `frame_end`, `step`, `event`, `trace`, `snapshot`, `stop`; también se aceptan los términos independientes `frame_start`, `frame_end`, `stop` y `vblank`. Comparaciones como `hp<10` no forman parte de esta gramática.

{{COMMAND:5}}

Use el primer comando para examinar el punto de entrada y el segundo para identificar el código que cambia el desplazamiento horizontal. Compruebe si se produjo realmente la parada solicitada.

### 13.7 Registrar puntos de observación y comparar ejecuciones

| Opción | Finalidad |
| --- | --- |
| `--trace-point "frame=30&&frame_end"` | Registra una observación cuando se cumple la condición. Repita la opción para varios puntos. |
| `--timeline-out out/timeline.jsonl` | Guarda la cronología de observaciones. |
| `--trace-jsonl out/timeline.jsonl` | Otro destino para la cronología, con prioridad sobre `--timeline-out`. No solicita una traza exhaustiva de todas las instrucciones. |
| `--timeline-format jsonl` | Selecciona `jsonl` (predeterminado) o `csv`; elija usted mismo la extensión correspondiente. |
| `--replay-interval 1` | Habilita los puntos de control de reproducción y elige el intervalo en fotogramas. |
| `--replay-max-checkpoints 120` | Limita los puntos de control conservados; el valor predeterminado es 16, con un intervalo de 1. |
| `--rewind-on-stop-frames 10` | Solicita retroceder después de una parada usando el historial de reproducción conservado. |
| `--stop-on-divergence` | Habilita el comportamiento de parada por divergencia del controlador de reproducción. |
| `--dump-replay-tape out/baseline.json` | Exporta los datos de reproducción registrados. Debe habilitar su registro para generarlos. |
| `--compare-replay-tape out/baseline.json` | Compara con datos de reproducción exportados. Use la misma ROM, entradas y estado inicial para una comparación determinista. |
| `--compare-replay-watch-only` | Restringe la comparación a las observaciones de memoria vigilada, sin tratarla como una comparación completa de la máquina. |
| `--snapshot-on-replay-mismatch out/mismatch` | Proporciona un prefijo para los archivos de investigación cuando la comparación detecta una diferencia. |

{{COMMAND:6}}

Compruebe el resultado de la comparación y la primera diferencia en el informe. Generar ambos archivos no basta para que la comparación se considere superada.

### 13.8 Diagnósticos e investigación reproducible

| Opción | Comportamiento real |
| --- | --- |
| `--emit-diagnostics out/events.jsonl` | Exporta eventos de diagnóstico para SARAKURA. |
| `--diagnostics-jsonl out/events.jsonl` | Otro destino de diagnóstico para ejecuciones directas; `--emit-diagnostics` tiene prioridad. |
| `--repro-bundle out/repro.zip` | Empaqueta un informe, eventos de diagnóstico y un manifiesto. La ROM y los metadatos se referencian por ruta, sin incorporarse al paquete; las capturas, estados y trazas no se incluyen automáticamente. |
| `--break-on-diagnostic all` | Examina los diagnósticos del informe final para capturar archivos de investigación. Esto **no** detiene la CPU en la primera instrucción problemática. Con cualquier filtro no vacío, cualquier diagnóstico final puede activar la ruta de captura. |
| `--png-on-diagnostic out/diagnostic-images` | Directorio de la pantalla final de diagnóstico, usado con la captura de diagnósticos. El archivo se llama `diagnostic_000001.png`. |
| `--snapshot-on-diagnostic out/diagnostic-states` | Directorio de destino para `diagnostic_000001.kqs`. Estas capturas reflejan el estado final actual, no el instante original de cada evento. |
| `--diagnostic-pack NAME` | Se acepta el argumento, pero la ruta de ejecución no aplica un paquete de diagnósticos. |
| `--diagnostic-rule RULE` | Se acepta y puede repetirse, pero la ruta de ejecución no aplica esta selección de reglas. |
| `--diagnostic-summary-limit N` | Se acepta el argumento, pero la ruta de ejecución no aplica este límite al resumen. |

{{COMMAND:7}}

Para detenerse en una instrucción o escritura concreta, use las opciones del depurador de 13.6. Interprete los diagnósticos en su contexto: una pantalla de título deliberadamente inactiva puede producir observaciones que no son defectos del juego.

### 13.9 Desensamblar instrucciones o examinar pseudocódigo

| Opción | Sintaxis y finalidad |
| --- | --- |
| `--disassemble-out out/code.txt` | Decodifica las instrucciones de la ROM sin ejecutar la tarea normal de emulación. |
| `--disassemble-range "0:0100-0150"` | Selecciona `BANK:START-END`; repita la opción para más intervalos. **Los tres números son hexadecimales**, incluso sin `0x`. |
| `--disassemble-format text` | `text` (predeterminado), `markdown` o `json`. |
| `--decompile-out out/functions.json` | Genera pseudocódigo e información de flujo de control. |
| `--decompile-format json` | `json` (predeterminado), `markdown` o `text`. |
| `--decompile-function main` | Selecciona una función; repita la opción para más funciones. Los símbolos correspondientes mejoran su identificación. |
| `--decompile-all` | Incluye todas las funciones con nombre conocidas por el descompilador. |
| `--decompile-annotations out/annotations.json` | Lee anotaciones en el formato JSON del descompilador. |
| `--decompile-trace out/trace.json` | Lee metadatos de traza del descompilador; un registro JSONL de diagnóstico cualquiera no los sustituye. |

{{COMMAND:8}}

El desensamblado sirve para comprobar las instrucciones generadas; el pseudocódigo ayuda a recorrer el flujo de control. Ninguno recupera exactamente el programa C original. Conserve los símbolos y metadatos de la misma compilación de la ROM.

### 13.10 Ejecutar varias máquinas conectadas

| Opción | Sintaxis y finalidad |
| --- | --- |
| `--link-job out/pair.json` | Lee la topología y las sesiones de una tarea de enlace JSON; las rutas relativas se resuelven desde el directorio de la tarea. |
| `--link-topology pair` | Selecciona `pair`, `four_player_adapter` o `dmg07` para las sesiones definidas en la línea de comandos. |
| `--link-session SPEC` | Añade una sesión. Se requieren al menos dos. En PowerShell, encierre entre comillas toda la cadena cuyos campos están separados por barras verticales. |
| `--link-initial-peer-slot 1` | Elige el interlocutor inicial cuando la topología permite seleccionarlo. |

Los campos de sesión incluyen `name`, `slot`, `rom`, `symbols`, `source_map`, `toolchain_metadata`, `load_state`, `save_state`, `input`, `input_sequence`, `audio_buffer_frames` y `watch_window`. `rom` es obligatorio. Un campo de vigilancia puede contener varias regiones separadas por comas, como `a:0xC700:4,b:0xC710:4`. Use programas que realmente intercambien datos serie: dos pantallas en ejecución no demuestran por sí solas que exista comunicación.
