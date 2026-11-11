"""
preparer_destinations_categories.py : données du graphique de flux « de banlieue à banlieue » (page 2).

Validé par Melvyn le 2026-11-11 (canevas « Proposition p2 : un seul graphique de flux »), à la place de la carte en
5 nuances et des deux tableaux 8 x 8 par département, jugés trop techniques.

Deux calculs, sur les actifs qui habitent en banlieue (Île-de-France hors Paris), recensement 2023 :
  1. Où travaillent-ils, par catégorie (cadres, employés, ouvriers) ? Trois destinations qui font 100 % : leur
     propre département, un autre département de banlieue, Paris. Seuls les actifs qui travaillent en Île-de-France
     sont comptés (ceux qui travaillent hors région sont écartés : ils ne relèvent pas du réseau francilien).
  2. Dans combien de communes de banlieue plus de la moitié des employés et ouvriers travaillent-ils dans une autre
     commune de banlieue ? Même définition que la carte validée ; communes d'au moins 200 employés et ouvriers
     (seuil de prudence de l'INSEE). Contrôle : avec le seuil de 57 %, on doit retrouver les « 4 communes sur 5 »
     de la carte validée.

Entrée  : production/data/brut/insee_mobpro_2023/RP2023_mobpro.parquet
Sorties : application/donnees/destinations_categories.csv, banlieue_a_banlieue_compte.csv

Lancer depuis le dossier application/ : python preparation/preparer_destinations_categories.py
"""

from pathlib import Path

import pandas as pd

APPLICATION = Path(__file__).resolve().parents[1]
BRUT = APPLICATION.parent / "data" / "brut"
DONNEES = APPLICATION / "donnees"
CATEGORIES = {"3": "Cadres", "5": "Employés", "6": "Ouvriers"}   # groupes socioprofessionnels de l'INSEE
SEUIL_EFFECTIF = 200           # communes d'au moins 200 employés et ouvriers (seuil de prudence de l'INSEE)
SEUIL_MOITIE_PCT = 50          # « plus de la moitié »
SEUIL_CARTE_VALIDEE_PCT = 57   # contrôle : borne de classe de la carte validée (« 4 communes sur 5 »)


def main() -> None:
    """Calcule les parts par destination et le nombre de communes, avec le contrôle sur la carte validée."""
    actifs = pd.read_parquet(BRUT / "insee_mobpro_2023" / "RP2023_mobpro.parquet",
                             columns=["COMMUNE", "DCLT", "REGION", "REGLT", "GS", "IPONDI"],
                             filters=[("REGION", "==", "11")])
    banlieue = actifs[~actifs["COMMUNE"].str.startswith("75")].copy()

    # 1. Destinations par catégorie (actifs qui travaillent en Île-de-France)
    idf = banlieue[banlieue["REGLT"] == "11"]
    destination = pd.Series("Autre département", index=idf.index)
    destination[idf["DCLT"].str[:2] == idf["COMMUNE"].str[:2]] = "Leur département"
    destination[idf["DCLT"].str.startswith("75")] = "Paris"
    idf = idf.assign(destination=destination)
    lignes = []
    for code, nom in CATEGORIES.items():
        groupe = idf[idf["GS"] == code]
        parts = groupe.groupby("destination")["IPONDI"].sum() / groupe["IPONDI"].sum() * 100
        for dest in ["Leur département", "Autre département", "Paris"]:
            lignes.append({"categorie": nom, "destination": dest, "part_pct": round(parts[dest], 1)})
    resultat = pd.DataFrame(lignes)
    assert (resultat.groupby("categorie")["part_pct"].sum().sub(100).abs() < 0.2).all(), "les parts ne font pas 100 %"
    resultat.to_csv(DONNEES / "destinations_categories.csv", index=False, encoding="utf-8-sig")

    # 2. Communes où plus de la moitié des employés et ouvriers travaillent dans une autre commune de banlieue
    eo = banlieue[banlieue["GS"].isin(["5", "6"])].copy()
    eo["de_banlieue_a_banlieue"] = ((eo["REGLT"] == "11") & ~eo["DCLT"].str.startswith("75")
                                    & (eo["DCLT"] != eo["COMMUNE"]))
    par_commune = eo.groupby("COMMUNE").apply(
        lambda d: pd.Series({"effectif": d["IPONDI"].sum(),
                             "part_pct": 100 * d.loc[d["de_banlieue_a_banlieue"], "IPONDI"].sum() / d["IPONDI"].sum()}),
        include_groups=False)
    fiables = par_commune[par_commune["effectif"] >= SEUIL_EFFECTIF]
    controle = 100 * (fiables["part_pct"] > SEUIL_CARTE_VALIDEE_PCT).mean()
    assert 75 <= controle <= 85, f"contrôle : {controle:.1f} % au-dessus de 57 %, la carte validée disait 4 sur 5"
    compte = pd.DataFrame([{"communes": len(fiables),
                            "communes_plus_de_la_moitie": int((fiables["part_pct"] > SEUIL_MOITIE_PCT).sum())}])
    compte.to_csv(DONNEES / "banlieue_a_banlieue_compte.csv", index=False, encoding="utf-8-sig")
    print(resultat.pivot(index="categorie", columns="destination", values="part_pct").to_string())
    print(compte.to_string(index=False), f"| contrôle 57 % : {controle:.1f} %")


if __name__ == "__main__":
    main()
