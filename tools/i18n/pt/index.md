## Boas-vindas
KITAQGB começou como um **fork do NORCAL**, compilador C para NES ligado à Zachtronics. A partir dessa base, o projeto desenvolve um compilador da família C para Game Boy e Game Boy Color, adaptando a geração de código, a memória, o vídeo, o áudio e os bancos de ROM a essas máquinas. Reconhecemos o projeto original e seu autor, Keith Holman.

{{ORIGIN}}

O NORCAL foi desenvolvido em conexão com a versão de HACK*MATCH para NES. Consulte as apresentações do autor sobre [NORCAL: A C Compiler for the NES](https://keithholman.net/nes-compiler.html) e [HACK*MATCH para NES](https://trashworldnews.com/hack-match/). O histórico do projeto e a explicação do nome seguem o README fornecido pelo autor.

## Como usar estes manuais
Como nos manuais dos primeiros computadores, esta coleção começa com programas curtos que você pode digitar, compilar e executar. Primeiro veja o resultado; depois, aprenda como a máquina funciona. Não é preciso decorar todos os termos antes de começar.

1. Comece pelo primeiro programa do volume 1, para GB, ou do volume 4, para FC.
2. Use o volume 2 ou o volume 5 para acrescentar controles, gráficos e som.
3. Observe a execução com KOKURA ou KUROSAKI e organize os diagnósticos com SARAKURA.
4. Se já souber o nome de uma função, use a busca do volume ou o dicionário da API.

A sintaxe da linguagem, as funções intrínsecas do compilador, as funções de biblioteca e os comandos de terminal têm seções próprias. Os volumes dos compiladores também incluem índices de instruções da CPU. Nomes parecidos nas versões GB e FC não garantem os mesmos argumentos nem o mesmo comportamento.

## Os sete volumes
| Volume | Entrada | Saída ou finalidade |
| --- | --- | --- |
| KITAQGB | Código C e recursos | ROMs GB/CGB, mapas e informações de compilação |
| Biblioteca KITAQGB | Chamadas do código do jogo | Gráficos, som, entrada, comunicação e serviços de jogo |
| KOKURA | ROMs GB/CGB | Execução, imagens, áudio, estados e observações |
| KITAQFC | Código C e recursos CHR | Imagens NES/FDS e informações de compilação |
| Biblioteca KITAQFC | Chamadas do código do jogo | Gráficos, som e dispositivos NES |
| KUROSAKI | Imagens NES/FDS | Execução, gravação e análise |
| SARAKURA | Informações de compilação e eventos de diagnóstico | Relatórios, planos de correção e planos de novos testes |

## A fonte incluída
As 26 letras maiúsculas, 10 algarismos, 26 letras minúsculas e 30 símbolos vêm do arquivo [ascii.c](samples/assets/ascii.c) do autor. Nenhum desenho de caractere foi acrescentado. Os 92 glifos originais foram preservados; consulte o [mapa de conversão](verification/font_conversion.json) e o [atlas de tiles](verification/font_source_atlas.png). O espaço usa um tile vazio. A barra invertida e a barra vertical não fazem parte da fonte fornecida e aparecem em branco. `gb_font.c` e `fc_font.c` exibem todos os glifos disponíveis.

## Edição e verificação
Esta edição se baseia na **cópia local do código-fonte de 14 de setembro de 2026**. “Mais recente” se refere a essa cópia, não a um acompanhamento automático das futuras alterações no GitHub. O inventário de referência registra as identificações dos fontes e dos executáveis. Afirmações de suporte ou verificação em READMEs antigos não são tratadas automaticamente como garantias atuais.

Uma compilação bem-sucedida significa que uma ROM foi produzida. Uma verificação de execução significa que um emulador avançou pelo número indicado de quadros. Comparações de pixels, comportamento dos controles e testes de som são registrados separadamente. Isso não garante compatibilidade com todos os periféricos ou consoles físicos; os avisos continuam disponíveis nos registros.

A distribuição pública atual não inclui as interfaces gráficas de KOKURA, KUROSAKI nem PLITA. Utilize os núcleos, as ferramentas de linha de comando e as APIs de integração publicados.

## Preparar a pasta de trabalho
Os exemplos usam **Windows PowerShell**. Salve os arquivos C como texto UTF-8. A pasta atual é aquela em que você executa o comando. Coloque entre aspas os caminhos com espaços e, quando necessário, use `& "caminho"` para chamar um executável. Clone os repositórios em pastas irmãs, conforme as [instruções de configuração do GitHub](../GITHUB_SETUP.md), e execute os comandos que envolvem vários projetos a partir da pasta que contém esses repositórios.

{{CODE:0}}

Substitua `game.c`, `game.gb` e `game.nes` pelos nomes dos seus arquivos. Indicações como `<ROM>` são marcadores: não digite os sinais de menor e maior. Em geral, os comandos aparecem em uma única linha. A continuação de linha com barra invertida do Bash não é sintaxe do PowerShell.

## Correções de compilador usadas nesta edição
A compilação dos exemplos revelou uma colisão de rótulos locais internos no KITAQGB e problemas de preservação de valores intermediários e de retorno entre chamadas no KITAQFC. As verificações registradas neste manual usaram os compiladores corrigidos, incluindo o exemplo de conjunto de objetos GB e os exemplos FC de funções e estruturas. Essas correções não comprovam suporte a todas as construções de C. Consulte o [registro de verificação](verification.html) de cada exemplo.

## Ler, imprimir e publicar o HTML
Abra `index.html` na pasta baixada para ler sem conexão. Estilos, busca, exemplos e imagens de verificação usam arquivos locais; não é necessário um CDN externo. Mantenha a pasta inteira em vez de copiar arquivos HTML isolados. O botão de impressão prepara um layout sem a coluna de navegação.

O repositório `kitaq-docs` contém o site dos manuais. A visualização de arquivos do GitHub normalmente mostra o código HTML; o GitHub Pages exibe o site renderizado. Consulte o README do repositório para obter instruções de publicação e clonagem. Esta tradução contém os mesmos sete volumes, entradas de API, exemplos e referências de verificação da edição japonesa. Os trechos de código e as saídas registradas das ferramentas mantêm sua redação original quando a tradução prejudicaria a identificação exata do fonte ou da resposta do comando.
