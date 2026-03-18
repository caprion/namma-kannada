# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Namma Kannada** — a static web app for learning Bangalore Kannada through staged, code-switched sentences. Live at `namma-kannada.pages.dev` (Cloudflare Pages, auto-deploys on push to `master`).

GitHub: `https://github.com/caprion/namma-kannada`

## Structure

```
index.html          Landing page — 4 stage cards with progress bars and lock states
learn.html          Sentence card learner (one stage at a time)
css/style.css       Indian Earth design system (all styles in one file)
js/data.js          Synchronous XHR loader → window.NAMMA_DATA
js/progress.js      localStorage wrapper — Progress.getStageProgress / setStageProgress
data/sentences.json 300 sentences across 4 stages (source of truth)
audio/{id}.wav      Pre-generated Sarvam Bulbul v3 TTS (committed as static assets)
generate_audio.py   One-time TTS generation script (Sarvam API, kavitha voice, 0.85 pace)
```

## Sentence Data Schema

```json
{
  "id": "s1_001",
  "kannada": "ಕಾಫಿ ಬೇಕು",
  "roman": "coffee beku",
  "gloss": "Want coffee",
  "new_word": "beku",
  "new_word_meaning": "want / need",
  "grammar_note": "beku ends the sentence. Always. Kannada is verb-final."
}
```
Fields `new_word`, `new_word_meaning`, `grammar_note` are optional (empty string = hidden in UI).

## Stage Progression (4 stages, 300 sentences)

| Stage | Name | Count | Focus |
|-------|------|-------|-------|
| 1 | Grammar Shapes | 30 | 9 function words: ide/illa, beku/beda, question words, postpositions (-ge/-alli/-inda) |
| 2 | Daily Survival | 70 | Commute, darshini food, office/WFH, time, navigation, market/UPI, social slang |
| 3 | Social Fluency | 100 | Family, health, emotions, discourse markers (amdre/maatra/bere), market, rituals |
| 4 | Naturalistic Bangalore | 100 | Silk Board/ORR traffic, tech-office, Bangalore identity, nostalgia, code-switch speech |

Unlock logic: each stage unlocks when the previous stage is 100% complete (`Progress.isStageUnlocked`).

## Learn Page Flow

1. Show English gloss → user taps "Show Kannada" (or Space/Enter)
2. Reveal: Kannada script + Roman + new_word tag + grammar_note
3. "Hear it" audio button appears (HEAD-checks `audio/{id}.wav` before showing)
4. Navigate with Prev/Next buttons or arrow keys
5. Stage breadcrumb `S1 › S2 › S3 › S4` at top — current stage highlighted green

## Audio Regeneration

If sentences change and audio needs regenerating:

```bash
cd C:\Learn\namma-kannada
python -m venv .venv && .venv\Scripts\activate
pip install sarvamai python-dotenv
# Add SARVAM_API_KEY to .env
python generate_audio.py --dry-run          # preview
python generate_audio.py --stage 1          # one stage only
python generate_audio.py                    # all missing
```

Rate: 1.1s/request (~54 req/min). Cost: ~Rs 24 for 300 sentences. Resume-safe (skips existing files).

## Deploy

Push to `master` → Cloudflare Pages auto-deploys. No build step — pure static.

```bash
git add -p
git commit -m "..."
git push origin master
```
