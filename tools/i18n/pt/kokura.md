## Executável de linha de comando para Windows
O repositório inclui `kokura-cli.exe` na raiz. Baixe o ZIP do repositório e mantenha os avisos de licença junto do executável. Essa ferramenta para Windows x64 não precisa de Rust, Python ou .NET para rodar. Os passos de compilação abaixo servem para reconstruí-la a partir dos fontes. O código próprio do projeto é distribuído por DAISUKE OBA sob a licença MIT; as condições das dependências estão preservadas em BINARY_NOTICES.md e licenses/.

## 1. O que o KOKURA faz
KOKURA emula programas GB/CGB e registra observações de imagem, áudio, execução da CPU, memória, bancos, entrada e eventos de diagnóstico. Este manual usa o nome atual `kokura-cli.exe`; não presuma que referências antigas a `kokuradbg` indiquem o executável desta distribuição.

## 2. Compilar e executar sua primeira ROM
{{CODE:0}}

Instale Rust e Cargo. Se precisar apenas da ferramenta de terminal, compile a crate indicada. Use a ROM de saudação do volume 1. O número padrão de quadros é um; defina `--run-frames` para alcançar a cena desejada. O valor conta quadros emulados, não segundos de espera.

## 3. Escolher DMG ou CGB
`--hardware auto` é o padrão; `dmg` e `cgb` permitem escolhas explícitas. Teste ROMs de modo duplo nos dois modos. Uma ROM exclusiva para CGB se recusar a iniciar como DMG não indica, por si só, defeito no emulador.

{{CODE:1}}

## 4. Fornecer comandos do controle
`--input` mantém uma combinação de botões pressionada; `--input-seq` fornece uma sequência ao longo do tempo. Os nomes dos botões são `A,B,START,SELECT,UP,DOWN,LEFT,RIGHT`; use `NONE` nos intervalos sem botões pressionados. No PowerShell, coloque entre aspas as sequências que contêm ponto e vírgula.

{{CODE:2}}

Inclua um intervalo com os botões soltos para testar a detecção de novas pressões. Manter A pressionado por 120 quadros é diferente de pressioná-lo 120 vezes. Na lição do contador de entrada, a sequência acima deve aumentar o contador apenas uma vez.

## 5. Imagens, vídeo e áudio
`--png` salva a tela final. `--screenshot`, junto de `--screenshot-frames`, captura quadros específicos. `--record-video` grava vídeo e `--record-wav` grava áudio. Um WAV silencioso é esperado em um programa de saudação que não usa a APU.

{{CODE:3}}

Os intervalos usam `start:end`. Guarde o relatório para distinguir o número de quadros acumulado em um estado carregado das posições da execução atual. Verifique separadamente o som audível, a afinação, as interrupções e o recorte de amplitude. Uma gravação do emulador não comprova igualdade amostra por amostra com o hardware físico.

## 6. Salvar e retomar estados
{{CODE:4}}

Normalmente, use a mesma ROM e a mesma versão do emulador. O estado do emulador é diferente dos dados de salvamento do próprio jogo. Os arquivos KQS da ferramenta de terminal e o estado JSON da API C têm formatos distintos; mudar a extensão não os torna intercambiáveis.

## 7. Observar símbolos e memória
Arquivos auxiliares `.map`, `.source_map.txt`, `.dbg2.json` e `.build_report.json` podem ser detectados ao lado da ROM. Mantenha a ROM com os arquivos da mesma compilação: dados de outra versão podem levar a interpretações erradas.

{{CODE:5}}

`wram` é o nome da região de observação, 0xC000 é o endereço inicial e 0x40 é seu tamanho. Regiões pequenas facilitam a identificação das variáveis alteradas. `--watch-baseline-mode` escolhe a comparação com os valores iniciais, o quadro anterior ou uma referência nomeada.

## 8. Condições de parada, reprodução e análise reversa
`--breakpoint`, `--watchpoint`, `--run-until` e `--snapshot-at` param a execução ou salvam um estado quando uma condição é atingida. A sintaxe dos argumentos difere entre essas opções; consulte a referência e a ajuda capturada abaixo.

{{CODE:6}}

Encontre a primeira divergência e observe um intervalo menor ao redor dela. `--decompile-out` gera pseudocódigo e informações de fluxo de controle; `--disassemble-out` mostra instruções de CPU. A descompilação não recupera perfeitamente o código C original nem os nomes das variáveis.

## 9. Enviar diagnósticos ao SARAKURA
{{CODE:7}}

A opção `--emit-diagnostics` do KOKURA recebe um **nome de arquivo JSONL**, como `out/gb_events.jsonl`. Um relatório JSON comum de execução ou um JSONL de rastreamento de CPU não equivale a um arquivo de eventos de diagnóstico.

## 10. Sessões de comunicação
`pair` modela duas máquinas. `four_player_adapter` representa uma organização lógica em que o host seleciona um participante. `dmg07` modela o protocolo do adaptador físico DMG-07. Forneça o JSON do trabalho com `--link-job` ou configure as sessões usando `--link-topology` e `--link-session`.

{{CODE:8}}

Cada ROM precisa implementar a comunicação. Executar dois programas comuns de saudação não testa a biblioteca de link. Registre a ROM, a posição de jogador, a entrada e o estado de cada sessão e indique quais comportamentos do dispositivo físico ainda não foram testados.

## 11. Aplicativos externos
A ABI C publicada está em `kokura-capi`; o acesso por Python é oferecido pela ponte e pela crate Python incluídas. Antes de investigar uma integração, estabeleça um caso mínimo reproduzível pela linha de comando.

## 12. Ler os relatórios na ordem
Confira primeiro os quadros executados e o motivo da parada; depois, a tela, o resultado dos controles, o som, os erros e avisos e o perfil de execução. Uma observação longa de uma tela de título sem entrada pode naturalmente gerar avisos de tela estática ou contador de programa repetido. Compare os avisos com a cena pretendida, em vez de tratar automaticamente cada um como falha.
