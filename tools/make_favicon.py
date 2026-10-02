"""Generate the favicons from the "U" mark of the logo (site/assets/img/utalk-logo.png).

The mark is centred on a white rounded square so it stays visible on dark browser tabs.
Writes site/favicon.ico (16/32/48), site/assets/img/favicon-32.png and apple-touch-icon.png (180).

Run from the project root:  python tools/make_favicon.py
"""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
LOGO = SITE / "assets" / "img" / "utalk-logo.png"

SIZE = 512     # master size, downscaled for each output
MARK = 0.70    # mark height as a share of the icon
RADIUS = 0.22  # corner radius as a share of the icon


def u_mark():
    logo = Image.open(LOGO).convert("RGBA")
    # The U is the black shape left of the red "TALK" (x < 450), above the subtitle line (y < 410).
    left = logo.crop((0, 0, 420, 410))
    px = left.load()
    for y in range(left.height):
        for x in range(left.width):
            r, g, b, a = px[x, y]
            if a < 40 or r > 120:  # keep only the dark pixels of the mark
                px[x, y] = (0, 0, 0, 0)
    return left.crop(left.getbbox())


def master():
    mark = u_mark()
    h = int(SIZE * MARK)
    w = round(mark.width * h / mark.height)
    mark = mark.resize((w, h), Image.LANCZOS)
    icon = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    ImageDraw.Draw(icon).rounded_rectangle((0, 0, SIZE - 1, SIZE - 1), radius=int(SIZE * RADIUS), fill="white")
    icon.alpha_composite(mark, ((SIZE - w) // 2, (SIZE - h) // 2))
    return icon


def main():
    icon = master()
    img = SITE / "assets" / "img"
    icon.save(SITE / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    icon.resize((32, 32), Image.LANCZOS).save(img / "favicon-32.png")
    # iOS adds its own rounded corners and ignores transparency: use a full white square.
    touch = Image.new("RGBA", (SIZE, SIZE), "white")
    touch.alpha_composite(icon)
    touch.convert("RGB").resize((180, 180), Image.LANCZOS).save(img / "apple-touch-icon.png")
    for p in ("favicon.ico", "assets/img/favicon-32.png", "assets/img/apple-touch-icon.png"):
        print("wrote", (SITE / p).relative_to(ROOT))


if __name__ == "__main__":
    main()
