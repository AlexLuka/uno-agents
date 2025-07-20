"""Module to define player for Uno game."""

import logging
from abc import ABC, abstractmethod
from random import shuffle
from secrets import choice

from uno_agents.classes.cards import Card, Colors, Deck, init_deck

logger = logging.getLogger(__name__)


class BasePlayer(ABC):
    """Base abstract class for the Player.

    It must show what methods must be implemented for custom player class.
    """

    player_id: int
    cards: list[Card]
    points: int

    def __init__(self, player_id: int) -> None:
        """Player initialization method."""
        self.player_id = player_id
        self.cards = []
        self.points = 0

    @abstractmethod
    def play_card(self) -> Card:
        """Method to select a card from available cards in a hand."""


class GeneralPlayer(BasePlayer):
    """Docstring."""

    def __init__(self, player_id: int) -> None:
        """Docstring."""
        super().__init__(player_id=player_id)

    def __str__(self) -> str:
        return f"Player {self.player_id}: {', '.join(str(card) for card in self.cards)}"

    def play_card(self, current_card: "Card") -> "Card":
        """Method to select a card to play.

        Returns:
            Card to play or None if no card to pick. Also must say something of play wild card.
        """
        # List all the cards that are currently playable
        playable_cards = []
        colors_need = {
            Colors.R: 0,
            Colors.G: 0,
            Colors.Y: 0,
            Colors.B: 0,
            Colors.A: 0,
        }

        for i, card in enumerate(self.cards):
            if ((card.color is Colors.A) or
                (card.color is current_card.color) or
                (card.card_type == current_card.card_type)):
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

        if card.card_type in {"wild", "wild_draw_four"}:
            # Select a color to call
            # TODO
            color_need, _ = max(colors_need.items(), key=lambda x: x[1])
            if color_need is Colors.A:
                color_need = choice([Colors.B, Colors.Y, Colors.G, Colors.R])

            # Here we assigned a color to the wild card. It must be reset when shuffle!
            card.color = color_need

            return card

        return card


class Dealer:
    """Dealer is going to a keeper of the game info."""

    round: int
    draw_pile: list
    discard_pile: list
    player_turn: int
    turn_direction: int

    def __init__(self, players: list[GeneralPlayer]) -> None:
        """When we init the dealer we are going to set the game settings before the game starts."""
        self.players = players

        # Keep the number of players
        self.number_of_players = len(players)

        # Determine the order of turns in each game
        shuffle(players)
        self.turn_order = [player.player_id for player in players]          # TODO do I need this???
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

        # This is the actual index of a player who must place a card to discard pile now
        self.current_player_index = -1

        # This is the deck
        self.deck = init_deck()

        # Flag that we have a winner
        self.has_winner = False

        # Round counter
        self.current_round = 0

        # Move counter
        self.current_move = 0

    def init_round(self) -> Deck[Card]:
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
        self.current_player_index = self.round_start_index
        self.current_round += 1
        self.current_move = 1

        # Shuffle the deck
        shuffle(self.deck)

        # Hands is a list of 7-tuples
        for _ in range(7):
            for j in range(self.number_of_players):
                # Get the card from the top
                card = self.deck.pop(0)

                # Give that card to the player
                self.players[j].cards.append(card)

        # TODO Remove this later
        assert self.has_winner is False

        return self.deck

    def shuffle_deck(self, draw_pile: list, discard_pile: list, player_cards: list):
        """
        """
        self.deck = draw_pile + discard_pile + player_cards

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
