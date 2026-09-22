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

| Statut | Nombre |
|---|---:|
| Corrigé (à partir de la pièce justificative) | 278 |
| À arbitrer (doublon) | 60 |
| À recontacter (téléphone non vérifiable) | 46 |
| À compléter (champ manquant) | 34 |
| À corriger manuellement (code commune hors référentiel) | 26 |

Détail dans `data/outputs/journal_corrections.csv`.

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
