# Manuais da KITAQ SERIES

[English](README.md#english) | [日本語](README.md#japanese) | **Português (Brasil)**

<!-- ai-prompts:start -->
## Prompts para desenvolver jogos com IA

Preencha os requisitos e envie o prompt completo ao assistente de IA. Ele abrange implementação, testes no emulador, análise com SARAKURA e verificação das correções.

[KITAQGB](https://bartaro.github.io/kitaq-docs/pt/loop-engineering.html#gb) · [KITAQFC](https://bartaro.github.io/kitaq-docs/pt/loop-engineering.html#fc)
<!-- ai-prompts:end -->

## Abrir o manual de cada ferramenta

Os links abaixo levam diretamente ao volume em português brasileiro.

| Volume | Conteúdo |
| --- | --- |
| [KITAQGB](https://bartaro.github.io/kitaq-docs/pt/kitaqgb.html) | Sintaxe, operações intrínsecas e compilação para Game Boy. |
| [Biblioteca KITAQGB](https://bartaro.github.io/kitaq-docs/pt/gb-library.html) | Funções das bibliotecas para Game Boy. |
| [KOKURA](https://bartaro.github.io/kitaq-docs/pt/kokura.html) | Execução, entrada, observação e gravação. |
| [KITAQFC](https://bartaro.github.io/kitaq-docs/pt/kitaqfc.html) | Sintaxe, operações intrínsecas e compilação para Famicom/NES. |
| [Biblioteca KITAQFC](https://bartaro.github.io/kitaq-docs/pt/fc-library.html) | Funções das bibliotecas para Famicom/NES. |
| [KUROSAKI](https://bartaro.github.io/kitaq-docs/pt/kurosaki.html) | Execução, salvamento e análise. |
| [SARAKURA](https://bartaro.github.io/kitaq-docs/pt/sarakura.html) | Diagnósticos e repetição de testes. |
| [Verificação](https://bartaro.github.io/kitaq-docs/pt/verification.html) | Registros de compilação, execução e comparação de imagens. |

## Manuais em HTML

Os sete volumes estão disponíveis em nove idiomas e descrevem o código-fonte de 14 de setembro de 2026. Todas as edições incluem as mesmas 1.053 entradas de API e 47 programas de exemplo completos. Abra `pt/index.html` em português, `en/index.html` em inglês ou `index.html` em japonês. Cada volume permite mudar de idioma. Os registros de verificação identificam os fontes, os executáveis e as condições dos testes.

Trechos dos fontes originais e saídas capturadas das ferramentas são mantidos sem alterações. Consulte as [instruções de obtenção e organização dos repositórios](GITHUB_SETUP.md) e as [verificações de publicação](PUBLICATION_CHECKS.md). Os arquivos HTML podem ser lidos offline e oferecem busca dentro do volume, cópia de código e impressão.

O sumário e o início do primeiro volume explicam o duplo sentido do nome KITAQGB e reconhecem sua origem no NORCAL. As letras, os algarismos e os símbolos usam o arquivo fornecido `samples/assets/ascii.c`. Para GB, os caracteres são reorganizados na ordem ASCII; para FC, são convertidos para os planos de bits do NES. O desenho dos caracteres é preservado.

Os textos, exemplos adicionais e ferramentas de geração usam a licença MIT. Em 12 de setembro de 2026, o autor confirmou que os 92 caracteres fornecidos são de sua autoria e podem ser publicados sob MIT. Os trechos dos programas originais mantêm seus avisos de direitos autorais. Redistribua os [avisos de terceiros](THIRD_PARTY_NOTICES.md) e as licenças aplicáveis junto com o material.

Os manuais incluem a [licença original em inglês](LICENSE) e uma [tradução de referência em japonês](LICENSE.ja). Os [avisos de terceiros](THIRD_PARTY_NOTICES.md) também apontam para as licenças em japonês de cada ferramenta. Em caso de divergência, prevalece o original em inglês. As distribuições binárias exigem ainda as licenças próprias de suas dependências. A autorização para publicar os manuais não significa que todas as ferramentas e dependências possam ser redistribuídas apenas sob MIT.

## Compilar os exemplos

Clone os repositórios como pastas irmãs dentro de uma mesma pasta e execute os comandos a partir dela. O arquivo [GITHUB_SETUP.md](GITHUB_SETUP.md) mostra a organização. Use os compiladores fornecidos ou recompile-os seguindo os manuais; esta edição inclui correções nos compiladores.

```powershell
.\kitaq-docs\samples\build.ps1 -Only gb_hello,fc_hello
.\kitaq-docs\samples\build.ps1
```

Se os fontes estiverem em outro local, informe `-Root "caminho absoluto da árvore de fontes"`. Use `-GbCompiler` e `-FcCompiler` para selecionar executáveis em outras pastas. Por padrão, as ROMs e os logs ficam em `samples/out/<sample-id>`. Este pacote de manuais não inclui executáveis dos compiladores, ROMs comerciais nem BIOS.

`samples/api-fragments` contém trechos que precisam ser inseridos em programas com inicialização e argumentos válidos. A compilação em lote de ROMs abrange os 47 programas de `samples/manifest.json`. Cada volume distingue APIs que só têm declaração, trechos não executados e recursos ainda não verificados em hardware físico.

## Publicar no GitHub

1. Coloque o conteúdo desta pasta na raiz do repositório ou em uma pasta `docs`.
2. Envie juntos `index.html`, os sete volumes, `verification.html`, `loop-engineering.html`, `prompts`, as pastas de idiomas, `assets`, `samples`, `reference`, `verification`, os READMEs e os avisos de licença. Inclua `.nojekyll`.
3. Em Settings → Pages → Build and deployment, escolha Deploy from a branch no campo Source.
4. Selecione a branch enviada e `/ (root)` ou `/docs`, conforme a organização, e salve.
5. Quando a publicação terminar, abra o endereço exibido em Pages e confira os links do sumário e dos volumes.

Consulte as [instruções do GitHub sobre a origem da publicação](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site). `manual/_manual_work` é uma área local de compilação e verificação e fica fora da publicação.

## Editar e atualizar

O texto em japonês fica em `tools/chapters.py`; o inglês, em `tools/en/*.md`. `tools/generate_en.py` gera a edição inglesa, `tools/generate.py` contém os dicionários de API e a geração de páginas, e `assets/manual.css` define o estilo. Use Python para atualizar os manuais.

```powershell
python -B kitaq-docs/tools/collect.py
python -B kitaq-docs/tools/make_samples.py
python -B kitaq-docs/tools/catalog.py
python -B kitaq-docs/tools/generate.py
python -B kitaq-docs/tools/generate_en.py
foreach ($language in @('ko','zh-CN','zh-TW','es','pt','fr','de')) {
    python -B kitaq-docs/tools/generate_i18n.py --language $language
    if ($LASTEXITCODE -ne 0) { throw "Manual generation failed: $language" }
}
python -B kitaq-docs/tools/check_site.py
python -B kitaq-docs/tools/check_bilingual.py
```

A coleta dos fontes e a compilação exigem as árvores de código originais e suas ferramentas. A conversão da fonte e as comparações de pixels usam Pillow. Para ler o HTML, não é necessário Python nem servidor. Depois de alterar fontes ou executáveis, não use resultados antigos como prova da nova versão. Consulte as [correções dos compiladores](verification/compiler_fixes.md) e os [avisos de terceiros](THIRD_PARTY_NOTICES.md).

## Escopo dos fontes publicados

KOKURA-GUI, KUROSAKI-GUI e PLITA ficam fora deste envio. Os fontes e manuais publicados abrangem a linha de comando, os núcleos e as APIs de integração.
