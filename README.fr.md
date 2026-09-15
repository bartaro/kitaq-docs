# Manuels de la série KITAQ

[English](README.md#english) | [日本語](README.md#japanese) | **Français**

<!-- ai-prompts:start -->
## Prompts de développement de jeux avec l’IA

Renseignez les besoins, puis transmettez le prompt complet à votre assistant IA. Il couvre l’implémentation, les tests dans l’émulateur, l’analyse avec SARAKURA et la vérification des corrections.

KITAQGB · KITAQFC
<!-- ai-prompts:end -->

## Manuels HTML

Les sept volumes sont disponibles en neuf langues et décrivent les sources du 14 septembre 2026. Toutes les éditions comprennent les mêmes 1 053 entrées d’API et 47 programmes d’exemple complets. Ouvrez `fr/index.html` pour le français, `en/index.html` pour l’anglais ou `index.html` pour le japonais. Chaque volume permet de changer de langue. Les comptes rendus de vérification précisent les sources, les exécutables et les conditions des tests.

Les extraits source et les sorties enregistrées des outils sont conservés sans modification. Consultez [la configuration GitHub](GITHUB_SETUP.md) et les [vérifications de publication](PUBLICATION_CHECKS.md). Les pages HTML permettent la lecture hors connexion, la recherche dans un volume, la copie du code et l'impression.

| Volume en français | Contenu |
| --- | --- |

Le sommaire et le début du volume 1 expliquent les deux sens du nom et mentionnent NORCAL. Les lettres, chiffres et symboles utilisent le fichier fourni `samples/assets/ascii.c`. Les ressources GB sont réordonnées selon les codes ASCII ; les ressources FC sont converties dans les plans de bits NES. Les dessins des glyphes restent inchangés.

Les textes, exemples ajoutés et outils de génération sont sous licence MIT. Le 12 septembre 2026, l'auteur a confirmé que les 92 glyphes fournis sont sa création originale et peuvent être publiés sous MIT. Les extraits des logiciels d'origine conservent leurs mentions de droit d'auteur. Redistribuez ensemble les [mentions de tiers](THIRD_PARTY_NOTICES.md) et les licences applicables.

Les manuels comprennent la [licence anglaise](LICENSE) et une [traduction japonaise à titre de référence](LICENSE.ja). Les [mentions de tiers](THIRD_PARTY_NOTICES.md) renvoient aux licences japonaises des outils. L'original anglais prévaut en cas de divergence entre les traductions. Les distributions binaires des logiciels nécessitent également les licences propres à leurs dépendances. L'autorisation de publier ces manuels ne signifie pas que tous les outils et dépendances peuvent être redistribués sous MIT uniquement.

## Compiler les exemples

Clonez les dépôts dans des dossiers voisins sous un même dossier parent, puis lancez les commandes suivantes depuis ce parent. [GITHUB_SETUP.md](GITHUB_SETUP.md) décrit l'organisation. Utilisez les compilateurs fournis ou reconstruisez-les selon le manuel ; cette édition comprend des corrections de compilateur.

```powershell
.\kitaq-docs\samples\build.ps1 -Only gb_hello,fc_hello
.\kitaq-docs\samples\build.ps1
```

Pour un autre emplacement des sources, indiquez `-Root "chemin absolu des sources"`. Choisissez des exécutables situés ailleurs avec `-GbCompiler` et `-FcCompiler`. Les ROM et journaux sont placés par défaut dans `samples/out/<sample-id>`. Ce paquet de manuels ne contient ni exécutables de compilateur, ni ROM commerciales, ni BIOS.

`samples/api-fragments` contient des fragments qui nécessitent une initialisation et des arguments valides dans le programme qui les entoure. La compilation par lot des ROM couvre les 47 programmes de `samples/manifest.json`. Chaque volume distingue les API déclarées sans implémentation, les fragments non exécutés et les fonctions non vérifiées sur matériel physique.

## Publier sur GitHub

1. Placez le contenu de ce dossier à la racine du dépôt ou dans un dossier `docs`.
2. Téléversez ensemble `index.html`, les sept volumes, `verification.html`, `loop-engineering.html`, `prompts`, les dossiers de langues, `assets`, `samples`, `reference`, `verification`, le README et les mentions de licence. Incluez `.nojekyll`.
3. Dans GitHub, ouvrez Settings → Pages → Build and deployment et choisissez Deploy from a branch comme source.
4. Sélectionnez la branche publiée et `/ (root)` ou `/docs`, puis enregistrez.
5. Une fois la publication terminée, ouvrez l'adresse indiquée dans Pages et vérifiez les liens du sommaire et des volumes.

Consultez les [instructions GitHub sur la source de publication](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site). `manual/_manual_work` est un espace local de compilation et de vérification, exclu de la publication.

## Modifier et actualiser

Le texte japonais se trouve dans `tools/chapters.py`, le texte anglais dans `tools/en/*.md`, la génération anglaise dans `tools/generate_en.py`, les dictionnaires API et la génération des pages dans `tools/generate.py`, et les styles dans `assets/manual.css`. Les traductions rédigées se trouvent dans `tools/i18n/<langue>/` ; le français utilise `fr`. Python sert à actualiser les manuels.

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

Pour régénérer le français à partir de ses textes après la génération anglaise, utilisez `python kitaq-docs/tools/generate_i18n.py --language fr`. Les traductions sont rédigées dans les fichiers ; aucun service de traduction n'est appelé. Cette génération utilise Beautiful Soup.

Les captures accompagnent les explications des exemples. Les fichiers publics ne contiennent ni journaux de compilation ou d’exécution, ni relevés de vérification locaux. Avant la mise en ligne, utilisez `tools/export_public.py` pour exporter le manuel vers une copie de travail Git distincte. Consultez les [mentions de tiers](THIRD_PARTY_NOTICES.md).

## Périmètre de cette publication

KOKURA-GUI, KUROSAKI-GUI et PLITA sont exclus de cet envoi. Les sources et manuels publiés couvrent les outils en ligne de commande, les cœurs et les API d'intégration.
