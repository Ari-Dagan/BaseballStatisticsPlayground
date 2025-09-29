import csv
import ast
from collections import defaultdict

# Input + Output files
RAW_FILE = "files/mlb_fridays_sundays_2025.csv"
SUMMARY_FILE = "files/mlb_fridays_sundays_summary_2025.csv"

# Store totals per player
# Key = (playerId, playerName, team), Value = {"Friday": {}, "Sunday": {}}
totals = defaultdict(lambda: {"Friday": defaultdict(int), "Sunday": defaultdict(int)})

# --- 1. Read the raw file ---
with open(RAW_FILE, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        weekday = row["weekday"]  # "Friday" or "Sunday"
        player_id = row["playerId"]
        player_name = row["playerName"]
        team = row["team"]

        # Parse the stats column (it's stored as a text dict)
        try:
            stats_dict = ast.literal_eval(row["stats"])
        except:
            continue

        # Add stats into the totals
        key = (player_id, player_name, team)
        for stat, value in stats_dict.items():
            if isinstance(value, (int, float)):
                totals[key][weekday][stat] += value

# --- 2. Figure out which stat categories to include ---
all_stats = set()
for _, splits in totals.items():
    for day in ["Friday", "Sunday"]:
        all_stats.update(splits[day].keys())
all_stats = sorted(all_stats)

# --- 3. Write the summary file ---
with open(SUMMARY_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    # Header: player info + stat columns split by weekday
    header = ["playerId","playerName","team"]
    for stat in all_stats:
        header.append(f"friday_{stat}")
    for stat in all_stats:
        header.append(f"sunday_{stat}")
    writer.writerow(header)

    # Rows per player
    for (player_id, player_name, team), splits in totals.items():
        row = [player_id, player_name, team]
        # Add Friday totals
        for stat in all_stats:
            row.append(splits["Friday"].get(stat, 0))
        # Add Sunday totals
        for stat in all_stats:
            row.append(splits["Sunday"].get(stat, 0))
        writer.writerow(row)

print(f"Summary written to {SUMMARY_FILE}")
