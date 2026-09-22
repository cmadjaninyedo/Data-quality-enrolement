# Fiche de bonnes pratiques de saisie

Public : agents enrôleurs. Objectif : réduire les anomalies dès la saisie.

## 1. Recopiez le nom et les prénoms exactement comme sur la pièce
*Pourquoi : règle R01+R02, 96 anomalies (22 % du total). C'est la première cause
d'anomalie détectée.*

## 2. Vérifiez toujours l'ordre jour/mois de la date de naissance
Une inversion (ex. 03/04 saisi pour 04/03) est l'erreur la plus fréquente sur la date
de naissance.
*Pourquoi : règle R03, 78 anomalies (18 % du total, la règle la plus fréquente).*

## 3. Une date de naissance ne peut jamais être postérieure à la date du jour
Si le champ l'accepte, c'est une erreur de saisie à corriger immédiatement.
*Pourquoi : règle R06, gravité critique.*

## 4. Vérifiez le code commune sur la liste officielle, jamais de mémoire
Un code inexistant (ex. 0000, 9999) bloque tout traitement automatisé ultérieur.
*Pourquoi : règle R08, 26 anomalies.*

## 5. Ne laissez jamais un champ obligatoire vide, y compris le nom de la mère
Si l'information n'est réellement pas disponible, signalez-le explicitement plutôt que
de laisser le champ vide.
*Pourquoi : règle R09, 34 anomalies.*

## 6. Avant d'enrôler une personne, vérifiez qu'elle n'est pas déjà enrôlée
Une nouvelle pièce présentée pour une personne déjà dans le système doit être signalée
à un responsable plutôt que ré-enrôlée directement.
*Pourquoi : règle R11, 60 cas détectés — la deuxième anomalie la plus fréquente.*

## 7. Vérifiez le format du numéro de téléphone avant validation
Le format attendu est `01` suivi de 8 chiffres.
*Pourquoi : règle R10, 46 anomalies.*
