from fastapi import APIRouter
import asyncio
from fastapi import HTTPException, WebSocket, WebSocketDisconnect
import traceback
from core.models.game_manager import GameManager
from core.models.session_manager import SessionManager
from core.game.handler import game_handler_main
from core.config import *
import random 
from core.game.utils import generate_game_key

router = APIRouter()

@router.websocket("/join_game")
async def join_socket(websocket: WebSocket):
    try:
        await websocket.accept()  
        query_params = websocket.query_params
        session_id = query_params.get('session_id',None)
        
        session_mngr = SessionManager(session_id)
        if not session_mngr.is_legit(): 
            await websocket.close(1000,'Invalid Session')
            return

        game_id = GameManager.get_game_id(session_id)

        if not game_id:
            await websocket.close(1000,"You can't join this game")
            return
        
        game = GameManager(game_id)
        
        if session_id not in game.all_sessions():
            await websocket.close(1000,'You dont belong to this game')
            return

        if game.started():
            await websocket.close(1000,'Game Already started')
            return
        
        session_mngr.join_game()
        
        game.update_session(session_id,
            **{
                'socket':websocket,
            })

        await websocket.send_json(
            game.get_profiles(session_id)
            )

        game_handler = asyncio.create_task(game_handler_main(game, websocket, session_id))

        await game.send_all_sockets(
            {
                'action':'joined',
                'name':session_mngr.get_name(),
                'pfp':session_mngr.get_pfp()   
            }, 
            [websocket]
        )

        await game_handler

    except WebSocketDisconnect:
        session_id = websocket.query_params.get('session_id')
        await game.remove_session(session_id)

    except Exception as e:
        traceback.print_exc(e)
        await websocket.close()
    

@router.post("/create_game")
async def create_game(session_id: str):
    try:
        session = SessionManager(session_id)
        if not session.is_legit() or session.in_game(): raise

        game_id = generate_game_key()
        table_card = random.choice(normal_cards)
        my_game = {
                'started':False,
                'turn':'red',
                'bots':False,
                'room_type':'private',
                'current_combo':table_card.split('/'),
                'bots_sessions':{},
                'sessions':{
                    session_id: {'leader': True},
                    }
        }

        GameManager(game_id).create_game(**my_game)
        session.join_game()
    except:
        raise HTTPException(status_code=400, detail='Falied to create the game')

@router.post('/public_join')
async def public_join(session_id: str):
        session = SessionManager(session_id)
        if not session.is_legit():
            raise HTTPException(status_code=400, detail='Invalid session.')
        if session.in_game():
            raise HTTPException(status_code=400, detail='Session already in a game.')
        
        all_game_ids = [game_id for game_id in active_games if active_games[game_id]['room_type'] == 'public' and len(active_games[game_id]['sessions']) != 4]

        if not all_game_ids:
            raise HTTPException(status_code=204)
        
        game = GameManager(random.choice(all_game_ids))

        game.add_session(
            session_id,**{
                'name':session.get_name(),
                'cards':[],
                'leader':False,
                'color': None,
                'socket':None,
                'pfp':session.get_pfp()
                }
            )

@router.post('/join')
async def join_game(session_id: str, game_id: str):
    try:
        session = SessionManager(session_id)
        game = GameManager(game_id)

        if not game.exists():
            raise HTTPException(status_code=404, detail='Game not found.')
        if game.started():
            raise HTTPException(status_code=400, detail='Game already started.')
        if session.in_game():
            raise HTTPException(status_code=400, detail='Session already in a game.')
        if game.is_full():
            raise HTTPException(status_code=400, detail='Game is full.')
        if not session.is_legit():
            raise HTTPException(status_code=400, detail='Invalid session.')
        
        game.add_session(
            session_id,**{
                'name':session.get_name(),
                'cards':[],
                'leader':False,
                'color': None,
                'socket':None,
                'pfp':session.get_pfp()
                }
            )
    except:
        raise HTTPException(status_code=400, detail='Failed To Join.') 