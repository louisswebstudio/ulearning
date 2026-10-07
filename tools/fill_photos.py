"""Swap photo placeholders (<div class="ph">…</div>) for real UTALK photos (Instagram reel covers),
plus 4 Unsplash stock photos (assets/img/stock/, Unsplash licence) for the programme cards.

The covers are small (640×1136 from Instagram, cleaned and upscaled to 800×1420 by tools/enhance_photos.swift; portrait), so wide slots get 2 or 4 photos side by side
(.photo-row) instead of one stretched image. Testimonial slots stay placeholders: they need
the real student's photo next to their real quote.

Idempotent: only untouched placeholders are replaced. Run after build_pages.py:
    python tools/fill_photos.py
"""
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

# key -> (file, alt text)
PHOTOS = {
    "hall":       ("DVbeFAijA2A", "Le hall d’UTALK Center, avec les kakémonos UTALK"),
    "speaking":   ("DXmmpJqDJwf", "Un étudiant prend la parole autour de la table"),
    "heart":      ("DYj_qf_scYO", "Une étudiante souriante, assise à l’accueil du centre"),
    "class":      ("DavO0NTNy_q", "Des étudiantes rient pendant une activité devant l’écran interactif"),
    "balloons":   ("DbDsbRftSWF", "Deux étudiants pendant un jeu de langue avec des ballons"),
    "roleplay":   ("Dd1DMVoNF_K", "Une étudiante en jeu de rôle, assise à un bureau"),
    "boardgames": ("Dd8u3z4N--g", "Des étudiants jouent à des jeux de société dans le centre"),
    "entrance":   ("DdTmEAyNO6t", "Devant l’affiche UTALK, à l’entrée du 12e étage"),
    "reception":  ("DdYjCJtNuX3", "L’accueil d’UTALK Center, avec le logo et les drapeaux des cinq langues"),
    "reception2": ("DdgZwF1tbxp", "L’accueil et le logo lumineux UTALK"),
    "openspace":  ("Ddln2h3tY5T", "Une étudiante dans l’espace lumineux du centre"),
    "advisor":    ("DdrEsgFtw_t", "Une conseillère UTALK reçoit un futur étudiant"),
    # Instagram highlights (stories)
    "hl-classe":    ("hl-classe", "Un cours en petit groupe autour de la grande table"),
    "hl-etudiante": ("hl-etudiante", "Une étudiante souriante pendant le cours"),
    "hl-adulte":    ("hl-adulte", "Un apprenant adulte, détendu, en salle de cours"),
    "hl-salle":     ("hl-salle", "Des étudiants dans une salle de cours lumineuse"),
    "hl-talklab":   ("hl-talklab", "Un étudiant à la table du TalkLab, devant l’écran interactif"),
    "hl-couloir":   ("hl-couloir", "Le couloir du centre, décoré aux couleurs d’UTALK"),
    "hl-vue-12e":   ("hl-vue-12e", "Vue sur le centre-ville de Casablanca depuis le 12e étage"),
}

# Stock photos (Unsplash): key -> (file in assets/img/stock, alt, width, height)
STOCK = {
    "st-group":      ("cours-de-langues", "Des étudiants souriants échangent pendant un cours", 1400, 788),
    "st-speaking":   ("communication-speaking", "Une femme prend la parole au micro devant un groupe", 1400, 931),
    "st-intensive":  ("cours-intensifs", "Un groupe d’étudiants travaille ensemble autour d’un ordinateur", 1400, 788),
    "st-individual": ("cours-individuels", "Une professeure et une élève travaillent sur le même cahier", 1400, 933),
    "st-preparation": ("preparation", "Une jeune femme souriante sur un toit de Paris, la tour Eiffel au loin", 1400, 933),
}

# placeholder label -> list of slots; a slot is one key or a tuple of keys (photo row).
# Repeated labels on the same page take the next slot (cycling).
MAP = {
    "Photo : une classe UTALK en action": [("class", "balloons")],
    "Photo : un étudiant qui parle": ["speaking"],
    "Photo : étudiants en activité": ["balloons", "boardgames"],
    "Vidéo ou photo plein écran : l’ambiance du centre": [("reception", "class", "boardgames", "speaking")],
    "Vidéo plein écran : visite du centre (fichier original à demander au client)": [("hall", "reception", "reception2", "entrance")],
    "Vidéo plein écran : une séance au TalkLab": [("boardgames", "balloons", "speaking", "class")],
    "Salle de classe": ["class"],
    "Salle de cours": ["hl-salle", "class"],
    "Atelier speaking": ["speaking"],
    "Vidéo TalkLab": ["boardgames"],
    "Vidéo : jeux de langue": ["balloons"],
    "Vidéo : jeu de langue": ["boardgames"],
    "Vidéo : débat": ["speaking"],
    "Photo : cours en groupe": ["st-group"],
    "Photo : atelier de prise de parole": ["st-speaking"],
    "Photo : session intensive": ["st-intensive"],
    "Photo : cours particulier": ["st-individual"],
    "Photo : une séance au TalkLab": ["boardgames"],
    "Photo : une conversation au TalkLab": ["hl-talklab"],
    "Photo : une activité au TalkLab": ["balloons"],
    "Photo : un point de suivi avec un professeur": ["advisor"],
    "Photo : un jeu de rôle en classe": ["roleplay"],
    "Photo : un cours en petit groupe": ["class"],
    "Photo : préparation à un examen": ["st-preparation"],
    "Photo : un cours en groupe chez UTALK": ["st-group"],
    "Photo : un cours au centre": ["class"],
    "Photo réelle du centre": ["reception"],
    "Photo réelle : le centre UTALK": ["reception"],
    "Photo : l’entrée ou l’accueil du centre": ["hall"],  # no people: the centre itself
    "Photo : l’accueil": [("reception", "reception2")],
    "Vue du 12ᵉ étage": [("hl-vue-12e", "hl-couloir")],
    "Espace détente": ["hl-couloir"],
    "Le TalkLab": ["boardgames"],
    "L’équipe": ["advisor"],
    "Étudiants en cours": ["hl-salle"],
    "Échange en petit groupe": ["speaking"],
    "Photo de groupe": [("hl-classe", "balloons")],
    "Au TalkLab": ["hl-talklab"],
    "Remise de certificats": ["heart"],
    "Quiz en équipe": ["balloons"],
    "Sortie ou événement": [("boardgames", "class")],
    "Portrait": ["hl-etudiante", "hl-adulte"],
    "Soirée à thème": ["hall"],
    "Conversation au TalkLab": [("speaking", "boardgames")],
    "Débat en groupe": ["speaking"],
    # language pages: no language-specific footage yet, so vary the scene per language
    "Photo : un cours d’anglais": ["speaking"],
    "Photo : un cours d’anglais chez UTALK": ["speaking"],
    "Photo : un cours de français": ["roleplay"],
    "Photo : un cours de français chez UTALK": ["roleplay"],
    "Photo : un cours d’allemand": ["class"],
    "Photo : un cours d’allemand chez UTALK": ["class"],
    "Photo : un cours d’espagnol": ["boardgames"],
    "Photo : un cours d’espagnol chez UTALK": ["boardgames"],
    "Photo : un cours d’italien": ["balloons"],
    "Photo : un cours d’italien chez UTALK": ["balloons"],
}

# Hero floating shapes + bento avatars: small crops of faces.
# Face centre per photo (x %, y %) so the tiny crops zoom on the person, not the background.
FACES = {
    "DYj_qf_scYO": (47, 26), "DXmmpJqDJwf": (52, 57), "DdTmEAyNO6t": (50, 26), "Ddln2h3tY5T": (40, 44),
}
FLOATS = ["heart", "speaking", "entrance", "openspace"]
AVATARS = ["heart", "entrance", "openspace", "speaking"]

PH_RE = re.compile(r'<div class="(xp__media )?ph(?: ph--dark)?"><span class="ph__icon(?: ph__icon--play)?"></span><span class="ph__label">([^<]*)</span></div>')


def img(key, prefix, cls="ph-img", lazy=True):
    if key in STOCK:
        file, alt, w, h = STOCK[key]
        path = f"stock/{file}"
    else:
        (file, alt), w, h = PHOTOS[key], 800, 1420
        path = f"instagram/{file}"
    load = ' loading="lazy"' if lazy else ""
    return f'<img class="{cls}" src="{prefix}assets/img/{path}.jpg" alt="{alt}" width="{w}" height="{h}"{load} decoding="async">'


def slot_html(slot, prefix, extra=""):
    if isinstance(slot, str):
        return img(slot, prefix)
    return f'<div class="{extra}photo-row photo-row--{len(slot)}">' + "".join(img(k, prefix, "photo-row__img") for k in slot) + "</div>"


def fill(html, prefix):
    seen = defaultdict(int)
    missing = set()

    def repl(m):
        extra, label = m.group(1) or "", m.group(2)
        slots = MAP.get(label)
        if not slots:
            missing.add(label)
            return m.group(0)
        slot = slots[seen[label] % len(slots)]
        seen[label] += 1
        return slot_html(slot, prefix, extra)

    html = PH_RE.sub(repl, html)

    floats = iter(FLOATS)
    html = re.sub(r'<span class="ph-person"></span>', lambda m: img(next(floats), prefix, "float__img", lazy=False), html)

    def avatars(m):
        return '<div class="avatars" aria-hidden="true">\n          ' + "".join(
            f'<span><img src="{prefix}assets/img/instagram/{PHOTOS[k][0]}.jpg" alt="" width="800" height="1420"></span>' for k in AVATARS
        ) + "\n        </div>"
    html = re.sub(r'<div class="avatars" aria-hidden="true">\s*(?:<span></span>)+\s*</div>', avatars, html)
    return face_crop(html), missing


def face_crop(html):
    """Point float/avatar crops at the face (idempotent: rewrites the style each run)."""
    def repl(m):
        tag, file = m.group(0), m.group(2)
        if file not in FACES:
            return tag
        fx, fy = FACES[file]
        tag = re.sub(r' style="[^"]*"', "", tag)
        return tag.replace("<img ", f'<img style="--fx:{fx}%;--fy:{fy}%" ', 1)
    return re.sub(r'<img (class="float__img" )?(?:style="[^"]*" )?src="[^"]*instagram/([^"/]+)\.jpg"[^>]*>',
                  lambda m: repl(m) if (m.group(1) or html[m.start() - 6:m.start()] == "<span>") else m.group(0), html)


def main():
    left = defaultdict(int)
    for path in sorted(SITE.rglob("*.html")):
        prefix = "../" * (len(path.relative_to(SITE).parts) - 1)
        src = path.read_text(encoding="utf8")
        out, missing = fill(src, prefix)
        for label in missing:
            left[label] += 1
        if out != src:
            path.write_text(out, encoding="utf8")
            print("filled", path.relative_to(ROOT))
    if left:
        print("left as placeholders:", dict(left))


if __name__ == "__main__":
    main()
