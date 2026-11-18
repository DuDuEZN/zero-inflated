# Présentation de la statistique descriptive des ventes journalières de Fum_Fer

*Section destinée au chapitre « Analyse descriptive des données » du mémoire.*

---

## 1. Cadre de l'étude et construction de la population

La base d'analyse porte sur les ventes journalières du produit **Fum_Fer** (fer folique,
comprimés) enregistrées par l'officine entre le **20 janvier 2022 et le 31 janvier 2026**.
La plage calendaire couvre **1 473 jours**, mais la base ne contient que **1 316 lignes** :
les **157 jours restants** — essentiellement les **dimanches sans garde** — ont été
retirés en amont, à la source, conformément au choix méthodologique arrêté à la suite
de la première relecture du mémoire. La population étudiée n'est donc pas « tous les
jours », mais **« les jours d'ouverture (ou de garde) de l'officine »** : chaque zéro
observé correspond à un jour où l'officine était ouverte, en garde ou en activité,
**sans enregistrer aucune vente de Fum_Fer**. C'est cette définition de la population
d'exposition qui donne leur sens aux zéros : ils ne sont plus des « jours fermés »
(zéros d'artefact administratif), mais des **journées commerciales sans vente**.

On rappelle que ce filtrage exclut du champ d'étude l'effet propre des fermetures
dominicales ; 53 dimanches subsistent dans la base, tous en **jour de garde**.
Aucune **valeur manquante** n'affecte la variable cible : aucune imputation n'est
nécessaire.

---

## 2. Indicateurs de position, de dispersion et de forme (Fum_Fer)

**Tableau 1 — Résumé numérique de Y = nombre d'unités de Fum_Fer vendues par jour
(n = 1 316).**

| Statistique | Valeur |
|---|---:|
| Minimum | 0 |
| Q1 (1er quartile) | 0 |
| Médiane | 1 |
| Moyenne | **1,807** |
| Q3 | 3 |
| Maximum | 24 |
| Variance (échantillon) | **6,335** |
| Écart-type | 2,517 |
| Coefficient de variation | **1,393** |
| Asymétrie (skewness) | 2,311 |
| Kurtosis (non centrée) | 11,83 |
| Proportion de zéros | **44,7 %** |

**Commentaire.** Trois enseignements structurent toute la suite. Premièrement, la
**variance (6,335) est près de trois fois et demie supérieure à la moyenne (1,807)** :
le rapport variance/moyenne (**VMR = 3,51**) signe une **surdispersion très marquée**,
de nature à invalider la loi de Poisson. Deuxièmement, le **coefficient de variation
de 1,39** dénote une dispersion relative importante pour des ventes journalières :
l'activité n'est ni régulière ni prévisible par sa seule moyenne. Troisièmement, la
**distribution est fortement asymétrique à droite** (skewness 2,31) et
**leptokurtique** (kurtosis 11,8) : la masse est concentrée sur les petites valeurs
(médiane à 1, Q1 à 0, 73,1 % des jours à 2 unités ou moins) alors qu'une queue longue
s'étire jusqu'à 24 unités, valeur quasi inaccessible sous une Poisson de même moyenne
(P(Y ≥ 24 | μ = 1,81) ≈ 10⁻¹⁸). Le **mode est 0** et **près d'un jour d'ouverture sur
deux (44,7 %) se solde par aucune vente**.

C'est le croisement de ces deux anomalies — surdispersion **et** surreprésentation du
zéro — qui motive le recours aux modèles de comptage à inflation de zéros.

---

## 3. Distribution empirique et écart à la loi de Poisson

**Tableau 2 — Effectifs et fréquences observés, fréquences attendues sous
Poisson(μ = 1,807).**

| k | Effectif | Fréquence obs. | Poisson attendue | Cumul obs. |
|---:|---:|---:|---:|---:|
| 0 | 588 | 0,4468 | 0,1641 | 0,4468 |
| 1 | 184 | 0,1398 | 0,2966 | 0,5866 |
| 2 | 190 | 0,1444 | 0,2680 | 0,7310 |
| 3 | 111 | 0,0843 | 0,1614 | 0,8153 |
| 4 | 74 | 0,0562 | 0,0729 | 0,8716 |
| 5 | 56 | 0,0426 | 0,0264 | 0,9141 |
| 6 | 43 | 0,0327 | 0,0079 | 0,9468 |
| 7 | 15 | 0,0114 | 0,0020 | 0,9582 |
| 8 | 26 | 0,0198 | 0,0005 | 0,9780 |
| 9 | 8 | 0,0061 | 0,0001 | 0,9840 |
| 10 | 8 | 0,0061 | < 0,0001 | 0,9901 |
| 11–14 | 11 | 0,0084 | ≈ 0 | 0,9985 |
| ≥ 19 | 2 | 0,0015 | ≈ 0 | 1,0000 |

Le contraste est frappant sur la modalité 0 : **588 jours observés sans vente contre
≈ 216 attendus** sous une Poisson de même moyenne, soit un ratio **observé/attendu
≈ 2,73**. Sur la queue, le phénomène s'inverse : la Poisson sous-estime massivement
toutes les modalités au-delà de 4 (à k = 6, par exemple, 43 observés contre ≈ 10
attendus). La distribution empirique n'est donc ni simplement « décalée vers 0 » ni
simplement « plus dispersée » — elle est les deux à la fois, signature classique d'un
**mélange de populations hétérogènes** : des journées ordinaires relativement
productives coexistent avec des journées quasi blanches (dimanches de garde, vacances),
ce que les modèles de mélange (ZIP/ZINB) et les modèles à barrière (hurdle)
traduisent directement.

**Figure 1** (`C_distribution_et_serie.png`) : histogramme superposé à la loi de
Poisson de même moyenne, et série temporelle avec moyenne mobile centrée sur 30 jours.
La moyenne mobile ne révèle **aucune tendance de fond marquée** sur la période, mais
des fluctuations de niveau d'année en année, qu'il conviendra de garder à l'esprit
avant de postuler la stationnarité.

---

## 4. Structure calendaire (jour de la semaine, mois)

**Tableau 3 — Ventes par jour de la semaine.**

| Jour | n | Zéros | Part de zéros | Moyenne |
|---|---:|---:|---:|---:|
| Lundi | 210 | 73 | 34,8 % | 2,314 |
| Mardi | 210 | 85 | 40,5 % | 2,119 |
| Mercredi | 210 | 92 | 43,8 % | 1,857 |
| Jeudi | 211 | 96 | 45,5 % | 1,711 |
| Vendredi | 211 | 95 | 45,0 % | 1,550 |
| Samedi | 211 | 102 | 48,3 % | 1,521 |
| **Dimanche (garde)** | 53 | **45** | **84,9 %** | **0,906** |

**Commentaire.** Le profil hebdomadaire est net et monotone du lundi au samedi :
l'activité décroît graduellement de **2,31 unités le lundi à 1,52 le samedi**, tandis
que la part de journées blanches grimpe de 34,8 % à 48,3 %. Ce décalage est cohérent
avec un comportement d'achat de début de semaine (ravitaillement après le week-end,
renouvellement des ordonnances) et devra être contrôlé explicitement dans la composante
de comptage (le dimanche servant de modalité de référence). **Le dimanche de garde —
53 observations seulement — est de loin la journée la plus atypique : 84,9 % de ces
dimanches se soldent par zéro vente** et la moyenne n'y atteint que 0,91, soit à peu
près la moitié de la moyenne globale. Ce n'est pas « un jour comme les autres » :
c'est précisément le profil d'une **journée quasi structurellement blanche**, que la
modélisation zéro-inflatée accueillera dans l'équation logit via la variable
indicateur `dimanche`.

Au total, la base recense **371 jours de garde** (53 dimanches + 318 jours de garde
ouvrés) et **380 jours de vacances** ; la répartition saisonnière s'établit à
446 jours de grande saison sèche, 378 de grande saison des pluies, 270 et 222 pour
les petites saisons (pluies puis sèche).

**Figure 2** (`D_calendrier.png`) : à gauche, la part de zéros par jour de semaine
contre la moyenne globale ; à droite, le profil mensuel de la moyenne journalière,
qui fait apparaître des variations saisonnières modérées sans rupture de tendance.

---

## 5. Organisation du point de vente et saison climatique

**Tableau 4 — Zéros et moyenne par modalité d'organisation.**

| Variable | Modalité | n | Part de zéros | Moyenne |
|---|---|---:|---:|---:|
| Vacance | 0 | 936 | 44,8 % | 1,799 |
| Vacance | 1 | 380 | 44,5 % | 1,826 |
| Jour_De_Garde | 0 | 945 | 44,3 % | 1,804 |
| Jour_De_Garde | 1 | 371 | 45,6 % | 1,814 |
| Saison | grande_saison_pluies | 378 | 40,7 % | **2,066** |
| Saison | grande_saison_seche | 446 | 44,6 % | 1,767 |
| Saison | petite_saison_pluies | 270 | 48,9 % | 1,615 |
| Saison | petite_saison_seche | 222 | 46,4 % | 1,680 |

**Commentaire.** C'est un résultat important, contre-intuitif au premier regard :
**en moyenne brute, ni les vacances ni le statut de jour de garde ne modulent
visiblement les zéros ni la moyenne** (44,5 % contre 44,8 % de zéros ; 1,83 contre
1,80 de moyenne). Cette « absence d'effet apparent » **n'est pas en contradiction**
avec l'analyse économétrique : elle est brouillée par (i) la construction de la base —
les dimanches sans garde sont déjà exclus, si bien que la comparaison se joue sur des
sous-populations non équilibrées — et (ii) un **biais d'agrégation temporelle** : dans
le fichier d'origine, la variable `Vacance` est codée sur une base hebdomadaire
(la même valeur est répétée sur les 7 jours de la semaine), ce qui dilue la relation
brute entre le marqueur et la vente du jour exact. L'effet propre des jours de garde
et des vacances devra donc être estimé **en régression, à jour de semaine et saison
fixés**, et non par des moyennes conditionnelles simples.

En revanche, l'effet de la **saison climatique est perceptible** : la grande saison
des pluies est la plus dynamique (2,07 unités/jour ; 40,7 % de zéros), les deux
petites saisons, les plus calmes (1,62 et 1,68). Cet ordre reste à confirmer par la
modélisation multivariée — la saison peut capter un effet de saisonnalité plus
général (flux de patients, approvisionnements).

**Figure 3** (`F_meteo_saison.png`, panneau gauche) : boîtes à moustaches de Y par
saison (valeurs extrêmes masquées), mettant en évidence la médiane plus élevée de la
grande saison des pluies et la queue haute commune à toutes les saisons.

---

## 6. Météo et corrélations avec les ventes

**Tableau 5 — Résumé des variables climatiques (n = 1 316).**

| Variable | min | Q1 | Médiane | Moyenne | Q3 | max | Variance |
|---|---:|---:|---:|---:|---:|---:|---:|
| Précipitation journalière (mm) | 0,0 | 0,5 | 1,6 | 3,75 | 4,5 | 61,1 | 36,28 |
| Température journalière (°C) | 24,1 | 26,2 | 27,5 | 27,24 | 28,3 | 30,1 | 1,67 |

**Tableau 6 — Corrélations brutes avec Y.**

| Variable | Pearson r | p (Pearson) | Spearman rs | p (Spearman) |
|---|---:|---:|---:|---:|
| Température | 0,036 | 0,190 | 0,032 | 0,242 |
| Précipitation | 0,009 | 0,748 | 0,008 | 0,772 |

**Commentaire.** Les deux corrélations brutes sont **statistiquement non
significatives au seuil de 5 %** et surtout **d'une ampleur négligeable**
(r ≈ 0,01–0,04) : aucune covariation linéaire ou monotone n'apparaît entre le climat
du jour et la vente de Fum_Fer. Ce résultat descriptif ne préjuge pas d'un effet en
régression (une relation potentiellement non linéaire, retardée ou masquée par la
structure saisonnière), mais il amène à **ne pas attendre un pouvoir explicatif
majeur de la météo** dans la composante de comptage, et justifie de la conserver
comme variable de contrôle plutôt que comme déterminant du modèle.

**Figure 3** (`F_meteo_saison.png`, panneau droit) : nuage de points
Température/Y, visuellement plat, en cohérence avec r = 0,04.

---

## 7. Dynamique annuelle et intermittence

**Tableau 7 — Statistiques par année calendaire (2026 : 28 jours seulement, janvier).**

| Année | n jours | Moyenne | Variance | Part de zéros | VMR |
|---|---:|---:|---:|---:|---:|
| 2022 | 309 | 1,877 | 6,050 | 44,7 % | 3,22 |
| 2023 | 326 | 1,960 | 8,783 | 45,7 % | 4,48 |
| 2024 | 327 | 1,609 | 4,595 | 46,8 % | 2,86 |
| 2025 | 326 | 1,819 | 6,087 | 41,1 % | 3,35 |
| 2026 | 28 | 1,429 | 4,106 | 50,0 % | 2,87 |

**Commentaire.** La surdispersion n'est **pas l'artefact d'une année particulière** :
le VMR reste compris entre 2,9 et 4,5 chaque année — y compris sur le court extrait de
janvier 2026 — ce qui indique un **trait structurel** de la distribution et non l'effet
d'années exceptionnelles. La moyenne annuelle oscille entre 1,61 et 1,96 sans tendance
franche : le processus de vente est **approximativement stationnaire en niveau**, ce
qui rend légitime le découpage temporel train/test 80/20 (coupure au 12 avril 2025)
utilisé pour l'évaluation prédictive hors échantillon.

L'analyse des **séquences de zéros consécutifs** complète ce constat : **314
séquences** de journées blanches, de longueur moyenne 1,87 jours ; **62 séquences
d'au moins 3 jours consécutifs, 19 d'au moins 5 jours et 7 d'au moins 7 jours**, avec
un **maximum de 8 jours d'affilée sans vente**. Ces plages longues de zéros traduisent
des **épisodes d'inactivité prolongés** (périodes de vacances typiquement) plutôt que
des ruptures isolées ; elles confortent la nécessité de modèles capables de rendre
compte à la fois du zéro ponctuel et des plages de zéros engendrées par
l'organisation de l'activité.

---

## 8. Synthèse descriptive — vers la modélisation

Trois messages se dégagent de ce portrait descriptif et encadrent la stratégie de
modélisation :

1. **La distribution de Fum_Fer n'est pas une Poisson** : VMR = 3,51, 44,7 % de zéros
   contre 16,4 % attendus, queue lourde (maximum = 24). Toute modélisation devra
   absorber à la fois la surdispersion et l'excès de zéros.
2. **Les zéros ne sont pas tous de même nature** : les dimanches de garde (84,9 % de
   zéros) — et a fortiori les dimanches fermés, déjà exclus de la base — relèvent de
   la quasi-certitude administrative ; les zéros des jours ouvrés (35–48 %) relèvent
   d'une variabilité plutôt « commerciale ». La distinction zéro structurel / zéro
   d'échantillonnage justifie une approche en **mélange** (ZIP/ZINB) ou à **deux
   composantes** (hurdle), à confronter systématiquement à la binomiale négative.
3. **Les variables calendaires dominent ; la météo et la saison jouent un rôle de
   contrôle modeste** : l'effet du jour de la semaine est fort et monotone, tandis que
   la garde et les vacances ne se départagent pas en moyenne brute — leur effet propre
   devra être identifié en régression, toutes choses égales par ailleurs.

Ces régularités conditionnent directement le dispositif de la partie inférentielle :
l'équation de comptage inclura le jour de semaine (dimanche en référence), la garde,
les vacances, la saison et la météo ; l'équation d'inflation testera explicitement le
rôle structurel des dimanches de garde.

---

*Chiffres produits par `analyse_descriptive.py` (sortie `sortie_descriptive.txt`,
tableaux et figures dans `figures_descriptives/`).*
