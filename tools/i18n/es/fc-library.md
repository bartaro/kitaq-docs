## 1. Elegir los componentes
`fc.h` reúne declaraciones, `core.h` define tipos e `intrinsics.h` declara operaciones del compilador. Las funciones C normales necesitan su implementación `.c`. Las macros de encabezado y las operaciones intrínsecas pueden no necesitar un archivo del mismo nombre.

{{CODE:0}}

No apuntes `-I` a la biblioteca GB de nombre parecido. Por ejemplo, `__oam_dma()` de NES no recibe argumentos; la operación GB recibe un puntero.

## 2. Runtime y system
`runtime.c` ofrece funciones C para los registros PPU, la copia de OAM en RAM y las colas VRAM. También existen rutas intrínsecas como `__vramq_*`. Comprueba qué datos consume la NMI antes de mezclar colas diferentes con nombres semejantes.

`system_init` inicializa los fotogramas y activa NMI. `system_wait_vblank` espera NMI e incrementa el contador de software. **En FC, `system_set_vblank_callback` guarda el valor, pero la función de espera actual no ejecuta el callback.** No concentres allí toda la actualización suponiendo que funciona como en GB.

## 3. PPU, tiles, atributos y paletas
`ppu_direct.h` ofrece acceso directo; `vram_queue.h`, actualizaciones por NMI; `tilemap` / `nametable_asset`, tablas y recursos; `attribute`, atributos; `palette`, paletas. Separa la carga inicial del trabajo por fotograma.

Las paletas de fondo y sprites ocupan 16 bytes cada una. Sus valores son códigos de color NES, no componentes RGB. Los atributos eligen colores para grupos de tiles: cambiar la paleta aparente de uno puede afectar a sus vecinos.

Algunas declaraciones de `ppu.h` no coinciden con nombres de implementación de `ppu.c`. Las entradas marcadas **solo declaración** no tienen un cuerpo localizado en las fuentes recogidas y no se llaman directamente en los ejemplos iniciales. Las lecciones ejecutables usan operaciones verificadas. Una declaración no demuestra que la función esté terminada ni que pueda enlazarse.

## 4. OAM, metasprites y reparto de visibilidad
NES admite hasta 64 sprites, normalmente ocho por línea de barrido. Nueve enemigos o proyectiles alineados no pueden verse todos a la vez. Los metasprites unen varios OBJ en una imagen; comprueba límites de asignación y formatos de terminación.

`oam_fair.h` y `oam_fair_impl.h` rotan el orden de candidatos manteniendo prioridades. Pueden dar preferencia al jugador o HUD y alternar objetos secundarios. Reordenar OAM no eleva el límite de hardware por línea.

## 5. Entrada, repetición y periféricos
`input.c` convierte los botones NES sin procesar en máscaras `BTN_*` al estilo GB. **A en NES vale 0x01; BTN_A en la biblioteca vale 0x10.** No pases BTN_A directamente a `--pad1` de KUROSAKI.

`pad` lee el mando y `input_repeat` gestiona la repetición al mantener pulsado. `zapper`, `keyboard`, `rob`, `mic` y `midi` exponen interfaces de bajo nivel. Leer cero de un dispositivo desconectado no demuestra que funcione: revisa sus requisitos de conexión.

## 6. Sonido
Después de `nes_apu_init`, utiliza `nes_sfx_square1`, `nes_sfx_square2`, `nes_sfx_triangle` o `nes_sfx_noise`. El argumento period es el periodo del temporizador, no una frecuencia en hercios. `fc_sound.c` es un ejemplo mínimo de tono de pulso.

Las muestras DMC tienen restricciones de dirección, longitud, alineación y frecuencia de muestreo. Revisa el mapa antes de pasar un puntero. DMC DMA también puede interferir con la lectura del mando; combina lecturas seguras con diagnósticos de KUROSAKI.

VRC6 aporta canales de pulso y diente de sierra; VRC7, registros FM; FDS, síntesis por tabla de ondas. Usa el mapper correspondiente y graba el resultado. Estas API son independientes del controlador `Audio_*` de GB.

## 7. Escenas, actores y entidades
`actor` y `entity` almacenan objetos en arrays fijos; `scene` mantiene el estado de escena. Detecta el agotamiento de capacidad y deja de usar los ID destruidos. Algunas API FC registran callbacks sin llamarlos. Para empezar, despacha explícitamente las funciones de cada estado desde el bucle principal.

`chain` conserva posiciones anteriores y `collision` comprueba contactos entre rectángulos y otras formas. Un orden constante de mover, comprobar colisiones y dibujar evita decisiones de colisión con un fotograma de retraso.

## 8. Matemáticas y física
`fixed.h` ofrece Q8.8; `math_fast` / `math_fixed`, operaciones numéricas; `math_lut`, cálculos por tablas. El `physics2d.h` actual proporciona **tipos y constantes Q5.3**, no una función de integración ni macros de actualización. No es la API de mundos y cuerpos de GB.

La parte fraccionaria Q5.3 mide octavos de píxel. Conserva por separado coordenada entera, fracción, velocidad y dirección, y realiza la suma y el acarreo en el juego. `fc_subpixel.c` añade 2/8 de píxel ocho veces, pasando de 40 a 42. No reutilices el valor 256 de Q8.8 como si representara lo mismo en Q5.3.

## 9. Recursos, mappers y FDS
`bank` y `asset` describen bancos PRG y recursos. El efecto de una operación de `mapper.h` depende del mapper seleccionado al compilar. Diseña configuración, activación, reconocimiento y desactivación de IRQ de desplazamiento como una secuencia coherente.

FDS reparte servicios entre `fds_file`, `fds_overlay`, `fds_save` y `fds_sound`. Cargar un overlay reemplaza código en una dirección existente; cuida los destinos de retorno y la vida de los datos. No presupongas el funcionamiento de una llamada lejana de cartucho.

## 10. Referencia y ejemplos
El diccionario sigue los encabezados públicos y distingue funciones, macros de función y alias. Los encabezados completos incluyen estructuras y constantes. Las declaraciones sin cuerpo, los callbacks solo almacenados y las interfaces especializadas se distinguen de las operaciones ordinarias verificadas. Los comentarios originales se conservan para compararlos con la implementación.

`vram_get_queue_capacity()` devuelve la capacidad total del búfer de comandos: 128 bytes. `vram_get_queue_free()` devuelve los bytes disponibles, calculados restando `vram_get_queue_used()` de la capacidad total. Se cuenta el tamaño de los comandos, incluidas las direcciones y otros metadatos, no el espacio libre de la VRAM física. Escribir un tile requiere 4 bytes; un relleno, 5; y una copia mediante puntero, 6. Comprueba el espacio antes de hacer commit, ya que la NMI puede consumir la cola después de confirmarla.
