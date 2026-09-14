## 1. Choisir les composants nécessaires
`fc.h` regroupe les déclarations, `core.h` définit les types et `intrinsics.h` déclare les opérations du compilateur. Une fonction C ordinaire de bibliothèque nécessite son implémentation `.c`. Les macros définies dans un en-tête et les fonctions intrinsèques ne nécessitent pas forcément de source du même nom.

{{CODE:0}}

Ne faites pas pointer `-I` vers la bibliothèque GB au nom proche. Par exemple, l'opération NES `__oam_dma()` ne reçoit aucun argument, contrairement à l'opération GB qui reçoit un pointeur.

## 2. Exécution et système
`runtime.c` fournit les fonctions C pour les registres PPU, la copie de travail de l'OAM et les files VRAM. Des fonctions intrinsèques telles que `__vramq_*` existent également. Vérifiez quelles données le gestionnaire NMI consomme, au lieu de mélanger des files distinctes aux noms similaires.

`system_init` initialise l'état des images et active la NMI. `system_wait_vblank` attend la NMI et incrémente le compteur logiciel d'images. **Sur FC, `system_set_vblank_callback` conserve le rappel, mais la fonction d'attente actuelle ne l'exécute pas.** N'y placez pas toutes les mises à jour du jeu en supposant le comportement GB.

## 3. PPU, tuiles, attributs et palettes
`ppu_direct.h` fournit les accès directs au PPU, `vram_queue.h` les mises à jour par NMI, `tilemap` / `nametable_asset` gèrent les tables et les ressources, `attribute` actualise les attributs et `palette` gère les palettes. Séparez le chargement initial du travail effectué à chaque image.

Les palettes d'arrière-plan et de sprites occupent chacune un groupe de 16 octets. Leurs valeurs sont des codes de couleur NES, pas des composantes RGB. Les attributs sélectionnent les couleurs par groupes de tuiles ; modifier la palette apparente d'une seule tuile peut donc affecter ses voisines.

Certaines déclarations de `ppu.h` ne correspondent pas aux noms d'implémentation de `ppu.c`. Les entrées marquées **déclaration seule** n'ont aucune implémentation retrouvée dans le périmètre collecté et ne sont pas appelées directement dans les exemples débutants. Les exercices exécutables utilisent les fonctions intrinsèques vérifiées. Une déclaration ne prouve pas, à elle seule, qu'une fonction est terminée et peut être liée au programme.

## 4. OAM, métasprites et partage de l'affichage
La NES accepte jusqu'à 64 sprites, normalement huit par ligne de balayage. Neuf ennemis ou projectiles sur la même ligne ne peuvent pas tous apparaître en même temps. Les métasprites assemblent plusieurs OBJ en une image ; vérifiez les limites d'allocation et le format des terminateurs.

`oam_fair.h` et `oam_fair_impl.h` font tourner l'ordre des candidats tout en conservant les priorités. Ils permettent de privilégier le joueur ou l'interface et de faire alterner les objets moins importants. Réordonner l'OAM ne change pas la limite matérielle par ligne.

## 5. Commandes, répétition et périphériques
`input.c` convertit les valeurs brutes des boutons NES en masques `BTN_*` de style GB. **Le bouton A brut NES vaut 0x01 ; BTN_A de la bibliothèque vaut 0x10.** Ne transmettez pas directement BTN_A à l'option `--pad1` de KUROSAKI.

`pad` lit les commandes de base ; `input_repeat` gère la répétition d'un bouton maintenu. `zapper`, `keyboard`, `rob`, `mic` et `midi` exposent des interfaces de périphériques de bas niveau. Lire zéro sur un périphérique absent ne prouve pas son bon fonctionnement : vérifiez ses conditions de connexion.

## 6. Son
Après `nes_apu_init`, utilisez `nes_sfx_square1`, `nes_sfx_square2`, `nes_sfx_triangle` ou `nes_sfx_noise` pour les canaux intégrés. Un argument de période désigne la période du temporisateur matériel, pas une fréquence en hertz. `fc_sound.c` est un exemple minimal de son à onde rectangulaire.

Les échantillons DMC imposent des contraintes d'adresse, de longueur, d'alignement et de cadence. Examinez leur placement avant de fournir un pointeur. Le DMA DMC peut aussi être à l'origine d'interférences possibles avec la lecture des manettes ; associez des lectures adaptées aux diagnostics de KUROSAKI.

VRC6 ajoute des canaux rectangulaires et en dents de scie, VRC7 expose des registres FM et FDS fournit un son à table d'ondes. Choisissez un mapper correspondant et enregistrez le résultat. Ces API sont distinctes du pilote GB `Audio_*`.

## 7. Scènes, acteurs et entités
`actor` et `entity` stockent les objets du jeu dans des tableaux fixes ; `scene` conserve l'état des scènes. Détectez l'épuisement de capacité et cessez d'utiliser les identifiants des objets détruits. Certaines API FC enregistrent actuellement des rappels sans les appeler. Dans les programmes débutants, appelez explicitement les fonctions de mise à jour propres à chaque état depuis la boucle principale.

`chain` conserve l'historique des coordonnées ; `collision` teste le contact entre des formes telles que des rectangles. Un ordre cohérent déplacement, collision, dessin évite de prendre les décisions de collision avec une image de retard.

## 8. Mathématiques et physique
`fixed.h` fournit le calcul Q8.8, `math_fast` / `math_fixed` des opérations numériques, et `math_lut` des calculs par tables. Le fichier actuel `physics2d.h` fournit des **types et constantes Q5.3**, pas une implémentation de fonctions d'intégration ou de macros de mise à jour. Ce n'est pas l'API physique GB de mondes et de corps.

Les fractions Q5.3 représentent des huitièmes de pixel. Conservez séparément les coordonnées entières, les parties fractionnaires, la vitesse et la direction, puis effectuez les additions et le traitement des retenues dans le code du jeu. `fc_subpixel.c` ajoute huit fois 2/8 de pixel, passant du pixel 40 au pixel 42. Ne réutilisez pas telle quelle la représentation Q8.8 de valeur 256 en Q5.3.

## 9. Ressources, mappers et FDS
`bank` et `asset` décrivent les banques PRG et les ressources. L'effet d'une opération de `mapper.h` dépend du mapper choisi à la compilation. Concevez la configuration, l'activation, l'acquittement et la désactivation de l'interruption de défilement comme une séquence cohérente.

Les services FDS sont répartis entre `fds_file`, `fds_overlay`, `fds_save` et `fds_sound`. Charger un overlay remplace du code à une adresse existante : surveillez les adresses de retour et la durée de validité des données. Ne supposez pas le comportement habituel des appels lointains d'une cartouche.

## 10. Référence et exemples
Le dictionnaire ci-dessous suit les en-têtes publics et distingue fonctions, macros de type fonction et alias. Les en-têtes complets exposent aussi des structures et des constantes. Les API déclarées sans implémentation, les rappels seulement conservés et les interfaces de périphériques spécialisés sont distingués des opérations ordinaires vérifiées. Les commentaires source sont conservés tels quels pour permettre une comparaison exacte avec l'implémentation.

`vram_get_queue_capacity()` renvoie la capacité totale du tampon de commandes, soit 128 octets. `vram_get_queue_free()` renvoie les octets restants : la capacité totale moins `vram_get_queue_used()`. Il s'agit des octets des commandes encodées, métadonnées comprises, pas de l'espace disponible en VRAM matérielle. L'écriture d'une tuile nécessite 4 octets, un remplissage 5 et une copie par pointeur 6. Vérifiez l'espace avant de valider la file ; la NMI peut consommer une file validée de manière asynchrone.
