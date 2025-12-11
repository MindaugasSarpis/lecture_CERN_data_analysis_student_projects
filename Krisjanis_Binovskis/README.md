# NBA Data Career Roguelite

This project is a small data-driven NBA "career roguelite" game built in Python.  
It uses real NBA player statistics (fetched using `nba_api`) and turns them into simplified attributes that influence gameplay events.

## Project structure

- analysis/
  - fetch_and_process_players.py — downloads & processes NBA data
- data/
  - events.json — career event cards for the game
  - players_raw.csv — created automatically
  - players_processed.csv — created automatically
- game/
  - config.py — game settings
  - main.py — main pygame game loop
- requirements.txt — required Python packages

## Installation

You need Python 3.10+ installed.

Install dependencies:

```bash
pip install -r requirements.txt
```

## Fetch NBA data

Before running the game, fetch and process real player stats:

```bash
python -m analysis.fetch_and_process_players
```

This will create:

- data/players_raw.csv  
- data/players_processed.csv

## Run the game

```bash
python -m game.main
```

## Adding your own art

In `game/main.py`, replace the player circle with your own sprite:

```python
player_sprite = pygame.image.load("my_player.png").convert_alpha()
w, h = player_sprite.get_size()
screen.blit(player_sprite, (int(player_x) - w // 2, int(player_y) - h // 2))
```

Place your .png image inside the `game/` folder.
