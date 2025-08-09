init python:
    import random
    from Classes.Card import Card
    from DurakCardGame import DurakCardGame

    CARD_WIDTH, CARD_HEIGHT, CARD_SPACING = 157, 237, 118
    suits = {'C': 'uvao', 'D': '2ch', 'H': 'ussr', 'S': 'utan'}
    ranks = {'6': '6', '7': '7', '8': '8', '9': '9', '10': '10', 'J': '11', 'Q': '12', 'K': '13', 'A': '1'} # '2': '2', '3': '3', '4': '4', '5': '5',

    def get_card_image(card):
        """Returns the image path for a card based on its rank and suit."""
        return base_card_img_src + "/{}_{}.png".format(ranks[card.rank], suits[card.suit])

    def compute_hand_layout():
        """Computes the layout for player and opponent hands based on the number of cards."""
        global player_card_layout, opponent_card_layout
        def layout(total, y, max_right_x):
            total_width = CARD_WIDTH + (total - 1) * CARD_SPACING
            max_hand_width = max_right_x - 20
            if total_width <= max_hand_width:
                spacing = CARD_SPACING
                start_x = max((1920 - total_width) // 2, 20)
            else:
                spacing = (max_hand_width - CARD_WIDTH) // max(total - 1, 1)
                start_x = 20
            return [{"x": start_x + i * spacing, "y": y} for i in range(total)]
        player_card_layout = layout(len(durak.player.hand), 825, 1700)
        opponent_card_layout = layout(len(durak.opponent.hand), 20, 1680)

    def handle_card_click(index):
        """Handles card click events for player actions."""
        global confirm_attack, selected_attack_card_indexes, selected_attack_card
        card = durak.player.hand[index]
        print("Card clicked:", card)

        if durak.state == "player_attack":
            if index in selected_attack_card_indexes:
                selected_attack_card_indexes.remove(index)
            else:
                selected_attack_card_indexes.add(index)
            confirm_attack = len(selected_attack_card_indexes) > 0

        elif durak.state == "player_defend" and selected_attack_card:
            if durak.defend_card(card, selected_attack_card):
                print("Player defended against " + str(selected_attack_card) + " with " + str(card))
                selected_attack_card = None
                durak.state = "ai_attack"
            else:
                print("Failed to defend with " + card)
                selected_attack_card = None

    def confirm_selected_attack():
        """Confirms all selected attack cards."""
        global confirm_attack, selected_attack_card_indexes

        if confirm_attack and selected_attack_card_indexes:
            cards = [durak.player.hand[i] for i in sorted(selected_attack_card_indexes)]
            if durak.attack_cards(cards):
                print("Player attacked with: " + ', '.join(str(c) for c in cards))
                durak.state = "ai_defend"
                selected_attack_card_indexes.clear()
                confirm_attack = False
                renpy.jump("durak_game_loop")
            else:
                print("Invalid attack. Resetting selection.")
                selected_attack_card_indexes.clear()
                confirm_attack = False

    def reset_durak_game():
        durak = DurakCardGame()
        player_name = None
        base_card_img_src = None
        base_cover_img_src = None
        opponent = None
        cards_bg = None
        selected_card = None
        selected_attack_card = None
        attack_target = None
        selected_attack_card_indexes = set()
        selected_card_indexes = set()
        hovered_card_index = -1
        confirm_attack = False
        confirm_take = False
        next_turn = True
        dealt_cards = []
        is_dealing = False
        draw_animations = []
        is_drawing = False
        table_animations = []
        is_table_animating = False
        player_card_layout = []
        opponent_card_layout = []

    def get_opponent_avatar_base():
        """
        Returns a path/displayable for the opponent avatar.
        Supports dict (prefers 'body') or string; falls back to placeholder.
        """
        placeholder = "images/cards/avatars/empty_avatar.png"
        try:
            opp = getattr(store, "durak").opponent
            av = getattr(opp, "avatar", None)

            # dict: prefer 'body'
            if isinstance(av, dict):
                body = av.get("body")
                if body:
                    return body
                # pick first string in dict if no 'body'
                for v in av.itervalues():
                    if isinstance(v, basestring):
                        return v
                return placeholder

            # string path
            if isinstance(av, basestring):
                return av
        except Exception:
            pass
        return placeholder

    def opponent_avatar_displayable(size=(150, 150), pad=6, top_pad=6):
        """
        Returns the avatar scaled to fit inside `size` with side padding
        and only top padding (no bottom padding).
        """
        base = get_opponent_avatar_base()

        # Width reduced by side padding, height reduced only by top padding
        inner_w = max(1, size[0] - pad * 2)
        inner_h = max(1, size[1] - top_pad - 2)

        avatar = Transform(base, xysize=(inner_w, inner_h))

        # Fixed container
        box = Fixed(
            xmaximum=size[0], ymaximum=size[1],
            xminimum=size[0], yminimum=size[1]
        )

        # Apply left/right and top padding, but let it reach the bottom
        positioned_avatar = Transform(avatar, xpos=pad, ypos=top_pad)

        box.add(positioned_avatar)
        return box
