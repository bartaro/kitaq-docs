## CLI de Windows ya compilada
La raíz del repositorio incluye `kurosaki.exe`. Descarga el ZIP y conserva los avisos de licencia con el ejecutable. La CLI para Windows x64 no requiere Rust, Python ni .NET para ejecutarse. Los pasos de compilación son para reconstruirla desde las fuentes. El código independiente está licenciado por DAISUKE OBA bajo MIT; las dependencias conservan sus condiciones en `BINARY_NOTICES.md` y `licenses/`.

## 1. Para qué sirve KUROSAKI
KUROSAKI es un emulador de observación NES/Famicom/FDS que interpreta información de KITAQFC. Su CLI inspecciona ROM, ejecuta software, graba audio, diagnostica, guarda estados, reproduce entradas, desensambla y descompila funciones candidatas. Los mappers tienen distintos grados de implementación; comprueba primero la ROM y la información de soporte.

## 2. Compilar y empezar
{{CODE:0}}

Los comandos abreviados `kurosaki` suponen que la carpeta del ejecutable está en PATH. Si no, usa `& "ruta completa del ejecutable"`.

{{CODE:1}}

Comprueba el texto con la ROM hello del volumen 4. `inspect-rom` analiza el encabezado; `run` avanza CPU y PPU. Inspeccionar correctamente no garantiza ejecutar correctamente.

## 3. Revisar mapper y placa
`mapper-list` enumera tipos registrados, `mapper-info` describe uno y `audit-board` comprueba restricciones de placa. El número de mapper relaciona el encabezado con supuestos de cableado físico. El nombre por sí solo no demuestra capacidad, presencia de CHR-RAM ni comportamiento de bancos fijos.

{{CODE:2}}

`--allow-unimplemented` deja continuar la observación tras encontrar partes no implementadas. Una ejecución con esta opción no demuestra soporte de esas partes.

## 4. Entrada de mandos
`run --pad1` y `--pad2` usan máscaras NES sin procesar: A=1, B=2, SELECT=4, START=8, UP=16, DOWN=32, LEFT=64 y RIGHT=128. Suma los valores para pulsaciones simultáneas.

{{CODE:3}}

El ejemplo mantiene A durante 120 fotogramas. Para acciones ordenadas, como título, inicio y confirmación, utiliza reproducción de entrada. El ejemplo CLI `replay-record` registra una ejecución de referencia sin entrada interactiva; no equivale a grabar a una persona manejando una GUI.

## 5. Instantáneas y reproducción
{{CODE:4}}

Los estados reanudables usan instantáneas de versión 2. Mantén la correspondencia SHA-256 con la ROM. `snapshot-resume` continúa desde el punto guardado. `snapshot-rebase` traslada explícitamente el estado a otra ROM compatible según un contrato. No reutilices sin comprobación un estado después de cambiar código o distribución de RAM; lo habitual es repetir las acciones desde el arranque.

## 6. Trazas, diagnósticos y perfiles
{{CODE:5}}

La traza registra qué ocurrió y cuándo; los diagnósticos señalan observaciones que cumplen reglas; el perfil muestra dónde se concentró la ejecución. Unos pocos fotogramas alrededor de la anomalía suelen ser más útiles que una traza extensa.

Entrega el JSON de depuración de esa compilación con `--kitaqfc-debug`. Una observación sin líneas de código no debe tratarse como una traza completa a nivel de fuente.

## 7. Guardar sonido e imágenes
{{CODE:6}}

Cambios de registros, PCM generado y sonido correcto son comprobaciones distintas. Registra el mapper al probar audio interno o de expansión. Un PNG aislado no prueba movimiento ni entrada: conserva también controles y estados anteriores y posteriores.

## 8. Desensamblado y descompilación
{{CODE:7}}

`disasm` muestra instrucciones. `decompile` produce candidatos a límites de función, CFG, referencias y pseudocódigo. Con bancos conmutables, una dirección de CPU no identifica por sí sola la posición física de ROM. Aporta el estado del mapper con `--snapshot` cuando haga falta y contrasta con trazas o anotaciones. No es una recuperación perfecta de las fuentes originales.

## 9. Conectar con SARAKURA
{{CODE:8}}

Como en KOKURA, `--emit-diagnostics` de KUROSAKI recibe una **ruta de archivo JSONL**. Separa trazas de CPU y eventos de diagnóstico.

## 10. Alcance de la publicación
KUROSAKI-GUI sigue sin publicarse. Este manual se centra en la CLI y sus API de integración.

## 11. FDS y RAM de guardado
`fds-inspect` examina la estructura del disco y `export-assets` extrae recursos. Prueba FDS por separado de los cartuchos NES: arranque, BIOS y acceso al disco tienen otros requisitos. Los `.sav` de batería y las instantáneas `.kss.json` sirven a propósitos distintos. Usa una distribución de guardado admitida por la implementación.

{{CODE:9}}

`battery-export` obtiene RAM de guardado sin procesar de una ROM e instantánea coincidentes. `battery-run` carga esa RAM y arranca desde el encendido; no restaura la ejecución suspendida de CPU o PPU. Indica la salida con `--save-out`. Estas operaciones requieren una ROM compatible con RAM de guardado y no se aplican a todas las lecciones.
