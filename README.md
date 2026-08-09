# AI/ML Interviewer 🎙️

An interactive, voice-powered AI technical interviewer specializing in Machine Learning, Deep Learning, and MLOps. This agent conducts realistic mock interviews, rotating through technical topics and providing a final rated summary of your performance.

## 🚀 Tech Stack

* **WebRTC & Real-time Audio:** [LiveKit](https://livekit.io/)
* **LLM (The Brain):** [Groq](https://groq.com/) running **Llama 3.3 70B** (`llama-3.3-70b-versatile`) for ultra-low latency conversational responses.
* **Text-to-Speech (The Voice):** [Rime](https://rime.ai/) for high-quality, ultra-realistic voice synthesis.
* **Speech-to-Text (The Ears):** Deepgram Nova-3 (via LiveKit Inference).
* **Frontend:** HTML/CSS/JS with a glassmorphic dark UI, running on Vercel.
* **Backend:** Python (`livekit-agents` SDK) running locally.

## 🛠️ Setup Instructions

### 1. API Keys
You will need API keys for three services:
1. **LiveKit Cloud**: Create a free project at [cloud.livekit.io](https://cloud.livekit.io).
2. **Groq**: Create a free API key at [console.groq.com](https://console.groq.com).
3. **Rime**: Create a free tier API key at [rime.ai](https://rime.ai).

### 2. Environment Variables
Create a `.env` file in the root directory **AND** in the `agent` directory.

**Root `.env`**:
```env
LIVEKIT_URL=wss://<your-project>.livekit.cloud
LIVEKIT_API_KEY=<your-api-key>
LIVEKIT_API_SECRET=<your-api-secret>
```

**`agent/.env`**:
```env
LIVEKIT_URL=wss://<your-project>.livekit.cloud
LIVEKIT_API_KEY=<your-api-key>
LIVEKIT_API_SECRET=<your-api-secret>
GROQ_API_KEY=<your-groq-api-key>
RIME_API_KEY=<your-rime-api-key>
```

### 3. Run the Application

You will need **two separate terminals** running side-by-side.

**Terminal 1 (Frontend):**
```bash
# In the root folder
npm install
npx vercel dev
```

**Terminal 2 (Python Backend):**
```bash
# In the agent folder
cd agent
uv sync
uv run python agent.py dev
```

### 4. Start the Interview
1. Open `http://localhost:3000` in your browser.
2. The UI defaults to **Mid-Level** difficulty.
3. Click **Start Interview**, allow microphone access, and you can begin! 

## 🎤 Interview Difficulties

The agent supports three difficulty tiers with different topic focuses:
- **Junior:** Bias-variance tradeoff, gradient descent, basic architectures.
- **Mid-Level:** Transformers, regularization techniques, experiment tracking.
- **Senior:** System design, scaling ML pipelines, research discussions.

*(Built by modifying the original Rime Voice Agent booth demo.)*
