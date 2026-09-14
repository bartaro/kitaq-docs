## 1. KITAQFC e o compilador GB
KITAQFC usa a etapa de análise do KITAQGB para gerar código para a CPU da família 6502 do NES/Famicom. Ele não converte uma ROM GB em uma ROM NES. Escreva o programa para o vídeo, o som, a memória e o mapper da plataforma de destino.

As verificações registradas executaram exemplos com cópias de estruturas e chamadas comuns de função. Entretanto, **do-while e switch geraram erros de geração de código não suportada para NES**. Uma construção ser reconhecida pelo analisador não comprova que ela possa ser usada nesse destino.

## 2. Requisitos e compilação
{{CODE:0}}

Instale o .NET Framework 4.8 Developer Pack e o Visual Studio Build Tools e use o Developer PowerShell. Os comandos seguintes usam o executável copiado para o repositório clonado de `kitaqfc`. Se usar outro local de compilação, ajuste o caminho. Gráficos CHR e código C são entradas distintas. O `font.chr` do manual é uma conversão de 8 KiB do `ascii.c` do autor.

## 3. Seu primeiro programa
{{CODE:1}}

{{CODE:2}}

O exemplo exibe HELLO WORLD e 042. A função auxiliar `m_wait` confirma a fila de VRAM, espera NMI e restaura a rolagem. As transferências por PPUADDR afetam o estado interno de rolagem; omitir a restauração pode deslocar o texto para uma borda. Aprenda a sequência: desligar a exibição, preparar os recursos, ligar a exibição e sincronizar com NMI.

## 4. Introdução à linguagem
As instruções e expressões do volume GB fornecem uma base comum. FC aceita `unsigned char` e `unsigned short`; `core.h` define `u8`, `u16`, `s8` e `s16`. `fc.h` reúne os cabeçalhos da biblioteca. Aqui, funções sem argumentos podem usar a forma `void main(void)`.

{{CODE:3}}

Mantenha os inteiros dentro dos intervalos de 8 ou 16 bits. Os índices de arrays começam em zero. `fc_aggregate.c` demonstra funções, ponteiros e estruturas; `fc_arithmetic.c`, aritmética; e `fc_control.c`, laços. Não inclua registradores CGB nem funções intrínsecas exclusivas de GB em um programa FC.

## 5. Reescrever construções não suportadas
{{CODE:4}}

Para substituir do-while, execute o corpo do laço uma vez antes de testar sua condição de saída. Um switch simples pode virar uma sequência de if/else. Esses são fragmentos explicativos: forneça suas próprias funções `update` e de estado. Use `fc_control.c` como exemplo de ROM completo.

Não presuma suporte semelhante ao de um ambiente desktop para recursão, chamadas indiretas ou funções com argumentos variáveis. Algumas APIs de retorno de chamada de scene/entity atualmente armazenam ponteiros de função sem invocá-los indiretamente.

## 6. Memória e PPU
A RAM interna da CPU do NES ocupa 0x0000–0x07FF. Seus espelhos acima de 0x0800 não são memória adicional. A pilha do 6502 ocupa a página 1, e cópias da OAM e filas reservam outras regiões. `--nes-local-ram=START:LENGTH` e `--nes-temp-ram=START:LENGTH` são configurações avançadas que exigem inspeção do mapa.

Os endereços da PPU pertencem a um espaço separado. CHR fornece os padrões gráficos, as nametables posicionam os tiles, as tabelas de atributos escolhem grupos de paletas e as paletas guardam códigos de cor. Os atributos do fundo normalmente se aplicam a áreas de 16 × 16 pixels, portanto não funcionam como os atributos de tile do GB.

## 7. NMI e a fila de VRAM
NMI é a interrupção associada ao limite entre quadros da tela. Grandes escritas diretas na PPU durante o desenho podem corromper a imagem. Faça a inicialização direta com a exibição desligada; nas atualizações normais, use `__vramq_put`, `__vramq_copy`, `__vramq_fill` e commit.

{{CODE:5}}

Verifique a capacidade da fila e a validade dos dados de origem. A NMI padrão processa a fila. Uma `__nes_nmi` personalizada precisa preservar o processamento necessário da fila, o trabalho com OAM e os registradores.

## 8. Mappers e organização da ROM
| Seleção | Uso inicial típico |
| --- | --- |
| nrom | Lições pequenas com ROM fixa |
| uxrom / cnrom / axrom | Troca simples de PRG ou CHR |
| mmc1 / mmc3 / mmc5 | Programas maiores e recursos específicos do mapper |
| vrc6 / vrc7 / fme7 | Bancos e os recursos de expansão correspondentes |
| fds | Geração de imagem de disco |

São opções do compilador, não uma tabela de compatibilidade completa do hardware ou do emulador. `--board=surom512` seleciona uma organização específica de placa MMC1; simplesmente completar um arquivo até 512 KiB não implementa essa organização. Use também a auditoria de placa do KUROSAKI.

{{CODE:6}}

Verifique os requisitos da placa para `--battery` / `--no-battery`, capacidade CHR, posição de PRG e chamadas entre bancos. Depois de mudar o mapper ou o espelhamento, teste a inicialização, a rolagem e a troca de dados, além de gerar a ROM.

## 9. FDS, som de expansão e periféricos
FDS envolve organização de arquivos em disco, inicialização, sobreposições de código e salvamento. Consulte `fds_manifest_sample.json` e os cabeçalhos FDS. Prepare qualquer BIOS necessária no seu próprio ambiente de execução; a distribuição pública não contém BIOS.

Chamar uma operação sonora de VRC6 ou VRC7 não altera a configuração de mapper da ROM. Use um mapper compatível com o som de expansão escolhido. Para periféricos, teste separadamente a leitura de entrada, o estado da conexão e os efeitos no caminho dos controles comuns.

## 10. Diagnósticos e resultados de compilação
Os diagnósticos KQ e comandos de desenvolvimento como `symfind`, `src2asm` e `romdiff` se parecem com os equivalentes GB. Algumas opções de ajuda herdadas de GB podem não corresponder a recursos NES implementados. O dicionário FC é coletado separadamente a partir dos fontes e cabeçalhos FC.

Avisos como KQ2421, sobre operações diretas na PPU, podem aparecer até durante a inicialização com a exibição desligada. Não prejudique uma inicialização segura apenas para eliminar um aviso: examine o momento das escritas e os registros de execução. Zero erros e zero avisos são resultados diferentes.

## Localização dos fontes
Os fontes do compilador e o arquivo de projeto ficam na subpasta com o mesmo nome do repositório. O executável fica na raiz, e as bibliotecas, em `lib/`. Consulte a [estrutura de pastas](../GITHUB_SETUP.md) para ver os caminhos e os requisitos de compilação.
