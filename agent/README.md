# AI4 Booth Voice Agent (LiveKit)

LiveKit port of `bryanbamf/rime-voice-agent`. Same booth experience (pick an
industry + voice, have a live spoken conversation with a Rime-voiced character)
rebuilt on LiveKit Agents for real turn-taking and barge-in.

## Stack

| Layer | Choice |
| --- | --- |
| STT | LiveKit Inference `deepgram/nova-3` (keyless) |
| LLM | Claude Haiku 4.5 (Anthropic plugin) |
| TTS | Rime Coda (Rime plugin), per-voice `time_scale_factor` |
| Turn-taking | `MultilingualModel` + Silero VAD + BVC noise cancellation |

The portable heart carries over verbatim from the browser demo:
`VOICE_RULES`, `CHARACTERS`, `INDUSTRIES`, per-voice greetings, `VOICE_SPEED`
(all in `personas.py`), and the `ttsPronounce()` transforms (`pronounce.py`,
run in front of the TTS). Browser mic/push-to-talk/barge-in was intentionally
not ported (LiveKit turn detection replaces it).

## Run locally

```bash
pip install uv
uv sync
cp .env.example .env    # fill in LiveKit Cloud + ANTHROPIC + RIME keys
uv run agent.py dev
```

Then connect a client:
- Fastest test with no frontend: the LiveKit Agents Playground
  (https://agents-playground.livekit.io), pointed at your LiveKit Cloud project.
- The booth frontend joins a room with JSON metadata
  `{"industry": "food", "voice": "vespera"}`; the agent reads it and loads the
  matching persona, voice, speed, and scripted greeting. With no metadata it
  defaults to healthcare + the recommended voice.

## Notes / still to do

- **Frontend**: the branded industry/voice picker UI still needs to be wired to
  LiveKit (join a room, set metadata from the selection). Decision pending:
  adapt Bryan's existing `index.html` vs. LiveKit's React starter.
- **Transcript**: `<laugh>`-style tokens reach Rime raw but should be stripped
  from the visible transcript (`display_text` in `pronounce.py`); wire it into a
  `transcription_node` override once the frontend is settled.
- **Booth**: use a Rime key that is stable for the whole week; deploy the agent
  (LiveKit Cloud agents or Render) for a permanent URL.
