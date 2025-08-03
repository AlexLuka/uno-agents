"""Module to define player for Uno game."""

import logging
from abc import ABC, abstractmethod
from secrets import choice

from uno_agents.classes.cards import Card, CardColor, CardType, Hand
from uno_agents.collections.names import player_names

logger = logging.getLogger(__name__)


class BasePlayer(ABC):
    """Base abstract class for the Player.

    It must show what methods must be implemented for custom player class.
    """

    name: str
    player_id: int
    cards: Hand[Card]

    # Total number of points a player has during a game.
    _points: int

    def __init__(self, player_id: int, name: str | None = None) -> None:
        """Player initialization method."""
        self.player_id = player_id
        self.cards = Hand()
        self.points = 0

        if name:
            self.name = name
        else:
            self.name = choice(player_names)

    def hand_points(self) -> int:
        """Property to return number of points in a Player's hand."""
        logger.debug("Player %d has %d points on hand", self.player_id, self.cards.points)
        return self.cards.points

    @property
    def points(self) -> int:
        """Property to access number of Player's points."""
        return self._points

    @points.setter
    def points(self, value: int) -> None:
        self._points = value

    @abstractmethod
    def play_card(self, current_card: Card, *args: list, **kwargs: dict) -> Card:
        """Method to select a card from available cards in a hand.

        Args:
            current_card: current card at the top of a discard pile.
            *args: additional arguments. The arguments can be the current state
                of a game, how many cards in discard and draw pile, which cards
                have been played already, etc. This information can be useful for
                agent players, but may be not used by the general player.
            **kwargs: also arguments passed by names to the method. These could be
                similar to those passed with *args.
        """

    def __str__(self) -> str:
        """Human-readable representation of GeneralPlayer object."""
        return (
            f"Player {self.name} [ID={self.player_id}]: "
            f"{', '.join(str(card) for card in self.cards)}"
        )


class GeneralPlayer(BasePlayer):
    """Docstring."""

    def __init__(self, player_id: int) -> None:
        """Docstring."""
        super().__init__(player_id=player_id)

    def play_card(self, current_card: Card) -> Card:
        """Method to select a card to play.

        Args:
            current_card: current card at the top of discard pile.

        Returns:
            Card to play or None if no card to pick. Also must say something of play wild card.
        """
        # List all the cards that are currently playable
        playable_cards = []
        colors_need = {
            CardColor.R: 0,
            CardColor.G: 0,
            CardColor.Y: 0,
            CardColor.B: 0,
            CardColor.A: 0,
        }

        for i, card in enumerate(self.cards):
            if ((card.color is CardColor.A) or
                (card.color is current_card.color) or
                (card.card_type is current_card.card_type)):
                playable_cards.append((card, i))

            colors_need[card.color] += 1
        logger.debug("Player %d has following playable cards: %s", self.player_id, playable_cards)

        if len(playable_cards) == 0:
            # This means that we do not have a playable cards
            return None

        # Select one playable card that cost most points
        selected_card_index = -1
        max_points = -1

        for card, ind in playable_cards:
            if card.value > max_points:
                max_points = card.value
                selected_card_index = ind

        # Selected card index is going to be defined anyway
        card  = self.cards.pop(selected_card_index)

        if card.card_type in {CardType.WILD, CardType.WILD4}:
            # Select a color to call
            color_need, _ = max(colors_need.items(), key=lambda x: x[1])
            if color_need is CardColor.A:
                color_need = choice([CardColor.B, CardColor.Y, CardColor.G, CardColor.R])

            # Here we assigned a color to the wild card. It must be reset when shuffle!
            card.color = color_need

            return card

        return card
