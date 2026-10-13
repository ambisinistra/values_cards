# PsychoMirror

A one-page tool for the **Personal Values Card Sort**. A person sorts 100 value cards, ranks their top values, and copies the result with an analysis prompt into Claude (Opus recommended). Claude then writes a professional psychological profile: value structure, personality characteristics, behavioural patterns, conflict zones and risks, resources, and hypotheses to test in an interview. The prompt asks for direct, evidence-based conclusions with a confidence level for each, and no softening or flattery.

Languages: English, Russian, Hungarian. Everything runs in the browser, and the page sends no data anywhere.

## How it works

1. **Sort.** All 100 cards go into five piles: Most important, Very important, Important, Somewhat important, Not important. Cards are shown in random order.
2. **Review.** The person checks the piles and moves cards. Pile sizes are not limited.
3. **Rank.** The person ranks all cards in the Most important pile.
4. **Copy.** There are three copy options:
   - the sort with the prompt, ready to paste;
   - the sort only, as a plain list;
   - the prompt only, without the person's data. The prompt is also available at any time from the Prompt button in the header.

This follows the 2011 update by the card sort's authors (5 piles, then ranking the top pile), without their suggested limit of 5–10 top values.

## Schwartz pole indices

The page computes four indices for the higher-order poles of the refined Schwartz value theory (2012): Openness to change, Conservation, Self-enhancement and Self-transcendence. The method:

- pile score from 0 (Not important) to 4 (Most important);
- pole index = mean score of the pole's cards minus the person's mean score over all 100 cards;
- border values are split equally between two poles;
- cards with an ambiguous mapping count with weight 0.5;
- cards outside the Schwartz model (23 of 100) are not counted.

The card-to-value mapping is an expert judgement, not a validated scale. The indices help structure the analysis. They are not a psychometric measurement.

## Files

| Path | What it is |
|---|---|
| `value_cards.py` | Single source of the 100 cards: EN text, RU and HU translations, Schwartz mapping, sensitive-card flags. Run it to validate the set and export `value_cards_100.csv`. |
| `prompts/analysis_{en,ru,hu}.md` | The analysis prompt. `{{LAYOUT}}` marks where the sorting data goes. |
| `src/template.html` | Page markup, styles and logic. |
| `build.py` | Builds `index.html` (for GitHub Pages and for sending as a file) and `dist/artifact.html`. |

After editing cards, prompts or the template, run:

```bash
python3 build.py
```

## Sources and licence

Cards: *Personal Values Card Sort* (update 2011), W. R. Miller, J. C'de Baca, D. B. Matthews, P. L. Wilbourne, University of New Mexico. The authors place it in the public domain: it "may be copied or adapted without further permission". The English names and definitions are kept verbatim.

The Russian and Hungarian versions are our own adaptations. They have not been checked by back-translation or with native-speaker reviewers yet.

Code: MIT licence, see `LICENSE`.

This tool supports self-reflection. It is not a psychological test and does not replace a professional consultation.
