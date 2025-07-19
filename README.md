# UNO Agents

The goal is to create a player agent. Then create multiple agents dynamically, with the same
or individual prompts. Pass game rules, and current game state to the agents and make agents
to make a move. There must be a dealer which controls that all the players play fairly.

What to store:
- History of moves: which cards left the game and which player played that game
- Who is making a move
- Current card at the top
- Number of cards remain in the deck.
- Deck must be generated in the beginning of the game.
- Dealer checks validity of a move for each agent
- Dealer is not an agent (for now), but a function