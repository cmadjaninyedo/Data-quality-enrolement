# Catalogue des règles de validation

| Code | Nom | Objectif / logique | Gravité | Anomalies détectées | Exemple réel |
|---|---|---|---|---|---|
| R01 | ECART_NOM | Nom saisi ≠ nom de la pièce (après normalisation) | Haute | 53 | `nom` saisi "AdJOVl" vs pièce "ADJOVI" |
| R02 | ECART_PRENOMS | Prénoms saisis ≠ pièce (l'ordre compte) | Haute | 43 | prénoms inversés par rapport à la pièce |
| R03 | ECART_DATE_NAISSANCE | Date de naissance saisie ≠ pièce | Haute | 78 | jour/mois inversés (ex. 03/04 saisi pour 04/03) |
| R04 | ECART_SEXE | Sexe saisi ≠ pièce | Haute | 25 | M saisi pour F sur la pièce |
| R05 | ECART_LIEU_NAISSANCE | Code commune de naissance saisi ≠ pièce | Haute | 57 | code d'une autre commune saisi |
| R06 | DATE_NAISSANCE_POSTERIEURE | Date de naissance > date d'enrôlement | Critique | 12 | naissance saisie après la date d'enrôlement |
| R07 | AGE_INVRAISEMBLABLE | Âge à l'enrôlement > 110 ans | Critique | 10 | date de naissance saisie dans les années 1880–1905 |
| R08 | CODE_COMMUNE_INEXISTANT | Code commune absent du référentiel | Moyenne | 26 | code `0000` ou `9999` saisi |
| R09 | CHAMP_OBLIGATOIRE_MANQUANT | `nom_mere` vide | Moyenne | 34 | champ laissé vide à la saisie |
| R10 | TELEPHONE_INVALIDE | Format invalide après normalisation (`01` + 8 chiffres) | Basse | 46 | ancien format à 8 chiffres, préfixe erroné |
| R11 | DOUBLON | Même `id_piece` enrôlé plusieurs fois | Haute | 60 | ré-enrôlement dans un autre centre |

**Total : 444 anomalies sur 396 enrôlements** (certains enrôlements déclenchent plusieurs règles).

## Normalisation appliquée avant comparaison

- **Texte** (nom, prénoms) : suppression des accents, mise en minuscules, réduction des
  espaces multiples à un seul, avant toute comparaison. Sans cette étape, des variantes
  bénignes (casse, accents, espaces) auraient été signalées à tort.
- **Téléphone** : suppression des espaces, points, tirets, et du préfixe international
  `+229` / `00229`, avant de vérifier le format `01` + 8 chiffres.
- **Dates** : comparées directement en texte ISO (AAAA-MM-JJ), qui se compare
  correctement en ordre lexicographique.

## Validation croisée

Les règles R06, R08 et R11 ont été réécrites en SQL (DuckDB, voir `src/rules_sql.py`)
et produisent exactement les mêmes ensembles d'identifiants que la version pandas
(`src/rules.py`), ce qui confirme l'absence d'erreur d'implémentation d'un côté ou de
l'autre.

## Base des corrections automatiques (src/apply_corrections.py)

| Règle | Corrigée automatiquement ? | Base |
|---|---|---|
| R01–R07, R09 | Oui | Valeur correspondante de la pièce (comparaison directe saisie/pièce, la pièce fait foi) |
| R08 | Oui, sous condition | Valeur de la pièce, **seulement si ce code est lui-même valide dans le référentiel** (c'est un problème de conformité référentielle, pas un simple écart texte : la pièce elle-même pourrait contenir un code invalide) |
| R10 | Non | Aucune pièce ne prouve un numéro de téléphone -> statut "à recontacter" |
| R11 | Non | Un doublon peut être une fraude, une erreur de saisie ou une correction légitime -> statut "à arbitrer" (décision humaine) |

**Bilan réel (`journal_corrections.csv`) : 338 anomalies corrigées automatiquement, 106 laissées à une action humaine** (46 "à recontacter", 60 "à arbitrer").

## Pourquoi les enrôlements avec anomalie(s) (396) sont inférieurs aux anomalies détectées (444)

48 enrôlements cumulent deux règles déclenchées simultanément (348 en ont une seule) :
348×1 + 48×2 = 444. Les combinaisons observées :

| Combinaison | Cas | Explication |
|---|---:|---|
| R05 + R08 | 26 | Un code commune erroné est presque toujours aussi absent du référentiel : les deux règles regardent le même champ sous deux angles différents |
| R03 + R06 | 12 | Une date de naissance postérieure à l'enrôlement est mécaniquement aussi différente de la pièce |
| R03 + R07 | 10 | Un âge invraisemblable (> 110 ans) est mécaniquement aussi différent de la pièce |
