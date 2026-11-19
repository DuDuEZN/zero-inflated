# Tableaux d'effets des six modeles — Fum_Fer (echantillon d'entrainement, n = 1 052)

*Conventions : exp(coef) = rapport de taux (IRR) pour la composante de comptage ; odds ratio (OR) pour 
la composante logit. Modalites de reference : dimanche (jour de semaine), grande saison des pluies (saison). 
IC95 a 1,96 ecarts-types ; test de Wald bilaterale. Les coefficients de comptage ne sont PAS comparables 
entre modeles (normalisation differente) ; seules les lois predites P(Y=k) le sont.*



## 1. Poisson

### Composante de comptage (exp(coef) = IRR)

| variable                    |    coef |   exp(coef) |   IC95_inf |   IC95_sup |   p_value |
|:----------------------------|--------:|------------:|-----------:|-----------:|----------:|
| const                       |  0.2345 |      1.2642 |     0.2611 |     6.1207 |    0.7708 |
| Precipitation_Journaliere   | -0.0082 |      0.9918 |     0.9825 |     1.0012 |    0.0866 |
| Temperature_Journaliere     | -0.0077 |      0.9923 |     0.9392 |     1.0484 |    0.7831 |
| Jour_De_Garde               |  0.0965 |      1.1013 |     0.9936 |     1.2208 |    0.0662 |
| Vacance                     |  0.118  |      1.1253 |     1.0015 |     1.2643 |    0.0471 |
| lundi                       |  0.8664 |      2.3783 |     1.7134 |     3.3012 |    0      |
| mardi                       |  0.8333 |      2.3009 |     1.6568 |     3.1953 |    0      |
| mercredi                    |  0.72   |      2.0544 |     1.4763 |     2.8588 |    0      |
| jeudi                       |  0.6261 |      1.8703 |     1.3417 |     2.6071 |    0.0002 |
| vendredi                    |  0.5168 |      1.6767 |     1.2004 |     2.342  |    0.0024 |
| samedi                      |  0.4631 |      1.589  |     1.1359 |     2.2229 |    0.0069 |
| saison_grande_saison_seche  | -0.117  |      0.8896 |     0.7897 |     1.0022 |    0.0543 |
| saison_petite_saison_pluies | -0.2814 |      0.7547 |     0.6492 |     0.8774 |    0.0003 |
| saison_petite_saison_seche  | -0.1937 |      0.8239 |     0.6876 |     0.9872 |    0.0358 |

**Commentaire (Poisson).** Modele de reference. Le gradient hebdomadaire est tranchant : le lundi se vend 2,38 fois plus d'unites que le dimanche garde (IRR = 2,38 ; IC95 [1,71 ; 3,30]), decroissant jusqu'au samedi (IRR = 1,59). La petite saison des pluies est significativement plus faible (IRR = 0,75 ; p = 0,0003). L'effet « Vacance » est significatif et de signe **positif** (IRR = 1,13 ; p = 0,047) : effet mal identifie d'une variable codee par semaine, qui se neutralise dans les modeles a deux composantes. **Ce modele est disqualifie theoriquement (dispersion de Pearson 3,63 ; 476 zeros observes contre 185 attendus) ; ses effets ne sont rapportes qu'a titre de reference.**


## 2. Binomial Negatif

### Composante de comptage (exp(coef) = IRR)

| variable                    |    coef |   exp(coef) |   IC95_inf |   IC95_sup |   p_value |
|:----------------------------|--------:|------------:|-----------:|-----------:|----------:|
| const                       | -0.1201 |      0.8868 |     0.0345 |    22.7826 |    0.9422 |
| Precipitation_Journaliere   | -0.0076 |      0.9924 |     0.9742 |     1.0109 |    0.42   |
| Temperature_Journaliere     |  0.0063 |      1.0063 |     0.8985 |     1.1271 |    0.9129 |
| Jour_De_Garde               |  0.1042 |      1.1098 |     0.9011 |     1.3669 |    0.3271 |
| Vacance                     |  0.1308 |      1.1398 |     0.8993 |     1.4447 |    0.2793 |
| lundi                       |  0.8076 |      2.2425 |     1.2874 |     3.9063 |    0.0043 |
| mardi                       |  0.7763 |      2.1734 |     1.2469 |     3.7884 |    0.0062 |
| mercredi                    |  0.6691 |      1.9525 |     1.1188 |     3.4074 |    0.0185 |
| jeudi                       |  0.5893 |      1.8028 |     1.0304 |     3.1543 |    0.0389 |
| vendredi                    |  0.4742 |      1.6068 |     0.9199 |     2.8067 |    0.0956 |
| samedi                      |  0.4089 |      1.5051 |     0.8613 |     2.6302 |    0.1511 |
| saison_grande_saison_seche  | -0.1163 |      0.8902 |     0.7019 |     1.1291 |    0.3376 |
| saison_petite_saison_pluies | -0.2293 |      0.7951 |     0.5961 |     1.0607 |    0.1189 |
| saison_petite_saison_seche  | -0.1864 |      0.83   |     0.5731 |     1.2019 |    0.3239 |

**Commentaire (Binomiale Negative).** Le gradient hebdomadaire subsiste (lundi IRR = 2,24 ; jeudi IRR = 1,80 ; p < 0,04) mais s'attenue — la surdispersion est desormais absorbee par le parametre alpha. Les variables d'organisation (garde, vacances, saisons) deviennent toutes non significatives, et vendredi/samedi perdent le seuil de 5 % (p = 0,096 et 0,151) : la variance par jour etant plus grande sous NB, la precision diminue. A retenir comme modele de « surdispersion pure » : il decrit bien le niveau des ventes, mais ne distingue pas les zeros structurels des zeros d'echantillonnage.


## 3. ZIP

### Composante de comptage (exp(coef) = IRR)

| variable                    |    coef |   exp(coef) |   IC95_inf |   IC95_sup |   p_value |
|:----------------------------|--------:|------------:|-----------:|-----------:|----------:|
| const                       |  1.9491 |      7.0223 |     1.223  |    40.3213 |    0.0288 |
| Precipitation_Journaliere   | -0.0084 |      0.9916 |     0.9811 |     1.0023 |    0.1228 |
| Temperature_Journaliere     | -0.0016 |      0.9984 |     0.9394 |     1.0611 |    0.9579 |
| Jour_De_Garde               | -0.0011 |      0.9989 |     0.8933 |     1.117  |    0.9849 |
| Vacance                     |  0.0658 |      1.068  |     0.9435 |     1.2089 |    0.2983 |
| lundi                       | -0.5706 |      0.5652 |     0.4051 |     0.7884 |    0.0008 |
| mardi                       | -0.5611 |      0.5706 |     0.4085 |     0.797  |    0.001  |
| mercredi                    | -0.58   |      0.5599 |     0.3996 |     0.7845 |    0.0008 |
| jeudi                       | -0.7112 |      0.4911 |     0.3495 |     0.69   |    0      |
| vendredi                    | -0.8214 |      0.4398 |     0.3126 |     0.6188 |    0      |
| samedi                      | -0.7892 |      0.4542 |     0.3223 |     0.6401 |    0      |
| saison_grande_saison_seche  | -0.1174 |      0.8893 |     0.7828 |     1.0101 |    0.0711 |
| saison_petite_saison_pluies | -0.1508 |      0.86   |     0.731  |     1.0118 |    0.069  |
| saison_petite_saison_seche  | -0.1719 |      0.8421 |     0.6926 |     1.0239 |    0.0848 |

**Commentaire (ZIP).** Ne pas s'alarmer de l'**inversion de signe** des jours de semaine par rapport au Poisson : le lundi affiche IRR = 0,565 dans la composante de comptage, car une grande partie de l'ecart lundi/dimanche est desormais transferee dans l'equation logit (les coefficients de comptage ne sont pas comparables d'un modele a l'autre ; seules les lois predites P(Y=k) le sont). **Equation d'inflation : OR du dimanche = 8,97 (IC95 [3,81 ; 21,16] ; p < 10^-4)** — les dimanches de garde multiplient par 9 le risque de jour « blanc ». Garde ouvrée (OR = 0,75 ; p = 0,074) et vacances (OR = 0,81 ; p = 0,153) non significatives. Lecture : **le zero structurel des donnees est, a lui seul, porte par le dimanche de garde.**


### Composante logit d'inflation (P(exces de zeros), exp(coef) = OR)

| variable      |    coef |   exp(coef) |   IC95_inf |   IC95_sup |   p_value |
|:--------------|--------:|------------:|-----------:|-----------:|----------:|
| const         | -0.246  |      0.7819 |     0.6558 |     0.9323 |    0.0061 |
| Vacance       | -0.2152 |      0.8063 |     0.6002 |     1.0833 |    0.1531 |
| dimanche      |  2.1944 |      8.9743 |     3.8056 |    21.1632 |    0      |
| Jour_De_Garde | -0.2881 |      0.7497 |     0.5468 |     1.0278 |    0.0735 |


## 4. ZINB

### Composante de comptage (exp(coef) = IRR)

| variable                    |    coef |   exp(coef) |   IC95_inf |   IC95_sup |   p_value |
|:----------------------------|--------:|------------:|-----------:|-----------:|----------:|
| const                       |  1.9708 |      7.1767 |     0.4249 |   121.218  |    0.1718 |
| Precipitation_Journaliere   | -0.0104 |      0.9897 |     0.9741 |     1.0055 |    0.1991 |
| Temperature_Journaliere     | -0.0029 |      0.9971 |     0.9052 |     1.0984 |    0.9535 |
| Jour_De_Garde               | -0.0044 |      0.9956 |     0.8258 |     1.2003 |    0.9628 |
| Vacance                     |  0.068  |      1.0703 |     0.8717 |     1.3142 |    0.5162 |
| lundi                       | -0.6603 |      0.5167 |     0.2661 |     1.0035 |    0.0512 |
| mardi                       | -0.6675 |      0.513  |     0.2635 |     0.9986 |    0.0495 |
| mercredi                    | -0.7173 |      0.4881 |     0.2499 |     0.9532 |    0.0357 |
| jeudi                       | -0.8395 |      0.4319 |     0.2208 |     0.8448 |    0.0142 |
| vendredi                    | -0.9552 |      0.3848 |     0.1972 |     0.7508 |    0.0051 |
| samedi                      | -0.969  |      0.3795 |     0.194  |     0.7421 |    0.0046 |
| saison_grande_saison_seche  | -0.1153 |      0.8911 |     0.729  |     1.0893 |    0.2606 |
| saison_petite_saison_pluies | -0.2279 |      0.7962 |     0.6201 |     1.0224 |    0.0741 |
| saison_petite_saison_seche  | -0.1927 |      0.8248 |     0.6044 |     1.1256 |    0.2246 |

**Commentaire (ZINB — modele retenu, AIC minimum).** **Composante logit : dimanche OR = 14,45 (IC95 [5,53 ; 37,77] ; p ≈ 5x10^-8)** — en parallele des 84,9 % de dimanches de garde sans vente observes dans le descriptif. Les autres variables d'inflation ne sont pas significatives (garde ouvrée OR = 0,67 ; p = 0,115 ; vacances OR = 0,78 ; p = 0,260). **Composante de comptage conditionnelle aux jours « non blancs »** : gradient hebdomadaire descendant du lundi (IRR = 0,52 ; p = 0,051) au samedi (IRR = 0,38 ; p = 0,005) — conditionnellement a ce que la journee vende, les jours ouvres vendent environ la moitie du niveau d'un dimanche de garde actif, traduction d'un effet de ravitaillement dominical. Meteo et saisons sans effet significatif — hierarchie des variables calendaires confirmee par la statistique descriptive.


### Composante logit d'inflation (P(exces de zeros), exp(coef) = OR)

| variable      |    coef |   exp(coef) |   IC95_inf |   IC95_sup |   p_value |
|:--------------|--------:|------------:|-----------:|-----------:|----------:|
| const         | -0.677  |      0.5082 |     0.3758 |     0.6872 |    0      |
| Vacance       | -0.2475 |      0.7808 |     0.5073 |     1.2015 |    0.2605 |
| dimanche      |  2.671  |     14.455  |     5.5315 |    37.7745 |    0      |
| Jour_De_Garde | -0.399  |      0.671  |     0.4085 |     1.1022 |    0.1151 |


## 5. Hurdle Poisson

### Composante de comptage (exp(coef) = IRR)

| variable                    |    coef |   exp(coef) |   IC95_inf |   IC95_sup |   p_value |
|:----------------------------|--------:|------------:|-----------:|-----------:|----------:|
| const                       |  1.9885 |      7.3049 |     1.2722 |    41.9434 |    0.0257 |
| Precipitation_Journaliere   | -0.0079 |      0.9922 |     0.9816 |     1.0029 |    0.1507 |
| Temperature_Journaliere     | -0.0031 |      0.9969 |     0.938  |     1.0595 |    0.9209 |
| Jour_De_Garde               | -0.006  |      0.994  |     0.8883 |     1.1123 |    0.9163 |
| Vacance                     |  0.0663 |      1.0685 |     0.9428 |     1.211  |    0.2994 |
| lundi                       | -0.581  |      0.5593 |     0.4006 |     0.781  |    0.0006 |
| mardi                       | -0.566  |      0.5678 |     0.4063 |     0.7936 |    0.0009 |
| mercredi                    | -0.581  |      0.5593 |     0.3992 |     0.7838 |    0.0007 |
| jeudi                       | -0.7124 |      0.4905 |     0.3489 |     0.6896 |    0      |
| vendredi                    | -0.8262 |      0.4377 |     0.3106 |     0.6168 |    0      |
| samedi                      | -0.7698 |      0.4631 |     0.3286 |     0.6526 |    0      |
| saison_grande_saison_seche  | -0.1176 |      0.889  |     0.7818 |     1.011  |    0.0729 |
| saison_petite_saison_pluies | -0.1339 |      0.8747 |     0.7437 |     1.0287 |    0.1056 |
| saison_petite_saison_seche  | -0.1701 |      0.8435 |     0.693  |     1.0267 |    0.0897 |

**Commentaire (Hurdle Poisson).** Deux mecanismes separes. **Barriere (logit, P(Y>0))** : lundi OR = 10,71 (IC95 [4,35 ; 26,38]) vs dimanche — la probabilite d'au moins une vente est 10 fois superieure un lundi qu'un dimanche de garde, decroissant jusqu'au samedi (OR = 6,11) ; hierarchie tres significative (tous p < 0,0002). **Comptage tronque a zero (jours avec vente)** : les jours ouvres affichent des intensites conditionnelles inferieures a la reference dominicale (IRR 0,44-0,56 ; p < 0,001) — c'est le propre du Hurdle : il separe la question « vendre ou pas ? » (dominee par le calendrier) de la question « combien ? » (dominee par les achats de debut de semaine sur les jours qui vendent).


### Composante logit de barriere (P(Y>0), exp(coef) = OR)

| variable                    |    coef |   exp(coef) |   IC95_inf |   IC95_sup |   p_value |
|:----------------------------|--------:|------------:|-----------:|-----------:|----------:|
| const                       | -1.8228 |      0.1616 |     0.0019 |    13.5636 |    0.42   |
| Precipitation_Journaliere   | -0.0062 |      0.9939 |     0.9701 |     1.0182 |    0.6183 |
| Temperature_Journaliere     |  0.0001 |      1.0001 |     0.8564 |     1.1678 |    0.9993 |
| Jour_De_Garde               |  0.2741 |      1.3154 |     0.9805 |     1.7646 |    0.0674 |
| Vacance                     |  0.1593 |      1.1727 |     0.8354 |     1.6463 |    0.3572 |
| lundi                       |  2.3714 |     10.7128 |     4.3512 |    26.3755 |    0      |
| mardi                       |  2.2445 |      9.4356 |     3.8397 |    23.187  |    0      |
| mercredi                    |  2.0221 |      7.554  |     3.0808 |    18.5219 |    0      |
| jeudi                       |  2.056  |      7.8149 |     3.1875 |    19.1597 |    0      |
| vendredi                    |  2.0281 |      7.5998 |     3.1    |    18.631  |    0      |
| samedi                      |  1.8096 |      6.1082 |     2.493  |    14.9659 |    0.0001 |
| saison_grande_saison_seche  | -0.0494 |      0.9518 |     0.6767 |     1.3389 |    0.7768 |
| saison_petite_saison_pluies | -0.345  |      0.7082 |     0.4747 |     1.0565 |    0.0909 |
| saison_petite_saison_seche  | -0.095  |      0.9094 |     0.5456 |     1.5159 |    0.7156 |


## 6. Hurdle NB

### Composante de comptage (exp(coef) = IRR)

| variable                    |    coef |   exp(coef) |   IC95_inf |   IC95_sup |   p_value |
|:----------------------------|--------:|------------:|-----------:|-----------:|----------:|
| const                       |  2.1672 |      8.7339 |     0.4419 |   172.623  |    0.1546 |
| Precipitation_Journaliere   | -0.0105 |      0.9896 |     0.9724 |     1.007  |    0.2408 |
| Temperature_Journaliere     | -0.009  |      0.991  |     0.8945 |     1.098  |    0.8629 |
| Jour_De_Garde               | -0.0121 |      0.988  |     0.8216 |     1.1879 |    0.8974 |
| Vacance                     |  0.0723 |      1.0749 |     0.8725 |     1.3244 |    0.4973 |
| lundi                       | -0.7185 |      0.4875 |     0.2504 |     0.949  |    0.0345 |
| mardi                       | -0.6977 |      0.4977 |     0.2552 |     0.9706 |    0.0406 |
| mercredi                    | -0.7134 |      0.49   |     0.2507 |     0.9579 |    0.037  |
| jeudi                       | -0.857  |      0.4244 |     0.2164 |     0.8323 |    0.0126 |
| vendredi                    | -0.9901 |      0.3715 |     0.1894 |     0.7288 |    0.004  |
| samedi                      | -0.9317 |      0.3939 |     0.2005 |     0.774  |    0.0069 |
| saison_grande_saison_seche  | -0.1326 |      0.8758 |     0.7091 |     1.0818 |    0.2186 |
| saison_petite_saison_pluies | -0.1806 |      0.8348 |     0.6388 |     1.0909 |    0.1859 |
| saison_petite_saison_seche  | -0.2101 |      0.8105 |     0.5807 |     1.1314 |    0.217  |

**Commentaire (Hurdle NB).** Barriere identique au Hurdle Poisson (lundi OR = 10,71 ; tous p < 0,0002) mais intensite conditionnelle plus lisible encore : lundi 0,49 (IC95 [0,25 ; 0,95] ; p = 0,034), mardi 0,50, mercredi 0,49, jeudi 0,42, vendredi 0,37, samedi 0,39 — **les jours ouvres, lorsqu'ils vendent, vendent a peu pres la moitie du niveau d'un dimanche de garde actif**. Ce resultat, coherent avec le ZINB, appuie un comportement de rattrapage le lundi (apres les jours de fermeture) et des commandes plus volumineuses en garde — l'image inverse (et apparente) du Poisson simple, qui melange les deux mecanismes.


### Composante logit de barriere (P(Y>0), exp(coef) = OR)

| variable                    |    coef |   exp(coef) |   IC95_inf |   IC95_sup |   p_value |
|:----------------------------|--------:|------------:|-----------:|-----------:|----------:|
| const                       | -1.8228 |      0.1616 |     0.0019 |    13.5636 |    0.42   |
| Precipitation_Journaliere   | -0.0062 |      0.9939 |     0.9701 |     1.0182 |    0.6183 |
| Temperature_Journaliere     |  0.0001 |      1.0001 |     0.8564 |     1.1678 |    0.9993 |
| Jour_De_Garde               |  0.2741 |      1.3154 |     0.9805 |     1.7646 |    0.0674 |
| Vacance                     |  0.1593 |      1.1727 |     0.8354 |     1.6463 |    0.3572 |
| lundi                       |  2.3714 |     10.7128 |     4.3512 |    26.3755 |    0      |
| mardi                       |  2.2445 |      9.4356 |     3.8397 |    23.187  |    0      |
| mercredi                    |  2.0221 |      7.554  |     3.0808 |    18.5219 |    0      |
| jeudi                       |  2.056  |      7.8149 |     3.1875 |    19.1597 |    0      |
| vendredi                    |  2.0281 |      7.5998 |     3.1    |    18.631  |    0      |
| samedi                      |  1.8096 |      6.1082 |     2.493  |    14.9659 |    0.0001 |
| saison_grande_saison_seche  | -0.0494 |      0.9518 |     0.6767 |     1.3389 |    0.7768 |
| saison_petite_saison_pluies | -0.345  |      0.7082 |     0.4747 |     1.0565 |    0.0909 |
| saison_petite_saison_seche  | -0.095  |      0.9094 |     0.5456 |     1.5159 |    0.7156 |
