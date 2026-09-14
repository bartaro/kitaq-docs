## 1. Escolher os componentes necessários
`fc.h` reúne declarações, `core.h` define tipos e `intrinsics.h` declara operações do compilador. As funções C comuns da biblioteca precisam de suas implementações `.c`. Macros definidas inteiramente no cabeçalho e funções intrínsecas podem dispensar um fonte de mesmo nome.

{{CODE:0}}

Não aponte `-I` para a biblioteca GB de nome semelhante. Por exemplo, `__oam_dma()` do NES não recebe argumentos, ao contrário da operação GB que recebe um ponteiro.

## 2. Runtime e sistema
`runtime.c` fornece funções auxiliares C para os registradores da PPU, a cópia da OAM em RAM e as filas de VRAM. Também existem caminhos intrínsecos, como `__vramq_*`. Confira quais dados o tratador de NMI consome, em vez de misturar filas independentes com nomes parecidos.

`system_init` inicializa o estado de quadros e ativa NMI. `system_wait_vblank` espera NMI e incrementa o contador de quadros do programa. **Em FC, `system_set_vblank_callback` armazena o valor, mas a função de espera atual não executa esse callback.** Não coloque todas as atualizações do jogo nele presumindo o comportamento da versão GB.

## 3. PPU, tiles, atributos e paletas
`ppu_direct.h` oferece operações diretas de PPU; `vram_queue.h`, atualizações por NMI; `tilemap` / `nametable_asset` cuidam de tabelas e recursos; `attribute` atualiza atributos; e `palette` trabalha com paletas. Separe a carga inicial do trabalho de cada quadro.

As paletas de fundo e de sprites ocupam, cada conjunto, 16 bytes. Os valores são códigos de cor NES, não componentes RGB. Os atributos selecionam cores para grupos de tiles; por isso, mudar a paleta aparente de um tile pode afetar outros próximos.

Algumas declarações de `ppu.h` não correspondem aos nomes implementados em `ppu.c`. As entradas marcadas como **somente declaração** não têm implementação localizada no conjunto coletado e não são usadas como chamadas diretas nos exemplos para iniciantes. As lições executáveis usam funções intrínsecas verificadas. Uma declaração sozinha não comprova que o recurso esteja completo e pronto para vinculação.

`vram_get_queue_capacity()` retorna a capacidade total do buffer de comandos, de 128 bytes. `vram_get_queue_free()` retorna os bytes livres, calculados subtraindo `vram_get_queue_used()` da capacidade total. São bytes de comandos codificados, incluindo seus metadados, não espaço disponível na VRAM física. Escrever um tile requer 4 bytes; preencher uma região, 5; e copiar por ponteiro, 6. Confira o espaço antes de fazer commit: depois disso, NMI pode consumir a fila de forma assíncrona.

## 4. OAM, metasprites e alternância de exibição
O NES suporta até 64 sprites, normalmente oito por linha de varredura. Nove ou mais inimigos ou projéteis na mesma linha não podem aparecer todos simultaneamente. Metasprites combinam vários OBJ em uma imagem; confira os limites de reserva e os formatos dos terminadores.

`oam_fair.h` e `oam_fair_impl.h` alternam a ordem dos candidatos mantendo suas prioridades. Eles permitem priorizar o jogador ou a interface e alternar objetos menos importantes ao longo do tempo. Reordenar a OAM não altera o limite físico de sprites por linha.

## 5. Entrada, repetição e periféricos
`input.c` converte os valores brutos de botões NES em máscaras `BTN_*` no estilo GB. **O A bruto de NES é 0x01; BTN_A da biblioteca é 0x10.** Não passe BTN_A diretamente à opção `--pad1` do KUROSAKI.

`pad` lê a entrada básica; `input_repeat` implementa a repetição ao manter um botão pressionado. `zapper`, `keyboard`, `rob`, `mic` e `midi` expõem interfaces de baixo nível dos dispositivos. Ler zero de um dispositivo ausente não comprova funcionamento: confira seus requisitos de conexão.

## 6. Som
Após `nes_apu_init`, use `nes_sfx_square1`, `nes_sfx_square2`, `nes_sfx_triangle` ou `nes_sfx_noise` para o som interno. Um argumento de período representa o período do temporizador do hardware, não uma frequência em hertz. `fc_sound.c` é um exemplo mínimo de som de onda de pulso.

Amostras DMC têm restrições de endereço, comprimento, alinhamento e taxa. Examine sua posição no mapa antes de fornecer um ponteiro. O DMA de DMC também pode interferir na leitura dos controles; combine rotinas de leitura seguras com os diagnósticos do KUROSAKI.

VRC6 fornece canais adicionais de pulso e dente de serra, VRC7 expõe registradores FM e FDS oferece som por tabela de ondas. Use o mapper correspondente e grave o resultado. Essas APIs são diferentes do controlador GB `Audio_*`.

## 7. Cenas, atores e entidades
`actor` e `entity` armazenam objetos em arrays fixos; `scene` guarda o estado das cenas. Detecte quando a capacidade se esgotar e deixe de usar identificadores destruídos. Algumas APIs FC atualmente registram callbacks sem chamá-los. Nos programas iniciais, despache explicitamente as funções de atualização de cada estado a partir do laço principal.

`chain` mantém um histórico de coordenadas; `collision` testa contato entre formas, como retângulos. Uma ordem consistente de mover, verificar colisões e desenhar evita decisões de colisão atrasadas em um quadro.

## 8. Matemática e física
`fixed.h` oferece aritmética Q8.8; `math_fast` / `math_fixed`, operações numéricas; e `math_lut`, cálculos por tabelas. O `physics2d.h` atual fornece **tipos e constantes Q5.3**, não uma implementação de integração física ou macros de atualização. Ele não é a API GB de mundos e corpos físicos.

As frações Q5.3 representam oitavos de pixel. Mantenha separados a coordenada inteira, a parte fracionária, a velocidade e a direção e faça as somas e o transporte para a parte inteira no código do jogo. `fc_subpixel.c` soma 2/8 de pixel oito vezes, indo do pixel 40 ao 42. Não reutilize sem conversão o valor 256 de Q8.8 como Q5.3.

## 9. Recursos, mappers e FDS
`bank` e `asset` descrevem bancos PRG e recursos. O efeito de uma operação de `mapper.h` depende do mapper escolhido na compilação. Organize a configuração, a ativação, o reconhecimento e a desativação das interrupções de rolagem como uma sequência coerente.

Os serviços FDS se dividem entre `fds_file`, `fds_overlay`, `fds_save` e `fds_sound`. Carregar uma sobreposição substitui código em um endereço existente: preste atenção aos endereços de retorno e à validade dos dados. Não presuma o mesmo comportamento das chamadas entre bancos de um cartucho comum.

## 10. Referência e exemplos
O dicionário abaixo segue os cabeçalhos públicos e distingue funções, macros com parâmetros e aliases. Os cabeçalhos completos também apresentam estruturas e constantes. APIs que só têm declaração, callbacks apenas armazenados e interfaces especializadas de dispositivos são identificados separadamente das operações comuns verificadas. Os comentários do fonte são preservados literalmente para permitir a comparação exata com a implementação.
