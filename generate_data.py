#!/usr/bin/env python3
"""
Génère un jeu de données 100 % SYNTHÉTIQUE pour un mini-projet de contrôle qualité
de données d'enrôlement (registre d'état civil fictif).

AUCUNE donnée réelle : tous les noms, dates, numéros et codes sont fabriqués au hasard.
Le référentiel des communes est SIMPLIFIÉ et ne doit pas être présenté comme officiel.

Fichiers produits dans data/raw/ :
  - pieces_justificatives.csv     : données transcrites des pièces (acte de naissance, etc.)
                                    -> la SOURCE DE VÉRITÉ pour la comparaison
  - enrolements.csv               : saisies numériques faites par les agents (avec erreurs)
  - ref_communes.csv              : référentiel des communes (code, commune, département)
  - verite_terrain_anomalies.csv  : liste des anomalies injectées (pour évaluer TES règles)
                                    -> à ne consulter QU'APRÈS avoir écrit tes règles

Usage :  python generate_data.py
"""
import csv
import random
import re
import unicodedata
from datetime import date, timedelta
from pathlib import Path

SEED = 2026
N_PIECES = 5000            # nombre de pièces (personnes) distinctes
N_DOUBLONS = 60            # ré-enrôlements de la même pièce
DATE_DEBUT = date(2025, 1, 1)
DATE_FIN = date(2026, 6, 30)
P_ERREUR = 0.06            # taux d'erreur de base par enrôlement
P_ERREUR_RISQUE = 0.22     # taux d'erreur pour les agents à risque
# Deux agents ont un taux d'erreur élevé, avec un type d'erreur dominant.
# (NE PAS LIRE avant d'avoir fait l'analyse par agent : c'est la réponse.)
AGENTS_A_RISQUE = {"AG007": "ECART_DATE_NAISSANCE", "AG023": "ECART_NOM"}
OUT = Path("data/raw")

random.seed(SEED)

# --------------------------------------------------------------------------- #
# Référentiel simplifié des communes (12 départements, 77 communes)
# --------------------------------------------------------------------------- #
DEPARTEMENTS = {
    "Alibori": ["Banikoara", "Gogounou", "Kandi", "Karimama", "Malanville", "Ségbana"],
    "Atacora": ["Boukoumbé", "Cobly", "Kérou", "Kouandé", "Matéri", "Natitingou",
                "Péhunco", "Tanguiéta", "Toucountouna"],
    "Atlantique": ["Abomey-Calavi", "Allada", "Kpomassè", "Ouidah", "Sô-Ava", "Toffo",
                   "Tori-Bossito", "Zè"],
    "Borgou": ["Bembèrèkè", "Kalalé", "N'Dali", "Nikki", "Parakou", "Pèrèrè", "Sinendé",
               "Tchaourou"],
    "Collines": ["Bantè", "Dassa-Zoumè", "Glazoué", "Ouèssè", "Savalou", "Savè"],
    "Couffo": ["Aplahoué", "Djakotomey", "Dogbo", "Klouékanmè", "Lalo", "Toviklin"],
    "Donga": ["Bassila", "Copargo", "Djougou", "Ouaké"],
    "Littoral": ["Cotonou"],
    "Mono": ["Athiémé", "Bopa", "Comè", "Grand-Popo", "Houéyogbé", "Lokossa"],
    "Ouémé": ["Adjarra", "Adjohoun", "Aguégués", "Akpro-Missérété", "Avrankou", "Bonou",
              "Dangbo", "Porto-Novo", "Sèmè-Kpodji"],
    "Plateau": ["Adja-Ouèrè", "Ifangni", "Kétou", "Pobè", "Sakété"],
    "Zou": ["Abomey", "Agbangnizoun", "Bohicon", "Covè", "Djidja", "Ouinhi", "Zagnanado",
            "Za-Kpota", "Zogbodomey"],
}
COMMUNES = []  # (code, commune, departement)
for i, (dep, comms) in enumerate(DEPARTEMENTS.items(), start=1):
    for j, c in enumerate(comms, start=1):
        COMMUNES.append((f"{i:02d}{j:02d}", c, dep))
CODES_VALIDES = [c[0] for c in COMMUNES]

CENTRES = ["Cotonou", "Abomey-Calavi", "Porto-Novo", "Parakou", "Bohicon", "Natitingou",
           "Djougou", "Lokossa", "Ouidah", "Kandi", "Dassa-Zoumè", "Aplahoué"]
AGENTS = [f"AG{i:03d}" for i in range(1, 41)]
CENTRE_AGENT = {a: CENTRES[i % len(CENTRES)] for i, a in enumerate(AGENTS)}

NOMS = ["Adjovi", "Agbodjan", "Hounkpatin", "Dossou", "Houngbo", "Gbaguidi", "Ahouansou",
        "Sossou", "Kpadonou", "Tossou", "Akpovi", "Zannou", "Agossou", "Hounsou", "Assogba",
        "Amoussou", "Fassinou", "Adande", "Alladaye", "Koukpaki", "Sagbo", "Ahoyo", "Bio",
        "Yarou", "Tchibozo", "Souley", "Idrissou", "Chabi", "Osseni", "Boni", "Codjia",
        "Dansou", "Glele", "Houessou", "Kiki", "Lokonon", "Mensah", "Nouatin", "Quenum",
        "Togbe", "Vodounon", "Zinsou"]
PRENOMS_M = ["Koffi", "Codjo", "Mahougnon", "Fabrice", "Rodrigue", "Ghislain", "Romaric",
             "Gildas", "Fidèle", "Brice", "Arnaud", "Ulrich", "Yves", "Moussa", "Ibrahim",
             "Comlan", "Rachid", "Bienvenu", "Serge", "Justin"]
PRENOMS_F = ["Sènami", "Espérance", "Judith", "Prudence", "Carine", "Sylvie", "Nadège",
             "Rosine", "Chimène", "Estelle", "Aïcha", "Rachidatou", "Fatoumata", "Salamatou",
             "Sèmèvo", "Ayaba", "Bernice", "Gisèle", "Flore", "Mariam"]


# --------------------------------------------------------------------------- #
# Utilitaires
# --------------------------------------------------------------------------- #
def sans_accents(s):
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c))


def normaliser(s):
    return re.sub(r"\s+", " ", sans_accents(s)).strip().lower()


def muter_texte(s):
    """Fait une faute de saisie réaliste, garantie différente après normalisation."""
    lettres = "abcdefghijklmnopqrstuvwxyz"
    for _ in range(30):
        t = list(s)
        op = random.choice(["remplacer", "supprimer", "permuter", "doubler"])
        i = random.randrange(len(t))
        if op == "remplacer" and t[i].isalpha():
            n = random.choice(lettres)
            t[i] = n if t[i].islower() else n.upper()
        elif op == "supprimer" and len(t) > 3:
            del t[i]
        elif op == "permuter" and i < len(t) - 1:
            t[i], t[i + 1] = t[i + 1], t[i]
        elif op == "doubler":
            t.insert(i, t[i])
        res = "".join(t)
        if normaliser(res) != normaliser(s):
            return res
    return s + "x"


def date_aleatoire(debut, fin):
    return debut + timedelta(days=random.randint(0, (fin - debut).days))


def telephone_valide():
    return "01" + "".join(random.choice("0123456789") for _ in range(8))


# --------------------------------------------------------------------------- #
# Génération des pièces et des enrôlements « propres »
# --------------------------------------------------------------------------- #
def generer_base():
    pieces, enrol = [], []
    for i in range(1, N_PIECES + 1):
        type_piece = random.choices(
            ["ACTE_NAISSANCE", "PASSEPORT", "CARTE_CONSULAIRE"], [70, 15, 15])[0]
        prefixe = {"ACTE_NAISSANCE": "AN", "PASSEPORT": "PP", "CARTE_CONSULAIRE": "CC"}[type_piece]
        sexe = random.choice(["M", "F"])
        prenoms = " ".join(random.sample(PRENOMS_M if sexe == "M" else PRENOMS_F,
                                         random.choice([1, 1, 2])))
        d_enrol = date_aleatoire(DATE_DEBUT, DATE_FIN)
        age = int(random.triangular(0, 90, 25))
        d_naiss = d_enrol - timedelta(days=age * 365 + random.randint(0, 364))
        piece = {
            "id_piece": f"{prefixe}-{i:06d}",
            "type_piece": type_piece,
            "nom": random.choice(NOMS).upper(),
            "prenoms": prenoms,
            "date_naissance": d_naiss.isoformat(),
            "sexe": sexe,
            "code_commune_naissance": random.choice(CODES_VALIDES),
            "nom_mere": f"{random.choice(NOMS).upper()} {random.choice(PRENOMS_F)}",
        }
        agent = random.choice(AGENTS)
        e = {
            "id_piece": piece["id_piece"],
            "type_piece": type_piece,
            "agent_id": agent,
            "centre_enrolement": CENTRE_AGENT[agent],
            "date_enrolement": d_enrol.isoformat(),
            "nom": piece["nom"],
            "prenoms": piece["prenoms"],
            "date_naissance": piece["date_naissance"],
            "sexe": piece["sexe"],
            "code_commune_naissance": piece["code_commune_naissance"],
            "nom_mere": piece["nom_mere"],
            "telephone": telephone_valide() if random.random() > 0.12 else "",
            "_gt": None,
        }
        pieces.append(piece)
        enrol.append(e)
    return pieces, enrol


# --------------------------------------------------------------------------- #
# Injection d'anomalies (une seule par enregistrement)
# --------------------------------------------------------------------------- #
POIDS_TYPES = [
    ("ECART_NOM", 14), ("ECART_PRENOMS", 10), ("ECART_DATE_NAISSANCE", 14),
    ("ECART_SEXE", 6), ("ECART_LIEU_NAISSANCE", 10), ("DATE_NAISSANCE_POSTERIEURE", 5),
    ("AGE_INVRAISEMBLABLE", 4), ("CODE_COMMUNE_INEXISTANT", 8),
    ("CHAMP_OBLIGATOIRE_MANQUANT", 12), ("TELEPHONE_INVALIDE", 12),
]
REGLES_ATTENDUES = {
    "ECART_NOM": "R01", "ECART_PRENOMS": "R02", "ECART_DATE_NAISSANCE": "R03",
    "ECART_SEXE": "R04", "ECART_LIEU_NAISSANCE": "R05",
    "DATE_NAISSANCE_POSTERIEURE": "R03;R06", "AGE_INVRAISEMBLABLE": "R03;R07",
    "CODE_COMMUNE_INEXISTANT": "R05;R08", "CHAMP_OBLIGATOIRE_MANQUANT": "R09",
    "TELEPHONE_INVALIDE": "R10",
}


def choisir_type(agent):
    if agent in AGENTS_A_RISQUE and random.random() < 0.5:
        return AGENTS_A_RISQUE[agent]
    types, poids = zip(*POIDS_TYPES)
    return random.choices(types, poids)[0]


def decaler_date(d_naiss, d_enrol):
    """Erreur de saisie plausible sur une date de naissance."""
    if d_naiss.day <= 12 and d_naiss.day != d_naiss.month and random.random() < 0.4:
        cand = date(d_naiss.year, d_naiss.day, d_naiss.month)  # jour/mois inversés
    else:
        k = random.choice([1, 2, 3, 10, 30, 365])
        cand = d_naiss + timedelta(days=k)
        if cand >= d_enrol:
            cand = d_naiss - timedelta(days=k)
    return cand


def injecter(e, piece):
    t = choisir_type(e["agent_id"])
    d_naiss = date.fromisoformat(piece["date_naissance"])
    d_enrol = date.fromisoformat(e["date_enrolement"])
    champ = valeur_attendue = None
    if t == "ECART_NOM":
        champ, valeur_attendue = "nom", piece["nom"]
        e["nom"] = muter_texte(piece["nom"])
    elif t == "ECART_PRENOMS":
        champ, valeur_attendue = "prenoms", piece["prenoms"]
        p = piece["prenoms"].split()
        e["prenoms"] = " ".join(reversed(p)) if len(p) > 1 else muter_texte(piece["prenoms"])
    elif t == "ECART_DATE_NAISSANCE":
        champ, valeur_attendue = "date_naissance", piece["date_naissance"]
        e["date_naissance"] = decaler_date(d_naiss, d_enrol).isoformat()
    elif t == "ECART_SEXE":
        champ, valeur_attendue = "sexe", piece["sexe"]
        e["sexe"] = "F" if piece["sexe"] == "M" else "M"
    elif t == "ECART_LIEU_NAISSANCE":
        champ, valeur_attendue = "code_commune_naissance", piece["code_commune_naissance"]
        e["code_commune_naissance"] = random.choice(
            [c for c in CODES_VALIDES if c != piece["code_commune_naissance"]])
    elif t == "DATE_NAISSANCE_POSTERIEURE":
        champ, valeur_attendue = "date_naissance", piece["date_naissance"]
        e["date_naissance"] = (d_enrol + timedelta(days=random.randint(1, 400))).isoformat()
    elif t == "AGE_INVRAISEMBLABLE":
        champ, valeur_attendue = "date_naissance", piece["date_naissance"]
        e["date_naissance"] = date_aleatoire(date(1880, 1, 1), date(1905, 12, 31)).isoformat()
    elif t == "CODE_COMMUNE_INEXISTANT":
        champ, valeur_attendue = "code_commune_naissance", piece["code_commune_naissance"]
        e["code_commune_naissance"] = random.choice(["0000", "9999", "0199", "0399", "1299"])
    elif t == "CHAMP_OBLIGATOIRE_MANQUANT":
        champ, valeur_attendue = "nom_mere", piece["nom_mere"]
        e["nom_mere"] = ""
    elif t == "TELEPHONE_INVALIDE":
        champ, valeur_attendue = "telephone", "(numéro valide attendu : 01 + 8 chiffres)"
        e["telephone"] = random.choice([
            "".join(random.choice("0123456789") for _ in range(8)),        # ancien format 8 chiffres
            "".join(random.choice("0123456789") for _ in range(9)),        # 9 chiffres
            "01" + "".join(random.choice("0123456789") for _ in range(10)),  # trop long
            "02" + "".join(random.choice("0123456789") for _ in range(8)),  # mauvais préfixe
            "01O2" + "".join(random.choice("0123456789") for _ in range(6)),  # lettre O
        ])
    e["_gt"] = {"type": t, "regles": REGLES_ATTENDUES[t], "champ": champ,
                "attendue": valeur_attendue}


def variante_benigne(e):
    """Variations de FORME sans erreur (pièges à faux positifs) : casse, espaces, accents,
    format du téléphone. Une bonne règle doit les normaliser et NE PAS les signaler."""
    v = random.choice(["casse", "espaces", "accents", "tel"])
    if v == "tel" and not e["telephone"]:
        v = "casse"
    if v == "casse":
        e["nom"] = e["nom"].lower()
    elif v == "espaces":
        e["prenoms"] = "  " + e["prenoms"].replace(" ", "   ") + " "
    elif v == "accents":
        e["prenoms"] = sans_accents(e["prenoms"])
        e["nom_mere"] = sans_accents(e["nom_mere"])
    elif v == "tel":
        t = e["telephone"]
        e["telephone"] = random.choice([
            f"{t[:2]} {t[2:4]} {t[4:6]} {t[6:8]} {t[8:]}", f"+229 {t}", f"+229{t}"])


def ecrire_csv(chemin, lignes, colonnes):
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=colonnes, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(lignes)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pieces, enrol = generer_base()
    par_piece = {p["id_piece"]: p for p in pieces}

    # 1) anomalies par enregistrement (taux plus élevé pour les agents à risque)
    for e in enrol:
        p = P_ERREUR_RISQUE if e["agent_id"] in AGENTS_A_RISQUE else P_ERREUR
        if random.random() < p:
            injecter(e, par_piece[e["id_piece"]])
        elif random.random() < 0.07:
            variante_benigne(e)

    # 2) doublons : ré-enrôlement d'une pièce déjà enrôlée proprement
    propres = [e for e in enrol if e["_gt"] is None]
    for orig in random.sample(propres, N_DOUBLONS):
        d = dict(orig)
        d["agent_id"] = random.choice(AGENTS)
        d["centre_enrolement"] = CENTRE_AGENT[d["agent_id"]]
        nouvelle = min(date.fromisoformat(orig["date_enrolement"])
                       + timedelta(days=random.randint(1, 90)), DATE_FIN)
        d["date_enrolement"] = nouvelle.isoformat()
        d["_gt"] = {"type": "DOUBLON", "regles": "R11", "champ": "id_piece",
                    "attendue": ""}
        enrol.append(d)

    # 3) tri chronologique puis attribution des identifiants
    enrol.sort(key=lambda e: e["date_enrolement"])
    premier = {}
    for k, e in enumerate(enrol, start=1):
        e["id_enrolement"] = f"ENR-{k:06d}"
        premier.setdefault(e["id_piece"], e["id_enrolement"])

    # 4) vérité terrain
    verite = []
    for e in enrol:
        g = e["_gt"]
        if not g:
            continue
        attendue = g["attendue"]
        saisie = e[g["champ"]]
        if g["type"] == "DOUBLON":
            attendue = f"déjà enrôlé sous {premier[e['id_piece']]}"
        verite.append({
            "id_enrolement": e["id_enrolement"], "id_piece": e["id_piece"],
            "type_anomalie": g["type"], "regles_attendues": g["regles"],
            "champ": g["champ"], "valeur_saisie": saisie, "valeur_attendue": attendue,
        })

    cols_enrol = ["id_enrolement", "id_piece", "type_piece", "agent_id", "centre_enrolement",
                  "date_enrolement", "nom", "prenoms", "date_naissance", "sexe",
                  "code_commune_naissance", "nom_mere", "telephone"]
    cols_piece = ["id_piece", "type_piece", "nom", "prenoms", "date_naissance", "sexe",
                  "code_commune_naissance", "nom_mere"]
    ecrire_csv(OUT / "enrolements.csv", enrol, cols_enrol)
    ecrire_csv(OUT / "pieces_justificatives.csv", pieces, cols_piece)
    ecrire_csv(OUT / "ref_communes.csv",
               [{"code_commune": c, "commune": n, "departement": d} for c, n, d in COMMUNES],
               ["code_commune", "commune", "departement"])
    ecrire_csv(OUT / "verite_terrain_anomalies.csv", verite,
               ["id_enrolement", "id_piece", "type_anomalie", "regles_attendues", "champ",
                "valeur_saisie", "valeur_attendue"])

    print(f"Enrôlements : {len(enrol)} | pièces : {len(pieces)} | communes : {len(COMMUNES)}")
    print(f"Anomalies injectées : {len(verite)} ({len(verite) / len(enrol):.1%})")
    for t in sorted({v['type_anomalie'] for v in verite}):
        print(f"  {t:30s} {sum(1 for v in verite if v['type_anomalie'] == t)}")
    print(f"Fichiers écrits dans : {OUT.resolve()}")


if __name__ == "__main__":
    main()
