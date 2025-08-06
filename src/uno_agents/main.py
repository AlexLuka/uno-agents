"""Module with main entrypoint for the agents."""

import secrets

import click

from uno_agents.classes.dealer import Dealer
from uno_agents.classes.player import GeneralPlayer, RandomPlayer
from uno_agents.collections.names import player_names
from uno_agents.utils.logger import init_logger

logger = init_logger("")


# Near term plan:
#   2. Create each player individually based on the inputs
#   4. Update readme
#   6. Make the first LLM player.
#   7. Create a documentation

@click.command()
# @click.argument("number_of_players", type=int)
# def main(number_of_players: int) -> None:
def main() -> None:
    """Main entrypoint for the game.

    We are going to start the game with a dealer. Then we determine the positions of players.
    The first player in the sequence is going to be the first player to start the first round.
    Next round, the second player going to start and so on. Dealer is going to shuffle the cards,
    and give each player 7 cards. After that, the game will begin.

    Args:
        number_of_players (int): total number of players to be in the game.
    """
    click.echo("Welcome to the game of UNO!")

    # Enter all the inputs
    number_of_players = click.prompt(
        "How many players would you like to create?",
        default=5,
        type=click.IntRange(2, 10),
    )
    click.echo(f"Game is going to have {number_of_players} players")

    enter_players_manually = click.prompt(
        "Would you like to define players manually?",
        default=False,
        type=bool,
    )
    click.echo(f"You are going to define players manually: {enter_players_manually}")

    # List of players
    players = []

    if enter_players_manually:
        # This is going to be the role of ID
        player_id = 0
        while player_id < number_of_players:
            click.echo("=" * 50)
            click.echo(f"\tCollecting information about player {player_id}")
            player_name = click.prompt(
                "Enter player's name",
                default=secrets.choice(player_names),
                type=str,
            )
            player_type = click.prompt(
                "Enter player's type",
                show_choices=True,
                type=click.Choice(
                    ["GeneralPlayer", "RandomPlayer", "AgentPlayer"],
                    case_sensitive=True,
                ),
            )

            match player_type:
                case "GeneralPlayer":
                    click.echo("Creating general player")
                    players.append(GeneralPlayer(player_id=player_id, name=player_name))

                case "RandomPlayer":
                    click.echo("Creating random player")
                    players.append(RandomPlayer(player_id=player_id, name=player_name))

                case "AgentPlayer":
                    click.echo("Creating an agent player")
                    raise NotImplementedError("AgentPlayer class has not been implemented yet")

                case _:
                    click.echo("Unknown player type: {player_type}. Try again.")
                    continue
    else:
        # This is going to be the default setting. We basically going to have general players,
        # plus one random one.
        for i in range(number_of_players-1):
            players.append(GeneralPlayer(i))
        players.append(RandomPlayer(player_id=i+1, name="Mr Random"))

    # Create a dealer
    dealer = Dealer()

    # Add players to the dealer
    for player in players:
        dealer.add_player(player)
    logger.debug(dealer)

    # Play the game
    dealer.play_game()

    # Print the game statistics once the game has finished
    logger.info(dealer.game_stat)


if __name__ == "__main__":
    main(number_of_players=5)
