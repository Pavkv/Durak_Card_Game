screen durak_base_ui():

    # Base UI for the Durak game
    tag base_ui
    zorder 0

    add cards_bg xpos 0 ypos 0 xysize (1920, 1080)

    if not in_game:
        frame:
            xpos 1755
            ypos 750
            xsize 150
            padding (0, 0)
            has vbox
            textbutton "{color=#fff}Вернуться в меню{/color}":
                style "card_game_button"
                text_size 23
                action [
                    Function(reset_durak_game),
                    Hide("durak_base_ui"),
                    Return(),
                ]

    if durak.result:
       timer 0.5 action Jump("durak_game_loop")
    else:
        # Opponent avatar
        frame:
            background None
            xpos 1750
            ypos 20
            has vbox

            frame:
                background RoundRect("#b2b3b4", 10)
                xysize (150, 150)
                add opponent_avatar_displayable(size=(150, 150), pad=10) align (0.5, 0.5)

            frame:
                background RoundRect("#b2b3b4", 10)
                xsize 150
                yoffset 8
                padding (5, 5)
                text durak.opponent.name color "#ffffff" text_align 0.5 align (0.5, 0.5)

        # Game Info Box
        $ show_end_turn = durak.table and durak.state in ["player_attack", "player_defend"]
        $ show_confirm_attack = durak.state == "player_attack" and len(selected_attack_card_indexes) > 0
        if show_end_turn and show_confirm_attack:
            $ y1 = 30
            $ y2 = 40
        else:
            $ y1 = y2 = 30

        frame:
            background None
            xpos 1750
            ypos 823
            has vbox

            frame:
                background RoundRect("#b2b3b4", 10)
                xsize 150
                yoffset 10
                padding (5, 5)
                text "Фаза Игры:" color "#ffffff" text_align 0.5 align (0.5, 0.5)

            frame:
                background RoundRect("#b2b3b4", 10)
                xsize 150
                yoffset 20
                padding (5, 5)
                $ phase_text = "—"
                if durak is not None and hasattr(durak, "state") and durak.state in durak_state_tl:
                    $ phase_text = durak_state_tl[durak.state]

                text phase_text:
                    color "#ffffff"
                    size 19
                    text_align 0.5
                    align (0.5, 0.5)

            if show_end_turn:
                frame:
                    xsize 150
                    padding (0, 0)
                    ypos y1
                    has vbox
                    textbutton ["{color=#fff}Бито{/color}" if durak.state == "player_attack" else "{color=#fff}Взять{/color}"]:
                        style "card_game_button"
                        text_size 25
                        action [If(
                            durak.state == "player_attack",
                            [SetVariable("durak.state", "end_turn"), SetVariable("selected_attack_card_indexes", set())],
                            SetVariable("durak.state", "ai_attack")
                        ), SetVariable("confirm_take", True)]

            if show_confirm_attack:
                frame:
                    xsize 150
                    padding (0, 0)
                    ypos y2
                    has vbox
                    textbutton "{color=#fff}Подтвердить\nатаку{/color}":
                        style "card_game_button"
                        text_size 18
                        action [SetVariable("confirm_attack", True), Function(confirm_selected_attack)]

        # Deck and Trump Card
        $ deck_text = str(len(durak.deck.cards)) if len(durak.deck.cards) > 0 else card_suits[durak.deck.trump_suit]
        $ deck_xpos = 55 if len(durak.deck.cards) > 9 else 73

        if durak.deck.cards:
            $ trump = durak.deck.trump_card
            if trump:
                add Transform(get_card_image(trump), xysize=(CARD_WIDTH, CARD_HEIGHT), rotate=90):
                    xpos CARD_WIDTH // 2 - 55
                    ypos 350

            add Transform(base_cover_img_src, xysize=(CARD_WIDTH, CARD_HEIGHT), rotate=0):
                xpos -50
                ypos 350

            text deck_text:
                xpos deck_xpos
                ypos 455
                size 60
        else:
            text card_suits[durak.deck.trump_suit]:
                xpos deck_xpos
                ypos 455
                size 75

        # Discard pile
        $ rotate = 0
        for card in durak.deck.discard:
            add Transform(base_cover_img_src, xysize=(CARD_WIDTH, CARD_HEIGHT), rotate=rotate + 15):
                xpos 1600
                ypos 350
            $ rotate += 15 if rotate < 360 else -360

        if not deal_cards:
            # Opponent hand layout
            for i, card in enumerate(durak.opponent.hand):
                $ card_x = opponent_card_layout[i]["x"]
                $ card_y = opponent_card_layout[i]["y"]

                add Transform(base_cover_img_src, xysize=(CARD_WIDTH, CARD_HEIGHT)):
                    xpos card_x
                    ypos card_y

            # Player hand
            for i, card in enumerate(durak.player.hand):
                $ card_x = player_card_layout[i]["x"]
                $ card_y = player_card_layout[i]["y"]

                $ is_hovered = (i == hovered_card_index)
                $ is_adjacent = abs(i - hovered_card_index) == 1
                $ is_selected = (i in selected_attack_card_indexes)

                $ x_shift = 20 if i == hovered_card_index + 1 else (-20 if i == hovered_card_index - 1 else 0)
                $ y_shift = -80 if is_hovered or is_selected else 0
                imagebutton:
                    idle Transform(get_card_image(card), xysize=(CARD_WIDTH, CARD_HEIGHT))
                    hover Transform(get_card_image(card), xysize=(CARD_WIDTH, CARD_HEIGHT))
                    xpos card_x
                    ypos card_y
                    at hover_offset(y=y_shift, x=x_shift)
                    action Function(handle_card_click, i)
                    hovered If(hovered_card_index != i, SetVariable("hovered_card_index", i))
                    unhovered If(hovered_card_index == i, SetVariable("hovered_card_index", -1))

screen deal_cards():

    for card_data in dealt_cards:

        $ i = card_data["index"]
        $ delay = card_data["delay"]

        if card_data["owner"] == "player":
            $ dest_x = player_card_layout[i]["x"]
            $ dest_y = player_card_layout[i]["y"]
            $ card_img_src = get_card_image(durak.player.hand[i])
        else:
            $ dest_x = opponent_card_layout[i]["x"]
            $ dest_y = opponent_card_layout[i]["y"]
            $ card_img_src = base_cover_img_src

        add Transform(card_img_src, xysize=(CARD_WIDTH, CARD_HEIGHT)) at deal_card(dest_x, dest_y, delay)

    timer delay + 1.0 action Jump("durak_game_loop")

screen draw_cards():

    # Animate drawing cards for player and opponent
    for card_data in draw_animations:

        $ i = card_data["index"]
        $ delay = card_data["delay"]

        if card_data["owner"] == "player":
            $ spacing = CARD_SPACING
            $ total = len(durak.player.hand)
            $ total_width = CARD_WIDTH + (total - 1) * spacing
            $ start_x = max((1920 - total_width) // 2, 20)
            $ dest_x = start_x + i * spacing
            $ dest_y = 825
            $ card_img_src = get_card_image(durak.player.hand[i])
        else:
            $ spacing = CARD_SPACING
            $ total = len(durak.opponent.hand)
            $ total_width = CARD_WIDTH + (total - 1) * spacing
            $ start_x = max((1920 - total_width) // 2, 20)
            $ dest_x = start_x + i * spacing
            $ dest_y = 20
            $ card_img_src = base_cover_img_src

        add Transform(card_img_src, xysize=(CARD_WIDTH, CARD_HEIGHT)) at deal_card(dest_x, dest_y, delay)

    timer delay + 1.0 action Jump("durak_game_loop")

screen table_card_animation():

    # Animate table cards moving to hand or discard
    for anim in table_animations:

        $ card = anim["card"]
        $ src_x = anim["src_x"]
        $ src_y = anim["src_y"]
        $ dest_x = anim["dest_x"]
        $ dest_y = anim["dest_y"]
        $ delay = anim["delay"]
        $ is_discard = anim["target"] == "discard"

        add Transform(get_card_image(card), xysize=(CARD_WIDTH, CARD_HEIGHT)) at animate_table_card(src_x, src_y, dest_x, dest_y, delay, is_discard)

    timer 0.5 action Hide("table_card_animation")

screen durak():

    # Main Durak game screen
    timer .5 action SetVariable("next_turn", False)
    if durak.state not in ["player_attack", "player_defend"]:
         timer 5 action Jump("durak_game_loop")

    # Table cards
    $ num_table_cards = len(durak.table.table)
    $ max_table_width = 1280
    $ base_x = 320
    $ pair_spacing = min(200, max_table_width // max(1, num_table_cards))

    for i, (atk, (beaten, def_card)) in enumerate(durak.table.table.items()):
        $ atk_x = base_x + i * pair_spacing
        $ atk_y = 375

        if durak.state == "player_defend" and not beaten:
            $ is_selected = selected_attack_card == atk
            imagebutton:
                idle Transform(get_card_image(atk), xysize=(CARD_WIDTH, CARD_HEIGHT),
                               yoffset=-20 if is_selected else 0,
                               alpha=1.0 if is_selected else 0.9)
                hover Transform(get_card_image(atk), xysize=(CARD_WIDTH, CARD_HEIGHT), yoffset=-20)
                xpos atk_x
                ypos atk_y
                action SetVariable("selected_attack_card", atk)
        else:
            add Transform(get_card_image(atk), xysize=(CARD_WIDTH, CARD_HEIGHT)):
                xpos atk_x
                ypos atk_y

        if def_card:
            add Transform(get_card_image(def_card), xysize=(CARD_WIDTH, CARD_HEIGHT)):
                xpos atk_x
                ypos atk_y + 120
