## 1. Utiliser la bibliothèque
La bibliothèque rassemble des sources C réutilisables qui s'appuient sur les fonctions intrinsèques `__` de KITAQGB. Elle couvre aussi bien l'affichage que la physique, la 3D et la communication.

{{CODE:0}}

{{CODE:1}}

Chaque entrée d'API indique sa déclaration, son en-tête, son implémentation et un exemple d'utilisation. Lorsqu'aucun exemple n'existait, un fragment montrant le passage des arguments a été ajouté. L'appelant doit fournir les tampons et les objets employés par ces fragments. Pour des exemples directement compilables en ROM, consultez la section des programmes complets.

## 2. Construire une image de jeu
`system_init` initialise la gestion des images. `system_wait_vblank` attend puis incrémente le compteur logiciel d'images. Sur GB, le rappel VBlank est appelé de manière coopérative par cette fonction d'attente ; son enregistrement n'installe pas de gestionnaire d'interruption matérielle.

1. Actualisez les commandes une fois.
2. Calculez les déplacements, les collisions et l'état du jeu.
3. Préparez les commandes de dessin et l'OAM.
4. Appliquez les mises à jour pendant VBlank.
5. Faites avancer la musique selon le pilote choisi.

Combiner des opérations d'attente comme `vram_flush` et `sprite_flush_oam` peut faire attendre deux images pour une seule mise à jour du jeu. Après avoir effectué l'attente vous-même, une opération `_now` correspondante peut convenir, à condition d'en garantir les contraintes temporelles.

## 3. Commandes et répétition
`input_down(mask)` teste un bouton maintenu, `input_pressed(mask)` un nouvel appui, `input_released(mask)` un relâchement, et `input_repeat(mask)` assure une répétition adaptée aux menus. Ces états sont actualisés par `input_update()`. Répéter cet appel dans une même image peut effacer l'événement de nouvel appui.

| Boutons | Masques |
| --- | --- |
| Droite, gauche, haut, bas | 0x01 / 0x02 / 0x04 / 0x08 |
| A, B, SELECT, START | 0x10 / 0x20 / 0x40 / 0x80 |

L'exemple `gb_input.c` compte les appuis sur A. Vérifiez que maintenir A n'incrémente pas le compteur en continu, puis remplacez `input_pressed` par `input_down` pour observer la différence.

## 4. Arrière-plans, texte et VRAM
`vram_queue_bg_tile` met une tuile en file, `vram_queue_bg_rect` un rectangle et `vram_queue_bg_block` le transfert d'un tableau. Vérifiez les valeurs de retour et `vram_get_overflowed()` pour détecter un dépassement de capacité. Si une opération conserve un pointeur source, ses données doivent rester inchangées, sa mémoire valide et sa banque accessible jusqu'à la fin du transfert.

`text.c` et `menu.c` implémentent les services de texte, de choix et de fenêtres déclarés dans `rpg.h`. Faites correspondre la conversion texte-vers-tuile à la police chargée en VRAM. Elle n'est pas nécessairement identique à celle de la fonction pédagogique `m_text` de ce manuel.

## 5. Sprites et animation
Commencez par `sprite_init`, `sprite_alloc`, `sprite_set_tile` et `sprite_set_pos`. La GB autorise 40 sprites au total et 10 par ligne de balayage : tenez compte de leur concentration horizontale, pas seulement de leur nombre. `sprite_warn_scanline_overflow` et `sprite_max_scanline_count` permettent d'examiner une disposition.

`MetaSpritePart` décrit le placement relatif des OBJ. `SpriteAnim` décrit les tuiles d'animation et leurs intervalles de mise à jour. Faites correspondre les éléments dessinés par `metasprite_draw` aux emplacements OBJ alloués. Le A de `gb_sprite.c` montre comment employer une tuile de caractère comme sprite.

## 6. Couleur, défilement, effets raster et caméras
Les composantes RGB de `cgb_bg_rgb` et `cgb_obj_rgb` vont de 0 à 31, et non de 0 à 255. `CGB_RGB15` les regroupe dans une valeur sur 16 bits. Les fonctions de palette CGB de haut niveau sont conçues pour ne rien faire sur DMG.

`Scroll_SetBg` positionne l'arrière-plan, `Scroll_SetWindow` la fenêtre, et le module caméra calcule la vue à partir des coordonnées du monde. Distinguez les unités en virgule fixe de la caméra des pixels entiers à l'écran.

`raster.c` construit des tables de défilement par bandes et des déformations horizontales ligne par ligne. Les opérations `Scroll_SplitCommit` utilisent les vecteurs VBlank/STAT. Ne laissez pas des gestionnaires de musique et de défilement s'approprier indépendamment le même vecteur ; prévoyez au besoin un répartiteur commun.

## 7. Musique et effets sonores
Compilez `audio_hwregs_gb.c`, puis `audio.c`, puis le source du jeu. Ne dupliquez pas les définitions des registres NR10 à NR52 si le jeu les fournit déjà. Après `Audio_Init`, appelez normalement `Audio_Update` une fois par image.

`Audio_PlayMusic(bank,song)` indique explicitement la banque de la musique. `Audio_PlaySFXBanked` joue un effet depuis une autre banque. Les priorités départagent les effets qui partagent des canaux physiques. La GB possède quatre canaux sonores physiques : CH1, CH2, CH3 et CH4.

Les commandes de flux musical `AUDIO_CMD_NOTE` et `AUDIO_CMD_SET_INST` conservent un ordre historique : **0=CH1, 1=CH2, 2=CH4, 3=CH3**. Ne le confondez pas avec les constantes de canaux de l'API ordinaire. L'en-tête définit actuellement `AUDIO_NOTE_MAX=67`.

Le flux d'effet CH1 de base lit une paire note/volume par image et se termine sur la note 0. CH3 utilise un marqueur et un format différents. Consultez `gb_sound.c`. Les fondus progressent pendant `Audio_Update` ; arrêter les mises à jour arrête aussi le fondu.

## 8. Musique par interruption VBlank
`audio_vblank.c` utilise son propre format de lecture. Les enregistrements temporisés contiennent cinq octets : `delay, ch2_note, ch1_note, ch3_note, ch4_noise_param`. Le pilote lit des morceaux directement accessibles ou consomme une file en WRAM. La bibliothèque publique ne fournit pas de fonction pour alimenter cette file : le jeu doit assurer cette production et coordonner les écritures avec la routine d’interruption. `LOOP` n’est reconnu que dans les flux directs, et `IMMEDIATE` uniquement en mode file. Les flux ordinaires d’`audio.c` doivent donc être convertis.

{{CODE:2}}

Le correctif place le vecteur VBlank à 0x0040 et actualise la somme de contrôle. Appliquez-le uniquement à une ROM prévue pour ce pilote. Vérifiez les interactions avec les gestionnaires VBlank personnalisés et le défilement fractionné. Une compilation réussie ne prouve pas que la musique est audible : enregistrez-la avec KOKURA et vérifiez que le morceau avance.

## 9. Virgule fixe, physique et 3D
Dans le format Q8.8 de `fixed.h`, 256 représente 1,0 et 128 représente 0,5. L'exemple `gb_fixed.c` présente `fix_from_int`, `fix_mul` et `fix_to_int`. Définissez les plages de valeurs avant les calculs afin d'éviter les débordements.

`physics2d` traite les rectangles, `physics2d_circle` les cercles et `physics3d` les AABB tridimensionnelles. Préparez et initialisez les tableaux de monde et de corps, réglez la vitesse ou la gravité, puis faites avancer la simulation. Utilisez des unités cohérentes pour la position et la vitesse par pas ; la bibliothèque ne les convertit pas implicitement en pixels. L’exemple des cercles utilise la position 40 et la vitesse 2. Une masse inverse nulle désigne un corps statique. Consultez les en-têtes pour la représentation des coefficients et les limites des calculs intermédiaires. Attention notamment à l’ancienne fonction `kq2d_body_apply_friction` : elle convertit son coefficient en octet signé, si bien que 128 à 255 deviennent des valeurs négatives, et non des facteurs d’amortissement Q8 non signés. `gb_circle.c` présente un pas complet.

`wire3d_dmg` est une bibliothèque de rendu filaire monochrome pour Game Boy. Compilez `wire3d_dmg_96.c` pour une vue de 128 × 96 ou `wire3d_dmg.c` pour 128 × 120, puis utilisez les fonctions `Wire3DDMG_*`. Les anciens fichiers `wire3d` et `dmg3d` restent des points d’entrée compatibles avec leurs profils respectifs ; n’en compilez qu’un seul. `wire3d_cgb` conserve son nom et reste le moteur couleur distinct. Réservez explicitement la RAM, la VRAM et les zones d’écran propres à chaque moteur. Les deux moteurs monochromes écartent les arêtes qui franchissent les limites de profondeur au lieu de les découper. L’occultation entre objets repose sur les rectangles englobants des faces et cinq points par ligne : c’est une approximation, pas un test de profondeur par pixel. Le rendu CGB utilise la double vitesse et le DMA, et exige `--cgb=cgb_only`.

`Wire3DDMG_BeginFrame` (`WIRE3D_DMG_HEIGHT=96`) efface le tampon de dessin. `Wire3DDMG_BeginFrame` (`WIRE3D_DMG_HEIGHT=120`) ne réinitialise que l’état d’occultation : DMG3D consomme et efface les données lors de leur transfert en VRAM. Le transfert des tuiles modifiées inclut celles de l’image précédente afin d’effacer les anciens pixels. Le transfert auxiliaire partage une partie du tampon principal ; il ne dispose pas d’un tampon indépendant. Adaptez l’ordre des opérations de chaque image au moteur choisi.

Pour les lignes CGB, utilisez les couleurs 1, 2 et 3. Le mode normal de 128 × 96 combine les bits de couleur : la superposition des couleurs 1 et 2 donne la couleur 3. La couleur 0 n'efface pas une ligne. Effacez l'image ou utilisez les fonctions d'effacement prévues à cet effet. En mode normal, `Wire3DCGB_DrawLine2D` et le dessin des modèles ne mémorisent pas la zone à transférer. Pour tracer des lignes en enregistrant cette zone, utilisez `Wire3DCGB_DrawLineClipped2D` ; pour inclure toute la zone de dessin dans le prochain transfert partiel, appelez `Wire3DCGB_InvalidateFrameHistory`.

Le mode de 160 × 144 alloue au maximum 127 tuiles par image. Si le tracé rapide ne peut pas allouer une tuile ou rencontre une coordonnée hors écran, `Wire3DCGB_GetFullScreenOverflow()` renvoie une valeur non nulle et les écritures de pixels sont suspendues jusqu'à l'initialisation de l'image suivante. Gardez les sommets dans la zone sélectionnée. La marge droite du masque triangulaire s'arrête à X=127 en mode 128 × 96 et à X=159 en plein écran. Respectez les exigences de sélection des banques WRAM indiquées pour chaque API, en particulier avec le plein écran ou FastMap.

## 10. Scènes, réserves d'objets et motifs de tirs
`scene` gère des états tels que titre, jeu et pause ; `entity` fournit une réserve d'objets de capacité fixe ; `chain` conserve l'historique des coordonnées d'un serpent, d'un train ou d'une corde. Vérifiez les valeurs d'échec d'allocation, telles que 0xFF, avant d'utiliser le pointeur renvoyé par `entity_get`.

`danmaku` propose des réserves de projectiles en virgule fixe, des tirs directionnels ou en éventail, la détection des impacts et des frôlements. Son rendu CGB par composition de l'arrière-plan évite la limite habituelle du nombre d'OBJ, mais le temps de calcul par image et le débit des transferts restent limités. Mesurez le temps de traitement plutôt que de viser uniquement un grand nombre de projectiles.

## 11. RPG, aventure, stratégie et sauvegarde
`rpg.h` rassemble les déclarations pour les nombres aléatoires, les indicateurs, les quêtes, la compression, le texte, les menus, les scripts, les cartes, les sauvegardes et la recherche de chemin. Les implémentations sont réparties dans des fichiers comme `rng.c`, `flags.c`, `rle.c` et `text.c`. Utilisez le dictionnaire pour sélectionner les unités nécessaires.

Une valeur fixe de `rng_seed` produit une suite reproductible pour les tests. Vérifiez si chaque fonction d'intervalle inclut sa borne supérieure. `flag_get` et `flag_set` manipulent des ensembles de bits. `save.c` utilise un accès à la SRAM de type MBC5 ; faites correspondre la capacité RAM de l'en-tête ROM à la zone de sauvegarde du jeu.

Les services de plateau, de liste de coups autorisés et d'annulation de `slg.h`, ainsi que la recherche de chemin de `slg_path.c`, doivent rester distincts des règles et de l'évaluation propres au jeu. La largeur, la hauteur et les tableaux de travail doivent respecter les limites de la bibliothèque et les exigences de chaque argument.

## 12. Communication
`link.c` fournit les transferts série d'octets ; `link_packet.c` ajoute une couche de paquets facultative. Placez `link_hwregs_gb.c` en premier dans la compilation. Les modes par interrogation et par interruption nécessitent des appels différents ; en mode interruption, le jeu doit raccorder le vecteur 0x0058.

Les opérations logiques `Link4_*` et les opérations `LinkDmg07_*` du périphérique Nintendo DMG-07 sont deux systèmes distincts. Le DMG-07 utilise une horloge externe : appelez fréquemment `LinkDmg07_Poll` et une fois par image `LinkDmg07_TickFrame`. Une seule interrogation par image peut ne pas respecter les délais nécessaires. Avec les tâches pair/dmg07 de KOKURA, testez séparément la connexion, le démarrage, la déconnexion et la reconnexion.

## 13. Banques, ressources et débogage
`BankPtr` associe un numéro de banque à un pointeur. `far_data_read` lit en RAM des ressources situées dans une autre banque. Le module de ressources associe des identifiants à des descripteurs ; le jeu reste responsable de leur durée de validité, de leurs banques et de leurs tailles.

`debug_trace_u8` et `debug_trace_u16` consignent des valeurs en RAM ; `debug_assert_fail` y enregistre un code de diagnostic. Ce ne sont pas des appels `printf` vers une console PC. Examinez ces données grâce aux outils d'observation mémoire de l'émulateur. L'exemple `gb_debug.c` enregistre HP=42.

`vram_get_queue_capacity()` renvoie le nombre total d'emplacements de commande, soit 32 par défaut. `vram_get_queue_free()` renvoie le nombre d'emplacements libres et `vram_get_queue_used()` le nombre d'emplacements occupés. Une opération en file occupe un emplacement, quelle que soit la taille du transfert. Ces fonctions décrivent la file de transfert, pas l'espace inutilisé de la VRAM matérielle.
