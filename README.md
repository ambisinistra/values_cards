# PsychoMirror

A one-page tool for the **Personal Values Card Sort**. A person plays through 100 value cards as a card game, dealing them onto four decks, and copies the result with an analysis prompt into Claude (Opus recommended). Claude then writes a professional psychological profile: value structure, personality profile, behavioural patterns, areas of conflict, resources, socialisation context, suitable professions and work environments, relationships, and practical recommendations.

Languages: English, Russian, Hungarian, Serbian (Latin script). Everything runs in the browser, and the page sends no data anywhere.

## How it works

1. **Sort.** The sort is played as a card game. **Start** deals a hand of 5 random cards to the top of the screen; below it, four decks fill the board: Very important, Important, Unsure, Not important. When the hand is empty the next 5 are dealt, 20 rounds in all.
   - Drag a card onto a deck with the mouse or a finger, or tap a card and then a deck. Keys 1–4 place the selected card (or the first one), ← and → change the selection, Backspace undoes.
   - Every card stays visible: the top card of a deck shows its definition, the cards under it show as title strips that get thinner as the deck grows, so the board always fits on the screen.
   - Drag a deck's top card to another deck or back to the hand. Tap any card on the board to read it, move it or take it back. **Back** undoes any move.
   - On phones the hand shows titles only (the selected card's definition appears below it) and the decks sit 2 × 2.
   - Progress is kept in the browser, so the game can be closed and continued later.
2. **Review.** The person checks the decks and moves cards. Deck sizes are not limited. The steps in the header let the person go back to sorting or review at any time.
3. **Copy.** There are three copy options:
   - the sort with the prompt, ready to paste;
   - the sort only, as a plain list;
   - the prompt only, without the person's data. The prompt is also available at any time from the Prompt button in the header.

The "Unsure" deck is not a point on the importance scale. It marks values the person has no settled position on, and the prompt asks the model to interpret it as a separate signal.

## Schwartz pole indices

The page computes four indices for the higher-order poles of the refined Schwartz value theory (2012): Openness to change, Conservation, Self-enhancement and Self-transcendence. The method:

- deck score: Not important 0, Important 1, Very important 2; Unsure cards get no score and are left out of the indices;
- pole index = mean score of the pole's cards minus the person's mean score over all scored cards;
- border values are split equally between two poles;
- cards with an ambiguous mapping count with weight 0.5;
- cards outside the Schwartz model (23 of 100) are not counted.

The card-to-value mapping is an expert judgement, not a validated scale. The indices help structure the analysis. They are not a psychometric measurement.

## Files

| Path | What it is |
|---|---|
| `value_cards.py` | Single source of the 100 cards: EN text, RU, HU and SR translations, Schwartz mapping, sensitive-card flags. Run it to validate the set and export `value_cards_100.csv`. |
| `prompts/analysis_{en,ru,hu,sr}.md` | The analysis prompt. `{{LAYOUT}}` marks where the sorting data goes. |
| `src/template.html` | Page markup, styles and logic. |
| `build.py` | Builds `index.html` (for GitHub Pages and for sending as a file) and `dist/artifact.html`. |
| `Dockerfile` | Two stages: `python:3.12-alpine` runs `build.py`, `nginx:1.27-alpine` serves the built `index.html`. |
| `docker/default.conf.template` | nginx config; listens on `$PORT` (80 by default, set by hosts such as Render). |

After editing cards, prompts or the template, run:

```bash
python3 build.py
```

## Running it

The page is one self-contained file: open `index.html` in a browser. Copying to the clipboard can be blocked on `file://` pages (the page then selects the text for Ctrl+C), so a local server is handier:

```bash
python3 -m http.server 8000      # then open http://localhost:8000
```

Or with Docker. The image builds the page from the sources and serves it with nginx:

```bash
docker build -t psychomirror .
docker run --rm -p 8080:80 psychomirror      # then open http://localhost:8080
```

On hosts that pass a `PORT` variable (Render sets 10000), nginx listens on that port instead of 80.

## Sources and licence

Cards: *Personal Values Card Sort* (update 2011), W. R. Miller, J. C'de Baca, D. B. Matthews, P. L. Wilbourne, University of New Mexico. The authors place it in the public domain: it "may be copied or adapted without further permission". The English names and definitions are kept verbatim.

The Russian, Hungarian and Serbian versions are our own adaptations. They have not been checked by back-translation or with native-speaker reviewers yet.

Code: MIT licence, see `LICENSE`.

This tool supports self-reflection. It is not a psychological test and does not replace a professional consultation.
