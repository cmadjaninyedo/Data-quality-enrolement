"""
Les mêmes règles en SQL (DuckDB), pour validation croisée avec rules.py (pandas).

Usage :  python src/rules_sql.py
"""
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"


def main():
    con = duckdb.connect()
    con.execute(f"CREATE VIEW e AS SELECT * FROM read_csv_auto('{RAW/'enrolements.csv'}', all_varchar=true)")
    con.execute(f"CREATE VIEW p AS SELECT * FROM read_csv_auto('{RAW/'pieces_justificatives.csv'}', all_varchar=true)")
    con.execute(f"CREATE VIEW c AS SELECT * FROM read_csv_auto('{RAW/'ref_communes.csv'}', all_varchar=true)")

    # R08 : code commune absent du référentiel
    r08 = con.execute("""
        SELECT e.id_enrolement
        FROM e LEFT JOIN c ON e.code_commune_naissance = c.code_commune
        WHERE c.code_commune IS NULL
    """).df()

    # R11 : doublons (occurrences après la première, ordonnées par date d'enrôlement)
    r11 = con.execute("""
        SELECT id_enrolement FROM (
            SELECT *, ROW_NUMBER() OVER (
                PARTITION BY id_piece ORDER BY date_enrolement, id_enrolement
            ) AS rang
            FROM e
        ) WHERE rang > 1
    """).df()

    # R06 : date de naissance postérieure à la date d'enrôlement
    r06 = con.execute("""
        SELECT id_enrolement FROM e WHERE date_naissance > date_enrolement
    """).df()

    print(f"R08 (SQL) : {len(r08)} anomalies")
    print(f"R11 (SQL) : {len(r11)} anomalies")
    print(f"R06 (SQL) : {len(r06)} anomalies")

    # Comparaison avec les résultats pandas
    import pandas as pd
    A = pd.read_csv(ROOT / "data/outputs/rapport_anomalies.csv", dtype=str)
    for code, df_sql in [("R08", r08), ("R11", r11), ("R06", r06)]:
        ids_pandas = set(A.loc[A.code_regle == code, "id_enrolement"])
        ids_sql = set(df_sql["id_enrolement"])
        print(f"{code}: pandas={len(ids_pandas)} sql={len(ids_sql)} "
              f"identiques={ids_pandas == ids_sql}")


if __name__ == "__main__":
    main()
