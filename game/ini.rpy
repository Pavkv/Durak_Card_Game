init:
    # Card selection and layout state
    default selected_card = None
    default selected_attack_card = None
    default attack_target = None
    default selected_attack_card_index = -1
    default selected_card_index = -1
    default hovered_card_index = -1

    # Turn and animation state
    default deal_cards = True
    default next_turn = True
    default dealt_cards = []
    default is_dealing = False
    default draw_animations = []
    default is_drawing = False
    default table_animations = []
    default is_table_animating = False

    # Deck position
    $ deck_x = 50
    $ deck_y = 350

    # Card layouts
    default player_card_layout = []
    default opponent_card_layout = []

    # Game phase and suit translation
    default durak_state_tl = {
        "player_attack": "Вы атакуете",
        "player_defend": "Вы защищаетесь",
        "ai_attack": "Противник атакует",
        "ai_defend": "Противник защищается",
        "end_turn": "Окончание хода",
        "results": "Игра окончена"
    }
    default card_suits = {
        "C": "♣️",
        "D": "♦️",
        "H": "♥️",
        "S": "♠️"
    }

    # Card transforms
    transform hover_offset(y=0, x=0):
        easein 0.1 yoffset y xoffset x

    transform no_shift:
        xoffset 0
        yoffset 0

    transform deal_card(dest_x, dest_y, delay=0):
        alpha 0.0
        xpos -50
        ypos 350
        pause delay
        linear 0.3 alpha 1.0 xpos dest_x ypos dest_y

    transform animate_table_card(x1, y1, x2, y2, delay=0.0, discard=False):
        alpha 1.0
        xpos x1
        ypos y1
        pause delay
        linear 0.4 xpos x2 ypos y2 alpha 0