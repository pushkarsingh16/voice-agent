import os, asyncio
from dotenv import load_dotenv
from livekit.plugins import openai
from livekit.agents import llm

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")

async def main():
    try:
        model = openai.LLM(
            model="llama-3.1-70b-versatile",
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key
        )
        ctx = llm.ChatContext().append(text="Hello", role="user")
        stream = await model.chat(chat_ctx=ctx)
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="")
        print("\nSUCCESS!")
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(main())
