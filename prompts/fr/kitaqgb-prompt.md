# Développer un jeu avec KITAQGB, KOKURA et SARAKURA

Renseignez les besoins, puis transmettez ce document entier à l’assistant IA. Les commandes supposent que les dépôts `kitaqgb`, `kitaqfc`, `kokura`, `kurosaki`, `sarakura` et `kitaq-docs`, ainsi que le projet `game-gb` ou `game-fc`, se trouvent dans le même dossier parent. Exécutez-les depuis ce dossier et adaptez les chemins à votre environnement.

## Besoins

- Titre du jeu : <à renseigner>
- Genre et mécanique principale : <à renseigner>
- Commandes et conditions de réussite ou d’échec : <à renseigner>
- Écrans, niveaux, ennemis et objets indispensables : <à renseigner>
- Style graphique, musique et effets sonores : <à renseigner, avec les chemins des ressources fournies>
- Sauvegarde, communication, périphériques et autres besoins : <à renseigner, ou aucun>
- Dossier du projet : <à renseigner>
- Conditions de redistribution : <par exemple, code et ressources originaux pouvant être publiés sous licence MIT>

- Machine cible : <Game Boy d’origine / compatibilité GB et CGB / CGB uniquement>
- Objectif de performances : <par exemple, 60 mises à jour de la logique par seconde en jeu normal ; préciser ce qui est acceptable dans les scènes exigeantes>

## Travail demandé

Implémentez le jeu avec KITAQGB et ses bibliothèques. Utilisez KOKURA pour l’exécution et le débogage, et SARAKURA pour organiser les diagnostics et comparer les résultats avant et après correction.

Répétez ce cycle jusqu’à satisfaire les critères d’acceptation : préciser la spécification → implémenter une petite modification → compiler → appliquer des entrées et observer → rechercher la cause → corriger → refaire les tests dans les mêmes conditions. Un plan, du code fourni ou une compilation réussie ne suffisent pas à terminer le travail.

### Vérifier l’environnement et les critères d’acceptation

1. Lisez les consignes du dossier de travail, les README, les manuels HTML ainsi que les en-têtes et implémentations des bibliothèques utilisées. Relevez les chemins des exécutables et leurs versions ou empreintes SHA-256. Vérifiez les commandes dans la sortie réelle de `--help` et les API dans le code source.
2. Définissez des critères mesurables pour les entrées, l’image, le son, la progression et la fréquence de mise à jour. Par exemple : appuyer puis relâcher START lance la partie ; une collision retire une vie ; la pause coupe les sons prévus et la reprise rétablit la lecture.
3. Ne posez de questions que sur les ambiguïtés importantes. Prenez de façon autonome les décisions courantes et réversibles. Ne réduisez pas les exigences ni les critères d’acceptation.
4. Commencez par faire passer un petit exemple fourni dans le compilateur, l’émulateur et SARAKURA. Cela vérifie leur articulation, pas l’achèvement du jeu demandé.

### Réaliser une première version jouable

- Utilisez le dialecte C de KITAQGB et `void main()`. Ne supposez pas que les API du C sur ordinateur ou de GBDK sont disponibles. Incluez les implémentations `.c` nécessaires, pas seulement leurs déclarations ; vérifiez initialisation, unités, signe, plages de valeurs, durée de vie des tampons et banques ROM.
- Prévoyez les mises à jour VRAM/OAM, VBlank, interruptions, pile, banques ROM/WRAM et limites de tuiles et de sprites. La capacité totale et libre de la file de transferts est distincte de la capacité et de l’espace libre de la VRAM physique.
- Un jeu DMG ne doit pas dépendre de fonctions réservées au CGB. Si les deux modes sont pris en charge, testez chacun d’eux.
- Utilisez la police originale fournie dans `ascii.c` pour les lettres, chiffres et symboles, et vérifiez la correspondance entre caractères et tuiles.

- Reliez d’abord démarrage, titre, personnage contrôlable, réussite ou échec, et nouvelle partie. Enrichissez ensuite le contenu.
- Conservez les sources modifiables des graphismes, musiques et effets ainsi que les étapes de génération. Vérifiez que la compilation utilise réellement les données exportées.
- Rédigez les commentaires du code en anglais et les comptes rendus d’avancement en français. Gardez les rapports standard de SARAKURA en anglais.

### Relier chaque compilation à son exécution

Séparez les sorties par itération, par exemple dans `out/iter-001`. Consignez commandes, codes de sortie et empreintes du code, des ressources, outils, ROM et métadonnées. N’exécutez jamais une ancienne ROM après une compilation échouée. Les cartes mémoire, correspondances avec les sources et informations de débogage doivent provenir de la même compilation que la ROM.

Voici une vérification de base pour DMG. Préparez `main.c` et les implémentations de bibliothèque nécessaires ; adaptez les options et la séquence d’entrées au jeu.

```powershell
$iteration = '.\game-gb\out\iter-001'
New-Item -ItemType Directory -Force $iteration | Out-Null

# Include all additional implementation units required by the game.
& '.\kitaqgb\kitaqgb.exe' '.\game-gb\src\main.c' `
  -I '.\kitaqgb\lib' -o "$iteration\game.gb" `
  --profile=dev --rst-disable --stack-bank=fixed --no-disasm `
  "--emit-ai-metadata=$iteration\build.json"
if ($LASTEXITCODE -ne 0) { throw 'Build failed; inspect the build log.' }

# This sequence presses START once, with released intervals on both sides.
& '.\kokura\kokura-cli.exe' "$iteration\game.gb" `
  --hardware dmg --run-frames 300 `
  --input-seq 'NONE:60;START:1;NONE:239' `
  --png "$iteration\frame.png" --record-wav "$iteration\audio.wav" `
  --dump-report "$iteration\run.json" `
  --emit-diagnostics "$iteration\events.jsonl"
if ($LASTEXITCODE -ne 0) { throw 'Emulator run failed; inspect the run log.' }

& '.\sarakura\sarakura.exe' gb analyze `
  --metadata "$iteration\build.json" --events "$iteration\events.jsonl" `
  --frames 300 --out "$iteration\analysis" --fail-on error
if ($LASTEXITCODE -ne 0) { throw 'Inspect the analysis report and fix the cause.' }
```


`--hardware dmg` sélectionne la Game Boy d’origine. Pour tester CGB ou les deux modes, faites correspondre l’en-tête ROM et le matériel choisi dans l’émulateur. La séquence appuie une fois sur START entre deux périodes où les boutons sont relâchés. Une exécution de 300 images ne teste pas l’ensemble du jeu.

### Vérifier l’image, le son, l’état et les performances

- Conservez les scénarios d’entrée en distinguant pression, maintien et relâchement. Parcourez toutes les voies prévues : démarrage, début de partie, déplacement, actions, collisions, défilement, changement de niveau, fin de partie, redémarrage, pause et, si nécessaire, sauvegarde ou communication.
- Gardez les PNG des images pertinentes, les entrées, rapports d’exécution, diagnostics JSONL, WAV et observations nécessaires d’état ou de mémoire. Vérifiez le nombre d’images atteint et la raison de l’arrêt. Ouvrez réellement les images : une seule capture ne prouve ni mouvement ni réponse aux commandes. Comparez compteurs, positions et transitions aux valeurs attendues ; examinez bords d’écran, limites de tuiles et d’attributs, et scènes chargées en sprites.
- Vérifiez musique, effets, lecture simultanée, coupures, pause et reprise. Produire un WAV ne prouve pas la justesse du son. Si l’écoute est impossible, distinguez les contrôles numériques ou de forme d’onde réalisés des qualités sonores non vérifiées.
- Mesurez les scènes exigeantes, le travail du CPU cible, les mises à jour et les transferts ; sur FC, incluez NMI. Le débit de l’émulateur sur l’ordinateur hôte n’est ni la fréquence de mise à jour du jeu ni une preuve de vitesse sur matériel réel. Poursuivre avec `--allow-unimplemented` ne prouve pas la prise en charge de la fonction manquante.

### Analyser, corriger et refaire les tests

- Fournissez à SARAKURA les métadonnées de la ROM testée et le JSONL diagnostic de cette exécution. Une trace CPU ou un rapport d’exécution ordinaire ne les remplace pas. `--frames` précise les conditions d’analyse ; SARAKURA n’exécute pas la ROM et ne modifie pas automatiquement les sources.
- Lisez `report.html`, `ai_diagnostics.json`, `repair_prompt.md` et `retest_plan.json`. Confrontez les diagnostics aux étapes de reproduction, images, sons et sources. Distinguez les emplacements ou causes supposés des faits vérifiés, et les boucles d’attente normales des blocages. Examinez chaque avertissement et notez les événements non pris en charge ou les limites d’analyse. Ne masquez pas les avertissements avec des filtres et ne raccourcissez pas les tests pour obtenir un succès.
- Réduisez les défauts à des cas minimaux, corrigez leur cause et recompilez. Si le compilateur ou l’émulateur est en cause, isolez son défaut du code du jeu et ajoutez une vérification de non-régression à la correction de l’outil.
- Refaites les tests avec les mêmes entrées, graine aléatoire, machine et standard vidéo, mapper, images observées et réglages diagnostics. Utilisez les métadonnées propres à chaque ROM ; ne réutilisez pas aveuglément les états sauvegardés après modification du code ou de la disposition RAM.

```powershell
& '.\sarakura\sarakura.exe' baseline-delta `
  --baseline '.\game-gb\out\iter-001\analysis' `
  --current '.\game-gb\out\iter-002\analysis' `
  --out '.\game-gb\out\delta.json' --markdown '.\game-gb\out\delta.md' `
  --fail-on-new error --fail-on-regression error --enforce
```


Associez les différences de diagnostic aux critères d’acceptation des commandes, graphismes et sons. Si le même échec se répète, réexaminez les preuves et l’hypothèse au lieu d’enchaîner des modifications arbitraires.

### Conditions de fin et livrables

Rejouez tous les scénarios obligatoires avec la ROM finale compilée depuis les sources et réglages livrés. L’invincibilité, des entrées automatiques de test ou un autre mapper ne suffisent pas à valider une partie normale dans la version finale. Fournissez un tableau reliant besoins et tests, expliquez les avertissements restants et indiquez les éléments non vérifiés ou non pris en charge. Précisez explicitement l’absence de tests sur matériel physique, le cas échéant.

Livrez les sources, l’identification des outils et bibliothèques, les ressources modifiables, les scripts reproductibles de compilation et de test, la ROM, les preuves finales et un README expliquant installation, commandes et limites connues. Incluez les replays et le programme de test si nécessaire. Publiez ou transmettez des fichiers à l’extérieur uniquement dans le périmètre expressément autorisé. Supprimez les compilations intermédiaires et traces temporaires inutiles après vérification, mais conservez sources, ressources, livrables et preuves de non-régression nécessaires.

Si l’environnement ou les permissions empêchent un contrôle obligatoire, indiquez les étapes exactes de reproduction et l’action nécessaire. Ne déclarez pas le travail terminé.
