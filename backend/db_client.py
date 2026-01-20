import os
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class DBClient:
    def __init__(self):
        self._lock = asyncio.Lock()
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        
        # Auto-correct URL if it's a DB connection string
        if url and url.startswith("postgresql://"):
            project_id = url.split("@db.")[1].split(".supabase.co")[0]
            url = f"https://{project_id}.supabase.co"
            print(f"INFO: Detected DB connection string. Auto-corrected Supabase API URL to: {url}")

        if not url or not key or "postgresql://" in url:
            print("\n" + "!"*50)
            print("⚠️  MISSING SUPABASE SERVICE ROLE KEY!")
            print("DATABASE ENTRIES WILL NOT SHOW UP IN THE DASHBOARD.")
            print("To fix this, paste your key into backend/.env")
            print("!"*50 + "\n")
            print("💡 FALLBACK: Using local mock_db.json for appointments.")
            self.use_mock = True
            self.supabase = None
            self.mock_file = "mock_db.json"
        else:
            try:
                self.supabase: Client = create_client(url, key)
                self.use_mock = False
                print(f"✅ SUCCESS: Connected to Supabase at {url}")
            except Exception as e:
                print(f"❌ ERROR: Failed to connect to Supabase: {e}")
                print("💡 FALLBACK: Using local mock_db.json.")
                self.use_mock = True
                self.mock_file = "mock_db.json"

    def _load_mock(self):
        import json
        if os.path.exists(self.mock_file):
            try:
                with open(self.mock_file, "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_mock(self, data):
        import json
        with open(self.mock_file, "w") as f:
            json.dump(data, f)

    async def get_slots(self):
        # Using local time strings (no 'Z') to match user local time expectations
        return [
            "2026-01-20T10:00:00",
            "2026-01-20T11:00:00",
            "2026-01-20T14:00:00",
            "2026-01-21T09:00:00",
            "2026-01-21T15:00:00"
        ]

    async def book_appointment(self, contact_number: str, slot: str, name: str):
        async with self._lock:
            if self.use_mock:
                db = self._load_mock()
                # Check for double booking in mock mode
                if any(a["slot"] == slot and a["status"] == "confirmed" for a in db):
                    return {"success": False, "message": f"Slot {slot} is already booked"}
                
                db.append({
                    "id": str(len(db) + 1),
                    "contact_number": contact_number,
                    "slot": slot,
                    "name": name,
                    "status": "confirmed"
                })
                self._save_mock(db)
                return {"success": True, "data": db[-1]}
                
            try:
                # Check for double booking
                res = self.supabase.table("appointments").select("*").eq("slot", slot).eq("status", "confirmed").execute()
                if res.data:
                    print(f"DEBUG: Slot {slot} is already taken: {res.data}")
                    return {"success": False, "message": f"Slot {slot} is already booked"}

                data = {
                    "contact_number": contact_number,
                    "slot": slot,
                    "name": name,
                    "status": "confirmed"
                }
                response = self.supabase.table("appointments").insert(data).execute()
                print(f"DEBUG: Booked appointment in Supabase: {response.data}")
                return {"success": True, "data": response.data}
            except Exception as e:
                print(f"ERROR: Supabase book fail: {e}")
                return {"success": False, "message": str(e)}

    async def retrieve_appointments(self, contact_number: str):
        if self.use_mock:
            db = self._load_mock()
            apps = [a for a in db if a["contact_number"] == contact_number]
            return {"success": True, "data": apps}
            
        try:
            response = self.supabase.table("appointments").select("*").eq("contact_number", contact_number).execute()
            print(f"DEBUG: Retrieved {len(response.data)} appointments from Supabase for {contact_number}")
            return {"success": True, "data": response.data}
        except Exception as e:
            print(f"ERROR: Supabase retrieve fail: {e}")
            return {"success": False, "message": str(e)}

    async def cancel_appointment(self, appointment_id: str):
        if self.use_mock:
            db = self._load_mock()
            for a in db:
                if a["id"] == appointment_id:
                    old_slot = a["slot"]
                    a["status"] = "cancelled"
                    self._save_mock(db)
                    print(f"DEBUG: Slot {old_slot} is now FREE (cancelled)")
                    return {"success": True, "data": a}
            return {"success": False, "message": "Appointment not found"}
            
        try:
            print(f"DEBUG: Attempting to cancel app ID {appointment_id} in Supabase")
            response = self.supabase.table("appointments").update({"status": "cancelled"}).eq("id", appointment_id).execute()
            if not response.data:
                print(f"ERROR: No rows updated for ID {appointment_id}")
                return {"success": False, "message": "Appointment not found in database"}
            print(f"DEBUG: Cancelled in Supabase: {response.data}")
            return {"success": True, "data": response.data}
        except Exception as e:
            print(f"ERROR: Supabase cancel fail: {e}")
            return {"success": False, "message": str(e)}

    async def modify_appointment(self, appointment_id: str, new_slot: str):
        if self.use_mock:
            db = self._load_mock()
            for a in db:
                if a["id"] == appointment_id:
                    # Check for double booking on new slot
                    if any(other["slot"] == new_slot and other["status"] == "confirmed" for other in db):
                        return {"success": False, "message": f"New slot {new_slot} is already booked"}
                    
                    a["slot"] = new_slot
                    self._save_mock(db)
                    return {"success": True, "data": a}
            return {"success": False, "message": "Appointment not found"}
            
        try:
            # Check for double booking on new slot
            res = self.supabase.table("appointments").select("*").eq("slot", new_slot).eq("status", "confirmed").execute()
            if res.data:
                return {"success": False, "message": "New slot already booked"}

            response = self.supabase.table("appointments").update({"slot": new_slot}).eq("id", appointment_id).execute()
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e)}
