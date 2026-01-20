import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

async def test_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"Testing key: {api_key[:10]}...")
    client = AsyncOpenAI(api_key=api_key)
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=5
        )
        print("LLM Success:", response.choices[0].message.content)
    except Exception as e:
        print("LLM Error:", e)

    try:
        # Test models list
        models = await client.models.list()
        all_models = [m.id for m in models.data]
        print("Whisper-1 available:", "whisper-1" in all_models)
        print("TTS-1 available:", "tts-1" in all_models)
        print("gpt-4o-mini-transcribe available:", "gpt-4o-mini-transcribe" in all_models)
        print("gpt-4o-mini-tts available:", "gpt-4o-mini-tts" in all_models)
        print("Available models:", all_models)
    except Exception as e:
        print("Models List Error:", e)

if __name__ == "__main__":
    asyncio.run(test_openai())
