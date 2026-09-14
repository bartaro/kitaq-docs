## 1. Découvrir KITAQGB
KITAQGB est un compilateur de la famille C pour GB/CGB, développé à partir du NORCAL de Zachtronics.

{{ORIGIN}}

Il lit les fichiers C, génère les instructions du processeur et les rassemble dans une ROM. Son langage, ses bibliothèques et ses conventions d'appel diffèrent de ceux d'un compilateur C pour ordinateur de bureau.

La GB possède un processeur 8 bits et peu de mémoire. La plupart des graphismes utilisent des tuiles de 8 × 8 pixels. Les sprites sont de petites images que l'on positionne indépendamment. Le texte nécessite lui aussi des tuiles graphiques : il ne faut pas compter sur un affichage de texte universel intégré. Ces exemples utilisent les glyphes du fichier `ascii.c` de l'auteur, réordonnés selon les codes ASCII pour la GB sans modifier leurs pixels. L'édition FC convertit les mêmes dessins au format CHR de la NES.

## 2. Prérequis et compilation du compilateur
Installez un environnement Visual Studio/MSBuild ciblant .NET Framework 4.8. Utilisez une invite Developer PowerShell dans laquelle `MSBuild.exe` est disponible.

{{CODE:0}}

Gardez l’exécutable et ses fichiers de configuration ensemble. Indiquez le chemin du compilateur dans les commandes pour identifier précisément le fichier utilisé. La compilation du projet copie l’exécutable à la racine du dépôt `kitaqgb`.

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

## 6. Branchements et boucles
{{CODE:4}}

`break` quitte une boucle ou un `switch`, `continue` passe à l'itération suivante et `return` quitte une fonction. Employez l'instruction explicite `fallthrough;` pour poursuivre volontairement l'exécution d'un cas de `switch` dans le suivant ; une continuation implicite fait l'objet d'un diagnostic. Consultez l'exemple complet `gb_control.c`.

## 7. Fonctions, tableaux et structures
{{CODE:5}}

Les indices des tableaux commencent à zéro : un tableau de quatre éléments utilise les indices 0 à 3. `player.x` sélectionne un membre ; `pointer->x` y accède par un pointeur. Le compilateur analyse les structures, les unions et les énumérations, mais leur disposition dépend des types et des attributs `__packed` / `__aligned`. Vérifiez `sizeof` avant de partager des données avec le matériel ou un format binaire.

L'ABI Legacy utilisée par défaut place les arguments et les variables locales à des adresses fixes. Ne supposez pas que la récursivité ou la réentrance depuis une interruption fonctionne comme sur un ordinateur de bureau. `__stackcall` et `--abi=stack` proposent d'autres conventions d'appel, destinées à un usage avancé. Si vous combinez plusieurs conventions, examinez les rapports ABI et vérifiez l'exécution.

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
