from core.models.game_manager import GameManager
from core.models.session_manager import SessionManager
from fastapi import WebSocket
from core.config import *
from core.game.bot import bot_pro
import asyncio

async def game_handler_main(game: GameManager, websocket: WebSocket, session_id: str) -> None:
    """
    Main handler for managing game actions through WebSocket communication.
    
    Args:
        game (GameManager): The game manager instance controlling the game.
        websocket (WebSocket): The WebSocket connection for client communication.
        session_id (str): The session ID of the player.

    This function listens for client messages, processes game actions, and interacts with the bot.
    """
    while game.exists() and SessionManager(session_id).is_legit():
        
        data = await websocket.receive_json()

        sender_session = data.get('session')
        
        if sender_session != session_id:
            # Ignore messages from other sessions
            continue
        # Only leader commands
        if game.is_leader(session_id) and not game.started():
            
            if data.get('start_game'):
                await game.start()
                await asyncio.sleep(17)  # Wait for some time before starting the bot
                await bot_pro(game)

            if data.get('change_room_type'):
                game.change_room_type()
                await game.send_all_sockets(
                    {
                        'action':'room_type_change',
                        'room_type':game.room_type()
                    }
                )
                
        elif game.started():
            if game.get_turn() != game.get_color(session_id):
                # Ignore actions if it's not the player's turn
                continue

            action = data.get('action')
            if action == 'throw':
                throwing_card = data.get('thrown')
                wild_color = data.get('wild_color_send')

                # Validate if the player has the card to throw
                if throwing_card and (game.has_card(session_id, throwing_card) or game.has_card(session_id, f"{throwing_card.split('-')[0]}.png")):
                    await game.handle_card(game.get_color(session_id), throwing_card, wild_color)
                else:
                    # Card not found in the player's hand or invalid action
                    continue
                
            elif action == 'draw':
                game.change_turn()
                await game.draw_card(game.get_color(session_id))

            await bot_pro(game)


