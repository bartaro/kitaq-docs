## 1. Utilizar la biblioteca
La biblioteca reúne código C reutilizable basado en las funciones intrínsecas `__` de KITAQGB. Abarca desde el control de pantalla hasta física, gráficos 3D y comunicaciones.

{{CODE:0}}

{{CODE:1}}

Cada entrada de API incluye la declaración, la cabecera, la implementación y un ejemplo de uso. Los fragmentos muestran cómo pasar argumentos; el programa que llama debe preparar los búferes y objetos necesarios. La sección de programas completos contiene ejemplos que se pueden compilar directamente como ROM.

## 2. Organizar un fotograma del juego
`system_init` inicializa la gestión de fotogramas. `system_wait_vblank` espera y aumenta el contador de fotogramas del programa. En GB, esa función de espera invoca la función de retorno de VBlank de forma cooperativa: registrarla no instala un manejador de interrupción de hardware.

1. Actualiza la entrada una vez.
2. Calcula el movimiento, las colisiones y el estado del juego.
3. Prepara las órdenes de dibujo y la OAM.
4. Aplica las actualizaciones durante VBlank.
5. Haz avanzar la música según el controlador elegido.

Si combinas operaciones que esperan, como `vram_flush` y `sprite_flush_oam`, una sola actualización del juego puede terminar esperando dos fotogramas. Si ya has realizado la espera, puede convenir la variante `_now`, siempre que respetes sus requisitos de acceso al hardware.

## 3. Entrada y repetición de botones
`input_down(mask)` comprueba si un botón sigue pulsado; `input_pressed(mask)`, si acaba de pulsarse; e `input_released(mask)`, si acaba de soltarse. `input_repeat(mask)` ofrece la repetición habitual de los menús. Estos estados se actualizan con `input_update()`. Llamarla varias veces en un mismo fotograma puede borrar la detección de una pulsación nueva.

| Botones | Máscaras |
| --- | --- |
| Derecha, izquierda, arriba, abajo | 0x01 / 0x02 / 0x04 / 0x08 |
| A, B, SELECT, START | 0x10 / 0x20 / 0x40 / 0x80 |

`gb_input.c` cuenta las pulsaciones de A. Comprueba que mantenerlo pulsado no aumenta continuamente el contador. Después sustituye `input_pressed` por `input_down` para observar la diferencia.

## 4. Fondos, texto y VRAM
`vram_queue_bg_tile` encola un tile, `vram_queue_bg_rect` un rectángulo y `vram_queue_bg_block` una transferencia desde un array. Comprueba los valores devueltos y `vram_get_overflowed()` para detectar si se ha agotado la capacidad. Si una operación conserva un puntero al origen, mantén los datos sin modificar, la memoria válida y su banco accesible hasta que termine la transferencia.

`vram_get_queue_capacity()` devuelve el número total de entradas de la cola de comandos (32 por defecto), `vram_get_queue_free()` indica cuántas quedan libres y `vram_get_queue_used()` cuántas están ocupadas. Cada operación encolada ocupa una entrada, independientemente de la cantidad de datos que transfiera. Estas funciones consultan la cola de transferencias, no el espacio libre de la VRAM física.

`text.c` y `menu.c` implementan los servicios de texto, selección y ventanas declarados en `rpg.h`. La correspondencia entre texto y tiles debe coincidir con la fuente cargada en VRAM. No tiene por qué ser la misma que utiliza la función auxiliar `m_text` de este manual.

## 5. Sprites y animación
Empieza con `sprite_init`, `sprite_alloc`, `sprite_set_tile` y `sprite_set_pos`. GB admite 40 sprites en total y 10 por línea de barrido. Ten en cuenta tanto el número total como su concentración en una misma línea horizontal. `sprite_warn_scanline_overflow` y `sprite_max_scanline_count` ayudan a examinar la distribución.

`MetaSpritePart` describe posiciones relativas de objetos OBJ. `SpriteAnim` define los tiles de cada paso de la animación y sus intervalos. Las partes que dibuja `metasprite_draw` deben corresponder a las entradas OBJ reservadas. La A de `gb_sprite.c` muestra cómo utilizar el tile de una letra como sprite.

## 6. Color, desplazamiento, efectos por línea y cámaras
Los componentes RGB de `cgb_bg_rgb` y `cgb_obj_rgb` van de 0 a 31, no de 0 a 255. `CGB_RGB15` los empaqueta en un valor de 16 bits. Las funciones de alto nivel para paletas CGB están diseñadas para no realizar ninguna operación en DMG.

`Scroll_SetBg` sitúa el fondo y `Scroll_SetWindow` la ventana. El módulo de cámara obtiene el área visible a partir de las coordenadas del mundo. No mezcles las unidades de punto fijo de la cámara con los píxeles enteros de pantalla.

`raster.c` genera tablas de desplazamiento por franjas y distorsión horizontal por línea. Las operaciones `Scroll_SplitCommit` utilizan los vectores VBlank/STAT. Si la música y el desplazamiento necesitan el mismo vector, coordínalos mediante un despachador común; dos manejadores independientes no pueden ocuparlo simultáneamente.

## 7. Música y efectos de sonido
Compila primero `audio_hwregs_gb.c`, después `audio.c` y por último el código del juego. No dupliques las definiciones de los registros NR10–NR52 si el juego ya las aporta. Tras `Audio_Init`, lo habitual es llamar a `Audio_Update` una vez por fotograma.

`Audio_PlayMusic(bank,song)` especifica expresamente el banco de la música. `Audio_PlaySFXBanked` reproduce un efecto situado en otro banco. Las prioridades resuelven la competencia entre efectos que utilizan los mismos canales físicos. GB dispone de cuatro: CH1, CH2, CH3 y CH4.

Las órdenes del flujo musical `AUDIO_CMD_NOTE` y `AUDIO_CMD_SET_INST` usan esta numeración de canales: **0=CH1, 1=CH2, 2=CH4, 3=CH3**. No lo confundas con las constantes de canal de la API habitual. La cabecera define actualmente `AUDIO_NOTE_MAX=67`.

El flujo básico de efectos de CH1 lee pares de nota y volumen por fotograma y termina con la nota 0. CH3 emplea otro marcador y otro formato. Consulta `gb_sound.c`. Los fundidos avanzan durante `Audio_Update`; si dejas de actualizar, el fundido también se detiene.

## 8. Música mediante la interrupción VBlank
`audio_vblank.c` utiliza un formato de reproducción independiente. Los registros temporizados contienen cinco bytes: `delay, ch2_note, ch1_note, ch3_note, ch4_noise_param`. El controlador lee canciones accesibles directamente o consume una cola en WRAM. La biblioteca pública no incluye una función que rellene esa cola: el juego debe aportar el productor y coordinar las escrituras con la ISR. `LOOP` solo se reconoce en flujos directos e `IMMEDIATE` solo en modo de cola. Los flujos habituales de `audio.c` no se pueden pasar sin convertirlos.

{{CODE:2}}

El parche modifica el vector VBlank en 0x0040 y actualiza la suma de comprobación. Aplícalo únicamente a una ROM preparada para este controlador. Revisa los posibles conflictos con manejadores VBlank propios y con el desplazamiento dividido. Compilar correctamente no demuestra que la música se oiga: grábala con KOKURA y comprueba que avance.

## 9. Punto fijo, física y 3D
En la aritmética Q8.8 de `fixed.h`, 256 representa 1,0 y 128 representa 0,5. `gb_fixed.c` muestra `fix_from_int`, `fix_mul` y `fix_to_int`. Define los rangos de valores antes de programar los cálculos para evitar desbordamientos.

`physics2d` trabaja con rectángulos, `physics2d_circle` con círculos y `physics3d` con AABB tridimensionales. Prepara e inicializa los arreglos de mundo y cuerpos, configura la velocidad o la gravedad y ejecuta un paso. Usa unidades coherentes para la posición y la velocidad por paso; la biblioteca no convierte automáticamente a píxeles. El ejemplo circular emplea posición 40 y velocidad 2. Una masa inversa nula indica un cuerpo estático. Consulta en las cabeceras la representación de cada coeficiente y los límites de los cálculos intermedios. En particular, la función `kq2d_body_apply_friction` convierte su coeficiente a un byte con signo: 128–255 pasan a ser valores negativos, no factores de amortiguación Q8 sin signo. `gb_circle.c` muestra un paso completo.

`wire3d_dmg` es una biblioteca de renderizado alámbrico monocromo para Game Boy. Compila `wire3d_dmg_96.c` para una vista de 128 × 96 o `wire3d_dmg.c` para 128 × 120, y utiliza las funciones `Wire3DDMG_*`. `wire3d` y `dmg3d` también ofrecen puntos de entrada para los perfiles de 96 y 120 líneas, respectivamente. Compila un solo punto de entrada por programa. `wire3d_cgb` es el renderizador dedicado al color. Reserva expresamente la RAM, la VRAM y las zonas de pantalla de cada renderizador. Los dos renderizadores monocromos descartan las aristas que cruzan los límites de profundidad, en lugar de recortarlas. La ocultación entre objetos se aproxima mediante rectángulos que encierran las caras y cinco muestras por línea; no es una prueba de profundidad por píxel. La versión CGB utiliza doble velocidad y DMA, y requiere `--cgb=cgb_only`.

`Wire3DDMG_BeginFrame` (`WIRE3D_DMG_HEIGHT=96`) borra el búfer de dibujo. `Wire3DDMG_BeginFrame` (`WIRE3D_DMG_HEIGHT=120`) solo reinicia el estado de ocultación: DMG3D consume y borra los datos al transferirlos a VRAM. La transferencia de tiles modificados incluye los del fotograma anterior para borrar los píxeles antiguos. La transferencia auxiliar comparte parte del búfer principal; no dispone de uno independiente. Organiza la secuencia de cada fotograma según el renderizador elegido.

Para las líneas de CGB, utilice los colores 1, 2 y 3. El modo normal de 128 × 96 combina los bits de color: al superponer los colores 1 y 2 se obtiene el color 3. El color 0 no borra una línea. Limpie el fotograma o use las funciones de borrado específicas. En el modo normal, `Wire3DCGB_DrawLine2D` y el dibujo de modelos no registran la región que debe transferirse. Para dibujar líneas y registrar esa región, use `Wire3DCGB_DrawLineClipped2D`; para incluir toda el área de dibujo en la siguiente transferencia parcial, llame a `Wire3DCGB_InvalidateFrameHistory`.

El modo de 160 × 144 asigna como máximo 127 teselas por fotograma. Si el trazador rápido no puede asignar una tesela o recibe una coordenada fuera de pantalla, `Wire3DCGB_GetFullScreenOverflow()` devuelve un valor distinto de cero y se suspenden las escrituras de píxeles hasta inicializar el siguiente fotograma. Mantenga los vértices dentro del área seleccionada. El margen derecho de la máscara triangular llega como máximo a X=127 en el modo de 128 × 96 y a X=159 en pantalla completa. Respete la configuración de bancos WRAM indicada en cada API, especialmente al usar pantalla completa o FastMap.

## 10. Escenas, grupos de objetos y patrones de proyectiles
`scene` gestiona estados como título, juego y pausa; `entity` ofrece un grupo de objetos de capacidad fija; y `chain` almacena un historial de coordenadas para una serpiente, un tren o una cuerda. Comprueba los valores que indican un fallo de reserva, como 0xFF, antes de utilizar el puntero devuelto por `entity_get`.

`danmaku` proporciona grupos de proyectiles en punto fijo, generación direccional y en abanico, impactos y roces. Su composición sobre el fondo CGB evita el límite habitual de objetos OBJ, pero siguen existiendo límites de tiempo por fotograma y de ancho de banda para actualizar el fondo. Mide el tiempo de procesamiento en lugar de fijarte únicamente en el número de proyectiles.

## 11. RPG, aventuras, estrategia y partidas guardadas
`rpg.h` reúne declaraciones de números aleatorios, indicadores, misiones, compresión, texto, menús, scripts, mapas, guardado y búsqueda de rutas. Las implementaciones se reparten entre archivos como `rng.c`, `flags.c`, `rle.c` y `text.c`. Utiliza el diccionario para escoger las unidades necesarias.

Un valor fijo de `rng_seed` genera una secuencia reproducible para las pruebas. Comprueba si cada función de rango incluye su límite superior. `flag_get` y `flag_set` trabajan sobre conjuntos de bits. `save.c` utiliza un esquema de acceso a SRAM de tipo MBC5: la capacidad de RAM de la cabecera de la ROM debe corresponder al área de guardado del juego.

Los servicios de tablero, listas de jugadas y deshacer de `slg.h`, así como la búsqueda de rutas de `slg_path.c`, son independientes de las reglas y la evaluación propias de cada juego. La anchura, la altura y los arrays de trabajo deben respetar tanto los límites de la biblioteca como los de cada argumento.

## 12. Comunicaciones
`link.c` implementa transferencias de bytes por el puerto serie; `link_packet.c` añade una capa opcional de paquetes. Enlaza primero `link_hwregs_gb.c`. Los modos de sondeo e interrupción requieren llamadas distintas. Para usar interrupciones, el juego debe conectar el vector 0x0058.

Las operaciones lógicas `Link4_*` y las operaciones `LinkDmg07_*` del adaptador físico Nintendo DMG-07 son sistemas distintos. DMG-07 utiliza un reloj externo: llama con frecuencia a `LinkDmg07_Poll` y una vez por fotograma a `LinkDmg07_TickFrame`. Sondear solo una vez por fotograma puede resultar demasiado lento. En los trabajos pair/dmg07 de KOKURA, prueba por separado la conexión, el inicio, la desconexión y la reconexión.

## 13. Bancos, recursos y depuración
`BankPtr` combina un número de banco con un puntero. `far_data_read` copia recursos de otro banco a RAM. El módulo de recursos relaciona identificadores con descriptores; el juego sigue siendo responsable de la vigencia de los datos, los bancos y los tamaños.

`debug_trace_u8` y `debug_trace_u16` registran valores en RAM; `debug_assert_fail` registra un código de diagnóstico. No son llamadas a `printf` que impriman en la consola del PC. Examina los registros mediante las herramientas de observación de memoria del emulador. `gb_debug.c` registra HP=42.
