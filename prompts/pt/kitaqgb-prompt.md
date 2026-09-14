# Desenvolvimento de jogos com KITAQGB, KOKURA e SARAKURA

Preencha os requisitos e envie este documento inteiro ao assistente de IA. Os comandos pressupõem que os repositórios `kitaqgb`, `kitaqfc`, `kokura`, `kurosaki`, `sarakura` e `kitaq-docs`, além do projeto `game-gb` ou `game-fc`, estejam na mesma pasta pai. Execute os comandos nessa pasta e ajuste os caminhos ao ambiente real.

## Requisitos

- Nome do jogo: <preencher>
- Gênero e mecânica principal: <preencher>
- Controles e condições de sucesso e fracasso: <preencher>
- Telas, fases, inimigos e itens obrigatórios: <preencher>
- Estilo visual, música e efeitos sonoros: <preencher e indicar os materiais fornecidos>
- Salvamento, comunicação, periféricos e outros requisitos: <preencher ou nenhum>
- Pasta do projeto: <preencher>
- Condições de redistribuição: <por exemplo, código e materiais originais que possam ser publicados sob a licença MIT>

- Plataforma: <Game Boy original / suporte a GB e CGB / somente CGB>
- Meta de desempenho: <por exemplo, 60 atualizações da lógica por segundo em situações normais; definir o comportamento aceitável nas cenas mais pesadas>

## Trabalho solicitado

Implemente o jogo com KITAQGB e suas bibliotecas. Use KOKURA para execução e depuração, e SARAKURA para organizar os diagnósticos e comparar os resultados antes e depois de uma correção.

Repita este ciclo até atender aos critérios de aceitação: detalhar a especificação → implementar uma pequena mudança → compilar → aplicar entradas e observar → investigar a causa → corrigir → testar novamente nas mesmas condições. Um plano, a apresentação do código ou uma compilação bem-sucedida não significam que o trabalho está concluído.

### Verificar o ambiente e os critérios de aceitação

1. Leia as instruções da pasta de trabalho, os README, os manuais HTML e os cabeçalhos e implementações das bibliotecas usadas. Registre os caminhos dos executáveis e suas versões ou hashes SHA-256. Confira os comandos na saída real de `--help` e as APIs no código-fonte.
2. Defina critérios verificáveis para entradas, imagem, som, progressão e frequência de atualização. Por exemplo: pressionar e soltar START inicia a partida; uma colisão tira uma vida; a pausa silencia o áudio especificado e, ao continuar, a reprodução é retomada.
3. Pergunte apenas sobre ambiguidades relevantes. Tome decisões comuns e reversíveis de implementação de forma autônoma. Não reduza os requisitos nem flexibilize os critérios de aceitação.
4. Primeiro execute um pequeno exemplo fornecido pelo compilador, pelo emulador e pelo SARAKURA. Isso verifica a integração entre as ferramentas, não a conclusão do jogo solicitado.

### Implementar uma primeira versão jogável

- Use o dialeto C do KITAQGB e `void main()`. Não presuma que APIs de C para desktop ou do GBDK estejam disponíveis. Inclua as implementações `.c` necessárias, não apenas as declarações; verifique inicialização, unidades, sinal, faixas, tempo de vida dos buffers e bancos de ROM.
- Planeje atualizações de VRAM/OAM, VBlank, interrupções, pilha, bancos de ROM/WRAM e limites de tiles e sprites. A capacidade total e livre da fila de transferências é diferente da capacidade e do espaço livre da VRAM física.
- Um jogo para DMG não pode depender de funções exclusivas do CGB. Se houver suporte aos dois modos, teste cada um separadamente.
- Use a fonte original fornecida em `ascii.c` para letras, números e símbolos, e confira a correspondência entre caracteres e tiles.

- Primeiro conecte inicialização, título, personagem controlável, sucesso ou fracasso e reinício. Amplie o conteúdo depois.
- Preserve os originais editáveis de gráficos, música e efeitos, além das etapas de geração. Confirme que a compilação realmente utiliza os dados exportados.
- Escreva comentários no código em inglês e relatórios de andamento em português do Brasil. Mantenha os relatórios padrão do SARAKURA em inglês.

### Relacionar cada compilação à sua execução

Separe as saídas por iteração, como em `out/iter-001`. Registre comandos, códigos de saída e hashes de código, materiais, ferramentas, ROM e metadados. Nunca execute uma ROM antiga depois de uma compilação com falha. Mapas, mapas de código-fonte e informações de depuração devem ser da mesma compilação da ROM.

O exemplo a seguir faz uma verificação básica em DMG. Prepare `main.c` e as implementações de biblioteca necessárias; adapte as opções e a sequência de entrada ao jogo.

```powershell
$iteration = '.\game-gb\out\iter-001'
New-Item -ItemType Directory -Force $iteration | Out-Null

# Include all additional implementation units required by the game.
& '.\kitaqgb\kitaqgb.exe' '.\game-gb\src\main.c' `
  -I '.\kitaqgb\lib' -o "$iteration\game.gb" `
  --profile=dev --rst-disable --stack-bank=fixed --no-disasm `
  "--emit-ai-metadata=$iteration\build.json"
if ($LASTEXITCODE -ne 0) { throw 'Build failed; inspect the build log.' }

# This sequence presses START once, with released intervals on both sides.
& '.\kokura\kokura-cli.exe' "$iteration\game.gb" `
  --hardware dmg --run-frames 300 `
  --input-seq 'NONE:60;START:1;NONE:239' `
  --png "$iteration\frame.png" --record-wav "$iteration\audio.wav" `
  --dump-report "$iteration\run.json" `
  --emit-diagnostics "$iteration\events.jsonl"
if ($LASTEXITCODE -ne 0) { throw 'Emulator run failed; inspect the run log.' }

& '.\sarakura\sarakura.exe' gb analyze `
  --metadata "$iteration\build.json" --events "$iteration\events.jsonl" `
  --frames 300 --out "$iteration\analysis" --fail-on error
if ($LASTEXITCODE -ne 0) { throw 'Inspect the analysis report and fix the cause.' }
```


`--hardware dmg` seleciona o Game Boy original. Ao testar CGB ou suporte aos dois modos, mantenha o cabeçalho da ROM e a configuração de hardware do emulador coerentes. A sequência pressiona START uma vez entre intervalos com os botões soltos. Executar 300 quadros não equivale a testar o jogo inteiro.

### Verificar imagem, som, estado e desempenho

- Salve cenários que diferenciem pressionar, segurar e soltar. Percorra todos os caminhos especificados: inicialização, início, movimento, ações, colisões, rolagem, mudanças de fase, fim de jogo, reinício, pausa e, quando aplicável, salvamento ou comunicação.
- Preserve PNGs de quadros relevantes, entradas, relatórios de execução, JSONL de diagnóstico, WAVs e as observações necessárias de estado ou memória. Verifique os quadros alcançados e o motivo da parada. Abra as imagens de fato: uma captura isolada não comprova movimento ou resposta aos controles. Compare contadores, posições e mudanças de estado com o esperado; confira bordas da tela, limites de tiles e atributos e cenas com muitos sprites.
- Verifique música, efeitos, reprodução simultânea, cortes, pausa e retomada. Gerar um WAV não comprova que o áudio está correto. Se não puder ouvi-lo, diferencie os testes numéricos ou de forma de onda das qualidades audíveis ainda não verificadas.
- Meça cenas pesadas, trabalho da CPU de destino, atualizações e transferências; em FC, inclua o trabalho de NMI. A velocidade do emulador no computador não é a frequência do jogo nem prova de desempenho no hardware real. Continuar com `--allow-unimplemented` não comprova suporte ao recurso ausente.

### Analisar, corrigir e testar novamente

- Forneça ao SARAKURA os metadados da ROM testada e o JSONL de diagnóstico daquela execução. Um rastreamento de CPU ou relatório comum não serve como substituto. `--frames` define condições de análise; SARAKURA não executa a ROM nem modifica o código automaticamente.
- Leia `report.html`, `ai_diagnostics.json`, `repair_prompt.md` e `retest_plan.json`. Compare os diagnósticos com reprodução, imagens, áudio e código. Separe localizações ou causas inferidas de fatos verificados e laços de espera normais de travamentos. Avalie cada aviso e registre eventos não suportados ou limites da análise. Não oculte avisos com filtros nem encurte testes para obter aprovação.
- Reduza falhas a casos mínimos, corrija a causa e recompile. Se a origem estiver no compilador ou emulador, isole o defeito do código do jogo e acrescente verificação de regressão à correção da ferramenta.
- Repita os testes com as mesmas entradas, semente aleatória, máquina e padrão de vídeo, mapper, quadros observados e configurações de diagnóstico. Cada ROM precisa dos metadados correspondentes; não reutilize estados salvos indiscriminadamente após mudar código ou organização da RAM.

```powershell
& '.\sarakura\sarakura.exe' baseline-delta `
  --baseline '.\game-gb\out\iter-001\analysis' `
  --current '.\game-gb\out\iter-002\analysis' `
  --out '.\game-gb\out\delta.json' --markdown '.\game-gb\out\delta.md' `
  --fail-on-new error --fail-on-regression error --enforce
```


Use as diferenças de diagnóstico junto com a avaliação de controles, gráficos e áudio. Se a mesma falha se repetir, reavalie as evidências e a hipótese em vez de continuar fazendo mudanças arbitrárias.

### Critérios de conclusão e entregáveis

Repita todos os cenários obrigatórios com a ROM final compilada a partir do código e das configurações entregues. Invencibilidade, entradas automáticas de teste ou outro mapper, isoladamente, não verificam uma partida normal na versão final. Entregue uma tabela relacionando requisitos e testes, explique os avisos restantes e identifique o que não foi verificado ou não é suportado. Se não houve teste em hardware físico, informe isso explicitamente.

Entregue código-fonte, identificação de ferramentas e bibliotecas, materiais editáveis, scripts reproduzíveis de compilação e testes, ROM, evidências finais e um README com instalação, controles e limitações conhecidas. Inclua replays e o programa de testes quando necessários. Publique ou envie arquivos externamente apenas no escopo autorizado de forma explícita. Remova compilações intermediárias e rastreamentos temporários desnecessários após a verificação, preservando fontes, materiais, entregáveis e evidências de regressão necessárias.

Se o ambiente ou as permissões impedirem uma verificação obrigatória, informe os passos exatos para reprodução e a ação necessária. Não marque o trabalho como concluído.
