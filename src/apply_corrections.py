"""
Applique les corrections traçables aux anomalies détectées.

Principe : on ne corrige automatiquement que ce qu'une pièce justificative
permet de vérifier avec certitude (l'enrôlement et la pièce désignent le
même champ, et la pièce fait foi).

  - R01–R05, R08, R09 : corrigé avec la valeur correspondante de la pièce
                        (nom, prénoms, date de naissance, sexe, code commune,
                        nom de la mère)
  - R06, R07           : corrigé avec la date de naissance de la pièce
                        (ces deux règles portent sur le même champ que R03)
  - R10 (téléphone)    : JAMAIS corrigé automatiquement -> statut "à recontacter"
                        (aucune pièce justificative ne prouve un numéro de téléphone)
  - R11 (doublon)      : JAMAIS résolu automatiquement -> statut "à arbitrer"
                        (un ré-enrôlement peut être une fraude, une erreur,
                        ou une correction légitime : décision humaine requise)

L'enrôlement original n'est jamais écrasé : enrolements_corriges.csv est une
copie modifiée, et journal_corrections.csv trace chaque changement avant/après.

Usage :  python src/apply_corrections.py
"""
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "outputs"

CHAMP_SOURCE = {  # règle -> (champ de l'enrôlement, champ correspondant de la pièce)
    "R01": ("nom", "nom_p"),
    "R02": ("prenoms", "prenoms_p"),
    "R03": ("date_naissance", "date_naissance_p"),
    "R04": ("sexe", "sexe_p"),
    "R05": ("code_commune_naissance", "code_commune_naissance_p"),
    "R06": ("date_naissance", "date_naissance_p"),
    "R07": ("date_naissance", "date_naissance_p"),
    "R08": ("code_commune_naissance", "code_commune_naissance_p"),
    "R09": ("nom_mere", "nom_mere_p"),
}
STATUT_NON_CORRIGE = {
    "R10": "à recontacter (aucune pièce ne prouve le numéro)",
    "R11": "à arbitrer (doublon, décision d'un responsable)",
}


def lire(nom):
    return pd.read_csv(RAW / nom, dtype=str, keep_default_na=False)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    E, P = lire("enrolements.csv"), lire("pieces_justificatives.csv")
    A = pd.read_csv(OUT / "rapport_anomalies.csv", dtype=str, keep_default_na=False)

    m = E.merge(P, on="id_piece", how="left", suffixes=("", "_p"))
    m = m.set_index("id_enrolement")
    corrige = E.set_index("id_enrolement").copy()

    journal = []
    for _, a in A.iterrows():
        eid, code = a["id_enrolement"], a["code_regle"]
        if code in CHAMP_SOURCE:
            champ_e, champ_p = CHAMP_SOURCE[code]
            avant = m.at[eid, champ_e]
            apres = m.at[eid, champ_p]
            corrige.at[eid, champ_e] = apres
            journal.append({
                "id_enrolement": eid, "champ": champ_e, "valeur_avant": avant,
                "valeur_apres": apres, "source": f"pièce {m.at[eid, 'id_piece']}",
                "code_regle": code, "date_correction": date.today().isoformat(),
                "statut": "corrigé",
            })
        else:
            journal.append({
                "id_enrolement": eid, "champ": a["champ"], "valeur_avant": a["valeur_saisie"],
                "valeur_apres": "", "source": "", "code_regle": code,
                "date_correction": date.today().isoformat(),
                "statut": STATUT_NON_CORRIGE[code],
            })

    corrige.reset_index().to_csv(OUT / "enrolements_corriges.csv", index=False)
    pd.DataFrame(journal).to_csv(OUT / "journal_corrections.csv", index=False)

    J = pd.DataFrame(journal)
    print(f"Lignes du journal : {len(J)}")
    print(J["statut"].value_counts().to_string())
    print("\nPar règle :")
    print(J.groupby(["code_regle", "statut"]).size().to_string())


if __name__ == "__main__":
    main()
