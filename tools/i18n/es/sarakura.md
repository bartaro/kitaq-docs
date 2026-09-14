## Ejecutable de consola para Windows
El repositorio incluye `sarakura.exe` en su raíz. Descarga el ZIP del repositorio y conserva los avisos de licencia junto al ejecutable. Esta herramienta de consola para Windows x64 no necesita Rust, Python ni .NET para ejecutarse. Los pasos siguientes sirven para volver a compilarla desde el código fuente. El código propio del proyecto se distribuye bajo la licencia MIT de DAISUKE OBA; las condiciones de las dependencias se conservan en BINARY_NOTICES.md y licenses/.

## 1. Para qué sirve SARAKURA
SARAKURA combina información de compilación con eventos de diagnóstico del emulador y los presenta de forma que ayuden a investigar reparaciones y repetir pruebas. No ejecuta ROM como un emulador ni modifica silenciosamente tu código C.

## 2. Compilar la herramienta
{{CODE:0}}

Los comandos abreviados `sarakura` suponen que el ejecutable está en PATH. Si no es así, utiliza su ruta. Elige `gb analyze` para GB o `fc analyze` para FC.

## 3. Tu primer análisis
Se necesitan dos entradas: `--metadata` es un JSON generado durante la compilación y `--events` es un JSONL de eventos de diagnóstico registrados durante la ejecución. JSONL contiene un objeto JSON por línea.

{{CODE:1}}

Abre el archivo de salida `report.html` en un navegador. Antes de leer los diagnósticos individuales, comprueba la plataforma, los fotogramas observados y los recuentos de errores y advertencias. `--frames` describe las condiciones del análisis; no ordena a SARAKURA ejecutar la ROM durante ese número de fotogramas.

## 4. Revisar primero las entradas
{{CODE:2}}

Descarta primero archivos ilegibles, plataformas que no coinciden y tipos de evento no admitidos. Pasar un informe ordinario del emulador como archivo de eventos no lo convierte en una entrada de diagnóstico válida.

## 5. Interpretar los diagnósticos
Un error merece atención prioritaria; una advertencia puede señalar un problema según las circunstancias; y un elemento informativo aporta contexto. La gravedad ayuda a ordenar la investigación, pero no interpreta por completo la intención del juego. Observar que se repite el contador de programa no siempre permite distinguir un bucle de espera normal de la pantalla de título de un bloqueo.

Compara el hash de la ROM, la secuencia de entrada, la escena, la imagen, el sonido y la ubicación en el código fuente. Mantén las mismas condiciones antes y después de una corrección: una reducción de los diagnósticos podría deberse simplemente a que se ejecutó otra escena.

## 6. Archivos de salida
Las explicaciones incorporadas, las sugerencias de diagnóstico y las instrucciones de reparación se generan en inglés; el HTML declara `lang="en"`. Las cadenas del usuario y los identificadores de eventos no se traducen automáticamente. La ocultación predeterminada sustituye determinadas etiquetas y rutas del proyecto, pero no anonimiza todas las direcciones ni todas las observaciones. Revisa los informes antes de publicar un análisis de datos privados.

| Archivo | Finalidad |
| --- | --- |
| ai_diagnostics.json | Diagnósticos normalizados para procesamiento automático |
| diagnostic_summary.json | Recuentos y resumen |
| report.html | Informe para su lectura en el navegador |
| repair_prompt.md | Contexto inicial para investigar una reparación |
| repair_plan.json / .md | Orden y objetivos de las reparaciones |
| automation_plan.json / .md | Plan de trabajo según las capacidades de las herramientas |
| retest_plan.json | Plan para repetir las comprobaciones |
| repro_bundle.zip | Paquete de información para reproducir el problema |

Generar un plan no equivale a ejecutarlo. Después de modificar el código C o una ROM, vuelve a ejecutar el compilador, el emulador y SARAKURA.

## 7. Catálogos, filtros y cobertura
{{CODE:3}}

`catalog` enumera las reglas de diagnóstico; `pack-plan` las agrupa por área; y `coverage` examina cuáles de sus eventos correspondientes se observaron. Que una regla figure en el catálogo no garantiza que el emulador actual emita ese evento.

{{CODE:4}}

`--diagnostic-rule` selecciona un nombre de evento o un identificador del catálogo; `--phase`, una fase; y `--diagnostic-pack`, un área. Ocultar un diagnóstico mediante un filtro no resuelve su causa.

## 8. Comparar el antes y el después
{{CODE:5}}

Los resultados se clasifican como nuevos, resueltos, mejorados, persistentes o empeorados. Distingue los problemas que siguen presentes de los que se han introducido con el cambio. Mantén fijos la entrada, el número de fotogramas y los filtros de diagnóstico durante la comparación.

## 9. Validación e integración continua
{{CODE:6}}

La integración continua automatiza comprobaciones reproducibles. `ci-summary` solo modifica el código de salida del proceso cuando se indica `--enforce`; en caso contrario, lee el veredicto de su JSON. En analyze, `--fail-on error` devuelve un código distinto de cero si se detectan errores. El valor predeterminado `never` no hace fallar el proceso por los diagnósticos, así que escoge expresamente la política que quieras aplicar en CI. Con `warn`, las advertencias también provocan un fallo.

```powershell
sarakura ci-summary --diagnostics .\out\report --fail-on error --enforce
if ($LASTEXITCODE -ne 0) { throw "The diagnostic failure condition was met" }
```

Validar correctamente el esquema comprueba el formato de los datos. Para verificar que el juego funciona como se pretende también hacen falta pruebas de entrada, imagen y sonido.

## 10. Gestionar los archivos de reproducción
`normalize-events` normaliza los registros de eventos. `inspect-repro` examina un paquete de reproducción. Antes de compartirlo, comprueba que sus datos correspondan a la ROM prevista y que incluya los pasos de entrada necesarios. `--allow-project-labels` conserva expresamente las etiquetas y los identificadores derivados del proyecto.

## 11. Entradas mínimas para practicar
El manual incluye pequeños ejemplos de metadatos de compilación y eventos para GB y FC. Abre el [informe sintético de GB](verification/sarakura-gb-synthetic.html) o el [informe sintético de FC](verification/sarakura-fc-synthetic.html). `samples/sarakura_demo.ps1` muestra cómo analizarlos. Son entradas sintéticas para aprender el formato, no registros obtenidos de una ROM real. Para probar una ROM real, utiliza eventos registrados por KOKURA o KUROSAKI.

## 12. Un ciclo de corrección y prueba
1. Reproduce el problema con la misma ROM y la misma entrada; conserva los registros y las imágenes.
2. Organiza las posibles causas con SARAKURA y examina el código pertinente.
3. Realiza un cambio concreto que aborde la causa.
4. Vuelve a compilar y repite las mismas acciones.
5. Compara baseline-delta con las imágenes, el audio y el comportamiento del juego.

Mantén este ciclo acotado para poder entender cada cambio y su efecto.
