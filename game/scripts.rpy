init:
    default selected_card = None
    default selected_attack_card = None
    default attack_target = None
    default hovered_card_index = -1
    default selected_card_index = -1
    default next_turn = True

    transform draw_card(x=0, y=0, duration=0.4):
        pos (-50, 350)
        zoom 0.4
        alpha 0.0
        linear duration pos (x, y) zoom 1.0 alpha 1.0

    transform take_card(dest_x, dest_y):
        easeout_cubic 1 xpos dest_x ypos dest_y

init python:
    from DurakCardGame import DurakCardGame

label start:
    "Welcome to Durak!"
    python:
        durak = DurakCardGame("Player1")
    jump durak_game_loop

label durak_game_loop:
    if durak.result:
        $ print("Game Over: ", durak.result)
        $ durak.state = "results"
        jump durak_game_loop

    if durak.state == "ai_attack":
        if durak.can_attack(durak.opponent):
            $ attack_success = durak.ai_attack()
            if attack_success:
                $ print("AI attacked successfully.")
                $ durak.state = "player_defend"
        else:
            $ print("AI could not attack, ending turn.")
            $ durak.state = "end_turn"
    elif durak.state == "ai_defend":
        $ defend_success = durak.ai_defend()
        if defend_success:
            $ print("AI defended successfully.")
            $ durak.state = "player_attack"
        else:
            $ print("AI could not defend, ending turn.")
            $ durak.state = "end_turn"
    elif durak.state == "end_turn":
        $ print("Table before ending turn: ", durak.table)
        $ print("Player hand before ending turn: ", durak.player.hand)
        $ print("Opponent hand before ending turn: ", durak.opponent.hand)
        if durak.current_turn != durak.player and durak.can_attack(durak.opponent):
            $ durak.throw_ins()
        $ durak.end_turn()
        $ print("Discarding table cards", durak.deck.discard)
        $ print("Player hand after ending turn: ", durak.player.hand)
        $ print("Opponent hand after ending turn: ", durak.opponent.hand)
        if durak.result:
            $ durak.state = "results"
        else:
            $ durak.state = durak.state
            $ next_turn = True
    elif durak.state == "results":
        "Game Over: [durak.result]"
        return
    call screen durak()