screen durak_base_ui():

    # Base UI for the Durak game
    tag base_ui
    zorder 0

    add "bg.jpg" xpos 0 ypos 0 xysize (1920, 1080)

    # Opponent avatar
    frame:
        background None
        xpos 1750
        ypos 20
        has vbox
        add "opponent.png" xysize (150, 150)
        frame:
            background "textbox_1.png" xysize (150, 35) yoffset 15
            has vbox
            text "Алиса" color "#ffffff" size 30 xpos 25 ypos 3

    # Game Info Box
    $ show_end_turn = durak.table and durak.state in ["player_attack", "player_defend"]
    $ show_confirm_attack = durak.state == "player_attack" and selected_attack_card_index != -1
    if show_end_turn and show_confirm_attack:
        $ y1 = 50
        $ y2 = 60
    else:
        $ y1 = y2 = 50

    frame:
        background None
        xpos 1750
        ypos 823
        has vbox

        frame:
            background "textbox.png" yoffset 10
            has vbox
            text "Фаза Игры:" color "#ffffff" size 20 xpos 7

        frame:
            background "textbox_2.png" yoffset 20
            has vbox
            text "[durak_state_tl[durak.state]]":
                color "#ffffff"
                size 12
                xpos 7
                ypos 7

        if show_end_turn:
            frame:
                background "textbox_2.png"
                ypos y1
                has vbox
                textbutton [" Бито" if durak.state == "player_attack" else "Взять"]:
                    text_size 25
                    xpos 37
                    action If(
                        durak.state == "player_attack",
                        SetVariable("durak.state", "end_turn"),
                        SetVariable("durak.state", "ai_attack")
                    )

        if show_confirm_attack:
            frame:
                background "textbox_1.png"
                ypos y2
                has vbox
                textbutton "Подтвердить\n      атаку":
                    text_size 15 xpos 22 ypos 1
                    action [SetVariable("confirm_attack", True), Function(confirm_selected_attack)]

    # Deck and Trump Card
    $ deck_text = str(len(durak.deck.cards)) if len(durak.deck.cards) > 0 else card_suits[durak.deck.trump_suit]
    $ deck_xpos = 55 if len(durak.deck.cards) > 9 else 73

    if durak.deck.cards:
        $ trump = durak.deck.trump_card
        if trump:
            add Transform(card_img[trump], xysize=(CARD_WIDTH, CARD_HEIGHT), rotate=90):
                xpos CARD_WIDTH // 2 - 55
                ypos 350

        add Transform("cards/cover.png", xysize=(CARD_WIDTH, CARD_HEIGHT), rotate=0):
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
        add Transform("cards/cover.png", xysize=(CARD_WIDTH, CARD_HEIGHT), rotate=rotate + 15):
            xpos 1600
            ypos 350
        $ rotate += 15 if rotate < 360 else -360

    if not deal_cards:
        # Opponent hand layout
        for i, card in enumerate(durak.opponent.hand):
            $ card_x = opponent_card_layout[i]["x"]
            $ card_y = opponent_card_layout[i]["y"]

            add Transform("cards/cover.png", xysize=(CARD_WIDTH, CARD_HEIGHT)):
                xpos card_x
                ypos card_y

        # Player hand
        for i, card in enumerate(durak.player.hand):
            $ card_x = player_card_layout[i]["x"]
            $ card_y = player_card_layout[i]["y"]

            $ is_hovered = (i == hovered_card_index)
            $ is_adjacent = abs(i - hovered_card_index) == 1
            $ is_selected = (i == selected_attack_card_index)

            $ x_shift = 20 if i == hovered_card_index + 1 else (-20 if i == hovered_card_index - 1 else 0)
            $ y_shift = -80 if is_hovered or is_selected else 0

            imagebutton:
                idle Transform(card_img[card], xysize=(CARD_WIDTH, CARD_HEIGHT))
                hover Transform(card_img[card], xysize=(CARD_WIDTH, CARD_HEIGHT))
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
            $ card_img_src = card_img[durak.player.hand[i]]
        else:
            $ dest_x = opponent_card_layout[i]["x"]
            $ dest_y = opponent_card_layout[i]["y"]
            $ card_img_src = "cards/cover.png"

        add Transform(card_img_src, xysize=(CARD_WIDTH, CARD_HEIGHT)) at deal_card(dest_x, dest_y, delay)

    timer delay + 1.0 action Return()

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
            $ card_img_src = card_img[durak.player.hand[i]]
        else:
            $ spacing = CARD_SPACING
            $ total = len(durak.opponent.hand)
            $ total_width = CARD_WIDTH + (total - 1) * spacing
            $ start_x = max((1920 - total_width) // 2, 20)
            $ dest_x = start_x + i * spacing
            $ dest_y = 20
            $ card_img_src = "cards/cover.png"

        add Transform(card_img_src, xysize=(CARD_WIDTH, CARD_HEIGHT)) at deal_card(dest_x, dest_y, delay)

    timer delay + 1.0 action Return()

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
        $ card_img_src = card_img.get(card, "cards/cover.png")

        add Transform(card_img_src, xysize=(CARD_WIDTH, CARD_HEIGHT)) at animate_table_card(src_x, src_y, dest_x, dest_y, delay, is_discard)

    timer 0.5 action Return()

screen durak():

    # Main Durak game screen
    timer .5 action SetVariable("next_turn", False)
    if durak.state not in ["player_attack", "player_defend"]:
         timer 5 action Jump("durak_game_loop")

    # Table cards
    for i, (atk, (beaten, def_card)) in enumerate(durak.table.table.items()):
        $ atk_x = 350 + i * 200
        $ atk_y = 375

        if durak.state == "player_defend" and not beaten:
            $ is_selected = selected_attack_card == atk
            imagebutton:
                idle Transform(card_img[atk], xysize=(CARD_WIDTH, CARD_HEIGHT),
                               yoffset=-20 if is_selected else 0,
                               alpha=1.0 if is_selected else 0.9)
                hover Transform(card_img[atk], xysize=(CARD_WIDTH, CARD_HEIGHT), yoffset=-20)
                xpos atk_x
                ypos atk_y
                action SetVariable("selected_attack_card", atk)
        else:
            add Transform(card_img[atk], xysize=(CARD_WIDTH, CARD_HEIGHT)):
                xpos atk_x
                ypos atk_y

        if def_card:
            add Transform(card_img[def_card], xysize=(CARD_WIDTH, CARD_HEIGHT)):
                xpos atk_x
                ypos atk_y + 120

    # Show result if needed
    if durak.result:
        frame:
            xpos 600
            ypos 400
            has vbox
            text "[durak.result]" size 40
            textbutton "Return to menu":
                action Return()