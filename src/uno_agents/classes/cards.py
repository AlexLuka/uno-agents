"""Module with classes for cards."""

from enum import Enum, unique


@unique
class Colors(Enum):
    """Class to keep colors."""

    R = "red"
    G = "green"
    Y = "yellow"
    B = "blue"
    A = "any"


@unique
class CartTypes(Enum):
    """Type of cards in Uno game."""

    SKIP = "skip"
    DRAW2 = "draw_two"
    REV = "reverse"
    WILD = "wild"
    WILD4 = "wild_draw_four"
    N0 = "0"
    N1 = "1"
    N2 = "2"
    N3 = "3"
    N4 = "4"
    N5 = "5"
    N6 = "6"
    N7 = "7"
    N8 = "8"
    N9 = "9"


class Card:
    """Card object to keep track of cards and their values."""

    color: Colors   # also called suit
    value: int
    card_type: CartTypes   # number, skip, draw two, reverse, wild, wild 4.
    is_action: bool

    def __init__(self, color: Colors, card_type: CartTypes) -> None:
        """Initialize the Card object with its value."""
        self.color = color
        self.card_type = card_type

        # TODO Rethink this part
        if self.color is Colors.A:
            self.value = 50
            self.is_action = True
        else:  # noqa: PLR5501
            if self.card_type in {CartTypes.SKIP, CartTypes.DRAW2, CartTypes.REV}:
                self.value = 20
                self.is_action = True
            else:
                self.value = int(self.card_type.value)
                self.is_action = False

    def __str__(self) -> str:
        """Method to get human-readable representation of a card."""
        return f"{self.card_type.value} {self.color.value}"

    def __repr__(self) -> str:
        """Method to get unambiguous representation."""
        return f"Card(type={self.card_type.value},color={self.color.value},value={self.value})"


class Deck(list):
    """Class to store deck of cards as a list."""

    def __str__(self) -> str:
        """Method to get human-readable representation of a deck."""
        return f"[{', '.join(map(str, self))}]"


def init_deck() -> list[Card]:
    """Function to init the deck."""
    deck = Deck()

    for color in Colors:
        if color is Colors.A:
            for _ in range(4):
                deck.append(Card(color=color, card_type=CartTypes.WILD))
                deck.append(Card(color=color, card_type=CartTypes.WILD4))
        else:
            deck.append(Card(color=color, card_type=CartTypes.N0))
            for i in range(1, 10):
                deck.append(Card(color=color, card_type=CartTypes(str(i))))
                deck.append(Card(color=color, card_type=CartTypes(str(i))))

            for _ in range(2):
                deck.append(Card(color=color, card_type=CartTypes.SKIP))
                deck.append(Card(color=color, card_type=CartTypes.REV))
                deck.append(Card(color=color, card_type=CartTypes.DRAW2))
    return deck
