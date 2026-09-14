## Outil Windows prêt à l'emploi
Le dépôt contient désormais `kokura-cli.exe` à sa racine. Téléchargez l'archive ZIP du dépôt et conservez les mentions de licence avec l'exécutable. Cet outil Windows x64 en ligne de commande ne nécessite aucune installation de Rust, Python ou .NET pour fonctionner. Les étapes de compilation ci-dessous servent à le reconstruire depuis les sources. Le code propre au projet est proposé par DAISUKE OBA sous licence MIT ; les conditions des dépendances sont conservées dans BINARY_NOTICES.md et licenses/.

## 1. À quoi sert KOKURA ?
KOKURA émule les logiciels GB/CGB et enregistre des observations sur l'image, le son, l'exécution du processeur, la mémoire, les banques, les commandes et les événements de diagnostic. Ce manuel utilise le nom actuel `kokura-cli.exe` ; les anciennes références à `kokuradbg` ne désignent pas nécessairement l'exécutable de cette distribution.

## 2. Compiler et lancer votre première ROM
{{CODE:0}}

Installez Rust et Cargo. Compilez la crate indiquée si vous n'avez besoin que de l'outil en ligne de commande. Utilisez la ROM hello du volume 1. Le nombre d'images par défaut est un ; précisez `--run-frames` pour atteindre la scène souhaitée. Cette valeur compte des images émulées, pas des secondes d'attente.

## 3. Choisir DMG ou CGB
`--hardware auto` est le réglage par défaut ; `dmg` et `cgb` imposent un modèle. Testez les ROM à deux modes sur les deux modèles. Le refus de démarrage d'une ROM réservée à la CGB en mode DMG n'indique pas, à lui seul, une panne de l'émulateur.

{{CODE:1}}

## 4. Fournir des commandes
`--input` maintient une combinaison de boutons simultanés ; `--input-seq` fournit une séquence dans le temps. Les noms sont `A,B,START,SELECT,UP,DOWN,LEFT,RIGHT` ; utilisez `NONE` pour les intervalles sans bouton appuyé. Dans PowerShell, entourez de guillemets les séquences contenant des points-virgules.

{{CODE:2}}

Prévoyez un intervalle de relâchement pour tester les nouveaux appuis. Maintenir A pendant 120 images n'équivaut pas à appuyer 120 fois sur A. Avec l'exercice du compteur d'appuis, la séquence ci-dessus doit incrémenter le compteur une seule fois.

## 5. Images, vidéo et audio
`--png` enregistre l'écran final. `--screenshot`, associé à `--screenshot-frames`, capture les images choisies. `--record-video` enregistre une vidéo et `--record-wav` l'audio. Il est normal d'obtenir un WAV silencieux à partir d'un programme hello qui n'utilise pas l'APU.

{{CODE:3}}

Les plages s'écrivent `start:end`. Conservez le rapport pour distinguer les numéros d'images accumulés dans un état chargé des positions dans l'exécution courante. Vérifiez séparément le son audible, la hauteur, les coupures et l'écrêtage. Un enregistrement d'émulateur ne prouve pas une égalité échantillon par échantillon avec le matériel physique.

## 6. Sauvegarder et reprendre un état
{{CODE:4}}

Utilisez normalement la même ROM et la même version de l'émulateur. Un état d'émulateur diffère de la sauvegarde propre au jeu. Les fichiers KQS de l'outil en ligne de commande et les états JSON de l'API C sont des formats distincts ; changer leur extension ne les rend pas interchangeables.

## 7. Observer les symboles et la mémoire
Les fichiers annexes `.map`, `.source_map.txt`, `.dbg2.json` et `.build_report.json` peuvent être détectés à côté de la ROM. Conservez chaque ROM avec les fichiers de sa compilation : ceux d'une autre version peuvent conduire à des observations trompeuses.

{{CODE:5}}

`wram` est le nom de la fenêtre d'observation, 0xC000 son adresse de départ et 0x40 sa longueur. De petites fenêtres facilitent l'identification des variables modifiées. `--watch-baseline-mode` choisit une comparaison avec les valeurs initiales, l'image précédente ou une référence nommée.

## 8. Conditions d'arrêt, rejeu et rétroanalyse
`--breakpoint`, `--watchpoint`, `--run-until` et `--snapshot-at` arrêtent ou sauvegardent l'exécution selon des conditions. La syntaxe de leurs arguments diffère ; consultez la référence et l'aide enregistrée ci-dessous.

{{CODE:6}}

Repérez la première divergence, puis observez un intervalle plus court autour d'elle. `--decompile-out` produit du pseudocode et des informations de flot de contrôle ; `--disassemble-out` affiche les instructions du processeur. La décompilation ne restaure pas parfaitement le code C d'origine ni les noms des variables.

## 9. Envoyer les diagnostics à SARAKURA
{{CODE:7}}

Dans KOKURA, `--emit-diagnostics` reçoit un **nom de fichier JSONL**, par exemple `out/gb_events.jsonl`. Un rapport d'exécution JSON ordinaire ou une trace processeur JSONL ne constitue pas la même entrée qu'un fichier d'événements de diagnostic.

## 10. Tâches de communication
`pair` modélise deux machines. `four_player_adapter` organise des échanges logiques dans lesquels l'hôte sélectionne son correspondant. `dmg07` modélise le protocole physique DMG-07. Fournissez une tâche JSON à `--link-job` ou configurez les sessions avec `--link-topology` et `--link-session`.

{{CODE:8}}

Chaque ROM doit implémenter la communication. Exécuter deux programmes hello ordinaires ne teste pas la bibliothèque de liaison. Consignez la ROM, l'emplacement, les commandes et l'état de chaque session, et indiquez les comportements du périphérique physique qui restent non testés.

## 11. Applications externes
L'ABI C publiée se trouve dans `kokura-capi` ; l'accès Python est fourni par la passerelle et la crate Python. Établissez une reproduction minimale en ligne de commande avant d'examiner un problème d'intégration.

## 12. Lire les rapports dans l'ordre
Vérifiez d'abord le nombre d'images exécutées et le motif d'arrêt, puis l'écran, le résultat des commandes, le son, les erreurs et avertissements, et enfin le profil. Une longue observation d'un écran titre sans aucune entrée peut naturellement produire des avertissements d'écran statique ou de compteur ordinal répété. Comparez les avertissements à la scène attendue au lieu de considérer mécaniquement chacun d'eux comme une anomalie.
