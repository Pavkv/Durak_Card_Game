import random

from Classes.Card import Card
from Classes.Player import Player
from Classes.Deck import Deck
from Classes.Table import Table
from Classes.AI import AI


class DurakCardGame:
    def __init__(self, player_name):
        self.deck = Deck()
        self.table = Table()

        self.player = Player(player_name)
        self.ai = AI()
        self.opponent = Player("Opponent")

        self.draw_cards()

        self.last_attacker_played_all = False
        self.last_defender_defended_all = False
        self.was_beaten = False
        self.result = None

        player_trump = self.player.lowest_trump_card(self.deck.trump_suit)
        opponent_trump = self.opponent.lowest_trump_card(self.deck.trump_suit)

        if player_trump and opponent_trump:
            self.current_turn = self.player if not Card.compare_ranks(player_trump.rank,
                                                                      opponent_trump.rank) else self.opponent
        else:
            self.current_turn = random.choice([self.player, self.opponent])

        self.state = "player_attack" if self.current_turn == self.player else "ai_attack"

    def draw_cards(self):
        self.player.draw_from_deck(self.deck)
        self.opponent.draw_from_deck(self.deck)

    def get_hand(self, who="player"):
        return self.player.hand if who == "player" else self.opponent.hand

    def get_table(self):
        return self.table.table

    def is_player_turn(self):
        return self.current_turn == self.player

    def can_attack(self, attacker):
        return len(self.table) == 0 or any(card.rank in self.table.ranks for card in attacker.hand)

    def attack_card(self, card):
        if not self.can_attack(self.current_turn):
            return False
        if not self.table.append(card):
            return False
        self.current_turn.hand.remove(card)
        return True

    def defend_card(self, attack_card, defend_card):
        if not Card.beats(defend_card, attack_card, self.deck.trump_suit):
            return False
        self.opponent.hand.remove(defend_card)
        self.table.beat(attack_card, defend_card)
        return True

    def ai_attack(self):
        card = self.ai.attack(self.opponent.hand, self.table, self.deck.trump_suit)
        if not card or not self.table.append(card):
            return False
        self.opponent.hand.remove(card)
        return True

    def ai_defend(self):
        for attack_card, (beaten, _) in self.table.table.items():
            if not beaten:
                defend_card = self.ai.defense(self.opponent.hand, attack_card, self.deck.trump_suit)
                if defend_card:
                    self.opponent.hand.remove(defend_card)
                    self.table.beat(attack_card, defend_card)
                else:
                    return False
        return True

    def throw_ins(self):
        throw_ins = self.ai.choose_throw_ins(self.opponent.hand, self.table, len(self.player.hand),
                                             self.deck.trump_suit)
        for card in throw_ins:
            if self.table.append(card):
                self.opponent.hand.remove(card)

    def all_cards_defended(self):
        return self.table.beaten()

    def end_turn(self):
        self.deck.discard.extend(self.table.keys())
        self.deck.discard.extend([v[1] for v in self.table.values() if v[1]])

        self.ai.remember_table(self.table)
        self.ai.seen_cards.update(self.deck.discard)

        self.last_attacker_played_all = len(self.table) == len(self.table.table)
        self.last_defender_defended_all = self.table.beaten()

        self.table.clear()
        self.draw_cards()
        self.check_endgame()

        self.current_turn = self.opponent if self.current_turn == self.player else self.player
        self.state = "player_attack" if self.current_turn == self.player else "ai_attack"

    def check_endgame(self):
        if self.deck.cards:
            return

        player_cards = len(self.player.hand)
        opponent_cards = len(self.opponent.hand)

        if player_cards == opponent_cards and self.last_attacker_played_all and self.last_defender_defended_all:
            self.result = "{} is Durak".format(
                self.opponent.name if self.current_turn == self.opponent else self.player.name)
        elif player_cards < opponent_cards:
            self.result = "{} wins! {} is Durak.".format(self.player.name, self.opponent.name)
        else:
            self.result = "{} wins! {} is Durak.".format(self.opponent.name, self.player.name)
