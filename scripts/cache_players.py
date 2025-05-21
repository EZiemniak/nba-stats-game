from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo, playercareerstats, commonallplayers
from random import randrange
import json
import pandas as pd

# Returns a random player's id
def get_random_player_id():
    rand = randrange(len(players_list) - 1)  
    return players_list[rand]['id']


# Make request to get all players 
# Each player has a unique id, a first name, last name, full name, and currently active status
players_list = players.get_players()


# Request player info and stats and append to each player
for p in players_list[:1]:
    try:
        player_info = commonplayerinfo.CommonPlayerInfo(player_id=p['id'])
        career = playercareerstats.PlayerCareerStats(per_mode36="PerGame", player_id=p['id'])
        season_by_season_stats = career.get_data_frames()[0]
        career_averages = career.get_data_frames()[1]
        player_info_df = player_info.get_data_frames()[0]

        # general player info
        p['info'] = {
          'height': player_info_df['HEIGHT'].values[0],
          'weight': player_info_df['WEIGHT'].values[0],
          'birthdate': str(pd.to_datetime(player_info_df['BIRTHDATE'].values[0]).date()),
          'position': player_info_df['POSITION'].values[0],
          'jersey_number': player_info_df['JERSEY'].values[0],
          'school': player_info_df['SCHOOL'].values[0],
          'country': player_info_df['COUNTRY'].values[0],
          'year_start': player_info_df['FROM_YEAR'].values[0],
          'year_end': player_info_df['TO_YEAR'].values[0],
          'seasons_played': player_info_df['SEASON_EXP'].values[0],
          'draft_year': player_info_df['DRAFT_YEAR'].values[0],
          'draft_round': player_info_df['DRAFT_ROUND'].values[0],  
          'draft_number': player_info_df['DRAFT_NUMBER'].values[0],
          'team_name': player_info_df['TEAM_NAME'].values[0],  
          'team_abbreviation': player_info_df['TEAM_ABBREVIATION'].values[0],
          'team_city': player_info_df['TEAM_CITY'].values[0],
          'roster_status': player_info_df['ROSTERSTATUS'].values[0],
          'greatest_75_flag': player_info_df['GREATEST_75_FLAG'].values[0],
          'nba_flag': player_info_df['NBA_FLAG'].values[0],
          'dleague_flag': player_info_df['DLEAGUE_FLAG'].values[0],
          # all teams played for 
          'teams_list': season_by_season_stats.query('TEAM_ABBREVIATION != "TOT"')['TEAM_ABBREVIATION'].unique().tolist()
        }
        # career stats and averages
        p['career_stats'] = {
            'games_started': career_averages['GS'].values[0].item(),
            'games_played': career_averages['GP'].values[0].item(),
            'minutes_avg': career_averages['MIN'].values[0].item(),
            'fgm_avg': career_averages['FGM'].values[0].item(),
            'fga_avg': career_averages['FGA'].values[0].item(),
            'fg_pct': career_averages['FG_PCT'].values[0].item(),
            '3pm_avg': career_averages['FG3M'].values[0].item(),
            '3pa_avg': career_averages['FG3A'].values[0].item(),
            '3p_pct': career_averages['FG3_PCT'].values[0].item(),
            'ftm_avg': career_averages['FTM'].values[0].item(),
            'fta_avg': career_averages['FTA'].values[0].item(),
            'ft_pct': career_averages['FT_PCT'].values[0].item(),
            'orb_avg': career_averages['OREB'].values[0].item(),
            'drb_avg': career_averages['DREB'].values[0].item(),
            'rpg': career_averages['REB'].values[0].item(),
            'apg': career_averages['AST'].values[0].item(),
            'spg': career_averages['STL'].values[0].item(),
            'bpg': career_averages['BLK'].values[0].item(),
            'tpg': career_averages['TOV'].values[0].item(),
            'ppg': career_averages['PTS'].values[0].item(),
            'pf': career_averages['PF'].values[0].item()
        }
        
        # season by season stats 
        p['season_by_season_stats'] = season_by_season_stats.to_dict(orient='records')
      

        print(p)
        
    except Exception as e:
        print(f"Error processing player {p['id']}: {p['full_name']}: {e}")
    
# Load cached players list
#with open("../data/active_players.json") as f1, open("../data/retired_players.json") as f2:
#    players = json.load(f1) + json.load(f2)



'''
{                          
  "awards": {
    "all_star": 3,                  
    "mvp": 1,                      
    "championships": 2             
  },
  "obscure_score": 1     // calculation of how obscure the player is           
}
'''