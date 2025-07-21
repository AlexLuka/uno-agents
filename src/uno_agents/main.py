"""Module with main entrypoint for the agents."""

import itertools
from random import shuffle

from uno_agents.classes.cards import CardColor, CardType
from uno_agents.classes.player import Dealer, GeneralPlayer
from uno_agents.utils.logger import init_logger

logger = init_logger("")


# TODO
#   1. Create a game object and call it in main
#   2. Move initialization of discard_pile to init_round() method in the Dealer
#      In fact, let's make a dealer a keeper of discard pile and draw pile. And
#      shuffle the cards when necessary using methods defined within Dealer class.

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
        draw_pile = dealer.init_round()
        discard_pile = []

        logger.debug("dealer=%s", dealer)
        logger.debug("draw_pile=%s", draw_pile)
        logger.info("")

        for player in players:
            logger.debug("player=%s", player)

        #
        # Pick card from the top of a draw pile until non-action card appears
        while True:
            card = draw_pile.pop(0)
            discard_pile.append(card)

            if not card.is_action:
                break
        logger.info("First discard card: %s", discard_pile[-1])

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
            dealer.current_move += 1
            logger.info("%s", "-" * 25)
            logger.info("Round %d, Move %d", dealer.current_round, dealer.current_move)

            # This is the player who must make the move
            player_to_move = players[dealer.current_player_index]
            logger.info("Player %d is moving", player_to_move.player_id)

            active_card = discard_pile[-1]
            logger.info("Current active card: %s", active_card)

            # make a move depending on the card at the top of discard pile
            # if active_card.is_action:
            if active_card.card_type is CardType.SKIP and action_played:
                logger.info("Skipping the move")
                action_played = False
            elif active_card.card_type is CardType.DRAW2 and action_played:
                logger.info("Drawing two cards")
                # But we must draw cards only if it is the game against current player.
                # If there are not enough cards, then pop(0) is going to throw an error.
                # Therefore, we must make sure that there are cards in the draw pile.
                for _ in range(2):
                    if len(draw_pile) == 0:
                        logger.info("Draw pile is empty. Shuffling the discard pile.")
                        # Take discard pile, and move all the cards from discard pile to
                        # the draw pile, except the top card.
                        draw_pile, discard_pile = discard_pile[:-1], discard_pile[-1:]
                        shuffle(draw_pile)
                        for card in draw_pile:
                            if card.card_type in {CardType.WILD, CardType.WILD4}:
                                card.color = CardColor.A

                    draw_card = draw_pile.pop(0)
                    player_to_move.cards.append(draw_card)
                action_played = False
            elif active_card.card_type is CardType.WILD4 and action_played:
                logger.info("Drawing four cards")
                for _ in range(4):
                    if len(draw_pile) == 0:
                        logger.info("Draw pile is empty. Shuffling the discard pile.")
                        # Take discard pile, and move all the cards from discard pile to
                        # the draw pile, except the top card.
                        draw_pile, discard_pile = discard_pile[:-1], discard_pile[-1:]
                        shuffle(draw_pile)
                        for card in draw_pile:
                            if card.card_type in {CardType.WILD, CardType.WILD4}:
                                card.color = CardColor.A

                    draw_card = draw_pile.pop(0)
                    player_to_move.cards.append(draw_card)
                action_played = False
            else:
                logger.info("Playing for the %s", active_card)
                # If card type "wild" it must have assigned color. Therefore
                # we can place any color on top
                # If it reverse, then also must be played by color.
                # If it is number card, must play card
                card_to_play = player_to_move.play_card(active_card)

                if card_to_play is None:
                    logger.info("Drawing a card")
                    if len(draw_pile) == 0:
                        logger.info("Draw pile is empty. Shuffling the discard pile.")
                        # Take discard pile, and move all the cards from discard pile to
                        # the draw pile, except the top card.
                        draw_pile, discard_pile = discard_pile[:-1], discard_pile[-1:]
                        shuffle(draw_pile)
                        for card in draw_pile:
                            if card.card_type in {CardType.WILD, CardType.WILD4}:
                                card.color = CardColor.A

                    draw_card = draw_pile.pop(0)
                    player_to_move.cards.append(draw_card)
                    logger.info("Player %d draw %s card", player_to_move.player_id, draw_card)
                    card_to_play = player_to_move.play_card(active_card)

                if card_to_play is None:
                    # Move to the next player
                    logger.info(
                        "Player %d still has no cards to play, moving to the next player",
                        player_to_move.player_id,
                    )
                else:
                    discard_pile.append(card_to_play)
                    logger.info("Player %d played %s", player_to_move.player_id, card_to_play)

                    # Here card to play is not None for sure
                    if card_to_play.card_type is CardType.REV:
                        dealer.turn_direction *= -1

                    elif card_to_play.card_type in {CardType.SKIP, CardType.DRAW2, CardType.WILD4}:
                        action_played = True

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
            logger.debug("Cards in draw pile: %d", len(draw_pile))
            logger.debug("Cards in discard pile: %d", len(discard_pile))
            logger.debug(
                "Cards in the game: %d",
                len(draw_pile) + len(discard_pile) + sum([len(player.cards) for player in players]),
            )

        # Count points here
        logger.info("Counting points")

        points = 0
        for player in players:
            # Technically, we can remove that condition, since the player
            # without cards is going to contribute 0 to the total points.
            # Going to keep it for clarity.
            if len(player.cards) > 0:
                points += sum([card.value for card in player.cards])
        round_winner = players[dealer.current_player_index]
        logger.info("Player %d gets %d points", round_winner.player_id, points)
        round_winner.points += points

        # Let's exit after 1 round until we make the game body here
        dealer.has_winner = True

        # If no winner, put all the cards back into the deck
        dealer.shuffle_deck(
            draw_pile=draw_pile,
            discard_pile=discard_pile,
            player_cards=list(itertools.chain(*[player.cards for player in players])),
        )
        # dealer.deck = draw_pile + discard_pile
        # for player in players:
        #     dealer.deck += player.cards
        #     player.cards = []
        logger.info("Dealer deck has %d cards", len(dealer.deck))


if __name__ == "__main__":
    main(number_of_players=5)
