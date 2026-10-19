# Islas Moriones Beach Resort: website concept (Twilight Retreat)

A static, single-page website concept with no build step. It is ready to host on GitHub Pages.

## Preview
- Quickest: open `index.html` directly in a browser.
- With a local server (closer to real hosting), run this from the project folder:
  `python -m http.server 8080` or `npx serve .`, then open http://localhost:8080

## Structure
- `index.html`: the page.
- `assets/css/styles.css`, `assets/js/main.js`: styles and interactions. Plain CSS and JS, no libraries.
- `assets/img/`: optimized, responsive image derivatives.
- `assets/brand/`: logo derivatives (transparent background), the logo mark and the favicon source.
- `edited-images/`: full-resolution cleaned copies of photos with graphic overlays removed (by cropping).
- `Initial Images/`: untouched originals, including `Logo.jpg`.
- `_tools/`: PowerShell scripts that regenerate the images (`build-images.ps1`, then `build-brand.ps1`) and a headless-Chrome QA helper.
- `_notes/content-sources.md`: internal record of every fact and its source file. Not published by GitHub Pages.

## Before going live
- Set absolute `og:image` / `twitter:image` URLs and add a canonical URL once the domain is known.
- Confirm the items listed as pending in `_notes/content-sources.md`.
- The inquiry form opens a prefilled WhatsApp or email draft. It has no backend and does not book.
