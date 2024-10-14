import random
import asyncio
from core.models.game_manager import GameManager
from core.config import colors

def bot_throw_card_func(x_cards: list, aval_plays: list) -> list:
    """
    Determine which cards the bot can throw based on available plays and special cards.
    
    Args:
        x_cards (list): List of cards the bot currently holds.
        aval_plays (list): List of valid plays (colors or numbers) on the current combo.

    Returns:
        list: A list of cards that the bot can throw. If none, returns None.
    """
    cards_can_throw = []
    for card in x_cards:
        # Check if the card matches any part of available plays or is a special card
        if any(part in aval_plays for part in card.split('/')) or card in ['special/+4.png', 'special/wild.png']:
            cards_can_throw.append(card)

    if not cards_can_throw:
        return None
    
    return random.choice(cards_can_throw)

async def bot_pro(game: GameManager) -> None:
    """
    Main function for bot operations in the game. The bot performs actions every few seconds
    as long as it is its turn.

    Args:
        game (GameManager): The game manager instance managing the game state.
    """
    while game.is_bot_turn():
        await asyncio.sleep(5)  # Bot actions happen every 5 seconds
        
        bot_color = game.get_turn()
        bot_cards = game.get_cards(bot_color)
        bot_thrown_card = bot_throw_card_func(bot_cards, game.current_combo())

        if bot_thrown_card:
            if bot_thrown_card in ['special/+4.png', 'special/wild.png']:
                # Handle special cards with additional logic
                await game.handle_card(bot_color, bot_thrown_card, random.choice(colors))
            else:
                # Handle regular cards
                await game.handle_card(bot_color, bot_thrown_card)
        else:
            # If no card can be thrown, draw a new card and change turn
            game.change_turn()
            await game.draw_card(bot_color)
