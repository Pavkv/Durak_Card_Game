class Card:
    suits = ['C', 'D', 'H', 'S'] # C for Clubs(Крести/Трефы), D for Diamonds(Бубны), H for Hearts(Черви), S for Spades(Пики)
    ranks = ['6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] # J for Jack(Валет), Q for Queen(Дама), K for King(Король), A for Ace(Туз)
    rank_values = {rank: i for i, rank in enumerate(ranks)}

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.rank}{self.suit}"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return isinstance(other, Card) and self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        return hash((self.rank, self.suit))

    @classmethod
    def compare_ranks(cls, rank1, rank2):
        return cls.rank_values[rank1] > cls.rank_values[rank2]

    @classmethod
    def beats(cls, defender, attacker, trump):
        if defender.suit == attacker.suit:
            return cls.rank_values[defender.rank] > cls.rank_values[attacker.rank]
        elif defender.suit == trump and attacker.suit != trump:
            return True
        else:
            return False