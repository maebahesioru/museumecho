# Devpost submission text — MuseumEcho (EurekaDev 2026)

## The Problem

Small museums run on paper maps and static signs. Visitors — especially families,
tourists, and first-time museum-goers — walk out without learning the stories that make
the exhibits matter. Commercial audio-guide hardware costs thousands of dollars per
museum; generic AI chatbots invent opening hours, café details, and exhibit facts, which
museums can never risk with their reputation.

## What makes it innovative

**MuseumEcho turns the museum's own visitor guide into an interactive audio guide — cited,
spoken, and honest.**

- Load the museum's guide (PDF / TXT / MD). Every exhibit keeps its exact source line.
- Visitors ask in plain language: "I have 30 minutes, what should I see?" — and get the
  museum's own suggested route, read aloud, with citations.
- Every answer cites the guide; anything the guide doesn't cover gets an explicit
  "I couldn't find this in the museum guide" — **the system refuses to invent hours,
  prices, or exhibits.**
- Audio-first: every answer is synthesized with neural TTS (cached), so it works as a
  real audio guide for low-vision and low-literacy visitors too.
- The museum stays in control: content is a file, updates are a new file, and there is
  zero hardware to buy or charge.

**Why it matters**: cultural access for small museums at the cost of writing a document —
with the honesty guarantees museums actually need.

## Technologies used (Coding Track)

- **Python + FastAPI** backend; single-page web UI (no build step).
- **Retrieval**: scikit-learn TF-IDF (runs locally, works for any language — museums can
  serve translated guides on the same engine) with optional LLM re-ranking.
- **Grounding contract**: retrieval-scoped prompts + mandatory citations + explicit
  refusal token (`NOT_COVERED`); off-guide questions are declined by design.
- **Audio**: edge-tts neural voices with content-hash caching (repeat synthesis = instant,
  low bandwidth — important for museums with weak Wi-Fi).
- **LLM**: any OpenAI-compatible endpoint (the demo runs on a DeepSeek-class model).
- **Data**: a fictional "Cedar City Museum" guide ships with the repo for demonstration.

## How it works

1. Museum loads its guide → the app parses it into source-linked passages (gallery,
   exhibit, facilities).
2. A visitor asks a question → the retriever finds the most relevant passages.
3. The model answers **only from those passages**, citing each fact; if nothing matches,
   it declines explicitly.
4. The answer is spoken via TTS and shown with citations and a "Browse exhibits" mode.

## What's next

- Multilingual guides (same engine, translated content).
- QR-code entry at each gallery, deep-linked to that exhibit's questions.
- Optional offline mode for museums with no connectivity.

## Built with

python, fastapi, scikit-learn, edge-tts, llm, rag, accessibility, museum
