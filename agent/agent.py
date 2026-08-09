"""AI/ML interviewer voice agent, LiveKit port.

Stack:
  STT  : LiveKit Inference, deepgram/nova-3 (keyless, LiveKit Cloud creds only)
  LLM  : Claude Haiku 4.5 via the Anthropic plugin (ANTHROPIC_API_KEY)
  TTS  : Rime Coda via the Rime plugin, per-voice time_scale_factor (RIME_API_KEY)
  Turn : MultilingualModel turn detection + Silero VAD + BVC noise cancellation

Each session is one difficulty level + one voice. The browser frontend creates
the room with JSON metadata {\"difficulty\": \"...\", \"voice\": \"...\", \"name\": \"...\"}
and the agent configures itself from it.
"""
import json
import logging

import os

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession, JobContext, RoomInputOptions, WorkerOptions, cli, inference
from livekit.plugins import openai, noise_cancellation, rime, silero

from personas import SCENARIOS, build_instructions, format_greeting, voice_entry, voice_speed
from pronounce import display_text, tts_pronounce

load_dotenv()
logger = logging.getLogger("aiml-interviewer")

DEFAULT_DIFFICULTY = "mid"


def _resolve_config(ctx: JobContext):
    """Read {difficulty, voice, name} from room (or job) metadata, with safe defaults."""
    raw = (ctx.room.metadata or "").strip() or (ctx.job.metadata or "").strip()
    difficulty, voice = DEFAULT_DIFFICULTY, SCENARIOS[DEFAULT_DIFFICULTY]["recommended"]
    candidate_name = None
    if raw:
        try:
            data = json.loads(raw)
            if data.get("difficulty") in SCENARIOS:
                difficulty = data["difficulty"]
                voice = SCENARIOS[difficulty]["recommended"]
            if data.get("voice"):
                voice = data["voice"]
            if data.get("name"):
                candidate_name = data["name"]
        except (ValueError, TypeError):
            logger.warning("could not parse room metadata: %r", raw)
    entry = voice_entry(difficulty, voice)  # validates + falls back to recommended
    return difficulty, entry, candidate_name


class InterviewerAgent(Agent):
    """Buffers the full reply before TTS (one full-context request, like the
    browser demo) and hardens pronunciation via tts_pronounce."""

    async def tts_node(self, text, model_settings):
        async def hardened():
            full = ""
            async for chunk in text:
                full += chunk
            yield tts_pronounce(full)

        async for frame in Agent.default.tts_node(self, hardened(), model_settings):
            yield frame

    async def transcription_node(self, text, model_settings):
        # Show the original text (Rime, AI4) cleaned of expressive tokens and
        # stress markers; tts_node still feeds the hardened text to the TTS.
        full = ""
        async for chunk in text:
            full += chunk
        yield display_text(full)


async def entrypoint(ctx: JobContext):
    await ctx.connect()

    difficulty, voice, candidate_name = _resolve_config(ctx)
    voice_id = voice["id"]
    logger.info("interview session: difficulty=%s voice=%s (%s) candidate=%s",
                difficulty, voice_id, voice["char"], candidate_name or "anonymous")

    session = AgentSession(
        stt=inference.STT(model="deepgram/nova-3", language="multi"),
        llm=openai.LLM(
            model="llama-3.3-70b-versatile",
            base_url="https://api.groq.com/openai/v1",
            api_key=os.environ.get("GROQ_API_KEY")
        ),
        tts=rime.TTS(
            model="coda",
            speaker=voice_id,
            time_scale_factor=voice_speed(voice_id),
        ),
        vad=silero.VAD.load(),
        turn_detection="manual",  # push-to-talk: the candidate drives turn boundaries
        # We disable preemptive_generation for Groq because its free tier rate limits
        # (30 req/min) will be instantly exhausted by speculative requests.
        preemptive_generation=False,
    )

    @session.on("user_input_transcribed")
    def _on_user_transcript(ev):
        logger.info("STT heard: %r (final=%s)", getattr(ev, "transcript", None), getattr(ev, "is_final", None))

    await session.start(
        room=ctx.room,
        agent=InterviewerAgent(
            instructions=build_instructions(difficulty, voice_id, candidate_name)
        ),
        room_input_options=RoomInputOptions(noise_cancellation=noise_cancellation.BVC()),
    )

    # Push-to-talk (strict half-duplex): the agent listens only during a turn
    # the candidate starts, so mic and agent audio never overlap. The frontend's
    # mic button drives these over RPC.
    session.input.set_audio_enabled(False)

    @ctx.room.local_participant.register_rpc_method("start_turn")
    async def _start_turn(data):
        session.interrupt()        # stop any agent speech immediately
        session.clear_user_turn()  # discard any buffered input
        session.input.set_audio_enabled(True)
        return "ok"

    @ctx.room.local_participant.register_rpc_method("end_turn")
    async def _end_turn(data):
        session.input.set_audio_enabled(False)
        session.commit_user_turn()  # process the turn and generate the reply
        return "ok"

    @ctx.room.local_participant.register_rpc_method("cancel_turn")
    async def _cancel_turn(data):
        session.input.set_audio_enabled(False)
        session.clear_user_turn()   # discard the turn without replying
        return "ok"

    # Scripted first line for this voice with candidate name interpolated.
    greeting = format_greeting(difficulty, voice_id, candidate_name)
    await session.say(greeting, allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, agent_name="aiml-interviewer"))
