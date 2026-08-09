"""Pronunciation hardening, ported verbatim from index.html ttsPronounce()
plus the server.js em-dash backstop. This MUST run in front of whatever feeds
the TTS (README: 'Keep the ttsPronounce() transforms in front of the TTS').

- "Rime" -> "Rhyme" so the brand name never mispronounces
- "AI4" -> "A. I. Four"
- normalizes over-exaggerated text (stretched spellings, stacked punctuation)
  that is the main source of Rime mispronunciations
- em dashes are banned everywhere; scrubbed to a comma as a backstop
"""
import re

_HA_RUN = re.compile(r"\b(?:ha[,\s]+)+ha\b", re.IGNORECASE)
_HA = re.compile(r"\bha\b", re.IGNORECASE)
_AI4 = re.compile(r"\bAI4\b", re.IGNORECASE)
_RIME = re.compile(r"\bRime\b")  # capitalized brand only, matching the JS
_STRAY_ASTERISK = re.compile(r"(?<!\*)\*(?!\*)")  # single * ; ** stress stays
_REPEAT = re.compile(r"([A-Za-z])\1{2,}")
_STACKED_PUNCT = re.compile(r"([!?])[!?]+")
_EM_DASH = re.compile(r"\s*—\s*")
_TAG = re.compile(r"<[^<>]+>")
_MULTISPACE = re.compile(r"\s{2,}")


def _collapse_repeat(m):
    run, ch = m.group(0), m.group(1)
    # sooooo -> so, yesss -> yes; hums/laughs keep a short run (mmm, hhh)
    return run[:3] if ch.lower() in ("m", "h") else ch


def tts_pronounce(text: str) -> str:
    """Transform LLM/greeting text into what Rime's engine should actually say."""
    text = _EM_DASH.sub(", ", text)          # backstop: no em dashes reach TTS
    text = _AI4.sub("AI four", text)
    text = _RIME.sub("Rhyme", text)          # brand name must never come out wrong
    text = _HA_RUN.sub("hahaha", text)       # "ha ha", "ha, ha ha" runs
    text = _HA.sub("haha", text)
    text = _STRAY_ASTERISK.sub("", text)     # stray single asterisks; ** stress stays
    text = _REPEAT.sub(_collapse_repeat, text)
    text = _STACKED_PUNCT.sub(r"\1", text)   # !!, ???, ?! -> a single mark
    return text


def display_text(text: str) -> str:
    """What the transcript shows: expressive tokens like <laugh> and the
    double-asterisk stress markers are for the engine, not the reader."""
    text = _EM_DASH.sub(", ", text)
    text = _TAG.sub("", text)
    text = text.replace("*", "")
    text = _MULTISPACE.sub(" ", text)
    return text.strip()
