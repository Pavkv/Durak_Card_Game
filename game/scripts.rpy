label start:
    $ player_name = renpy.input("Введите ваше имя", length=20)
    $ opponent_name = "Противник"
    $ cards_bg = "images/bg/bg_14.jpg"
    $ in_game = False
    $ base_card_img_src = "cards"
    python:
        durak = DurakCardGame(player_name, opponent_name)
        base_cover_img_src = base_card_img_src + "/cover.png"
        durak.opponent.avatar = durak_avatar
        durak.draw_cards()
        compute_hand_layout()
        durak.define_first_turn()

        dealt_cards = []
        is_dealing = True
        deal_cards = True

        delay = 0.0
        for i in range(len(durak.player.hand)):
            dealt_cards.append({
                "owner": "player",
                "index": i,
                "delay": delay
            })
            delay += 0.1

        for i in range(len(durak.opponent.hand)):
            dealt_cards.append({
                "owner": "opponent",
                "index": i,
                "delay": delay
            })
            delay += 0.1

    show screen durak_base_ui
    jump durak_game_loop

label durak_game_loop:

    if is_dealing:
#         $ renpy.block_rollback()
        $ is_dealing = False
        call screen deal_cards
    else:
        $ deal_cards = False

    if durak.result:
#         $ renpy.block_rollback()
        $ print("Game Over: ", durak.result)
        $ durak.state = "results"

    if durak.state == "ai_attack":
#         $ renpy.block_rollback()
        if durak.can_attack(durak.opponent):
            $ attack_success = durak.ai_attack()
            if attack_success:
                $ print("AI attacked successfully.")
                $ durak.state = "player_defend"
        else:
            if not durak.table.beaten() and not confirm_take:
                $ print("AI could not attack, player must defend or take.")
                $ durak.state = "player_defend"
            else:
                $ print("AI could not attack, ending turn.")
                $ confirm_take = False
                $ durak.state = "end_turn"

    elif durak.state == "ai_defend":
#         $ renpy.block_rollback()
        $ defend_success = durak.ai_defend()
        if defend_success:
            $ print("AI defended successfully.")
        else:
            $ print("AI could not defend, ending turn.")
        $ durak.state = "player_attack"

    elif durak.state == "end_turn":
#         $ renpy.block_rollback()

        if durak.current_turn == durak.opponent and durak.can_attack(durak.opponent):
            $ print("Ai adding throw ins.")
            $ durak.throw_ins()

        $ print("Table before ending turn: ", durak.table)
        $ print("Player hand before ending turn: ", durak.player.hand)
        $ print("Opponent hand before ending turn: ", durak.opponent.hand)

        # Make sure old animation is gone
        hide screen table_card_animation

        # Build the new animation list
        python:
            table_animations = []
            delay = 0.0
            for i, (atk, (beaten, def_card)) in enumerate(durak.table.table.items()):
                src_x = 350 + i * 200
                src_y = 375
                cards = list(filter(None, [atk, def_card]))

                if not durak.table.beaten():
                    receiver = durak.player if durak.current_turn != durak.player else durak.opponent
                    for card in cards:
                        table_animations.append({
                            "card": card,
                            "src_x": src_x,
                            "src_y": src_y if card == atk else src_y + 120,
                            "dest_x": 700,
                            "dest_y": 825 if receiver == durak.player else 20,
                            "delay": delay,
                            "target": "hand"
                        })
                        delay += 0.1
                else:
                    for card in cards:
                        table_animations.append({
                            "card": card,
                            "src_x": src_x,
                            "src_y": src_y if card == atk else src_y + 120,
                            "dest_x": 1600,
                            "dest_y": 350,
                            "delay": delay,
                            "target": "discard"
                        })
                        delay += 0.1

        # Show the fresh animation
        show screen table_card_animation
        $ is_table_animating = False

        $ durak.take_or_discard_cards()
        $ durak.end_turn()

        $ print("Discarding table cards", durak.deck.discard)
        $ print("Player hand after ending turn: ", durak.player.hand)
        $ print("Opponent hand after ending turn: ", durak.opponent.hand)

        if durak.result:
            $ durak.state = "results"
        else:
            $ old_player_len = len(durak.player.hand)
            $ old_opponent_len = len(durak.opponent.hand)

            $ durak.draw_cards()
            $ compute_hand_layout()

            $ print("Player hand after drawing: ", durak.player.hand)
            $ print("Opponent hand after drawing: ", durak.opponent.hand)

            $ new_player_len = len(durak.player.hand)
            $ new_opponent_len = len(durak.opponent.hand)

            $ next_turn = True
            $ confirm_take = False

    if durak.state == "results":
#       $ renpy.block_rollback()
        jump expression durak_results[durak.result]

    call screen durak
    jump durak_game_loop
