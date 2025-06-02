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

Caching:

- Extensive data for ~5000 past and present NBA players is fetched and cached.
- Stores a list of cached players IDs, to avoid making requests for already cached players.
- Script (runner.py) made to run the caching script repeatedly until there are no players left to cache, while avoiding NBA API rate limit of ~600 requests per session.
- There are seperate json files for retired players, active players, and cached IDs. 
- Seperating active and retired player data allows for future integration of automated offseason or daily updated datasets for active players only.
Note: G-League/D-League players who have not played in the NBA will cause exceptions and be excluded from the data (but will show in logs).

JSON Data Structure

- The `active_players.json` and `retired_players.json` files store player data. See the [JSON schema](/docs/players_schema.md) for the full structure or [JSON sample](/docs/player_sample.json) for sample data for a player.



Caching Script Setup Instructions

1. Clone or download the repository 

2. (Optional but recommended) Create and activate a virtual environment 

3. Install dependencies
pip install -r requirements.txt

4. Delete all files from data folder. 

5. Choose setup A (200 player data sample) or setup B (~all players in NBA history)


5A: For a quick sample of the data, run runner.py and terminate once caching begins, allowing for creation of necessary JSON files, as well as logs directory with a log (showing any players excluded from caching). 

5B: (Warning: This script takes multiple hours to complete) For data on ~5000 past and present NBA players: Run runner.py. In the data folder, JSON files will be created, then updated upon completion of the program. Logs directory will be created with logs updated during the run (showing any players excluded from the data). If a crash or program termination occurs (e.g loss of connection to API), the data extracted so far is saved. To continue, rerun the program, this will skip any already cached players to avoid duplicated players or data. 

6A: Run cache_players.py until script completes for a 200 player data sample cached into the data folder. Logs directory will be created with logs updated during the run (showing any players excluded from the data).

6B: Let the program run for as long as desired. Every segment of players (200 players) cached will update the JSON files with their data. The program can be continued if it is stopped, and it will pick up where it left off on caching player segments.


Frontend: 


Features: