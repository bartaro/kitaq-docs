## 1. Conheça o KITAQGB
KITAQGB é um compilador da família C para GB/CGB desenvolvido a partir do NORCAL, da Zachtronics.

{{ORIGIN}}

Ele lê arquivos C, gera instruções de CPU e organiza tudo em uma ROM. Sua linguagem, suas bibliotecas e suas convenções de chamada diferem das de um compilador C para computadores de uso geral.

O GB tem uma CPU de 8 bits e pouca memória. A maior parte dos gráficos usa tiles de 8 × 8 pixels. Sprites são imagens pequenas posicionadas de forma independente. O texto também precisa de gráficos de tiles: não há uma tela de texto universal presumida pelo compilador. Estes exemplos usam os glifos do `ascii.c` do autor, reorganizados pelos códigos ASCII para GB sem alterar seus bits. A edição FC converte os mesmos desenhos para o formato CHR do NES.

## 2. Requisitos e compilação do compilador
Instale um ambiente Visual Studio/MSBuild com suporte ao .NET Framework 4.8. Use um prompt Developer PowerShell em que `MSBuild.exe` esteja disponível.

{{CODE:0}}

Mantenha o executável junto com seus arquivos de configuração. Informe o caminho do compilador nos comandos para deixar claro qual arquivo será usado. A compilação do projeto copia o executável para a raiz do repositório `kitaqgb`.

## 3. Seu primeiro programa
O exemplo `samples/gb_hello.c` usa funções auxiliares de tela e texto de `gb_common.h`. Mantenha esse cabeçalho e os arquivos da fonte de caracteres na mesma estrutura de pastas. `#include` lê declarações ou definições de outro arquivo.

{{CODE:1}}

{{CODE:2}}

O objetivo é mostrar HELLO WORLD e 042 na tela. Os nomes que começam com `m_` são funções didáticas definidas no cabeçalho comum dos exemplos, não comandos padrão do KITAQGB. Entre as funções intrínsecas do compilador estão operações como `__wait_vblank` e `__vram_copy`.

## 4. Sintaxe básica e tipos
Termine as instruções com `;` e agrupe-as com `{ }`. `//` inicia um comentário de linha e `/* ... */` delimita um comentário de bloco. Os nomes diferenciam maiúsculas de minúsculas. Use `void main()` como ponto de entrada. **Nesta versão GB, `void main(void)` causa erro de sintaxe**; portanto, não copie sem alterações a declaração usada em FC.

| Tipo | Significado e intervalo |
| --- | --- |
| `u8` | Inteiro de 8 bits sem sinal, de 0 a 255 |
| `s8` | Inteiro de 8 bits com sinal, de -128 a 127 |
| `u16` | Inteiro de 16 bits sem sinal, de 0 a 65535 |
| `s16` | Inteiro de 16 bits com sinal, de -32768 a 32767 |
| `void` | Sem valor de retorno |
| `T*` | Ponteiro para dados do tipo T |

Comece com esses nomes curtos. Não presuma as definições de `int`, `long`, `float`, `double` ou dos cabeçalhos padrão de um ambiente desktop. Esta versão trata `char` como dado de 8 bits sem sinal; use explicitamente `s8` ou `s16` quando precisar de aritmética com sinal.

{{CODE:3}}

`(u16)` é uma conversão explícita de tipo. Atribuir a uma variável maior um valor pequeno que já sofreu estouro não recupera os bits perdidos: amplie os operandos antes do cálculo. Para movimentos fracionários, use a biblioteca de ponto fixo.

## 5. Expressões e operadores
| Grupo | Operadores | Exemplo ou significado |
| --- | --- | --- |
| Aritmética | `+ - * / %` | `n / 10` é o quociente inteiro; `n % 10` é o resto |
| Comparação | `== != < <= > >=` | `lives == 0` testa igualdade |
| Lógica | `! &&` / `||` | Negação, ambas as condições, pelo menos uma condição |
| Bits | `&` / `|` / `^ ~ << >>` | Máscaras de botões e outros conjuntos de bits |
| Atribuição | `= += -=` e formas relacionadas | `x += 1` atualiza um valor |
| Incremento | `++ --` | `i++` aumenta o valor em um |
| Seleção | `condition ? A : B` | Escolhe um valor conforme a condição |
| Ponteiros | `&variable` / `*p` | Obtém um endereço ou acessa seu destino |

Não confunda `=` com `==`. Use parênteses para esclarecer expressões complexas e evite acumular chamadas e efeitos colaterais em uma única instrução. Evite divisão por zero e índices fora dos limites de arrays. `sizeof` fornece um tamanho em bytes; `offsetof` fornece o deslocamento de um membro de estrutura.

## 6. Desvios e laços
{{CODE:4}}

`break` sai de um laço ou switch, `continue` inicia a próxima iteração e `return` sai da função. Use a instrução explícita `fallthrough;` quando quiser prosseguir de um caso de switch para o seguinte; a passagem implícita gera um diagnóstico. Consulte o exemplo completo `gb_control.c`.

## 7. Funções, arrays e estruturas
{{CODE:5}}

Os índices de arrays começam em zero: um array de quatro elementos tem índices de 0 a 3. `player.x` seleciona um membro; `pointer->x` acessa um membro por meio de um ponteiro. O analisador aceita estruturas, uniões e enumerações, mas o layout depende dos tipos e dos atributos `__packed` / `__aligned`. Confira `sizeof` antes de compartilhar dados com o hardware ou com formatos binários.

A ABI Legacy padrão coloca argumentos e variáveis locais em posições fixas. Não presuma recursão ou reentrância em interrupções como em um ambiente desktop. `__stackcall` e `--abi=stack` são opções avançadas de convenção de chamada. Ao combinar convenções, examine os relatórios de ABI e verifique a execução.

## 8. Vários arquivos e o pré-processador
Coloque tipos, constantes e declarações em cabeçalhos e os corpos das funções em arquivos `.c`. Use `#pragma once` ou guardas de inclusão para impedir inclusões repetidas. A compilação condicional oferece `#define`, `#undef`, `#if`, `#ifdef`, `#ifndef`, `#elif`, `#else` e `#endif`.

{{CODE:6}}

`-I` acrescenta uma pasta à busca de cabeçalhos. Incluir o cabeçalho de uma biblioteca não vincula sua implementação: liste os arquivos `.c` necessários no comando de compilação. Selecione as unidades de que precisa; adicionar todos os fontes indiscriminadamente pode duplicar definições de registradores ou tratadores de interrupção.

## 9. ROM, memória e bancos
A ROM guarda código e constantes; a WRAM, variáveis; a VRAM, gráficos; e a OAM, descrições de sprites. A troca de bancos muda qual memória física aparece em determinado endereço da CPU. Um ponteiro de 16 bits sozinho não identifica dados de outro banco.

{{CODE:7}}

`__prg_rom` coloca dados em ROM. Atributos como `__location(0xFF40)` escolhem um endereço fixo, enquanto `__wram` / `__hram` selecionam regiões de memória. Ao usar `#pragma bank` ou `#pragma fixed_bank`, examine o mapa e garanta que o código e os dados usados pelas interrupções continuem acessíveis.

{{CODE:8}}

`--cgb=dmg` declara software voltado ao DMG, `--cgb=cgb` declara software de modo duplo e `--cgb=cgb_only` declara software exclusivo para CGB. Jogos de modo duplo precisam detectar o hardware antes de usar recursos exclusivos do CGB. Uma indicação no cabeçalho não implementa esse comportamento dentro do jogo.

## 10. Atualizações gráficas seguras
VBlank é o intervalo entre quadros da tela. Escritas em VRAM e OAM fora do momento adequado podem corromper a imagem ou perder atualizações. Carregue os recursos iniciais com a tela desligada; nas atualizações regulares, use funções intrínsecas seguras ou a fila de VRAM. Funções marcadas como `_unsafe` ou `_fast` exigem que o código que as chama forneça um intervalo seguro para a transferência.

Alinhe o buffer de DMA da OAM em um limite de 256 bytes. Em GB, `__oam_dma` recebe o endereço de origem. A função intrínseca FC de mesmo nome não recebe argumentos: mantenha as APIs separadas.

## 11. Comandos e arquivos de compilação
`-o` escolhe a saída, `-O0` / `-O1` selecionam a otimização e `--profile=dev|release|test` escolhe um conjunto de configurações. `--no-disasm` desativa a listagem em assembly. `--debug-out=...` e `--trace-out=...` definem onde salvar dados de investigação. Escolha o volume de saída apropriado para uma compilação rápida ou uma análise detalhada.

{{CODE:9}}

`.map` registra nomes e posições; `.funcsizes.txt`, tamanhos de funções; `.dbg2.json` / `.source_map.txt` relacionam posições de execução ao código-fonte; e `.build_report.json` resume a compilação. Gerar explicitamente o JSON de `--emit-ai-metadata` facilita o uso posterior do SARAKURA.

## 12. Comece pelo primeiro erro
Leia o nome do arquivo, a linha e o número de diagnóstico KQ do primeiro erro. Os seguintes podem ser consequências desse erro de sintaxe inicial. Se um símbolo não estiver definido, verifique sua declaração, implementação e inclusão no comando de compilação. Se a ROM exceder o espaço disponível, examine os tamanhos dos recursos e das funções e sua distribuição entre bancos.

{{CODE:10}}

## 13. Assembly embutido
`__asm { ... }` aceita os nomes de instrução do KITAQGB. Isso não significa que qualquer código escrito para outro montador GB seja aceito. Entre os nomes internos está `LD_A_IMM`. Antes de usar assembly embutido, entenda os argumentos, o retorno, os registradores preservados e o comportamento da pilha. O apêndice lista os nomes das instruções e os formatos dos operandos.

{{CODE:11}}

## Localização dos fontes
Os fontes do compilador e o arquivo de projeto ficam na subpasta com o mesmo nome do repositório. O executável fica na raiz, e as bibliotecas, em `lib/`. Consulte a [estrutura de pastas](../GITHUB_SETUP.md) para ver os caminhos e os requisitos de compilação.
