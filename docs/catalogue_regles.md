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
