import json, time, os, subprocess, sys
from nba_api.stats.static import players

# Directories
scripts_dir = os.path.dirname(__file__)
data_dir = os.path.join(scripts_dir, '../data')
logs_dir = os.path.join(scripts_dir, '../logs')

cached_ids_file = os.path.join(data_dir, 'cached_player_ids.json')

def load_cached_ids():
    try:
        with open(cached_ids_file, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f'Error: Failed to load cached IDs: {e}\nTry deleting cached_player_ids.json and running again.')
        sys.exit(1)

# Ensure data and logs directories exist
def ensure_directories():
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

    active_players_file = os.path.join(data_dir, 'active_players.json')
    retired_players_file = os.path.join(data_dir, 'retired_players.json')

    # Initialize files with empty lists if they don't exist yet
    for file in [cached_ids_file, active_players_file, retired_players_file]:
        if not os.path.exists(file):
            with open(file, 'w') as f_init:
                json.dump([], f_init)

# --------------MAIN SCRIPT-------------- 
if __name__ == "__main__":
    ensure_directories()

    max_attempts = 30 # Should be enough sessions ran to cache all players
    attempt = 0

    script_path = os.path.join(scripts_dir, 'cache_players.py')
    if not os.path.exists(script_path):
        print(f"Error: {script_path} does not exist.")
        sys.exit(1)

    while attempt < max_attempts:
        attempt += 1
        print(f'Attempt {attempt} of {max_attempts} to cache players segments...')
        cached_ids = set(load_cached_ids())
        full_id_list = set(p['id'] for p in players.get_players())
        remaining_ids = full_id_list - cached_ids
        print(f'{len(cached_ids)} / {len(full_id_list)} players cached. {len(remaining_ids)} remaining.')
    
        if not remaining_ids:
            print("All player IDs are cached.")
            break
           
        result = subprocess.run([sys.executable, script_path], check=True)
        
    print("All runs completed. Exiting.")


