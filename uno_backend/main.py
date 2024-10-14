from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.routes.game_routes import router as game_router
from core.routes.session_routes import router as session_router
from core.garbage_collector import clean_sessions
import os
from dotenv import load_dotenv
import asyncio 

load_dotenv()

origin = os.getenv('ORIGIN')
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(game_router)
app.include_router(session_router)

@app.on_event('startup')
async def app_startup():
    asyncio.create_task(clean_sessions())


@app.get('/')
async def root(): 
    return {"message": "Welcome to the Uno Game API!"}

