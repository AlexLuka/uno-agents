"""Module with main entrypoint for the agents."""

from enum import Enum, unique
from random import shuffle
from pydantic import BaseModel


class Player(BaseModel):
    """Docstring."""

    player_id: int
    cards: list[str]


@unique
class Colors(Enum):
    R = "red"
    G = "green"
    Y = "yellow"
    B = "blue"
    A = "any"


class Card:
    color: Colors   # also called suit
    value: int
    type: str   #number, skip, draw two, reverse, wild, wild 4.

    def __init__(self, color: Colors, type: str):
        self.color = color
        self.type = type

        # TODO Rethink this part
        if self.color is Colors.A:
            self.value = 50
        else:
            if self.type in {"skip", "draw_two", "reverse"}:
                self.value = 20
            else:
                self.value = int(self.type)

    def __str__(self):
        return f"{self.type} {self.color.value}"


def init_deck():
    deck = list()

    for color in Colors:
        if color is Colors.A:
            for _ in range(4):
                deck.append(Card(color=color, type="wild"))
                deck.append(Card(color=color, type="wild_draw_four"))
        else:
            deck.append(Card(color=color, type="0"))
            for i in range(1, 10):
                deck.append(Card(color=color, type=i))
                deck.append(Card(color=color, type=i))

            for _ in range(2):
                deck.append(Card(color=color, type="skip"))
                deck.append(Card(color=color, type="reverse"))
                deck.append(Card(color=color, type="draw_two"))
    return deck


class Dealer:
    """Dealer is going to a keeper of the game info."""

    round: int
    draw_pile: list
    discard_pile: list
    player_turn: int
    turn_direction: int

    def __init__(self, number_of_players: int):
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
        """
        self.round_start_index = (
            0 if self.round_start_index is -1 else
            (self.round_start_index + 1) % self.number_of_players
        )
        self.current_round += 1

        shuffle(self.deck)

        assert self.has_winner is False

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

    # Create a dealer
    dealer = Dealer(number_of_players=number_of_players)
    print(dealer)

    while not dealer.has_winner:
        dealer.init_round()
        print(dealer)

        # Let's exit after 1 round until we make the game body here
        dealer.has_winner = True




if __name__ == "__main__":
    main(number_of_players=3)
