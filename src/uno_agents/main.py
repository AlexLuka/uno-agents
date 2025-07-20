"""Module with main entrypoint for the agents."""

from abc import ABC, abstractmethod
from enum import Enum, unique
from random import choice, shuffle


class BasePlayer(ABC):
    """Base abstract class for the Player.

    It must show what methods must be implemented for custom player class.
    """

    @abstractmethod
    def play_card(self) -> "Card":
        """Method to select a card from available cards in a hand."""


class GeneralPlayer(BasePlayer):
    """Docstring."""

    player_id: int
    cards: list["Card"]

    def __init__(self, player_id: int) -> None:
        """Docstring."""
        self.player_id = player_id
        self.cards = []

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
            if (card.color is Colors.A) or (card.color is current_card.color) or (card.card_type == current_card.card_type):
                playable_cards.append((card, i))

            colors_need[card.color] += 1
        print(f"Player {self.player_id} has following playable cards: {playable_cards}")

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
    is_action: bool

    def __init__(self, color: Colors, card_type: str) -> None:
        """Initialize the Card object with its value."""
        self.color = color
        self.card_type = card_type

        # TODO Rethink this part
        if self.color is Colors.A:
            self.value = 50
            self.is_action = True
        else:  # noqa: PLR5501
            if self.card_type in {"skip", "draw_two", "reverse"}:
                self.value = 20
                self.is_action = True
            else:
                self.value = int(self.card_type)
                self.is_action = False

    def __str__(self) -> str:
        """Method to get human-readable representation of a card."""
        return f"{self.card_type} {self.color.value}"

    def __repr__(self) -> str:
        """Method to get unambiguous representation."""
        return f"Card(type={self.card_type},color={self.color.value},value={self.value})"


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

        # Shuffle the deck
        shuffle(self.deck)

        # Hands is a list of 7-tuples
        # hands = [[] for _ in range(self.number_of_players)]
        for _ in range(7):
            for j in range(self.number_of_players):
                # Get the card from the top
                card = self.deck.pop(0)

                # Give that card to the player
                # hands[j].append(card)
                self.players[j].cards.append(card)

        assert self.has_winner is False

        return self.deck

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
    players = [GeneralPlayer(i) for i in range(number_of_players)]

    # Create a dealer
    dealer = Dealer(players=players)
    print(dealer)

    while not dealer.has_winner:
        # Initialize the round
        draw_pile = dealer.init_round()
        discard_pile = []

        print(dealer)
        # print(hands)
        print(f"draw_pile={draw_pile}")
        print()

        for player in players:
            print(player)

        #
        # Pick card from the top of a draw pile until non-action card appears
        while True:
            card = draw_pile.pop(0)
            discard_pile.append(card)

            if not card.is_action:
                break
        print(f"First discard card: {discard_pile[-1]}")

        # Now we have non-action card at the top of the discard_pile, players can
        # start the game

        # TODO continue game here with players. Here the round starts.
        # We are going to play the game while all the players have cards.
        round_ended = False

        # This flag determines whether the action card has been played or not. To be
        # more precise, whether current player must take cards, or skip move because
        # previous player placed that action card to the discard pile. We need this in
        # order to avoid players to stuck in infinite loop if an action card is played.
        # For example, if we have 3 players (0, 1, 2) and player 0 plays "draw 2" card
        # then player 1 must take 2 cards, but player 2 must not! Player 2 must play
        # based on color or type now. Therefore, action is over for the card on the top
        # of the discard pile.
        action_played = False

        while not round_ended:
            # Play the game
            # The first player to move is player under round_start_index
            print()

            # This is the player who must make the move
            player_to_move = players[dealer.current_player_index]
            print(f"Player {player_to_move.player_id} is moving")

            active_card = discard_pile[-1]
            print(f"Current active card: {active_card}")

            # make a move depending on the card at the top of discard pile
            # if active_card.is_action:
            if active_card.card_type == "skip" and action_played:
                print("Skipping the move")
                action_played = False
            elif active_card.card_type == "draw_two" and action_played:
                print("Drawing two cards")
                # But we must draw cards only if it is the game against current player.
                for _ in range(2):
                    draw_card = draw_pile.pop(0)
                    player_to_move.cards.append(draw_card)
                action_played = False
            elif active_card.card_type == "wild_draw_four" and action_played:
                print("Drawing four cards")
                for _ in range(4):
                    draw_card = draw_pile.pop(0)
                    player_to_move.cards.append(draw_card)
                action_played = False
            else:
                print(f"Playing for the {active_card}")
                # If card type "wild" it must have assigned color. Therefore
                # we can place any color on top
                # If it reverse, then also must be played by color.
                # If it is number card, must play card
                card_to_play = player_to_move.play_card(active_card)

                if card_to_play is None:
                    print("Drawing a card")
                    draw_card = draw_pile.pop(0)
                    player_to_move.cards.append(draw_card)
                    print(f"Player {player_to_move.player_id} draw {draw_card} card")
                    card_to_play = player_to_move.play_card(active_card)

                if card_to_play is None:
                    # Move to the next player
                    print(f"Player {player_to_move.player_id} still has no cards to play, moving to the next player")
                else:
                    discard_pile.append(card_to_play)
                    print(f"Player {player_to_move.player_id} played {card_to_play}")

                    # Here card to play is not None for sure
                    if card_to_play.card_type == "reverse":
                        dealer.turn_direction *= -1

                    elif card_to_play.card_type in {"skip", "draw_two", "wild_draw_four"}:
                        action_played = True

            # What player must do:
            #   Player must do one of the following:
            #       Either place one of the cards on hands to a discard pile
            #       Pick a card from the draw deck
            for player in players:
                print(f"\t{player}")

            # Check the number of cards on players hands
            if len(player_to_move.cards) == 0:
                round_ended = True  # TODO probably redundant, remove later if yes
                break

            # Move to the next player
            # If we have 5 players this is going to work like following:
            #   Normal turn (turn_direction = 1):
            #       current_player_index = 0 -> (0 + 1) % 5 = 1
            #       current_player_index = 2 -> (2 + 1) % 5 = 3
            #       current_player_index = 4 -> (4 + 1) % 5 = 0
            #   Reversed turn (turn_direction = -1):
            #       current_player_index = 0 -> (0 - 1) % 5 = 4
            #       current_player_index = 1 -> (1 - 1) % 5 = 0
            #       current_player_index = 4 -> (4 - 1) % 5 = 3
            dealer.current_player_index = (
                (dealer.current_player_index + dealer.turn_direction) % dealer.number_of_players
            )

        # Count points here
        print("counting points")

        # Let's exit after 1 round until we make the game body here
        dealer.has_winner = True




if __name__ == "__main__":
    main(number_of_players=3)
