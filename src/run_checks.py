import sys
from pathlib import Path

import pandas as pd

import rules

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "outputs"


def lire(nom):
    return pd.read_csv(RAW / nom, dtype=str, keep_default_na=False)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    e, p, ref = lire("enrolements.csv"), lire("pieces_justificatives.csv"), lire("ref_communes.csv")

    m = e.merge(p, on="id_piece", how="left", suffixes=("", "_p"))
    m["rang_piece"] = (m.sort_values(["date_enrolement", "id_enrolement"])
                         .groupby("id_piece").cumcount())

    resultats, ignorees = [], []
    for regle in rules.REGLES:
        try:
            resultats.append(regle(m, ref))
        except NotImplementedError:
            ignorees.append(regle.__name__)

    if not resultats:
        sys.exit("Aucune règle implémentée.")

    anomalies = pd.concat(resultats, ignore_index=True)
    anomalies.to_csv(OUT / "rapport_anomalies.csv", index=False)

    print(f"Enrôlements contrôlés              : {len(m)}")
    print(f"Enrôlements avec anomalie(s)       : {anomalies['id_enrolement'].nunique()}")
    print(f"Anomalies détectées (toutes règles): {len(anomalies)}")
    print(anomalies.groupby("code_regle").size().rename("anomalies").to_string())
    if ignorees:
        print(f"\nRègles non implémentées (ignorées) : {', '.join(ignorees)}")


if __name__ == "__main__":
    main()
