---
name: stamp-cover
description: Make a cover page in the "rubber-stamp / studio label" style (light grey paper, grainy distressed black ink, extended and condensed lettering, all-English labels, black mushroom logo). ALWAYS use this for any SHARPS (شارپس / شاربس) cover or any PDF made for SHARPS: the first page must be this cover. Also use when the user asks for a cover, title page or poster in this style, or says "stamp cover" or "the cover style we saved". Cairo font only.
---

# Stamp cover

Reference look: a studio stamp on grey paper. Wide flat headline, bracketed subtitle, tight condensed lines, one tall centred block, small flanking numbers (like `20` and `26`), and an info block at the bottom. Imperfect on purpose: speckled ink, rough edges, dust, hairline scratches, paper grain.

## SHARPS rule (standing order)
When the user asks for a **SHARPS cover** or **any PDF for SHARPS** (brief, deck, report, price list, anything), page 1 is always this cover, built from `examples/sharps.json`. Do not ask which style; just do it.
1. Write or generate the body PDF as usual (body pages should be matte black `#0b0b0c`, Cairo text, Space Mono numbers).
2. Copy `examples/sharps.json`, change only the tall title block (`LAUNCH` / `BRIEF`) and the info lines (`PREPARED FOR`, `INFO ID`) to fit the document. Keep the logo, the wide `SHARPS` headline, and `( DISCOVER · TRY · PROVE )`.
3. Merge: `python3 scripts/add_cover.py BODY.pdf OUT.pdf CONFIG.json`.
4. Look at page 1 of the result before sending it.
5. **No health, medical or cognitive claims anywhere in a SHARPS document** (SFDA: SHARPS is a food supplement). Taste, ritual, routine, origin and story only. Product names (FOCUS, Lion's Mane, Nine Mushrooms) are fine as names.

## Rules (do not break)
1. **Font: Cairo only** (weights 700, 800, 900). No second typeface. Width changes come from `textLength` and a vertical scale (`sy`), never from another font.
2. **All text in English**, uppercase. Names go in: company/brand names, the people's names, and the brief's own name.
3. **Layout order, top to bottom:** wide headline (weight 900, `sy` about 0.6) · bracketed subtitle (800) · two condensed lines (700, `sy` about 1.12) · tall centred block (900, `sy` about 1.3) with short numbers either side · prepared-for / by lines (700) · info lines (800).
4. **Keep the flaws.** Ink speckle, displaced edges, dust, scratches, grain and vignette are the point. Do not clean them up.
5. Colours: paper `#e8e8e4`, ink `#1b1b1a`. No other colours.
6. One idea per cover. Leave generous empty space at the top (about 20% of the page).

## How to make one
```bash
python3 .claude/skills/stamp-cover/scripts/make_cover.py CONFIG.json cover.png --jpg cover.jpg
```
- Start from `examples/growth-brief.json` and change the `t` text. Each line has `t`, `y`, `size`, `weight`, `width` (px of the stretched line), `sy`, and optional `x` (default centred).
- Page is 1240x1754 units (A4 at 150 dpi), rendered at 2x to 2480x3508.
- First run downloads Cairo from Google Fonts and caches it in `~/.cache/stamp-cover`. Needs Pillow and Chromium.
- Always look at the PNG afterwards. Check that no line is clipped, lines do not touch, and the speckle is fine rather than blotchy. If the speckle eats whole letters, the `blot` threshold in `make_cover.py` is too low.

## Logo
Add the brand mark at the top as black ink with the same distress: `"images": [{"src": "../assets/logo-mushroom.webp", "x": 620, "top": 118, "width": 210}]` (path is relative to the config file). Transparent logos use their alpha as the shape; opaque logos on white use distance from white. It is always recoloured to the ink colour. The mushroom mark in `assets/` is the one the user supplied.

## Putting the cover on an existing PDF
`python3 scripts/add_cover.py BODY.pdf OUT.pdf CONFIG.json` builds the cover, makes it a full-bleed A4 page, and merges it in front (needs `pdfunite` from poppler, or the `pypdf` package).

## Using it as the first page of a PDF you are building yourself
Print from Chromium with a named page so the image is full-bleed and carries no header or page number:
```css
@page{size:A4;margin:16mm 15mm 18mm}
@page cover{margin:0;background:#e8e8e4;@top-left{content:none}@top-right{content:none}@bottom-center{content:none}}
.cp{page:cover;width:210mm;height:297mm;page-break-after:always}
.cp img{width:210mm;height:297mm;display:block}
```
```html
<section class="cp"><img src="cover.jpg"></section>
```
Put the page background on `@page`, not on `html`, or the margins print white. Add `--print-background` to the print command.

## Matching inner pages (optional, used in the Growth Brief)
Matte black `#0b0b0c` page background with a faint noise tile, text in Cairo, numbers in Space Mono, and a small running header in mono grey (`GROWTH BRIEF // ...` left, `INFO ID: ...` right).
