import random
import uuid
from core.config import cards_per_player, colors

def generate_session_key() -> str:
    """
    Generate a unique session key using UUID4.
    
    Returns:
        str: A unique session key.
    """
    return str(uuid.uuid4())

def generate_game_key() -> str:
    """
    Generate a unique game key using UUID1.
    
    Returns:
        str: A unique game key.
    """
    return str(uuid.uuid4()).replace('-', '')[:6]


def distribute_cards(cards_list: list) -> dict:
    """
    Distribute cards to each color category based on the predefined number of cards per player.

    Args:
        cards_list (list): List of available cards to distribute.

    Returns:
        dict: A dictionary where each key is a color and the value is a list of cards.
    """
    cards_dict = {color: [] for color in colors}

    for color in colors:
        for _ in range(cards_per_player):
            card = random.choice(cards_list)
            cards_dict[color].append(card)
    
    return cards_dict
