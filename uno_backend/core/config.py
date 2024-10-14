active_games = {}
active_sessions = {}
colors = ['red','green','blue','yellow']
valid_pfp = ['pfp/0.jpg','pfp/1.jpg','pfp/2.jpg','pfp/3.jpg','pfp/4.jpg','pfp/5.jpg']
normal_cards = [
    # Number cards
    "red/0.png", "red/1.png", "red/1.png", "red/2.png", "red/2.png",
    "red/3.png", "red/3.png", "red/4.png", "red/4.png", "red/5.png",
    "red/5.png", "red/6.png", "red/6.png", "red/7.png", "red/7.png",
    "red/8.png", "red/8.png", "red/9.png", "red/9.png",
    "yellow/0.png", "yellow/1.png", "yellow/1.png", "yellow/2.png", "yellow/2.png",
    "yellow/3.png", "yellow/3.png", "yellow/4.png", "yellow/4.png", "yellow/5.png",
    "yellow/5.png", "yellow/6.png", "yellow/6.png", "yellow/7.png", "yellow/7.png",
    "yellow/8.png", "yellow/8.png", "yellow/9.png", "yellow/9.png",
    "green/0.png", "green/1.png", "green/1.png", "green/2.png", "green/2.png",
    "green/3.png", "green/3.png", "green/4.png", "green/4.png", "green/5.png",
    "green/5.png", "green/6.png", "green/6.png", "green/7.png", "green/7.png",
    "green/8.png", "green/8.png", "green/9.png", "green/9.png",
    "blue/0.png", "blue/1.png", "blue/1.png", "blue/2.png", "blue/2.png",
    "blue/3.png", "blue/3.png", "blue/4.png", "blue/4.png", "blue/5.png",
    "blue/5.png", "blue/6.png", "blue/6.png", "blue/7.png", "blue/7.png",
    "blue/8.png", "blue/8.png", "blue/9.png", "blue/9.png",
]
action_and_wild = [
    # Action cards
    "red/reverse.png", "red/reverse.png", "red/skip.png", "red/skip.png",
    "red/+2.png", "red/+2.png",
    "yellow/reverse.png", "yellow/reverse.png", "yellow/skip.png", "yellow/skip.png",
    "yellow/+2.png", "yellow/+2.png",
    "green/reverse.png", "green/reverse.png", "green/skip.png", "green/skip.png",
    "green/+2.png", "green/+2.png",
    "blue/reverse.png", "blue/reverse.png", "blue/skip.png", "blue/skip.png",
    "blue/+2.png", "blue/+2.png",
    
    # # Wild cards
    "special/+4.png", "special/+4.png", "special/+4.png", "special/+4.png",
    "special/wild.png", "special/wild.png", "special/wild.png", "special/wild.png"
]
cards = normal_cards + action_and_wild
cards_per_player = 7

session_expiry_time = 0.3 # (in hours)

garbage_clean_every = 1 # (in hours)