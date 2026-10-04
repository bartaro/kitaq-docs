## 1. Découvrir KITAQGB
KITAQGB est un compilateur de la famille C pour GB/CGB, développé à partir du NORCAL de Zachtronics.

{{ORIGIN}}

Il lit les fichiers C, génère les instructions du processeur et les rassemble dans une ROM. Son langage, ses bibliothèques et ses conventions d'appel diffèrent de ceux d'un compilateur C pour ordinateur de bureau.

La GB possède un processeur 8 bits et peu de mémoire. La plupart des graphismes utilisent des tuiles de 8 × 8 pixels. Les sprites sont de petites images que l'on positionne indépendamment. Le texte nécessite lui aussi des tuiles graphiques : il ne faut pas compter sur un affichage de texte universel intégré. Ces exemples utilisent les glyphes du fichier `ascii.c` de l'auteur, réordonnés selon les codes ASCII pour la GB sans modifier leurs pixels. L'édition FC convertit les mêmes dessins au format CHR de la NES.

## 2. Prérequis et compilation du compilateur
Rust 1.85 ou ultérieur permet de construire le compilateur et tous les outils auxiliaires pour Windows, Linux, macOS ARM et macOS Intel. Les exécutables natifs ne nécessitent pas .NET ; les outils de ressources fonctionnent aussi sans Python ni Pillow.

{{CODE:0}}

Les exécutables Windows se trouvent à la racine du dépôt. Ceux de Linux et macOS sont dans les dossiers bin/ indiqués ci-dessous. Conservez lib/ et les mentions de licence avec les outils. Sous Linux/macOS, attribuez les droits d'exécution avec chmod +x, puis ajoutez le dossier au PATH ou utilisez le chemin complet.

Les scripts PowerShell utilisent l'exécutable Windows à la racine. Sous Linux/macOS, transmettez les mêmes sources C et options au compilateur natif, ou utilisez PowerShell 7. Les graphismes CHR et le source C sont des entrées distinctes ; font.chr conserve la police des exemples.

## 3. Votre premier programme
Le fichier fourni `samples/gb_hello.c` utilise les fonctions d'affichage et de texte de `gb_common.h`. Conservez cet en-tête avec les fichiers de police. La directive `#include` lit les déclarations ou les définitions contenues dans un autre fichier.

{{CODE:1}}

{{CODE:2}}

L'exemple doit afficher HELLO WORLD et 042. Les noms commençant par `m_` sont des fonctions pédagogiques définies dans l'en-tête commun des exemples, pas des commandes standard de KITAQGB. Les fonctions intrinsèques du compilateur comprennent notamment `__wait_vblank` et `__vram_copy`.

## 4. Syntaxe de base et types
Terminez les instructions par `;` et regroupez-les entre `{ }`. `//` ouvre un commentaire de ligne ; `/* ... */` délimite un commentaire de bloc. Les noms distinguent les majuscules des minuscules. Utilisez `void main()` comme point d'entrée. **Dans cette version GB, `void main(void)` provoque une erreur de syntaxe** : ne recopiez donc pas telle quelle la déclaration utilisée sur FC.

| Type | Signification et plage |
| --- | --- |
| `u8` | Entier non signé sur 8 bits, de 0 à 255 |
| `s8` | Entier signé sur 8 bits, de -128 à 127 |
| `u16` | Entier non signé sur 16 bits, de 0 à 65535 |
| `s16` | Entier signé sur 16 bits, de -32768 à 32767 |
| `void` | Aucune valeur de retour |
| `T*` | Pointeur vers des données de type T |

Commencez par ces noms de types courts. Ne supposez pas que `int`, `long`, `float`, `double` ou les en-têtes standard se comportent comme sur un ordinateur de bureau. Cette version traite `char` comme une donnée non signée sur 8 bits ; utilisez explicitement `s8` ou `s16` pour les calculs signés.

{{CODE:3}}

`(u16)` est une conversion de type explicite. Affecter à une grande variable une petite valeur qui a déjà débordé ne récupère pas les bits perdus : élargissez les opérandes avant le calcul. Pour les déplacements fractionnaires, utilisez la bibliothèque de calcul en virgule fixe.

## 5. Expressions et opérateurs
| Groupe | Opérateurs | Exemple ou signification |
| --- | --- | --- |
| Arithmétique | `+ - * / %` | `n / 10` donne le quotient entier ; `n % 10`, le reste |
| Comparaison | `== != < <= > >=` | `lives == 0` teste l'égalité |
| Logique | `! &&` / `||` | Négation, deux conditions vraies, au moins une condition vraie |
| Bits | `&` / `|` / `^ ~ << >>` | Masques de boutons et autres ensembles de bits |
| Affectation | `= += -=` et formes apparentées | `x += 1` modifie une valeur |
| Incrémentation | `++ --` | `i++` ajoute un |
| Sélection | `condition ? A : B` | Choisit une valeur selon une condition |
| Pointeurs | `&variable` / `*p` | Obtient une adresse ou accède à la donnée pointée |

Distinguez `=` de `==`. Utilisez des parenthèses pour rendre les expressions complexes lisibles et évitez d'accumuler appels et effets de bord dans une seule instruction. Évitez les divisions par zéro et les accès hors des limites des tableaux. `sizeof` donne une taille en octets ; `offsetof`, le décalage d'un membre dans une structure.

<!-- common-language-kitaqgb:start -->
### Résultats des expressions et évaluation

Les opérateurs de comparaison `==`, `!=`, `<`, `<=`, `>`, `>=` et les opérateurs logiques `!`, `&&`, `||` renvoient 0 pour faux et 1 pour vrai. Vous pouvez stocker le résultat dans un `u16`, le passer en argument, le renvoyer ou l’utiliser dans un calcul. Par exemple, `score = 500 + (lives != 0);` donne 501 s’il reste une vie, et 500 sinon.

`&&` n’évalue pas son opérande droit lorsque celui de gauche vaut zéro. `||` n’évalue pas son opérande droit lorsque celui de gauche est non nul. Dans `pointer != 0 && pointer->active != 0`, un pointeur nul empêche l’accès au membre. Les deux octets d’une valeur de 16 bits participent au test logique : 256 est donc vrai. Les opérateurs bit à bit `&` et `|` ne court-circuitent pas l’évaluation.

`++value` renvoie la valeur mise à jour ; `value++` renvoie la valeur initiale. Ces opérateurs acceptent aussi les éléments de tableau, les pointeurs déréférencés et les membres de structure. `buffer[index()]++` appelle `index()` une seule fois. Avec `u16 *p`, `p++` avance de deux octets vers l’élément suivant, tandis que `(*p)++` incrémente la valeur pointée.

`sizeof(array)` donne la taille en octets de tout le tableau ; `sizeof(pointer)` vaut 2. Pour `u16 values[9];`, `sizeof(values)` vaut 18. Cela s’applique aux tableaux en ROM, aux tableaux locaux et aux membres de type tableau. `sizeof(function())` examine le type de retour sans appeler la fonction.

La déclaration et la définition d’une fonction doivent avoir les mêmes types de paramètres, dans le même ordre. Les noms peuvent différer ; le corps utilise ceux de la définition. Par exemple, `u8 next(u8 input);` peut être défini par `u8 next(u8 value) { return (u8)(value + 1); }`. Les paramètres et variables locales masquent les variables globales de même nom.

La sélection de tableaux ou de chaînes avec `?:` produit un pointeur vers le type d’élément sélectionné. Vous pouvez le passer directement, par exemple dans `show(ready ? "READY" : "WAIT");`. Pour des tableaux `u16` nommés `a` et `b`, `(ready ? a : b) + 1` avance de deux octets vers le deuxième élément du tableau choisi. Le tableau n’est pas copié.

`condition ? yes : no` évalue la condition, puis uniquement la branche choisie. La condition et les branches peuvent contenir des décalages dont le nombre de bits est variable. Par exemple, `on = (pattern & (0x80 >> bit)) != 0 ? 4 : 2;` choisit quatre ou deux selon le bit désigné. Les appels de fonction présents dans un opérande droit ignoré par `&&` ou `||` sont eux aussi ignorés. Un `continue` dans une boucle `for` exécute une fois l’expression de mise à jour avant de réévaluer la condition ; dans `while` et `do ... while`, il passe à la condition.

<!-- common-language-kitaqgb:end -->

## 6. Branchements et boucles
{{CODE:4}}

`break` quitte une boucle ou un `switch`, `continue` passe à l'itération suivante et `return` quitte une fonction. Employez l'instruction explicite `fallthrough;` pour poursuivre volontairement l'exécution d'un cas de `switch` dans le suivant ; une continuation implicite fait l'objet d'un diagnostic. Consultez l'exemple complet `gb_control.c`.

## 7. Fonctions, tableaux et structures
{{CODE:5}}

Les indices des tableaux commencent à zéro : un tableau de quatre éléments utilise les indices 0 à 3. `player.x` sélectionne un membre ; `pointer->x` y accède par un pointeur. Le compilateur analyse les structures, les unions et les énumérations, mais leur disposition dépend des types et des attributs `__packed` / `__aligned`. Vérifiez `sizeof` avant de partager des données avec le matériel ou un format binaire.

L’ABI Legacy par défaut place les arguments et le stockage local à des adresses fixes. Ne supposez pas une récursion ou une réentrance depuis les interruptions comparable à celle d’un ordinateur de bureau. `__stackcall` et `--abi=stack` sont des choix avancés de convention d’appel. Si vous combinez plusieurs conventions, examinez les rapports ABI et vérifiez l’exécution. Les rappels par pointeur de fonction ne sont pas pris en charge avec `--abi=stack`. Compilez les exemples complets de rappels système et de scène avec l’ABI Legacy par défaut, comme indiqué dans leurs commandes de compilation.

## 8. Plusieurs fichiers et préprocesseur
Placez les types, constantes et déclarations dans les en-têtes, et le corps des fonctions dans les fichiers `.c`. Utilisez `#pragma once` ou des gardes d'inclusion pour éviter les inclusions répétées. La compilation conditionnelle prend en charge `#define`, `#undef`, `#if`, `#ifdef`, `#ifndef`, `#elif`, `#else` et `#endif`.

{{CODE:6}}

L'option `-I` ajoute un dossier de recherche d'en-têtes. Inclure l'en-tête d'une bibliothèque n'ajoute pas son implémentation : indiquez les fichiers `.c` nécessaires dans la commande de compilation. Choisissez les unités utiles ; ajouter sans distinction tous les sources peut dupliquer les définitions de registres ou les gestionnaires d'interruption.

## 9. ROM, mémoire et banques
La ROM contient le code et les constantes, la WRAM les variables, la VRAM les graphismes et l'OAM les descriptions des sprites. La commutation de banques change la mémoire physique visible à une adresse du processeur. Un pointeur sur 16 bits ne suffit pas à identifier des données situées dans une autre banque.

{{CODE:7}}

`__prg_rom` place les données en ROM. Des attributs tels que `__location(0xFF40)` imposent une adresse, tandis que `__wram` / `__hram` sélectionnent une région mémoire. Avec `#pragma bank` ou `#pragma fixed_bank`, examinez le fichier de placement et assurez-vous que le code et les données utilisés par les interruptions restent accessibles.

{{CODE:8}}

`--cgb=dmg` déclare un logiciel destiné à la DMG, `--cgb=cgb` un logiciel compatible avec les deux modes et `--cgb=cgb_only` un logiciel réservé à la CGB. Un jeu à deux modes doit détecter le matériel avant d'utiliser des fonctions propres à la CGB. Un indicateur dans l'en-tête ne crée pas à lui seul ce comportement dans le jeu.

## 10. Mettre à jour les graphismes au bon moment
VBlank est l'intervalle entre deux images affichées. Écrire dans la VRAM ou l'OAM sans tenir compte du moment peut altérer l'affichage ou faire perdre des mises à jour. Chargez les ressources initiales lorsque l'écran est désactivé ; pour les mises à jour régulières, utilisez les fonctions intrinsèques adaptées ou la file VRAM. Les fonctions marquées `_unsafe` ou `_fast` exigent que l'appelant garantisse une période de transfert sûre.

Alignez le tampon de DMA OAM sur une limite de 256 octets. Sur GB, `__oam_dma` reçoit l'adresse source. La fonction intrinsèque FC du même nom ne reçoit aucun argument : ne confondez pas ces API.

## 11. Commandes de compilation et fichiers produits
`-o` choisit la sortie, `-O0` / `-O1` le niveau d'optimisation et `--profile=dev|release|test` un ensemble de réglages. `--no-disasm` désactive la sortie du désassemblage. `--debug-out=...` et `--trace-out=...` fixent les emplacements des données d'investigation. Adaptez la quantité de sorties à une compilation rapide ou à une recherche détaillée.

{{CODE:9}}

Le fichier `.map` consigne les noms et leur placement ; `.funcsizes.txt`, la taille des fonctions ; `.dbg2.json` / `.source_map.txt` relient les positions d'exécution au source ; `.build_report.json` résume la compilation. Produire explicitement le JSON `--emit-ai-metadata` facilite le passage des données à SARAKURA.

## 12. Lire les erreurs en commençant par la première
Repérez le nom de fichier, la ligne et le numéro de diagnostic KQ de la première erreur. Les suivantes peuvent découler d'une seule faute de syntaxe. Pour un symbole non défini, vérifiez sa déclaration, son implémentation et sa présence dans la commande de compilation. En cas de débordement de ROM, examinez la taille des ressources et des fonctions, ainsi que leur répartition entre banques.

{{CODE:10}}

## 13. Assembleur intégré
`__asm { ... }` accepte les noms d'instructions de KITAQGB. Cela ne signifie pas qu'un source quelconque écrit pour un autre assembleur GB sera accepté. Les noms internes comprennent par exemple `LD_A_IMM`. Avant d'utiliser l'assembleur intégré, maîtrisez les arguments, les valeurs de retour, les registres préservés et le fonctionnement de la pile. L'annexe répertorie les noms d'instructions et les formes d'opérandes.

{{CODE:11}}

## Emplacement des sources
Les sources du compilateur et le fichier projet se trouvent dans le sous-dossier portant le nom du dépôt. L’exécutable est à la racine et les bibliothèques dans `lib/`. Consultez la [structure des dossiers](../GITHUB_SETUP.md) pour les chemins et les prérequis de compilation.
