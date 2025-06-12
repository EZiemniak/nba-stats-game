import json, os, subprocess, sys
from nba_api.stats.static import players
from config import ACTIVE_PLAYERS_UPDATE, SCRIPTS_DIR, LOGS_DIR, ACTIVE_PLAYERS_FILE, RETIRED_PLAYERS_FILE, CACHED_IDS_FILE

def load_cached_ids() -> list:
    try:
        with open(CACHED_IDS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f'Error: Failed to load cached IDs: {e}\nTry deleting cached_player_ids.json and running again.')
        sys.exit(1)

# Create log directory and JSON files for cached ids, active and retired players, if they don't exist
def ensure_directories() -> None:
    os.makedirs(LOGS_DIR, exist_ok=True)

    # Initialize files with empty lists if they don't exist yet
    for file in [CACHED_IDS_FILE, ACTIVE_PLAYERS_FILE, RETIRED_PLAYERS_FILE]:
        if not os.path.exists(file):
            try:
                with open(file, 'w') as f_init:
                    json.dump([], f_init)
            except Exception as e:
                print(f"Error while ensuring log directory and JSON files: {e}")
                sys.exit(1)


# --------------MAIN SCRIPT-------------- 
# Run cache_players.py as a subprocess (to avoid per session rate limits) until all players are cached (update active players cache or create new caches) 
if __name__ == "__main__":
    ensure_directories()

    max_runs = 30 # Should be enough runs to cache all players (30 runs * 200 players per run = 6000 players. ~5000 NBA players in history)
    runs = 0

    script_path = os.path.join(SCRIPTS_DIR, 'cache_players.py')
    if not os.path.exists(script_path):
        print(f"Error: {script_path} does not exist.")
        sys.exit(1)
    
    previous_remaining_ids = 0

    while runs < max_runs:
        runs += 1
        print(f'Attempt {runs} of {max_runs} to cache players segments...')
        
        cached_ids = load_cached_ids()
        players_list = players.get_active_players() if ACTIVE_PLAYERS_UPDATE else players.get_players()
        remaining_ids = len(players_list) - len(cached_ids)
        print(f'{len(cached_ids)} / {len(players_list)} players cached. {remaining_ids} remaining.')
        if remaining_ids == previous_remaining_ids:
            print(f'{remaining_ids} players remaining, but no new players to cache. Exiting after {runs} runs.')
            print(f"No new players to cache. Exiting after {runs} runs.")
            break
        if not remaining_ids:
            print("All player IDs are cached.")
            break
        
        previous_remaining_ids = remaining_ids
        # Run the caching script in a subprocess, so each process gets its own rate limit, on current python interpreter
        try:
            result = subprocess.run([sys.executable, script_path], check=True) # check=True raises exception if process fails
        except subprocess.CalledProcessError as e:
            print(f"Error running caching script: {e}")
            break
    
    # Reset updated IDs so next run can update again (future improvement: github actions scheduling)
    if ACTIVE_PLAYERS_UPDATE:
        try:
            with open(CACHED_IDS_FILE, 'w') as f_reset:
                json.dump([], f_reset)
        except Exception as e:
            print(f'Error: Failed to reset updated IDs: {e}\nTry deleting updated_ids.json and running again.')
            sys.exit(1)

    print("All runs completed. Exiting.")


