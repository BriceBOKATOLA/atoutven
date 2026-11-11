"""
04_tester_h12_vendredi.py : test de l'hypothèse H12 selon le protocole écrit
dans hypotheses.md AVANT l'ouverture des données.

H12 : plus une gare dessert une commune où travaillent beaucoup de cadres,
      plus ses validations baissent le vendredi (et le lundi).

Étapes du protocole :
  1. Validations du réseau ferré, par jour et par gare (12 derniers mois publiés).
  2. Jours retenus : hors vacances scolaires (zone C), jours fériés, ponts,
     et jours anormaux (grève, panne) repérés par une règle fixée d'avance.
  3. Titre retenu : "Forfait Navigo" (abonnements, surtout des actifs).
  4. Indicateur par gare : baisse du vendredi = 1 - (moyenne vendredi / moyenne mardi-jeudi).
  5. Gares écartées : moins de 1 000 validations Navigo par jour en moyenne.
  6. Variable explicative : part de cadres parmi ceux qui TRAVAILLENT dans la commune.
  7. Contrôle : part de cadres parmi ceux qui HABITENT la commune.
  Critères de verdict : corrélation de Spearman >= 0,3 ET écart >= 5 points
  entre le quart de gares le plus "cadres" et le quart le moins "cadres".

Entrées : data/brut/idfm_validations_ferre/, data/brut/idfm_referentiel_arrets/,
          data/brut/calendrier/, data/brut/insee_mobpro_2023/
Sorties : console + CSV dans resultats/04_h12/

Lancer depuis la racine du projet :
    .venv\\Scripts\\python.exe src\\04_tester_h12_vendredi.py
"""

import json
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Constantes : toutes viennent du protocole (hypotheses.md), fixé avant le test
# ---------------------------------------------------------------------------

RACINE = Path(__file__).resolve().parent.parent
BRUT = RACINE / "data" / "brut"

TITRE_RETENU = "Forfait Navigo"   # abonnements : surtout des trajets domicile-travail
SEUIL_JOUR_ANORMAL = 0.80         # jour exclu si total < 80 % de la médiane du même jour de semaine du mois
SEUIL_GARE_MIN = 1000             # validations Navigo par jour en moyenne, en dessous : trop de bruit
SEUIL_SPEARMAN = 0.3              # critère 1 du verdict
SEUIL_ECART_POINTS = 5            # critère 2 du verdict (points de pourcentage)

# Numéros de jour de pandas (lundi = 0 ... dimanche = 6)
LUNDI, MARDI, MERCREDI, JEUDI, VENDREDI = 0, 1, 2, 3, 4
# Référence "du mardi au jeudi", comme écrit dans le protocole avant le test.
# On ne la modifie pas après coup, même si le mercredi est un peu plus
# télétravaillé : changer la règle en cours de route fausserait le test.
JOURS_REFERENCE = [MARDI, MERCREDI, JEUDI]

# Code INSEE des cadres dans la variable GS du recensement
CODE_CADRES = "3"
DEPARTEMENTS_IDF = ["75", "77", "78", "91", "92", "93", "94", "95"]


# ---------------------------------------------------------------------------
# 1. Validations
# ---------------------------------------------------------------------------

def charger_validations() -> pd.DataFrame:
    """Lit les 4 fichiers trimestriels et harmonise leurs différences.

    Pourquoi harmoniser : d'un trimestre à l'autre, IDFM a changé le nom de la
    colonne d'identifiant de gare ("id_zdc" ou "ida") et le format des nombres
    (71379 ou 71379.0). Sans cette étape, les gares ne se raccorderaient pas.
    """
    morceaux = []
    for fichier in sorted((BRUT / "idfm_validations_ferre").glob("validations_ferre_jour_*.csv")):
        # utf-8-sig : enlève le caractère invisible (BOM) en début de fichier
        morceau = pd.read_csv(fichier, sep=";", encoding="utf-8-sig")
        morceau = morceau.rename(columns={"ida": "id_zdc"})
        morceaux.append(morceau[["jour", "id_zdc", "libelle_arret", "categorie_titre", "nb_vald"]])
    validations = pd.concat(morceaux, ignore_index=True)
    validations["jour"] = pd.to_datetime(validations["jour"])
    # Identifiant de gare en texte sans ".0", comme dans le référentiel IDFM
    validations["id_zdc"] = validations["id_zdc"].astype("Int64").astype(str)
    return validations


# ---------------------------------------------------------------------------
# 2. Calendrier : jours à exclure
# ---------------------------------------------------------------------------

def jours_feries_et_ponts() -> set:
    """Jours fériés (fichier officiel) + ponts déduits par une règle simple.

    Règle des ponts : le lundi avant un mardi férié et le vendredi après un
    jeudi férié, car beaucoup d'actifs ne travaillent pas ces jours-là.
    """
    with open(BRUT / "calendrier" / "jours_feries_metropole.json", encoding="utf-8") as f:
        feries = {pd.Timestamp(jour) for jour in json.load(f)}
    ponts = set()
    for jour in feries:
        if jour.day_of_week == MARDI:
            ponts.add(jour - pd.Timedelta(days=1))
        if jour.day_of_week == JEUDI:
            ponts.add(jour + pd.Timedelta(days=1))
    return feries | ponts


def jours_vacances_zone_c() -> set:
    """Jours de vacances scolaires de la zone C (académie de Paris).

    Les dates du fichier sont en heure UTC (ex. 2025-10-17T22:00 = 18 octobre
    à minuit, heure de Paris). On les convertit en heure de Paris, puis on
    garde les jours du début (inclus) à la reprise (exclue).
    """
    vacances = pd.read_csv(BRUT / "calendrier" / "vacances_scolaires_zone_c.csv", sep=";", encoding="utf-8-sig")
    # Une seule académie suffit : Paris, Créteil et Versailles ont les mêmes dates.
    # "Enseignants" est écarté : seule la date de reprise des élèves compte ici.
    vacances = vacances[(vacances["location"] == "Paris") & (vacances["population"] != "Enseignants")]
    jours = set()
    for _, periode in vacances.iterrows():
        debut = pd.Timestamp(periode["start_date"]).tz_convert("Europe/Paris").tz_localize(None).normalize()
        reprise = pd.Timestamp(periode["end_date"]).tz_convert("Europe/Paris").tz_localize(None).normalize()
        jours.update(pd.date_range(debut, reprise - pd.Timedelta(days=1)))
    return jours


def jours_anormaux(validations: pd.DataFrame) -> set:
    """Repère les jours de grève ou de panne avec la règle fixée d'avance.

    Un jour est anormal si le total Navigo du réseau est inférieur à 80 % de la
    médiane des mêmes jours de semaine du même mois (ex. tous les mardis de
    novembre). On compare à la médiane, pas à la moyenne, car la médiane n'est
    pas tirée vers le bas par les jours de grève eux-mêmes.
    """
    total = validations.groupby("jour")["nb_vald"].sum().to_frame("total")
    total["mois"] = total.index.to_period("M")
    total["jour_semaine"] = total.index.day_of_week
    mediane = total.groupby(["mois", "jour_semaine"])["total"].transform("median")
    return set(total.index[total["total"] < SEUIL_JOUR_ANORMAL * mediane])


# ---------------------------------------------------------------------------
# 3-5. Indicateur par gare
# ---------------------------------------------------------------------------

def indicateurs_par_gare(validations: pd.DataFrame) -> pd.DataFrame:
    """Calcule pour chaque gare la baisse du vendredi et du lundi (en %).

    Baisse = 100 x (1 - moyenne du jour / moyenne mardi-jeudi).
    Exemple : 8 000 validations le vendredi contre 10 000 en moyenne le mardi
    et le jeudi donne une baisse de 20 %.
    """
    # Somme des validations par gare et par jour (une gare peut avoir plusieurs lignes par jour)
    par_jour = validations.groupby(["id_zdc", "jour"])["nb_vald"].sum().reset_index()
    par_jour["jour_semaine"] = par_jour["jour"].dt.day_of_week
    moyennes = par_jour.groupby(["id_zdc", "jour_semaine"])["nb_vald"].mean().unstack()
    reference = moyennes[JOURS_REFERENCE].mean(axis=1)
    resultat = pd.DataFrame({
        "moyenne_mardi_jeudi": reference,
        "baisse_vendredi_pct": 100 * (1 - moyennes[VENDREDI] / reference),
        "baisse_lundi_pct": 100 * (1 - moyennes[LUNDI] / reference),
        # Moyenne sur tous les jours ouvrés retenus : sert au seuil de taille de gare
        "moyenne_jour_ouvre": par_jour[par_jour["jour_semaine"] <= VENDREDI].groupby("id_zdc")["nb_vald"].mean(),
    })
    return resultat.reset_index()


# ---------------------------------------------------------------------------
# 6-7. Part de cadres par commune (recensement 2023)
# ---------------------------------------------------------------------------

def parts_cadres_par_commune() -> pd.DataFrame:
    """Part de cadres parmi ceux qui travaillent et parmi ceux qui habitent chaque commune.

    À Paris, on travaille à l'arrondissement : c'est aussi l'échelle du
    référentiel des gares (ex. 75117 pour Paris 17e).
    - Lieu de travail : DCLT donne déjà l'arrondissement.
    - Lieu de résidence : COMMUNE vaut 75056 (Paris entier), l'arrondissement
      est dans ARM. On remplace donc COMMUNE par ARM pour les Parisiens.
    """
    chemin = BRUT / "insee_mobpro_2023" / "RP2023_mobpro.parquet"
    actifs = pd.read_parquet(chemin, columns=["COMMUNE", "ARM", "DCLT", "REGION", "REGLT", "GS", "IPONDI"])
    actifs["cadre"] = actifs["GS"] == CODE_CADRES
    actifs["residence"] = actifs["COMMUNE"].where(actifs["ARM"] == "ZZZZZ", actifs["ARM"])

    def part_cadres(sous_ensemble: pd.DataFrame, colonne_commune: str) -> pd.Series:
        """Part pondérée (en %) de cadres par commune."""
        poids_cadres = sous_ensemble["IPONDI"].where(sous_ensemble["cadre"], 0)
        return 100 * poids_cadres.groupby(sous_ensemble[colonne_commune]).sum() \
            / sous_ensemble.groupby(colonne_commune)["IPONDI"].sum()

    # Travailleurs : toute personne qui travaille en Île-de-France, où qu'elle habite
    travail = part_cadres(actifs[actifs["REGLT"] == "11"], "DCLT").rename("part_cadres_emplois_pct")
    # Habitants : résidents d'Île-de-France
    habitants = part_cadres(actifs[actifs["REGION"] == "11"], "residence").rename("part_cadres_habitants_pct")
    return pd.concat([travail, habitants], axis=1).rename_axis("code_commune").reset_index()


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def evaluer(gares: pd.DataFrame, variable: str, indicateur: str) -> dict:
    """Applique les deux critères du protocole à un couple (variable, indicateur).

    Spearman : corrélation sur les rangs, robuste aux valeurs extrêmes
    (une gare géante comme La Défense ne pèse pas plus qu'une autre).
    Écart des quartiles : différence de baisse moyenne entre le quart des gares
    au plus fort taux de cadres et le quart au plus faible.
    """
    # Spearman = corrélation classique (Pearson) calculée sur les RANGS.
    # On l'écrit ainsi pour ne pas installer scipy, que pandas réclame sinon.
    spearman = gares[variable].rank().corr(gares[indicateur].rank())
    quartile = pd.qcut(gares[variable], 4, labels=["Q1", "Q2", "Q3", "Q4"])
    moyennes_quartiles = gares.groupby(quartile, observed=True)[indicateur].mean()
    ecart = moyennes_quartiles["Q4"] - moyennes_quartiles["Q1"]
    # int() sur chaque critère AVANT l'addition : avec les booléens de numpy,
    # True + True vaut True (OU logique) et non 2, ce qui faussait le verdict.
    criteres = int(spearman >= SEUIL_SPEARMAN) + int(ecart >= SEUIL_ECART_POINTS)
    verdict = {2: "CONFIRMÉE", 1: "NUANCÉE", 0: "RÉFUTÉE"}[criteres]
    return {"variable": variable, "indicateur": indicateur, "spearman": spearman,
            "baisse_Q1_pct": moyennes_quartiles["Q1"], "baisse_Q4_pct": moyennes_quartiles["Q4"],
            "ecart_Q4_Q1_points": ecart, "verdict": verdict}


def main() -> None:
    """Enchaîne les étapes du protocole et affiche le verdict."""
    validations = charger_validations()
    print(f"Validations lues : {len(validations):,} lignes, du {validations['jour'].min():%d/%m/%Y} "
          f"au {validations['jour'].max():%d/%m/%Y}".replace(",", " "))

    # Étape 3 : titre retenu
    validations = validations[validations["categorie_titre"] == TITRE_RETENU]

    # Étape 2 : exclusion des jours particuliers, avec le décompte pour la transparence
    exclus_calendrier = jours_feries_et_ponts() | jours_vacances_zone_c()
    exclus_anormaux = jours_anormaux(validations) - exclus_calendrier
    tous_les_jours = set(validations["jour"].unique())
    print(f"Jours au total : {len(tous_les_jours)} | exclus (vacances, fériés, ponts) : "
          f"{len(tous_les_jours & exclus_calendrier)} | exclus (anormaux) : {len(exclus_anormaux)}")
    print("Jours anormaux :", sorted(j.strftime("%a %d/%m/%Y") for j in exclus_anormaux))
    validations = validations[~validations["jour"].isin(exclus_calendrier | exclus_anormaux)]
    nb_par_jour = validations.drop_duplicates("jour")["jour"].dt.day_of_week.value_counts().sort_index()
    print("Jours retenus par jour de semaine (0 = lundi) :", nb_par_jour.to_dict())

    # Étapes 4-5 : indicateur par gare, puis rattachement à la commune
    gares = indicateurs_par_gare(validations)
    referentiel = pd.read_csv(BRUT / "idfm_referentiel_arrets" / "zones-de-correspondance.csv",
                              sep=";", dtype=str, encoding="utf-8-sig")
    referentiel = referentiel.rename(columns={"zdcid": "id_zdc", "zdcname": "gare",
                                              "zdcpostalregion": "code_commune", "zdctown": "commune"})
    gares = gares.merge(referentiel[["id_zdc", "gare", "code_commune", "commune"]], on="id_zdc", how="left")
    nb_avant = len(gares)
    gares = gares[(gares["moyenne_jour_ouvre"] >= SEUIL_GARE_MIN) & gares["code_commune"].notna()]
    print(f"Gares : {nb_avant} au total, {len(gares)} retenues "
          f"(au moins {SEUIL_GARE_MIN} validations Navigo par jour et commune connue)")

    # Étapes 6-7 : part de cadres de la commune de la gare
    gares = gares.merge(parts_cadres_par_commune(), on="code_commune", how="left")
    sans_insee = gares["part_cadres_emplois_pct"].isna().sum()
    if sans_insee:
        print(f"Attention : {sans_insee} gares sans donnée INSEE (commune hors Île-de-France ?), écartées")
        gares = gares.dropna(subset=["part_cadres_emplois_pct"])

    # Verdict : variable principale (emplois) et contrôle (habitants), vendredi puis lundi
    evaluations = pd.DataFrame([
        evaluer(gares, variable, indicateur)
        for indicateur in ["baisse_vendredi_pct", "baisse_lundi_pct"]
        for variable in ["part_cadres_emplois_pct", "part_cadres_habitants_pct"]
    ])
    print(f"\nBaisse médiane du vendredi sur les gares retenues : {gares['baisse_vendredi_pct'].median():.1f} %")
    print("\n=== Verdict selon les critères fixés d'avance ===")
    print(evaluations.to_string(index=False, float_format=lambda x: f"{x:.2f}"))

    # Exemples concrets, utiles pour comprendre (pas pour prouver)
    colonnes = ["gare", "commune", "moyenne_mardi_jeudi", "baisse_vendredi_pct", "part_cadres_emplois_pct"]
    print("\n--- 8 gares où le vendredi baisse le plus ---")
    print(gares.nlargest(8, "baisse_vendredi_pct")[colonnes].to_string(index=False, float_format=lambda x: f"{x:.1f}"))
    print("\n--- 8 gares où le vendredi baisse le moins ---")
    print(gares.nsmallest(8, "baisse_vendredi_pct")[colonnes].to_string(index=False, float_format=lambda x: f"{x:.1f}"))

    dossier_sortie = RACINE / "resultats" / "04_h12"
    dossier_sortie.mkdir(parents=True, exist_ok=True)
    gares.to_csv(dossier_sortie / "baisse_vendredi_par_gare.csv", index=False, encoding="utf-8-sig")
    evaluations.to_csv(dossier_sortie / "verdict_h12.csv", index=False, encoding="utf-8-sig")
    print(f"\nCSV enregistrés dans : {dossier_sortie}")


if __name__ == "__main__":
    main()
