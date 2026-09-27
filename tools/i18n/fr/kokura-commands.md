## 13. Exemples de commandes et syntaxe exacte des arguments

Exécutez ces commandes PowerShell depuis le répertoire parent des dépôts placés côte à côte. Créez d’abord le dossier de sortie avec `New-Item -ItemType Directory -Force out`. Remplacez `out/game.gb` par votre ROM. KOKURA place ses options après le chemin de la ROM ; il n’utilise pas la sous-commande `run` de KUROSAKI. `--help` affiche les options de l’exécutable installé.

### 13.1 Choisir une opération et une limite d’images

| Argument | Rôle et comportement |
| --- | --- |
| `ROM` | Fichier ROM pour une exécution ordinaire. Une tâche ou une matrice peut fournir sa propre ROM. |
| `--hardware auto`, `dmg`, `cgb` | Sélection du matériel. La valeur par défaut est `auto` ; testez explicitement les deux modes pour un jeu compatible avec les deux machines. |
| `--run-frames 120` | Nombre maximal d’images en exécution directe, fixé à 1 par défaut. Une condition d’arrêt peut terminer l’exécution plus tôt. Les séquences d’entrée ont aussi leurs propres durées. |
| `--job out/test.json` | Exécute une tâche JSON. Sa limite d’images se définit dans `run.frames` ; la ROM, l’état, les entrées et les captures proviennent de la tâche. Les chemins relatifs internes sont résolus par rapport au fichier de tâche. |
| `--dump-report out/run.json` | Enregistre le rapport JSON obtenu. Sans destination, une exécution ordinaire écrit le rapport sur la sortie standard. |
| `--regression-matrix out/matrix.json` | Exécute des tâches accompagnées d’observations attendues. Examinez les résultats de chaque cas dans le JSON : la réussite de la commande ne signifie pas que tous les cas ont passé les vérifications. |

Choisissez une opération par invocation. L’ordre de priorité est : décompilation, désassemblage, matrice de régression, tâche de liaison, sessions liées définies dans la commande, puis exécution ordinaire. Combiner les modes ne les exécute pas successivement.

{{COMMAND:0}}

Cette commande avance d’au plus 120 images émulées et enregistre l’écran final ainsi qu’un rapport. Vérifiez le nombre réel d’images et la raison de l’arrêt avant d’interpréter la capture.

### 13.2 Maintenir des boutons ou fournir une séquence temporisée

| Option | Syntaxe et utilisation |
| --- | --- |
| `--input "A,RIGHT"` | Maintient les deux boutons pendant une exécution directe. Les noms ne sont pas sensibles à la casse. `NONE` relâche tous les boutons. |
| `--input-seq "NONE:30;A:1;NONE:89"` | Intervalles `BUTTONS:FRAMES` séparés par des points-virgules et exécutés dans l’ordre. Ici : relâchement pendant 30 images, appui sur A pendant une image, puis relâchement pendant 89 images. |
| `--input-script "NONE:30;A:1;NONE:89"` | Accepte le même texte de séquence ; ce n’est pas un nom de fichier. Si les deux options de séquence sont présentes, `--input-script` a priorité. |

Les noms de boutons sont `RIGHT,LEFT,UP,DOWN,A,B,SELECT,START`. Les masques hexadécimaux sont RIGHT=0x01, LEFT=0x02, UP=0x04, DOWN=0x08, A=0x10, B=0x20, SELECT=0x40 et START=0x80. Ce sont les masques d’entrée de KOKURA ; ne réutilisez pas ceux des manettes NES. Dans PowerShell, placez toute la séquence entre guillemets. Pour tester un nouvel appui, prévoyez des intervalles de relâchement et faites couvrir à la séquence toute la période d’observation souhaitée.

{{COMMAND:1}}

Dans l’exemple du compteur de boutons, le compteur doit augmenter une fois. Une seule image fixe ne permet pas d’établir si la répétition d’un bouton maintenu fonctionne : comparez un appui prolongé à plusieurs appuis distincts.

### 13.3 Capturer l’écran, les mouvements et le son

| Option | Syntaxe et utilisation |
| --- | --- |
| `--png out/final.png` | Enregistre l’écran final ; a priorité sur `--screenshot` si les deux sont présents. |
| `--screenshot out/frame.png` | Autre destination pour une capture d’écran. PNG et BMP sont pris en charge ; un chemin sans extension reçoit `.png`. |
| `--screenshot-frames 30:32` | Enregistre chaque image sélectionnée en ajoutant son numéro au nom de fichier. Nécessite une destination de capture. |
| `--record-wav out/audio.wav` | Enregistre le son au format WAV. Utilisez une ROM et un intervalle où du son est réellement joué. |
| `--record-wav-frames 1:180` | Sélectionne l’intervalle d’enregistrement, bornes incluses. Il s’agit de numéros d’images, pas de nombres d’échantillons. |
| `--record-video out/motion.gif` | Enregistre les mouvements en GIF ou Y4M. Un chemin sans extension reçoit `.gif` ; MP4 n’est pas un format accepté. |
| `--record-video-frames 30:120` | Sélectionne l’intervalle vidéo, bornes incluses. |
| `--audio-buffer-frames 8192` | Définit la capacité du tampon audio en trames d’échantillons stéréo, et non en images vidéo émulées ou en échantillons gauche/droite individuels. |

Les intervalles de capture sont décimaux et commencent à 1 : `30` sélectionne une image, tandis que `30:32` inclut les images 30, 31 et 32. Zéro et les intervalles inversés sont rejetés. Les indices concernent l’exécution en cours : conservez donc le rapport lorsque vous reprenez un état antérieur. Créez les dossiers parents avant la capture.

{{COMMAND:2}}

Examinez plusieurs images pour évaluer un défilement ou une animation. Évaluez le son avec le WAV ; un numéro de fin visible à l’écran ne prouve pas que le canal attendu a joué.

### 13.4 Enregistrer et reprendre l’état de la machine

| Option | Rôle et priorité |
| --- | --- |
| `--save-state out/checkpoint.kqs` | Enregistre l’état de la machine en fin d’exécution. |
| `--snapshot out/checkpoint.kqs` | Même rôle de sortie ; a priorité sur `--save-state`. |
| `--load-state out/checkpoint.kqs` | Charge un état KQS avant l’exécution. |
| `--resume-state out/checkpoint.kqs` | A priorité sur `--load-state` et peut remplacer l’état d’entrée d’une tâche. |
| `--snapshot-at "frame=60&&frame_end=>out/frame60.kqs"` | Enregistre lorsqu’une condition d’observation est remplie. Répétez l’option pour plusieurs demandes. Sans `=>path`, un nom numéroté est dérivé du nom de la ROM dans le répertoire courant. |

Utilisez un état correspondant à la ROM et à la version de l’émulateur. KQS représente l’état de la machine, pas la RAM de sauvegarde de la cartouche ni la sérialisation JSON de l’API C.

{{COMMAND:3}}

### 13.5 Examiner des zones mémoire nommées

| Option | Syntaxe et utilisation |
| --- | --- |
| `--symbols out/game.map` | Charge les symboles issus de la compilation correspondante. |
| `--source-map out/game.source_map.txt` | Associe l’exécution aux emplacements du code source. |
| `--toolchain-metadata out/game.dbg2.json` | Charge les métadonnées structurées de la chaîne de compilation. Les fichiers compagnons correspondants peuvent aussi être détectés à côté de la ROM. |
| `--watch-window "player:0xC700:16"` | Observe 16 octets à partir de 0xC700 sous le nom player. Répétez l’option pour d’autres zones. Elle observe la mémoire, mais n’arrête pas elle-même l’exécution. |
| `--watch-baseline-mode initial` | Compare aux valeurs initiales. `previous-frame` compare des images successives ; `named` sélectionne une référence explicitement capturée. |
| `--watch-baseline-tag ready` | Choisit le nom de la référence pour une comparaison nommée. |
| `--capture-watch-baseline "ready=>frame=30&&frame_end"` | Capture une référence nommée lorsque la condition est remplie. Répétez pour d’autres références. |
| `--watch-fields preview,diff` | Choisit les groupes de champs observés : `hash`, `activity`, `preview`, `baseline`, `diff`, `insights` ou `all`. Les octets d’aperçu ne constituent qu’un aperçu limité, pas un vidage mémoire sans limite. |
| `--report-sections cpu,watched_memory` | Conserve les sections indiquées. `meta` et `schema_version` restent présents. Un nom inconnu ne crée pas de nouvelle section. |
| `--report-minimal cpu,watched_memory` | Autre entrée pour la liste des sections, prioritaire sur `--report-sections`. Exige des valeurs séparées par des virgules ; ce n’est pas un simple commutateur booléen. |

Les adresses et tailles acceptent le décimal ou l’hexadécimal préfixé par `0x`. Trouvez les variables avec les symboles de la compilation actuelle ; 0xC700 n’est ici qu’un exemple d’adresse, pas un emplacement standard du joueur.

{{COMMAND:4}}

### 13.6 S’arrêter sur des événements d’exécution ou matériels

| Option | Syntaxe et rôle |
| --- | --- |
| `--breakpoint "pc:0x0150"` | S’arrête à une adresse CPU. `symbol:main` utilise les symboles ; ajoutez `@bank:2` pour limiter la banque. |
| `--watchpoint "player@0xC700+4"` | S’arrête lors d’une écriture dans une plage de quatre octets. Le préfixe facultatif nomme le point de surveillance ; sans `+size`, un seul octet est surveillé. |
| `--stop-on-mmio "scroll@0xFF43"` | S’arrête lors d’une écriture dans le registre MMIO indiqué, ici SCX. |
| `--stop-on-irq "vblank:serviced"` | Sélectionne une source d’interruption et une phase : `requested`, `serviced`, `blocked` ou `any`. Une phase seule correspond à toutes les sources. |
| `--stop-on-dma oam_start` | Sélectionne un événement DMA. Noms acceptés : `oam_start`, `oam_complete`, `hdma_start`, `hdma_block`, `hdma_complete`, `hdma_cancel`, `gdma_stall`, `hdma_deferred`, `hdma_ignored`. |
| `--run-until "frame=60&&frame_end"` | S’arrête lorsque tous les termes d’une condition d’observation correspondent. Répétez l’option pour ajouter des demandes. |

Les marqueurs de point d’arrêt `pc:`, `symbol:` et `@bank:` sont sensibles à la casse. Adresses mémoire et banques utilisent le décimal ou l’hexadécimal préfixé par `0x`. Conservez une limite d’images même si vous demandez un arrêt dont la condition pourrait ne jamais se produire.

Les conditions d’observation utilisent `&&` pour ET ; ce ne sont pas des expressions C. Les termes acceptés sont `frame=`, `ly=`, `pc=`, `bank=`, `bank_pc=bank:pc`, `symbol=`, `source=`, `event=`, `ppu_mode=` (ou `mode=`) et `basis=`. Les valeurs d’image et de LY sont décimales. Les termes de symbole, source et événement comparent du texte. Les valeurs de basis comprennent `frame_start`, `frame_end`, `step`, `event`, `trace`, `snapshot`, `stop` ; les termes seuls `frame_start`, `frame_end`, `stop` et `vblank` sont également acceptés. Les comparaisons telles que `hp<10` ne font pas partie de cette grammaire.

{{COMMAND:5}}

La première commande permet d’examiner le point d’entrée ; la seconde repère le code qui modifie le défilement horizontal. Vérifiez que l’arrêt demandé s’est effectivement produit.

### 13.7 Enregistrer des points d’observation et comparer les exécutions

| Option | Rôle |
| --- | --- |
| `--trace-point "frame=30&&frame_end"` | Enregistre une observation lorsque la condition est remplie. Répétez pour plusieurs points. |
| `--timeline-out out/timeline.jsonl` | Enregistre la chronologie des observations. |
| `--trace-jsonl out/timeline.jsonl` | Autre destination de chronologie, prioritaire sur `--timeline-out`. Ne demande pas une trace exhaustive de toutes les instructions. |
| `--timeline-format jsonl` | Sélectionne `jsonl` (par défaut) ou `csv` ; choisissez vous-même l’extension correspondante. |
| `--replay-interval 1` | Active les points de contrôle de rejeu et définit leur intervalle en images. |
| `--replay-max-checkpoints 120` | Limite les points de contrôle conservés. Par défaut, le rejeu en conserve 16 avec un intervalle de 1. |
| `--rewind-on-stop-frames 10` | Demande un retour en arrière après un arrêt, à partir de l’historique de rejeu conservé. |
| `--stop-on-divergence` | Active le comportement d’arrêt sur divergence du contrôleur de rejeu. |
| `--dump-replay-tape out/baseline.json` | Exporte les données de rejeu enregistrées. Il faut activer leur enregistrement pour les produire. |
| `--compare-replay-tape out/baseline.json` | Compare avec un enregistrement de rejeu exporté. Pour une comparaison déterministe, utilisez la même ROM, les mêmes entrées et le même état initial. |
| `--compare-replay-watch-only` | Limite la comparaison aux observations de la mémoire surveillée, sans la considérer comme une comparaison complète de la machine. |
| `--snapshot-on-replay-mismatch out/mismatch` | Fournit un préfixe aux fichiers d’investigation créés lorsqu’une différence est détectée. |

{{COMMAND:6}}

Vérifiez le résultat de la comparaison et la première différence dans le rapport. La seule production des deux fichiers ne signifie pas que la comparaison est réussie.

### 13.8 Diagnostics et investigation reproductible

| Option | Comportement réel |
| --- | --- |
| `--emit-diagnostics out/events.jsonl` | Exporte les événements de diagnostic pour SARAKURA. |
| `--diagnostics-jsonl out/events.jsonl` | Autre destination des diagnostics en exécution directe ; `--emit-diagnostics` a priorité. |
| `--repro-bundle out/repro.zip` | Regroupe un rapport, les événements de diagnostic et un manifeste. La ROM et les métadonnées sont référencées par chemin, sans être incorporées ; les captures, états et traces ne sont pas ajoutés automatiquement. |
| `--break-on-diagnostic all` | Examine les diagnostics du rapport final pour déclencher la capture de fichiers d’investigation. Cela **n’arrête pas** le CPU à la première instruction fautive. Avec un filtre non vide, n’importe quel diagnostic final peut déclencher le chemin de capture. |
| `--png-on-diagnostic out/diagnostic-images` | Répertoire de l’écran final lors d’une capture de diagnostic. Le nom du fichier est `diagnostic_000001.png`. |
| `--snapshot-on-diagnostic out/diagnostic-states` | Répertoire de sortie de `diagnostic_000001.kqs`. Ces captures reflètent l’état final actuel, pas l’instant initial de chaque événement. |
| `--diagnostic-pack NAME` | Argument accepté ; le chemin d’exécution n’applique pas de pack de diagnostics. |
| `--diagnostic-rule RULE` | Argument accepté et répétable ; le chemin d’exécution n’applique pas ces sélections de règles. |
| `--diagnostic-summary-limit N` | Argument accepté ; le chemin d’exécution n’applique pas cette limite de résumé. |

{{COMMAND:7}}

Pour arrêter sur une instruction ou une écriture précise, utilisez les options du débogueur en 13.6. Interprétez les diagnostics dans leur contexte : un écran-titre volontairement inactif peut produire des observations qui ne sont pas des défauts du jeu.

### 13.9 Désassembler les instructions ou examiner le pseudocode

| Option | Syntaxe et rôle |
| --- | --- |
| `--disassemble-out out/code.txt` | Décode les instructions de la ROM sans lancer la tâche ordinaire d’émulation. |
| `--disassemble-range "0:0100-0150"` | Sélectionne `BANK:START-END` ; répétez pour plusieurs plages. **Les trois nombres sont hexadécimaux**, même sans `0x`. |
| `--disassemble-format text` | `text` (par défaut), `markdown` ou `json`. |
| `--decompile-out out/functions.json` | Génère du pseudocode et des informations de contrôle de flux. |
| `--decompile-format json` | `json` (par défaut), `markdown` ou `text`. |
| `--decompile-function main` | Sélectionne une fonction ; répétez pour d’autres fonctions. Des symboles correspondants améliorent leur identification. |
| `--decompile-all` | Inclut toutes les fonctions nommées connues du décompilateur. |
| `--decompile-annotations out/annotations.json` | Lit des annotations au format JSON du décompilateur. |
| `--decompile-trace out/trace.json` | Lit les métadonnées de trace du décompilateur ; un journal de diagnostic JSONL quelconque ne peut pas les remplacer. |

{{COMMAND:8}}

Le désassemblage permet de vérifier les instructions générées ; le pseudocode aide à parcourir le contrôle de flux. Aucun des deux ne restitue exactement le programme C d’origine. Conservez les symboles et métadonnées issus de la même compilation de la ROM.

### 13.10 Exécuter plusieurs machines liées

| Option | Syntaxe et rôle |
| --- | --- |
| `--link-job out/pair.json` | Lit la topologie et les sessions d’une tâche de liaison JSON. Les chemins relatifs sont résolus depuis son répertoire. |
| `--link-topology pair` | Sélectionne `pair`, `four_player_adapter` ou `dmg07` pour les sessions définies dans la commande. |
| `--link-session SPEC` | Ajoute une session. Il en faut au moins deux. Dans PowerShell, placez entre guillemets la chaîne complète dont les champs sont séparés par des barres verticales. |
| `--link-initial-peer-slot 1` | Choisit le correspondant initial lorsque la topologie permet cette sélection. |

Les champs de session comprennent `name`, `slot`, `rom`, `symbols`, `source_map`, `toolchain_metadata`, `load_state`, `save_state`, `input`, `input_sequence`, `audio_buffer_frames` et `watch_window`. `rom` est obligatoire. Un champ de surveillance peut contenir plusieurs zones séparées par des virgules, par exemple `a:0xC700:4,b:0xC710:4`. Utilisez des programmes qui échangent réellement des données série ; deux écrans en cours d’exécution ne prouvent pas à eux seuls que la communication fonctionne.
