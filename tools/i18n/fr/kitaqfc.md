## 1. KITAQFC et le compilateur GB
KITAQFC reprend la partie frontale de KITAQGB pour générer du code destiné au processeur de la famille 6502 de la NES/Famicom. Il ne convertit pas une ROM GB en ROM NES. Écrivez le logiciel pour l'affichage, le son, la mémoire et le mapper de la machine cible.

Les vérifications consignées ont exécuté des exemples utilisant des copies de structures et des appels de fonctions ordinaires. En revanche, **do-while et switch ont provoqué des erreurs de génération de code non prise en charge sur NES**. La présence d'une construction dans l'analyseur syntaxique ne suffit pas à démontrer qu'elle est utilisable sur cette cible.

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

## 5. Réécrire les constructions non prises en charge
{{CODE:4}}

Pour remplacer do-while, exécutez le corps de la boucle une première fois avant d'en tester la condition de sortie. Un aiguillage simple par switch peut devenir une suite de if/else. Ces fragments servent d'explication : fournissez vos propres fonctions `update` et de gestion d'état. L'exemple `fc_control.c` constitue un programme ROM complet.

Ne supposez pas que la récursivité, les appels indirects de fonctions ou les fonctions à nombre variable d'arguments sont pris en charge comme sur un ordinateur de bureau. Certaines API de scène ou d'entité conservent actuellement des pointeurs de fonction sans les appeler indirectement.

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

## 9. FDS, extensions sonores et périphériques
Le FDS implique le placement des fichiers sur disque, le démarrage, les overlays et les sauvegardes. Consultez `fds_manifest_sample.json` et les en-têtes FDS. Préparez le BIOS éventuellement nécessaire dans votre propre environnement d'exécution ; la distribution publique ne contient aucun BIOS.

Appeler une opération sonore VRC6 ou VRC7 ne change pas le mapper choisi pour la ROM. Faites correspondre le mapper à l'extension sonore employée. Pour les périphériques, testez séparément la lecture des entrées, l'état de connexion et les effets sur les manettes ordinaires.

## 10. Diagnostics et résultats de compilation
Les diagnostics KQ et les commandes de développement comme `symfind`, `src2asm` et `romdiff` ressemblent à leurs équivalents GB. Certaines options d'aide héritées de la GB ne correspondent pas nécessairement à des fonctions NES implémentées. Le dictionnaire FC est extrait séparément des sources et en-têtes FC.

Des avertissements comme KQ2421, relatif aux accès directs au PPU, peuvent apparaître même pendant une initialisation avec affichage désactivé. Ne modifiez pas une initialisation sûre uniquement pour supprimer un avertissement : examinez le moment du rendu et les journaux d'exécution. Zéro erreur et zéro avertissement sont deux résultats différents.

## Emplacement des sources après la réorganisation
Les sources du compilateur se trouvent désormais dans le sous-dossier portant le même nom que leur dépôt. Les anciennes indications de chemin de la référence API conservent les chemins du 12 septembre. Consultez [la réorganisation des dossiers](../GITHUB_SETUP.md) pour établir la correspondance. Les chemins de l'exécutable à la racine et de la bibliothèque restent les mêmes.
