# Maintaining the profile

The README uses self-contained SVG cards with embedded fonts. The paper-and-ink design was inspired by [Avi Vashishta's profile](https://github.com/AVIVASHISHTA29), then adapted for Antonio's work. The scripts were independently written for this profile.

The Background card sits before the toolkit. Its introduction, roles and date ranges are adapted from [Antonio's LinkedIn profile](https://www.linkedin.com/in/antonio-potenza-345b551a7/), read on 13 November 2026. Update `background()` when these details change. LinkedIn, APT Systems and Instagram use dedicated SVG icons wrapped in normal README links.

The animated toolkit replaces the contribution calendar and activity chart. Its twelve tiles show the tools listed in the existing profile. Icons are embedded from Devicon (MIT; license included under `assets/tool-icons/`), with an original TimescaleDB monogram. No external image service or contribution scraping is needed.

The GitHub Action rebuilds cards when their scripts, tool icons or profile configuration change, and can also be run manually. It has no daily schedule.

Normal update:

```sh
python scripts/render_cards.py
```

To replace the portrait or regenerate font subsets:

```sh
python -m pip install -r scripts/requirements-art.txt
python scripts/prepare_card_assets.py
python scripts/render_cards.py
```

The portrait preparation expects `assets/antonio-cartoon.png` with alpha. Adjust its face crop if replacing the artwork. `assets/antonio-avatar.png` is a compressed PNG copy for GitHub's avatar upload limit. Original fonts come from Google Fonts; their licenses are in `fonts/`. The image generation prompt is recorded in `assets/README.md`.

The company website is [aptsystems.it](https://aptsystems.it); the Aptios card links to it. Animation is confined to SVG CSS and SMIL, with reduced-motion support. GitHub renders the cards as images and the README provides their links.
