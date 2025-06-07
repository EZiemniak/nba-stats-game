Project Overview

This project pulls and caches data from nba_api to allow users to play stats-based games, while showcasing my work with APIs, data handling, and web development.


Backend:




Features:

Virtual Environment:

- A virtual environment keeps this project’s dependencies isolated from any other Python installations on the machine.
- It prevents version conflicts and ensures that anyone cloning the repo can reproduce the exact environment.

NBA API:

- Uses nba_api endpoints (https://github.com/swar/nba_api) to fetch this data on every NBA player in history:
    - General Player Info (Name, Birthday, Height, College, etc.)
    - Career averages
    - Season-by-season logs
    - Awards
- Through testing, a hard rate limit of ~600 requests per session was found.
- Since each player requires 3 endpoint calls, there is a limit of 200 players per run to avoid exceeding the session rate limit.
- Although fetching straight from the API would have likely worked for this project, I wanted to simulate the need to extract and store large amounts of data and host my own API.

Caching:

- Extensive data for ~5000 past and present NBA players is fetched and cached.
- Stores a list of cached players IDs, to avoid making requests for already cached players.
- Script (runner.py) made to run the caching script repeatedly until there are no players left to cache, while avoiding NBA API rate limit of ~600 requests per session.
- There are seperate json files for retired players, active players, and cached IDs. 
- Seperating active and retired player data allows for future integration of automated offseason or daily updated datasets for active players only.
Note: G-League/D-League players who have not played in the NBA will cause exceptions and be excluded from the data (but will show in logs).

JSON Data Structure

- The `active_players.json` and `retired_players.json` files store player data. See the [JSON schema](/docs/players_schema.md) for the full structure or [JSON sample](/docs/sample_player.json) for sample data for a player.



Caching Script Setup Instructions

1. Clone or download the repository 

2. (Optional but recommended) Create and activate a virtual environment 

3. Install dependencies
pip install -r requirements.txt

    Update Active Players:

    1. Set ACTIVE_PLAYERS_UPDATE to true in config.py.
    2. Run runner.py. This will take approximately 15 minutes. After every 200 players, those players are cached to JSON, even if the program terminates. So, you may stop the program and continue caching where you left off by starting runner.py again, and no duplicate players will be cached.
    3. Recently updated players will not be updated again. You may change how recent the update must be by setting TIME_BETWEEN_UPDATES in config.py (e.g. to ensure every player is updated every time the script runs, you may set TIME_BETWEEN_UPDATES to timedelta(seconds=1)).

    Cache New Data:

    1. Set ACTIVE_PLAYERS_UPDATE to false in config.py.
    2. Delete all files from data folder. 
    3. Run runner.py. Caching process takes approximately 2 hours to complete. After every 200 players, those players are cached to JSON, even if the program terminates. So, you may stop the program and continue caching where you left off by starting runner.py again, and no duplicate players will be cached.


Frontend: 


Features: