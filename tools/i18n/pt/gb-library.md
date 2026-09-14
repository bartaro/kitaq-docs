## 1. Usar a biblioteca
A biblioteca reúne código C reutilizável baseado nas funções intrínsecas `__` do KITAQGB. Ela vai do controle de tela à física, aos gráficos 3D e à comunicação.

{{CODE:0}}

{{CODE:1}}

Cada entrada de API apresenta a declaração, o cabeçalho, a implementação e um exemplo de uso. Os fragmentos mostram como passar argumentos; o programa que faz a chamada deve preparar os buffers e objetos necessários. A seção de programas completos contém exemplos que podem ser compilados diretamente como ROMs.

## 2. Organizar um quadro do jogo
`system_init` inicializa o gerenciamento de quadros. `system_wait_vblank` espera e avança o contador de quadros do programa. Em GB, essa espera chama o callback de VBlank de forma cooperativa; registrar o callback não instala um tratador de interrupção de hardware.

1. Atualize a entrada uma vez.
2. Calcule o movimento, as colisões e o estado do jogo.
3. Prepare os comandos de desenho e a OAM.
4. Aplique as atualizações durante VBlank.
5. Faça a música avançar conforme a organização do controlador escolhido.

Combinar operações que esperam, como `vram_flush` e `sprite_flush_oam`, pode fazer uma atualização do jogo esperar dois quadros. Depois de esperar por conta própria, talvez seja adequado usar a operação `_now` correspondente, desde que você garanta o momento correto de acesso ao hardware.

## 3. Entrada e repetição
`input_down(mask)` testa um botão mantido pressionado; `input_pressed(mask)`, uma nova pressão; `input_released(mask)`, a liberação; e `input_repeat(mask)` oferece a repetição típica de menus. Esses estados mudam em `input_update()`. Chamá-la repetidamente no mesmo quadro pode apagar a detecção de uma nova pressão.

| Botões | Máscaras |
| --- | --- |
| Direita, esquerda, cima, baixo | 0x01 / 0x02 / 0x04 / 0x08 |
| A, B, SELECT, START | 0x10 / 0x20 / 0x40 / 0x80 |

`gb_input.c` conta quantas vezes A foi pressionado. Verifique se manter o botão pressionado não aumenta continuamente o contador; depois substitua `input_pressed` por `input_down` para observar a diferença.

## 4. Fundos, texto e VRAM
`vram_queue_bg_tile` coloca um tile na fila, `vram_queue_bg_rect` coloca um retângulo e `vram_queue_bg_block` agenda uma transferência de array. Confira os valores retornados e `vram_get_overflowed()` para detectar o esgotamento da capacidade. Se uma operação guardar um ponteiro de origem, mantenha os dados inalterados, a memória válida e o banco acessível até o fim da transferência.

`vram_get_queue_capacity()` retorna o total de entradas da fila de comandos, 32 por padrão. `vram_get_queue_free()` retorna as entradas livres e `vram_get_queue_used()` as ocupadas. Cada operação agendada ocupa uma entrada, independentemente do volume de dados transferido. Essas funções descrevem a fila de transferências, não o espaço livre da VRAM física.

`text.c` e `menu.c` implementam os serviços de texto, seleção e janelas declarados em `rpg.h`. A correspondência entre caracteres e tiles deve combinar com a fonte carregada na VRAM. Ela não é necessariamente a mesma usada pela função auxiliar `m_text` deste manual.

## 5. Sprites e animação
Comece com `sprite_init`, `sprite_alloc`, `sprite_set_tile` e `sprite_set_pos`. O GB admite 40 sprites no total e 10 por linha de varredura; considere tanto o total quanto a concentração horizontal. `sprite_warn_scanline_overflow` e `sprite_max_scanline_count` ajudam a examinar a distribuição.

`MetaSpritePart` descreve a posição relativa de OBJ. `SpriteAnim` define os tiles das etapas de animação e seus intervalos. As partes desenhadas por `metasprite_draw` devem corresponder às entradas OBJ reservadas. O A de `gb_sprite.c` demonstra o uso de um tile de caractere como sprite.

## 6. Cor, rolagem, efeitos por linha e câmeras
Os argumentos RGB de `cgb_bg_rgb` e `cgb_obj_rgb` variam de 0 a 31, não de 0 a 255. `CGB_RGB15` empacota esses componentes em um valor de 16 bits. As funções de alto nível para paletas CGB foram projetadas para não fazer nada em DMG.

`Scroll_SetBg` posiciona o fundo, `Scroll_SetWindow` posiciona a janela e o módulo de câmera calcula a área visível a partir das coordenadas do mundo. Não misture as unidades de ponto fixo da câmera com os pixels inteiros da tela.

`raster.c` constrói tabelas de rolagem por faixas e distorção horizontal por linha. As operações `Scroll_SplitCommit` usam os vetores VBlank/STAT. Se música e rolagem precisarem do mesmo vetor, coordene-as por um despachador comum; dois tratadores independentes não podem assumir esse vetor ao mesmo tempo.

## 7. Música e efeitos sonoros
Compile `audio_hwregs_gb.c`, depois `audio.c` e, por último, o fonte do jogo. Não acrescente definições duplicadas de NR10–NR52 se o jogo já as fornecer. Após `Audio_Init`, normalmente chame `Audio_Update` uma vez por quadro.

`Audio_PlayMusic(bank,song)` informa explicitamente o banco da música. `Audio_PlaySFXBanked` reproduz um efeito de outro banco. As prioridades resolvem a disputa entre efeitos que compartilham canais físicos. O GB tem quatro canais de som físicos: CH1, CH2, CH3 e CH4.

Os comandos de fluxo musical `AUDIO_CMD_NOTE` e `AUDIO_CMD_SET_INST` usam esta numeração de canais: **0=CH1, 1=CH2, 2=CH4, 3=CH3**. Não a confunda com as constantes de canal da API comum. O cabeçalho define atualmente `AUDIO_NOTE_MAX=67`.

O fluxo básico de efeitos CH1 lê pares de nota e volume por quadro e termina na nota 0. CH3 usa outro marcador e outro formato. Consulte `gb_sound.c`. Os fades avançam durante `Audio_Update`; interromper as atualizações também interrompe o fade.

## 8. Música pela interrupção VBlank
`audio_vblank.c` usa um formato de reprodução próprio. Os registros temporizados têm cinco bytes: `delay, ch2_note, ch1_note, ch3_note, ch4_noise_param`. O driver lê músicas acessíveis diretamente ou consome uma fila na WRAM. A biblioteca pública não inclui uma função para abastecer essa fila: o jogo precisa fornecer o produtor e coordenar as escritas com a ISR. `LOOP` só é reconhecido em fluxos diretos, e `IMMEDIATE`, apenas no modo de fila. Os fluxos comuns de `audio.c` não podem ser passados sem conversão.

{{CODE:2}}

O patch instala o vetor VBlank em 0x0040 e atualiza a soma de verificação. Aplique-o somente a uma ROM preparada para esse controlador. Confira a compatibilidade com tratadores VBlank próprios e rolagem dividida. A compilação bem-sucedida não comprova reprodução audível: grave com KOKURA e verifique se a música avança.

## 9. Ponto fixo, física e 3D
Na aritmética Q8.8 de `fixed.h`, 256 representa 1,0 e 128 representa 0,5. `gb_fixed.c` demonstra `fix_from_int`, `fix_mul` e `fix_to_int`. Defina os intervalos de valores antes de implementar os cálculos para evitar estouros.

`physics2d` trabalha com retângulos, `physics2d_circle` com círculos e `physics3d` com AABBs tridimensionais. Prepare e inicialize os arrays de mundo e corpos, defina a velocidade ou a gravidade e avance a simulação. Use unidades consistentes para posição e velocidade por passo; a biblioteca não converte esses valores automaticamente em pixels. O exemplo de círculos usa posição 40 e velocidade 2. Massa inversa zero indica um corpo estático. Confira nos cabeçalhos a representação de cada coeficiente e os limites dos cálculos intermediários. Em especial, a função `kq2d_body_apply_friction` converte seu coeficiente em um byte com sinal: valores de 128 a 255 tornam-se negativos e não representam o amortecimento Q8 sem sinal usual. `gb_circle.c` mostra um passo completo.

`wire3d_dmg` é uma biblioteca de renderização de estruturas de arame monocromáticas para Game Boy. Compile `wire3d_dmg_96.c` para uma área de 128 × 96 ou `wire3d_dmg.c` para 128 × 120 e use as funções `Wire3DDMG_*`. `wire3d` e `dmg3d` também oferecem pontos de entrada para os perfis de 96 e 120 linhas, respectivamente. Compile apenas um ponto de entrada por programa. `wire3d_cgb` é o renderizador dedicado a cores. Reserve explicitamente a RAM, a VRAM e as regiões de tela de cada um. Os dois renderizadores monocromáticos descartam as arestas que cruzam os limites de profundidade, em vez de recortá-las. A oclusão entre objetos é aproximada por retângulos que envolvem as faces e cinco amostras ao longo de cada linha; não há teste de profundidade por pixel. A versão CGB usa velocidade dupla e DMA e exige `--cgb=cgb_only`.

`Wire3DDMG_BeginFrame` (`WIRE3D_DMG_HEIGHT=96`) limpa o buffer de desenho. Já `Wire3DDMG_BeginFrame` (`WIRE3D_DMG_HEIGHT=120`) apenas reinicia o estado de oclusão: DMG3D consome e limpa os dados ao transferi-los para a VRAM. A transferência dos tiles alterados também inclui os do quadro anterior para apagar os pixels antigos. A transferência auxiliar compartilha parte do buffer principal; não é um buffer independente. Organize a sequência de cada quadro de acordo com o renderizador escolhido.

Nas linhas do CGB, use as cores 1, 2 e 3. O modo normal de 128 × 96 combina os bits de cor: a sobreposição das cores 1 e 2 resulta na cor 3. A cor 0 não apaga uma linha. Limpe o quadro ou use as funções específicas de apagamento. No modo normal, `Wire3DCGB_DrawLine2D` e o desenho de modelos não registram a região para transferência parcial. Para desenhar linhas e registrar essa região, use `Wire3DCGB_DrawLineClipped2D`; para incluir toda a área de desenho na próxima transferência parcial, chame `Wire3DCGB_InvalidateFrameHistory`.

O modo de 160 × 144 aloca no máximo 127 tiles por quadro. Se o caminho rápido de desenho de linhas não conseguir alocar um tile ou encontrar uma coordenada fora da tela, `Wire3DCGB_GetFullScreenOverflow()` retorna um valor diferente de zero e a gravação de pixels é suspensa até a inicialização do próximo quadro. Mantenha os vértices dentro da área selecionada. A margem direita da máscara triangular vai até X=127 no modo de 128 × 96 e até X=159 no modo de tela inteira. Siga as exigências de mapeamento dos bancos WRAM descritas em cada API, especialmente ao usar tela inteira ou FastMap.

## 10. Cenas, conjuntos de objetos e padrões de projéteis
`scene` gerencia estados como título, jogo e pausa; `entity` oferece um conjunto de objetos de capacidade fixa; e `chain` armazena um histórico de coordenadas para uma cobra, um trem ou uma corda. Verifique valores de falha de reserva, como 0xFF, antes de usar o ponteiro retornado por `entity_get`.

`danmaku` oferece conjuntos de projéteis em ponto fixo, disparos direcionais e em leque, colisões e detecção de passagem próxima. Sua composição sobre o fundo CGB evita o limite habitual de OBJ, mas o tempo por quadro e a capacidade de transferência do fundo continuam limitados. Meça o tempo de processamento em vez de buscar apenas uma contagem alta de projéteis.

## 11. RPG, aventura, estratégia e salvamento
`rpg.h` reúne declarações de números aleatórios, flags, missões, compressão, texto, menus, scripts, mapas, salvamento e busca de caminhos. As implementações estão divididas em arquivos como `rng.c`, `flags.c`, `rle.c` e `text.c`. Use o dicionário para escolher as unidades necessárias.

Um `rng_seed` fixo produz uma sequência repetível para testes. Confira se cada função de intervalo inclui o limite superior. `flag_get` e `flag_set` operam sobre conjuntos de bits. `save.c` utiliza acesso a SRAM no estilo MBC5; a capacidade de RAM declarada no cabeçalho da ROM deve corresponder à região de salvamento do jogo.

Mantenha os serviços de tabuleiro, lista de jogadas válidas e desfazer de `slg.h`, assim como a busca de caminhos de `slg_path.c`, separados das regras e da avaliação específicas do jogo. Largura, altura e arrays de trabalho precisam respeitar os limites da biblioteca e os requisitos de cada argumento.

## 12. Comunicação
`link.c` fornece transferências seriais de bytes; `link_packet.c` é uma camada opcional de pacotes. Vincule primeiro `link_hwregs_gb.c`. Os modos de polling e interrupção exigem chamadas diferentes; no modo de interrupção, o jogo precisa conectar o vetor 0x0058.

As operações lógicas `Link4_*` e as operações `LinkDmg07_*` do adaptador físico Nintendo DMG-07 são sistemas separados. DMG-07 usa relógio externo: chame `LinkDmg07_Poll` com frequência e `LinkDmg07_TickFrame` uma vez por quadro. Fazer polling apenas uma vez por quadro pode não atender aos requisitos de tempo. Nos trabalhos pair/dmg07 do KOKURA, teste conexão, início, desconexão e reconexão separadamente.

## 13. Bancos, recursos e depuração
`BankPtr` combina um número de banco com um ponteiro. `far_data_read` lê recursos de outro banco para a RAM. O módulo de recursos associa identificadores a descritores; o jogo continua responsável pela validade dos dados, pelos bancos e pelos tamanhos.

`debug_trace_u8` e `debug_trace_u16` registram valores em RAM; `debug_assert_fail` registra um código de diagnóstico. Não são chamadas a `printf` que imprimem no terminal do PC. Examine os registros pelas ferramentas de observação de memória do emulador. `gb_debug.c` registra HP=42.
