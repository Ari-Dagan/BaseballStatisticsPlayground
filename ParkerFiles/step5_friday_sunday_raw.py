import requests
import csv
from datetime import date, timedelta

# --- 1. Get all Fridays + Sundays in 2025 ---
start = date(2025, 3, 27)   # MLB season start buffer
end   = date(2025, 9, 30)  # MLB season end buffer

dates = []
d = start
while d <= end:
    if d.weekday() in [4, 6]:  # 4 = Friday, 6 = Sunday
        dates.append(d)
    d += timedelta(days=1)

print(f"Found {len(dates)} Fridays/Sundays in 2025")

# --- 2. Open CSV to save all data ---
with open("files/mlb_fridays_sundays_2025.csv", "w", newline="") as f:
    writer = csv.writer(f)
    # Added "weekday" column
    writer.writerow(["date","weekday","gamePk","team","playerId","playerName","position","stats"])

    # --- 3. Loop through all dates ---
    for game_date in dates:
        # Figure out weekday label
        weekday_label = "Friday" if game_date.weekday() == 4 else "Sunday"

        schedule_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={game_date.isoformat()}&gameTypes=R"
        schedule = requests.get(schedule_url).json()
        games = [g["gamePk"] for d in schedule.get("dates", []) for g in d.get("games", [])]

        print(f"{game_date} ({weekday_label}): {len(games)} games")

        # --- 4. Loop through each game and pull boxscore ---
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
                    stats = pdata.get("stats", {}).get("batting", {})  # batting stats as example

                    writer.writerow([
                        game_date.isoformat(),
                        weekday_label,
                        gamePk,
                        team_name,
                        player_id,
                        player_name,
                        position,
                        stats
                    ])