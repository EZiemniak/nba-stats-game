# Players Data JSON Schema
## Simplified and commented for readability, see docs/sample_player.json for a full player data sample.
```
{
    "id": 200768, 
    "full_name": "Kyle Lowry",
    "first_name": "Kyle",
    "last_name": "Lowry",
    "is_active": true,
    **General Player Info**
    "info": {
      "height": "6-0",
      "weight": "196",
      "birthdate": "1986-03-25",
      "position": "Guard",
      "jersey_number": "7",
      "school": "Villanova",
      "country": "USA",
      "year_start": 2006,
      "year_end": 2024,
      "seasons_played": 18,
      "draft_year": "2006",
      "draft_round": "1",
      "draft_number": "24",
      "team_name": "76ers",
      "team_abbreviation": "PHI",
      "team_city": "Philadelphia",
      "roster_status": "Active",
      "greatest_75_flag": "N",
      "nba_flag": "Y",
      "dleague_flag": "N",
      "teams_list": [
        "MEM",
        "HOU",
        "TOR",
        "MIA",
        "PHI"
      ]
    },
    **Career stats hold careers averages for the player**
    "career_stats": {
      "games_started": 898,
      "games_played": 1173,
      "minutes_avg": 31.3,
      "fgm_avg": 4.5,
      "fga_avg": 10.6,
      "fg_pct": 0.423,
      "3pm_avg": 1.9,
      "3pa_avg": 5.1,
      "3p_pct": 0.368,
      "ftm_avg": 3.1,
      "fta_avg": 3.8,
      "ft_pct": 0.815,
      "orb_avg": 0.8,
      "drb_avg": 3.5,
      "rpg": 4.2,
      "apg": 6.1,
      "spg": 1.3,
      "bpg": 0.3,
      "tpg": 2.2,
      "ppg": 13.9,
      "pf": 2.7
    },
    **Season by season stats will contain all seasons played for the player**
    "season_by_season_stats": [    
      {
        "PLAYER_ID": 200768,
        "SEASON_ID": "2019-20",
        "LEAGUE_ID": "00",
        "TEAM_ID": 1610612761,
        "TEAM_ABBREVIATION": "TOR",
        "PLAYER_AGE": 34.0,
        "GP": 58,
        "GS": 58,
        "MIN": 36.2,
        "FGM": 5.8,
        "FGA": 13.8,
        "FG_PCT": 0.416,
        "FG3M": 2.8,
        "FG3A": 8.0,
        "FG3_PCT": 0.352,
        "FTM": 5.1,
        "FTA": 5.9,
        "FT_PCT": 0.857,
        "OREB": 0.6,
        "DREB": 4.5,
        "REB": 5.0,
        "AST": 7.5,
        "STL": 1.4,
        "BLK": 0.4,
        "TOV": 3.1,
        "PF": 3.3,
        "PTS": 19.4
      }
      {
        *Other seasons are in the same format as above...*
      }
    ],
    "awards": {
      "resource": "playerawards",
      "parameters": {
        "PlayerID": 200768
      },
      "resultSets": [
        {
          "name": "PlayerAwards",
          "headers": [
            "PERSON_ID",
            "FIRST_NAME",
            "LAST_NAME",
            "TEAM",
            "DESCRIPTION",
            "ALL_NBA_TEAM_NUMBER",
            "SEASON",
            "MONTH",
            "WEEK",
            "CONFERENCE",
            "TYPE",
            "SUBTYPE1",
            "SUBTYPE2",
            "SUBTYPE3"
          ],
          "rowSet": [
            [
              200768,
              "Kyle",
              "Lowry",
              "Toronto Raptors",
              "NBA Champion",
              "",
              "2018-19",
              null,
              null,
              "",
              "Award",
              "Champion",
              "",
              ""
            ]
          ]
        }
      ]
    },
    "last_updated": "2025-06-02T00:11:04.129158"
}
```