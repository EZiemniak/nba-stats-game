from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo, playercareerstats, playerawards
from requests.exceptions import HTTPError, ConnectionError, Timeout
from time import sleep
import datetime, json, logging, os, sys
import pandas as pd
from tqdm import tqdm
from config import ACTIVE_PLAYERS_UPDATE, DATA_DIR, LOGS_DIR, ACTIVE_PLAYERS_FILE, RETIRED_PLAYERS_FILE, TIME_BETWEEN_UPDATES
   
def get_item(val):
    return val.item() if hasattr(val, 'item') else None
    
# Fetch player info, career stats, season-by-season logs, and awards
def get_player_info(player: dict) -> None:

    if player['is_active'] and ACTIVE_PLAYERS_UPDATE:
        last_updated = datetime.datetime.fromisoformat(player['last_updated'])
        if last_updated > datetime.datetime.now() - TIME_BETWEEN_UPDATES:
            print(f"Player {player['full_name']} ({player['id']}) is already up-to-date, skipping.")
            return
    player_info = commonplayerinfo.CommonPlayerInfo(player_id=player['id'])
    career = playercareerstats.PlayerCareerStats(per_mode36="PerGame", player_id=player['id'])
    season_by_season_stats = career.get_data_frames()[0]
    career_averages = career.get_data_frames()[1]
    player_info_df = player_info.get_data_frames()[0]

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
      'teams_list': season_by_season_stats.query('TEAM_ABBREVIATION != "TOT"')['TEAM_ABBREVIATION'].unique().tolist()
    }

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
        
    player['season_by_season_stats'] = season_by_season_stats.to_dict(orient='records')
      
    player['awards'] = playerawards.PlayerAwards(player_id=player['id']).get_dict()
    
    if player['is_active']:
        player['last_updated'] = datetime.datetime.now().isoformat()
    print(f"Cached player: {player['full_name']} ({player['id']})")

    
# --------------MAIN SCRIPT-------------- 
# Loads cached IDs and players from JSON (active only, or all players, dependant on ACTIVE_PLAYERS_UPDATE)
# For players not in cache (or active + not updated, if ACTIVE_PLAYERS_UPDATE is true), fetches their info, career stats, season-by-season logs, and awards (and a timestamp if its an update)
# After reaching API rate limit for this session, stores fetched players and IDs in JSON cache files

if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

    max_requests_per_session = 200 # NBA API: ~600 requests/session → 200 players @ 3 calls per player
    requests_count = 0

    if ACTIVE_PLAYERS_UPDATE:
        cached_ids_file = os.path.join(DATA_DIR, 'updated_ids.json')
    else:
        cached_ids_file = os.path.join(DATA_DIR, 'cached_player_ids.json')

    log_file = os.path.join(LOGS_DIR, 'cache_players.log')
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        with open(ACTIVE_PLAYERS_FILE, 'r', encoding='utf-8') as f:
            active_players = json.load(f)
            if ACTIVE_PLAYERS_UPDATE:
                players_list = active_players
                # Dict to quickly access players by ID for updates
                player_dict = {p['id']: p for p in players_list}
            else:
                players_list = players.get_players()
    except Exception as e:
        print(f'Error: Failed to load active players: {e}\nTry deleting JSON files and run again.')
        sys.exit(1)   
    if len(players_list) < 300:
        print(f'Only {len(players_list)} players found, try setting ACTIVE_PLAYERS_UPDATE to False in config.py to cache all players first.')
        sys.exit(1)
    try:
        if not ACTIVE_PLAYERS_UPDATE:
            with open(RETIRED_PLAYERS_FILE, 'r', encoding='utf-8') as f:
                retired_players = json.load(f)
    except Exception as e:
        print(f'Error: Failed to load retired players: {e}\nTry deleting JSON files and run again.')
        sys.exit(1) 
    try:
        with open(cached_ids_file, "r") as f:
            cached_ids = json.load(f)
    except Exception as e:
        print(f'Error: Failed to load cached IDs: {e}\nTry deleting JSON files and run again.')
        sys.exit(1)

    cache_load = tqdm(players_list, desc="Caching players") if not ACTIVE_PLAYERS_UPDATE else players_list

    for player in cache_load: # Cache segments of players list as testing shows NBA API has a limit of 200 players per run/session, even with large sleep times
        if requests_count >= max_requests_per_session:
            print("Max requests per session reached, ending session.")
            break
        if player['id'] in cached_ids:
            print(f"Player {player['full_name']} ({player['id']}) already cached, skipping.")
            continue

        success = False
        for attempt in range(3): # Up to 3 retries on timeouts
            try:
                requests_count += 1

                if ACTIVE_PLAYERS_UPDATE:
                    print(f"{requests_count} / {max_requests_per_session} players")
    
                get_player_info(player)

                success = True
                break

            except Timeout:
                if attempt < 2:
                    print("Request timed out")
                    sleep(10)
                else:
                    print("Max timeouts reached, ending script.")
                    logging.error(f"{attempt + 1} timeouts for player {player['id']}: {player['full_name']}")
                    sys.exit(1)
            except Exception as e: # Continue on player errors and log the player and error (e.g. G-League players with no NBA games, future rookies with no NBA games yet)
                print(f"Error processing player {player['id']}: {player['full_name']}: {type(e)} : {e}")
                logging.error(f"Error processing player {player['id']}: {player['full_name']}: {type(e)} : {e}")
                success = True  # Marked as logged and handled  
                break
            
        if success:
            cached_ids.append(player['id']) 

            if not player['is_active']:
                retired_players.append(player)
            elif player['is_active'] and ACTIVE_PLAYERS_UPDATE:
                player_dict[player['id']] = player
            else:
                active_players.append(player)
        
        sleep(1)

    try:
        if ACTIVE_PLAYERS_UPDATE:
            active_players = list(player_dict.values())
        # Save updated player lists and cached IDs list to JSON, separating active and retired players
        with open(cached_ids_file, "w") as f_ids:
            json.dump(cached_ids, f_ids)
        with open(ACTIVE_PLAYERS_FILE, "w", encoding='utf-8') as f_active:
            json.dump(active_players, f_active, ensure_ascii=False, indent=2)
        if not ACTIVE_PLAYERS_UPDATE:
            with open(RETIRED_PLAYERS_FILE, "w", encoding='utf-8') as f_retired:
                json.dump(retired_players, f_retired, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f'Error: Failed to save cached IDs or player lists: {e}\nTry deleting JSON files and run again.')
        sys.exit(1)

    sys.exit(0)  # Exit successfully
  
