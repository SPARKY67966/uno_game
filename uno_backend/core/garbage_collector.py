import asyncio
from core.config import active_sessions, session_expiry_time, garbage_clean_every
from datetime import datetime, timedelta

SESSION_EXPIRATION_TIME = timedelta(hours=session_expiry_time)

async def clean_sessions():
    while True:
        time_now = datetime.now()
        expired_sessions = [session for session in active_sessions if time_now - active_sessions[session]['created_at'] > SESSION_EXPIRATION_TIME and not active_sessions[session]['in_game']]
        for session_id in expired_sessions:
            del active_sessions[session_id]
        await asyncio.sleep(garbage_clean_every*60*60)

# TODO : game cleaner