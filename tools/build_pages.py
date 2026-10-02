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
    "fr": '<clipPath id="f-fr"><circle cx="30" cy="30" r="30"/></clipPath><g clip-path="url(#f-fr)"><rect width="20" height="60" fill="#0055A4"/><rect x="20" width="20" height="60" fill="#fff"/><rect x="40" width="20" height="60" fill="#EF4135"/></g>',
    "de": '<clipPath id="f-de"><circle cx="30" cy="30" r="30"/></clipPath><g clip-path="url(#f-de)"><rect width="60" height="20" fill="#000"/><rect y="20" width="60" height="20" fill="#DD0000"/><rect y="40" width="60" height="20" fill="#FFCE00"/></g>',
    "es": '<clipPath id="f-es"><circle cx="30" cy="30" r="30"/></clipPath><g clip-path="url(#f-es)"><rect width="60" height="60" fill="#AA151B"/><rect y="15" width="60" height="30" fill="#F1BF00"/></g>',
    "it": '<clipPath id="f-it"><circle cx="30" cy="30" r="30"/></clipPath><g clip-path="url(#f-it)"><rect width="20" height="60" fill="#009246"/><rect x="20" width="20" height="60" fill="#fff"/><rect x="40" width="20" height="60" fill="#CE2B37"/></g>',
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
<link rel="icon" href="{p}favicon.ico" sizes="any">
<link rel="icon" type="image/png" href="{p}assets/img/favicon-32.png">
<link rel="apple-touch-icon" href="{p}assets/img/apple-touch-icon.png">
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
    steps = c.get("steps")
    if c.get("levels"):
        steps = ("Les niveaux", "Nos niveaux suivent le Cadre européen commun de référence pour les langues (CECRL).", LEVELS)
    if steps:
        h, intro, rows = steps
        levels = f"""
      <h2 class="course__h">{h}</h2>
      <p class="course__p">{intro}</p>
      <ol class="levels">{"".join(f'''
        <li class="level"><span class="level__code">{a}</span><span class="level__name">{b}</span><span class="level__text">{t}</span></li>''' for a, b, t in rows)}
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

def language(code, name, noun, photo, about, learn, who, cta):
    """Language page data, same structure as ENGLISH."""
    return {
        "label": "Nos langues", "name": name, "tint": code, "levels": True,
        "meta": [f'<svg class="flag flag--sm" viewBox="0 0 60 60" aria-hidden="true">{FLAGS[code]}</svg> Cours {noun}', "Niveaux A1 → C1", "Groupes &amp; individuels"],
        "photo": photo, "about": about, "learn": learn, "who": who,
        "side_label": f"Cours {noun}", "side_big": "A1 → C1",
        "side": ENGLISH["side"], "cta": cta,
    }


FRANCAIS = language(
    "fr", "Français", "de français", "Photo : un cours de français chez UTALK",
    "Le français de tous les jours et le français professionnel. Que vous partiez de zéro ou que vous vouliez reprendre le français appris à l’école, nos professeurs vous font parler dès la première séance.",
    ["Tenir une conversation fluide sur la vie de tous les jours",
     "Écrire avec assurance : e-mails, rapports, lettres",
     "Utiliser le français au travail : réunions, entretiens, présentations",
     "Prendre la parole sans stress grâce aux séances au TalkLab"],
    ["Étudiants qui suivent ou préparent des études en français",
     "Professionnels qui travaillent en français au quotidien",
     "Personnes qui préparent un projet au Canada ou en France"],
    "Prêt à parler français&nbsp;?")

DEUTSCH = language(
    "de", "Deutsch", "d’allemand", "Photo : un cours d’allemand chez UTALK",
    "Pour étudier, travailler ou partir en Allemagne, en partant de zéro. Nos cours d’allemand vous donnent des bases solides et vous font pratiquer l’oral à chaque séance.",
    ["Comprendre et utiliser l’allemand du quotidien",
     "Gérer les démarches de la vie sur place : visa, logement, travail",
     "Maîtriser les bases de la grammaire allemande, pas à pas",
     "Prendre la parole sans stress grâce aux séances au TalkLab"],
    ["Futurs étudiants et candidats à une Ausbildung",
     "Professionnels qui visent un poste en Allemagne",
     "Personnes qui préparent leur installation à l’étranger"],
    "Prêt à parler allemand&nbsp;?")

ESPANOL = language(
    "es", "Español", "d’espagnol", "Photo : un cours d’espagnol chez UTALK",
    "Une langue parlée sur quatre continents, et rapide à prendre en main quand on parle déjà français. Nos cours d’espagnol vous font parler très vite, avec plaisir.",
    ["Tenir une conversation en espagnol très rapidement",
     "Comprendre les différents accents d’Espagne et d’Amérique latine",
     "Utiliser l’espagnol en voyage, au travail ou pour vos études",
     "Prendre la parole sans stress grâce aux séances au TalkLab"],
    ["Voyageurs qui veulent échanger sur place",
     "Étudiants qui ajoutent une langue à leur parcours",
     "Professionnels en contact avec des clients hispanophones"],
    "¿Listo? Prêt à parler espagnol&nbsp;?")

ITALIANO = language(
    "it", "Italiano", "d’italien", "Photo : un cours d’italien chez UTALK",
    "La langue de l’art, de la mode et de la cuisine. Pour vos études en Italie, vos voyages ou par passion, nos cours d’italien vous font parler dès la première séance.",
    ["Tenir une conversation en italien sur la vie de tous les jours",
     "Comprendre l’italien parlé, à un rythme naturel",
     "Découvrir la culture italienne à travers la langue",
     "Prendre la parole sans stress grâce aux séances au TalkLab"],
    ["Futurs étudiants en Italie",
     "Passionnés de culture italienne",
     "Voyageurs qui veulent profiter pleinement de l’Italie"],
    "Prêt à parler italien&nbsp;?")


PROG_LABEL = '<a href="programmes.html">Nos programmes</a>'

PROG_LANGUES = {
    "label": PROG_LABEL, "name": "Cours de langues", "tint": "fr", "levels": True,
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


PROG_SPEAKING = {
    "label": PROG_LABEL, "name": "Communication &amp; Speaking", "tint": "en",
    "meta": ["Expression orale", "Tous niveaux à partir de A2", "Ateliers en groupe"],
    "photo": "Photo : atelier de prise de parole",
    "about": "Des ateliers pour gagner en aisance à l’oral : prise de parole, débats et mises en situation. Moins de théorie, plus de pratique : vous parlez, on vous fait progresser.",
    "learn": ["Prendre la parole en public sans stress",
              "Structurer vos idées et convaincre",
              "Débattre, répondre et rebondir dans une conversation",
              "Réussir un entretien, une réunion ou une présentation"],
    "steps": ("Comment se passe un atelier", "Chaque atelier suit la méthode UTALK : apprendre, pratiquer, parler, progresser.", [
        ("01", "Échauffement", "Quelques minutes pour se mettre en confiance et lancer la conversation."),
        ("02", "Mise en situation", "Un thème, un rôle, un objectif : entretien, réunion, débat ou présentation."),
        ("03", "Prise de parole", "Chacun parle, devant le groupe, à son niveau et à son rythme."),
        ("04", "Feedback", "Des retours concrets du professeur pour progresser dès l’atelier suivant."),
    ]),
    "who": ["Professionnels qui veulent briller en réunion ou en entretien",
            "Étudiants qui préparent un oral, un exposé ou une soutenance",
            "Toute personne qui comprend la langue mais bloque au moment de parler"],
    "side_label": "Programme", "side_big": "Expression orale",
    "side": [("group", "Ateliers en groupe"), ("clock", "Horaires : à confirmer"),
             ("chat", "En lien avec le TalkLab"), ("pin", "Centre-ville, Casablanca")],
    "cta": "Prêt à prendre la parole&nbsp;?",
}

PROG_INTENSIFS = {
    "label": PROG_LABEL, "name": "Cours intensifs", "tint": "de",
    "meta": ["Progression rapide", "5 langues", "Groupes &amp; individuels"],
    "photo": "Photo : session intensive",
    "about": "Un rythme soutenu pour progresser vite, avant un examen, un voyage ou un nouveau poste. Plus d’heures par semaine, un objectif clair, et l’oral toujours au centre.",
    "learn": ["Gagner un niveau en peu de temps",
              "Vous préparer à une échéance précise : examen, entretien, départ",
              "Mémoriser le vocabulaire utile à votre objectif",
              "Parler avec plus d’assurance grâce à la pratique quotidienne"],
    "steps": ("Comment ça marche", "Un parcours court et cadré, construit autour de votre objectif.", [
        ("01", "Test de niveau", "On fait le point sur votre niveau à l’oral et à l’écrit."),
        ("02", "Objectif &amp; planning", "On fixe ensemble l’objectif, la durée et le rythme des séances."),
        ("03", "Sessions intensives", "Des séances rapprochées, avec beaucoup de pratique orale."),
        ("04", "Bilan final", "On mesure vos progrès et on vous conseille pour la suite."),
    ]),
    "who": ["Candidats à un examen ou à des études à l’étranger",
            "Professionnels qui ont un nouveau poste ou une mission",
            "Personnes qui partent bientôt en voyage ou s’installent à l’étranger"],
    "side_label": "Programme", "side_big": "Intensif",
    "side": [("sparkle", "Rythme soutenu"), ("calendar", "Durée et horaires : à confirmer"),
             ("group", "En groupe ou en individuel"), ("chat", "Pratique orale au TalkLab"),
             ("pin", "Centre-ville, Casablanca")],
    "cta": "Prêt à accélérer&nbsp;?",
}

PROG_INDIVIDUELS = {
    "label": PROG_LABEL, "name": "Cours individuels", "tint": "it",
    "meta": ["1 : 1 · Sur mesure", "5 langues", "Tous niveaux A1 → C1"],
    "photo": "Photo : cours particulier",
    "about": "Un professeur rien que pour vous, avec un programme et des horaires adaptés à vos objectifs. Vous avancez à votre rythme, et chaque minute du cours est consacrée à vos besoins.",
    "learn": ["Ce dont vous avez besoin : quotidien, travail, études ou examen",
              "Corriger vos propres erreurs, avec une attention personnelle",
              "Parler davantage, car tout le cours est pour vous",
              "Avancer à votre rythme, plus vite ou plus lentement selon vos besoins"],
    "steps": ("Comment ça marche", "Un cours construit pour vous, du premier échange au suivi.", [
        ("01", "Premier échange", "On parle de vos objectifs, de votre niveau et de vos disponibilités."),
        ("02", "Programme sur mesure", "Votre professeur prépare un programme adapté à votre objectif."),
        ("03", "Cours 1 : 1", "Des séances en tête-à-tête, centrées sur l’oral et sur vos besoins."),
        ("04", "Suivi &amp; ajustements", "On mesure vos progrès et on ajuste le programme en continu."),
    ]),
    "who": ["Professionnels avec un emploi du temps chargé ou irrégulier",
            "Personnes avec un objectif précis : examen, entretien, départ à l’étranger",
            "Personnes qui préfèrent apprendre sans groupe, à leur rythme"],
    "side_label": "Programme", "side_big": "1 : 1",
    "side": [("user", "Un professeur pour vous seul"), ("clock", "Horaires flexibles : à confirmer"),
             ("sparkle", "Programme personnalisé"), ("chat", "Accès au TalkLab"),
             ("pin", "Centre-ville, Casablanca")],
    "cta": "Prêt à apprendre à votre rythme&nbsp;?",
}

# ---------------------------------------------------------------------------
# Méthode
# ---------------------------------------------------------------------------
STEPS = [
    ("Learn", "en classe", "En classe", "Photo : un cours en petit groupe",
     "Des cours en petits groupes, avec des professeurs qui adaptent le rythme à votre niveau.",
     ["Petits groupes, pour que chacun participe",
      "Un programme par niveau, de A1 à C1 (CECRL)",
      "Des professeurs qui mettent l’oral au centre du cours"], None),
    ("Practice", "à chaque séance", "Mises en situation", "Photo : un jeu de rôle en classe",
     "Jeux, mises en situation et activités pour utiliser la langue tout de suite.",
     ["Jeux et activités pour retenir sans apprendre par cœur",
      "Mises en situation : au restaurant, au travail, en voyage",
      "On utilise ce qu’on vient d’apprendre, dès la même séance"], None),
    ("Speak", "au TalkLab", "TalkLab", "Photo : une conversation au TalkLab",
     "Vous échangez dans de vraies conversations et vous prenez confiance à l’oral.",
     ["Conversations et débats en petits groupes",
      "Jeux et événements pour parler sans stress",
      "Ouvert à tous les niveaux"], ("talklab.html", "Découvrir le TalkLab")),
    ("Improve", "chaque mois", "Suivi mensuel", "Photo : un point de suivi avec un professeur",
     "Un suivi régulier de vos progrès, pour savoir où vous en êtes et quoi travailler.",
     ["Un point régulier sur vos progrès",
      "Des retours concrets de vos professeurs",
      "Le passage au niveau suivant quand vous êtes prêt"], None),
]


def methode_body():
    overview = section_from_home("methode").replace("        Notre\n", "        Les 4\n", 1).replace(
        '<span class="method__word">méthode</span>', '<span class="method__word">étapes</span>', 1)
    cards = ""
    for i, (en, when, tag, photo, text, points, link) in enumerate(STEPS, 1):
        more = f'\n            <a href="{link[0]}" class="prog__more">{link[1]} <span aria-hidden="true">→</span></a>' if link else ""
        cards += f"""
      <li class="prog prog--{i}">
        <div class="prog__card">
          <svg class="prog__swirl" viewBox="0 0 600 500" preserveAspectRatio="none" aria-hidden="true"><path d="M-20 470 C160 380 330 300 640 140" /><path d="M120 520 C260 430 420 330 640 250" /></svg>
          <div class="prog__content">
            <span class="prog__num">0{i}</span>
            <h3 class="prog__name">{en} — {when}</h3>
            <p class="prog__text">{text}</p>
            <ul class="course__list prog__points">{lis(points)}</ul>
            <span class="prog__tag">{tag}</span>{more}
          </div>
          <div class="prog__photo">{ph(photo)}</div>
        </div>
      </li>"""
    swash = '<span class="swash">détail<svg viewBox="0 0 160 30" preserveAspectRatio="none" aria-hidden="true"><path d="M4 22 C40 8 110 4 156 12" /></svg></span>'
    return page_head("Notre méthode", "Learn. Practice. Speak. Improve.",
                     lead="Moins de théorie, plus de pratique : chaque étape vous rapproche de la vraie conversation.") + f"""
<!-- ============ 4 STEPS OVERVIEW (ref: Brightpath "How it works", from the home page) ============ -->
{overview}

<!-- ============ STEPS IN DETAIL (ref: Kidora stacked program cards) ============ -->
<section class="progs">
  <div class="container">
    <div class="progs__head">
      <div>
        <p class="label">Étape par étape</p>
        <h2 class="progs__title">Chaque étape, en {swash}</h2>
      </div>
    </div>
    <ol class="progs__list">{cards}
    </ol>
  </div>
</section>

<!-- ============ ÉTUDIANTS (ref: Kidora photo + quote cards, from the home page) ============ -->
{section_from_home("etudiants")}
""" + cta("Prêt à tester la méthode UTALK&nbsp;?")


# ---------------------------------------------------------------------------
# Programmes overview
# ---------------------------------------------------------------------------
PROGS = [
    (1, "fr", "Cours de langues", "programmes/cours-de-langues.html", "Photo : cours en groupe",
     "Des cours en groupe pour apprendre l’anglais, le français, l’allemand, l’espagnol ou l’italien, du niveau débutant au niveau avancé.",
     [("sparkle", "A1 → C1"), ("group", "En groupe"), ("chat", "5 langues")]),
    (2, "en", "Communication &amp; Speaking", "programmes/communication-speaking.html", "Photo : atelier de prise de parole",
     "Des ateliers pour gagner en aisance à l’oral : prise de parole, débats et mises en situation.",
     [("chat", "Expression orale"), ("sparkle", "À partir de A2"), ("group", "Ateliers en groupe")]),
    (3, "de", "Cours intensifs", "programmes/cours-intensifs.html", "Photo : session intensive",
     "Un rythme soutenu pour progresser vite, avant un examen, un voyage ou un nouveau poste.",
     [("calendar", "Progression rapide"), ("chat", "5 langues"), ("group", "Groupes &amp; individuels")]),
    (4, "it", "Cours individuels", "programmes/cours-individuels.html", "Photo : cours particulier",
     "Un professeur rien que pour vous, avec un programme et des horaires adaptés à vos objectifs.",
     [("user", "1 : 1 · Sur mesure"), ("chat", "5 langues"), ("sparkle", "A1 → C1")]),
]


def programmes_body():
    cards = ""
    for n, tint, name, href, photo, text, meta in PROGS:
        pills = "".join(f'<li><span class="side-ico side-ico--{i}"></span>{t}</li>' for i, t in meta)
        cards += f"""
      <a href="{href}" class="lcard lcard--{tint}">
        <div class="lcard__media">{ph(photo)}<span class="lcard__badge"><span class="lcard__num lcard__num--{n}">0{n}</span>Programme</span></div>
        <h2 class="lcard__title">{name}</h2>
        <p class="lcard__text">{text}</p>
        <ul class="lcard__meta">{pills}</ul>
        <span class="lcard__foot">Voir le programme <span class="lcard__go" aria-hidden="true"></span></span>
      </a>"""
    return page_head(
        "Nos programmes",
        "Choisissez votre programme",
        "Quatre façons d’apprendre, un même objectif : vous faire parler.",
    ) + f"""
<!-- ============ PROGRAMME CARDS (ref: BrightMind "Browse Our Courses" grid, 2 columns) ============ -->
<section class="lcards-sec">
  <div class="container lcards lcards--2">{cards}
      <a href="contact.html" class="lcard lcard--cta">
        <h2 class="lcard__title">Quel programme choisir&nbsp;?</h2>
        <p class="lcard__text">Dites-nous votre objectif : on vous conseille le bon programme, la bonne langue et le bon niveau.</p>
        <span class="lcard__foot">On vous conseille <span class="lcard__go" aria-hidden="true"></span></span>
      </a>
  </div>
</section>
""" + cta("Prêt à commencer&nbsp;?")


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


# ---------------------------------------------------------------------------
# Expérience (covers = Instagram reel thumbnails, 360x640; swap for originals when the client sends them)
# ---------------------------------------------------------------------------
IG = "https://www.instagram.com/utalk_center/"
CIRCLE = '<svg viewBox="0 0 200 80" preserveAspectRatio="none" aria-hidden="true"><path d="M18 52 C4 30 40 8 104 8 C170 8 198 26 192 46 C186 68 130 76 88 74 C44 72 10 62 12 44 C14 30 40 18 70 14" /></svg>'

XP_FILTERS = [("centre", "UTALK Center"), ("classrooms", "Classrooms"),
              ("communication", "Communication"), ("activities", "Activities")]

REELS = [
    ("Dd8u3z4N--g", "activities", "Jeux de société et de cartes autour d’une table"),
    ("Dd1DMVoNF_K", "communication", "Mise en situation au bureau"),
    ("DdrEsgFtw_t", "centre", "L’accueil d’UTALK Center"),
    ("Ddln2h3tY5T", "classrooms", "Une étudiante dans une salle de cours"),
    ("DdgZwF1tbxp", "centre", "La réception et le logo UTALK"),
    ("DbDsbRftSWF", "activities", "Un jeu en équipe avec des ballons"),
    ("DdYjCJtNuX3", "centre", "Visite de l’accueil du centre"),
    ("DavO0NTNy_q", "classrooms", "Un cours devant l’écran interactif"),
    ("DXmmpJqDJwf", "communication", "Un étudiant prend la parole"),
    ("DdTmEAyNO6t", "centre", "L’entrée du centre, au 12e étage"),
    ("DYj_qf_scYO", "communication", "Une étudiante en salle de cours"),
    ("DVbeFAijA2A", "centre", "Le couloir et l’espace d’accueil"),
]


def experience_body():
    labels = dict(XP_FILTERS)
    filters = "".join(
        f'\n        <button type="button" class="filter" data-filter="{k}" aria-pressed="false">{v}</button>'
        for k, v in XP_FILTERS)
    reels = "".join(
        f'\n      <li class="tile" data-cat="{cat}"><a class="reel" href="{IG}reel/{rid}/" target="_blank" rel="noopener" '
        f'aria-label="{alt} (vidéo Instagram)"><img src="assets/img/instagram/{rid}.jpg" alt="" width="361" height="640" loading="lazy">'
        f'<span class="reel__play" aria-hidden="true"></span><span class="chip">{labels[cat]}</span></a></li>'
        for rid, cat, alt in REELS)
    words = "<span>Classrooms</span><i>✦</i><span>Communication</span><i>✦</i><span>TalkLab</span><i>✦</i><span>Activities</span><i>✦</i><span>Events</span><i>✦</i>"
    return page_head(
        "Expérience",
        f'Découvrez l’ambiance <span class="xp__circled">UTALK{CIRCLE}</span>',
        "Les cours, les ateliers, les jeux et les gens : voici à quoi ressemble la vie au centre.",
    ) + f"""
<!-- ============ VIDEO BANNER (ref: Kidora "Discover our learning space") ============ -->
<section class="xp">
  <div class="xp__banner">
    <div class="xp__media ph ph--dark"><span class="ph__icon"></span><span class="ph__label">Vidéo plein écran : visite du centre (fichier original à demander au client)</span></div>
    <div class="xp__overlay"></div>
    <div class="container xp__banner-inner">
      <p class="eyebrow eyebrow--light">✦ Au cœur du centre</p>
      <h2 class="xp__title">Ici, on apprend en parlant.</h2>
      <button type="button" class="xp__play" aria-label="Lire la vidéo de présentation"><span class="xp__play-icon" aria-hidden="true"></span>Voir la vidéo</button>
    </div>
  </div>
  <div class="marquee" aria-hidden="true">
    <div class="marquee__track">
      {words}
      {words}
      {words}
    </div>
  </div>
</section>

<!-- ============ GALLERY: Instagram reels, filters as on the home page ============ -->
<section class="xp">
  <div class="container xp__gallery">
    <div class="xp__head">
      <h2 class="xp__subtitle">Le centre en vidéos</h2>
      <div class="filters" role="group" aria-label="Filtrer les vidéos">
        <button type="button" class="filter is-active" data-filter="all" aria-pressed="true">Tout</button>{filters}
      </div>
    </div>
    <ul class="tiles tiles--reels">{reels}
    </ul>
    <div class="xp__more">
      <a href="{IG}" class="btn-pill" target="_blank" rel="noopener">Suivez-nous sur Instagram <span class="btn-pill__icon" aria-hidden="true"></span></a>
    </div>
  </div>
</section>
""" + cta("Envie de vivre l’expérience ?")


# ---------------------------------------------------------------------------
# Langues overview (ref: BrightMind /course listing, 3-column course cards; author + price row -> "Voir le cours")
# ---------------------------------------------------------------------------
LANGS = [
    ("en", "English", "langues/english.html", "Photo : un cours d’anglais",
     "La langue internationale, pour vos études, votre travail et vos voyages."),
    ("fr", "Français", "langues/francais.html", "Photo : un cours de français",
     "Le français de tous les jours et le français professionnel."),
    ("de", "Deutsch", "langues/deutsch.html", "Photo : un cours d’allemand",
     "Pour étudier, travailler ou partir en Allemagne."),
    ("es", "Español", "langues/espanol.html", "Photo : un cours d’espagnol",
     "Une langue parlée sur quatre continents, à apprendre en parlant."),
    ("it", "Italiano", "langues/italiano.html", "Photo : un cours d’italien",
     "La langue de l’art, de la mode et de la cuisine."),
]


def langues_body():
    meta = ('<ul class="lcard__meta"><li><span class="side-ico side-ico--sparkle"></span>A1 → C1</li>'
            '<li><span class="side-ico side-ico--group"></span>Groupes &amp; individuels</li>'
            '<li><span class="side-ico side-ico--chat"></span>TalkLab</li></ul>')
    cards = "".join(f"""
      <a href="{href}" class="lcard lcard--{code}">
        <div class="lcard__media">{ph(photo)}<span class="lcard__badge"><svg class="flag" viewBox="0 0 60 60" aria-hidden="true">{FLAGS[code]}</svg>{code.upper()}</span></div>
        <h2 class="lcard__title">{name}</h2>
        <p class="lcard__text">{text}</p>
        {meta}
        <span class="lcard__foot">Voir le cours <span class="lcard__go" aria-hidden="true"></span></span>
      </a>""" for code, name, href, photo, text in LANGS)
    return page_head(
        "Nos langues",
        "Choisissez votre langue",
        "Cinq langues, cinq niveaux, et toujours le même objectif : vous faire parler.",
    ) + f"""
<!-- ============ LANGUAGE CARDS (ref: BrightMind "Browse Our Courses" grid) ============ -->
<section class="lcards-sec">
  <div class="container lcards">{cards}
      <a href="contact.html" class="lcard lcard--cta">
        <h2 class="lcard__title">Pas sûr de votre niveau&nbsp;?</h2>
        <p class="lcard__text">Dites-nous où vous en êtes : on vous conseille la bonne langue, le bon niveau et le bon format.</p>
        <span class="lcard__foot">On vous conseille <span class="lcard__go" aria-hidden="true"></span></span>
      </a>
  </div>
</section>
""" + cta("Prêt à choisir votre langue&nbsp;?")


def main():
    page("programmes.html", "Nos programmes · UTALK Center",
         "Les programmes d’UTALK Center à Casablanca : cours de langues, communication &amp; speaking, cours intensifs et cours individuels.",
         programmes_body())
    page("methode.html", "Notre méthode · UTALK Center",
         "La méthode UTALK Center : Learn, Practice, Speak, Improve. Quatre étapes pour parler une langue.",
         methode_body(), current="methode.html")
    page("langues.html", "Nos langues · UTALK Center",
         "Cours d’anglais, de français, d’allemand, d’espagnol et d’italien à Casablanca, du niveau A1 au C1.",
         langues_body(), current="langues.html")
    page("experience.html", "Expérience · UTALK Center",
         "L’expérience UTALK Center en images et en vidéos : cours, ateliers de communication et activités à Casablanca.",
         experience_body(), current="experience.html")
    page("langues/english.html", "English · UTALK Center",
         "Cours d’anglais à Casablanca chez UTALK Center : niveaux A1 à C1, en groupe ou en individuel.",
         course_body(ENGLISH), current="langues.html")
    page("langues/francais.html", "Français · UTALK Center",
         "Cours de français à Casablanca chez UTALK Center : niveaux A1 à C1, en groupe ou en individuel.",
         course_body(FRANCAIS), current="langues.html")
    page("langues/deutsch.html", "Deutsch · UTALK Center",
         "Cours d’allemand à Casablanca chez UTALK Center : niveaux A1 à C1, en groupe ou en individuel.",
         course_body(DEUTSCH), current="langues.html")
    page("langues/espanol.html", "Español · UTALK Center",
         "Cours d’espagnol à Casablanca chez UTALK Center : niveaux A1 à C1, en groupe ou en individuel.",
         course_body(ESPANOL), current="langues.html")
    page("langues/italiano.html", "Italiano · UTALK Center",
         "Cours d’italien à Casablanca chez UTALK Center : niveaux A1 à C1, en groupe ou en individuel.",
         course_body(ITALIANO), current="langues.html")
    page("programmes/cours-de-langues.html", "Cours de langues · UTALK Center",
         "Cours de langues en groupe à Casablanca : anglais, français, allemand, espagnol, italien.",
         course_body(PROG_LANGUES))
    page("programmes/communication-speaking.html", "Communication & Speaking · UTALK Center",
         "Ateliers de communication et de prise de parole à Casablanca : débats, mises en situation, entretiens.",
         course_body(PROG_SPEAKING))
    page("programmes/cours-intensifs.html", "Cours intensifs · UTALK Center",
         "Cours de langues intensifs à Casablanca : progresser vite avant un examen, un voyage ou un nouveau poste.",
         course_body(PROG_INTENSIFS))
    page("programmes/cours-individuels.html", "Cours individuels · UTALK Center",
         "Cours de langues individuels à Casablanca : un professeur pour vous seul, un programme et des horaires sur mesure.",
         course_body(PROG_INDIVIDUELS))
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
