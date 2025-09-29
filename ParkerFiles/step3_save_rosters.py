import requests
import csv

# 1. Get all teams
teams_url = "https://statsapi.mlb.com/api/v1/teams?sportId=1"
resp = requests.get(teams_url).json()
teams = resp.get("teams", [])

print(f"Found {len(teams)} MLB teams")

# 2. Open a CSV file to save data
with open("files/mlb_rosters_2025.csv", "w", newline="") as f:
    writer = csv.writer(f)
    # Write header row
    writer.writerow(["teamId", "teamName", "playerId", "playerName", "position"])

    # 3. Loop through teams and collect players
    for t in teams:
        team_id = t["id"]
        team_name = t["name"]

        roster_url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster?season=2025"
        roster_resp = requests.get(roster_url).json()

        roster = roster_resp.get("roster", [])
        print(f"{team_name} roster has {len(roster)} players")

        for player in roster:
            player_id = player["person"]["id"]
            player_name = player["person"]["fullName"]
            position = player["position"]["abbreviation"]

            # Write a row to CSV
            writer.writerow([team_id, team_name, player_id, player_name, position])
