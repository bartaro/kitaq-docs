## 1. Elegir los componentes
`fc.h` reúne declaraciones, `core.h` define tipos e `intrinsics.h` declara operaciones del compilador. Las funciones C normales necesitan su implementación `.c`. Las macros de encabezado y las operaciones intrínsecas pueden no necesitar un archivo del mismo nombre.

{{CODE:0}}

No apuntes `-I` a la biblioteca GB de nombre parecido. Por ejemplo, `__oam_dma()` de NES no recibe argumentos; la operación GB recibe un puntero.

## 2. Runtime y system
`runtime.c` ofrece funciones C para los registros PPU, la copia de OAM en RAM y las colas VRAM. También existen rutas intrínsecas como `__vramq_*`. Comprueba qué datos consume la NMI antes de mezclar colas diferentes con nombres semejantes.

`system_init` inicializa el estado de los fotogramas y habilita las NMI. `system_wait_vblank` espera una NMI, incrementa el contador de fotogramas por software y llama una vez, de forma síncrona, al callback registrado. Pase cero a `system_set_vblank_callback` para desactivarlo. El callback se ejecuta en el contexto que llama a la función de espera, no dentro del manejador NMI.

## 3. PPU, tiles, atributos y paletas
`ppu_direct.h` ofrece acceso directo; `vram_queue.h`, actualizaciones por NMI; `tilemap` / `nametable_asset`, tablas y recursos; `attribute`, atributos; `palette`, paletas. Separa la carga inicial del trabajo por fotograma.

Las paletas de fondo y sprites ocupan 16 bytes cada una. Sus valores son códigos de color NES, no componentes RGB. Los atributos eligen colores para grupos de tiles: cambiar la paleta aparente de uno puede afectar a sus vecinos.

`ppu.h` y `ppu.c` proporcionan control de pantalla, transferencia de una paleta de 32 bytes e inicialización completa de una tabla de nombres. `nes_ppu_seek_bytes(hi,lo)` reinicia el latch de dirección y establece una dirección a partir de dos bytes. Puede enlazarse junto con `nes_ppu_seek(address)` de `runtime.c`, que recibe la dirección en una sola palabra. Desactive el renderizado antes de las transferencias y la inicialización.

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
`actor` y `entity` almacenan los objetos del juego en arrays de tamaño fijo; `scene` gestiona el estado de las escenas. Detecta cuándo se agota la capacidad y deja de usar los ID destruidos. Las transiciones, actualizaciones y operaciones de dibujo de escenas invocan sus callbacks registrados de forma síncrona. Comprueba el orden de llamada y las restricciones de reentrada de cada API.

`chain` proporciona seguimiento de cuerpos articulados mediante `ChainBody` e historial de posiciones mediante `Chain`; `collision` comprueba el contacto entre formas, como rectángulos. Mantener el orden movimiento, colisión y dibujo evita que las decisiones de colisión lleguen con un fotograma de retraso.

## 8. Matemáticas y física
`fixed.h` proporciona aritmética Q8.8, `math_fast` y `math_fixed` operaciones numéricas, y `math_lut` cálculos mediante tablas. `physics2d` gestiona la integración del movimiento de cajas, la gravedad, los contactos AABB y la respuesta de las superficies. `physics3d` gestiona cajas 3D sin rotación, rebotes y valores de impacto. Reserva un mundo y un array de cuerpos, inicialízalos, configura sus parámetros y llama a la función de paso de simulación. Las posiciones y velocidades usan unidades enteras coherentes elegidas por quien llama a la API.

La parte fraccionaria Q5.3 mide octavos de píxel. Conserva por separado coordenada entera, fracción, velocidad y dirección, y realiza la suma y el acarreo en el juego. `fc_subpixel.c` añade 2/8 de píxel ocho veces, pasando de 40 a 42. No reutilices el valor 256 de Q8.8 como si representara lo mismo en Q5.3.

## 9. Recursos, mappers y FDS
`bank` y `asset` describen bancos PRG y recursos. El efecto de una operación de `mapper.h` depende del mapper seleccionado al compilar. Diseña configuración, activación, reconocimiento y desactivación de IRQ de desplazamiento como una secuencia coherente.

FDS reparte servicios entre `fds_file`, `fds_overlay`, `fds_save` y `fds_sound`. Cargar un overlay reemplaza código en una dirección existente; cuida los destinos de retorno y la vida de los datos. No presupongas el funcionamiento de una llamada lejana de cartucho.

## 10. Referencia y ejemplos
El diccionario sigue los encabezados públicos y distingue funciones, macros de función y alias. Los encabezados completos incluyen estructuras y constantes. Las declaraciones sin cuerpo, los callbacks solo almacenados y las interfaces especializadas se distinguen de las operaciones ordinarias verificadas. Los comentarios originales se conservan para compararlos con la implementación.

`vram_get_queue_capacity()` devuelve la capacidad total del búfer de comandos: 128 bytes. `vram_get_queue_free()` devuelve los bytes disponibles, calculados restando `vram_get_queue_used()` de la capacidad total. Se cuenta el tamaño de los comandos, incluidas las direcciones y otros metadatos, no el espacio libre de la VRAM física. Escribir un tile requiere 4 bytes; un relleno, 5; y una copia mediante puntero, 6. Comprueba el espacio antes de hacer commit, ya que la NMI puede consumir la cola después de confirmarla.
