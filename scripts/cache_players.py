from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo, playercareerstats
from random import randint
import json
# Get all players
all_players = players.get_players()

# Add all players ids to a list
players = []
for player in all_players:
    players.append(player['id'])

# Returns a random player id
def get_random_player_id():
    rand = randint(0, len(players))  
    return players[rand]

rand_id = get_random_player_id()

rand_player_info = commonplayerinfo.CommonPlayerInfo(player_id=rand_id) # Get general player info
#rand_player_seasons = playercareerstats.PlayerCareerStats(player_id=rand_id) # Get player season by season stats

seasons = rand_player_info.available_seasons.get_json()  # Print the player's ID

print(json.loads(seasons))  # Print the number of seasons played
# Expected output:
'''
{
  "name": "Player Name",
  "id": "unique_player_id",           // for referencing or fetching
  "year_start": 2001,
  "year_end": 2015,
  "seasons_played": 14,
  "is_active": false,                 // true if year_end != 0
  "teams": ["BOS", "MIA", "LAL"],     // or abbreviations used in app
  "num_teams": 3,
  "position": "SG",                   // or whatever format API gives
  "career_ppg": 12.5,                 // float, rounded 
  "career_rpg": 5.3,                  // optional
  "career_apg": 4.1,                  // optional
  "awards": {
    "all_star": 3,                    // number of All-Star appearances
    "mvp": 1,                         // optional
    "championships": 2               // number of rings
  },
  "obscure_score": 7                 // optional: custom calc for shortcut for filtering
}
'''