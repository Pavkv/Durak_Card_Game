from Classes.Card import Card


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def __str__(self):
        return f"Player {self.name} has {len(self.hand)} cards: {', '.join(str(card) for card in self.hand)}"

    def __len__(self):
        return len(self.hand)

    def draw_from_deck(self, deck):
        self.hand.extend(deck.deal(len(self.hand)))
        self.sort_hand()

    def lowest_trump_card(self, trump):
        trump_cards = [card for card in self.hand if card.suit == trump]
        if not trump_cards:
            return None
        return min(trump_cards, key=lambda card: Card.rank_values[card.rank])

    def sort_hand(self):
        def card_sort_key(card):
            rank_value = Card.rank_values[card.rank]
            return rank_value

        self.hand.sort(key=card_sort_key)
