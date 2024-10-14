import asyncio
import random
from fastapi import WebSocket, WebSocketDisconnect
from core.config import *
from core.models.session_manager import SessionManager
from core.game.utils import distribute_cards

class GameManager:
    def __init__(self, game_id: str) -> None:
        self.game_id = game_id

    def create_game(self, **kwargs: dict) -> None:
        active_games[self.game_id] = kwargs

    def exists(self) -> bool:
        return self.game_id in active_games
    
    def has_bots(self) -> bool:
        return active_games[self.game_id]['bots']

    async def start(self) -> None:
        active_games[self.game_id]['started'] = True

        sending_data = {color:{} for color in colors}
        
        game_sessions = list(self.all_sessions().keys())
                
        distribute_cards_layout = distribute_cards(cards)

        layout_shuffled_keys = list(distribute_cards_layout.keys()) 
                
        random.shuffle(layout_shuffled_keys)
        
        # ASSIGN CARDS TO SESSIONS
        for session in game_sessions:
            session_color = layout_shuffled_keys.pop()
            self.update_session(
                session,
                    **{
                        'color':session_color,
                        'cards':distribute_cards_layout[session_color]
                    }
                )
        # ADD BOTS
        if not self.is_full():
            for color in layout_shuffled_keys:
                self.add_bot(color,distribute_cards_layout[color])
                        
        for session in self.all_sessions():
            
            my_color = self.get_color(session)
            my_cards = self.get_cards(my_color)
            for color in colors:
                sending_data[color]['cards'] = ['uno.png']*len(self.get_cards(color)) if color != my_color else my_cards 
            bot_colors =  self.bot_colors()
            for color in colors:
                if color in bot_colors:
                    sending_data[color]['name'] = 'Bot'
                    sending_data[color]['pfp'] = random.choice(valid_pfp)
                else:
                    session_mngr = SessionManager(self.get_session(color))
                    sending_data[color]['name'] = session_mngr.get_name()
                    sending_data[color]['pfp'] = session_mngr.get_pfp()
            try:                    
                await active_games[self.game_id]['sessions'][session]['socket'].send_json(
                    {
                        'action':'start',
                        'color':my_color,
                        'turn':self.get_turn(),
                        'combo':self.current_combo(),
                        'table_card':'/'.join(self.current_combo()),
                        'colors_data':sending_data
                    }
                )

            except WebSocketDisconnect:
                await self.remove_session(session)

    def started(self) -> bool:
        return active_games[self.game_id]['started']

    def session_in_game(self, session_id: str) -> bool:
        return session_id in active_games[self.game_id]['sessions']

    def current_combo(self) -> list:
        return active_games[self.game_id]['current_combo']
    
    def change_combo(self, combo: list):
        active_games[self.game_id]['current_combo'] = combo
    
    def is_leader(self, session_id) -> bool:
        return active_games[self.game_id]['sessions'][session_id]['leader']

    def all_sessions(self) -> dict:
        return active_games[self.game_id]['sessions']

    def change_turn(self, color= None, reverse = False) -> None:
        if color:
            active_games[self.game_id]['turn'] = color
            return
        if reverse: colors.reverse()
        index = colors.index(self.get_turn()) 
        if index == len(colors)-1:
            next_color = colors[0]
        else:
            next_color = colors[index+1]
        active_games[self.game_id]['turn'] = next_color

    def is_full(self) -> bool:
        return len(active_games[self.game_id]['sessions']) == 4

    async def draw_card(self, color: str) -> None:
        data = {
            'action':'draw',
            'color':color,
            'turn':self.get_turn()
        }
        card = random.choice(cards)
        if self.is_bot(color):
            active_games[self.game_id]['bots_sessions'][color].append(card)
            await self.send_all_sockets(data)
        else:
            session_id = self.get_session(color)
            session_socket = active_games[self.game_id]['sessions'][session_id]['socket']
            active_games[self.game_id]['sessions'][session_id]['cards'].append(card)
            await self.send_all_sockets(data,[session_socket])
            data['action'] = 'self_draw'
            data['card'] = card
            all_sockets = self.get_all_sockets()
            all_sockets.remove(session_socket)
            await self.send_all_sockets(data,all_sockets)
           

    def is_bot_turn(self) -> bool:
        try:
            return self.get_turn() in active_games[self.game_id]['bots_sessions'].keys()
        except:
            return False
        
    def is_bot(self, color: str) -> bool:
        try:
            active_games[self.game_id]['bots_sessions'][color]
            return True
        except:
            return False

    def add_bot(self, color: str, cards: list) -> None:
        active_games[self.game_id]['bots_sessions'][color] = cards

    def remove_bot(self, color: str) -> None:
        del active_games[self.game_id]['bots_sessions'][color]

    def get_color(self, session_id: str) -> str:
        return active_games[self.game_id]['sessions'][session_id]['color']
    
    def get_cards(self, color: str) -> list:
        try:
            return [active_games[self.game_id]['sessions'][x]['cards'] for x in active_games[self.game_id]['sessions'] if active_games[self.game_id]['sessions'][x]['color'] == color][0]
        except:
            return active_games[self.game_id]['bots_sessions'][color]
    
    async def end_game(self, winner_color : str) -> None:
        data = {
            'action':'end',
            'color': winner_color
        }
        await self.send_all_sockets(data)
        for session in self.all_sessions():
            try:
                active_sessions[session]['in_game'] = False
            except:
                pass
        del active_games[self.game_id]
 
    async def remove_session(self, session_id: str) -> None:
        color = self.get_color(session_id)
        cards = self.get_cards(color)
        del active_games[self.game_id]['sessions'][session_id]
        if self.started():
           if len(active_games[self.game_id]['sessions']) == 0:
               del active_games[self.game_id]
           else:
            await self.send_all_sockets({'action':'left','color':color})
            self.add_bot(color,cards)
            from core.game.bot import bot_pro
            await bot_pro(self)
        else:
          await self.send_all_sockets({'action':'left','pfp':SessionManager(session_id).get_pfp(),'name':SessionManager(session_id).get_name()})
        SessionManager(session_id).remove()


    async def send_all_sockets(self, data: dict, except_wsocket: list = []) -> None:
            for socket in self.get_all_sockets():
                if socket in except_wsocket: continue
                try:
                    await socket.send_json(data)
                except WebSocketDisconnect:
                    for session in self.all_sessions():
                        if active_games[self.game_id]['sessions'][session]['socket'] == socket: 
                            await self.remove_session(session)
                            return

    def update_session(self, session_id: str, **kwargs: dict) -> None:
        for name, value in kwargs.items():
            active_games[self.game_id]['sessions'][session_id][name] = value

    def change_room_type(self) -> None:
        active_games[self.game_id]['room_type'] = 'public' if self.room_type() == 'private' else 'private'

    def room_type(self) -> str:
        return active_games[self.game_id]['room_type']

    def get_profiles(self, session_id: str) -> dict:
        my_data = {
            'action':'self_joined',
            'players':{},
            'room_type':self.room_type(),
            'game_id':self.game_id,
            'leader':self.is_leader(session_id)
            }
        for session in active_games[self.game_id]['sessions']:
         my_data['players'][SessionManager(session).get_name()] = SessionManager(session).get_pfp()
        return my_data
    
    def bot_colors(self) -> list:
        return list(active_games[self.game_id]['bots_sessions'].keys())

    def get_turn(self) -> str:
        return active_games[self.game_id]['turn']
    
    def add_session(self, session_id: str, **kwargs: dict) -> None:
        active_games[self.game_id]['sessions'][session_id] = {}
        for key, value in kwargs.items():
            active_games[self.game_id]['sessions'][session_id][key] = value

    def has_card(self, session_id: str, card: str) -> bool:
        return card in active_games[self.game_id]['sessions'][session_id]['cards']
    
    def get_all_sockets(self) -> list[WebSocket]:
        return [active_games[self.game_id]['sessions'][x]['socket'] for x in active_games[self.game_id]['sessions'] if active_games[self.game_id]['sessions'][x]['socket']]

    def get_game_id(session_id: str) -> str | None:
        try:
            return [x for x in active_games if session_id in active_games[x]['sessions'].keys()][0]
        except:
            return None   
    
    async def throw_card(self, color : str, card: str, wild_card: bool = False, change_combo: bool = True) -> None:
        if not wild_card:
            if self.is_bot(color):
                active_games[self.game_id]['bots_sessions'][color].remove(card)
                
            else:
                session_id = self.get_session(color)
                active_games[self.game_id]['sessions'][session_id]['cards'].remove(card)
                
        if change_combo: self.change_combo(card.split('/'))

        cards_len = len(self.get_cards(color))

        await self.send_all_sockets({
            'action':'throw',
            'color':color,
            'card':card,
            'combo':self.current_combo(),
            'turn':self.get_turn() if cards_len != 0 else color
        })
        
        if cards_len == 0:
            await asyncio.sleep(1.5)
            await self.end_game(color)
        
    def get_session(self, color: str) -> str:
        for session in self.all_sessions():
            if active_games[self.game_id]['sessions'][session]['color'] == color:
                return session


    async def handle_card(self, color : str, card: str, wild_color: str = None) -> None:
        if card in action_and_wild:
            match card.split('/')[1].split('.')[0]:
                case '+4':
                    if wild_color not in colors: raise
                    self.change_combo([wild_color])
                    self.change_turn()
                    victim_color = self.get_turn()
                    self.change_turn()
                    await self.throw_card(color,card,False,False)
                    for _ in range(4):
                        await asyncio.sleep(1)
                        await self.draw_card(victim_color)
                    await asyncio.sleep(1)
                    await self.throw_card(color,f'{wild_color}/x.png',True,False)

                case '+2':
                    self.change_turn()
                    victim_color = self.get_turn()
                    self.change_turn()
                    await self.throw_card(color,card)
                    for _ in range(2):
                        await asyncio.sleep(1)
                        await self.draw_card(victim_color)
                
                case 'skip':
                    self.change_turn()
                    self.change_turn()
                    await self.throw_card(color,card)

                case 'reverse':
                    self.change_turn(reverse=True)
                    await self.throw_card(color,card)

                case 'wild':
                    if wild_color not in colors: raise
                    self.change_combo([wild_color])
                    self.change_turn()
                    await self.throw_card(color,card,False,False)
                    await asyncio.sleep(1)
                    await self.throw_card(color,f'{wild_color}/x.png',True,False)
        
        else:
            self.change_turn()
            await self.throw_card(color,card)