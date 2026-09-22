"""
Évalue rapport_anomalies.csv contre la vérité terrain (précision, rappel, rappel par type).

À lancer SEULEMENT après avoir écrit tes règles :  python src/evaluate.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main():
    G = pd.read_csv(ROOT / "data/raw/verite_terrain_anomalies.csv", dtype=str, keep_default_na=False)
    det = pd.read_csv(ROOT / "data/outputs/rapport_anomalies.csv", dtype=str, keep_default_na=False)

    signales, attendus = set(det["id_enrolement"]), set(G["id_enrolement"])
    tp, fp, fn = len(signales & attendus), len(signales - attendus), len(attendus - signales)
    precision = tp / (tp + fp) if tp + fp else 0.0
    rappel = tp / (tp + fn) if tp + fn else 0.0
    print(f"Précision {precision:.1%} | Rappel {rappel:.1%} | VP {tp} | FP {fp} | FN {fn}")

    # Les règles attendues ont-elles bien toutes été déclenchées pour chaque anomalie ?
    declenchees = det.groupby("id_enrolement")["code_regle"].apply(set).to_dict()
    G["ok"] = G.apply(
        lambda r: set(r["regles_attendues"].split(";")) <= declenchees.get(r["id_enrolement"], set()),
        axis=1)
    print("\nRappel par type d'anomalie :")
    print(G.groupby("type_anomalie")["ok"].mean().round(3).to_string())

    if fp:
        print("\nExemples de faux positifs (id_enrolement) :", sorted(signales - attendus)[:10])
    if fn:
        print("Exemples de faux négatifs (id_enrolement) :", sorted(attendus - signales)[:10])


if __name__ == "__main__":
    main()
