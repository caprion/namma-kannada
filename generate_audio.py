"""Generate TTS audio for all 300 sentences using Sarvam Bulbul v3.

Usage:
    python generate_audio.py              # generate all missing
    python generate_audio.py --dry-run    # show what would be generated

Output: audio/{sentence_id}.wav
Cost:   ~Rs 63 for 300 sentences at Bulbul v3 pricing (well within free credits)

Resume safe: skips sentences that already have audio files.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")
from sarvamai import SarvamAI

# ── Config ────────────────────────────────────────────────────────────

# Load API key from local .env or from autoresearcher/.env
load_dotenv(Path(__file__).parent / ".env")
load_dotenv(Path(__file__).parent.parent / "autoresearcher" / ".env")

API_KEY    = os.getenv("SARVAM_API_KEY", "")
TTS_MODEL  = "bulbul:v3"
SPEAKER    = "kavitha"      # Natural female Kannada voice
PACE       = 0.85           # Slightly slow — learner-friendly
LANGUAGE   = "kn-IN"

SENTENCES_FILE = Path("data/sentences.json")
AUDIO_DIR      = Path("audio")
RATE_LIMIT_S   = 1.1        # 1.1s between requests = ~54 req/min, under 60 limit

# ── Main ──────────────────────────────────────────────────────────────

def load_sentences() -> list[dict]:
    data = json.loads(SENTENCES_FILE.read_text(encoding="utf-8"))
    sentences = []
    for stage in data["stages"]:
        for s in stage["sentences"]:
            s["_stage"] = stage["id"]
            sentences.append(s)
    return sentences


def generate_audio(client: SarvamAI, text: str, out_path: Path) -> bool:
    """Call Sarvam TTS and save WAV to out_path. Returns True on success."""
    try:
        response = client.text_to_speech.convert(
            text=text,
            target_language_code=LANGUAGE,
            model=TTS_MODEL,
            speaker=SPEAKER,
            pace=PACE,
        )
        if response.audios and len(response.audios) > 0:
            audio_bytes = base64.b64decode(response.audios[0])
            out_path.write_bytes(audio_bytes)
            return True
        print(f"  WARNING: empty audio response for: {text[:50]}")
        return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Show what would run, no API calls")
    parser.add_argument("--stage", type=int, help="Only generate for this stage (1-4)")
    args = parser.parse_args()

    if not API_KEY and not args.dry_run:
        print("ERROR: SARVAM_API_KEY not set. Add it to .env")
        sys.exit(1)

    AUDIO_DIR.mkdir(exist_ok=True)
    sentences = load_sentences()

    if args.stage:
        sentences = [s for s in sentences if s["_stage"] == args.stage]

    # Find what needs generating
    pending = []
    already_done = 0
    for s in sentences:
        out = AUDIO_DIR / f"{s['id']}.wav"
        if out.exists():
            already_done += 1
        else:
            pending.append(s)

    print(f"Total sentences:   {len(sentences)}")
    print(f"Already generated: {already_done}")
    print(f"To generate:       {len(pending)}")

    if not pending:
        print("All audio files already exist.")
        return

    # Estimate cost
    total_chars = sum(len(s["kannada"]) for s in pending)
    cost_rs = (total_chars / 10000) * 30
    print(f"Estimated chars:   {total_chars}")
    print(f"Estimated cost:    Rs {cost_rs:.2f} (Bulbul v3)")
    print()

    if args.dry_run:
        print("DRY RUN — first 5 sentences that would be generated:")
        for s in pending[:5]:
            print(f"  [{s['id']}] {s['kannada'][:60]}")
        return

    client = SarvamAI(api_subscription_key=API_KEY)

    ok, failed = 0, 0
    for i, s in enumerate(pending, 1):
        out = AUDIO_DIR / f"{s['id']}.wav"
        text = s["kannada"]
        stage = s["_stage"]

        print(f"[{i}/{len(pending)}] Stage {stage} | {s['id']} | {text[:45]}...", end=" ", flush=True)

        success = generate_audio(client, text, out)
        if success:
            size_kb = out.stat().st_size // 1024
            print(f"OK ({size_kb}KB)")
            ok += 1
        else:
            print("FAILED")
            failed += 1

        # Rate limit — stay under 60 req/min
        if i < len(pending):
            time.sleep(RATE_LIMIT_S)

    print()
    print(f"Done. Generated: {ok}  Failed: {failed}")
    if failed:
        print(f"Re-run to retry failed sentences.")


if __name__ == "__main__":
    main()
