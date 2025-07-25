# UNO Agents

This project implements UNO Game with 108 cards played. The goal is to create players using
deterministic logic and LLM agents using different models and see how they compete with each
other. In this project I want to implement various things like UNO algorithm, LLM agents,
documentation, maybe UI to display game statistics, add database that adds all the stats and
maybe add workflow with docs. So, this is my pet project to have some fun.

## Action items

+ [x] Implement main game logic
+ [ ] Create few different players with different deterministic card selection strategies.
+ [ ] Create an LLM agent, start with Gemini
+ [ ] Extend LLM agents to OpenAI models family, Grok from xAI, and Anthropic models.
+ [ ] Think how to collect statistics about the game. Do we need SQL + cache? This is done when
      the list is updated with new action items. Add all the new action items to the bottom.
+ [ ] Maybe add a class that stores all the game stat? Yes.
+ [ ] Parametrize game inputs with arguments
+ [ ] Generate documentation workflow
+ [ ] Add unit tests for functions, classes that are more or less stable
+ [ ] Work on UI to display game statistics and game dynamics.
