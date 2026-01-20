# AI Voice Agent - Setup & Documentation

## Features
- **Voice Conversation**: Real-time STT (Deepgram), LLM (GPT-4o), and TTS (Cartesia) via LiveKit.
- **Visual Avatar**: Synchronized avatar display via Tavus/Beyond Presence.
- **Database Integration**: Appointment management with Supabase.
- **Dynamic UI**: Real-time tool call visualization and end-of-call summary.

## Prerequisites
You will need API keys for:
- [LiveKit Cloud](https://cloud.livekit.io)
- [OpenAI](https://platform.openai.com)
- [Deepgram](https://console.deepgram.com)
- [Cartesia](https://cartesia.ai)
- [Supabase](https://supabase.com)
- [Tavus](https://tavus.io)

## Backend Setup
1. `cd backend`
2. Create `.env` from `.env.example` and fill in your keys.
3. Install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. Run the agent:
   ```bash
   python agent.py dev
   ```

## Frontend Setup
1. `cd frontend`
2. Create `.env` from `.env.example`.
3. Install dependencies:
   ```bash
   npm install
   ```
4. Run the app:
   ```bash
   npm run dev
   ```

## Database Schema
Run the SQL in `backend/schema.sql` in your Supabase SQL Editor.

## Limitations
- **Token Generation**: For security, token generation should happen on a backend server. This demo expects a token endpoint or manual configuration.
- **Avatar Sync**: Advanced lip-sync requires passing the audio stream to Tavus, which is configured in the `Avatar` component via the replica ID.
