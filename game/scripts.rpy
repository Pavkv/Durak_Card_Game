init:
    default durak = None
    default selected_card = None
    default cards_state = "init"
    default attack_target = None
    default hovered_card_index = -1
    default next_turn = True

    transform draw_card(x=0, y=0, duration=0.4):
        pos (-50, 350)  # deck position
        zoom 0.4
        alpha 0.0
        linear duration pos (x, y) zoom 1.0 alpha 1.0

init python:
    from DurakCardGame import DurakCardGame

label start:
    "Welcome to Durak!"
    python:
        durak = DurakCardGame("Player1")
        cards_state = durak.state
    jump turn

label turn:
    $ player_hand = durak.get_hand("player")
    $ opponent_hand = durak.get_hand("opponent")
    $ next_turn = True
    jump durak_game_loop

label durak_game_loop:

    $ table_cards = durak.get_table()
    $ player_hand = durak.get_hand("player")
    $ opponent_hand = durak.get_hand("opponent")

    show screen show_cards
    $ renpy.pause(100000, hard=True)