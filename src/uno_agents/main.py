"""Module with main entrypoint for the agents."""

import itertools

from uno_agents.classes.cards import CardType
from uno_agents.classes.player import Dealer, GeneralPlayer
from uno_agents.utils.logger import init_logger

logger = init_logger("")


# TODO
#   1. Create a game object and call it in main: probably dealer is the one!
#   2.
#   3. Rethink shuffle_deck() method in Dealer class - must collect all the cards and shuffle - create new draw pile
#   4. Update readme
#   5. Make a player that plays randomly
#   6. Make the first LLM player.
#   7. Create a documentation
#   8. Move all the if statements about active_card.card_type to some method or function to make code simplier.

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
    logger.debug(dealer)

    while not dealer.has_winner:
        # Initialize the round
        dealer.init_round()
        logger.debug("dealer=%s", dealer)
        logger.debug("draw_pile=%s", dealer.draw_pile)
        logger.debug("discard_pile=%s", dealer.discard_pile)
        logger.info("-" * 50)

        # Plot what players have on hands
        for player in players:
            logger.debug("player=%s", player)

        logger.info("First discard card: %s", dealer.top_card())

        # Now we have non-action card at the top of the discard_pile, players can
        # start the game

        # Continue game here with players. Here the round starts.
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
        play_action_card = False

        while not round_ended:
            # Play the game
            # The first player to move is player under round_start_index
            dealer.current_move += 1
            logger.info("%s", "-" * 25)
            logger.info("Round %d, Move %d", dealer.current_round, dealer.current_move)

            # This is the player who must make the move
            player_to_move = players[dealer.current_player_index]
            logger.info("Player %d is moving", player_to_move.player_id)

            active_card = dealer.top_card()
            logger.info("Current active card: %s", active_card)

            # make a move depending on the card at the top of discard pile
            play_action_card = dealer.play_move(player_to_move, play_action_card)
            # if active_card.is_action:
            # if active_card.card_type is CardType.SKIP and action_played:
            #     logger.info("Skipping the move")
            #     action_played = False
            # elif active_card.card_type is CardType.DRAW2 and action_played:
            #     logger.info("Drawing two cards")
            #     # But we must draw cards only if it is the game against current player.
            #     # If there are not enough cards, then pop(0) is going to throw an error.
            #     # Therefore, we must make sure that there are cards in the draw pile.
            #     dealer.draw_card(player=player_to_move, number_of_cards=2)
            #     action_played = False
            # elif active_card.card_type is CardType.WILD4 and action_played:
            #     logger.info("Drawing four cards")
            #     dealer.draw_card(player=player_to_move, number_of_cards=4)
            #     action_played = False
            # else:
            #     logger.info("Playing for the %s", active_card)
            #     # If card type "wild" it must have assigned color. Therefore
            #     # we can place any color on top
            #     # If it reverse, then also must be played by color.
            #     # If it is number card, must play card
            #     card_to_play = player_to_move.play_card(active_card)

            #     if card_to_play is None:
            #         logger.info("Drawing a card")
            #         dealer.draw_card(player=player_to_move, number_of_cards=1)

            #         # Here we make a decision whether to play the card again because
            #         # in some situations a player may take good card and decide not
            #         # to play it immediately, but play later in the game. This scenario
            #         # is going to be possible if the play_card() method is non-deterministic,
            #         # but more LLM-driven.
            #         card_to_play = player_to_move.play_card(active_card)

            #     if card_to_play is None:
            #         # Move to the next player
            #         logger.info(
            #             "Player %d still has no cards to play, moving to the next player",
            #             player_to_move.player_id,
            #         )
            #     else:
            #         dealer.discard_pile.append(card_to_play)
            #         logger.info("Player %d played %s", player_to_move.player_id, card_to_play)

            #         # Here card to play is not None for sure
            #         if card_to_play.card_type is CardType.REV:
            #             dealer.turn_direction *= -1

            #         elif card_to_play.card_type in {CardType.SKIP, CardType.DRAW2, CardType.WILD4}:
            #             action_played = True

            # What player must do:
            #   Player must do one of the following:
            #       Either place one of the cards on hands to a discard pile
            #       Pick a card from the draw deck
            for player in players:
                logger.debug("\t%s", player)

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

            # Check number of cards in the draw pile
            logger.debug("Cards in draw pile: %d", len(dealer.draw_pile))
            logger.debug("Cards in discard pile: %d", len(dealer.discard_pile))
            logger.debug(
                "Cards in the game: %d",
                (
                    len(dealer.draw_pile) +
                    len(dealer.discard_pile) +
                    sum([len(player.cards) for player in players])
                ),
            )

        # Count points here
        logger.info("Counting points")

        round_points = 0
        for player in players:
            round_points += player.hand_points()

        round_winner = players[dealer.current_player_index]
        logger.info("Player %d gets %d points", round_winner.player_id, round_points)
        round_winner.points += round_points

        # Let's exit after 1 round until we make the game body here
        dealer.has_winner = True

        # If no winner, put all the cards back into the deck
        # TODO no need to pass arguments move to method def in Dealer class
        dealer.shuffle_deck(
            draw_pile=dealer.draw_pile,
            discard_pile=dealer.discard_pile,
            player_cards=list(itertools.chain(*[player.cards for player in players])),
        )
        logger.info("Dealer deck has %d cards", len(dealer.draw_pile))


if __name__ == "__main__":
    main(number_of_players=5)
