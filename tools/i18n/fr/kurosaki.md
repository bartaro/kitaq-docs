## Outil Windows prêt à l'emploi
Le dépôt contient désormais `kurosaki.exe` à sa racine. Téléchargez l'archive ZIP du dépôt et conservez les mentions de licence avec l'exécutable. Cet outil Windows x64 en ligne de commande ne nécessite aucune installation de Rust, Python ou .NET pour fonctionner. Les étapes de compilation ci-dessous servent à le reconstruire depuis les sources. Le code propre au projet est proposé par DAISUKE OBA sous licence MIT ; les conditions des dépendances sont conservées dans BINARY_NOTICES.md et licenses/.

## 1. À quoi sert KUROSAKI ?
KUROSAKI est un émulateur d'observation NES/Famicom/FDS capable de lire les informations de KITAQFC. Son outil en ligne de commande inspecte les ROM, exécute les logiciels, enregistre l'audio, produit des diagnostics, sauvegarde des états, rejoue les commandes, désassemble les instructions et décompile des fonctions candidates. L'étendue des implémentations de mappers varie : commencez par examiner la ROM et les informations de prise en charge.

## 2. Compiler et démarrer
{{CODE:0}}

Les commandes courtes `kurosaki` ci-dessous supposent que le dossier de l'exécutable figure dans PATH. Sinon, remplacez le nom de commande par `& "chemin complet de l'exécutable"`.

{{CODE:1}}

Utilisez la ROM hello du volume 4 pour vérifier l'affichage du texte. `inspect-rom` examine un en-tête ; `run` fait avancer l'exécution du processeur et du PPU. Une inspection réussie ne garantit pas une exécution réussie.

## 3. Vérifier le mapper et la carte
`mapper-list` répertorie les types de mappers enregistrés, `mapper-info` décrit un type et `audit-board` vérifie les contraintes de la carte. Le numéro de mapper relie l'en-tête de la ROM à des hypothèses sur le câblage physique. Un nom ne suffit pas à établir la capacité, la présence de CHR-RAM ou le comportement des banques fixes.

{{CODE:2}}

`--allow-unimplemented` autorise la poursuite de l'observation malgré des éléments non implémentés. Une exécution avec cette option ne prouve pas leur prise en charge.

## 4. Commandes des manettes
`run --pad1` et `--pad2` utilisent les masques bruts NES : A=1, B=2, SELECT=4, START=8, UP=16, DOWN=32, LEFT=64 et RIGHT=128. Additionnez les valeurs pour appuyer simultanément sur plusieurs boutons.

{{CODE:3}}

Cette commande maintient A pendant 120 images. Utilisez le rejeu pour des actions ordonnées, comme passer du titre au démarrage puis confirmer. L'exemple CLI `replay-record` enregistre une exécution de référence sans saisie interactive ; il ne correspond pas à l'enregistrement d'une personne utilisant une interface graphique.

## 5. Instantanés et rejeu
{{CODE:4}}

Les états permettant une reprise utilisent les instantanés de version 2. Conservez la correspondance entre le SHA-256 de la ROM et son état. `snapshot-resume` poursuit l'exécution depuis un point sauvegardé. `snapshot-rebase` transfère explicitement un état vers une autre ROM compatible, selon un contrat fourni. Réutiliser sans vérification un ancien état après avoir modifié le code ou le placement RAM est risqué ; reproduisez normalement les mêmes actions depuis le démarrage.

## 6. Traces, diagnostics et profils
{{CODE:5}}

Une trace enregistre ce qui s'est passé dans le temps ; les diagnostics signalent les observations correspondant à des règles ; un profil montre où l'exécution s'est concentrée. Quelques images autour d'une anomalie sont généralement plus faciles à examiner qu'une longue trace complète.

Fournissez le JSON de débogage de la compilation correspondante avec `--kitaqfc-debug`. Une observation dépourvue d'informations de lignes source ne doit pas être présentée comme une trace complète au niveau du source.

## 7. Enregistrer le son et les images
{{CODE:6}}

Les changements de registres, le PCM généré et un son conforme à l'attente sont trois vérifications distinctes. Notez le mapper lors des tests audio, qu'ils concernent les canaux intégrés ou une extension. Un PNG unique ne prouve ni le mouvement ni la réaction aux commandes ; conservez aussi les états et les entrées qui le précèdent et le suivent.

## 8. Désassemblage et décompilation
{{CODE:7}}

`disasm` produit des suites d'instructions. `decompile` produit des limites de fonctions candidates, des graphes de flot de contrôle, des références et du pseudocode. En présence de banques commutables, une adresse processeur ne suffit pas à identifier une position physique dans la ROM. Fournissez au besoin l'état du mapper avec `--snapshot` et étayez l'analyse par des traces d'exécution ou des annotations. Il ne s'agit pas d'une restitution parfaite du source d'origine.

## 9. Raccorder SARAKURA
{{CODE:8}}

Comme dans KOKURA, `--emit-diagnostics` de KUROSAKI reçoit un **chemin de fichier JSONL**. Distinguez les traces processeur des fichiers d'événements de diagnostic.

## 10. Périmètre de publication
KUROSAKI-GUI reste non publié. Ce manuel porte sur l'outil en ligne de commande et ses API d'intégration.

## 11. FDS et RAM de sauvegarde
`fds-inspect` examine la structure du disque ; `export-assets` exporte les ressources. Testez le FDS séparément des cartouches NES, car le démarrage, le BIOS et les accès disque ont des exigences différentes. Les fichiers de sauvegarde sur pile `.sav` et les instantanés `.kss.json` ont des rôles distincts ; utilisez une disposition de sauvegarde prise en charge par l'implémentation.

{{CODE:9}}

`battery-export` extrait la RAM de sauvegarde brute d'une ROM et d'un instantané correspondants. `battery-run` charge cette RAM et démarre à la mise sous tension ; il ne restaure pas l'état d'exécution interrompue du processeur ou du PPU. Indiquez la sortie avec `--save-out`. Ces opérations nécessitent une ROM prise en charge disposant de RAM de sauvegarde et ne s'appliquent pas à tous les exercices.
