import random

from Classes.Card import Card


class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for suit in Card.suits for rank in Card.ranks]
        self.discard = []
        self.shuffle()
        self.trump_card = self.get_trump_card()
        self.trump_suit = self.trump_card.suit if self.trump_card else None

    def shuffle(self):
        random.shuffle(self.cards)

    def get_trump_card(self):
        return self.cards[-1] if self.cards else None

    def deal(self, num_cards):
        return [self.cards.pop(0) for _ in range(min(6 - num_cards, len(self.cards)))]