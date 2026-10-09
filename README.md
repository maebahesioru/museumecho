# MuseumEcho — the audio guide that knows your museum

> EurekaDev 2026 — Coding Track (Computer Science + AI · Problem in the Community)

**Built from the museum's own guide. Cited, spoken, honest.**

MuseumEcho turns a museum's visitor guide into an interactive audio guide. Visitors ask
questions in plain language — "I have 30 minutes, what should I see?" — and get answers
**cited to the exact line of the museum's own guide**, read aloud, with an honest
"I couldn't find this in the guide" for anything the guide doesn't cover.

## The problem

Small museums run on paper maps and static signs. Visitors — especially families,
tourists, and first-time museum-goers — walk out without learning the stories that make
the exhibits matter. Commercial audio-guide hardware costs thousands; generic AI chatbots
invent opening hours, café details, and exhibit facts, which museums can never risk.

## What MuseumEcho does

| Feature | Detail |
|---|---|
| **Guide ingestion** | Load the museum's own guide (PDF / TXT / MD) — every exhibit keeps its exact source |
| **Ask in plain language** | 🦖 "Tell me about the T. rex" · 🧒 "What's good for kids?" · ♿ "Is the museum accessible?" |
| **🔊 Spoken answers** | Every answer is synthesized to audio (neural TTS, cached) — it's an audio guide first |
| **Cited, never invented** | Each fact cites the guide `[unit_id]`; anything not covered gets an explicit refusal |
| **Suggested routes** | The museum's own 30-minute and 2-hour routes, surfaced on request |
| **Browse mode** | Every gallery and exhibit, with a one-tap "Ask about this" button |

## Why it's safe for museums

- **No invented hours, prices, or exhibits.** Answers come only from the uploaded guide;
  off-guide questions are declined. A wrong café hour is worse than no answer for a museum.
- **The museum stays in control.** The content is a file — the museum writes its guide,
  MuseumEcho speaks it. Updates are just a new file.
- **Zero hardware.** Runs on any phone browser; no audio-guide devices to buy or charge.

## How it works

```
 upload guide ──► ingest (pdf/txt/md) ──► source-linked passages
                                            │
                          browse ──► galleries & exhibits list
                                            │
 question ──► TF-IDF retrieval ──► grounded answer + citations ──► 🔊 TTS
```

- Python + FastAPI backend; single-page web UI (no build step).
- Retrieval: scikit-learn TF-IDF (local, any language) — museums can serve multiple languages.
- Grounding: retrieval-scoped prompts, mandatory citations, explicit refusal token.
- Audio: edge-tts neural voices with content-hash caching (repeat = instant, low bandwidth).
- LLM: any OpenAI-compatible endpoint.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp config.example.env .env      # LLM_BASE_URL / LLM_API_KEY / LLM_MODEL
uvicorn server:app --port 7866  # open http://127.0.0.1:7866
```

Load `data/sample_course/museum_guide.md` (a fictional "Cedar City Museum" guide) to try it.

## Impact

- **Cultural access**: small museums get a modern audio guide for the cost of writing a file.
- **Honesty**: the guide refuses to invent — safe for staff, trustworthy for visitors.
- **Accessibility**: audio-first design serves low-vision and low-literacy visitors; the
  guide's accessibility info is one question away.
- **Multilingual future**: swap in translated guides; the engine is language-agnostic.

## Honest limitations

- The demo museum ("Cedar City") is fictional; real deployments use the museum's guide.
- Scanned guides need OCR first.
- Not a substitute for staff — for anything urgent, ask at the ticket desk.
