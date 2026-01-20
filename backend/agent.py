import asyncio
import logging
import os
from dotenv import load_dotenv
from livekit.agents import (
    AutoSubscribe, 
    JobContext, 
    WorkerOptions, 
    cli, 
    llm,
)
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import openai, deepgram, cartesia, silero
from db_client import DBClient

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("voice-agent")

class AssistantTools:
    def __init__(self, db: DBClient, ctx: JobContext, session: AgentSession):
        self.db = db
        self.ctx = ctx
        self.session = session
        self.contact_number = None
        self.session_appointment_ids = [] # To track what happened THIS session

    async def _save_summary(self):
        import json
        import datetime
        summary_data = {
            "text": "The conversation has ended. Thank you for using our AI booking assistant.",
            "appointments": [],
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        if self.contact_number:
            res = await self.db.retrieve_appointments(self.contact_number)
            if res["success"]:
                # Filter for confirmed appointments AND only those touched this session
                summary_data["appointments"] = [
                    a for a in res["data"] 
                    if a.get("status") == "confirmed" and a.get("id") in self.session_appointment_ids
                ]
        
        with open("latest_summary.json", "w") as f:
            json.dump(summary_data, f)
        logger.info(f"Summary updated with {len(summary_data['appointments'])} appointments")

    @llm.function_tool(description="Identify the user by their phone number.")
    async def identify_user(self, phone_number: str):
        logger.info(f"Identifying user: {phone_number}")
        self.contact_number = phone_number
        await self._save_summary()
        return f"User identified as {phone_number}. Checking for existing appointments..."

    @llm.function_tool(description="Fetch available slots for appointments.")
    async def fetch_slots(self):
        logger.info("Fetching slots")
        slots = await self.db.get_slots()
        return f"Available slots: {', '.join(slots)}"

    @llm.function_tool(description="Book a new appointment.")
    async def book_appointment(self, slot: str, name: str):
        if not self.contact_number:
            return "Please provide your phone number first using 'identify_user'."
        logger.info(f"Booking appointment for {name} at {slot}")
        res = await self.db.book_appointment(self.contact_number, slot, name)
        if res["success"]:
            # Track this ID for the session summary
            new_id = res["data"]["id"] if isinstance(res["data"], dict) else res["data"][0]["id"]
            if new_id not in self.session_appointment_ids:
                self.session_appointment_ids.append(new_id)
                
            await self._save_summary()
            return f"Appointment confirmed for {name} on {slot}."
        return f"Failed to book: {res['message']}"

    @llm.function_tool(description="Retrieve existing appointments for the user.")
    async def retrieve_appointments(self):
        if not self.contact_number:
            return "Please identify yourself first."
        res = await self.db.retrieve_appointments(self.contact_number)
        if res["success"]:
            if not res["data"]:
                return "No appointments found."
            apps = [f"ID: {a['id']} - Slot: {a['slot']} ({a['status']})" for a in res["data"]]
            return f"Your appointments:\n" + "\n".join(apps)
        return "Error retrieving appointments."

    @llm.function_tool(description="Cancel an existing appointment.")
    async def cancel_appointment(self, appointment_id: str):
        res = await self.db.cancel_appointment(appointment_id)
        if res["success"]:
            # If we cancel an appointment that was in our session list, remove it
            if appointment_id in self.session_appointment_ids:
                self.session_appointment_ids.remove(appointment_id)
            
            await self._save_summary()
            return f"Appointment {appointment_id} cancelled."
        return f"Error: {res['message']}"

    @llm.function_tool(description="Modify an appointment to a new slot.")
    async def modify_appointment(self, appointment_id: str, new_slot: str):
        res = await self.db.modify_appointment(appointment_id, new_slot)
        if res["success"]:
            # Track this ID (it might be an existing app we modified)
            if appointment_id not in self.session_appointment_ids:
                self.session_appointment_ids.append(appointment_id)
                
            await self._save_summary()
            return f"Appointment rescheduled to {new_slot}."
        return f"Error: {res['message']}"

    @llm.function_tool(description="End the conversation gracefully.")
    async def end_conversation(self):
        logger.info("Ending conversation requested by tool")
        await self._save_summary()
        # Say goodbye explicitly before shutting down
        await self.session.say("I'm ending the call now. Thank you for booking with us. Goodbye!", allow_interruptions=False)
        # Schedule the shutdown after a longer delay (5s) to ensure the message is heard
        asyncio.get_event_loop().call_later(5, self.ctx.shutdown)
        return "Ending the call. Goodbye!"

async def entrypoint(ctx: JobContext):
    logger.info(f"--- [ALEX v2.0] STARTING SESSION IN {ctx.room.name} ---")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    logger.info(f"Connected to room: {ctx.room.name}")

    db = DBClient()
    session = AgentSession()
    assistant_tools = AssistantTools(db, ctx, session)
    
    agent = Agent(
        instructions=(
            "You are 'Alex', an incredibly friendly and efficient AI booking assistant. "
            "Your personality: Warm, professional, and very human-like. "
            "Conversational style:\n"
            "- Use short, punchy sentences. Avoid long lists.\n"
            "- Use natural fillers like 'Got it', 'Sure thing', or 'Let me see...' when appropriate.\n"
            "- If booking, say something like 'Great choice! One second while I lock that in for you.'\n"
            "Steps:\n"
            "1. ALWAYS identify the user first with 'identify_user' if unknown.\n"
            "2. Offer to 'fetch_slots' for availability.\n"
            "3. IMPORTANT: You MUST repeat the date, time, and name to the user and ask 'Shall I go ahead and book that for you?' before calling 'book_appointment'.\n"
            "4. Use 'book_appointment', 'retrieve_appointments', 'cancel_appointment', or 'modify_appointment' as needed.\n"
            "5. IMPORTANT: Always retrieve appointments before canceling/modifying.\n"
            "6. Call 'end_conversation' when finished.\n"
            "Keep response times FAST. Stay in character as a helpful local assistant."
        ),
        stt=deepgram.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(voice="f786b574-daa5-4673-aa0c-cbe3e8534c02"), # Premium Sonic voice
        vad=silero.VAD.load(
            min_silence_duration=0.1,
            activation_threshold=0.4, # Slightly higher to avoid accidental triggers
        ),
        tools=llm.find_function_tools(assistant_tools)
    )
    
    @session.on("speech_started")
    def on_speech_started(speech):
        logger.info("AI started speaking")

    @session.on("speech_finished")
    def on_speech_finished(speech):
        logger.info("AI finished speaking")

    logger.info("Starting agent session")
    await session.start(agent, room=ctx.room)
    
    # Wait for the agent to be ready and then greet
    await asyncio.sleep(1)
    logger.info("Sending initial greeting")
    await session.say("Hello! I'm your booking assistant. How can I help you today?", allow_interruptions=True)

    # Keep alive until shutdown
    try:
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"Session loop error: {e}")
    finally:
        # Final save logic
        summary_data = {
            "text": "The conversation has ended.",
            "appointments": [],
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        if assistant_tools.contact_number:
            res = await db.retrieve_appointments(assistant_tools.contact_number)
            if res["success"]:
                summary_data["appointments"] = res["data"]
        
        with open("latest_summary.json", "w") as f:
            json.dump(summary_data, f)
        logger.info("Final summary saved")

if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
    ))
