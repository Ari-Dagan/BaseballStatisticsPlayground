import requests
import csv

# Pick the date you want
DATE = "2025-06-01"

# 1. Get all games for the date
schedule_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={DATE}"
schedule = requests.get(schedule_url).json()
games = [g["gamePk"] for d in schedule.get("dates", []) for g in d.get("games", [])]

print(f"Found {len(games)} games on {DATE}")

# 2. Open CSV to save player stats
with open(f"files/mlb_boxscores_{DATE}.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["gamePk", "team", "playerId", "playerName", "position", "stats"])

    # 3. Loop through games
    for gamePk in games:
        box_url = f"https://statsapi.mlb.com/api/v1/game/{gamePk}/boxscore"
        boxscore = requests.get(box_url).json()

        teams = boxscore.get("teams", {})
        for side in ["home", "away"]:
            team = teams.get(side, {})
            team_name = team.get("team", {}).get("name", "")

            players = team.get("players", {})
            for player_id, pdata in players.items():
                player_name = pdata["person"]["fullName"]
                position = pdata.get("position", {}).get("abbreviation", "")
                stats = pdata.get("stats", {}).get("batting", {})  # batting as example

                writer.writerow([gamePk, team_name, player_id, player_name, position, stats])
