"""Module with classes for cards."""

import logging
from collections import UserList
from enum import Enum, unique

from pydantic import BaseModel, computed_field

logger = logging.getLogger(__name__)


@unique
class CardColor(Enum):
    """Class to keep colors."""

    R = "red"
    G = "green"
    Y = "yellow"
    B = "blue"
    A = "any"


@unique
class CardType(Enum):
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


class Card(BaseModel):
    """Card object to keep track of cards and their values."""

    color: CardColor        # also called suit
    card_type: CardType     # number, skip, draw two, reverse, wild, wild 4.

    @computed_field
    @property
    def value(self) -> int:
        """Property to compute a value of a card."""
        if self.card_type in {CardType.WILD, CardType.WILD4}:
            return 50

        if self.card_type in {CardType.SKIP, CardType.DRAW2, CardType.REV}:
            return 20

        return int(self.card_type.value)

    @computed_field
    @property
    def is_action(self) -> bool:
        """Property to determine if card is an action card."""
        return self.card_type in {
            CardType.WILD, CardType.WILD4, CardType.SKIP, CardType.DRAW2, CardType.REV,
        }

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


class Hand(UserList):
    """Class to store deck of cards as a list."""

    _points: int

    def __init__(self) -> None:
        """Initialize a hand."""
        super().__init__()

        # Set points to 0 on init
        self.points = 0

    @property
    def points(self) -> int:
        """Property to return number of points in a hand."""
        return self._points

    @points.setter
    def points(self, value: int) -> None:
        self._points = value

    def append(self, card: Card) -> None:
        """Method to add a card to a hand."""
        # Increase number of points
        super().append(card)
        self.points += card.value

    def pop(self, index: int = -1) -> Card:
        """Overrides the default pop method to add custom behavior.

        For example, it prints a message before popping an element.
        """
        if not self:
            msg = "pop from empty list"
            raise IndexError(msg)

        # Add your custom logic here before or after the original pop operation
        logger.debug("Popping element at index %d from a Hand.", index)

        # Call the original list's pop method using super()
        card = super().pop(index)

        self.points -= card.value
        return card

    def __str__(self) -> str:
        """Method to get human-readable representation of a deck."""
        return f"[{', '.join(map(str, self))}]"


def init_deck() -> list[Card]:
    """Function to init the deck."""
    deck = Deck()

    for color in CardColor:
        if color is CardColor.A:
            for _ in range(4):
                deck.append(Card(color=color, card_type=CardType.WILD))
                deck.append(Card(color=color, card_type=CardType.WILD4))
        else:
            deck.append(Card(color=color, card_type=CardType.N0))
            for i in range(1, 10):
                deck.append(Card(color=color, card_type=CardType(str(i))))
                deck.append(Card(color=color, card_type=CardType(str(i))))

            for _ in range(2):
                deck.append(Card(color=color, card_type=CardType.SKIP))
                deck.append(Card(color=color, card_type=CardType.REV))
                deck.append(Card(color=color, card_type=CardType.DRAW2))
    return deck
