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

    def next_turn(self, beaten):
        if beaten:
            if self.current_turn == self.player:
                self.current_turn = self.opponent
            else:
                self.current_turn = self.player

        self.draw_cards()

        self.play_turn(self.current_turn, self.opponent if self.current_turn == self.player else self.player)

    def attack(self, attacker):
        if attacker == self.player:
            while True:
                user_input = input("Choose a card to play (e.g., 7C for 7 of Clubs): ").strip().upper()
                rank = user_input[:-1]
                suit = user_input[-1]

                selected_card = next((card for card in attacker.hand if card.rank == rank and card.suit == suit), None)

                if not selected_card:
                    print("You don't have that card. Try another.")
                    continue

                if not self.table.append(selected_card):
                    print("You can't play that card (rank doesn't match cards on table). Try another.")
                    continue

                attacker.hand.remove(selected_card)
                print(f"{attacker.name} played {selected_card}.")
                return True  # success
        else:
            # Computer plays a random valid card
            valid_cards = [card for card in attacker.hand if self.table.append(card)]

            # If the table accepted none of the cards, end the round
            if not valid_cards:
                print(f"{attacker.name} has no valid cards to attack.")
                return False  # nothing to play

            selected_card = random.choice(valid_cards)
            attacker.hand.remove(selected_card)
            print(f"{attacker.name} played {selected_card}.")
            return True

    def defend(self, defender):
        if defender == self.player:
            while True:
                target_input = input("Which card are you defending against? (e.g., 7C): ").strip().upper()
                defend_input = input("Which card do you want to defend with? (e.g., 8C): ").strip().upper()

                target_rank, target_suit = target_input[:-1], target_input[-1]
                defend_rank, defend_suit = defend_input[:-1], defend_input[-1]

                attack_card = next(
                    (card for card in self.table.table if card.rank == target_rank and card.suit == target_suit), None)
                defend_card = next(
                    (card for card in defender.hand if card.rank == defend_rank and card.suit == defend_suit), None)

                if not Card.beats(defend_card, attack_card, self.deck.trump_suit):
                    print(f"{defend_card} does not beat {attack_card}. Try a different card.")
                    continue

                defender.hand.remove(defend_card)
                self.table.beat(attack_card, defend_card)
                print(f"{defender.name} defended {attack_card} with {defend_card}.")
                break

        else:
            # Computer defense placeholder (not yet intelligent)
            for attack_card in self.table.table:
                if not self.table.table[attack_card][0]:
                    for defend_card in defender.hand:
                        if Card.beats(defend_card, attack_card, self.deck.trump_suit):
                            defender.hand.remove(defend_card)
                            self.table.beat(attack_card, defend_card)
                            print(f"{defender.name} defended {attack_card} with {defend_card}.")
                            return
            print(f"{defender.name} cannot defend.")

    def play_turn(self, attacker, defender):
        print(f"\n--- {attacker.name}'s Turn to Attack ---")
        print(f"Trump Suit: {self.deck.trump_suit}")
        print(str(attacker))
        print(str(defender))

        was_beaten = False  # <--- Track result

        while len(self.table) < 6 and attacker.hand:
            if not self.attack(attacker):
                print(f"{attacker.name} cannot continue the attack. Ending round.")
                break

            if not self.table.can_beat(defender.hand, self.deck.trump_suit):
                print(f"{defender.name} cannot defend. {attacker.name} wins the round.")
                defender.hand.extend(self.table.table.keys())
                was_beaten = False
                break

            continue_defend = input(f"{defender.name}, do you want to defend? (yes/no): ").strip().lower()
            if continue_defend != 'yes':
                print(f"{defender.name} declined to defend. Taking all cards.")
                defender.hand.extend(self.table.table.keys())
                was_beaten = False
                break

            self.defend(defender)

        if self.table.beaten():
            print("All cards were successfully defended!")
            was_beaten = True

        print(f"The end of {attacker.name}'s turn.")
        self.deck.discard.extend(self.table.table.keys())
        self.deck.discard.extend([v[1] for v in self.table.table.values() if v[1]])
        self.table.clear()
        self.next_turn(was_beaten)
