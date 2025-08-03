"""Module with main entrypoint for the agents."""

from uno_agents.classes.dealer import Dealer
from uno_agents.classes.player import GeneralPlayer
from uno_agents.utils.logger import init_logger

logger = init_logger("")


# Near term plan:
#   1. Add a class to keep all the game statistics and print it in the end of each round.
#   2. Create each player individually based on the inputs
#   4. Update readme
#   5. Make a player that plays randomly
#   6. Make the first LLM player.
#   7. Create a documentation

def main(number_of_players: int) -> None:
    """Main entrypoint for the game.

    We are going to start the game with a dealer. Then we determine the positions of players.
    The first player in the sequence is going to be the first player to start the first round.
    Next round, the second player going to start and so on. Dealer is going to shuffle the cards,
    and give each player 7 cards. After that, the game will begin.

    Args:
        number_of_players (int): total number of players to be in the game.
    """
    # Create a dealer
    dealer = Dealer()

    # Initialize all the players. Each player is going to have a unique integer ID
    # starting from 0.
    for i in range(number_of_players):
        dealer.add_player(GeneralPlayer(i))
    logger.debug(dealer)

    # Play the game
    dealer.play_game()

    # Print the game statistics once the game has finished
    logger.info(dealer.game_stat)


if __name__ == "__main__":
    main(number_of_players=5)
