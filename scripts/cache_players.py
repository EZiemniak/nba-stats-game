from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo, playercareerstats, playerawards
from requests.exceptions import HTTPError, ConnectionError, Timeout
from time import sleep
from datetime import datetime, timezone
import json, logging, os, sys
import pandas as pd
from tqdm import tqdm
from config import ACTIVE_PLAYERS_UPDATE, LOGS_DIR, ACTIVE_PLAYERS_FILE, RETIRED_PLAYERS_FILE, CACHED_IDS_FILE, TIME_BETWEEN_UPDATES
   
""" Recursively convert NaN values to None for a list of dicts"""
def convert_nans_to_none(obj):
    if isinstance(obj, dict):
        return {k: convert_nans_to_none(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_nans_to_none(item) for item in obj]
    elif isinstance(obj, float) and pd.isna(obj):
        return None
    else:
        return obj
    
def get_item(val):
    return val.item() if hasattr(val, 'item') else None
    
# Fetch player info, career stats, season-by-season logs, and awards
def get_player_info(player: dict) -> None:

    if player['is_active'] and ACTIVE_PLAYERS_UPDATE:
        try:
            last_updated = datetime.fromisoformat(player['last_updated'])
        except KeyError as e:
            print(f"Player {player['full_name']} ({player['id']}) has no last_updated field.")
            logging.info(f"Player {player['full_name']} ({player['id']}) has no last_updated field: {e}")
            last_updated = datetime.now(timezone.utc)
        if last_updated > datetime.now(timezone.utc) - TIME_BETWEEN_UPDATES:
            print(f"Player {player['full_name']} ({player['id']}) is already up-to-date, skipping.")
            return
    player_info = commonplayerinfo.CommonPlayerInfo(player_id=player['id'])
    career = playercareerstats.PlayerCareerStats(per_mode36="PerGame", player_id=player['id'])
    
    raw_career_averages_df = career.get_data_frames()[1]
    raw_player_info_df = player_info.get_data_frames()[0]

    season_by_season_stats_df = career.get_data_frames()[0]
    career_averages_df = raw_career_averages_df.where(pd.notnull(raw_career_averages_df), None)
    player_info_df = raw_player_info_df.where(pd.notnull(raw_player_info_df), None)

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
      'teams_list': season_by_season_stats_df.query('TEAM_ABBREVIATION != "TOT"')['TEAM_ABBREVIATION'].unique().tolist()
    }

    player['career_stats'] = {
        'games_started': get_item(career_averages_df['GS'].values[0]),
        'games_played': get_item(career_averages_df['GP'].values[0]),
        'minutes_avg': get_item(career_averages_df['MIN'].values[0]),
        'fgm_avg': get_item(career_averages_df['FGM'].values[0]),
        'fga_avg': get_item(career_averages_df['FGA'].values[0]),
        'fg_pct': get_item(career_averages_df['FG_PCT'].values[0]),
        '3pm_avg': get_item(career_averages_df['FG3M'].values[0]),
        '3pa_avg': get_item(career_averages_df['FG3A'].values[0]),
        '3p_pct': get_item(career_averages_df['FG3_PCT'].values[0]),
        'ftm_avg': get_item(career_averages_df['FTM'].values[0]),
        'fta_avg': get_item(career_averages_df['FTA'].values[0]),
        'ft_pct': get_item(career_averages_df['FT_PCT'].values[0]),
        'orb_avg': get_item(career_averages_df['OREB'].values[0]),
        'drb_avg': get_item(career_averages_df['DREB'].values[0]),
        'rpg': get_item(career_averages_df['REB'].values[0]),
        'apg': get_item(career_averages_df['AST'].values[0]),
        'spg': get_item(career_averages_df['STL'].values[0]),
        'bpg': get_item(career_averages_df['BLK'].values[0]),
        'tpg': get_item(career_averages_df['TOV'].values[0]),
        'ppg': get_item(career_averages_df['PTS'].values[0]),
        'pf': get_item(career_averages_df['PF'].values[0])
    }
        
    player['season_by_season_stats'] = convert_nans_to_none(season_by_season_stats_df.to_dict(orient='records'))
      
    player['awards'] = playerawards.PlayerAwards(player_id=player['id']).get_dict()
    
    if player['is_active']:
        player['last_updated'] = datetime.now(timezone.utc).isoformat()
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
        with open(CACHED_IDS_FILE, "r") as f:
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
            except IndexError as e: # Continue on player stat errors and log the player and error (e.g. G-League players with no NBA games, future rookies with no NBA games yet)
                print(f"Unable to process player (likely has no NBA games played) {player['id']}: {player['full_name']}: {e}")
                logging.info(f"Unable to process player (likely has no NBA games played) {player['id']}: {player['full_name']} : {e}")
                success = True  # Marked as logged and handled  
                break
            except Exception as e:
                print(f"Unexpected error processing player {player['id']}: {player['full_name']}: {e}")
                logging.error(f"Unexpected error processing player {player['id']}: {player['full_name']}: {e}")
                sys.exit(1)
            
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
        with open(CACHED_IDS_FILE, "w") as f_ids:
            json.dump(cached_ids, f_ids)
        with open(ACTIVE_PLAYERS_FILE, "w", encoding='utf-8') as f_active:
            json.dump(active_players, f_active, ensure_ascii=False, allow_nan=False, indent=2)
        if not ACTIVE_PLAYERS_UPDATE:
            with open(RETIRED_PLAYERS_FILE, "w", encoding='utf-8') as f_retired:
                json.dump(retired_players, f_retired, ensure_ascii=False, allow_nan=False, indent=2)
    except Exception as e:
        print(f'Error: Failed to save cached IDs or player lists: {e}\nTry deleting JSON files and run again.')
        sys.exit(1)

    sys.exit(0)  # Exit successfully
  
