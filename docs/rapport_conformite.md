# Rapport de conformité : enrôlements du 2025-01-01 au 2026-06-30

> Données 100 % synthétiques. Ce rapport illustre la démarche, pas un système réel.

## 1. Indicateurs clés

| Indicateur | Valeur |
|---|---|
| Enrôlements contrôlés | 5 060 |
| Enrôlements avec anomalie(s) | 396 (7,8 %) |
| Taux de conformité | 92,2 % |
| Anomalies détectées (toutes règles) | 444 |
| Anomalies critiques (R06 + R07) | 22 |

**Note sur l'écart 396 / 444 :** 48 enrôlements cumulent deux règles déclenchées
simultanément (348 × 1 règle + 48 × 2 règles = 444). Le détail est documenté dans
`docs/catalogue_regles.md`.

### Matrice de confusion (niveau enrôlement), lecture métier

| | Anomalie réelle | Pas d'anomalie |
|---|---:|---:|
| **Signalé** | VP = 396 | FP = 0 |
| **Non signalé** | FN = 0 | VN = 4 664 |

- **Faux positif** (dossier sain signalé à tort) : coût = temps agent perdu à revérifier un
  dossier déjà conforme.
- **Faux négatif** (anomalie réelle non détectée) : coût = une donnée erronée entre dans le
  registre, avec un impact potentiel sur l'identité légale d'une personne — un risque plus
  grave qu'un faux positif dans ce contexte, ce qui justifie de préférer des règles
  légèrement plus strictes en production, quitte à générer davantage de faux positifs.

**Limite méthodologique importante :** ce score de 100 % / 100 % est attendu et non
significatif en soi : les règles ont été conçues à partir de la même logique que celle
ayant servi à injecter les anomalies dans ce jeu de données synthétique. Sur des données
réelles, un tel score ne se reproduirait jamais — les erreurs de saisie réelles prennent
des formes que des règles, même bien conçues, ne couvrent jamais entièrement. En
production, la performance se mesurerait par échantillonnage et revue humaine, pas par
comparaison à une vérité terrain connue.

## 2. Répartition par type d'anomalie

| Règle | Nom | Nombre | Part |
|---|---|---:|---:|
| R03 | ECART_DATE_NAISSANCE | 78 | 17,6 % |
| R11 | DOUBLON | 60 | 13,5 % |
| R05 | ECART_LIEU_NAISSANCE | 57 | 12,8 % |
| R01 | ECART_NOM | 53 | 11,9 % |
| R10 | TELEPHONE_INVALIDE | 46 | 10,4 % |
| R02 | ECART_PRENOMS | 43 | 9,7 % |
| R09 | CHAMP_OBLIGATOIRE_MANQUANT | 34 | 7,7 % |
| R08 | CODE_COMMUNE_INEXISTANT | 26 | 5,9 % |
| R04 | ECART_SEXE | 25 | 5,6 % |
| R06 | DATE_NAISSANCE_POSTERIEURE | 12 | 2,7 % |
| R07 | AGE_INVRAISEMBLABLE | 10 | 2,3 % |

Les écarts entre saisie et pièce justificative (R01–R05) représentent à eux seuls
58 % des anomalies détectées.

## 3. Agents et centres à accompagner

Le taux médian d'anomalies par agent est de 7,2 %. Deux agents dépassent nettement
ce seuil :

| Agent | Taux d'anomalies | Erreur dominante |
|---|---:|---|
| AG007 | 20,9 % | Écarts de date de naissance (R03) |
| AG023 | 20,8 % | Écarts de nom (R01) |

Les centres de Djougou (11,8 %) et Dassa-Zoumè (11,2 %) affichent les taux les plus
élevés, mais l'analyse suggère que cet écart est surtout porté par la présence de ces
deux agents dans ces centres plutôt qu'un problème structurel propre au centre.

## 4. Corrections effectuées / en attente

| Statut | Nombre | Base de la décision |
|---|---:|---|
| Corrigé automatiquement (R01–R09) | 338 | Valeur correspondante de la pièce justificative ; pour R08, seulement si le code de la pièce est lui-même valide dans le référentiel |
| À arbitrer (R11, doublon) | 60 | Un ré-enrôlement peut être une fraude, une erreur ou une correction légitime : décision humaine requise |
| À recontacter (R10, téléphone) | 46 | Aucune pièce ne prouve un numéro de téléphone |

Détail ligne par ligne (avant/après/source) dans `data/outputs/journal_corrections.csv`.

## 5. Recommandations

1. **Accompagnement individuel ciblé** pour AG007 (relecture des dates de naissance)
   et AG023 (recopie exacte des noms), qui concentrent 12,4 % des anomalies pour 5 %
   des enrôlements.
2. **Contrôle bloquant à la saisie** pour R06 et R08 : ce sont des erreurs à 100 %
   évitables par une validation immédiate (date future refusée, code commune vérifié
   contre le référentiel en temps réel).
3. **Procédure de revue humaine pour les doublons (R11)** plutôt qu'une correction
   automatique : un ré-enrôlement peut aussi être une correction légitime d'un dossier
   existant, une suppression automatique serait risquée.

## 6. Limites de l'analyse

- Données entièrement synthétiques : les taux et effectifs ci-dessus n'ont aucune
  valeur en dehors de ce projet d'entraînement.
- La vérité terrain n'existe pas dans un système réel : en production, la précision
  se mesure par échantillonnage et revue humaine, pas par comparaison directe.
- Le référentiel de communes est simplifié (77 communes) et non officiel.
- Le format de validation du téléphone (règle R10) est une convention du projet, pas
  une règle métier réelle de l'ANIP.
