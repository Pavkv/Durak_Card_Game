import random

from Classes.Card import Card
from Classes.Player import Player
from Classes.Deck import Deck
from Classes.Table import Table


class DurakCardGame:
    def __init__(self, player_name):
        # Initialize the deck, table
        self.deck = Deck()
        self.table = Table()

        # Initialize players
        self.player = Player(player_name)
        self.opponent = Player("Opponent")
        self.draw_cards()

        # Determine who has the lowest trump card
        player_trump = self.player.lowest_trump_card(self.deck.trump_suit)
        opponent_trump = self.opponent.lowest_trump_card(self.deck.trump_suit)

        # Determine who starts the game
        if player_trump and opponent_trump:
            if not Card.compare_ranks(player_trump.rank, opponent_trump.rank):
                self.current_turn = self.player
            else:
                self.current_turn = self.opponent
        else:
            self.current_turn = random.choice([self.player, self.opponent])

        self.play_turn(self.current_turn, self.opponent if self.current_turn == self.player else self.player)

    def draw_cards(self):
        self.player.draw_from_deck(self.deck)
        self.opponent.draw_from_deck(self.deck)

    def next_turn(self):
        if self.current_turn == self.player:
            self.current_turn = self.opponent
        else:
            self.current_turn = self.player

        self.draw_cards()

        self.play_turn(self.current_turn, self.opponent if self.current_turn == self.player else self.player)

    def attack(self, attacker):
        if attacker == self.player:
            card = input("Choose a card to play (e.g., 7C for 7 of Clubs): ").strip().upper().split("")
            attacker.hand.remove(Card(card[0], card[1]))
        else:
            card = random.choice(attacker.hand)
            attacker.hand.remove(card)

        if not self.table.append(card):
            print(f"{attacker.name} cannot play {card}.")
            return

        print(f"{attacker.name} played {card}.")

    def defend(self, defender):
        if defender == self.player:
            card = input("Choose a card to defend (e.g., 8D for 8 of Diamonds): ").strip().upper().split("")
            defend_card = input("Choose a card to defend with (e.g., 8D for 8 of Diamonds): ").strip().upper().split("")
        else:
            card = random.choice(defender.hand)
            defend_card = random.choice(defender.hand)

        card = Card(card[0], card[1])
        defend_card = Card(defend_card[0], defend_card[1])

        if not Card.beats(card, defend_card, self.deck.trump_suit):
            print(f"{defender.name} cannot defend against {card} with {defend_card}.")
            return

        defender.hand.remove(defend_card)
        self.table.beat(card, defend_card)
        print(f"{defender.name} defended with {card}.")

    def play_turn(self, attacker, defender):
        print(f"\n--- {attacker.name}'s Turn to Attack ---")
        print(f"Trump Suit: {self.deck.trump_suit}")
        print(str(attacker))
        print(str(defender))

        while len(self.table) < 6 or attacker.hand or defender.hand:
            self.attack(attacker)
            continue_defend = input(f"{defender.name}, do you want to defend? (yes/no): ").strip().lower()
            if continue_defend == 'no':
                print(f"{defender.name} cannot defend. {attacker.name} wins the round.")
                break
            self.defend(defender)

        print(f"The end of {attacker.name}'s turn.")
        self.deck.discard.extend(self.table)
        self.table.clear()
        self.next_turn()



