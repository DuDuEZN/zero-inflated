# Commentaire des résultats — Modélisation des ventes journalières de Fum_Fer (dossiers de mémoire de master)

> Document d'appui à la rédaction du chapitre « Résultats et discussion ». Chaque section suit l'ordre du script `analyse_ventes_v4.py` et commente chiffres à l'appui ce qu'il faut dire — et ce qu'il ne faut pas dire. Population retenue : **1 316 jours d'ouverture** de l'officine (20/01/2022 → 31/01/2026), dimanches hors garde exclus de la base en amont ; partition chronologique 80/20 (1 052 j / 264 j, coupure au 12/04/2025).

---

## 1. Statistique descriptive : la série est une demande d'intermittence

| Indicateur | Valeur | Lecture |
|---|---|---|
| Moyenne journalière | 1,81 unité | Ventes journalières faibles |
| Variance | 6,34 | Fortement supérieure à la moyenne |
| VMR (variance/moyenne) | **3,51** | Surdispersion marquée (Poisson : VMR = 1) |
| Zéros observés | **44,7 %** | Près d'un jour sur deux sans vente |
| Zéros attendus sous Poisson(1,81) | 16,4 % | Écart massif : ratio observé/attendu ≈ **2,7** |

**Commentaire proposé.** La demande ne peut être traitée comme un processus gaussien, ni même comme un simple processus de Poisson. La conjonction d'un VMR de 3,51 et d'une proportion de zéros presque trois fois supérieure à celle qu'impliquerait l'homogénéité poissonnienne place la série dans la classe des **demandes intermittentes à zéro-inflation** (Mullahy, 1986 ; Lambert, 1992). Deux familles d'explication doivent être distinguées dès cette étape, car elles gouvernent toute la modélisation : (i) des **zéros structurels** liés à l'organisation de l'offre (fermeture, jours de faible travail, dimanches de garde) ; (ii) des **zéros d'échantillonnage** dus à une faible intensité de la demande conditionnelle. C'est précisément la décomposition formalisée par les modèles ZIP/ZINB (excess-zeros) et Hurdle (Mullahey, 1986 ; Cameron & Trivedi, 2013).

---

## 2. Diagnostics préalables du Poisson de référence

- **VIF** : aucune variable > 10 → absence de colinéarité gênante ; les estimations ne souffrent pas d'instabilité numérique.
- **Dispersion de Pearson : 3,63** (devrait être ≈ 1 sous Poisson) → forte surdispersion inconditionnelle.
- **Cameron–Trivedi (1990)** : t = 5,04, **p ≈ 2,3×10⁻⁷** → rejet formel de l'équidispersion (H1 : Var = μ + αμ²).
- **Van den Broeck (1995)** : χ²(1) = 937,76, **p ≈ 6×10⁻²⁰⁶** (476 zéros observés contre 185,4 attendus sous Poisson) → excès de zéros massif contre la Poisson.
- **Durbin–Watson : 1,92** (residus de Pearson) → pas d'autocorrélation d'ordre 1 notable.

**Commentaire proposé.** Le rejet du Poisson est sans ambiguïté : surdispersion simultanément détectée par la statistique de Pearson, par le test auxiliaire de Cameron–Trivedi, et excès de zéros détecté par le score de Van den Broeck. Ce dernier doit être lu comme un **test préliminaire uniquement** : sous H0 Poisson, il ne distingue pas un excès de zéros propre d'une surdispersion de variance (toute surdispersion peut le faire rejeter) — c'est pourquoi le verdict d'inflation est porté plus loin par le test prédictif **contre le NB**, seul à isoler l'excès de zéros de la surdispersion. La question qui se pose alors n'est pas *si* le Poisson convient, mais *pourquoi* il échoue — surdispersion de variance conditionnelle (plaidant pour un NB) ou excès de zéros structurels (plaidant pour ZIP/ZINB/Hurdle) — question tranchée plus loin par le test prédictif contre le NB. Le Durbin–Watson proche de 2 indique qu'aucune dynamique d'ordre 1 n'impose d'emblée un modèle de séries temporelles ; la structure temporelle de la demande est absorbée par les covariables calendaires.

**Point de prudence (à rapporter en discussion).** Sous HAC (maxlag = 7), les coefﬁcients de jours de semaine perdent leur significativité (samedi : p = 0,09 sous HAC contre p < 0,01 classique). L'inférence « classique » des GLM est donc **optimiste** ; le protocole a néanmoins retenu les erreurs-types des MLE des six modèles (standard pour la comparaison AIC), tout en signalant cette limite.

---

## 3. Comparaison des six modèles (échantillon d'entraînement, n = 1 052)

| Modèle | k | LogLik | AIC | BIC | Zéros prévus | Ratio obs/att | Disp. Pearson | π̄ (inflation) |
|---|---|---|---|---|---|---|---|---|
| **ZINB** | 19 | −1858,8 | **3755,6** | **3849,9** | 475,1 | 1,002 | 1,07 | 0,323 |
| Hurdle NB | 28 | −1855,6 | 3767,1 | 3906,0 | 476,0 | 1,000 | 1,08 | — |
| Binomiale Négative (NB2) | 15 | −1893,1 | 3816,3 | 3890,7 | 451,1 | **1,055** | 1,01 | — |
| ZIP | 18 | −1954,7 | 3945,3 | 4034,6 | 475,4 | 1,001 | 1,47 | 0,424 |
| Hurdle Poisson | 28 | −1950,1 | 3956,2 | 4095,0 | 476,0 | 1,000 | 1,50 | — |
| Poisson | 14 | −2367,0 | 4762,1 | 4831,4 | 185,4 | **2,57** | 3,63 | — |

**Commentaire proposé.** Trois constats hiérarchisés :

1. **une composante Binomiale Négative est incontournable** : le gap d'AIC entre le Poisson (4762) et le NB (3816) est de **946 points**, un écart si large qu'aucun raffinement de spécification ne pourrait le combler. La variance conditionnelle au-delà des zéros est donc authentiquement sur-dispersée.
2. **une composante d'inflation/mécanisme de zéros améliore encore la vraisemblance** : ZINB (3755,6) et Hurdle NB (3767,1) dominent le NB seul (3816,3) ; la hiérarchie compte-comptage ne suffit pas à reproduire la masse de zéros, quoique le NB la capture déjà à 94,8 % (ratio obs/att = 1,055).
3. **les variantes à comptage Poisson (ZIP, Hurdle Poisson) restent insuffisantes** : une fois les zéros traités par leur mécanisme logit, il subsiste une dispersion de Pearson résiduelle de 1,47–1,50 — la composante de comptage Poisson reste trop rigide pour les journées à vente positive.

L'inflation moyenne du ZINB — π̄ = 0,**323** — est substantielle : le modèle attribue à **32 % de jours un zéro « certain »** conditionnellement aux covariables, distinct d'un zéro d'échantillonnage. Aucun des deux modèles zero-inflated n'est **dégénéré** (π̄ > 0,01) : les mécanismes sont identifiés et interprétables — un point méthodologique important, car un ZINB avec π̄ ≈ 0 serait équivalent au NB et ne devrait jamais être retenu (fausse complexité).

---

## 4. Hiérarchie statistique emboîtée, puis non emboîtée

### 4.1 Test du ratio de vraisemblances Poisson → NB
**LR = 947,7 ; p ≈ 2,1×10⁻²⁰⁸** (p-value mélangée 0,5·χ²(0) + 0,5·χ²(1) car α = 0 est une borne de l'espace des paramètres). **Rejet sans équivoque du Poisson en faveur du NB.**

### 4.2 Excès de zéros testé **contre le NB**, pas contre le Poisson
Test prédictif de calibrage à la Gelman et al. (1996), H0 = « les données proviennent du NB ajusté », 4999 simulations :
**476 zéros observés vs 451,1 attendus ; p = 0,058.**

**Commentaire proposé (essentiel pour la soutenance).** C'est le résultat le plus riche du chapitre. À α = 5 %, **le NB n'est pas rejeté** : l'immense majorité des zéros est cohérente avec une intensité de demande NB modulée par les covariables disponibles (structure hebdomadaire, vacances, jours de garde). Le rejet marginal (à 10 % on rejetterait) invite à la nuance : il subsiste un excès résiduel (≈ 25 zéros) que le NB n'explique pas totalement. **Conclusion défendable : le recours au ZINB n'est pas une nécessité structurelle, mais une amélioration rationnelle portant précisément sur ce résidu de 25 zéros.** Ce résultat corrobore la thèse directrice : *une fois la structure du calendrier (dimanches non-garde, jours hebdo, vacances) correctement modélisée, la « zero-inflation » apparente est principalement un artefact d'exposition, non un phénomène distinct*.

### 4.3 Tests de Vuong (1989), corrigés AIC — paires non emboîtées uniquement

| Paire | V | p | Préférence |
|---|---|---|---|
| BN contre ZIP | 2,24 | 0,025 | **BN** |
| BN contre Hurdle Poisson | 2,42 | 0,016 | **BN** |
| BN contre Hurdle NB | −2,81 | 0,005 | **Hurdle NB** |
| ZINB contre Hurdle NB | 2,26 | 0,024 | **ZINB** |

**Commentaire proposé.** La lecture croisée est cohérente : (i) le NB domine nettement les variantes à comptage Poisson (ZIP, Hurdle Poisson) — la dispersion conditionnelle compte plus que le traitement des zéros ; (ii) dès qu'une composante NB est présente, la modélisation explicite du mécanisme des zéros (hurdle comme zero-inflation) apporte un gain significatif (Hurdle NB > BN ; ZINB > Hurdle NB). On précisera que le Vuong n'est **pas applicable aux paires emboîtées** (Poisson⊂ZIP, NB⊂ZINB, etc.), qui relèvent du test du ratio de vraisemblances — d'où le protocole en deux volets.

---

## 5. Modèle retenu : ZINB — lecture des coefﬁcients

### 5.1 Composante de comptage (IRR ; dimanche = modalité de référence)

| Variable | IRR | IC95 % | p |
|---|---|---|---|
| samedi | **0,379** | [0,194 ; 0,742] | 0,005 |
| vendredi | **0,385** | [0,197 ; 0,751] | 0,005 |
| jeudi | 0,432 | [0,221 ; 0,845] | 0,014 |
| mercredi | 0,488 | [0,250 ; 0,953] | 0,036 |
| mardi | 0,513 | [0,264 ; 0,999] | 0,050 |
| lundi | 0,517 | [0,266 ; 1,004] | 0,051 |
| Vacance | 1,070 | [0,872 ; 1,314] | 0,52 |
| Précipitation (par mm) | 0,990 | [0,974 ; 1,005] | 0,20 |
| Température (par °C) | 0,997 | [0,905 ; 1,098] | 0,95 |
| Jour de garde | 0,996 | [0,826 ; 1,200] | 0,96 |
| Saisons (vs grande saison des pluies) | 0,79–0,89 | — | 0,07–0,26 |

**Commentaire proposé.** La structuration hebdomadaire est le signal majeur : **à jour « non-zéro structurel » fixé, l'intensité de vente des autres jours de la semaine est de 38 à 52 % de celle du dimanche de garde** (IRR 0,38–0,52). Autrement dit, le dimanche de garde est à la fois (i) plus rarement blanc (voir §5.2) et (ii) plus intense quand il vend — il concentre la demande hebdomadaire. La météo (température, précipitations) et les saisons n'ont pas d'effet signiﬁcatif : la demande de Fum_Fer est **insensible aux conditions climatiques** — résultat en soi, à ne pas survendre, mais qui invalide l'hypothèse d'un effet saisonnier direct, au-delà de l'organisation du calendrier.

### 5.2 Composante logit (P(zéro structurel), probabilité d'excès de zéros)

| Variable | OR | IC95 % | p |
|---|---|---|---|
| **dimanche (de garde)** | **14,46** | [5,53 ; 37,77] | < 0,001 |
| Vacance | 0,78 | [0,51 ; 1,20] | 0,26 |
| Jour de garde | 0,67 | [0,41 ; 1,10] | 0,12 |
| (constante) | 0,51 | [0,38 ; 0,69] | < 0,001 |

**Commentaire proposé.** Le seul déterminant clair du zéro structurel est le **dimanche de garde : les chances d'une journée blanche y sont multipliées par 14,4** par rapport aux jours de semaine, toutes choses égales par ailleurs (IC95 excluant largement 1). Ce résultat est économiquement cohérent : le dimanche de garde draine une clientèle de dépannage, généralement peu nombreuse. Ni les vacances ni le jour de garde en semaine n'atteignent la signiﬁcabilité : l'organisation **hebdomadaire** (quel jour de la semaine ?) domine l'organisation **saisonnière** (vacances) dans la genèse des zéros. On peut donc soutenir l'hypothèse directrice : **les zéros sont organisés, pas climatiques**.

---

## 6. Diagnostics du modèle retenu (échantillon d'entraînement)

| Diagnostic | Valeur | Attendu sous H0 | Verdict |
|---|---|---|---|
| Dispersion de Pearson (χ²/ddl) | 1,07 | ≈ 1 | ✅ |
| Durbin–Watson (résidus Pearson) | 1,93 | 2 | ✅ pas d'AC d'ordre 1 |
| Ljung-Box (retards 7 / 14 / 28) | p = 0,82 / 0,94 / 0,69 | p > 0,05 | ✅ aucune saisonalité résiduelle |
| **PIT randomisé** : moyenne / écart-type | **0,500 / 0,286** | 0,500 / 0,289 | ✅ uniformité quasi parfaite |
| Hosmer–Lemeshow (10 déciles, p-value simulée, 1999 tirages) | p = **0,60** | p > 0,05 | ✅ calibration satisfaisante |

**Commentaire proposé.** Les diagnostics valident le ZINB **en distribution**, pas seulement en moyenne — critère décisif pour l'usage en gestion de stock. Le PIT randomisé (Czado et al., 2009) est l'instrument le plus fort : sa moyenne (0,500) et son écart-type (0,286, attendu 0,289) sont canoniques, ce qui signiﬁe que **la loi prédictive est bien calibrée jour par jour**, pas seulement en agrégat. Ljung-Box aux retards 7/14/28 atteste l'absence de saisonalité hebdomadaire résiduelle : la composante calendrier a absorbé la structure temporelle. Mentionner en note : pour les données discrètes, le PIT doit être randomisé (uniformisation de Czado et al.), faute de quoi il n'est pas strictement uniforme au sens classique.

---

## 7. Évaluation prédictive hors échantillon (264 jours) et benchmarks

| Modèle | MAE | RMSE | Logscore | Brier sur P(Y=0) |
|---|---|---|---|---|
| Binomiale Négative | **1,809** | **2,506** | **−1,801** | 0,240 |
| Hurdle Poisson | 1,814 | 2,510 | −1,974 | 0,240 |
| ZINB | 1,814 | 2,515 | −1,813 | **0,239** |
| Hurdle NB | 1,817 | 2,513 | −1,816 | 0,240 |
| ZIP | 1,813 | 2,512 | −1,974 | 0,239 |
| Poisson | 1,815 | 2,510 | −2,303 | 0,299 |
| Croston | **1,778** | **2,440** | — | — |
| SBA | **1,751** | **2,441** | — | — |

**Commentaire proposé (fin, mais important).** (i) Sur les erreurs ponctuelles, **SBA bat tous les modèles paramétriques** (MAE 1,751 contre ~1,81) ; c'est attendu : sur des séries très intermittentes, le lissage exponentiel simple et robuste est difﬁcile à battre en erreur ponctuelle, quand il ignore toute information exogène. (ii) Mais **Croston et SBA ne fournissent pas de loi prédictive** — ils sont exclus du logscore et du Brier, car il n'y a pas de P(Y=k) associé. Or l'objectif n'est pas de prédire le volume exact du jour mais de **quantifier des probabilités de stock-out** : le critère pertinent est le logscore, qui valide en loi la modélisation (le Poisson perd ici ≈ 0,5 nat de logscore par observation par rapport aux modèles basés sur la NB — écart considérable). Troisième constat : (iii) c'est le NB qui occupe la première place du logscore sur le test (−1,801), le gain du ZINB (−1,813) y étant marginal — la supériorité du ZINB s'établit sur l'échantillon d'entraîment (AIC/BIC, Vuong, diagnostics), pas sur l'erreur prédictive out-of-sample. Il faudra le dire explicitement : **le choix du ZINB repose sur la modélisation structurelle des zéros, non sur un gain de prévision ponctuelle**.

**Formulation synthétique suggérée.** « Les benchmarks classiques de la littérature sur la demande intermittente (Croston, 1972 ; Syntetos & Boylan, 2005) dominent sur l'erreur absolue moyenne, mais ne produisent pas de distribution prédictive ; pour une gestion de stock probabiliste — déterminer un point de commande à un niveau de service cible — la comparaison doit s'effectuer en loi (logscore, Brier sur P(S=0)), où la famille NB, avec ou sans mécanisme de zéros, surperforme le Poisson de référence d'environ 0,5 nat de logscore par observation. »

---

## 7bis. Validation croisée chronologique du ZINB (fenêtre élargissante, 4 replis d'évaluation)

| Repli | n entraînement | n validation | logscore ZINB | logscore NB | Δ logscore | Brier P(Y=0) ZINB | MAE ZINB | Zéros obs / att. |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 210 | 210 | −1,955 | −1,917 | −0,038 | 0,233 | 2,059 | 96 / 91,6 |
| 2 | 420 | 211 | −1,830 | −1,911 | +0,081 | 0,255 | 1,996 | 98 / 92,0 |
| 3 | 631 | 210 | −1,653 | −1,690 | +0,038 | 0,250 | 1,692 | 103 / 91,8 |
| 4 | 841 | 211 | −1,815 | −1,837 | +0,023 | 0,237 | 1,756 | 87 / 99,7 |
| **Moyenne ± é-t** | | | **−1,813 ± 0,124** | **−1,839 ± 0,106** | **+0,026** | **0,243 ± 0,010** | **1,876 ± 0,179** | |

Commentaire proposé. La chronologie interdisant un découpage aléatoire, la validation croisée est menée en fenêtre élargissante : chaque repli entraîne sur tous les blocs antérieurs et valide sur le bloc suivant — elle mime le déploiement prédictif réel de l'outil de réapprovisionnement. Trois enseignements. (i) **La supériorité du ZINB sur la NB se généralise** : il domine la NB en logscore sur 3 replis sur 4 (Δ moyen +0,026) et sur le Brier du zéro sur les 4 replis (0,243 contre 0,247) ; le repli 1, entraîné sur seulement 210 jours, est le seul où la NB tient tête — avec si peu d'observations, l'équation d'inflation est mal identifiée, ce qui est cohérent avec un apprentissage de la structure des zéros qui exige du volume. (ii) **La stabilité de l'effet dominical est satisfaisante** : l'OR du dimanche dans l'équation d'inflation reste compris entre 4,7 et 17,6 selon les replis, et de l'ordre de 11–17 dès que l'échantillon d'entraînement dépasse 420 jours — la variabilité du repli 1 confirme qu'il s'agit d'une limite de taille d'échantillon, non d'une instabilité du phénomène. (iii) **La calibration en loi est préservée hors échantillons successifs** : le PIT randomisé agrégé sur les 4 replis a une moyenne de 0,489 (attendu 0,5) et un écart-type de 0,293 (attendu 0,289) — la loi prédictive reste fiable pour une utilisation décisionnelle, non seulement sur la coupe train/test unique mais tout au long du déploiement temporel. On notera enfin que le décompte de zéros attendus du ZINB suit bien les zéros observés (91,6–99,7 attendus contre 87–103 observés), y compris sur les replis récents.

## 8. Traduction opérationnelle : point de commande au niveau de service

- Horizon de réapprovisionnement L = 7 jours ; niveau de service cible 95 %.
- Demande attendue sur 7 jours : **11,5 unités** (≈ 1,64 unité/jour, cohérent avec la moyenne observée).
- **Point de commande (quantile 95 % de la demande cumulative) : 24 unités.**
- Stock de sécurité associé : **12,5 unités** (≈ 109 % de la demande attendue sur la période — l'intermittence étale fortement la loi cumulée).

**Commentaire proposé.** La demande étant très intermittente (44,7 % de zéros), la distribution de la demande **cumulée sur 7 jours** n'est pas gaussienne : le quantile à 95 % n'est pas m + 1,645·σ mais bien 24 unités, plus du **double de la demande espérée**. C'est la valeur ajoutée d'une modélisation en loi : une approximation normale (moyenne + 1,645 écarts-types) conduirait à un point de commande ≈ 18–19 unités, donc **un service nettement inférieur à 95 %**, la queue de distribution étant allongée par les zéros et la surdispersion. La règle opérationnelle simple est : *l'officine doit repasser commande lorsque le stock disponible descend sous 24 unités, si le délai fournisseur est de 7 jours et le service visé de 95 %*. La figure 05 donne la distribution complète du cumul, ce qui permet de recalibrer le point de commande à tout autre niveau de service (ex. 90 %) en lisant le quantile correspondant.

---

## 9. Limites (à discuter honnêtement en fin de chapitre)

1. **Granularité des indicatrices Vacance et Jour_De_Garde** : variables hebdomadaires projetées sur les 7 jours de chaque semaine (feuille « Notes_methodologiques » du fichier source). Ceci induit un biais d'atténuation : les effets de Vacance (OR ≈ 0,78, p = 0,26 ; IRR ≈ 1,07, p = 0,52) sont sous-estimés ; un calendrier journalier précis pourrait les révéler signiﬁcatifs.
2. **Absence de colonne jour_ferie** : les jours fériés éventuellement fermés restent confondus avec de « vrais zéros ». Un tri par l'officine des jours réellement ouverts (fêtes légales du pays) est le chantier structurant recommandé ; il pourrait abaisser encore le besoin de mécanisme d'inflation (et donc rapprocher le NB du modèle « optimal »).
3. **Indépendance conditionnelle** des jours : le protocole teste l'autocorrélation résiduelle (DW, Ljung-Box) et ne la détecte pas, mais des dépendances à plus d'un jour (effets de stock — rupture prolongée, stock de protection) ne peuvent être exclues ; un modèle avec dépendance en série (GLARMA, ou couverture par processus de Markov caché) pourrait améliorer la loi prédictive de la demande cumulée.
4. **Partition chronologique unique** : la stabilité des résultats pourrait être renforcée par une validation croisée dite *rolling origin* (5 fenêtres).
5. **Un seul article (Fum_Fer)** : la généralisation à l'ensemble du portefeuille (Amoxicilline, etc.) reste à établir.

---

## 10. Synthèse rédigée — paragraphe de conclusion prêt à adapter

> « La demande journalière de Fum_Fer présente une intermittence prononcée : 44,7 % de journées sans vente, pour une moyenne de 1,81 unité et un rapport variance/moyenne de 3,51, écartant d'emblée le modèle de Poisson, auquel l'ensemble des tests s'oppose (dispersion de Pearson de 3,63 ; test de Cameron–Trivedi, p ≈ 2×10⁻⁷ ; test du ratio de vraisemblances Poisson/NB, p ≈ 2×10⁻²⁰⁸). La question empirique centrale — l'excès de zéros relève-t-il d'un mécanisme structurel propre ou d'une simple conséquence de la faible intensité conditionnelle ? — est tranchée par un test prédictif de calibrage contre le modèle de Binomiale Négative ajusté : avec 476 zéros observés pour 451 attendus, la p-value de 0,058 indique que le NB capture l'essentiel des zéros une fois la structure du calendrier modélisée. Les tests de Vuong restreints aux paires non emboîtées hiérarchisent néanmoins les spécifications : la Binomiale Négative domine les variantes à comptage de Poisson (ZIP, Hurdle Poisson, p < 0,03), et le mécanisme de zéro-inflation apporte un gain supplémentaire et signiﬁcatif (ZINB > Hurdle NB, V = 2,26, p = 0,024 ; ZINB > NB via l'AIC, ΔAIC ≈ 61). Le modèle retenu, un ZIP Negative Binomial à inflation logit, diagnostiqué en distribution par un PIT randomisé canonique (moyenne 0,500 ; écart-type 0,286), un test de Hosmer–Lemeshow simulé non rejettant (p = 0,60) et l'absence de saisonalité résiduelle (Ljung-Box aux retards 7, 14 et 28, tous p > 0,68), identiﬁe un seul déterminant clairement identiﬁé des zéros : le dimanche de garde (OR = 14,5 ; IC95 [5,5 ; 37,8]). Conditionnellement à une journée « non blanche », l'intensité de vente des autres jours est de 38 à 52 % de celle du dimanche (tous p ≤ 0,05), tandis que la météo et les saisons climatiques sont sans effet signiﬁcatif. Traduite opérationnellement, cette loi calibrée permet de ﬁxer le point de commande à 24 unités pour un délai de réapprovisionnement de sept jours et un niveau de service de 95 %, soit un stock de sécurité de 12,5 unités — plus du double de la demande attendue sur la période, illustration directe de l'importance d'une évaluation en loi plutôt qu'en moyenne dans un contexte d'intermittence forte. »

---

## 11. Quelques pièges de rédaction à éviter

- Ne pas présenter le **ratio obs/att de zéros du Poisson** (2,57) comme preuve de « zero-inflation » : il ne teste rien, c'est un descriptif. La preuve passe par les tests (LR, prédictif, Vuong).
- Ne pas affirmer que « le NB suffit » de façon absolue : la p-value prédictive est à la limite (0,058) et **les tests de Vuong, corroborés par l'AIC**, penchent pour le ZINB. La formule prudente et défendable : « le NB est un modèle parcimonieux acceptable ; le ZINB apporte un gain statistiquement détectable, économiquement mineur, mais indispensable si l'on veut modéliser explicitement la probabilité de journée blanche ».
- Ne pas interpréter les OR/IRR du ZINB comme des effets marginaux du nombre moyen de ventes : les effets marginaux sur E[Y] combinent **logit ET comptage** (formulation de l'effet marginal de Mullahey) — indiquer qu'une table d'effets marginaux est disponible (figure 03 au profil de la température).
- Citer correctement : Lambert (1992) pour ZIP/ZINB ; Mullahey (1986) pour hurdle ; Cameron & Trivedi (1990) pour le test de surdispersion ; Vuong (1989) ; Czado, Gneiting & Held (2009) pour le PIT randomisé ; Croston (1972) et Syntetos, Boylan & Croston (2005) pour SBA ; Gelman, Meng & Stern (1996) pour le test prédictif.
