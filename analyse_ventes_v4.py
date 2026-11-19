# -*- coding: utf-8 -*-
"""
================================================================================
Modelisation statistique des ventes journalieres d'une officine
Code corrigé (version 4, academique) - Master de recherche en statistique
================================================================================
Population etudiee : jours d'ouverture de l'officine uniquement. Les dimanches
hors garde ont ete retires de la base en amont ; les jours feries restants
sont traites explicitement (variable jour_ferie dans la partie logit des
modeles compounds) et font l'objet d'une analyse de sensibilite (section 10).

Protocole :
  1. Exploration et partition chronologique train/test (80/20)
  2. Reference Poisson : VIF, surdispersion (Cameron & Trivedi 1990),
     autocorrelation (Durbin-Watson), erreurs-types HAC
  3. Six modeles a armes egales : Poisson, Binomiale Negative (NB2), ZIP, ZINB,
     Hurdle Poisson, Hurdle NB (logit sur P(Y>0) + comptage tronque a zero)
  4. Exces de zeros teste CONTRE le modele NB (test predictif Monte-Carlo),
     et non contre le Poisson
  5. Tests de Vuong (corriges AIC) uniquement sur les paires NON emboitees
  6. Evaluation en distribution : logscore, Brier sur P(Y=0), PIT randomise
  7. Benchmarks Croston et SBA (Croston 1972 ; Syntetos & Boylan 2005)
  8. Point de commande au niveau de service cible : quantile de la demande
     cumulee sur l'horizon L (convolution des lois predictives quotidiennes)
  9. Analyse de sensibilite : exclusion des jours feries
================================================================================
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm, nbinom, poisson as poisson_dist, chi2, uniform

import statsmodels.api as sm
from statsmodels.discrete.discrete_model import Poisson, NegativeBinomial, Logit
from statsmodels.discrete.count_model import ZeroInflatedPoisson, ZeroInflatedNegativeBinomialP
from statsmodels.discrete.truncated_model import TruncatedLFPoisson, TruncatedLFNegativeBinomialP
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.stats.stattools import durbin_watson
from statsmodels.graphics.tsaplots import plot_acf
from sklearn.metrics import mean_absolute_error

warnings.filterwarnings("ignore")

# ==============================================================================
# 0. CONFIGURATION
# ==============================================================================

FICHIER_DONNEES = "base_donnees_journaliere_corrige.xlsx"
FEUILLE_DONNEES = "Donnees_journalieres"
VARIABLE_CIBLE = "Fum_Fer"                       # ou "Amoxicilline"
DOSSIER_FIGURES = "figures_v4"
ALPHA = 0.05
RANDOM_STATE = 42
PART_TRAIN = 0.8                                 # coupure chronologique
PERIODE = 7                                      # periodicite hebdomadaire (HAC)
LAGS_LJUNG_BOX = [PERIODE, 2 * PERIODE, 4 * PERIODE]   # retards coherents partout
VARIABLE_PROFIL = "Temperature_Journaliere"
LEAD_TIME = 7                                    # delai de reapprovisionnement (jours)
NIVEAU_SERVICE = 0.95                            # probabilite de non-rupture ciblee
N_SIM_EXCESS = 4999                              # simulations du test predictif de calibrage
N_SIM_HL = 1999                                  # simulations du Hosmer-Lemeshow generalise
N_GROUPES_L = 10                                 # groupes du test de Hosmer-Lemeshow

# Partie logit de l'inflation ZIP/ZINB (mecanisme des zeros quasi structurels)
VARIABLES_INFLATION = ["Vacance", "dimanche", "Jour_De_Garde", "jour_ferie"]

NOMS_MODELES = ["Poisson", "Binomial Negatif", "ZIP", "ZINB", "Hurdle Poisson", "Hurdle NB"]

os.makedirs(DOSSIER_FIGURES, exist_ok=True)
np.random.seed(RANDOM_STATE)
sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams["figure.dpi"] = 110

# ==============================================================================
# 1. DONNEES ET CONSTRUCTION DES MATRICES
# ==============================================================================

df = pd.read_excel(FICHIER_DONNEES, sheet_name=FEUILLE_DONNEES)
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)
df["Y"] = df[VARIABLE_CIBLE].astype(int)

df = pd.get_dummies(df, columns=["Saison_Du_Jour"], prefix="saison", drop_first=True)
colonnes_saison = [c for c in df.columns if c.startswith("saison_")]
df[colonnes_saison] = df[colonnes_saison].astype(int)

for c in ["Vacance", "Jour_De_Garde", "jour_ferie"]:
    if c in df.columns:
        df[c] = df[c].astype(int)

# Indicateurs de jours reconstruits depuis la date. Dimanche = modalite de
# reference dans la composante comptage ; seuls les dimanches DE GARDE subsistent
# dans la base (population = jours d'ouverture), donc "dimanche" reste utilise
# comme covariable de l'inflation ZIP/ZINB.
df = df.drop(columns=["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"],
             errors="ignore")
jours = {"lundi": 0, "mardi": 1, "mercredi": 2, "jeudi": 3,
         "vendredi": 4, "samedi": 5, "dimanche": 6}
for j, num in jours.items():
    df[j] = (df["date"].dt.day_of_week == num).astype(int)

# Les variables optionnelles (ex. jour_ferie) ne sont retenues que si presentes
dispo = set(df.columns)
VARIABLES_EXPLICATIVES = (
    [c for c in ["Precipitation_Journaliere", "Temperature_Journaliere", "Jour_De_Garde",
                 "Vacance", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi",
                 "jour_ferie"] if c in dispo]
    + colonnes_saison
)
VARIABLES_INFLATION = [c for c in VARIABLES_INFLATION if c in dispo]

print("=== 1. Population et descriptif ===")
print(f"Periode : {df['date'].min().date()} -> {df['date'].max().date()} "
      f"(n = {len(df)} jours d'ouverture)")
if "jour_ferie" in dispo:
    print(f"Jours feries dans la base : {int(df['jour_ferie'].sum())}")
print(f"Jours de garde : {int(df['Jour_De_Garde'].sum())} | "
      f"Dimanches (garde) : {int(df['dimanche'].sum())}")
moy_y, var_y = df["Y"].mean(), df["Y"].var(ddof=1)
print(f"Moyenne = {moy_y:.3f} | Variance = {var_y:.3f} | VMR = {var_y / moy_y:.2f}")
print(f"Zeros observes = {(df['Y'] == 0).mean():.1%} | attendus sous Poisson({moy_y:.2f}) = "
      f"{poisson_dist.pmf(0, mu=moy_y):.1%}")

coupure = int(len(df) * PART_TRAIN)
d_tr, d_te = df.iloc[:coupure].copy(), df.iloc[coupure:].copy()
y_tr = d_tr["Y"].values.astype(int)
y_te = d_te["Y"].values.astype(int)
X_tr = sm.add_constant(d_tr[VARIABLES_EXPLICATIVES].astype(float), has_constant="add")
X_te = sm.add_constant(d_te[VARIABLES_EXPLICATIVES].astype(float), has_constant="add")
Xi_tr = sm.add_constant(d_tr[VARIABLES_INFLATION].astype(float), has_constant="add")
Xi_te = sm.add_constant(d_te[VARIABLES_INFLATION].astype(float), has_constant="add")
K = int(df["Y"].max()) * 2 + 30
print(f"Train = {len(d_tr)} | Test = {len(d_te)} (coupure : {d_te['date'].iloc[0].date()}) | "
      f"max = {int(df['Y'].max())}, troncature PMF K = {K}")

fig, axes = plt.subplots(1, 2, figsize=(15, 5))
sns.histplot(df["Y"], discrete=True, stat="probability", ax=axes[0], color="steelblue")
xv = np.arange(0, int(df["Y"].max()) + 1)
axes[0].plot(xv, poisson_dist.pmf(xv, mu=moy_y), "o--", color="red",
             label=f"Poisson({moy_y:.2f})")
axes[0].set(title="Distribution des ventes journalieres (jours d'ouverture)",
            xlabel="Unites vendues", ylabel="Frequence relative")
axes[0].legend()
axes[1].plot(df["date"], df["Y"], lw=0.6, color="steelblue")
axes[1].plot(df["date"], df["Y"].rolling(30, center=True).mean(), color="red", lw=1.8,
             label="Moyenne mobile 30 j")
axes[1].set(title="Serie temporelle", xlabel="Date", ylabel="Unites vendues")
axes[1].legend()
plt.tight_layout()
plt.savefig(f"{DOSSIER_FIGURES}/01_distribution_et_serie.png", bbox_inches="tight")
plt.show()
plt.close()

# ==============================================================================
# 2. COLINEARITE (VIF) ET REFERENCE POISSON : TESTS PRELIMINAIRES
# ==============================================================================

X_vif = sm.add_constant(df[VARIABLES_EXPLICATIVES].astype(float), has_constant="add")
vif = pd.Series([variance_inflation_factor(X_vif.values, i) for i in range(1, X_vif.shape[1])],
                index=VARIABLES_EXPLICATIVES)
print("\n=== 2. Colinearite et Poisson de reference ===")
print("VIF > 10 :", vif[vif > 10].round(1).to_dict() if (vif > 10).any() else "aucune variable")

glm_pois = sm.GLM(y_tr, X_tr, family=sm.families.Poisson()).fit()
mu_p = np.asarray(glm_pois.fittedvalues)
disp_p = float(np.sum((y_tr - mu_p) ** 2 / mu_p) / glm_pois.df_resid)
pearson_p = (y_tr - mu_p) / np.sqrt(mu_p)

# Cameron & Trivedi (1990) : regression auxiliaire de ((y-mu)^2 - y)/mu sur mu
# sans constante ; statistique z asymptotique, test unilaterale (alpha > 0)
z_ct = ((y_tr - mu_p) ** 2 - y_tr) / mu_p
aux_ct = sm.OLS(z_ct, mu_p).fit()
t_ct, p_ct = float(aux_ct.tvalues[0]), float(norm.sf(aux_ct.tvalues[0]))

dw_p = durbin_watson(pearson_p)

# Van den Broeck (1995), generalise au cas de regression (p0_i = exp(-mu_i), mu_i ajuste par le GLM) :
# score de l'exces de zeros contre la Poisson ; terme correctif - mu_i*p0_i^2 car mu est estime
p0_p = np.exp(-mu_p)
num_vdb = float((int((y_tr == 0).sum()) - float(np.sum(p0_p))) ** 2)
den_vdb = float(np.sum(p0_p * (1 - p0_p) - mu_p * p0_p ** 2))
stat_vdb = num_vdb / den_vdb if den_vdb > 0 else np.nan
p_vdb = float(chi2.sf(stat_vdb, 1)) if np.isfinite(stat_vdb) else np.nan

print(f"Dispersion de Pearson (Poisson) : {disp_p:.3f}  (>1 : surdispersion)")
print(f"Cameron-Trivedi (unilateral)    : t = {t_ct:.3f}, p = {p_ct:.4g}  -> "
      f"{'surdispersion confirmee' if p_ct < ALPHA else 'Poisson acceptable'}")
obs_zeros, att_zeros = int((y_tr == 0).sum()), float(np.sum(p0_p))
print(f"Zeros observes vs attendus      : {obs_zeros} vs {att_zeros:.1f}  (ratio {obs_zeros / att_zeros:.2f})")
print(f"Van den Broeck (exces de zeros) : chi2 = {stat_vdb:.2f}, p = {p_vdb:.4g}  -> "
      f"{'exces de zeros contre la Poisson' if p_vdb < ALPHA else 'pas d exces de zeros detecte'}"
      "  [preliminaire : ne distingue pas l'exces de zeros de la surdispersion ; "
      "le test decisif est fait contre la NB, cf. section 6]")
print(f"Durbin-Watson (residus Pearson) : {dw_p:.3f}  (2 = pas d'autocorrelation d'ordre 1)")

glm_hac = sm.GLM(y_tr, X_tr, family=sm.families.Poisson()).fit(
    cov_type="HAC", cov_kwds={"maxlags": PERIODE})
tab_se = pd.DataFrame({
    "coef": glm_pois.params, "SE_classique": glm_pois.bse, "SE_HAC": glm_hac.bse,
    "p_classique": glm_pois.pvalues, "p_HAC": glm_hac.pvalues
})
print("\nPoisson : erreurs-types classiques vs HAC (maxlag = PERIODE)")
print(tab_se.round(4).to_string())
tab_se.to_csv(f"{DOSSIER_FIGURES}/poisson_se_classique_vs_hac.csv", encoding="utf-8-sig")

tests = {}
tests["Exces de zeros (Van den Broeck, chi2)"] = (stat_vdb, p_vdb)
tests["Surdispersion (Cameron-Trivedi)"] = (t_ct, p_ct)
tests["Autocorrelation (Durbin-Watson)"] = (dw_p, np.nan)
tests["Dispersion de Pearson (reference Poisson)"] = (disp_p, np.nan)

# ==============================================================================
# 3. AJUSTEMENT DES SIX MODELES
# ==============================================================================

print("\n=== 3. Ajustement des six modeles ===")
modeles = {}
for nom in NOMS_MODELES:
    try:
        if nom == "Poisson":
            r = Poisson(y_tr, X_tr).fit(disp=0, maxiter=200)
            p, s = np.asarray(r.params), np.asarray(r.bse)
            modeles[nom] = dict(beta=p, se_beta=s, alpha=None, gamma=None, se_gamma=None,
                                k=len(p),
                                ok=bool(getattr(r, "mle_retvals", {}).get("converged", True)))
        elif nom == "Binomial Negatif":
            r = NegativeBinomial(y_tr, X_tr, loglike_method="nb2").fit(disp=0, maxiter=200)
            p, s = np.asarray(r.params), np.asarray(r.bse)
            modeles[nom] = dict(beta=p[:-1], se_beta=s[:-1], alpha=float(p[-1]),
                                gamma=None, se_gamma=None, k=len(p),
                                ok=bool(getattr(r, "mle_retvals", {}).get("converged", True)))
        elif nom in ("ZIP", "ZINB"):
            ki = Xi_tr.shape[1]               # statsmodels : inflation en premier
            if nom == "ZIP":
                r = ZeroInflatedPoisson(y_tr, X_tr, exog_infl=Xi_tr,
                                        inflation="logit").fit(disp=0, maxiter=500)
            elif nom == "ZINB":
                sp_p = ZeroInflatedPoisson(y_tr, X_tr, exog_infl=Xi_tr,
                                           inflation="logit").fit(disp=0, maxiter=500)
                sp_par = np.append(np.asarray(sp_p.params), 0.1)
                r = ZeroInflatedNegativeBinomialP(y_tr, X_tr, exog_infl=Xi_tr,
                                                  inflation="logit", p=2).fit(
                    disp=0, maxiter=2000, method="lbfgs", start_params=sp_par)
            p, s = np.asarray(r.params), np.asarray(r.bse)
            fin = None if nom == "ZIP" else -1
            modeles[nom] = dict(gamma=p[:ki], se_gamma=s[:ki], beta=p[ki:fin],
                                se_beta=s[ki:fin],
                                alpha=None if nom == "ZIP" else float(p[-1]), k=len(p),
                                ok=bool(getattr(r, "mle_retvals", {}).get("converged", True)))
        else:  # Hurdle : logit sur P(Y>0) + comptage tronque a zero, estimes separement
            pos = y_tr > 0
            lg = Logit(pos.astype(int), X_tr).fit(disp=0, maxiter=2000, method="lbfgs")
            if nom == "Hurdle Poisson":
                tr = TruncatedLFPoisson(y_tr[pos], X_tr.iloc[pos],
                                        truncation=0).fit(disp=0, maxiter=500)
                beta, se_beta, alpha = (np.asarray(tr.params), np.asarray(tr.bse), None)
            else:
                tr_pois = TruncatedLFPoisson(y_tr[pos], X_tr.iloc[pos],
                                             truncation=0).fit(disp=0, maxiter=500)
                tr = TruncatedLFNegativeBinomialP(y_tr[pos], X_tr.iloc[pos], truncation=0, p=2
                                                  ).fit(disp=0, maxiter=2000,
                                                        start_params=np.append(
                                                            np.asarray(tr_pois.params), 0.1))
                beta, se_beta, alpha = (np.asarray(tr.params)[:-1], np.asarray(tr.bse)[:-1],
                                        float(np.asarray(tr.params)[-1]))
            ok_lg = bool(lg.mle_retvals["converged"])
            if nom == "Hurdle NB":
                # alpha identifie seulement s'il reste strictement positif ;
                # s'il est a la frontiere (~0), Hurdle NB se confond avec Hurdle Poisson
                ok_nb = (bool(tr.mle_retvals.get("converged")) and alpha > 1e-6)
            else:
                ok_nb = bool(tr.mle_retvals["converged"])
            modeles[nom] = dict(beta=beta, se_beta=se_beta, alpha=alpha,
                                gamma=np.asarray(lg.params), se_gamma=np.asarray(lg.bse),
                                k=len(lg.params) + len(beta), ok=ok_lg and ok_nb)
        print(f"[OK] {nom} (convergence : {modeles[nom]['ok']})")
    except Exception as e:
        print(f"[Echec] {nom} : {e}")

# Seuls les modeles a coefficients et erreurs-types finis entrent dans la comparaison
noms = [n for n in NOMS_MODELES
        if n in modeles
        and all(v is None or np.all(np.isfinite(np.asarray(v)))
                for v in (modeles[n]["beta"], modeles[n]["se_beta"],
                          modeles[n]["gamma"], modeles[n]["se_gamma"]))]

# Matrices predictives P(Y = k | x_i), k = 0..K-1, construites par modele (sans fonction)
P_tr, P_te = {}, {}
for n in noms:
    m = modeles[n]
    mu_tr = np.exp(np.asarray(X_tr) @ m["beta"])
    mu_te = np.exp(np.asarray(X_te) @ m["beta"])
    k_ax = np.arange(K)[None, :]
    if m["alpha"] is None:
        f_tr = poisson_dist.pmf(k_ax, mu_tr[:, None])
        f_te = poisson_dist.pmf(k_ax, mu_te[:, None])
    else:
        a = max(m["alpha"], 1e-8)
        f_tr = nbinom.pmf(k_ax, 1 / a, 1 / (1 + a * mu_tr[:, None]))
        f_te = nbinom.pmf(k_ax, 1 / a, 1 / (1 + a * mu_te[:, None]))
    if n in ("ZIP", "ZINB"):
        pi = (1 / (1 + np.exp(-(np.asarray(Xi_tr) @ m["gamma"]))))[:, None]
        pi_te = (1 / (1 + np.exp(-(np.asarray(Xi_te) @ m["gamma"]))))[:, None]
        P = (1 - pi) * f_tr
        P[:, [0]] += pi
        Pt = (1 - pi_te) * f_te
        Pt[:, [0]] += pi_te
    elif n in ("Hurdle Poisson", "Hurdle NB"):
        phi = (1 / (1 + np.exp(-(np.asarray(X_tr) @ m["gamma"]))))[:, None]
        phi_te = (1 / (1 + np.exp(-(np.asarray(X_te) @ m["gamma"]))))[:, None]
        P = phi * f_tr / np.clip(1 - f_tr[:, [0]], 1e-12, None)
        P[:, [0]] = 1 - phi
        Pt = phi_te * f_te / np.clip(1 - f_te[:, [0]], 1e-12, None)
        Pt[:, [0]] = 1 - phi_te
    else:
        P, Pt = f_tr, f_te
    P_tr[n] = P / P.sum(axis=1, keepdims=True)
    P_te[n] = Pt / Pt.sum(axis=1, keepdims=True)

# ==============================================================================
# 4. COMPARAISON GLOBALE : AIC/BIC, ZEROS, DISPERSION, CRITERES DE VALIDATION
# ==============================================================================

print("\n=== 4. Comparaison des modeles ===")
lignes = []
for n in noms:
    m = modeles[n]
    P = P_tr[n]
    k_ax = np.arange(P.shape[1])
    moy_tr = P @ k_ax
    var_tr = np.clip(P @ k_ax ** 2 - moy_tr ** 2, 1e-9, None)
    moy_te = P_te[n] @ k_ax
    llf = float(np.sum(np.log(np.clip(P[np.arange(len(y_tr)),
                                      np.minimum(y_tr, P.shape[1] - 1)], 1e-12, None))))
    zeros_att = float(P[:, 0].sum())
    pi_moy = (float(np.mean(1 / (1 + np.exp(-(np.asarray(Xi_tr) @ m["gamma"])))))
              if n in ("ZIP", "ZINB") else np.nan)
    lignes.append({
        "modele": n, "converge": m["ok"], "k": m["k"], "LogLik": llf,
        "AIC": -2 * llf + 2 * m["k"], "BIC": -2 * llf + m["k"] * np.log(len(y_tr)),
        "zeros_obs": int((y_tr == 0).sum()), "zeros_attendus": zeros_att,
        "ratio_obs_att": (y_tr == 0).sum() / zeros_att,
        "disp_Pearson": float(np.sum((y_tr - moy_tr) ** 2 / var_tr) / (len(y_tr) - m["k"])),
        "pi_inflation_moyen": pi_moy,
        "MAE_test": mean_absolute_error(y_te, moy_te),
        "RMSE_test": float(np.sqrt(np.mean((y_te - moy_te) ** 2))),
        "logscore_test": float(np.mean(np.log(np.clip(
            P_te[n][np.arange(len(y_te)), np.minimum(y_te, P_te[n].shape[1] - 1)],
            1e-12, None)))),
        "Brier_P0_test": float(np.mean(((y_te == 0).astype(float) - P_te[n][:, 0]) ** 2)),
    })
tab = pd.DataFrame(lignes).set_index("modele").sort_values("AIC")
# "degenere" ne concerne que les modeles zero-inflated dont l'inflation s'evapore
zi_mask = tab.index.isin(["ZIP", "ZINB"])
tab["degenere"] = zi_mask & (tab["pi_inflation_moyen"].values < 0.01)
print(tab.round(3).to_string())
if tab["degenere"].any():
    print("\n[ATTENTION] modeles zero-inflated degeneres (inflation moyenne < 1 %) : "
          f"{tab.index[tab['degenere']].tolist()} -> equivalents au modele sans inflation, "
          "a ne pas interpreter (zeros deja expliques par l'exposition).")
tab.to_csv(f"{DOSSIER_FIGURES}/comparaison_modeles.csv", encoding="utf-8-sig")

if "Poisson" in noms and "Binomial Negatif" in noms:
    lr = 2 * (tab.loc["Binomial Negatif", "LogLik"] - tab.loc["Poisson", "LogLik"])
    p_lr = 0.5 * chi2.sf(max(lr, 0), 1)      # alpha = 0 en bordure : 0.5*chi2(0)+0.5*chi2(1)
    tests["LR Poisson vs NB"] = (lr, p_lr)
    print(f"\nLR Poisson vs NB : LR = {lr:.2f}, p = {p_lr:.4g}  -> "
          f"{'NB preferable' if p_lr < ALPHA else 'Poisson suffisant'}")

# --- Exces de zeros CONTRE le NB : test predictif de calibrage (Gelman et al. 1996) ---
# H0 : les donnees proviennent du modele NB ajuste / H1 unilateral : plus de zeros que prevu
if ("Binomial Negatif" in noms) and (not bool(tab.loc["Binomial Negatif", "degenere"])):  # noqa: E501
    P_nb = P_tr["Binomial Negatif"]
    cdf_nb = np.cumsum(P_nb, axis=1)
    rng = np.random.default_rng(RANDOM_STATE)
    zeros_obs = int((y_tr == 0).sum())
    zeros_sim = np.empty(N_SIM_EXCESS)
    n_obs = len(y_tr)
    for b in range(N_SIM_EXCESS):
        u = rng.random((n_obs, 1))
        y_sim = np.minimum((u > cdf_nb).sum(axis=1), P_nb.shape[1] - 1)
        zeros_sim[b] = np.sum(y_sim == 0)
    p_excess = float((1 + np.sum(zeros_sim >= zeros_obs)) / (N_SIM_EXCESS + 1))
    mu_ex = float(np.mean(zeros_sim))
    tests["Exces de zeros vs NB (predictif)"] = (zeros_obs / mu_ex, p_excess)
    print(f"\nExces de zeros CONTRE le NB (test predictif, {N_SIM_EXCESS} simulations) :")
    print(f"  zeros observes = {zeros_obs} | attendus sous NB (moyenne simulee) = {mu_ex:.1f} | "
          f"p = {p_excess:.4f}  -> "
          f"{'zeros non expliques par le NB : machinerie zero-inflated justifiee' if p_excess < ALPHA else 'NB capture les zeros : zero-inflation superflue'}")

# --- Tests de Vuong (corriges AIC) : paires NON emboitees uniquement ---
PAIRES_VUONG = [("Binomial Negatif", "ZIP"),
                ("Binomial Negatif", "Hurdle Poisson"),
                ("Binomial Negatif", "Hurdle NB"),
                ("ZINB", "Hurdle NB")]
lignes_v = []
for a, b in PAIRES_VUONG:
    if (a in noms) and (b in noms) and (not tab.loc[[a, b], "degenere"].any()):
        ll1 = np.log(np.clip(P_tr[a][np.arange(len(y_tr)), np.minimum(y_tr, P_tr[a].shape[1] - 1)],
                             1e-12, None))
        ll2 = np.log(np.clip(P_tr[b][np.arange(len(y_tr)), np.minimum(y_tr, P_tr[b].shape[1] - 1)],
                             1e-12, None))
        d_i = ll1 - ll2
        stat_v = (np.sqrt(len(y_tr)) * (d_i.mean() -
                  (modeles[a]["k"] - modeles[b]["k"]) / len(y_tr)) / d_i.std(ddof=1))
        p_v = 2 * norm.sf(abs(stat_v))
        pref = (a if stat_v > 0 else b) if p_v < ALPHA else "pas de difference significative"
        lignes_v.append({"modele_1": a, "modele_2": b, "V": stat_v, "p_value": p_v,
                         "prefere": pref})
tab_v = pd.DataFrame(lignes_v)
print("\n--- Tests de Vuong (corriges AIC) sur paires NON emboitees ---")
print(tab_v.round(4).to_string(index=False))
tab_v.to_csv(f"{DOSSIER_FIGURES}/tests_vuong_non_emboitees.csv", index=False,
             encoding="utf-8-sig")

# ==============================================================================
# 5. ROOTOGRAMMES (calibration en distribution, echelle racine carree)
# ==============================================================================

KR = min(15, int(y_tr.max()))
k_r = np.arange(KR + 1)
obs = np.array([(y_tr == k).mean() for k in k_r])
fig, axes = plt.subplots(len(noms), 2, figsize=(16, 3.4 * len(noms)))
for i, n in enumerate(noms):
    att = P_tr[n][:, :KR + 1].mean(axis=0)
    axes[i, 0].bar(k_r, np.sqrt(obs), color=plt.cm.tab10(i % 10), edgecolor="white")
    axes[i, 0].plot(k_r, np.sqrt(att), "o-", color="red", lw=1.5, ms=4)
    axes[i, 0].set_title(f"{n} : standing (sqrt frequence observee, pointille attendue)",
                         fontsize=10)
    axes[i, 1].bar(k_r, np.sqrt(obs) - np.sqrt(att), color=plt.cm.tab10(i % 10),
                   edgecolor="white")
    axes[i, 1].axhline(0, color="red", lw=1.2)
    axes[i, 1].set_title(f"{n} : suspended (ecart a l'attendu)", fontsize=10)
plt.suptitle(f"Rootogrammes par modele - entrainement, {VARIABLE_CIBLE}", fontsize=13, y=1.005)
plt.tight_layout()
plt.savefig(f"{DOSSIER_FIGURES}/02_rootogrammes_tous_modeles.png", bbox_inches="tight")
plt.show()
plt.close()

# ==============================================================================
# 6. MODELE RETENU : EFFETS ET PROFIL DE PREDICTION
# ==============================================================================

cand = tab[tab["converge"] & ~tab["degenere"]]
meilleur = (cand if len(cand) else tab).index[0]
m_best = modeles[meilleur]
P = P_tr[meilleur]
suffixe = meilleur.replace(" ", "_")
print(f"\n=== 6. Modele retenu : {meilleur} (AIC minimal parmi les modeles convergents "
      "non degeneres) ===")

tab_cnt = pd.DataFrame({
    "coef": m_best["beta"], "exp(coef)": np.exp(m_best["beta"]),
    "IC95_inf": np.exp(m_best["beta"] - 1.96 * m_best["se_beta"]),
    "IC95_sup": np.exp(m_best["beta"] + 1.96 * m_best["se_beta"]),
    "p_value": 2 * norm.sf(np.abs(m_best["beta"] / m_best["se_beta"])),
}, index=X_tr.columns)
print("\nComposante comptage : exp(coef) = rapport de taux (IRR)")
print(tab_cnt.round(4).to_string())
tab_cnt.to_csv(f"{DOSSIER_FIGURES}/effets_comptage_{suffixe}.csv", encoding="utf-8-sig")

if m_best["gamma"] is not None:
    zi = meilleur in ("ZIP", "ZINB")
    noms_lg = Xi_tr.columns if zi else X_tr.columns
    tab_lg = pd.DataFrame({
        "coef": m_best["gamma"], "exp(coef)": np.exp(m_best["gamma"]),
        "IC95_inf": np.exp(m_best["gamma"] - 1.96 * m_best["se_gamma"]),
        "IC95_sup": np.exp(m_best["gamma"] + 1.96 * m_best["se_gamma"]),
        "p_value": 2 * norm.sf(np.abs(m_best["gamma"] / m_best["se_gamma"])),
    }, index=noms_lg)
    sens = ("P(exces de zeros) : exp(coef) > 1 => plus de jours sans vente structurels" if zi
            else "P(Y > 0) : exp(coef) > 1 => plus de chances d'avoir au moins une vente")
    print(f"\nComposante logit - {sens}")
    print(tab_lg.round(4).to_string())
    tab_lg.to_csv(f"{DOSSIER_FIGURES}/effets_logit_{suffixe}.csv", encoding="utf-8-sig")

# --- Profil de prediction : variable continue variee, autres a valeur de reference ---
grille = np.linspace(df[VARIABLE_PROFIL].min(), df[VARIABLE_PROFIL].max(), 60)
base = X_tr.mean()
for c in X_tr.columns:
    if set(X_tr[c].unique()) <= {0.0, 1.0}:
        base[c] = 0.0
base["const"] = 1.0
Xn = pd.DataFrame([base] * len(grille)).reset_index(drop=True)
Xn[VARIABLE_PROFIL] = grille
base_xi = Xi_tr.mean()
for c in Xi_tr.columns:
    if set(Xi_tr[c].unique()) <= {0.0, 1.0}:
        base_xi[c] = 0.0
base_xi["const"] = 1.0
Xin = pd.DataFrame([base_xi] * len(grille)).reset_index(drop=True)
mu_pr = np.exp(np.asarray(Xn) @ m_best["beta"])
k_ax = np.arange(K)[None, :]
f_pr = (poisson_dist.pmf(k_ax, mu_pr[:, None]) if m_best["alpha"] is None
        else nbinom.pmf(k_ax, 1 / max(m_best["alpha"], 1e-8),
                        1 / (1 + max(m_best["alpha"], 1e-8) * mu_pr[:, None])))
if meilleur in ("ZIP", "ZINB"):
    pi_pr = (1 / (1 + np.exp(-(np.asarray(Xin) @ m_best["gamma"]))))[:, None]
    P_pr = (1 - pi_pr) * f_pr
    P_pr[:, [0]] += pi_pr
elif meilleur in ("Hurdle Poisson", "Hurdle NB"):
    phi_pr = (1 / (1 + np.exp(-(np.asarray(Xn) @ m_best["gamma"]))))[:, None]
    P_pr = phi_pr * f_pr / np.clip(1 - f_pr[:, [0]], 1e-12, None)
    P_pr[:, [0]] = 1 - phi_pr
else:
    P_pr = f_pr
P_pr = P_pr / P_pr.sum(axis=1, keepdims=True)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].plot(grille, P_pr @ np.arange(K), color="blue", label="Ventes attendues (reponse)")
axes[0].plot(grille, mu_pr, color="lightblue", ls="--", label="Composante comptage (mu)")
axes[0].set(title=f"{meilleur} : effet de {VARIABLE_PROFIL} (autres covariables figees : "
                  "continues a la moyenne, binaires a 0)",
            xlabel=VARIABLE_PROFIL, ylabel="Unites / jour")
axes[0].legend()
axes[1].plot(grille, P_pr[:, 0], color="red")
axes[1].set(title="Probabilite d'un jour sans vente", xlabel=VARIABLE_PROFIL, ylabel="P(Y=0)")
plt.tight_layout()
plt.savefig(f"{DOSSIER_FIGURES}/03_profil_prediction.png", bbox_inches="tight")
plt.show()
plt.close()

# ==============================================================================
# 7. DIAGNOSTICS DU MODELE RETENU : DISPERSION, AUTOCORRELATION, PIT
# ==============================================================================

k_ax = np.arange(P.shape[1])
moy = P @ k_ax
var_res = np.clip(P @ k_ax ** 2 - moy ** 2, 1e-9, None)
disp_final = float(np.sum((y_tr - moy) ** 2 / var_res) / (len(y_tr) - m_best["k"]))
pearson = (y_tr - moy) / np.sqrt(var_res)
dw = durbin_watson(pearson)
lb = acorr_ljungbox(pearson, lags=LAGS_LJUNG_BOX, return_df=True)

print(f"\n=== 7. Diagnostics de {meilleur} (entrainement) ===")
print(f"Dispersion de Pearson (chi2/ddl) : {disp_final:.3f}")
print(f"Durbin-Watson                    : {dw:.3f}")
print(f"Ljung-Box (retards {LAGS_LJUNG_BOX}, coherents dans toute l'analyse) :")
print(lb.round(4).to_string())

# PIT randomise (Czado et al. 2009 ; Denuit et al.) : valeur pivot u tiree
# uniformement dans [F(y-1), F(y)] ; uniformite du PIT -> calibration en distribution
rng = np.random.default_rng(RANDOM_STATE)
cdf = np.cumsum(P, axis=1)
idx = np.arange(len(y_tr))
u_lo = np.where(y_tr == 0, 0.0, cdf[idx, np.maximum(y_tr - 1, 0)])
u_hi = cdf[idx, np.minimum(y_tr, P.shape[1] - 1)]
piv = rng.uniform(u_lo, u_hi)
print(f"PIT randomise : moyenne = {piv.mean():.3f} (attendu 0.5) | "
      f"ecart-type = {piv.std():.3f} (attendu 0.289)")

# Hosmer-Lemeshow generalise : deciles de risque, somme des ecarts au carre
# p-value par simulation sous la loi ajustee du modele retenu (pas de loi pivot
# exacte pour les comptages)
grp = pd.qcut(pd.Series(moy).rank(method="first"), N_GROUPES_L, labels=False).values
obs_g = np.bincount(grp, weights=y_tr.astype(float), minlength=N_GROUPES_L)
att_g = np.bincount(grp, weights=moy, minlength=N_GROUPES_L)
hl_stat = float(np.sum((obs_g - att_g) ** 2 / att_g))
s_hl_sim = np.empty(N_SIM_HL)
for b in range(N_SIM_HL):
    u_b = rng.random((len(y_tr), 1))
    y_b = np.minimum((u_b > cdf).sum(axis=1), P.shape[1] - 1)
    o_b = np.bincount(grp, weights=y_b.astype(float), minlength=N_GROUPES_L)
    s_hl_sim[b] = np.sum((o_b - att_g) ** 2 / att_g)
p_hl = float((1 + np.sum(s_hl_sim >= hl_stat)) / (N_SIM_HL + 1))
print(f"Hosmer-Lemeshow simulate : stat = {hl_stat:.2f}, p = {p_hl:.4f}  -> "
      f"{'calibration insuffisante' if p_hl < ALPHA else 'calibration satisfaisante'}")

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
plot_acf(pearson, lags=40, ax=axes[0], title=f"ACF des residus de Pearson ({meilleur})")
sns.histplot(piv, bins=20, stat="density", ax=axes[1], color="mediumpurple")
axes[1].axhline(1.0, color="red", lw=1.5, label="Uniformite (densite = 1)")
axes[1].set(title="PIT randomise (calibration en distribution)", ylim=(0, 2))
axes[1].legend()
sm.qqplot(piv, dist=uniform, line="45", ax=axes[2])
axes[2].set_title("QQ-plot du PIT vs U(0,1)")
plt.tight_layout()
plt.savefig(f"{DOSSIER_FIGURES}/04_diagnostics_residus_pit.png", bbox_inches="tight")
plt.show()
plt.close()

tests[f"[{meilleur}] Dispersion de Pearson"] = (disp_final, np.nan)
tests[f"[{meilleur}] Durbin-Watson"] = (dw, np.nan)
tests[f"[{meilleur}] Ljung-Box lag 28"] = (float(lb["lb_stat"].iloc[-1]),
                                           float(lb["lb_pvalue"].iloc[-1]))
tests[f"[{meilleur}] Hosmer-Lemeshow (simule)"] = (hl_stat, p_hl)

# ==============================================================================
# 8. BENCHMARKS DE SERIES D'INTERMITTENCE : CROSTON ET SBA
# ==============================================================================

print("\n=== 8. Benchmarks Croston et SBA (prevision un pas devant sur le test) ===")
y_tot = np.concatenate([y_tr, y_te])
alpha_c = 0.1
z_hat, q_hat = None, None
intervalle = 1
fc = np.full(len(y_tot), np.nan)
for t in range(len(y_tot)):
    if y_tot[t] > 0:
        if z_hat is None:
            z_hat, q_hat = float(y_tot[t]), float(intervalle)
        else:
            z_hat = (1 - alpha_c) * z_hat + alpha_c * y_tot[t]
            q_hat = (1 - alpha_c) * q_hat + alpha_c * intervalle
        intervalle = 1
    else:
        intervalle += 1
    fc[t] = (z_hat / q_hat) if z_hat is not None else moy_y

croston_te = fc[coupure:]
sba_te = croston_te * (1 - alpha_c / 2)
res_bench = pd.DataFrame({
    "modele": ["Croston", "SBA"],
    "MAE_test": [mean_absolute_error(y_te, croston_te), mean_absolute_error(y_te, sba_te)],
    "RMSE_test": [float(np.sqrt(np.mean((y_te - croston_te) ** 2))),
                  float(np.sqrt(np.mean((y_te - sba_te) ** 2)))],
}).set_index("modele")
tab_perf = pd.concat([tab[["MAE_test", "RMSE_test", "logscore_test", "Brier_P0_test"]],
                      res_bench[["MAE_test", "RMSE_test"]]])
tab_perf.loc[["Croston", "SBA"], "logscore_test"] = np.nan
tab_perf.loc[["Croston", "SBA"], "Brier_P0_test"] = np.nan
print(tab_perf.round(3).to_string())
print("Croston/SBA ne fournissent pas de loi predictive complete : seuls MAE/RMSE "
      "sont comparables.")
tab_perf.to_csv(f"{DOSSIER_FIGURES}/performance_test_benchmarks.csv", encoding="utf-8-sig")

# ==============================================================================
# 9. POINT DE COMMANDE AU NIVEAU DE SERVICE (reponse a la question decisionnelle)
# ==============================================================================

print(f"\n=== 9. Point de commande : horizon L = {LEAD_TIME} jours, "
      f"niveau de service = {NIVEAU_SERVICE:.0%} ===")
# Demande cumulee sur L jours : convolution des lois predictives quotidiennes
# (independance conditionnelle des jours au vu des covariables observees ;
# si moins de L jours disponibles, on complete par la loi predictieve moyenne)
n_dispo = min(LEAD_TIME, P_te[meilleur].shape[0])
pmf_jours = [P_te[meilleur][P_te[meilleur].shape[0] - n_dispo + j] for j in range(n_dispo)]
while len(pmf_jours) < LEAD_TIME:
    pmf_jours.append(P_te[meilleur].mean(axis=0))
taille_max = int(np.ceil(LEAD_TIME * (y_tot.max() + 12)))
p_tot = np.array([1.0])
for pmf_j in pmf_jours:
    p_tot = np.convolve(p_tot, pmf_j)[:taille_max]
if p_tot.sum() <= 0:
    raise ValueError("Convolution degrader : augmenter taille_max")
p_tot = p_tot / p_tot.sum()
cum_tot = np.cumsum(p_tot)
point_commande = int(np.searchsorted(cum_tot, NIVEAU_SERVICE))
demande_attendue = float(p_tot @ np.arange(len(p_tot)))
print(f"Demande attendue sur {LEAD_TIME} jours       : {demande_attendue:.1f} unites")
print(f"Point de commande (quantile {NIVEAU_SERVICE:.0%}) : {point_commande} unites")
print(f"Stock de securite associe            : {point_commande - demande_attendue:.1f} unites")

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(np.arange(len(p_tot)), p_tot, color="steelblue")
ax.axvline(point_commande, color="red", ls="--", lw=1.5,
           label=f"Point de commande ({NIVEAU_SERVICE:.0%}) = {point_commande}")
ax.set(title=f"Distribution predictive de la demande cumulee sur {LEAD_TIME} jours ({meilleur})",
       xlabel="Unites", ylabel="Probabilite")
ax.legend()
plt.tight_layout()
plt.savefig(f"{DOSSIER_FIGURES}/05_point_de_commande.png", bbox_inches="tight")
plt.show()
plt.close()

# ==============================================================================
# 10. ANALYSE DE SENSIBILITE : EXCLUSION DES JOURS FERIES
# ==============================================================================

print("\n=== 10. Analyse de sensibilite : exclusion des jours feries ===")
mask_tr = d_tr["jour_ferie"].values == 0 if "jour_ferie" in d_tr.columns else None
if mask_tr is None:
    print("Indisponible : la colonne jour_ferie est absente de la base. "
          "Action recommandee : faire trier par l'officine la liste des jours "
          "effectivement fermes (fetes legales) pour qualifier la population "
          "ouverte et les zerosStructurels associes.")
elif mask_tr.sum() > 30:
    # jour_ferie est constant une fois les feries exclus : colonne vide a retirer
    vars_sens = [c for c in VARIABLES_EXPLICATIVES if c != "jour_ferie"]
    y_tr_s = y_tr[mask_tr]
    X_tr_s = sm.add_constant(d_tr.loc[mask_tr, vars_sens].astype(float),
                             has_constant="add")
    g_s = Poisson(y_tr_s, X_tr_s).fit(disp=0, maxiter=200)
    nb_s = NegativeBinomial(y_tr_s, X_tr_s, loglike_method="nb2").fit(disp=0, maxiter=200)
    mu_s = np.asarray(g_s.fittedvalues)
    disp_s = float(np.sum((y_tr_s - mu_s) ** 2 / mu_s) / g_s.df_resid)
    zeros_s = int((y_tr_s == 0).sum())
    mu_at_s = np.exp(np.asarray(X_tr_s) @ np.asarray(g_s.params))
    zeros_att_s = float(poisson_dist.pmf(0, mu_at_s).sum())
    print(f"n = {int(mask_tr.sum())} jours (feries exclus) | dispersion Pearson Poisson = "
          f"{disp_s:.3f}")
    print(f"Poisson sans feries : zeros observes = {zeros_s} | attendus = {zeros_att_s:.1f} | "
          f"ratio = {zeros_s / zeros_att_s:.2f}")
    print(f"AIC : Poisson = {-2 * g_s.llf + 2 * X_tr_s.shape[1]:.1f} | "
          f"NB = {-2 * nb_s.llf + 2 * X_tr_s.shape[1] + 2:.1f}")
else:
    print("Trop peu de jours deverrie pour une analyse de sensibilite fiable.")

# ==============================================================================
# 11. SYNTHESE DES TESTS
# ==============================================================================

print("\n=== Synthese des tests ===")
tab_tests = pd.DataFrame(tests, index=["statistique", "p_value"]).T
tab_tests["significatif_5%"] = tab_tests["p_value"] < ALPHA
print(tab_tests.round(4).to_string())
tab_tests.to_csv(f"{DOSSIER_FIGURES}/synthese_tests.csv", encoding="utf-8-sig")
print(f"\n[Fichiers] {DOSSIER_FIGURES}/")
