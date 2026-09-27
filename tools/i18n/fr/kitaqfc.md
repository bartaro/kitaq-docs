## 1. KITAQFC et le compilateur GB
KITAQFC reprend la partie frontale de KITAQGB pour générer du code destiné au processeur de la famille 6502 de la NES/Famicom. Il ne convertit pas une ROM GB en ROM NES. Écrivez le logiciel pour l'affichage, le son, la mémoire et le mapper de la machine cible.

KITAQFC prend en charge les copies de structures, les appels de fonctions ordinaires et les boucles for, while et do-while. Une boucle do-while exécute son corps au moins une fois avant de tester la condition. continue passe à ce test final ; break quitte la boucle. Un switch sélectionne une constante case comprise entre 0 et 255, ou le corps default si aucun case ne correspond. Son expression de sélection n’est évaluée qu’une fois. break quitte la boucle ou le switch le plus interne ; un continue à l’intérieur d’un switch passe à l’itération suivante de la boucle englobante.

## 2. Prérequis et compilation
{{CODE:0}}

Installez le Developer Pack .NET Framework 4.8 et Visual Studio Build Tools, puis utilisez Developer PowerShell. Les commandes suivantes emploient l'exécutable copié dans le dépôt `kitaqfc`. Si vous le compilez ailleurs, adaptez le chemin. Les graphismes CHR et le source C sont deux entrées distinctes. Le fichier `font.chr` du manuel est une conversion sur 8 Kio du fichier `ascii.c` de l'auteur.

## 3. Votre premier programme
{{CODE:1}}

{{CODE:2}}

L'exemple affiche HELLO WORLD et 042. Sa fonction `m_wait` valide la file VRAM, attend la NMI et restaure le défilement. Les transferts passant par PPUADDR modifient l'état interne du défilement ; sans restauration, le texte peut être décalé vers un bord. Retenez cette séquence : désactiver l'affichage, préparer les ressources, réactiver l'affichage, puis se synchroniser avec la NMI.

## 4. Introduction au langage
Les instructions et expressions du volume GB constituent une base commune. FC accepte `unsigned char` et `unsigned short` ; `core.h` définit `u8`, `u16`, `s8` et `s16`. `fc.h` est l'en-tête de regroupement. Ici, les fonctions sans argument peuvent s'écrire sous la forme `void main(void)`.

{{CODE:3}}

Respectez les plages des entiers sur 8 ou 16 bits. Les indices des tableaux commencent à zéro. `fc_aggregate.c` présente les fonctions, pointeurs et structures ; `fc_arithmetic.c`, les calculs ; `fc_control.c`, les boucles. N'incluez pas de registres CGB ni de fonctions intrinsèques réservées à la GB dans un programme FC.

<!-- common-language-kitaqfc:start -->
### Résultats des expressions et évaluation

Les opérateurs de comparaison `==`, `!=`, `<`, `<=`, `>`, `>=` et les opérateurs logiques `!`, `&&`, `||` renvoient 0 pour faux et 1 pour vrai. Vous pouvez stocker le résultat dans un `u16`, le passer en argument, le renvoyer ou l’utiliser dans un calcul. Par exemple, `score = 500 + (lives != 0);` donne 501 s’il reste une vie, et 500 sinon.

`&&` n’évalue pas son opérande droit lorsque celui de gauche vaut zéro. `||` n’évalue pas son opérande droit lorsque celui de gauche est non nul. Dans `pointer != 0 && pointer->active != 0`, un pointeur nul empêche l’accès au membre. Les deux octets d’une valeur de 16 bits participent au test logique : 256 est donc vrai. Les opérateurs bit à bit `&` et `|` ne court-circuitent pas l’évaluation.

`++value` renvoie la valeur mise à jour ; `value++` renvoie la valeur initiale. Ces opérateurs acceptent aussi les éléments de tableau, les pointeurs déréférencés et les membres de structure. `buffer[index()]++` appelle `index()` une seule fois. Avec `u16 *p`, `p++` avance de deux octets vers l’élément suivant, tandis que `(*p)++` incrémente la valeur pointée.

`sizeof(array)` donne la taille en octets de tout le tableau ; `sizeof(pointer)` vaut 2. Pour `u16 values[9];`, `sizeof(values)` vaut 18. Cela s’applique aux tableaux en ROM, aux tableaux locaux et aux membres de type tableau. `sizeof(function())` examine le type de retour sans appeler la fonction.

La déclaration et la définition d’une fonction doivent avoir les mêmes types de paramètres, dans le même ordre. Les noms peuvent différer ; le corps utilise ceux de la définition. Par exemple, `u8 next(u8 input);` peut être défini par `u8 next(u8 value) { return (u8)(value + 1); }`. Les paramètres et variables locales masquent les variables globales de même nom.

La sélection de tableaux ou de chaînes avec `?:` produit un pointeur vers le type d’élément sélectionné. Vous pouvez le passer directement, par exemple dans `show(ready ? "READY" : "WAIT");`. Pour des tableaux `u16` nommés `a` et `b`, `(ready ? a : b) + 1` avance de deux octets vers le deuxième élément du tableau choisi. Le tableau n’est pas copié.

`condition ? yes : no` évalue la condition, puis uniquement la branche choisie. La condition et les branches peuvent contenir des décalages dont le nombre de bits est variable. Par exemple, `on = (pattern & (0x80 >> bit)) != 0 ? 4 : 2;` choisit quatre ou deux selon le bit désigné. Les appels de fonction présents dans un opérande droit ignoré par `&&` ou `||` sont eux aussi ignorés. Un `continue` dans une boucle `for` exécute une fois l’expression de mise à jour avant de réévaluer la condition ; dans `while` et `do ... while`, il passe à la condition.

<!-- common-language-kitaqfc:end -->

## 5. Boucles et répartition par état
{{CODE:4}}

Ces fragments montrent une boucle qui effectue au moins une mise à jour et une branche qui choisit le traitement de l’état courant. Définissez update, condition, state et les traitements des états dans votre programme. Consultez fc_control.c pour un exemple complet de boucle, et l’exemple de gestion des images et des scènes de la bibliothèque pour une ROM complète de gestion des scènes.

Enregistrez les rappels de scène, d’entité et de système avec les types d’arguments et de retour exigés par leurs déclarations. Les bibliothèques appellent les traitements enregistrés depuis les opérations correspondantes de mise à jour, de dessin ou d’attente d’image. Respectez les contraintes de banque ROM et de mappage de chaque API. Ne supposez pas que la récursion ou les fonctions variadiques sont prises en charge comme sur un ordinateur de bureau.

## 6. Mémoire et PPU
La RAM interne du processeur NES occupe 0x0000–0x07FF. Ses miroirs au-delà de 0x0800 ne constituent pas de la RAM supplémentaire. La pile du 6502 occupe la page 1 ; les copies de travail de l'OAM et les files réservent d'autres régions. Les réglages avancés `--nes-local-ram=START:LENGTH` et `--nes-temp-ram=START:LENGTH` nécessitent d'examiner le fichier de placement.

Les adresses PPU appartiennent à un espace distinct. Le CHR fournit les motifs, les tables de noms placent les tuiles, les tables d'attributs choisissent les groupes de palettes et les palettes contiennent les codes de couleur. Les attributs d'arrière-plan s'appliquent normalement à des régions de 16 × 16 pixels ; ils ne fonctionnent donc pas comme les attributs de tuiles GB.

## 7. NMI et file VRAM
La NMI est l'interruption associée à la limite entre deux images affichées. Des écritures directes importantes dans le PPU pendant le rendu peuvent corrompre l'écran. Effectuez l'initialisation directe lorsque le rendu est désactivé ; pour les mises à jour ordinaires, utilisez `__vramq_put`, `__vramq_copy`, `__vramq_fill`, puis validez la file.

{{CODE:5}}

Vérifiez la capacité de la file et la durée de validité des sources. La NMI par défaut traite la file. Un gestionnaire `__nes_nmi` personnalisé doit conserver l'exécution nécessaire de la file, le travail sur l'OAM et la préservation des registres.

## 8. Mappers et disposition de la ROM
| Choix | Premier usage typique |
| --- | --- |
| nrom | Petits exercices avec ROM fixe |
| uxrom / cnrom / axrom | Commutation simple de PRG ou de CHR |
| mmc1 / mmc3 / mmc5 | Programmes plus grands et fonctions propres au mapper |
| vrc6 / vrc7 / fme7 | Banques et extensions correspondantes |
| fds | Production d'images de disque |

Il s'agit des choix du compilateur, pas d'un tableau de compatibilité matérielle ou d'exhaustivité de l'émulateur. `--board=surom512` sélectionne une organisation particulière de carte MMC1 ; compléter simplement un fichier jusqu'à 512 Kio ne crée pas cette organisation. Utilisez également l'audit de carte de KUROSAKI.

{{CODE:6}}

Vérifiez les exigences de la carte pour `--battery` / `--no-battery`, la capacité CHR, le placement PRG et les appels entre banques. Après un changement de mapper ou de mode miroir, testez le démarrage, le défilement et la commutation des données, en plus de la génération de la ROM.

Les lectures ordinaires par indice et les références par pointeur C à des tableaux en ROM placent ces tableaux dans la banque commune 0, sauf si `#pragma fixed_bank` fixe explicitement leur emplacement. Les données restent ainsi visibles lorsque l’appelant s’exécute dans une banque commutable. Pour un accès distant explicite, passez dans le même appel le nom du tableau seul et `__bankof` appliqué à ce même nom, par exemple `__farpeek8(__bankof(table), table)`. Une simple demande de numéro de banque ne demande pas de placement en banque commune. Pour les données explicitement fixées à une banque et les références en assembleur, vous devez maintenir le mappage correct. Cette règle vérifie le placement à partir de la syntaxe ; elle n’analyse pas le cheminement des pointeurs. La capacité de la banque commune reste limitée.

## 9. FDS, extensions sonores et périphériques
Le FDS implique le placement des fichiers sur disque, le démarrage, les overlays et les sauvegardes. Consultez `fds_manifest_sample.json` et les en-têtes FDS. Préparez le BIOS éventuellement nécessaire dans votre propre environnement d'exécution ; la distribution publique ne contient aucun BIOS.

Appeler une opération sonore VRC6 ou VRC7 ne change pas le mapper choisi pour la ROM. Faites correspondre le mapper à l'extension sonore employée. Pour les périphériques, testez séparément la lecture des entrées, l'état de connexion et les effets sur les manettes ordinaires.

## 10. Diagnostics et résultats de compilation
Les diagnostics KQ et les commandes de développement comme `symfind`, `src2asm` et `romdiff` ressemblent à leurs équivalents GB. Certaines options d'aide héritées de la GB ne correspondent pas nécessairement à des fonctions NES implémentées. Le dictionnaire FC est extrait séparément des sources et en-têtes FC.

Des avertissements comme KQ2421, relatif aux accès directs au PPU, peuvent apparaître même pendant une initialisation avec affichage désactivé. Ne modifiez pas une initialisation sûre uniquement pour supprimer un avertissement : examinez le moment du rendu et les journaux d'exécution. Zéro erreur et zéro avertissement sont deux résultats différents.

## Emplacement des sources
Les sources du compilateur et le fichier projet se trouvent dans le sous-dossier portant le nom du dépôt. L’exécutable est à la racine et les bibliothèques dans `lib/`. Consultez la [structure des dossiers](../GITHUB_SETUP.md) pour les chemins et les prérequis de compilation.
