## Executável de linha de comando para Windows
O repositório inclui `kurosaki.exe` na raiz. Baixe o ZIP do repositório e mantenha os avisos de licença junto do executável. Essa ferramenta para Windows x64 não precisa de Rust, Python ou .NET para rodar. Os passos de compilação abaixo servem para reconstruí-la a partir dos fontes. O código próprio do projeto é distribuído por DAISUKE OBA sob a licença MIT; as condições das dependências estão preservadas em BINARY_NOTICES.md e licenses/.

## 1. O que o KUROSAKI faz
KUROSAKI é um emulador de observação NES/Famicom/FDS que lê informações do KITAQFC. Sua ferramenta de terminal inspeciona ROMs, executa programas, grava áudio, diagnostica comportamentos, salva estados, reproduz entradas, lista instruções em assembly e descompila possíveis funções. O alcance das implementações de mapper varia; comece inspecionando a ROM e as informações de suporte.

## 2. Compilar e iniciar
{{CODE:0}}

Os comandos abreviados `kurosaki` abaixo presumem que a pasta do executável esteja no PATH. Caso contrário, substitua o nome do comando por `& "caminho completo do executável"`.

{{CODE:1}}

Use a ROM de saudação do volume 4 para verificar a exibição de texto. `inspect-rom` examina o cabeçalho; `run` faz a CPU e a PPU avançarem. Uma inspeção bem-sucedida não garante uma execução bem-sucedida.

## 3. Conferir o mapper e a placa
`mapper-list` lista os tipos de mapper registrados, `mapper-info` descreve um deles e `audit-board` verifica restrições da placa. O número do mapper relaciona o cabeçalho da ROM a pressupostos sobre as conexões físicas. O nome sozinho não define a capacidade, a presença de CHR-RAM ou o comportamento dos bancos fixos.

{{CODE:2}}

`--allow-unimplemented` permite continuar a observação mesmo diante de elementos não implementados. Uma execução com essa opção não comprova suporte a esses elementos.

## 4. Entrada dos controles
`run --pad1` e `--pad2` usam máscaras brutas de botões NES: A=1, B=2, SELECT=4, START=8, UP=16, DOWN=32, LEFT=64 e RIGHT=128. Some os valores para pressionar botões simultaneamente.

{{CODE:3}}

Esse comando mantém A pressionado por 120 quadros. Use replay para ações em sequência, como passar pelo título, iniciar e confirmar. O exemplo de terminal `replay-record` registra uma execução de referência sem entrada interativa; não é uma gravação de alguém usando uma interface gráfica.

## 5. Estados e reprodução de entradas
{{CODE:4}}

Os estados que permitem retomada usam snapshots versão 2. Mantenha o SHA-256 da ROM correspondente ao do estado. `snapshot-resume` continua de um ponto salvo. `snapshot-rebase` transfere explicitamente um estado para outra ROM compatível, conforme um contrato fornecido. Reutilizar sem verificação um estado antigo após mudar o código ou a organização da RAM pode produzir resultados incorretos; normalmente, repita as mesmas ações desde a inicialização.

## 6. Rastreamentos, diagnósticos e perfis
{{CODE:5}}

Um rastreamento registra o que aconteceu ao longo do tempo; os diagnósticos identificam observações que correspondem a regras; e um perfil mostra onde a execução se concentrou. Em geral, é mais fácil examinar poucos quadros ao redor de uma anomalia do que um rastreamento completo e longo.

Forneça o JSON de depuração da mesma compilação com `--kitaqfc-debug`. Uma observação sem informações de linha do fonte não deve ser interpretada como um rastreamento completo em nível de código-fonte.

## 7. Salvar som e imagens
{{CODE:6}}

Mudanças de registradores, PCM gerado e áudio que soa corretamente são verificações distintas. Registre o mapper ao testar som interno ou de expansão. Um único PNG não comprova movimento nem comportamento dos controles; guarde também a entrada e os estados anterior e posterior.

## 8. Assembly e descompilação
{{CODE:7}}

`disasm` gera sequências de instruções. `decompile` gera possíveis limites de funções, grafos de fluxo de controle, referências e pseudocódigo. Com bancos comutáveis, um endereço de CPU sozinho não identifica uma posição física na ROM. Quando necessário, forneça o estado do mapper com `--snapshot` e use rastreamentos de execução ou anotações como evidência adicional. Isso não recupera perfeitamente o fonte original.

## 9. Conectar ao SARAKURA
{{CODE:8}}

A opção `--emit-diagnostics` do KUROSAKI recebe um **caminho de arquivo JSONL**, assim como no KOKURA. Mantenha separados os rastreamentos de CPU e os arquivos de eventos de diagnóstico.

## 10. Escopo da publicação
KUROSAKI-GUI ainda não foi publicado. Este manual cobre a ferramenta de linha de comando e suas APIs de integração.

## 11. FDS e RAM de salvamento
`fds-inspect` examina a estrutura do disco; `export-assets` exporta recursos. Teste FDS separadamente dos cartuchos NES, pois os requisitos de inicialização, BIOS e acesso a disco são diferentes. Arquivos de bateria `.sav` e estados `.kss.json` têm finalidades distintas; use uma organização de salvamento aceita pela implementação.

{{CODE:9}}

`battery-export` extrai a RAM bruta de salvamento de uma ROM e de um estado correspondentes. `battery-run` carrega essa RAM e inicia como ao ligar o console; ele não restaura o ponto de execução da CPU ou da PPU. Defina o arquivo de saída com `--save-out`. Essas operações exigem uma ROM suportada com RAM de salvamento e não se aplicam a todos os exemplos do manual.
