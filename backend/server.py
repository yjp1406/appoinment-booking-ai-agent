import os
from aiohttp import web
from livekit import api
from dotenv import load_dotenv

load_dotenv()

import aiohttp_cors

async def get_token(request):
    # Clear stale summary when a new session starts
    try:
        if os.path.exists("latest_summary.json"):
            os.remove("latest_summary.json")
    except Exception:
        pass

    # Use a fresh room name to avoid stale session issues
    room_name = 'voice-booking-session-' + os.urandom(4).hex()
    participant_name = 'user-' + os.urandom(2).hex()
    
    api_key = os.environ.get('LIVEKIT_API_KEY')
    api_secret = os.environ.get('LIVEKIT_API_SECRET')
    
    if not api_key or not api_secret:
        return web.json_response({'error': 'LIVEKIT_API_KEY/SECRET not set'}, status=500)
    
    grants = api.VideoGrants(
        room_join=True,
        room=room_name,
        agent=True
    )
    
    token = api.AccessToken(api_key, api_secret) \
        .with_identity(participant_name) \
        .with_name(participant_name) \
        .with_grants(grants)
    
    jwt = token.to_jwt()
    print(f"--- [SERVER v2.0] TOKEN CREATED: room={room_name} ---")
    return web.json_response({'token': jwt})

async def get_summary(request):
    import json
    if os.path.exists("latest_summary.json"):
        with open("latest_summary.json", "r") as f:
            data = json.load(f)
            return web.json_response(data)
    return web.json_response({'error': 'No summary found'}, status=404)

async def health_check(request):
    return web.Response(text="OK")

app = web.Application()
app.add_routes([
    web.get('/', health_check),
    web.get('/api/token', get_token),
    web.get('/api/summary', get_summary)
])

# Configure CORS
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
})

for route in list(app.router.routes()):
    cors.add(route)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting token server on port {port}...")
    for route in app.router.routes():
        print(f"Registered route: {route}")
    web.run_app(app, host='0.0.0.0', port=port)

