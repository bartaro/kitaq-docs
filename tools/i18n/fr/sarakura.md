## Outil Windows prêt à l'emploi
Le dépôt contient désormais `sarakura.exe` à sa racine. Téléchargez l'archive ZIP du dépôt et conservez les mentions de licence avec l'exécutable. Cet outil Windows x64 en ligne de commande ne nécessite aucune installation de Rust, Python ou .NET pour fonctionner. Les étapes de compilation ci-dessous servent à le reconstruire depuis les sources. Le code propre au projet est proposé par DAISUKE OBA sous licence MIT ; les conditions des dépendances sont conservées dans BINARY_NOTICES.md et licenses/.

## 1. Le rôle de SARAKURA
SARAKURA rassemble les informations de compilation et les événements de diagnostic des émulateurs pour les présenter sous une forme utile aux corrections et aux nouveaux tests. Il n'exécute pas les ROM et ne modifie pas discrètement votre code C.

## 2. Compiler l'outil
{{CODE:0}}

Les commandes courtes `sarakura` supposent que l'exécutable est dans PATH. Sinon, utilisez son chemin. Choisissez `gb analyze` pour la GB ou `fc analyze` pour la FC.

## 3. Votre première analyse
Deux entrées sont nécessaires : `--metadata` reçoit le JSON produit à la compilation et `--events` le JSONL de diagnostic produit à l'exécution. Un fichier JSONL contient un objet JSON par ligne.

{{CODE:1}}

Ouvrez le fichier de sortie `report.html` dans un navigateur. Vérifiez la cible, le nombre d'images observées, le nombre d'erreurs et celui des avertissements avant de lire les diagnostics individuels. `--frames` décrit les conditions d'analyse ; il ne demande pas à SARAKURA d'exécuter une ROM pendant ce nombre d'images.

## 4. Examiner d'abord les entrées
{{CODE:2}}

Traitez les fichiers illisibles, les incohérences de plateforme et les types d'événements non pris en charge avant d'examiner le comportement du jeu. Fournir un rapport ordinaire d'émulateur comme fichier d'événements n'en fait pas une entrée de diagnostic valide.

## 5. Interpréter les diagnostics
Une erreur mérite la priorité, un avertissement peut indiquer un problème selon les circonstances et une information apporte du contexte. La gravité aide au tri, mais ne connaît pas toute l'intention du jeu. Une observation de compteur ordinal répété ne permet pas toujours de distinguer une boucle d'attente normale sur un écran titre d'un blocage.

Comparez l'empreinte de la ROM, la séquence d'entrées, la scène, l'écran, le son et l'emplacement source. Gardez les mêmes conditions avant et après correction ; sinon, une diminution des diagnostics peut simplement signifier qu'une autre scène a été exécutée.

## 6. Fichiers de sortie
Les explications intégrées, les conseils de diagnostic et les instructions de correction sont en anglais, et le HTML déclare `lang="en"`. Les chaînes de l'utilisateur et les identifiants d'événements ne sont pas traduits automatiquement. Le masquage par défaut remplace certains libellés et chemins de projet ; il n'anonymise pas toutes les adresses ni toutes les observations. Examinez les rapports avant de publier une analyse fondée sur des entrées privées.

| Fichier | Rôle |
| --- | --- |
| ai_diagnostics.json | Diagnostics normalisés pour un traitement automatisé |
| diagnostic_summary.json | Comptages et résumé |
| report.html | Rapport destiné à la lecture humaine |
| repair_prompt.md | Contexte de départ pour rechercher une correction |
| repair_plan.json / .md | Ordre et cibles des corrections |
| automation_plan.json / .md | Plan de travail fondé sur les capacités des outils |
| retest_plan.json | Plan des vérifications à refaire |
| repro_bundle.zip | Archive des informations de reproduction |

Produire un plan ne signifie pas l'exécuter. Après une modification du source C ou de la ROM, relancez le compilateur, l'émulateur et SARAKURA.

## 7. Catalogues, filtres et couverture
{{CODE:3}}

`catalog` répertorie les règles de diagnostic, `pack-plan` les regroupe par domaine et `coverage` examine les événements correspondants effectivement observés. La présence d'une entrée dans le catalogue ne garantit pas que l'émulateur actuel émet cet événement.

{{CODE:4}}

`--diagnostic-rule` choisit un nom d'événement ou un identifiant de catalogue, `--phase` une étape et `--diagnostic-pack` un domaine. Masquer un diagnostic par un filtre ne résout pas sa cause.

## 8. Comparer avant et après
{{CODE:5}}

Les résultats sont classés comme nouveaux, résolus, améliorés, persistants ou aggravés. Distinguez les problèmes qui demeurent de ceux qui viennent d'apparaître. Conservez les mêmes entrées, nombres d'images et filtres de diagnostic pendant les comparaisons.

## 9. Validation et intégration continue
{{CODE:6}}

L'intégration continue automatise les vérifications reproductibles. `ci-summary` ne modifie le code de sortie du processus que si `--enforce` est fourni ; sinon, lisez son verdict JSON. Pour analyze, `--fail-on error` renvoie un code non nul en présence d'erreurs. Le réglage par défaut `never` ne fait pas échouer le processus à cause des diagnostics : choisissez donc explicitement une politique en CI. Le choix `warn` ajoute les avertissements aux conditions d'échec.

```powershell
sarakura ci-summary --diagnostics .\out\report --fail-on error --enforce
if ($LASTEXITCODE -ne 0) { throw "The diagnostic failure condition was met" }
```

Une validation de schéma réussie vérifie le format des données. Pour vérifier qu'un jeu fonctionne comme prévu, il faut aussi tester les commandes, l'écran et le son.

## 10. Gérer les fichiers de reproduction
`normalize-events` normalise les événements. `inspect-repro` examine une archive de reproduction. Avant de la partager, vérifiez que ses informations correspondent à la ROM visée et qu'elle comprend les étapes d'entrée nécessaires. `--allow-project-labels` conserve explicitement les libellés et identifiants issus du projet.

## 11. Entrées minimales pour s'exercer
Le manuel fournit de petits exemples GB/FC de métadonnées de compilation et d'événements. Ouvrez le [rapport synthétique GB](verification/sarakura-gb-synthetic.html) ou le [rapport synthétique FC](verification/sarakura-fc-synthetic.html). `samples/sarakura_demo.ps1` montre comment les analyser. Ces entrées synthétiques servent à apprendre le format ; elles ne constituent pas des observations recueillies sur une vraie ROM. Pour les tests de ROM réelles, utilisez les événements enregistrés par KOKURA ou KUROSAKI.

## 12. Un cycle de correction et de nouveau test
1. Reproduisez le problème avec la même ROM et les mêmes entrées, en conservant journaux et images.
2. Organisez les pistes avec SARAKURA et examinez le source concerné.
3. Apportez une modification ciblée sur la cause.
4. Recompilez et rejouez les mêmes actions.
5. Comparez baseline-delta avec les images, l'audio et le comportement du jeu.

Gardez ce cycle court pour que chaque modification et son effet restent compréhensibles.
