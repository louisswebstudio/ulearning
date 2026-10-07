"""Give every section heading the "Notre méthode" look: one accent word in red, tilted,
with a hand-drawn double underline and a spark (.scribble, drawn in CSS).

- Old accent styles inside h1/h2 (.accent, .swash, .xp__circled, .method__scribble) become .scribble.
- A heading without an accent gets its last word wrapped in .scribble.
- Component headings stay as they are: card titles, course text headings, CTA panels, contact block.

Idempotent. Run after build_pages.py (build_pages.py also calls it):
    python tools/headings.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

SKIP = ("lcard__title", "course__h", "cta-panel__title", "contact__title", "visit__title")

HEADING = re.compile(r'<(h[12])( class="([^"]*)")?>(.*?)</\1>', re.S)


def to_scribble(inner):
    inner = re.sub(r'<span class="method__scribble">\s*<span class="method__word">(.*?)</span>.*?</svg>\s*</span>',
                   r'<span class="scribble">\1</span>', inner, flags=re.S)
    inner = re.sub(r'<span class="(?:swash|xp__circled)">(.*?)<svg[^>]*>.*?</svg></span>',
                   r'<span class="scribble">\1</span>', inner, flags=re.S)
    inner = inner.replace('<span class="accent">', '<span class="scribble">')
    return inner


def wrap_last_word(inner):
    """Wrap the last word (with its trailing punctuation) when the heading has no accent yet."""
    m = re.search(r'([^\s>]+)(\s*)$', inner)
    if not m or "<" in m.group(1):
        return inner
    word = m.group(1)
    # keep a lone question/exclamation mark outside the accent: "Pour qui ?" -> "Pour <qui> ?"
    if word in ("?", "!", "&nbsp;?", "&nbsp;!") or word.startswith("&nbsp;"):
        return inner
    return inner[:m.start(1)] + f'<span class="scribble">{word}</span>' + m.group(2)


def style(html):
    def repl(m):
        tag, cls_attr, cls, inner = m.group(1), m.group(2) or "", m.group(3) or "", m.group(4)
        if any(s in cls.split() for s in SKIP):
            return m.group(0)
        inner = to_scribble(inner)
        if 'class="scribble"' not in inner:
            inner = wrap_last_word(inner)
        return f"<{tag}{cls_attr}>{inner}</{tag}>"
    return HEADING.sub(repl, html)


def main():
    for path in sorted(SITE.rglob("*.html")):
        src = path.read_text(encoding="utf8")
        out = style(src)
        if out != src:
            path.write_text(out, encoding="utf8")
            print("headings", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
