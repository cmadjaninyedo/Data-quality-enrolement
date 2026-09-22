"""
Règles de validation R01–R11 (spécification : docs/catalogue_regles.md).

Toutes les règles ont la même signature :  regle(m, ref) -> DataFrame d'anomalies
  - m   : enrolements JOINT pieces_justificatives (colonnes de la pièce suffixées "_p"),
          avec en plus la colonne `rang_piece` (0 = premier enrôlement de la pièce)
  - ref : référentiel des communes (colonnes code_commune, commune, departement)

Toutes les colonnes sont lues en texte (dtype=str) : ne pas oublier les zéros de tête
des codes commune et les champs vides ("" et non NaN).
"""
import re
import unicodedata

import pandas as pd

COLS = ["id_enrolement", "id_piece", "agent_id", "centre_enrolement", "date_enrolement"]


def normaliser(s: str) -> str:
    """Minuscules, sans accents, espaces multiples réduits : pour comparer sans faux positifs."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip().lower()


def normaliser_telephone(t: str) -> str:
    """Retire espaces/points/tirets et le préfixe international +229 / 00229."""
    t = re.sub(r"[ .\-]", "", t or "")
    t = re.sub(r"^(\+229|00229)", "", t)
    return t


def signaler(df, masque, code, champ, gravite, attendu=None):
    """Construit le tableau d'anomalies (format commun à toutes les règles)."""
    out = df.loc[masque, COLS].copy()
    out["code_regle"] = code
    out["champ"] = champ
    out["valeur_saisie"] = df.loc[masque, champ]
    out["valeur_attendue"] = attendu[masque] if attendu is not None else ""
    out["gravite"] = gravite
    return out


# --------------------------------------------------------------------------- #
# R01 — R05 : écarts entre la saisie et la pièce justificative
# --------------------------------------------------------------------------- #
def r01_ecart_nom(m, ref):
    """nom saisi != nom de la pièce (après normalisation)."""
    masque = m["nom"].map(normaliser) != m["nom_p"].map(normaliser)
    return signaler(m, masque, "R01", "nom", "Haute", attendu=m["nom_p"])


def r02_ecart_prenoms(m, ref):
    """prenoms saisis != pièce (après normalisation ; l'ordre des prénoms compte)."""
    masque = m["prenoms"].map(normaliser) != m["prenoms_p"].map(normaliser)
    return signaler(m, masque, "R02", "prenoms", "Haute", attendu=m["prenoms_p"])


def r03_ecart_date_naissance(m, ref):
    """date_naissance saisie != pièce (dates au format ISO AAAA-MM-JJ, comparaison texte valide)."""
    masque = m["date_naissance"] != m["date_naissance_p"]
    return signaler(m, masque, "R03", "date_naissance", "Haute", attendu=m["date_naissance_p"])


def r04_ecart_sexe(m, ref):
    """sexe saisi != pièce."""
    masque = m["sexe"] != m["sexe_p"]
    return signaler(m, masque, "R04", "sexe", "Haute", attendu=m["sexe_p"])


def r05_ecart_lieu_naissance(m, ref):
    """code_commune_naissance saisi != pièce."""
    masque = m["code_commune_naissance"] != m["code_commune_naissance_p"]
    return signaler(m, masque, "R05", "code_commune_naissance", "Haute",
                     attendu=m["code_commune_naissance_p"])


# --------------------------------------------------------------------------- #
# R06 — R07 : cohérence interne (indépendantes de la pièce)
# --------------------------------------------------------------------------- #
def r06_date_naissance_posterieure(m, ref):
    """date_naissance > date_enrolement (comparaison de dates ISO, valide lexicographiquement)."""
    masque = m["date_naissance"] > m["date_enrolement"]
    return signaler(m, masque, "R06", "date_naissance", "Critique")


def r07_age_invraisemblable(m, ref):
    """âge à l'enrôlement > 110 ans."""
    age = ((pd.to_datetime(m["date_enrolement"]) - pd.to_datetime(m["date_naissance"]))
           .dt.days / 365.25)
    masque = age > 110
    return signaler(m, masque, "R07", "date_naissance", "Critique")


# --------------------------------------------------------------------------- #
# R08 — R10 : référentiel, complétude, format
# --------------------------------------------------------------------------- #
def r08_code_commune_inexistant(m, ref):
    """code_commune_naissance absent de ref["code_commune"]."""
    masque = ~m["code_commune_naissance"].isin(ref["code_commune"])
    return signaler(m, masque, "R08", "code_commune_naissance", "Moyenne")


def r09_champ_obligatoire_manquant(m, ref):
    """nom_mere vide."""
    masque = m["nom_mere"].str.strip() == ""
    return signaler(m, masque, "R09", "nom_mere", "Moyenne")


def r10_telephone_invalide(m, ref):
    """Si renseigné : après normalisation, doit valoir '01' + 8 chiffres (règle du projet)."""
    non_vide = m["telephone"].str.strip() != ""
    valide = m["telephone"].map(normaliser_telephone).str.fullmatch(r"01\d{8}").fillna(False)
    masque = non_vide & ~valide
    return signaler(m, masque, "R10", "telephone", "Basse")


# --------------------------------------------------------------------------- #
# R11 : doublons
# --------------------------------------------------------------------------- #
def r11_doublon(m, ref):
    """Même id_piece enrôlé plusieurs fois : signaler les occurrences après la première."""
    masque = m["rang_piece"] > 0
    return signaler(m, masque, "R11", "id_piece", "Haute")


REGLES = [
    r01_ecart_nom, r02_ecart_prenoms, r03_ecart_date_naissance, r04_ecart_sexe,
    r05_ecart_lieu_naissance, r06_date_naissance_posterieure, r07_age_invraisemblable,
    r08_code_commune_inexistant, r09_champ_obligatoire_manquant, r10_telephone_invalide,
    r11_doublon,
]
