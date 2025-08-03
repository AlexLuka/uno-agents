"""Module to keep player's and game statistics."""

from pydantic import BaseModel


class GameStatistics(BaseModel):
    """In this class we are going to store game statistics.

    The game statistics is going to be the following:
    - Number of players
    - Player's names with the order they played in a game
    - Number of rounds to win a game
    - Number of moves in each round
    - Name of a player who win a game. This is not the same as a type of a player.
      Type of a player is determined by a strategy player's use, and therefore by
      a class of a player. However, we may have games where all players were created
      from the same class! This means that we might need to create more individual
      instances and store them in database.
    - Number of points each player got by the end of the game.

    Statistics object is created by a dealer in the end of each game.
    """

    number_of_players: int = 0
    number_of_rounds: int = 0
    number_of_round_moves: list[int] = []

    players_names: list[str] = []
    players_end_of_round_points: list[list[int]] = []

    winner_name: str = None
    winner_points: int = None
    winner_class: str = None

    def __str__(self) -> str:
        """Method to customize the print of game statistics to stdout."""
        # Need to generate a table like
        # | round | ... Players ... |

        longest_player_name = len(max(self.players_names, key=len))

        # Add the header row
        table = (
            f"|{'round':<10}| " +
            " | ".join([f"{pn:<{longest_player_name}}" for pn in self.players_names]) +
            " |\n")

        # Add a separation line between header row and the data
        table += (
            f"\t|{'-'*10}|" +
            f"{'-' * (longest_player_name + 2)}|" * self.number_of_players +
            "\n")

        # Add all the data
        for i, points in enumerate(self.players_end_of_round_points):
            table += (
                f"\t|{i + 1:<10}| " +
                " | ".join([f"{p:<{longest_player_name}}" for p in points]) +
                " |\n")

        return f"""
        number_of_players: {self.number_of_players}
        number_of_rounds: {self.number_of_rounds}
        {table}

        Winner: {self.winner_name}
        Winner points: {self.winner_points}
        Winner class: {self.winner_class}
        """
