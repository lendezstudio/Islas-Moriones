# Islas Moriones Beach Resort: website

Static, single-page site with no build step, ready for GitHub Pages.

- `main` branch: version 1, the Twilight Retreat concept.
- `version-2` branch: the digital brochure built from the client's assets and questionnaire. Official colours #009891, white, gray and black; booking through Little Hotelier; no rates on the site.

## Preview
Open `index.html` in a browser, or run `python -m http.server 8080` in this folder and visit http://localhost:8080.

## Structure
- `index.html`, `assets/css/styles.css`, `assets/js/main.js`: the page, plain CSS and JS.
- `assets/img/`: optimized images. `assets/brand/`: logo derivatives (teal, white, full colour; transparent).
- `edited-images/`: full-size cleaned copies of photos (overlays cropped out).
- `Initial Images/`, `Assets from Client/`: untouched originals.
- `_tools/`: PowerShell scripts that rebuild the images (`build-images.ps1`, then `build-brand.ps1`), plus a headless-Chrome QA helper.
- `_notes/`: internal content-source record (git-ignored).
