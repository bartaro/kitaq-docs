# Manuales de KITAQ SERIES

[English](README.md#english) | [日本語](README.md#japanese) | **Español**

<!-- ai-prompts:start -->
## Prompts para desarrollar juegos con IA

Completa los requisitos y entrega el prompt íntegro a tu asistente de IA. Incluye implementación, pruebas en el emulador, análisis con SARAKURA y verificación de las correcciones.

KITAQGB · KITAQFC
<!-- ai-prompts:end -->

## Acceso directo al manual de cada herramienta

Estos enlaces abren directamente el volumen correspondiente en español.

| Volumen | Contenido |
| --- | --- |

## Manuales HTML

Los siete volúmenes están disponibles en nueve idiomas y describen el código fuente del 14 de septiembre de 2026. Todas las ediciones incluyen las mismas 1.055 entradas de API y 47 programas de ejemplo completos. Abra `es/index.html` en español, `en/index.html` en inglés o `index.html` en japonés. Puede cambiar de idioma desde cada volumen. Los registros de verificación identifican los fuentes, los ejecutables y las condiciones de las pruebas.

Los fragmentos de código originales y las salidas capturadas de las herramientas se conservan sin traducir. Consulte también la [obtención y organización de los repositorios](GITHUB_SETUP.md) y el [registro de comprobaciones de publicación](PUBLICATION_CHECKS.md). El HTML permite lectura sin conexión, búsqueda dentro de cada volumen, copia de código e impresión.

El índice y el comienzo del primer volumen explican el doble significado de KITAQGB y reconocen su origen en NORCAL. Las letras latinas, los números y los símbolos utilizan el archivo indicado, `samples/assets/ascii.c`. Los recursos de GB se reordenan según ASCII y los de FC se convierten al formato de planos de bits de NES, sin alterar la forma de los glifos.

El texto, los ejemplos adicionales y las herramientas de generación se ofrecen bajo la licencia MIT. El 12 de septiembre de 2026, el autor confirmó que los 92 glifos proporcionados son de creación propia y pueden publicarse bajo MIT. Los extractos de los programas originales conservan sus avisos de derechos de autor. Al redistribuirlos, adjunte los [avisos de terceros](THIRD_PARTY_NOTICES.md) y las licencias aplicables.

Se incluyen el [texto original de la licencia en inglés](LICENSE) y una [traducción japonesa de referencia](LICENSE.ja). Los [avisos de terceros](THIRD_PARTY_NOTICES.md) también enlazan las licencias japonesas de cada herramienta. En caso de discrepancia, prevalece el texto inglés. La distribución de binarios debe respetar además las licencias de sus dependencias: poder publicar estos manuales no implica que todas las herramientas y dependencias puedan redistribuirse únicamente bajo MIT.

## Compilar los ejemplos

Clone los repositorios como directorios hermanos dentro de un mismo directorio padre y ejecute los comandos siguientes desde ese directorio. La disposición se explica en [GITHUB_SETUP.md](GITHUB_SETUP.md). Puede utilizar los compiladores incluidos o recompilarlos según el manual; esta edición contiene correcciones de los compiladores.

```powershell
.\kitaq-docs\samples\build.ps1 -Only gb_hello,fc_hello
.\kitaq-docs\samples\build.ps1
```

Si el código fuente está en otra ubicación, indique `-Root "ruta absoluta del árbol de código"`. Las opciones `-GbCompiler` y `-FcCompiler` permiten seleccionar compiladores de otros directorios. Las ROM y los registros se guardan por defecto en `samples/out/<sample-id>`. Este paquete de manuales no incluye ejecutables de compiladores, ROM comerciales ni BIOS.

`samples/api-fragments` contiene fragmentos que deben integrarse en un programa ya inicializado y recibir argumentos válidos. La compilación por lotes de ROM abarca los 47 programas completos de `samples/manifest.json`. Los volúmenes distinguen las API que solo tienen declaración, los fragmentos no ejecutados y las funciones sin verificación en hardware real.

## Publicar en GitHub

1. Coloque el contenido de este directorio en la raíz del repositorio o en `docs`.
2. Suba juntos `index.html`, los siete volúmenes, `verification.html`, `loop-engineering.html`, `prompts`, los directorios de idiomas, `assets`, `samples`, `reference`, `verification`, los README y los avisos de licencia. Incluya `.nojekyll`.
3. En GitHub, abra Settings → Pages → Build and deployment y seleccione Deploy from a branch como Source.
4. Elija la rama que ha subido y `/ (root)` o `/docs`, según la ubicación de los archivos, y guarde la configuración.
5. Cuando termine la publicación, abra la dirección indicada en Pages y compruebe los enlaces del índice y de cada volumen.

Consulte la [documentación de GitHub sobre el origen de publicación](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site). `manual/_manual_work` es un espacio local de compilación y verificación; no forma parte de la publicación.

## Editar y actualizar

El texto japonés está en `tools/chapters.py` y el inglés en `tools/en/*.md`. `tools/generate_en.py` genera la versión inglesa; `tools/generate.py` contiene el diccionario de API y la lógica de generación de páginas. Los estilos están en `assets/manual.css`. Para actualizar los manuales con Python:

```powershell
python -B kitaq-docs/tools/collect.py
python -B kitaq-docs/tools/make_samples.py
python -B kitaq-docs/tools/catalog.py
python -B kitaq-docs/tools/generate.py
python -B kitaq-docs/tools/generate_en.py
foreach ($language in @('ko','zh-CN','zh-TW','es','pt','fr','de')) {
    python -B kitaq-docs/tools/generate_i18n.py --language $language
    if ($LASTEXITCODE -ne 0) { throw "Manual generation failed: $language" }
}
python -B kitaq-docs/tools/check_site.py
python -B kitaq-docs/tools/check_bilingual.py
```

Las capturas acompañan las explicaciones de los ejemplos. Los archivos públicos no incluyen registros de compilación, de ejecución ni de verificación local. Antes de subirlos, use `tools/export_public.py` para exportar el manual a una copia de trabajo de Git independiente. Consulte los [avisos de terceros](THIRD_PARTY_NOTICES.md).

## Alcance de esta publicación de código fuente

KOKURA-GUI, KUROSAKI-GUI y PLITA no se subirán en esta ocasión. El código y los manuales públicos cubren las herramientas de línea de comandos, los núcleos y las API de integración.
