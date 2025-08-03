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
