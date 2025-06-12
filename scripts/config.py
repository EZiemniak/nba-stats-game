import os
from datetime import timedelta

ACTIVE_PLAYERS_UPDATE = True  # Set to True to update active players who haven't been updated for 24 hours

TIME_BETWEEN_UPDATES = timedelta(hours=24)  # Time between updates for active players 

# Directories
SCRIPTS_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(SCRIPTS_DIR, '../data')
LOGS_DIR = os.path.join(SCRIPTS_DIR, '../logs')
# Files
ACTIVE_PLAYERS_FILE = os.path.join(DATA_DIR, 'active_players.json')
RETIRED_PLAYERS_FILE = os.path.join(DATA_DIR, 'retired_players.json')

CACHED_IDS_FILE = os.path.join(DATA_DIR, 'updated_ids.json') if ACTIVE_PLAYERS_UPDATE else os.path.join(DATA_DIR, 'cached_player_ids.json')



