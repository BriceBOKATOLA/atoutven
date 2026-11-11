"""
preparer_liaisons_banlieue.py : données du bloc « travailler dans un autre département de banlieue » (page 2).

Validé par Melvyn le 2026-11-11 (canevas « Proposition p2 : ligne « plus on s'éloigne » + tableau des départs »), à la
place des tableaux 8 x 8 par département, jugés trop techniques.

Population : employés et ouvriers qui habitent en banlieue et travaillent dans un AUTRE département de banlieue
(Paris exclu des deux côtés), recensement 2023. Chaque trajet est classé selon les deux départements :
  - « petite » : entre deux départements de petite couronne (92, 93, 94) ;
  - « mixte »  : entre un département de petite couronne et un de grande couronne ;
  - « grande » : entre deux départements de grande couronne (77, 78, 91, 95).
Pour chaque type : nombre de trajets et part faite en voiture (variable TRANS = 5, comme dans les scripts 06 et 07).

Entrée  : production/data/brut/insee_mobpro_2023/RP2023_mobpro.parquet
Sortie  : application/donnees/liaisons_banlieue.csv

Lancer depuis le dossier application/ : python preparation/preparer_liaisons_banlieue.py
"""

from pathlib import Path

import pandas as pd

APPLICATION = Path(__file__).resolve().parents[1]
BRUT = APPLICATION.parent / "data" / "brut"
PETITE_COURONNE = {"92", "93", "94"}
CODE_VOITURE = "5"
ORDRE = ["petite", "mixte", "grande"]   # de Paris vers l'extérieur


def type_liaison(dep_a: str, dep_b: str) -> str:
    """Type de liaison entre deux départements de banlieue (petite, mixte ou grande couronne)."""
    nb_petite = (dep_a in PETITE_COURONNE) + (dep_b in PETITE_COURONNE)
    return {2: "petite", 1: "mixte", 0: "grande"}[nb_petite]


def main() -> None:
    """Calcule la part de la voiture par type de liaison et contrôle que les trois types couvrent tous les trajets."""
    actifs = pd.read_parquet(BRUT / "insee_mobpro_2023" / "RP2023_mobpro.parquet",
                             columns=["COMMUNE", "DCLT", "REGION", "REGLT", "GS", "TRANS", "IPONDI"],
                             filters=[("REGION", "==", "11"), ("REGLT", "==", "11")])
    eo = actifs[actifs["GS"].isin(["5", "6"]) & ~actifs["COMMUNE"].str.startswith("75")
                & ~actifs["DCLT"].str.startswith("75")]
    autre_dep = eo[eo["COMMUNE"].str[:2] != eo["DCLT"].str[:2]].copy()
    autre_dep["type"] = [type_liaison(a[:2], b[:2]) for a, b in zip(autre_dep["COMMUNE"], autre_dep["DCLT"])]
    autre_dep["voiture"] = autre_dep["TRANS"] == CODE_VOITURE
    resultat = autre_dep.groupby("type").apply(
        lambda d: pd.Series({"trajets": d["IPONDI"].sum(),
                             "voiture_pct": 100 * d.loc[d["voiture"], "IPONDI"].sum() / d["IPONDI"].sum()}),
        include_groups=False).reindex(ORDRE)
    assert abs(resultat["trajets"].sum() - autre_dep["IPONDI"].sum()) < 1e-6, "des trajets ne sont classés dans aucun type"
    resultat.round(1).reset_index().to_csv(APPLICATION / "donnees" / "liaisons_banlieue.csv", index=False,
                                           encoding="utf-8-sig")
    print(resultat.round(1).to_string())


if __name__ == "__main__":
    main()
