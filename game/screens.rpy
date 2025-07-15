init python:
    card_img = {}
    suits = {'uvao': 'C', '2ch': 'D', 'ussr': 'H', 'utan': 'S'}
    ranks = {'6': '6', '7': '7', '8': '8', '9': '9', '10': '10', '11': 'J', '12': 'Q', '13': 'K', '1': 'A'}
    CARD_WIDTH = 157
    CARD_HEIGHT = 237
    CARD_SPACING = 118

    from Classes.Card import Card

    for suitk, suitv in suits.items():
        for rankk, rankv in ranks.items():
            key = Card(rankv, suitv)
            path = f"cards/{rankk}_{suitk}.png"
            card_img[key] = path

    def handle_card_click(index):
        card = durak.get_hand("player")[index]

        if durak.state == "player_attack":
            if durak.attack_card(card):
                durak.state = "ai_defend"

        elif durak.state == "player_defend":
            global selected_attack_card
            if selected_attack_card and durak.defend_card(selected_attack_card, card):
                selected_attack_card = None
                if durak.all_cards_defended():
                    durak.state = "end_turn"

screen show_cards():

    tag cardgame
    modal True

    # Background
    add "bg.jpg" xpos 0 ypos 0 xysize (1920, 1080)

    timer .5 action SetVariable("next_turn", False)

    # Opponent hand
    $ opp_total = len(opponent_hand)
    $ opp_total_width = CARD_WIDTH + (opp_total - 1) * CARD_SPACING
    $ opp_start_x = (1920 - opp_total_width) // 2 + 100
    for i, card in enumerate(opponent_hand):
        $ card_x = opp_start_x + i * CARD_SPACING - 100
        $ card_y = 20

        if next_turn:
            add Transform("cards/cover.png", xysize=(CARD_WIDTH, CARD_HEIGHT)) at draw_card(card_x, card_y)
        else:
            add Transform("cards/cover.png", xysize=(CARD_WIDTH, CARD_HEIGHT)):
                xpos card_x
                ypos card_y


    # Table cards
    for i, (atk, (beaten, def_card)) in enumerate(table_cards.items()):
        $ atk_x = 350 + i * 200
        $ atk_y = 375

        if durak.state == "player_defend" and not beaten:
            imagebutton:
                idle Transform(card_img[atk], xysize=(CARD_WIDTH, CARD_HEIGHT))
                xpos atk_x
                ypos atk_y
                action SetVariable("selected_attack_card", atk)
        else:
            add Transform(card_img[atk], xysize=(CARD_WIDTH, CARD_HEIGHT)):
                xpos atk_x
                ypos atk_y

        if def_card:
            add Transform(card_img[def_card], xysize=(CARD_WIDTH, CARD_HEIGHT)):
                xpos 350 + i * 200
                ypos 420

    # Player hand
    $ total_cards = len(player_hand)
    $ total_width = CARD_WIDTH + (total_cards - 1) * CARD_SPACING
    $ start_x = (1920 - total_width) // 2
    for i, card in enumerate(player_hand):

        $ offset = 0

        if hovered_card_index != -1:
            if i == hovered_card_index:
                $ offset = -80
            elif abs(i - hovered_card_index) == 1:
                $ offset = 20 if i > hovered_card_index else -20
            else:
                $ offset = 0

        $ card_x = start_x + i * CARD_SPACING
        $ card_y = 825

        if next_turn:
            imagebutton:
                at draw_card(card_x, card_y)
                idle Transform(card_img[card], xysize=(CARD_WIDTH, CARD_HEIGHT),
                               xoffset=(offset if i != hovered_card_index else 0),
                               yoffset=(offset if i == hovered_card_index else 0))
                action Function(handle_card_click, i)
                hovered SetVariable("hovered_card_index", i)
                unhovered SetVariable("hovered_card_index", -1)
        else:
            imagebutton:
                idle Transform(card_img[card], xysize=(CARD_WIDTH, CARD_HEIGHT),
                               xoffset=(offset if i != hovered_card_index else 0),
                               yoffset=(offset if i == hovered_card_index else 0))
                xpos card_x
                ypos card_y
                action Function(handle_card_click, i)
                hovered SetVariable("hovered_card_index", i)
                unhovered SetVariable("hovered_card_index", -1)



    # Deck (face-down)
    if durak.deck.cards:
        $ trump = durak.deck.trump_card
        if trump:
            # Trump card FIRST (drawn below deck)
            add Transform(card_img[trump], xysize=(CARD_WIDTH, CARD_HEIGHT), rotate=90):
                xpos CARD_WIDTH // 2 - 55
                ypos 350

        # Deck (face-down on top)
        add Transform("cards/cover.png", xysize=(CARD_WIDTH, CARD_HEIGHT), rotate=0):
            xpos -50
            ypos 350

    # Discard pile (show last discarded card)
    if durak.deck.discard:
        add Transform("cards/cover.png", xysize=(CARD_WIDTH, CARD_HEIGHT), rotate=90):
            xpos 1500
            ypos 350
        add Transform("cards/cover.png", xysize=(CARD_WIDTH, CARD_HEIGHT), rotate=45):
            xpos 1500
            ypos 350
        add Transform("cards/cover.png", xysize=(CARD_WIDTH, CARD_HEIGHT), rotate=135):
            xpos 1500
            ypos 350


    # State label
    text "Phase: [cards_state]" xpos 20 ypos 20 size 30

    # Show result if needed
    if durak.result:
        frame:
            xpos 600
            ypos 400
            has vbox
            text "[durak.result]" size 40
            textbutton "Return to menu":
                action Return()