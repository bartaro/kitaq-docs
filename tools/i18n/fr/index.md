## Bienvenue
KITAQGB est issu d'un **fork de NORCAL**, le compilateur C pour NES associé à Zachtronics. Le projet prolonge cette base pour proposer un compilateur de la famille C destiné à la Game Boy et à la Game Boy Color : génération de code, mémoire, affichage, son et commutation des banques de ROM sont adaptés à ces machines. Nous rendons crédit au projet d'origine et à son auteur, Keith Holman.

{{ORIGIN}}

NORCAL a été développé dans le cadre de la version NES de HACK*MATCH. Consultez les présentations de l'auteur : [NORCAL: A C Compiler for the NES](https://keithholman.net/nes-compiler.html) et [HACK*MATCH pour NES](https://trashworldnews.com/hack-match/). L'historique du projet et l'explication de son nom reprennent le README fourni par l'auteur.

## Comment utiliser ces manuels
À la manière des manuels des premiers micro-ordinateurs, cette collection commence par de petits programmes que vous pouvez saisir, compiler et exécuter. Observez d'abord le résultat, puis découvrez le fonctionnement de la machine. Il n'est pas nécessaire d'apprendre tout le vocabulaire avant de commencer.

1. Commencez par le premier programme du volume 1 pour la GB, ou du volume 4 pour la FC.
2. Appuyez-vous sur le volume 2 ou le volume 5 pour ajouter les commandes, les graphismes et le son.
3. Observez l'exécution avec KOKURA ou KUROSAKI, puis regroupez les diagnostics avec SARAKURA.
4. Si vous connaissez déjà le nom d'une fonction, utilisez la recherche du volume ou le dictionnaire de l'API.

La syntaxe du langage, les fonctions intrinsèques du compilateur, les fonctions de bibliothèque et les commandes du terminal font l'objet de rubriques distinctes. Les volumes consacrés aux compilateurs comportent aussi un index des instructions du processeur. Des noms proches sur GB et FC ne garantissent ni les mêmes arguments ni le même comportement.

## Les sept volumes
| Volume | Entrée | Sortie ou usage |
| --- | --- | --- |
| KITAQGB | Code C et ressources | ROM GB/CGB, fichiers de placement et informations de compilation |
| Bibliothèque KITAQGB | Appels depuis le code du jeu | Graphismes, son, commandes, communication et services de jeu |
| KOKURA | ROM GB/CGB | Exécution, images, audio, états et observations |
| KITAQFC | Code C et ressources CHR | Images NES/FDS et informations de compilation |
| Bibliothèque KITAQFC | Appels depuis le code du jeu | Graphismes, son et périphériques NES |
| KUROSAKI | Images NES/FDS | Exécution, enregistrement et analyse |
| SARAKURA | Informations de compilation et événements de diagnostic | Rapports, plans de correction et plans de nouveaux tests |

## La police fournie
Les 26 majuscules, 10 chiffres, 26 minuscules et 30 symboles proviennent du fichier [ascii.c](samples/assets/ascii.c) de l'auteur. Aucun dessin de caractère n'a été ajouté. Les 92 glyphes d'origine sont conservés ; consultez la [table de conversion](verification/font_conversion.json) et la [planche des tuiles](verification/font_source_atlas.png). L'espace utilise une tuile vide. La barre oblique inverse et la barre verticale ne figurent pas dans la police fournie et s'affichent comme des espaces. Les exemples `gb_font.c` et `fc_font.c` montrent tous les glyphes disponibles.

## Édition et vérifications
Ce manuel décrit les **sources du 14 septembre 2026**. L’inventaire de référence consigne les empreintes des sources et des exécutables. Les comptes rendus de vérification précisent les données d’entrée, les conditions et la portée de chaque test.

Une compilation réussie indique qu'une ROM a été produite. Un test d'exécution indique qu'un émulateur a avancé du nombre d'images prévu. Les comparaisons de pixels, les réactions aux commandes et les tests audio sont consignés séparément. Ces résultats ne garantissent pas la compatibilité avec tous les périphériques ou toutes les consoles physiques ; les avertissements restent visibles dans les journaux.

La distribution publique actuelle ne comprend ni les interfaces graphiques de KOKURA, ni celle de KUROSAKI, ni PLITA. Utilisez les cœurs d'émulation, les outils en ligne de commande et les API d'intégration publiés.

## Préparer un dossier de travail
Les exemples utilisent **Windows PowerShell**. Enregistrez les fichiers C en texte UTF-8. Le dossier courant est celui depuis lequel vous lancez une commande. Entourez de guillemets les chemins contenant des espaces et utilisez au besoin `& "chemin"` pour appeler un exécutable. Clonez les dépôts dans des dossiers voisins, conformément aux [instructions de configuration GitHub](../GITHUB_SETUP.md), et lancez les commandes faisant intervenir plusieurs projets depuis leur dossier parent.

{{CODE:0}}

Remplacez `game.c`, `game.gb` et `game.nes` par vos noms de fichiers. Les indications telles que `<ROM>` sont des paramètres à remplacer : ne saisissez pas les chevrons. Les commandes sont généralement présentées sur une seule ligne. La continuation de ligne par barre oblique inverse de Bash ne s'applique pas à PowerShell.

## Corrections de compilateur utilisées pour cette édition
La compilation des exemples a révélé une collision d'étiquettes locales internes dans KITAQGB et des problèmes de conservation des valeurs intermédiaires et des valeurs de retour entre appels dans KITAQFC. Les vérifications consignées dans ce manuel ont utilisé les compilateurs corrigés, notamment pour l'exemple de réserve d'objets GB et les exemples FC de fonctions et de structures. Ces corrections ne démontrent pas la prise en charge de toutes les constructions du C. Consultez le [compte rendu de vérification](verification.html) de chaque exemple.

## Lire, imprimer et publier le HTML
Ouvrez `index.html` dans le dossier téléchargé pour lire les manuels hors connexion. Les styles, la recherche, les exemples et les images de vérification utilisent des fichiers locaux ; aucun CDN externe n'est nécessaire. Conservez l'ensemble du dossier plutôt que de copier des fichiers HTML isolés. Le bouton d'impression prépare une mise en page sans colonne de navigation.

Le dépôt `kitaq-docs` contient le site des manuels. Dans l'explorateur du dépôt, GitHub affiche normalement le code source HTML ; GitHub Pages sert les pages mises en forme. Le README du dépôt explique la publication et le clonage. Cette traduction comporte les mêmes sept volumes, entrées d'API, exemples et références de vérification que l'édition japonaise. Les extraits de code et les sorties enregistrées des outils gardent leur texte d'origine lorsqu'une traduction empêcherait d'identifier exactement le source ou la réponse de la commande.
