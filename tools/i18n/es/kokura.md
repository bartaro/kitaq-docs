## CLI de Windows ya compilada
La raíz del repositorio incluye `kokura-cli.exe`. Descarga el ZIP y conserva los avisos de licencia junto al ejecutable. Esta CLI para Windows x64 no necesita Rust, Python ni .NET para ejecutarse. Los pasos de compilación siguientes sirven para reconstruirla desde las fuentes. DAISUKE OBA licencia el código independiente bajo MIT; las condiciones de las dependencias figuran en `BINARY_NOTICES.md` y `licenses/`.

## 1. Para qué sirve KOKURA
KOKURA emula software GB/CGB y registra imágenes, audio, ejecución de CPU, memoria, bancos, entrada y eventos de diagnóstico. El ejecutable de línea de comandos se llama `kokura-cli.exe`.

## 2. Compilar y ejecutar la primera ROM
{{CODE:0}}

Instala Rust y Cargo. Si solo necesitas la CLI, compila el crate indicado. Usa la ROM hello del volumen 1. El valor predeterminado es un fotograma; establece `--run-frames` para llegar a la escena deseada. Son fotogramas emulados, no segundos de espera real.

## 3. Elegir DMG o CGB
`--hardware auto` es el valor predeterminado; `dmg` y `cgb` fuerzan un modo. Prueba las ROM de modo dual en ambos. Que una ROM exclusiva de CGB rechace arrancar como DMG no demuestra por sí solo un fallo del emulador.

{{CODE:1}}

## 4. Proporcionar controles
`--input` mantiene pulsada una combinación y `--input-seq` define acciones a lo largo del tiempo. Los botones son `A,B,START,SELECT,UP,DOWN,LEFT,RIGHT`; `NONE` indica que se sueltan. En PowerShell, encierra entre comillas las secuencias con punto y coma.

{{CODE:2}}

Incluye intervalos sin pulsación para probar flancos de entrada. Mantener A durante 120 fotogramas no equivale a pulsarlo 120 veces. En la lección del contador, la secuencia anterior debe incrementarlo una sola vez.

## 5. Imágenes, vídeo y sonido
`--png` guarda la pantalla final. `--screenshot` y `--screenshot-frames` capturan fotogramas concretos. `--record-video` graba vídeo y `--record-wav` graba audio. Un WAV silencioso es normal si el programa hello no utiliza la APU.

{{CODE:3}}

Los intervalos usan `start:end`. Conserva el informe para distinguir los fotogramas acumulados en un estado cargado de las posiciones de esta ejecución. Comprueba por separado sonido audible, afinación, interrupciones y saturación. La grabación del emulador no demuestra igualdad muestra a muestra con la consola física.

## 6. Guardar y reanudar estados
{{CODE:4}}

Normalmente debes usar la misma ROM y versión del emulador. Un estado de emulación no es el archivo de guardado propio del juego. El KQS de la CLI y el estado JSON de la API C son formatos diferentes; cambiar la extensión no los convierte.

## 7. Observar símbolos y memoria
Los archivos `.map`, `.source_map.txt`, `.dbg2.json` y `.build_report.json` pueden detectarse junto a la ROM. Conserva los correspondientes a esa compilación; mezclar archivos de otra versión puede inducir a error.

{{CODE:5}}

`wram` es el nombre de la ventana de observación, 0xC000 su inicio y 0x40 su longitud. Las ventanas pequeñas facilitan reconocer variables que cambian. `--watch-baseline-mode` compara con valores iniciales, el fotograma anterior o una referencia con nombre.

## 8. Paradas, reproducción y análisis inverso
`--breakpoint`, `--watchpoint`, `--run-until` y `--snapshot-at` detienen o guardan según condiciones. Sus minilenguajes de argumentos son distintos: consulta la referencia y la ayuda capturada.

{{CODE:6}}

Localiza la primera divergencia y estrecha después el intervalo observado. `--decompile-out` genera pseudocódigo y flujo de control; `--disassemble-out`, instrucciones de CPU. La descompilación no recupera perfectamente el C original ni los nombres de variables.

## 9. Enviar diagnósticos a SARAKURA
{{CODE:7}}

`--emit-diagnostics` de KOKURA recibe un **nombre de archivo JSONL**, por ejemplo `out/gb_events.jsonl`. Un informe JSON normal o una traza de CPU en JSONL no son entradas equivalentes de eventos de diagnóstico.

## 10. Trabajos de comunicación
`pair` modela dos máquinas; `four_player_adapter`, una topología lógica en la que el anfitrión selecciona al interlocutor; `dmg07`, el protocolo del adaptador físico DMG-07. Proporciona el trabajo JSON con `--link-job` o configura las sesiones con `--link-topology` y `--link-session`.

{{CODE:8}}

Cada ROM debe implementar la comunicación. Ejecutar dos programas hello corrientes no prueba la biblioteca de enlace. Registra ROM, ranura, entrada y estado de cada sesión, y distingue qué comportamiento físico sigue sin comprobarse.

## 11. Aplicaciones externas
La ABI C publicada está en `kokura-capi`. Python puede acceder mediante el puente y el crate suministrados. Antes de investigar la integración, prepara una reproducción mínima desde la CLI.

## 12. Leer los informes en orden
Empieza por los fotogramas ejecutados y el motivo de parada; continúa con pantalla, entrada, sonido, errores y avisos, y perfil de ejecución. Una pantalla de título sin entrada durante mucho tiempo puede producir avisos legítimos de imagen estática o PC repetido. Interprétalos según la escena prevista, no como fallos automáticos.
