// Vercel serverless function: mint a candidate join token and declare the
// aiml-interviewer dispatch with the chosen {difficulty, voice, name} as metadata.
import { AccessToken, RoomConfiguration, RoomAgentDispatch } from "livekit-server-sdk";

const DIFFICULTIES = new Set(["junior", "mid", "senior"]);
const rand = () => Math.random().toString(36).slice(2, 8);

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).json({ error: "POST only" });

  const { LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET } = process.env;
  if (!LIVEKIT_URL || !LIVEKIT_API_KEY || !LIVEKIT_API_SECRET) {
    return res.status(500).json({ error: "LiveKit credentials are not set." });
  }

  const body = typeof req.body === "string" ? JSON.parse(req.body || "{}") : req.body || {};
  const difficulty = DIFFICULTIES.has(body.difficulty) ? body.difficulty : "mid";
  const voice = typeof body.voice === "string" ? body.voice : undefined;
  const name = typeof body.name === "string" ? body.name.slice(0, 40) : undefined;

  const room = `interview-${difficulty}-${rand()}`;
  const identity = `candidate-${rand()}`;
  const metadata = JSON.stringify({ difficulty, voice, name });

  const at = new AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET, { identity, name: name || "Candidate" });
  at.addGrant({ roomJoin: true, room, canPublish: true, canSubscribe: true });
  at.roomConfig = new RoomConfiguration({
    agents: [new RoomAgentDispatch({ agentName: "aiml-interviewer", metadata })],
  });

  try {
    const token = await at.toJwt();
    return res.status(200).json({ serverUrl: LIVEKIT_URL, token, room });
  } catch (err) {
    console.error("token error:", err);
    return res.status(500).json({ error: "Failed to mint token." });
  }
}
