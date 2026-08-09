# Rime Voice Demo — AI4 Booth Edition (LiveKit)

The official Rime voice demo for the AI4 conference in Las Vegas. Booth visitors pick an industry, pick a voice, and have a live spoken conversation with a Rime-voiced AI character. Rebuilt on **LiveKit Agents** for real turn-taking and barge-in.

**Live:** https://rime-ai4-booth.vercel.app  (custom domain https://ai4.rime.ai pending a DNS record)

## Architecture

Two parts:

```
Visitor browser ──► token server (/api/token) ──► LiveKit room
      │                                                 ▲
      └──────────── LiveKit JS client ─────────────────┘
                                                        │
                              LiveKit Agent (agent/) ───┘
                        Deepgram STT (Inference) ─► Claude Haiku 4.5 ─► Rime Coda TTS
```

- **`agent/`** — the LiveKit voice agent (Python). STT via LiveKit Inference (`deepgram/nova-3`, keyless), LLM = Claude Haiku 4.5, TTS = Rime **Coda** with per-voice `time_scale_factor`, plus LiveKit turn detection and BVC noise cancellation. The portable heart carries over verbatim from the browser version: `VOICE_RULES`, `CHARACTERS`, the four `INDUSTRIES` personas, per-voice greetings and `VOICE_SPEED` (`personas.py`), and the `ttsPronounce()` transforms (`pronounce.py`), run in front of the TTS.
- **root** — the booth frontend (the same brand UI) plus a Vercel serverless token function (`api/token.js`). `POST /api/token` mints a visitor join token and declares a `booth-agent` dispatch carrying the chosen `{industry, voice}` as metadata; the agent reads it and loads the matching persona, voice, speed, and greeting.

LiveKit turn detection replaces the old browser push-to-talk and barge-in; that browser-specific code is gone.

## Run locally

**1. Agent** (needs LiveKit + Anthropic + Rime keys):

```bash
cd agent
pip install uv
uv sync
cp .env.example .env      # fill in LIVEKIT_*, ANTHROPIC_API_KEY, RIME_API_KEY
uv run agent.py dev
```

**2. Frontend + token function** (needs LiveKit keys only):

```bash
npm install
cp .env.example .env       # fill in LIVEKIT_URL / LIVEKIT_API_KEY / LIVEKIT_API_SECRET
npx vercel dev             # http://localhost:3000 (emulates the Vercel build)
```

Open http://localhost:3000 in Chrome, pick an industry and voice, and talk.

## Voice casting

The picker shows official Rime voice names; in the conversation each voice plays a named person (greeting, transcript label, and LLM persona all follow the character).

| Industry | Company | Rime voice → Character | Notes |
| --- | --- | --- | --- |
| Healthcare | Lakeside Family Health | **Arcade → Frank** (recommended), Luna → Lindsey | Luna runs at 1.1x slower (`time_scale_factor`) |
| Finance | Meridian Trust Bank | **Clara** (recommended), Marlu → Kevin | Professional register (overrides casual rules) |
| Food Ordering | Blaze Burger | **Vespera → Megan** (recommended), Vayu → Jake | Vespera at 1.05x slower; highest energy persona |
| Retail | Harbor & Pine | **Wawona → Katie** (recommended), Cupola → Jordan | |

## Pronunciation design (carried over)

- Replies synthesize with full context; per-sentence fragments mispronounce. The LLM prompt embeds Rime's dialogue text style guide (`VOICE_RULES`).
- `ttsPronounce()` (`agent/pronounce.py`) runs in front of the TTS: **"Rime" → "Rhyme"**, **"AI4" → "A. I. Four"**, stretched-spelling and stacked-punctuation normalization, stray-asterisk strip, em-dash backstop.
- Expressive tokens like `<laugh>` reach Rime raw but are stripped from the visible transcript (`display_text`).

## Deploy

- **Agent** → LiveKit Cloud Agents: from `agent/`, `lk agent create --region us-east --secrets-file .env` (first time), then `lk agent deploy` to update.
- **Frontend** → Vercel (Rime-web team): `vercel --prod`. Turn Deployment Protection off for public booth access.

Use a Rime API key that is stable for the whole event.

## Booth tips

- Allow the mic once per origin in Chrome before the event.
- Voice or industry changes start a fresh call by design; every visitor gets a clean scripted greeting.
- API keys live only in `.env` (gitignored). Share via a password manager, never in chat or commits.
