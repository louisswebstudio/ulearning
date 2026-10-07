# UTALK Center: WordPress theme

The upload file is `dist/utalk-theme.zip`. It is built from the static site in `site/`.

## Install on the live site

1. WordPress admin: **Appearance > Themes > Add New Theme > Upload Theme**, choose `utalk-theme.zip`, then **Install Now** and **Activate**.
2. Open the site once. On activation the theme:
   - creates the pages: Accueil, Nos langues (+ English, Français, Deutsch, Español, Italiano), Nos programmes (+ 4 programmes), Notre méthode, Expérience, TalkLab, Étudiants, UTALK Center, Contact. Pages that already exist at the same address are reused, not duplicated.
   - sets **Accueil** as the home page, unless a static home page is already set.
   - switches permalinks to `/%postname%/`, but only if they were on "Plain".
3. **Settings > General**: set the site title to `UTALK Center`. It shows in the browser tab.

Each page's design lives in its theme template (`page-<slug>.php`), so the WordPress editor content of those pages isn't shown. To change text or photos, edit `site/` and rebuild (see below).

## Contact form

- Every request is saved in **Messages UTALK** in the admin menu and emailed to the admin address (**Settings > General > Administration Email Address**).
- Many hosts don't send email reliably. Install **WP Mail SMTP** and connect a real mailbox; messages are saved in the admin either way.
- Spam is filtered by a hidden honeypot field.

## WooCommerce

- Supported and styled: shop, product pages, cart, checkout, account.
- There's no shop link in the menu yet, since nothing is for sale. Add one when products exist.

## Rebuild after changes

```bash
python3 tools/build_pages.py      # regenerate inner pages + style headings (tools/headings.py)
python3 tools/fill_photos.py      # put the photos back into the placeholders
python3 tools/build_wp_theme.py   # write wp-theme/utalk and dist/utalk-theme.zip
```

To update the live site, upload the new zip under Appearance > Themes > Add New Theme > Upload Theme. WordPress offers **Replace active with uploaded**.

## Still needed from the client

- Real phone and WhatsApp number (currently `+212 6 00 00 00 00` everywhere).
- Facebook, TikTok and YouTube links (currently `#`), or remove the icons.
- Student testimonials: name, quote, level and photo or video for each. The 4 cards on Accueil and Étudiants still hold sample text.
- Original photos and videos. The current photos are Instagram reel covers (360×640), which are fine for the site but soft on large screens.
