# Contrôle qualité de données d'enrôlement : projet sur données synthétiques

Mini-projet de data quality : détection, documentation et correction traçable d'anomalies
de saisie en comparant des enrôlements à leurs pièces justificatives.

> **Données 100 % synthétiques** (aucune donnée personnelle réelle). Référentiel des communes simplifié, non officiel. Aucun système réel n'est reproduit.

## Problématique
Comment détecter rapidement les écarts entre saisies et pièces justificatives, comprendre
leur origine et réduire les erreurs dès la saisie ?

## Ce que fait le projet
- 11 règles de validation (Python/pandas, avec 3 règles rejouées et validées croisées en SQL/DuckDB) : cohérence pièce/saisie, cohérence interne, référentiel, complétude, format, doublons
- Évaluation contre une vérité terrain : **précision 100 %, rappel 100 %** (396 vrais positifs, 0 faux positif, 0 faux négatif)
- Analyse des typologies d'erreurs par règle, agent, centre et type de pièce
- Corrections traçables (journal avant / après / source), sans écrasement des données d'origine
- Dictionnaire de données, catalogue de règles, fiche de bonnes pratiques, rapport de conformité

## Résultats clés
- **5 060 enrôlements contrôlés, 396 avec anomalie(s) (7,8 %), 444 anomalies détectées** (certains enrôlements déclenchent plusieurs règles)
- Les écarts entre saisie et pièce (noms, prénoms, dates, sexe, lieu de naissance) représentent 58 % des anomalies
- Deux agents sur 40 concentrent des taux d'anomalies de 20,9 % et 20,8 %, contre 7,2 % de médiane, chacun avec un type d'erreur dominant différent (dates de naissance vs noms)
- 278 anomalies corrigées automatiquement à partir de la pièce justificative ; 166 nécessitent une action humaine (doublon, champ manquant, téléphone, code commune)

## Limites
- Données synthétiques : les résultats ne reflètent aucun système réel, en particulier celui de l'ANIP.
- La vérité terrain n'existe pas dans la réalité : en pratique, la précision se mesure par échantillonnage et revue humaine.
- Règles simplifiées (ex. format de téléphone fixé par convention du projet).

## Structure
```
data/raw/        4 CSV (pièces, enrôlements, référentiel, vérité terrain)
data/outputs/    résultats (rapport d'anomalies, enrôlements corrigés, journal des corrections)
src/             rules.py, run_checks.py, evaluate.py, apply_corrections.py, rules_sql.py
notebooks/       profilage et analyse (rempli, avec résultats et graphique)
docs/            dictionnaire de données, catalogue de règles, fiche de bonnes pratiques, rapport de conformité
```

## Lancer le projet
```bash
python -m venv .venv && source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install -r requirements.txt
python generate_data.py        # optionnel : régénère les données (même graine = mêmes données)
python src/run_checks.py       # détecte les anomalies -> data/outputs/rapport_anomalies.csv
python src/evaluate.py         # précision / rappel contre la vérité terrain
python src/apply_corrections.py  # corrections traçables -> data/outputs/
python src/rules_sql.py        # bonus : validation croisée SQL (DuckDB)
```
