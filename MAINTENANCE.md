# Maintaining the profile

The README uses self-contained SVG cards with embedded fonts. It follows the current paper-and-ink layout of [Avi Vashishta's profile](https://github.com/AVIVASHISHTA29), rather than the older terminal layout described in his article. The scripts were independently written for Antonio's profile. No personal statistics or portrait from the reference are reused.

The GitHub Action fetches the public contributions calendar daily at 06:17 UTC and regenerates `cards/`. The monthly graph, totals, active days, streaks and best day come from the same calendar snapshot. The graph contains GitHub's 53-week calendar; the monthly chart shows the most recent 12 calendar months. GitHub can delay scheduled runs.

Normal update:

```sh
python -m pip install -r scripts/requirements.txt
python scripts/fetch_contributions.py
python scripts/render_cards.py
python -m unittest discover -s scripts -p 'test_*.py'
```

To replace the portrait or regenerate font subsets:

```sh
python -m pip install -r scripts/requirements-art.txt
python scripts/prepare_card_assets.py
python scripts/render_cards.py
```

The portrait preparation expects `assets/antonio-cartoon.png` with alpha. Adjust its face crop if replacing the artwork. Original fonts come from Google Fonts; their licenses are in `fonts/`. The image generation prompt is recorded in `assets/README.md`.

Animation is confined to SVG CSS and SMIL, with reduced-motion support. GitHub renders the cards as images. Links around cards belong to the README, so they work without JavaScript. The original terminal artwork remains in repository history and is no longer displayed.
