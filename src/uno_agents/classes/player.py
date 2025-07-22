"""Module to define player for Uno game."""

import logging
from abc import ABC, abstractmethod
from random import shuffle
from secrets import choice

from uno_agents.classes.cards import Card, CardColor, CardType, Deck, Hand, init_deck

logger = logging.getLogger(__name__)


class BasePlayer(ABC):
    """Base abstract class for the Player.

    It must show what methods must be implemented for custom player class.
    """

    player_id: int
    cards: Hand[Card]

    # Total number of points a player has during a game.
    _points: int

    def __init__(self, player_id: int) -> None:
        """Player initialization method."""
        self.player_id = player_id
        self.cards = Hand()
        self.points = 0

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


class GeneralPlayer(BasePlayer):
    """Docstring."""

    def __init__(self, player_id: int) -> None:
        """Docstring."""
        super().__init__(player_id=player_id)

    def __str__(self) -> str:
        """Human-readable representation of GeneralPlayer object."""
        return f"Player {self.player_id}: {', '.join(str(card) for card in self.cards)}"

    def play_card(self, current_card: Card) -> Card:
        """Method to select a card to play.

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


class Dealer:
    """Dealer is going to a keeper of the game info."""

    draw_pile: list[Card]
    discard_pile: list
    player_turn: int
    round: int
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
        self.draw_pile = init_deck()

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
        shuffle(self.draw_pile)

        # Hands is a list of 7-tuples
        for _ in range(7):
            for j in range(self.number_of_players):
                # Get the card from the top
                card = self.draw_pile.pop(0)

                # Give that card to the player
                self.players[j].cards.append(card)

        # Also create a discard pile
        self.discard_pile = []

        # Pick card from the top of a draw pile until the first non-action card appears
        while True:
            card = self.draw_pile.pop(0)
            self.discard_pile.append(card)

            if not card.is_action:
                break
        # This method doesn't return anything because the dealer is a keeper of the piles

    def top_card(self) -> Card:
        """Method that returns top card on top of discard pile."""
        return self.discard_pile[-1]

    def draw_card(self, player: BasePlayer, number_of_cards: int) -> None:
        """Method to draw 1, 2, or 4 cards from a draw pile and add them to player's hand.

        Args:
            player: object that represents a player
            number_of_cards: number of cards to add
        """
        for _ in range(number_of_cards):
            if len(self.draw_pile) == 0:
                logger.info("Draw pile is empty. Shuffling the discard pile.")

                # Take discard pile, and move all the cards from discard pile to
                # the draw pile, except the top card. It must remain in the discard
                # pile.
                self.draw_pile, self.discard_pile = self.discard_pile[:-1], self.discard_pile[-1:]

                # Shuffle the cards in the draw pile
                shuffle(self.draw_pile)

                # Since we have played the wild cards and assigned colors to them, the colors
                # need to be reset to A (Any). So, the next time a player takes a card, the card
                # must have no color, and player will assign it on play.
                for card in self.draw_pile:
                    if card.card_type in {CardType.WILD, CardType.WILD4}:
                        card.color = CardColor.A

            # Draw 1 card
            card = self.draw_pile.pop(0)
            logger.info("Player %d draw %s card", player.player_id, card)

            # Add card to a player's hand
            player.cards.append(card)

    def play_move(self, player: BasePlayer, action_played: bool) -> bool:
        """TODO Review this method!!!"""
        active_card = self.top_card()
        logger.info("Current active card: %s", active_card)

        # make a move depending on the card at the top of discard pile
        # if active_card.is_action:
        if active_card.card_type is CardType.SKIP and action_played:
            logger.info("Skipping the move")
            return False

        if active_card.card_type is CardType.DRAW2 and action_played:
            logger.info("Drawing two cards")
            # But we must draw cards only if it is the game against current player.
            # If there are not enough cards, then pop(0) is going to throw an error.
            # Therefore, we must make sure that there are cards in the draw pile.
            self.draw_card(player=player, number_of_cards=2)
            return False

        if active_card.card_type is CardType.WILD4 and action_played:
            logger.info("Drawing four cards")
            self.draw_card(player=player, number_of_cards=4)
            return False

        logger.info("Playing for the %s", active_card)
        # If card type "wild" it must have assigned color. Therefore
        # we can place any color on top
        # If it reverse, then also must be played by color.
        # If it is number card, must play card
        card_to_play = player.play_card(active_card)

        if card_to_play is None:
            logger.info("Drawing a card")
            self.draw_card(player=player, number_of_cards=1)

            # Here we make a decision whether to play the card again because
            # in some situations a player may take good card and decide not
            # to play it immediately, but play later in the game. This scenario
            # is going to be possible if the play_card() method is non-deterministic,
            # but more LLM-driven.
            card_to_play = player.play_card(active_card)

        if card_to_play is None:
            # Move to the next player
            logger.info(
                "Player %d still has no cards to play, moving to the next player",
                player.player_id,
            )
        else:
            self.discard_pile.append(card_to_play)
            logger.info("Player %d played %s", player.player_id, card_to_play)

            # Here card to play is not None for sure
            if card_to_play.card_type is CardType.REV:
                self.turn_direction *= -1

            elif card_to_play.card_type in {CardType.SKIP, CardType.DRAW2, CardType.WILD4}:
                return True
        return False

    def shuffle_deck(self, draw_pile: list, discard_pile: list, player_cards: list) -> None:
        """Method to reshuffle a deck.

        The reason why it maybe required is to clear the colors of wild cards.
        """
        self.draw_pile = draw_pile + discard_pile + player_cards

        for card in self.draw_pile:
            if card.card_type in {CardType.WILD, CardType.WILD4}:
                card.color = CardColor.A

    def __str__(self) -> str:
        """Returns a game state as a string."""
        player = (
            "Unknown" if self.round_start_index < 0 else
            self.turn_order[self.round_start_index]
        )
        return f"""Game state: round {self.current_round}
        Number of cards: {len(self.draw_pile)}
        Number of players: {self.number_of_players}
        Round start index: {self.round_start_index}
        Players order: {self.turn_order}
        Player to start the round: {player}
        Game direction: {self.turn_direction}
        {", ".join(str(card) for card in self.draw_pile)}
        """
