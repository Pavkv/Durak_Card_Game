init python:
    import random
    from Classes.Card import Card
    from DurakCardGame import DurakCardGame

    CARD_WIDTH, CARD_HEIGHT, CARD_SPACING = 157, 237, 118
    suits = {'uvao': 'C', '2ch': 'D', 'ussr': 'H', 'utan': 'S'}
    ranks = {'6': '6', '7': '7', '8': '8', '9': '9', '10': '10', '11': 'J', '12': 'Q', '13': 'K', '1': 'A'} # '2': '2', '3': '3', '4': '4', '5': '5',
    card_img = {Card(rankv, suitv): f"cards/{rankk}_{suitk}.png"
                for suitk, suitv in suits.items()
                for rankk, rankv in ranks.items()}

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
                print(f"Player defended against {selected_attack_card} with {card}")
                selected_attack_card = None
                durak.state = "ai_attack"
            else:
                print(f"Failed to defend with {card}")
                selected_attack_card = None

    def confirm_selected_attack():
        """Confirms all selected attack cards."""
        global confirm_attack, selected_attack_card_indexes

        if confirm_attack and selected_attack_card_indexes:
            cards = [durak.player.hand[i] for i in sorted(selected_attack_card_indexes)]
            if durak.attack_cards(cards):
                print(f"Player attacked with: {', '.join(str(c) for c in cards)}")
                durak.state = "ai_defend"
                selected_attack_card_indexes.clear()
                confirm_attack = False
                renpy.jump("durak_game_loop")
            else:
                print("Invalid attack. Resetting selection.")
                selected_attack_card_indexes.clear()
                confirm_attack = False