# Dictionnaire de données

## Table `enrolements` (saisies des agents : 5 060 lignes)

| Champ | Type | Description | Obligatoire | Format / valeurs | Règle(s) associée(s) | Exemple |
|---|---|---|---|---|---|---|
| id_enrolement | texte | Identifiant unique de l'enrôlement | Oui | `ENR-######` | — | ENR-000123 |
| id_piece | texte | Identifiant de la pièce justificative présentée | Oui | `AN/PP/CC-######` | R01–R05, R11 | AN-001234 |
| type_piece | texte | Type de pièce présentée | Oui | ACTE_NAISSANCE, PASSEPORT, CARTE_CONSULAIRE | — | ACTE_NAISSANCE |
| agent_id | texte | Agent ayant réalisé l'enrôlement | Oui | `AG###` | — | AG007 |
| centre_enrolement | texte | Centre d'enrôlement | Oui | nom de ville | — | Djougou |
| date_enrolement | date | Date de l'enrôlement | Oui | AAAA-MM-JJ | R06, R07 | 2025-09-14 |
| nom | texte | Nom saisi par l'agent | Oui | majuscules | R01 | ADJOVI |
| prenoms | texte | Prénom(s) saisi(s) | Oui | texte libre | R02 | Codjo Fabrice |
| date_naissance | date | Date de naissance saisie | Oui | AAAA-MM-JJ | R03, R06, R07 | 1994-03-02 |
| sexe | texte | Sexe saisi | Oui | M, F | R04 | M |
| code_commune_naissance | texte | Code commune de naissance saisi | Oui | 4 chiffres | R05, R08 | 0102 |
| nom_mere | texte | Nom complet de la mère | Oui | texte libre | R09 | ADJOVI Espérance |
| telephone | texte | Numéro de téléphone (optionnel) | Non | `01` + 8 chiffres (après normalisation) | R10 | +229 01 62 88 05 20 |

## Table `pieces_justificatives` (source de vérité : 5 000 lignes)

Mêmes champs que `enrolements` pour `id_piece`, `type_piece`, `nom`, `prenoms`,
`date_naissance`, `sexe`, `code_commune_naissance`, `nom_mere` : ce sont les valeurs
de référence transcrites depuis la pièce présentée par le citoyen. Un `id_piece`
apparaît une seule fois dans cette table (contrairement à `enrolements`, où les
doublons de saisie sont possibles).

## Table `ref_communes` (référentiel simplifié, non officiel : 77 lignes)

| Champ | Type | Description | Exemple |
|---|---|---|---|
| code_commune | texte | Code à 4 chiffres | 0102 |
| commune | texte | Nom de la commune | Kandi |
| departement | texte | Département de rattachement | Alibori |

## Table `rapport_anomalies` (sortie de `run_checks.py` : 444 lignes)

| Champ | Description |
|---|---|
| id_enrolement, id_piece, agent_id, centre_enrolement, date_enrolement | copiés depuis `enrolements` |
| code_regle | R01 à R11 |
| champ | champ concerné par l'anomalie |
| valeur_saisie | valeur telle que saisie |
| valeur_attendue | valeur de la pièce (vide si non applicable, ex. R06–R11) |
| gravite | Haute / Critique / Moyenne / Basse |
