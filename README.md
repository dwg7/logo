# dwg7 logo — v0.6

**dwg7 / test new technologies.**

These files are the release assets of the dwg7 logo, version 0.6 (UNopenGIS/7 #1018).
The logo does not use the UN emblem. dwg7 is a working group of the UN Open GIS Initiative; please state this affiliation in text, not in the logo.

## Files

All SVG files are outlined. They do not need any font to display.

| Lockup | Use |
|---|---|
| `dwg7-primary*.svg` | Two lines: the wordmark and the tagline. Default choice. |
| `dwg7-horizontal*.svg` | One line. For headers and narrow spaces. |
| `dwg7-wordmark*.svg` | The wordmark only. For small sizes and slide footers. |
| `dwg7-icon.svg` | Square icon (GitHub avatar, app icon). 64 px and larger. |
| `dwg7-icon-small.svg` | Square icon with a heavier 7. 48 px and smaller (favicon). |
| `dwg7-mark.svg` | The 7 alone, no background. |
| `favicon.ico` | 16, 32 and 48 px. |
| `png/` | PNG files with transparent backgrounds, made from the SVG files. |

| Variant | Colors | Use on |
|---|---|---|
| (none) | dwg #1E5AA0, tagline #13233A | White or light backgrounds |
| `-dark` | dwg #6FA8E8, tagline #E6EDF3 | Dark backgrounds (for example GitHub dark mode) |
| `-reversed` | White on #1E5AA0 (background included) | When a blue block is wanted |
| `-mono-black` | #111111 | One-color printing |
| `-mono-white` | #FFFFFF | Photos and dark backgrounds, one color |

For a GitHub README that follows the reader's theme:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="dwg7-horizontal-dark.svg">
  <img alt="dwg7 — test new technologies." src="dwg7-horizontal.svg" height="48">
</picture>
```

## Rules

- Do not change the colors, except to the variants above.
- On dark backgrounds (for example GitHub dark mode), use the `-dark` variant: dwg #6FA8E8, tagline #E6EDF3.
- Do not stretch, rotate, outline or add effects.
- Do not redraw the wordmark with another font.
- Keep clear space around the logo. The files already include it (one quarter of the "dwg" height).
- Use the wordmark without the tagline when the logo is less than 48 px tall.

## Construction

- "dwg": Sora, weight 500, letter-spacing −0.03 em.
- "7": a stroke path, `M4 17 H62 L30 88` in a 74 × 92 box, stroke width 13, miter join. The 7 is 1.27 times the font size of "dwg" (so "dwg" is about 75 % of the 7), and it is moved 0.2 em to the left.
- Tagline: IBM Plex Mono, weight 400.
- Blue #1E5AA0, ink #13233A.

The fonts Sora and IBM Plex Mono are licensed under the SIL Open Font License 1.1. The SVG files contain outlines of their glyphs, not the fonts.

## Rebuilding the assets

The scripts in `src/` rebuild the SVG, PNG and `favicon.ico` files. The fonts they need are in `fonts/` (Sora 500 and IBM Plex Mono 400, from the npm packages `@fontsource/sora` and `@fontsource/ibm-plex-mono` 5.3.0, with their OFL license files).

Requirements: Python 3, [fontTools](https://github.com/fonttools/fonttools) (with `brotli`), [Pillow](https://python-pillow.org/), and [Playwright](https://playwright.dev/python/) with Chromium.

```sh
python3 -m venv .venv && . .venv/bin/activate
pip install fonttools brotli pillow playwright
playwright install chromium

python3 src/build.py    # outlined SVG files -> src/dist/
python3 src/tighten.py  # fit each viewBox to the ink box plus clear space
python3 src/render.py   # PNG files and favicon.ico -> src/dist/
```

Run the commands from the repository root, in this order. The output goes to `src/dist/` (not tracked by git); copy the files you want to the top level and to `png/`. A rebuild may differ slightly from the released files (a few hundredths of a unit in glyph positions, and up to about 1 % in the size of the clear space), because Chromium lays out the text.

## License

To be decided by the dwg7 co-chairs.
