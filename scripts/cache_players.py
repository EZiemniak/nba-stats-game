from nba_api.stats.static import players

# Find all players
all_players = players.get_players()
print(f"Total players: {len(all_players)}")