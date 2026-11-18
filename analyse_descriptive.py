# -*- coding: utf-8 -*-
"""
Statistique descriptive de la base ventes journalieres (Fum_Fer).
Produit : figures + tableaux consolidés + sortie console pour la rédaction.
Code linéaire, sans fonctions ni classes.
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import skew, kurtosis, poisson as poisson_dist, pearsonr, spearmanr

warnings.filterwarnings("ignore")

FICHIER_DONNEES = "base_donnees_journaliere_corrige.xlsx"
FEUILLE_DONNEES = "Donnees_journalieres"
VARIABLE_CIBLE = "Fum_Fer"
DOSSIER_FIGURES = "figures_descriptives"

os.makedirs(DOSSIER_FIGURES, exist_ok=True)
np.random.seed(42)
sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams["figure.dpi"] = 110

# ---------------------------------------------------------------- chargement
df = pd.read_excel(FICHIER_DONNEES, sheet_name=FEUILLE_DONNEES)
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)
df["Y"] = df[VARIABLE_CIBLE].astype(int)
df["annee"] = df["date"].dt.year
df["mois"] = df["date"].dt.month
df["nom_mois"] = df["date"].dt.strftime("%b")
df["jour_sem"] = df["date"].dt.day_of_week
noms_jours = {0: "Lundi", 1: "Mardi", 2: "Mercredi", 3: "Jeudi",
              4: "Vendredi", 5: "Samedi", 6: "Dimanche (garde)"}
df["lib_sem"] = df["jour_sem"].map(noms_jours)

print("=== A. Cadre de l'etude ===")
print(f"Periode               : {df['date'].min().date()} -> {df['date'].max().date()}")
print(f"Jours couverts        : {(df['date'].max() - df['date'].min()).days + 1}")
print(f"Lignes (jours ouverts): {len(df)}")
print(f" trous (dim. non garde, fermetures) : {(df['date'].max() - df['date'].min()).days + 1 - len(df)}")
print(f"Valeurs manquantes Y  : {int(df[VARIABLE_CIBLE].isna().sum())}")

# ------------------------------------------------- B. synthese numerique Y
print("\n=== B. Fum_Fer : indicateurs de position, dispersion, forme ===")
y = df["Y"]
desc = pd.DataFrame({
    "valeur": [int(y.min()), float(y.quantile(.25)), float(y.median()), float(y.mean()),
               float(y.quantile(.75)), int(y.max()), float(y.var(ddof=1)), float(y.std(ddof=1)),
               float(y.std(ddof=1) / y.mean()), float(skew(y)), float(kurtosis(y, fisher=False)),
               float((y == 0).mean())],
}, index=["min", "Q1", "mediane", "moyenne", "Q3", "max", "variance", "ecart_type",
          "coeff_variation", "asymetrie_pearson", "kurtosis_brev", "proportion_de_zeros"])
print(desc.round(3).to_string())
desc.round(3).to_csv(f"{DOSSIER_FIGURES}/B_indicateurs_y.csv", encoding="utf-8-sig")

# --------------------------------------------- C. distribution et matrice pmf
print("\n=== C. Distribution empirique vs loi de Poisson (moyenne egale) ===")
kmax = int(y.max())
tab_dist = pd.DataFrame({
    "ventes": np.arange(kmax + 1),
    "effectif": [(y == k).sum() for k in range(kmax + 1)],
    "frequence": [(y == k).mean() for k in range(kmax + 1)],
})
tab_dist["poisson_attendue"] = poisson_dist.pmf(tab_dist["ventes"], mu=y.mean())
tab_dist["cumul_obs"] = tab_dist["frequence"].cumsum()
print(tab_dist.round(4).to_string(index=False))
tab_dist.round(4).to_csv(f"{DOSSIER_FIGURES}/C_distribution.csv", index=False,
                         encoding="utf-8-sig")
print(f"Mode(s)            : {sorted(y.mode().tolist())}")
print(f"Cumul k<=2         : {tab_dist['frequence'][:3].sum():.1%} des jours | k >= 2 : {(y >= 2).mean():.1%}")
print(f"Cumul k<=4         : {tab_dist['frequence'][:5].sum():.1%} des jours")

fig, axes = plt.subplots(1, 2, figsize=(15, 5))
sns.histplot(y, discrete=True, stat="probability", ax=axes[0], color="steelblue")
xv = np.arange(0, kmax + 1)
axes[0].plot(xv, tab_dist["poisson_attendue"], "o--", color="red", ms=3,
             label=f"Poisson(moyenne = {y.mean():.2f})")
axes[0].set(title=f"Distribution empirique des ventes journalieres — {VARIABLE_CIBLE}",
            xlabel="Unites vendues", ylabel="Frequence relative")
axes[0].legend()
axes[1].plot(df["date"], y, lw=0.5, color="steelblue", alpha=0.8)
axes[1].plot(df["date"], y.rolling(30, center=True).mean(), color="red", lw=1.8,
             label="Moyenne mobile 30 jours")
axes[1].set(title="Evolution temporelle et tendance (moyenne mobile 30 j)",
            xlabel="Date", ylabel="Unites vendues")
axes[1].legend()
plt.tight_layout()
plt.savefig(f"{DOSSIER_FIGURES}/C_distribution_et_serie.png", bbox_inches="tight")
plt.show()
plt.close()

# ------------------------------------------------------- D. structure calendaire
print("\n=== D. Structure calendaire de la base ===")
g_sem = df.groupby("lib_sem", sort=False).agg(n=("Y", "size"), zeros=("Y", lambda v: (v == 0).sum()),
                                              moyenne=("Y", "mean"))
ordre = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche (garde)"]
g_sem = g_sem.loc[ordre]
g_sem["part_zeros"] = g_sem["zeros"] / g_sem["n"]
print(g_sem.round(3).to_string())
g_sem.round(3).to_csv(f"{DOSSIER_FIGURES}/D_jours_semaine.csv", encoding="utf-8-sig")
print(f"Jours de garde total         : {int(df['Jour_De_Garde'].sum())}")
print(f"Jours de garde hors dimanche : {int(((df['jour_sem'] < 6) & (df['Jour_De_Garde'] == 1)).sum())}")
print(f"Dimanches (tous en garde)    : {int((df['jour_sem'] == 6).sum())}")
print(f"Zeros les dimanches de garde : {int(((df['jour_sem'] == 6) & (y == 0)).sum())} / {int((df['jour_sem'] == 6).sum())}")
print(f"Jours de vacances           : {int(df['Vacance'].sum())}")
print(f"Saison modalites            : {df['Saison_Du_Jour'].value_counts().to_dict()}")

fig, axes = plt.subplots(1, 2, figsize=(15, 5))
sns.barplot(x=g_sem.index, y=g_sem["part_zeros"], ax=axes[0], color="steelblue")
axes[0].axhline((y == 0).mean(), color="red", ls="--", label=f"Moyenne globale ({(y == 0).mean():.0%})")
axes[0].set(title="Part de journées blanches par jour de la semaine",
            xlabel="", ylabel="Proportion de zéros")
axes[0].tick_params(axis="x", rotation=30)
axes[0].legend()
g_mois = df.groupby("mois").agg(moyenne=("Y", "mean"), zeros=("Y", lambda v: (v == 0).mean()))
sns.lineplot(x=g_mois.index, y=g_mois["moyenne"], ax=axes[1], marker="o", color="steelblue")
axes[1].set(title="Moyenne journalière des ventes par mois de l'année",
            xlabel="Mois", ylabel="Ventes moyennes / jour")
axes[1].set_xticks(range(1, 13))
plt.tight_layout()
plt.savefig(f"{DOSSIER_FIGURES}/D_calendrier.png", bbox_inches="tight")
plt.show()
plt.close()

# ----------------------------------------------- E. zéros par variable d'organisation
print("\n=== E. Zéros et moyenne par modalité d'organisation ===")
lignes_e = []
for var in ["Vacance", "Jour_De_Garde"]:
    for mod, gr in df.groupby(var):
        lignes_e.append({"variable": var, "modalite": int(mod), "n": len(gr),
                         "part_zeros": (gr["Y"] == 0).mean(), "moyenne": gr["Y"].mean()})
for mod, gr in df.groupby("Saison_Du_Jour"):
    lignes_e.append({"variable": "Saison_Du_Jour", "modalite": mod, "n": len(gr),
                     "part_zeros": (gr["Y"] == 0).mean(), "moyenne": gr["Y"].mean()})
tab_e = pd.DataFrame(lignes_e)
print(tab_e.round(3).to_string(index=False))
tab_e.round(3).to_csv(f"{DOSSIER_FIGURES}/E_organisation.csv", index=False, encoding="utf-8-sig")

# ------------------------------------------------- F. meteo et correlations
print("\n=== F. Météo et lien avec les ventes ===")
meteo = df[["Precipitation_Journaliere", "Temperature_Journaliere"]].describe().T[["min", "25%", "50%", "mean", "75%", "max"]]
meteo["variance"] = df[["Precipitation_Journaliere", "Temperature_Journaliere"]].var()
print(meteo.round(2).to_string())
meteo.round(2).to_csv(f"{DOSSIER_FIGURES}/F_meteo.csv", encoding="utf-8-sig")
r_p, pv_p = pearsonr(df["Temperature_Journaliere"], y)
r_pr, pv_pr = pearsonr(df["Precipitation_Journaliere"], y)
rs_t, pvs_t = spearmanr(df["Temperature_Journaliere"], y)
rs_r, pvs_r = spearmanr(df["Precipitation_Journaliere"], y)
tab_corr = pd.DataFrame({
    "variable": ["Temperature_Journaliere", "Precipitation_Journaliere"],
    "pearson_r": [r_p, r_pr], "pearson_p": [pv_p, pv_pr],
    "spearman_rs": [rs_t, rs_r], "spearman_p": [pvs_t, pvs_r],
})
tab_corr.round(4).to_csv(f"{DOSSIER_FIGURES}/F_correlations.csv", index=False, encoding="utf-8-sig")
print(f"Pearson  Température–Y : r = {r_p:.3f} (p = {pv_p:.4g})   |  Spearman : rs = {rs_t:.3f} (p = {pvs_t:.4g})")
print(f"Pearson  Précipitation–Y : r = {r_pr:.3f} (p = {pv_pr:.4g})   |  Spearman : rs = {rs_r:.3f} (p = {pvs_r:.4g})")

fig, axes = plt.subplots(1, 2, figsize=(15, 5))
df_jr = df[df["Y"] > 0]
sns.boxplot(data=df, x="Saison_Du_Jour", y="Y", ax=axes[0], color="steelblue",
            showfliers=False)
axes[0].set(title=f"Ventes par saison climatique (hors outliers)", xlabel="", ylabel="Unites / jour")
axes[0].tick_params(axis="x", rotation=20)
axes[1].scatter(df["Temperature_Journaliere"] + np.random.uniform(-.15, .15, len(df)),
                y, s=6, alpha=0.35, color="steelblue")
axes[1].set(title=f"Nuage Température / ventes (r = {r_p:.2f})", xlabel="Temperature_Journaliere",
            ylabel="Unites vendues")
plt.tight_layout()
plt.savefig(f"{DOSSIER_FIGURES}/F_meteo_saison.png", bbox_inches="tight")
plt.show()
plt.close()

# ----------------------------------------- G. dynamique annuelle et intermittence
print("\n=== G. Dynamique annuelle ===")
g_an = df.groupby("annee").agg(n_jours=("Y", "size"), moyenne=("Y", "mean"),
                               variance=("Y", lambda v: v.var(ddof=1)),
                               part_zeros=("Y", lambda v: (v == 0).mean()))
g_an["VMR"] = g_an["variance"] / g_an["moyenne"]
print(g_an.round(3).to_string())
g_an.round(3).to_csv(f"{DOSSIER_FIGURES}/G_par_annee.csv", encoding="utf-8-sig")
zeros_flag = (y == 0).astype(int).values
runs, run_cour = [], 0
for z in zeros_flag:
    if z == 1:
        run_cour += 1
    else:
        if run_cour > 0:
            runs.append(run_cour)
        run_cour = 0
if run_cour > 0:
    runs.append(run_cour)
runs = np.array(runs)
print(f"Sequences de zeros consecutifs : n_sequences = {len(runs)}, moyenne = {runs.mean():.2f}")
for seuil in [3, 5, 7]:
    print(f"  sequences >= {seuil} jours : {(runs >= seuil).sum()}  |  plus longue : {int(runs.max())} jours")
tab_runs = pd.DataFrame({"n_sequences": [len(runs)], "moyenne": [runs.mean()], "max": [int(runs.max())],
                         "n>=3jours": [(runs >= 3).sum()], "n>=5jours": [(runs >= 5).sum()],
                         "n>=7jours": [(runs >= 7).sum()]})
tab_runs.round(2).to_csv(f"{DOSSIER_FIGURES}/G_sequences_zeros.csv", index=False, encoding="utf-8-sig")
