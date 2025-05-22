from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo, playercareerstats, commonallplayers, playerawards
from random import randrange
from time import sleep
import json
import pandas as pd

def get_item(val):
    try:
        return val.item()
    except Exception:
        return None
    
# Request player info + stats and append to each player
def get_player_info(player):
    player_info = commonplayerinfo.CommonPlayerInfo(player_id=player['id'])
    sleep(randrange(1, 3))  
    career = playercareerstats.PlayerCareerStats(per_mode36="PerGame", player_id=player['id'])
    sleep(randrange(1, 3))
    season_by_season_stats = career.get_data_frames()[0]
    career_averages = career.get_data_frames()[1]
    player_info_df = player_info.get_data_frames()[0]

    # general player info
    player['info'] = {
      'height': player_info_df['HEIGHT'].values[0],
      'weight': player_info_df['WEIGHT'].values[0],
      'birthdate': str(pd.to_datetime(player_info_df['BIRTHDATE'].values[0]).date()),
      'position': player_info_df['POSITION'].values[0],
      'jersey_number': player_info_df['JERSEY'].values[0],
      'school': player_info_df['SCHOOL'].values[0],
      'country': player_info_df['COUNTRY'].values[0],
      'year_start': get_item(player_info_df['FROM_YEAR'].values[0]),
      'year_end': get_item(player_info_df['TO_YEAR'].values[0]),
      'seasons_played': get_item(player_info_df['SEASON_EXP'].values[0]),
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
    player['career_stats'] = {
        'games_started': get_item(career_averages['GS'].values[0]),
        'games_played': get_item(career_averages['GP'].values[0]),
        'minutes_avg': get_item(career_averages['MIN'].values[0]),
        'fgm_avg': get_item(career_averages['FGM'].values[0]),
        'fga_avg': get_item(career_averages['FGA'].values[0]),
        'fg_pct': get_item(career_averages['FG_PCT'].values[0]),
        '3pm_avg': get_item(career_averages['FG3M'].values[0]),
        '3pa_avg': get_item(career_averages['FG3A'].values[0]),
        '3p_pct': get_item(career_averages['FG3_PCT'].values[0]),
        'ftm_avg': get_item(career_averages['FTM'].values[0]),
        'fta_avg': get_item(career_averages['FTA'].values[0]),
        'ft_pct': get_item(career_averages['FT_PCT'].values[0]),
        'orb_avg': get_item(career_averages['OREB'].values[0]),
        'drb_avg': get_item(career_averages['DREB'].values[0]),
        'rpg': get_item(career_averages['REB'].values[0]),
        'apg': get_item(career_averages['AST'].values[0]),
        'spg': get_item(career_averages['STL'].values[0]),
        'bpg': get_item(career_averages['BLK'].values[0]),
        'tpg': get_item(career_averages['TOV'].values[0]),
        'ppg': get_item(career_averages['PTS'].values[0]),
        'pf': get_item(career_averages['PF'].values[0])
    }
        
    # season by season stats 
    player['season_by_season_stats'] = season_by_season_stats.to_dict(orient='records')
      
    # awards
    player['awards'] = playerawards.PlayerAwards(player_id=player['id']).get_dict()
        
    sleep(randrange(1, 3))
    
    print(player)
    

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
players_list = players.get_players()

active_players = []
retired_players = []

for player in players_list:
    try:
      get_player_info(player)
      if player['is_active']:
          active_players.append(player)
      else:
          retired_players.append(player)
    except Exception as e:
        print(f"Error processing player {player['id']}: {player['full_name']}: {e}")
    finally:
        sleep(1)


# Save player lists to json, seperating active and retired players
with open("../data/active_players.json", "w") as f_active:
    json.dump(active_players, f_active, indent=2)
with open("../data/retired_players.json", "w") as f_retired:
    json.dump(retired_players, f_retired, indent=2)
  
