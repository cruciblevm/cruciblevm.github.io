<img src="./assets/branding/logo-readme.svg" alt="CrucibleVM (alpha)" width="352" align="right">

# cruciblevm.github.io

Source for [cruciblevm.github.io](https://cruciblevm.github.io/) — the landing page for
[CrucibleVM](https://github.com/SiteNetSoft/crucible), open-source profile-guided optimization
for GraalVM Community Edition `native-image`.

- Static HTML/CSS with a small vanilla-JS color-scheme toggle, no build step. Edit
  `index.html`, `assets/css/main.css`, and `assets/js/theme.js` directly.
- The color-scheme toggle is adapted from [sitenetsoft.org](https://sitenetsoft.org/). The choice
  persists in localStorage under `cruciblevm-color-scheme` (values `system | light | dark`).
- `assets/branding/` is a copy of `crucible/branding/` from the main repository; update it there
  first. Favicons and `assets/og-banner.png` are rendered from those SVGs with Inkscape.
- Benchmark figures on the page come from `crucible/README.md` and `crucible/ROADMAP.md`; keep
  them in step when those change.
- Served by GitHub Pages from the `main` branch root.
