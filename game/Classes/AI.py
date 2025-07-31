from Classes.Card import Card

class AI:
    def __init__(self):
        self.seen_cards = set()
        self.player_hand_estimate = set()

        # Cache the full deck once to avoid repeated creation
        self._full_deck = [Card(rank, suit) for suit in Card.suits for rank in Card.ranks]
        self._unseen_cache = None
        self._cache_dirty = True

    def _update_unseen_cache(self):
        if self._cache_dirty:
            self._unseen_cache = [card for card in self._full_deck if card not in self.seen_cards]
            self._cache_dirty = False

    def remember_card(self, card):
        if card not in self.seen_cards:
            self.seen_cards.add(card)
            self._cache_dirty = True

    def remember_table(self, table):
        for card, (beaten, defender_card) in table.table.items():
            self.remember_card(card)
            if defender_card:
                self.remember_card(defender_card)

    def unseen_cards(self):
        self._update_unseen_cache()
        return self._unseen_cache

    def known_remaining_cards(self, hand):
        self._update_unseen_cache()
        return [card for card in self._unseen_cache if card not in hand]

    def estimate_player_has_trumps(self, trump_suit):
        self._update_unseen_cache()
        return any(card.suit == trump_suit for card in self._unseen_cache)

    def choose_throw_ins(self, ai_hand, table, defender_hand_size, trump_suit):
        table_ranks = table.ranks
        candidates = [card for card in ai_hand if card.rank in table_ranks]

        # Efficient sort: non-trumps first, lowest rank
        candidates.sort(key=lambda c: (c.suit == trump_suit, Card.rank_values[c.rank]))

        throw_ins = []
        for card in candidates:
            if len(throw_ins) + len(table) >= 6:
                break
            if len(throw_ins) >= defender_hand_size:
                break
            throw_ins.append(card)

        return throw_ins

    def choose_attack_cards(self, hand, table, trump_suit, defender_hand_size):
        has_trump_left = self.estimate_player_has_trumps(trump_suit)
        table_ranks = table.ranks
        table_size = len(table)

        # Sort all hand cards (non-trumps first, lowest rank)
        hand_sorted = sorted(hand, key=lambda c: (c.suit == trump_suit, Card.rank_values[c.rank]))

        attack_cards = []

        if table_size == 0:
            # First attack: play the lowest card
            first = None
            for card in hand_sorted:
                if has_trump_left and card.suit != trump_suit:
                    first = card
                    break
            if not first:
                first = hand_sorted[0]
            attack_cards.append(first)

            # Look for other cards with the same rank
            same_rank_cards = [c for c in hand_sorted if c != first and c.rank == first.rank]
            for card in same_rank_cards:
                if len(attack_cards) < defender_hand_size:
                    attack_cards.append(card)

        else:
            # Follow-up: only cards that match ranks on the table
            follow_ups = [c for c in hand_sorted if c.rank in table_ranks]
            for card in follow_ups:
                if len(attack_cards) < defender_hand_size:
                    attack_cards.append(card)

        return attack_cards

    def defense(self, hand, attack_card, trump_suit):
        has_trump_left = self.estimate_player_has_trumps(trump_suit)

        candidates = [card for card in hand if Card.beats(card, attack_card, trump_suit)]
        if not candidates:
            return None

        candidates.sort(key=lambda c: (c.suit == trump_suit, Card.rank_values[c.rank]))

        if has_trump_left:
            for card in candidates:
                if card.suit != trump_suit:
                    return card
        return candidates[0]
