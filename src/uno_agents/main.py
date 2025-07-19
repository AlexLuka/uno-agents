"""Module with main entrypoint for the agents."""

from enum import Enum, unique
from random import shuffle


class Player:
    """Docstring."""

    player_id: int
    cards: list[str]

    def __init__(self, player_id: int):
        self.player_id = player_id


@unique
class Colors(Enum):
    """Class to keep colors."""

    R = "red"
    G = "green"
    Y = "yellow"
    B = "blue"
    A = "any"


class Card:
    """Card object to keep track of cards and their values."""

    color: Colors   # also called suit
    value: int
    card_type: str   #number, skip, draw two, reverse, wild, wild 4.

    def __init__(self, color: Colors, card_type: str) -> None:
        """Initialize the Card object with its value."""
        self.color = color
        self.card_type = card_type

        # TODO Rethink this part
        if self.color is Colors.A:
            self.value = 50
        else:  # noqa: PLR5501
            if self.card_type in {"skip", "draw_two", "reverse"}:
                self.value = 20
            else:
                self.value = int(self.card_type)

    def __str__(self):
        return f"{self.card_type} {self.color.value}"


def init_deck() -> list[Card]:
    """Function to init the deck."""
    deck = []

    for color in Colors:
        if color is Colors.A:
            for _ in range(4):
                deck.append(Card(color=color, card_type="wild"))
                deck.append(Card(color=color, card_type="wild_draw_four"))
        else:
            deck.append(Card(color=color, card_type="0"))
            for i in range(1, 10):
                deck.append(Card(color=color, card_type=i))
                deck.append(Card(color=color, card_type=i))

            for _ in range(2):
                deck.append(Card(color=color, card_type="skip"))
                deck.append(Card(color=color, card_type="reverse"))
                deck.append(Card(color=color, card_type="draw_two"))
    return deck


class Dealer:
    """Dealer is going to a keeper of the game info."""

    round: int
    draw_pile: list
    discard_pile: list
    player_turn: int
    turn_direction: int

    def __init__(self, number_of_players: int) -> None:
        """When we init the dealer we are going to set the game settings before the game starts."""
        # Keep the number of players
        self.number_of_players = number_of_players

        # Determine the order of turns in each game
        self.turn_order = list(range(number_of_players))
        print(f"turn_order = {self.turn_order}")
        shuffle(self.turn_order)
        print(f"turn_order = {self.turn_order}")

        self.turn_direction = 1 # OR -1

        # Index of a layer that is going to start the round. This is not
        # the same as player_id !!! This is an index within turn_order list!
        # For example, if turn_order = [4, 2, 0, 1, 3] and round_start_index=0
        # then the player with index 4 is going to start the round. Positions of
        # players are not going to change over time, but each round the index is
        # going to shift by 1. We set it to None in the beginning of the game to
        # initialize in the beginning of the round.
        self.round_start_index = -1

        # This is the deck
        self.deck = init_deck()

        # Flag that we have a winner
        self.has_winner = False

        # Round counter
        self.current_round = 0

    def init_round(self) -> None:
        """Method to init the round.

        Before each round begins we need to do the following.
        1. Determine which player is going to start the round
        1. Shuffle the deck
        2. Give each player 7 cards
        4. Since we init the round, then we do not have a winner. Therefore,
           the winner flag must be False

        Return the cards of each player, draw pile, and the first card at the top.
        If the top card is an action card, discard it until you get any non-action
        card. Action cards are cards that do not have numbers. Non-action cards are
        cards with numbers from 0 to 9 and one of green, blue, yellow or red colors.
        """
        self.round_start_index = (
            0 if self.round_start_index == -1 else
            (self.round_start_index + 1) % self.number_of_players
        )
        self.current_round += 1

        # Shuffle the deck
        shuffle(self.deck)

        # Hands is a list of 7-tuples
        hands = [[] for _ in range(self.number_of_players)]
        for _ in range(7):
            for j in range(self.number_of_players):
                # Get the card from the top
                card = self.deck.pop(0)

                # Give that card to the player
                hands[j].append(card)

        assert self.has_winner is False

        return hands, self.deck

    def __str__(self) -> str:
        """Returns a game state as a string."""
        return f"""Game state: round {self.current_round}
        Number of cards: {len(self.deck)}
        Number of players: {self.number_of_players}
        Round start index: {self.round_start_index}
        Players order: {self.turn_order}
        Player to start the round: {"Unknown" if self.round_start_index < 0 else self.turn_order[self.round_start_index]}
        Game direction: {self.turn_direction}
        {", ".join(str(card) for card in self.deck)}
        """


def main(number_of_players: int) -> None:
    """Main entrypoint for the game.

    We are going to start the game with a dealer. Then we determine the positions of players.
    The first player in the sequence is going to be the first player to start the first round.
    Next round, the second player going to start and so on. Dealer is going to shuffle the cards,
    and give each player 7 cards. After that, the game will begin.

    Args:
        number_of_players (int): total number of players to be in the game.
    """
    # Initialize all the players. Each player is going to have a unique integer ID
    # starting from 0.
    players = [Player(i) for i in range(number_of_players)]

    # Create a dealer
    dealer = Dealer(number_of_players=number_of_players)
    print(dealer)

    while not dealer.has_winner:
        hands, draw_pile = dealer.init_round()
        print(dealer)
        print(hands)
        print(draw_pile)

        # Let's exit after 1 round until we make the game body here
        dealer.has_winner = True




if __name__ == "__main__":
    main(number_of_players=3)
