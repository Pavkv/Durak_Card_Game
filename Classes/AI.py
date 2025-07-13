from Classes.Card import Card


class AI:
    def __init__(self):
        self.seen_cards = set()  # Cards seen by AI
        self.player_hand_estimate = set()  # Estimated hand of the player

    def remember_card(self, card):
        self.seen_cards.add(card)

    def remember_table(self, table):
        for card in table.table:
            self.remember_card(card)
            if table.table[card][1]:
                self.remember_card(table.table[card][1])

    def unseen_cards(self):
        full_deck = [Card(rank, suit) for suit in Card.suits for rank in Card.ranks]
        return [card for card in full_deck if card not in self.seen_cards]

    def known_remaining_cards(self, hand):
        return [card for card in self.unseen_cards() if card not in hand]

    def estimate_player_has_trumps(self, trump_suit):
        return any(card.suit == trump_suit for card in self.unseen_cards())

    def choose_throw_ins(self, ai_hand, table, defender_hand_size, trump_suit):
        throw_ins = []
        table_ranks = table.ranks

        # Candidates must match existing table ranks
        candidates = [card for card in ai_hand if card.rank in table_ranks]
        # Sort by: non-trump first, then lowest rank
        candidates.sort(key=lambda c: (c.suit == trump_suit, Card.rank_values[c.rank]))

        for card in candidates:
            if len(throw_ins) + len(table) >= 6:
                break
            if len(throw_ins) >= defender_hand_size:
                break
            throw_ins.append(card)

        return throw_ins

    def attack(self, hand, table, trump_suit):
        table_ranks = table.ranks
        has_trump_left = self.estimate_player_has_trumps(trump_suit)

        # Sort hand by (is trump, rank value)
        hand_sorted = sorted(hand, key=lambda c: (c.suit == trump_suit, Card.rank_values[c.rank]))

        # First attack
        if len(table) == 0:
            if has_trump_left:
                # Player likely has trumps — bait with low non-trump if possible
                for card in hand_sorted:
                    if card.suit != trump_suit:
                        return card
            # Otherwise, play the lowest available card
            return hand_sorted[0]

        # Follow-up attack: only use cards matching ranks on table
        playable = [card for card in hand_sorted if card.rank in table_ranks]

        if playable:
            # If player still has trumps, use a weak baiting card
            if has_trump_left:
                for card in playable:
                    if card.suit != trump_suit:
                        return card
            # Otherwise, use the best legal card (lowest overall)
            return playable[0]

        return None

    def defense(self, hand, attack_card, trump_suit):
        has_trump_left = self.estimate_player_has_trumps(trump_suit)
        # All cards that can beat the attack
        candidates = [card for card in hand if Card.beats(card, attack_card, trump_suit)]
        if not candidates:
            return None

        # Sort by (is trump, rank)
        candidates_sorted = sorted(candidates, key=lambda c: (c.suit == trump_suit, Card.rank_values[c.rank]))

        if has_trump_left:
            # Avoid using trump if possible
            non_trumps = [c for c in candidates_sorted if c.suit != trump_suit]
            return non_trumps[0] if non_trumps else candidates_sorted[0]
        else:
            # Player likely has no trump, be greedy: use cheapest winning, even if it's a trump
            return candidates_sorted[0]
