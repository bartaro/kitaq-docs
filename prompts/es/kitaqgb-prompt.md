# Desarrollo de juegos con KITAQGB, KOKURA y SARAKURA

Completa los requisitos y entrega este documento íntegro al asistente de IA. Los comandos suponen que los repositorios `kitaqgb`, `kitaqfc`, `kokura`, `kurosaki`, `sarakura` y `kitaq-docs`, junto con el proyecto `game-gb` o `game-fc`, comparten un directorio padre. Ejecútalos desde ese directorio y adapta las rutas al entorno real.

## Requisitos

- Título del juego: <completar>
- Género y mecánica principal: <completar>
- Controles y condiciones de éxito y fracaso: <completar>
- Pantallas, niveles, enemigos y objetos obligatorios: <completar>
- Estilo visual, música y efectos de sonido: <completar e indicar los recursos proporcionados>
- Guardado, comunicación, periféricos y otros requisitos: <completar o ninguno>
- Directorio del proyecto: <completar>
- Condiciones de redistribución: <por ejemplo, código y recursos originales aptos para publicarse con licencia MIT>

- Máquina de destino: <Game Boy original / compatibilidad con GB y CGB / solo CGB>
- Rendimiento: <por ejemplo, 60 actualizaciones de la lógica por segundo durante el juego normal; definir lo aceptable en escenas exigentes>

## Trabajo solicitado

Implementa el juego con KITAQGB y sus bibliotecas. Utiliza KOKURA para ejecutar y depurar, y SARAKURA para organizar los diagnósticos y comparar los resultados antes y después de una corrección.

Repite este ciclo hasta cumplir los criterios de aceptación: concretar la especificación → implementar un cambio pequeño → compilar → aplicar entradas y observar → investigar la causa → corregir → repetir las pruebas en las mismas condiciones. Un plan, un listado de código o una compilación correcta no bastan para dar el trabajo por terminado.

### Comprobar el entorno y los criterios de aceptación

1. Lee las instrucciones del directorio de trabajo, los README, los manuales HTML y las cabeceras e implementaciones de las bibliotecas que vayas a usar. Registra las rutas de los ejecutables y sus versiones o hashes SHA-256. Comprueba los comandos con la salida real de `--help` y las API con el código fuente.
2. Define criterios verificables para entradas, imagen, sonido, progreso y frecuencia de actualización. Por ejemplo: pulsar y soltar START inicia la partida; una colisión resta una vida; la pausa silencia el audio indicado y al continuar se reanuda la reproducción.
3. Pregunta solo por ambigüedades importantes. Resuelve de forma autónoma las decisiones habituales y reversibles. No rebajes los requisitos ni los criterios de aceptación.
4. Primero ejecuta un pequeño ejemplo incluido con el compilador, el emulador y SARAKURA. Esto comprueba la conexión entre herramientas, no la finalización del juego solicitado.

### Implementar una primera versión jugable

- Utiliza el dialecto C de KITAQGB y `void main()`. No des por disponibles las API de C de escritorio o GBDK. Incluye los archivos `.c` necesarios, no solo sus declaraciones; comprueba inicialización, unidades, signo, rangos, vida útil de los búferes y bancos ROM.
- Planifica las actualizaciones de VRAM/OAM, VBlank, interrupciones, pila, bancos ROM/WRAM y límites de tiles y sprites. La capacidad total y libre de la cola de transferencias es distinta de la capacidad y el espacio libre de la VRAM física.
- Un juego para DMG no debe depender de funciones exclusivas de CGB. Si admite ambos modos, pruébalos por separado.
- Para letras, números y símbolos, utiliza la fuente original proporcionada en `ascii.c` y comprueba la correspondencia entre caracteres y tiles.

- Conecta primero arranque, título, personaje controlable, éxito o fracaso y reinicio. Amplía el contenido después.
- Conserva los originales editables de gráficos, música y efectos, así como los pasos de generación. Comprueba que la compilación consume realmente los datos exportados.
- Escribe los comentarios del código en inglés y los informes de progreso en español. Mantén los informes estándar de SARAKURA en inglés.

### Vincular cada compilación con su ejecución

Separa las salidas por iteración, por ejemplo en `out/iter-001`. Registra comandos, códigos de salida y hashes de código, recursos, herramientas, ROM y metadatos. Nunca ejecutes una ROM anterior después de una compilación fallida. Los mapas, mapas de código fuente y datos de depuración deben corresponder a la misma compilación que la ROM.

Este es un ejemplo de comprobación básica para DMG. Prepara `main.c` y las implementaciones de biblioteca necesarias; adapta opciones y secuencia de entrada al juego.

```powershell
$iteration = '.\game-gb\out\iter-001'
New-Item -ItemType Directory -Force $iteration | Out-Null

# Include all additional implementation units required by the game.
& '.\kitaqgb\kitaqgb.exe' '.\game-gb\src\main.c' `
  -I '.\kitaqgb\lib' -o "$iteration\game.gb" `
  --profile=dev --rst-disable --stack-bank=fixed --no-disasm `
  "--emit-ai-metadata=$iteration\build.json"
if ($LASTEXITCODE -ne 0) { throw 'Build failed; inspect the build log.' }

# This sequence presses START once, with released intervals on both sides.
& '.\kokura\kokura-cli.exe' "$iteration\game.gb" `
  --hardware dmg --run-frames 300 `
  --input-seq 'NONE:60;START:1;NONE:239' `
  --png "$iteration\frame.png" --record-wav "$iteration\audio.wav" `
  --dump-report "$iteration\run.json" `
  --emit-diagnostics "$iteration\events.jsonl"
if ($LASTEXITCODE -ne 0) { throw 'Emulator run failed; inspect the run log.' }

& '.\sarakura\sarakura.exe' gb analyze `
  --metadata "$iteration\build.json" --events "$iteration\events.jsonl" `
  --frames 300 --out "$iteration\analysis" --fail-on error
if ($LASTEXITCODE -ne 0) { throw 'Inspect the analysis report and fix the cause.' }
```


`--hardware dmg` selecciona la Game Boy original. Al probar CGB o ambos modos, ajusta de forma coherente la cabecera ROM y el hardware del emulador. La secuencia pulsa START una vez entre intervalos con los botones sueltos. Ejecutar 300 fotogramas no equivale a probar el juego completo.

### Comprobar imagen, sonido, estado y rendimiento

- Guarda escenarios que distingan pulsar, mantener y soltar. Recorre todas las rutas especificadas: arranque, inicio, movimiento, acciones, colisiones, desplazamiento, cambios de nivel, fin de partida, reinicio, pausa y, cuando corresponda, guardado o comunicación.
- Conserva PNG de fotogramas relevantes, entradas, informes de ejecución, JSONL de diagnóstico, WAV y las observaciones necesarias de estado o memoria. Comprueba los fotogramas alcanzados y el motivo de parada. Abre las imágenes: una sola captura no demuestra movimiento ni respuesta a los controles. Compara contadores, posiciones y cambios de estado con lo esperado; revisa bordes de pantalla, límites de tiles y atributos, y escenas con muchos sprites.
- Comprueba música, efectos, reproducción simultánea, cortes, pausa y reanudación. Crear un WAV no demuestra que el sonido sea correcto. Si no puedes escucharlo, distingue las comprobaciones numéricas o de forma de onda de las cualidades audibles aún sin verificar.
- Mide escenas exigentes, trabajo de la CPU de destino, actualizaciones y transferencias; en FC, incluye el trabajo de NMI. La velocidad del emulador en el equipo anfitrión no es la frecuencia del juego ni prueba la velocidad en hardware real. Continuar con `--allow-unimplemented` no demuestra soporte para la función ausente.

### Analizar, corregir y volver a probar

- Proporciona a SARAKURA los metadatos de la ROM probada y el JSONL de diagnóstico de esa ejecución. Una traza CPU o un informe ordinario no los sustituyen. `--frames` establece condiciones de análisis; SARAKURA no ejecuta la ROM ni modifica automáticamente el código.
- Lee `report.html`, `ai_diagnostics.json`, `repair_prompt.md` y `retest_plan.json`. Contrasta los diagnósticos con reproducción, imágenes, audio y código. Distingue ubicaciones o causas inferidas de hechos comprobados, y bucles de espera normales de bloqueos. Evalúa las advertencias una por una y registra eventos no soportados o límites del análisis. No ocultes advertencias con filtros ni acortes las pruebas para conseguir un resultado favorable.
- Reduce cada fallo a un caso mínimo, corrige su causa y recompila. Si procede del compilador o emulador, aísla el defecto del código del juego y añade comprobaciones de regresión para la corrección de la herramienta.
- Repite las pruebas con las mismas entradas, semilla aleatoria, máquina y norma de vídeo, mapper, fotogramas observados y ajustes de diagnóstico. Cada ROM requiere sus metadatos; no reutilices estados guardados a ciegas tras cambiar código o distribución de RAM.

```powershell
& '.\sarakura\sarakura.exe' baseline-delta `
  --baseline '.\game-gb\out\iter-001\analysis' `
  --current '.\game-gb\out\iter-002\analysis' `
  --out '.\game-gb\out\delta.json' --markdown '.\game-gb\out\delta.md' `
  --fail-on-new error --fail-on-regression error --enforce
```


Usa las diferencias de diagnóstico junto con la aceptación de controles, gráficos y audio. Si el mismo fallo se repite, revisa las pruebas y la hipótesis en lugar de encadenar cambios arbitrarios.

### Criterios de finalización y entregables

Repite todos los escenarios obligatorios con la ROM final compilada a partir del código y los ajustes entregados. La invencibilidad, entradas automáticas de prueba u otro mapper, por sí solos, no verifican una partida normal en la versión final. Entrega una tabla de requisitos y pruebas, explica las advertencias restantes e identifica lo no comprobado o no soportado. Si no se ha probado en hardware físico, indícalo explícitamente.

Entrega código fuente, identificación de herramientas y bibliotecas, recursos editables, scripts reproducibles de compilación y pruebas, ROM, evidencia final y un README de instalación, controles y limitaciones conocidas. Incluye reproducciones y el programa de pruebas cuando sean necesarios. Publica o envía archivos al exterior solo dentro del alcance autorizado expresamente. Elimina compilaciones intermedias y trazas temporales innecesarias tras verificarlas, conservando fuentes, recursos, entregables y evidencia de regresión necesaria.

Si el entorno o los permisos impiden una comprobación obligatoria, comunica los pasos exactos de reproducción y la acción necesaria. No des el trabajo por terminado.
