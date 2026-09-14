## Executável de linha de comando para Windows
O repositório inclui `sarakura.exe` na raiz. Baixe o ZIP do repositório e mantenha os avisos de licença junto do executável. Essa ferramenta para Windows x64 não precisa de Rust, Python ou .NET para rodar. Os passos de compilação abaixo servem para reconstruí-la a partir dos fontes. O código próprio do projeto é distribuído por DAISUKE OBA sob a licença MIT; as condições das dependências estão preservadas em BINARY_NOTICES.md e licenses/.

## 1. A função do SARAKURA
SARAKURA combina informações de compilação com eventos de diagnóstico do emulador e os apresenta de uma forma útil para investigar correções e repetir testes. Ele não executa ROMs como um emulador nem altera silenciosamente seu código C.

## 2. Compilar a ferramenta
{{CODE:0}}

Os comandos abreviados `sarakura` presumem que o executável esteja no PATH. Caso contrário, use o caminho do arquivo compilado. Escolha `gb analyze` para GB ou `fc analyze` para FC.

## 3. Sua primeira análise
São necessárias duas entradas: `--metadata` recebe o JSON da compilação e `--events` recebe o JSONL de eventos de diagnóstico da execução. JSONL contém um objeto JSON por linha.

{{CODE:1}}

Abra o `report.html` gerado em um navegador. Confira a plataforma, os quadros observados e as contagens de erros e avisos antes de ler os diagnósticos individuais. `--frames` descreve as condições da análise; ele não pede ao SARAKURA que execute uma ROM por esse número de quadros.

## 4. Inspecionar as entradas primeiro
{{CODE:2}}

Resolva primeiro os arquivos ilegíveis, as plataformas incompatíveis e os tipos de evento não suportados. Passar um relatório comum do emulador como arquivo de eventos não o transforma em uma entrada válida de diagnóstico.

## 5. Interpretar os diagnósticos
Um erro merece prioridade; um aviso pode indicar um problema conforme as circunstâncias; e um item informativo fornece contexto. A gravidade ajuda a organizar a investigação, mas não compreende toda a intenção do jogo. Uma observação de contador de programa repetido, sozinha, pode não distinguir um laço normal de espera na tela de título de um travamento.

Compare o hash da ROM, a sequência de entrada, a cena, a tela, o som e a posição no fonte. Mantenha as condições iguais antes e depois da correção; caso contrário, menos diagnósticos podem significar apenas que outra cena foi executada.

## 6. Arquivos de saída
As explicações incorporadas, as sugestões de diagnóstico e as instruções de correção são geradas em inglês, e o HTML declara `lang="en"`. Textos do usuário e identificadores de eventos não são traduzidos automaticamente. A ocultação padrão substitui alguns rótulos e caminhos do projeto; ela não anonimiza todos os endereços ou observações. Inspecione os relatórios antes de publicar análises de entradas privadas.

| Arquivo | Finalidade |
| --- | --- |
| ai_diagnostics.json | Diagnósticos normalizados para processamento automático |
| diagnostic_summary.json | Contagens e resumo |
| report.html | Relatório para leitura no navegador |
| repair_prompt.md | Contexto inicial para investigar uma correção |
| repair_plan.json / .md | Ordem e alvos das correções |
| automation_plan.json / .md | Plano de trabalho conforme as capacidades das ferramentas |
| retest_plan.json | Plano para repetir as verificações |
| repro_bundle.zip | Pacote de informações para reproduzir o problema |

Produzir um plano não é executá-lo. Depois de alterar o código C ou uma ROM, rode novamente o compilador, o emulador e o SARAKURA.

## 7. Catálogos, filtros e cobertura
{{CODE:3}}

`catalog` lista as regras de diagnóstico, `pack-plan` as agrupa por área e `coverage` examina quais eventos correspondentes foram observados. Uma entrada no catálogo não garante que o emulador atual emita aquele evento.

{{CODE:4}}

`--diagnostic-rule` seleciona um nome de evento ou identificador do catálogo, `--phase` seleciona uma etapa e `--diagnostic-pack` seleciona uma área. Tirar um diagnóstico da visualização por meio de um filtro não resolve sua causa.

## 8. Comparar antes e depois
{{CODE:5}}

Os resultados são classificados como novos, resolvidos, melhorados, persistentes ou agravados. Distinga os problemas que permaneceram dos que foram introduzidos. Mantenha fixos a entrada, a quantidade de quadros e os filtros de diagnóstico durante as comparações.

## 9. Validação e integração contínua
{{CODE:6}}

A integração contínua automatiza verificações repetíveis. `ci-summary` só altera o código de saída do processo quando `--enforce` é informado; nos demais casos, leia o veredicto no JSON. Em analyze, `--fail-on error` retorna um código diferente de zero quando há erros. O padrão `never` não faz o processo falhar por causa dos diagnósticos, então escolha explicitamente a política de CI. Com `warn`, os avisos também causam falha.

```powershell
sarakura ci-summary --diagnostics .\out\report --fail-on error --enforce
if ($LASTEXITCODE -ne 0) { throw "The diagnostic failure condition was met" }
```

A validação bem-sucedida de um esquema verifica o formato dos dados. Para confirmar que um jogo funciona como deveria, também é preciso testar os controles, a imagem e o som.

## 10. Trabalhar com arquivos de reprodução
`normalize-events` normaliza os registros de eventos. `inspect-repro` examina um pacote de reprodução. Antes de compartilhá-lo, confira se as informações correspondem à ROM pretendida e incluem os passos de entrada necessários. `--allow-project-labels` mantém explicitamente os rótulos e identificadores derivados do projeto.

## 11. Entradas mínimas para praticar
O manual inclui pequenos exemplos de metadados de compilação e eventos GB/FC. Abra o [relatório sintético GB](verification/sarakura-gb-synthetic.html) ou o [relatório sintético FC](verification/sarakura-fc-synthetic.html). `samples/sarakura_demo.ps1` demonstra como analisá-los. São entradas sintéticas para aprender o formato, não evidências capturadas de uma ROM real. Para testar ROMs reais, use eventos registrados por KOKURA ou KUROSAKI.

## 12. Um ciclo de correção e novo teste
1. Reproduza o problema com a mesma ROM e a mesma entrada, guardando registros e imagens.
2. Organize as possíveis causas com SARAKURA e examine o fonte correspondente.
3. Faça uma alteração específica que trate a causa.
4. Recompile e repita as mesmas ações.
5. Compare baseline-delta com as imagens, o áudio e o comportamento do jogo.

Mantenha esse ciclo pequeno para que cada mudança e seu efeito sejam compreensíveis.
