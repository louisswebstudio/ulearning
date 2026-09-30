"""Generate the static inner pages from the home page's shared parts.

- Navbar and footer are copied from site/index.html so every page stays in sync.
- Language / programme pages: BrightMind course detail layout
  (centered H1 + meta row, content 781 + sticky sidebar 397, red CTA panel). No prices (client decision).
- TalkLab, Étudiants, UTALK Center, Contact: page header + blocks already cloned on the home page
  (Kidora banner/gallery, Brightpath tilted cards, Kidora story cards, BrightMind about, Lexio form).

Run from the project root:  python tools/build_pages.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
HOME = SITE / "index.html"

FLAGS = {
    "en": '<clipPath id="f-en"><circle cx="30" cy="30" r="30"/></clipPath><g clip-path="url(#f-en)"><rect width="60" height="60" fill="#012169"/><path d="M0 0L60 60M60 0L0 60" stroke="#fff" stroke-width="12"/><path d="M0 0L60 60M60 0L0 60" stroke="#C8102E" stroke-width="4"/><path d="M30 0V60M0 30H60" stroke="#fff" stroke-width="18"/><path d="M30 0V60M0 30H60" stroke="#C8102E" stroke-width="10"/></g>',
}

# CEFR levels (standard scale; official French level names).
LEVELS = [
    ("A1", "Découverte", "Se présenter, poser des questions simples, comprendre l’essentiel."),
    ("A2", "Survie", "Échanger sur le quotidien : achats, trajets, travail, loisirs."),
    ("B1", "Seuil", "Raconter, donner son avis, se débrouiller en voyage ou au travail."),
    ("B2", "Avancé", "Débattre, argumenter et suivre une conversation rapide."),
    ("C1", "Autonome", "S’exprimer avec aisance dans un cadre professionnel ou académique."),
]

PH = '<div class="ph"><span class="ph__icon{play}"></span><span class="ph__label">{label}</span></div>'


def ph(label, play=False):
    return PH.format(label=label, play=" ph__icon--play" if play else "")


# ---------------------------------------------------------------------------
# Shell
# ---------------------------------------------------------------------------
SHELL = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="{p}assets/css/style.css">
</head>
<body>

{nav}

<main>
{body}
</main>

{footer}

<script src="{p}assets/js/main.js"></script>
</body>
</html>
"""


def shared_parts():
    home = HOME.read_text(encoding="utf8")
    nav = home[home.index('<header class="nav">'):home.index('</header>') + len('</header>')]
    footer = home[home.index('<footer class="footer">'):home.index('</footer>') + len('</footer>')]
    return home, nav, footer


def relink(html, p):
    """Rewrite home-relative links for a page living at depth prefix p ('' or '../')."""
    html = re.sub(r'href="#(\w*)"', lambda m: f'href="{p}index.html#{m.group(1)}"' if m.group(1) else f'href="{p}index.html"', html)
    if p:
        html = re.sub(r'(href|src)="(?!https?:|tel:|mailto:|\.\./|#)([^"]+)"', lambda m: f'{m.group(1)}="{p}{m.group(2)}"', html)
    return html


def mark_current(nav, target):
    return nav.replace(f'href="{target}">', f'href="{target}" aria-current="page">', 1)


def page(path, title, desc, body, current=None):
    home, nav, footer = shared_parts()
    depth = path.count("/")
    p = "../" * depth
    nav_r, foot_r = relink(nav, p), relink(footer, p)
    if current:
        nav_r = mark_current(nav_r, p + current)
    html = SHELL.format(title=title, desc=desc, p=p, nav=nav_r, footer=foot_r, body=relink(body, p))
    out = SITE / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf8")
    print("wrote", out.relative_to(ROOT))


def section_from_home(cls_id):
    """Copy one <section ... id="cls_id"> block from the home page."""
    home = HOME.read_text(encoding="utf8")
    m = re.search(rf'<section class="[^"]*" id="{cls_id}">.*?</section>', home, re.S)
    return m.group(0)


def page_head(label, title_html, lead=None, meta=None):
    meta_html = ""
    if meta:
        meta_html = '\n    <ul class="course-hero__meta">' + "".join(f"<li>{m}</li>" for m in meta) + "</ul>"
    lead_html = f'\n    <p class="page-hero__lead">{lead}</p>' if lead else ""
    return f"""<!-- ============ PAGE HEADER (ref: BrightMind course header, centered) ============ -->
<section class="course-hero">
  <div class="container">
    <p class="label">{label}</p>
    <h1 class="course-hero__title page-hero__title">{title_html}</h1>{meta_html}{lead_html}
  </div>
</section>
"""


def cta(title, href="contact.html", label="Contactez-nous"):
    return f"""
<!-- ============ CTA PANEL (ref: BrightMind "Take the First Step") ============ -->
<section class="cta-band">
  <div class="container">
    <div class="cta-panel">
      <h2 class="cta-panel__title">{title}</h2>
      <a href="{href}" class="btn cta-panel__btn">{label}</a>
    </div>
  </div>
</section>"""


def lis(items):
    return "".join(f"\n        <li>{x}</li>" for x in items) + "\n      "


# ---------------------------------------------------------------------------
# Course template (languages + programmes)
# ---------------------------------------------------------------------------
def course_body(c):
    levels = ""
    if c.get("levels"):
        levels = f"""
      <h2 class="course__h">Les niveaux</h2>
      <p class="course__p">Nos niveaux suivent le Cadre européen commun de référence pour les langues (CECRL).</p>
      <ol class="levels">{"".join(f'''
        <li class="level"><span class="level__code">{a}</span><span class="level__name">{b}</span><span class="level__text">{t}</span></li>''' for a, b, t in LEVELS)}
      </ol>
"""
    side = "".join(f'\n          <li><span class="side-ico side-ico--{i}"></span>{t}</li>' for i, t in c["side"])
    return page_head(c["label"], c["name"], meta=c["meta"]) + f"""
<!-- ============ COURSE BODY (ref: BrightMind course detail: content 781 + sticky card 397) ============ -->
<section class="course">
  <div class="container course__grid">
    <div class="course__main">
      <figure class="course__photo">{ph(c["photo"])}</figure>

      <h2 class="course__h">À propos du cours</h2>
      <p class="course__p">{c["about"]}</p>

      <h2 class="course__h">Ce que vous allez apprendre</h2>
      <ul class="course__list">{lis(c["learn"])}</ul>
{levels}
      <h2 class="course__h">Pour qui ?</h2>
      <ul class="course__list">{lis(c["who"])}</ul>
    </div>

    <aside class="course__side">
      <div class="side-card side-card--{c["tint"]}">
        <p class="side-card__label">{c["side_label"]}</p>
        <p class="side-card__big">{c["side_big"]}</p>
        <ul class="side-card__list">{side}
        </ul>
        <a href="contact.html" class="btn btn--primary side-card__btn">Demander des informations</a>
        <p class="side-card__note">Tarifs communiqués sur demande.</p>
      </div>
    </aside>
  </div>
</section>
""" + cta(c["cta"])


ENGLISH = {
    "label": "Nos langues", "name": "English", "tint": "en", "levels": True,
    "meta": [f'<svg class="flag flag--sm" viewBox="0 0 60 60" aria-hidden="true">{FLAGS["en"]}</svg> Cours d’anglais', "Niveaux A1 → C1", "Groupes &amp; individuels"],
    "photo": "Photo : un cours d’anglais chez UTALK",
    "about": "Nos cours d’anglais vous font parler dès la première séance. En petit groupe ou en cours individuel, vous progressez niveau par niveau avec des professeurs qui mettent l’oral au centre de chaque cours.",
    "learn": ["Tenir une conversation en anglais sur la vie de tous les jours",
              "Comprendre l’anglais parlé, à un rythme naturel",
              "Utiliser l’anglais au travail : réunions, e-mails, présentations",
              "Prendre la parole sans stress grâce aux séances au TalkLab"],
    "who": ["Étudiants qui préparent leurs études ou un examen",
            "Professionnels qui utilisent l’anglais au travail",
            "Toute personne qui veut enfin oser parler anglais"],
    "side_label": "Cours d’anglais", "side_big": "A1 → C1",
    "side": [("group", "Cours en petit groupe"), ("user", "Cours individuels sur mesure"),
             ("clock", "Horaires : à confirmer"), ("chat", "Pratique orale au TalkLab"), ("pin", "Centre-ville, Casablanca")],
    "cta": "Prêt à parler anglais ?",
}

PROG_LANGUES = {
    "label": "Nos programmes", "name": "Cours de langues", "tint": "fr", "levels": True,
    "meta": ["5 langues", "Niveaux A1 → C1", "En groupe"],
    "photo": "Photo : un cours en groupe chez UTALK",
    "about": "Le programme principal d’UTALK : des cours en groupe pour apprendre l’anglais, le français, l’allemand, l’espagnol ou l’italien, du niveau débutant au niveau avancé, avec l’oral au centre de chaque séance.",
    "learn": ["Les bases solides de la langue : vocabulaire, grammaire, prononciation",
              "Comprendre et vous faire comprendre dans les situations du quotidien",
              "Prendre la parole en groupe, avec des activités et des mises en situation",
              "Progresser niveau par niveau, avec un suivi régulier"],
    "who": ["Débutants qui partent de zéro",
            "Personnes qui veulent reprendre une langue apprise à l’école",
            "Étudiants et professionnels qui visent un niveau précis"],
    "side_label": "Programme", "side_big": "5 langues",
    "side": [("group", "Cours en petit groupe"), ("clock", "Horaires : à confirmer"),
             ("chat", "Pratique orale au TalkLab"), ("pin", "Centre-ville, Casablanca")],
    "cta": "Prêt à commencer ?",
}


# ---------------------------------------------------------------------------
# TalkLab
# ---------------------------------------------------------------------------
ACTIVITIES = [
    ("chat", "Conversations", "— chaque semaine", "Des échanges guidés sur des sujets du quotidien, en petits groupes."),
    ("group", "Débats", "— tous niveaux", "Donner son avis, argumenter et répondre, dans une ambiance détendue."),
    ("sparkle", "Jeux de langue", "— en équipe", "Quiz, jeux de rôle et défis pour utiliser la langue en s’amusant."),
    ("calendar", "Événements", "— toute l’année", "Soirées à thème et rencontres pour pratiquer en dehors des cours."),
]


def talklab_body():
    cards = "".join(f"""
      <li class="step step--{i + 1}">
        <span class="step__num step__num--icon"><span class="side-ico side-ico--{ico}"></span></span>
        <div class="step__body">
          <h3 class="step__title">{t} <span class="step__tag">{tag}</span></h3>
          <p class="step__text">{txt}</p>
        </div>
      </li>""" for i, (ico, t, tag, txt) in enumerate(ACTIVITIES))
    tiles = [("big", "conversations", "Conversation au TalkLab", False, "Conversations"),
             ("", "jeux", "Vidéo : jeu de langue", True, "Jeux"),
             ("tall", "debats", "Débat en groupe", False, "Débats"),
             ("", "events", "Soirée à thème", False, "Événements"),
             ("wide", "conversations", "Échange en petit groupe", False, "Conversations"),
             ("", "jeux", "Quiz en équipe", False, "Jeux"),
             ("", "debats", "Vidéo : débat", True, "Débats")]
    tiles_html = "".join(
        f'\n      <li class="tile{" tile--" + s if s else ""}" data-cat="{cat}">{ph(lbl, play)}<span class="chip">{chip}</span></li>'
        for s, cat, lbl, play, chip in tiles)
    circled = '<span class="xp__circled">Live<svg viewBox="0 0 200 80" preserveAspectRatio="none" aria-hidden="true"><path d="M18 52 C4 30 40 8 104 8 C170 8 198 26 192 46 C186 68 130 76 88 74 C44 72 10 62 12 44 C14 30 40 18 70 14" /></svg></span>'
    return page_head("TalkLab", f"Learn the language. {circled} the language.",
                     lead="Le TalkLab, c’est l’espace d’UTALK où l’on pratique pour de vrai : conversations, débats, jeux et événements.") + f"""
<!-- ============ VIDEO BANNER (ref: Kidora "Discover our learning space") ============ -->
<section class="xp">
  <div class="xp__banner">
    <div class="xp__media ph ph--dark"><span class="ph__icon"></span><span class="ph__label">Vidéo plein écran : une séance au TalkLab</span></div>
    <div class="xp__overlay"></div>
    <div class="container xp__banner-inner">
      <p class="eyebrow eyebrow--light">✦ Au cœur du TalkLab</p>
      <h2 class="xp__title">Ici, on parle.</h2>
      <button type="button" class="xp__play" aria-label="Lire la vidéo du TalkLab"><span class="xp__play-icon" aria-hidden="true"></span>Voir la vidéo</button>
    </div>
  </div>
  <div class="marquee" aria-hidden="true">
    <div class="marquee__track">
      <span>Conversations</span><i>✦</i><span>Débats</span><i>✦</i><span>Jeux de langue</span><i>✦</i><span>Événements</span><i>✦</i>
      <span>Conversations</span><i>✦</i><span>Débats</span><i>✦</i><span>Jeux de langue</span><i>✦</i><span>Événements</span><i>✦</i>
      <span>Conversations</span><i>✦</i><span>Débats</span><i>✦</i><span>Jeux de langue</span><i>✦</i><span>Événements</span><i>✦</i>
    </div>
  </div>
</section>

<!-- ============ ACTIVITIES (ref: Brightpath "How it works" tilted cards) ============ -->
<section class="method">
  <div class="container method__grid">
    <div class="method__intro">
      <h2 class="method__title">Nos
        <span class="method__scribble">
          <span class="method__word">activités</span>
          <svg class="method__spark" viewBox="0 0 34 34" aria-hidden="true"><path d="M8 20 L12 6 M17 24 L29 12" /></svg>
          <svg class="method__underline" viewBox="0 0 232 44" preserveAspectRatio="none" aria-hidden="true"><path d="M4 22 C60 14 150 12 214 18" /><path d="M22 34 C90 26 170 26 228 36" /></svg>
        </span>
      </h2>
      <p class="method__lead">Quatre façons de pratiquer, pour passer de la théorie à la vraie conversation.</p>
      <figure class="method__photo">{ph("Photo : une activité au TalkLab")}</figure>
    </div>
    <ol class="method__steps">{cards}
    </ol>
  </div>
</section>

<!-- ============ GALLERY (filters, as on the home page) ============ -->
<section class="xp">
  <div class="container xp__gallery">
    <div class="xp__head">
      <h2 class="xp__subtitle">Le TalkLab en images</h2>
      <div class="filters" role="group" aria-label="Filtrer la galerie">
        <button type="button" class="filter is-active" data-filter="all" aria-pressed="true">Tout</button>
        <button type="button" class="filter" data-filter="conversations" aria-pressed="false">Conversations</button>
        <button type="button" class="filter" data-filter="debats" aria-pressed="false">Débats</button>
        <button type="button" class="filter" data-filter="jeux" aria-pressed="false">Jeux</button>
        <button type="button" class="filter" data-filter="events" aria-pressed="false">Événements</button>
      </div>
    </div>
    <ul class="tiles">{tiles_html}
    </ul>
  </div>
</section>
""" + cta("Envie de pratiquer ?")


# ---------------------------------------------------------------------------
# Étudiants
# ---------------------------------------------------------------------------
def story(badge, quote, meta, video):
    label = "Vidéo témoignage" if video else "Photo de l’étudiant"
    return f"""
    <li class="story">
      <div class="story__photo">{ph(label, video)}</div>
      <div class="story__body">
        <span class="story__badge">{badge}</span>
        <p class="story__quote">« {quote} »</p>
        <p class="story__name">Prénom N.</p>
        <p class="story__meta">{meta}</p>
      </div>
    </li>"""


def etudiants_body():
    videos = "".join([
        story("Vidéo", "Ici, le témoignage vidéo d’un étudiant UTALK : ce qu’il a appris et comment il a progressé.", "English · A2 → B2", True),
        story("Vidéo", "Ici, le témoignage vidéo d’un étudiant sur son expérience au TalkLab.", "Deutsch · A1 → B1", True),
        story("Vidéo", "Ici, le témoignage vidéo d’un étudiant sur ses cours et ses professeurs.", "Español · A2 → B2", True),
        story("Expérience", "Ici, le témoignage écrit d’un étudiant : l’ambiance, les activités, ce qu’il retient.", "Italiano · A1 → A2", False),
    ])
    success = "".join(f"""
    <article class="success">
      <figure class="success__photo">{ph("Photo de l’étudiant")}</figure>
      <div class="success__body">
        <span class="story__badge">Success story</span>
        <h3 class="success__title">{t}</h3>
        <dl class="success__facts">
          <div><dt>Objectif</dt><dd>À compléter avec l’objectif de départ de l’étudiant.</dd></div>
          <div><dt>Parcours</dt><dd>À compléter : langue, niveaux, programme suivi.</dd></div>
          <div><dt>Résultat</dt><dd>À compléter : ce que la langue lui a permis de faire.</dd></div>
        </dl>
        <p class="story__name">Prénom N.</p>
        <p class="story__meta">{m}</p>
      </div>
    </article>""" for t, m in [("Titre de la success story", "Français · B1 → C1"),
                               ("Titre de la success story", "English · A2 → B2")])
    photos = "".join(f'\n      <li class="tile{" tile--" + s if s else ""}">{ph(lbl)}</li>' for s, lbl in
                     [("big", "Photo de groupe"), ("", "Étudiants en cours"), ("tall", "Au TalkLab"),
                      ("", "Remise de certificats"), ("wide", "Sortie ou événement"), ("", "Portrait"), ("", "Portrait")])
    title = 'They learned. They practiced. They started <span class="swash">speaking.<svg viewBox="0 0 160 30" preserveAspectRatio="none" aria-hidden="true"><path d="M4 22 C40 8 110 4 156 12" /></svg></span>'
    return page_head("Étudiants", title, lead="Leurs témoignages, leurs parcours et leurs premiers pas à l’oral.") + f"""
<!-- ============ VIDEO TESTIMONIALS (ref: Kidora testimonial cards, as a grid) ============ -->
<section class="stu stu--page">
  <div class="container">
    <h2 class="section-title stu__subtitle">Témoignages <span class="accent">vidéo</span></h2>
    <ul class="stories-grid">{videos}
    </ul>
  </div>
</section>

<!-- ============ SUCCESS STORIES (ref: Kidora split photo + text) ============ -->
<section class="successes">
  <div class="container">
    <h2 class="section-title stu__subtitle">Success <span class="accent">stories</span></h2>
    <div class="successes__list">{success}
    </div>
  </div>
</section>

<!-- ============ PHOTOS ============ -->
<section class="xp">
  <div class="container xp__gallery">
    <div class="xp__head"><h2 class="xp__subtitle">Nos étudiants en images</h2></div>
    <ul class="tiles">{photos}
    </ul>
  </div>
</section>
""" + cta("À votre tour de parler ?")


# ---------------------------------------------------------------------------
# UTALK Center (about) — ref: BrightMind /about (short version agreed with the user)
#   1 title + full-width photo · 2 "Inspiring Journey" split · 3 "Core Values" 4 cards
#   4 photo grid · 5 where-to-find strip · 6 CTA panel
# ---------------------------------------------------------------------------
def centre_body():
    checks = "".join(f'\n          <li><span class="check" aria-hidden="true"></span><span>{t}</span></li>' for t in [
        "5 langues, du niveau A1 au niveau C1",
        "Cours en groupe et cours individuels",
        "Le TalkLab pour pratiquer l’oral",
        "Au 12<sup>e</sup> étage de l’Immeuble 44, Armée Royale",
    ])
    values = "".join(f"""
      <div class="value-card value-card--{tint}">
        <span class="value-card__ico"><span class="side-ico side-ico--{ico}"></span></span>
        <p class="value-card__title">{t}</p>
        <p class="value-card__text">{txt}</p>
      </div>""" for tint, ico, t, txt in [
        ("en", "chat", "Parler d’abord", "L’oral est au centre de chaque cours."),
        ("fr", "group", "Pratiquer", "Le TalkLab pour utiliser la langue en situation réelle."),
        ("it", "sparkle", "Progresser", "Des niveaux clairs, de A1 à C1, pour avancer pas à pas."),
        ("de", "user", "Oser", "Une ambiance conviviale où l’on parle sans stress."),
    ])
    photos = "".join(f'\n      <li class="tile{" tile--" + s if s else ""}">{ph(lbl)}</li>' for s, lbl in
                     [("big", "Photo : l’accueil"), ("", "Salle de cours"), ("tall", "Le TalkLab"),
                      ("", "Espace détente"), ("wide", "Vue du 12ᵉ étage"), ("", "Salle de cours"), ("", "L’équipe")])
    return f"""<!-- ============ 1. TITLE + WIDE PHOTO (ref: BrightMind /about header: H1 90 centered, photo 1240×600 r16) ============ -->
<section class="about-hero">
  <div class="container">
    <h1 class="about-hero__title">À propos d’<span class="accent">UTALK</span></h1>
    <p class="about-hero__lead">Un centre de langues et de communication au cœur de Casablanca, où l’on apprend en parlant.</p>
    <figure class="about-hero__photo">{ph("Photo réelle : le centre UTALK")}</figure>
  </div>
</section>

<!-- ============ 2. QUI SOMMES-NOUS (ref: BrightMind "Inspiring Journey" split) ============ -->
<section class="journey">
  <div class="container journey__grid">
    <div class="journey__body">
      <h2 class="journey__title"><span class="accent">Qui</span> sommes-nous ?</h2>
      <p class="journey__lead">UTALK Center est un centre de formation en langues et en communication, installé au centre-ville de Casablanca. On y apprend l’anglais, le français, l’allemand, l’espagnol et l’italien.</p>
      <ul class="checklist">{checks}
      </ul>
      <a href="index.html#programmes" class="btn btn--primary">Nos programmes</a>
    </div>
    <figure class="journey__photo">{ph("Photo : un cours au centre")}</figure>
  </div>
</section>

<!-- ============ 3. NOTRE PHILOSOPHIE (ref: BrightMind "Our Core Values" 4 pastel cards) ============ -->
<section class="core-values">
  <div class="container">
    <h2 class="section-title core-values__title">Notre <span class="accent">philosophie</span></h2>
    <div class="core-values__grid">{values}
    </div>
  </div>
</section>

<!-- ============ 4. LE CENTRE EN IMAGES (home gallery grid) ============ -->
<section class="xp">
  <div class="container xp__gallery">
    <div class="xp__head"><h2 class="xp__subtitle">Le centre en images</h2></div>
    <ul class="tiles">{photos}
    </ul>
  </div>
</section>

<!-- ============ 5. OÙ NOUS TROUVER (short strip) ============ -->
<section class="find">
  <div class="container">
    <div class="find__strip">
      <span class="visit__pin" aria-hidden="true"></span>
      <div class="find__text">
        <p class="find__title">Où nous trouver</p>
        <p class="find__addr">Centre-ville de Casablanca · Armée Royale, Immeuble 44 · 12<sup>e</sup> étage</p>
      </div>
      <div class="find__actions">
        <a class="visit__link" href="https://www.google.com/maps/search/?api=1&amp;query=Armée+Royale+Immeuble+44+Casablanca" target="_blank" rel="noopener"><span class="visit__ico visit__ico--map"></span>Google Maps</a>
        <a class="visit__link" href="contact.html"><span class="visit__ico visit__ico--phone"></span>Nous contacter</a>
      </div>
    </div>
  </div>
</section>
""" + cta("Venez nous rencontrer", label="Nous rendre visite")


# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------
def contact_body():
    form = section_from_home("contact")
    return page_head("Contact", 'Contactez-<span class="accent">nous</span>',
                     lead="Une question sur nos cours ? Écrivez-nous, appelez-nous ou passez au centre.") + form + """

<!-- ============ MAP (Google Maps embed on WordPress; link in the preview) ============ -->
<section class="map">
  <div class="container">
    <div class="map__box">
      <div class="map__inner">
        <span class="visit__pin" aria-hidden="true"></span>
        <p class="map__title">UTALK Center Casablanca</p>
        <p class="map__addr">Centre-ville · Armée Royale, Immeuble 44 · 12<sup>e</sup> étage</p>
        <a class="btn btn--primary" href="https://www.google.com/maps/search/?api=1&amp;query=Armée+Royale+Immeuble+44+Casablanca" target="_blank" rel="noopener">Ouvrir dans Google Maps</a>
        <p class="map__note">La carte Google Maps sera intégrée ici sur le site WordPress.</p>
      </div>
    </div>
  </div>
</section>
"""


def main():
    page("langues/english.html", "English · UTALK Center",
         "Cours d’anglais à Casablanca chez UTALK Center : niveaux A1 à C1, en groupe ou en individuel.",
         course_body(ENGLISH), current="index.html#langues")
    page("programmes/cours-de-langues.html", "Cours de langues · UTALK Center",
         "Cours de langues en groupe à Casablanca : anglais, français, allemand, espagnol, italien.",
         course_body(PROG_LANGUES))
    page("talklab.html", "TalkLab · UTALK Center",
         "Le TalkLab d’UTALK Center : conversations, débats, jeux et événements pour pratiquer les langues.",
         talklab_body(), current="talklab.html")
    page("etudiants.html", "Étudiants · UTALK Center",
         "Témoignages, success stories et photos des étudiants d’UTALK Center.",
         etudiants_body(), current="etudiants.html")
    page("centre.html", "UTALK Center · Qui sommes-nous",
         "UTALK Center, centre de langues et de communication au centre-ville de Casablanca.",
         centre_body())
    page("contact.html", "Contact · UTALK Center",
         "Contactez UTALK Center : formulaire, téléphone, WhatsApp et adresse à Casablanca.",
         contact_body(), current="contact.html")


if __name__ == "__main__":
    main()
