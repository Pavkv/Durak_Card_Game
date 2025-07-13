import random

from Classes.Card import Card
from Classes.Player import Player
from Classes.Deck import Deck
from Classes.Table import Table
from Classes.AI import AI


class DurakCardGame:
    def __init__(self, player_name):
        # Initialize the deck, table
        self.deck = Deck()
        self.table = Table()

        # Initialize players
        self.player = Player(player_name)
        self.ai = AI()
        self.opponent = Player("Opponent")
        self.draw_cards()

        # Initialize endgame tracking
        self.last_attacker_played_all = False
        self.last_defender_defended_all = False

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
        self.check_endgame()

        self.play_turn(self.current_turn, self.opponent if self.current_turn == self.player else self.player)

    def can_attack(self, attacker):
        if len(self.table) == 0:
            return True
        return any(card.rank in self.table.ranks for card in attacker.hand)

    def attack(self, attacker):
        if attacker == self.player:
            while True:
                user_input = input("Choose a card to play (e.g., 7C for 7 of Clubs): ").strip().upper()
                rank = user_input[:-1]
                suit = user_input[-1]
                selected_card = Card(rank, suit)

                if not self.table.append(selected_card):
                    print("You can't play that card (rank doesn't match cards on table). Try another.")
                    continue

                attacker.hand.remove(selected_card)
                print(f"{attacker.name} played {selected_card}.")
                return True
        else:
            card = self.ai.attack(attacker.hand, self.table, self.deck.trump_suit)
            if not card:
                return False  # No valid card to attack
            if not self.table.append(card):
                return False  # Defensive fallback
            attacker.hand.remove(card)
            print(f"{attacker.name} attacks with {card}.")
            return True

    def defend(self, defender):
        if defender == self.player:
            while True:
                target_input = input("Which card are you defending against? (e.g., 7C): ").strip().upper()
                defend_input = input("Which card do you want to defend with? (e.g., 8C): ").strip().upper()

                target_rank, target_suit = target_input[:-1], target_input[-1]
                defend_rank, defend_suit = defend_input[:-1], defend_input[-1]
                attack_card = Card(target_rank, target_suit)
                defend_card = Card(defend_rank, defend_suit)

                if not Card.beats(defend_card, attack_card, self.deck.trump_suit):
                    print(f"{defend_card} does not beat {attack_card}. Try a different card.")
                    continue

                defender.hand.remove(defend_card)
                self.table.beat(attack_card, defend_card)
                print(f"{defender.name} defended {attack_card} with {defend_card}.")
                break
        else:
            for attack_card, (beaten, _) in self.table.table.items():
                if not beaten:
                    defend_card = self.ai.defense(defender.hand, attack_card, self.deck.trump_suit)
                    if not defend_card:
                        print(f"{defender.name} cannot defend against {attack_card}.")
                        return
                    defender.hand.remove(defend_card)
                    self.table.beat(attack_card, defend_card)
                    print(f"{defender.name} defended {attack_card} with {defend_card}.")
                    return

    def play_turn(self, attacker, defender):
        print(f"\n--- {attacker.name}'s Turn to Attack ---")
        print(f"Trump Suit: {self.deck.trump_suit}")
        print(str(attacker))
        print(str(defender))

        was_beaten = False

        while len(self.table) < 6 and attacker.hand:
            if self.current_turn == self.player:
                if not self.can_attack(attacker):
                    print(f"{attacker.name} has no valid cards to continue the attack.")
                    break
                if len(self.table) != 0:
                    continue_attack = input(
                        f"{attacker.name}, do you want to continue attacking? (yes/no): ").strip().lower()
                    if continue_attack != 'yes':
                        print(f"{attacker.name} declined to continue attacking. Ending round.")
                        break

            if not self.attack(attacker):
                print(f"{attacker.name} cannot continue the attack. Ending round.")
                break

            print(f"Current Table Ranks: {self.table.ranks}")

            if not self.table.can_beat(defender.hand, self.deck.trump_suit):
                print(f"{defender.name} cannot defend. {attacker.name} wins the round.")

                # Let attacker throw in additional cards (up to 6 total), defender still has cards
                while len(self.table) < 6 and attacker.hand and len(self.table) <= len(defender.hand):
                    valid_throw_ins = [card for card in attacker.hand if card.rank in self.table.ranks]
                    if not valid_throw_ins:
                        break

                    if attacker == self.player:
                        print(f"You may throw in additional cards. Table has {len(self.table)} cards.")
                        user_input = input("Throw in a card or press Enter to stop: ").strip().upper()
                        if not user_input:
                            break
                        rank = user_input[:-1]
                        suit = user_input[-1]
                        card = Card(rank, suit)
                    else:
                        throw_ins = self.ai.choose_throw_ins(attacker.hand, self.table, len(defender.hand),
                                                             self.deck.trump_suit)
                        for card in throw_ins:
                            if self.table.append(card):
                                attacker.hand.remove(card)
                                print(f"{attacker.name} throws in {card}.")

                # Defender collects all table cards
                defender.hand.extend(self.table.table.keys())
                defender.hand.extend([v[1] for v in self.table.table.values() if v[1]])
                was_beaten = False
                break

            if self.current_turn != self.player:
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

        # Track AI memory
        self.ai.remember_table(self.table)
        self.ai.seen_cards.update(self.deck.discard)

        self.last_attacker_played_all = (len(self.table) == len(self.table.table))
        self.last_defender_defended_all = self.table.beaten()

        self.table.clear()
        self.next_turn(was_beaten)

    def check_endgame(self):
        if self.deck.cards:
            return  # Game not finished

        player_cards = len(self.player.hand)
        opponent_cards = len(self.opponent.hand)

        if player_cards == opponent_cards:
            if self.last_attacker_played_all and self.last_defender_defended_all:
                loser = self.opponent.name if self.current_turn == self.opponent else self.player.name
                print(f"Both have {player_cards} cards. {loser} is Durak by rule (defender loses).")
                exit()

        if player_cards < opponent_cards:
            print(f"{self.player.name} wins! {self.opponent.name} is Durak.")
        else:
            print(f"{self.opponent.name} wins! {self.player.name} is Durak.")
        exit()

