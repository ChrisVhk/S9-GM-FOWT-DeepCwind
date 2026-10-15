"""Clarté du dépôt public (lots P1 à P4) : l'atelier tour est une ressource (annexes/), plus une séance ; un seul tableau de parcours ;
nettoyage ; index unique de la théorie `fiches/README.md`. Écrits AVANT les déplacements et les réécritures (aucun contenu pédagogique
ne change : on déplace, on relie, on indexe)."""
import os
import re
import subprocess
import unicodedata
from pathlib import Path
from urllib.parse import unquote

import pytest

from .conftest import RACINE

LIEN = re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
# motifs scindés en deux littéraux : ce fichier ne doit pas se déclarer lui-même fautif (anciens chemins, R-9)
ANCIEN_ATELIER = ("seances/ate" "lier_tour", "../ate" "lier_tour")
CONSIGNES = [RACINE / "seances" / d / "README.md" for d in ("0a", "0b", "phase1", "phase2", "phase3", "phase4", "phase5", "phase6")]
GUIDE = RACINE / "annexes" / "atelier_tour" / "README.md"


def suivis():
    sortie = subprocess.run(["git", "ls-files"], cwd=RACINE, capture_output=True, text=True, check=True).stdout
    return [f for f in sortie.split("\n") if f]


def hors_code(texte):
    sortie, dedans = [], False
    for ligne in texte.split("\n"):
        if ligne.lstrip().startswith("```"):
            dedans = not dedans
            continue
        sortie.append("" if dedans else re.sub(r"`[^`]*`", "", ligne))
    return sortie


def slug(titre):
    """Ancre GitHub d'un titre : minuscules, ponctuation retirée (sauf tiret et soulignement), espaces en tirets."""
    t = unicodedata.normalize("NFC", titre.strip().lower())
    t = re.sub(r"[^\w\- ]", "", t)
    return t.replace(" ", "-")


def ancres(chemin):
    texte = chemin.read_text(encoding="utf-8")
    trouvees = {m.group(1) for m in re.finditer(r"""<a\s+(?:id|name)=["']([^"']+)["']""", texte)}
    vus = {}
    for ligne in hors_code(texte):
        m = re.match(r"^#{1,6}\s+(.*?)\s*#*$", ligne)
        if m:
            s = slug(re.sub(r"[*_`]|\[([^\]]*)\]\([^)]*\)", lambda x: x.group(1) or "", m.group(1)))
            n = vus.get(s, 0)
            trouvees.add(s if n == 0 else f"{s}-{n}")
            vus[s] = n + 1
    return trouvees


def texte(p):
    return Path(p).read_text(encoding="utf-8")


# ---- P1 : l'atelier tour devient une ressource -------------------------------------------------------------------------
def test_l_atelier_est_une_ressource_des_annexes():
    assert not (RACINE / "seances" / "atelier_tour").exists()
    assert GUIDE.is_file()
    premier_titre = next(l for l in texte(GUIDE).split("\n") if l.startswith("# "))
    assert "Guide du classeur de dimensionnement de tour" in premier_titre, premier_titre


def test_le_guide_dit_a_quoi_il_sert_et_quand_on_l_ouvre():
    debut = "\n".join(texte(GUIDE).split("\n")[:12])
    assert "phase 3" in debut and "phase 5" in debut and "classeur" in debut, debut


def test_aucun_lien_ni_chemin_vers_l_ancien_emplacement():
    fautes = []
    for f in suivis():
        if not f.endswith((".md", ".py", ".ipynb", ".sh", ".txt", ".yml")):
            continue
        t = (RACINE / f).read_text(encoding="utf-8", errors="ignore")
        if any(a in t for a in ANCIEN_ATELIER):
            fautes.append(f)
    assert not fautes, fautes


def test_plus_aucun_renvoi_par_numero_de_section_de_l_atelier():
    fautes = []
    for f in [GUIDE, RACINE / "seances" / "phase3" / "README.md", RACINE / "seances" / "phase5" / "README.md"]:
        if not f.is_file():
            fautes.append(f"{f.name} absent")
            continue
        for n, ligne in enumerate(texte(f).split("\n"), start=1):
            if re.search(r"§\s?\d", ligne) and "ENONCE" not in ligne:
                fautes.append(f"{f.relative_to(RACINE)}:{n}: {ligne.strip()[:90]}")
    assert not fautes, fautes


@pytest.mark.parametrize("phase", ["phase3", "phase5"])
def test_les_phases_3_et_5_renvoient_au_guide_par_des_ancres_et_le_presentent_comme_ressource(phase):
    t = texte(RACINE / "seances" / phase / "README.md")
    cibles = [c for c in LIEN.findall("\n".join(hors_code(t))) if "annexes/atelier_tour/README.md" in c]
    assert any("#" in c for c in cibles), "aucun lien du guide avec ancre"
    avant = t.split("## 2. Avant de commencer", 1)[1].split("\n## ", 1)[0]
    assert re.search(r"Ressource\s*:.*atelier_tour/README\.md", avant), "ligne « Ressource : … » absente de « Avant de commencer »"


def test_toute_ancre_citee_existe():
    fautes = []
    f_suivis = set(suivis())
    cache = {}
    for f in sorted(f_suivis):
        if not f.endswith(".md"):
            continue
        for n, ligne in enumerate(hors_code(texte(RACINE / f)), start=1):
            for cible in LIEN.findall(ligne):
                if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", cible) or "#" not in cible:
                    continue
                chemin, frag = cible.split("#", 1)
                voulu = (RACINE / f).parent / unquote(chemin) if chemin else RACINE / f
                try:
                    rel = str(voulu.resolve().relative_to(RACINE))
                except ValueError:
                    continue
                if not rel.endswith(".md") or rel not in f_suivis:
                    continue
                cache.setdefault(rel, ancres(RACINE / rel))
                if unquote(frag) not in cache[rel]:
                    fautes.append(f"{f}:{n}: ancre absente de {rel} : #{frag}")
    assert not fautes, fautes


# ---- P2 : un seul tableau de parcours, colonne « Séances », vocabulaire -------------------------------------------------
def lignes_tableau(t, motif):
    return [l for l in t.split("\n") if l.startswith("|") and re.search(motif, l)]


def test_le_tableau_de_parcours_n_a_que_des_etapes_avec_volume_et_une_colonne_seances():
    t = texte(RACINE / "README.md")
    entete = next(l for l in t.split("\n") if l.startswith("|") and "Contenu" in l and "Volume" in l)
    assert "Séances" in entete, entete
    assert not lignes_tableau(t, r"(?i)atelier"), "l'atelier ne figure pas dans le tableau de parcours"
    for l in lignes_tableau(t, r"\]\(seances/"):
        cellules = [c.strip() for c in l.strip("|").split("|")]
        assert cellules[2] not in ("", "—"), f"ligne sans volume : {l[:80]}"


def test_l_enonce_ne_reprend_pas_le_tableau_de_parcours():
    t = texte(RACINE / "ENONCE.md")
    assert not lignes_tableau(t, r"\]\(seances/"), "l'ENONCE renvoie au README au lieu de répéter le tableau"
    assert "README.md" in t


def test_vocabulaire_seance_et_phase_defini_dans_le_readme():
    t = texte(RACINE / "README.md")
    assert re.search(r"[Uu]ne \*\*séance\*\*", t) and re.search(r"[Uu]ne \*\*phase\*\*", t)


# ---- P3 : nettoyage -----------------------------------------------------------------------------------------------------
def test_le_pas_a_pas_historique_a_quitte_le_public_et_transition_le_dit():
    assert not (RACINE / "annexes" / "historique").exists()
    t = texte(RACINE / "TRANSITION.md")
    assert "PAS_A_PAS_2026-10-12" in t and "annexes/atelier_tour" in t


def test_la_copie_en_coulisses_existe_si_les_coulisses_sont_disponibles():
    racine = os.environ.get("S9GM_RACINE_MASTERS")
    if not racine:
        pytest.skip("S9GM_RACINE_MASTERS=<dossier du dépôt privé> non défini")
    archive = Path(racine) / ("_Cou" "lisses-depots-publics") / "S9-GM-FOWT-DeepCwind" / "archives_public"
    assert (archive / "PAS_A_PAS_2026-10-12.md").is_file()


# ---- P4 : index unique de la théorie ------------------------------------------------------------------------------------
INDEX = RACINE / "fiches" / "README.md"


def test_l_index_existe_et_reference_toutes_les_fiches():
    assert INDEX.is_file()
    cibles = {unquote(c.split("#")[0]) for c in LIEN.findall("\n".join(hors_code(texte(INDEX))))}
    for f in sorted((RACINE / "fiches").glob("*.md")):
        if f.name != "README.md":
            assert f.name in cibles, f"{f.name} absente de l'index"


def test_les_fiches_a_venir_figurent_avec_leur_emplacement_provisoire():
    t = texte(INDEX)
    for fiche in ("F3", "F4", "F6", "F7", "F8"):
        assert re.search(rf"{fiche}.*à venir", t), fiche


def test_le_readme_racine_et_chaque_consigne_renvoient_a_l_index():
    assert "fiches/README.md" in texte(RACINE / "README.md")
    for c in CONSIGNES:
        theorie = texte(c).split("## 6. Théorie à lire", 1)[1].split("\n## ", 1)[0]
        assert "fiches/README.md" in theorie, f"{c.parent.name} : la rubrique « Théorie à lire » ne renvoie pas à l'index"


def test_l_index_ne_contient_aucune_explication_nouvelle():
    """L'index pointe, il n'explique pas : aucune formule, aucun bloc de code."""
    t = texte(INDEX)
    assert "```" not in t and "$" not in t
