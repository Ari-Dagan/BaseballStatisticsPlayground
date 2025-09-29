import csv

INPUT_FILE = "files/mlb_fridays_sundays_summary_2025.csv"
OUTPUT_FILE = "files/mlb_fridays_sundays_rates_2025.csv"

def safe_divide(numerator, denominator):
    return round(numerator / denominator, 3) if denominator != 0 else 0.0

with open(INPUT_FILE, "r") as f_in, open(OUTPUT_FILE, "w", newline="") as f_out:
    reader = csv.DictReader(f_in)
    fieldnames = ["playerId","playerName","team",
                  "friday_avg","friday_obp","friday_slg","friday_ops",
                  "sunday_avg","sunday_obp","sunday_slg","sunday_ops"]
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        # Extract values safely
        H_fri = int(row.get("friday_hits", 0))
        AB_fri = int(row.get("friday_atBats", 0))
        BB_fri = int(row.get("friday_baseOnBalls", 0))
        HBP_fri = int(row.get("friday_hitByPitch", 0))
        SF_fri = int(row.get("friday_sacFlies", 0))
        doubles_fri = int(row.get("friday_doubles", 0))
        triples_fri = int(row.get("friday_triples", 0))
        HR_fri = int(row.get("friday_homeRuns", 0))
        singles_fri = H_fri - doubles_fri - triples_fri - HR_fri
        TB_fri = singles_fri + 2*doubles_fri + 3*triples_fri + 4*HR_fri

        H_sun = int(row.get("sunday_hits", 0))
        AB_sun = int(row.get("sunday_atBats", 0))
        BB_sun = int(row.get("sunday_baseOnBalls", 0))
        HBP_sun = int(row.get("sunday_hitByPitch", 0))
        SF_sun = int(row.get("sunday_sacFlies", 0))
        doubles_sun = int(row.get("sunday_doubles", 0))
        triples_sun = int(row.get("sunday_triples", 0))
        HR_sun = int(row.get("sunday_homeRuns", 0))
        singles_sun = H_sun - doubles_sun - triples_sun - HR_sun
        TB_sun = singles_sun + 2*doubles_sun + 3*triples_sun + 4*HR_sun

        # Calculate advanced stats
        fri_avg = safe_divide(H_fri, AB_fri)
        fri_obp = safe_divide(H_fri + BB_fri + HBP_fri, AB_fri + BB_fri + HBP_fri + SF_fri)
        fri_slg = safe_divide(TB_fri, AB_fri)
        fri_ops = round(fri_obp + fri_slg, 3)

        sun_avg = safe_divide(H_sun, AB_sun)
        sun_obp = safe_divide(H_sun + BB_sun + HBP_sun, AB_sun + BB_sun + HBP_sun + SF_sun)
        sun_slg = safe_divide(TB_sun, AB_sun)
        sun_ops = round(sun_obp + sun_slg, 3)

        writer.writerow({
            "playerId": row["playerId"],
            "playerName": row["playerName"],
            "team": row["team"],
            "friday_avg": fri_avg,
            "friday_obp": fri_obp,
            "friday_slg": fri_slg,
            "friday_ops": fri_ops,
            "sunday_avg": sun_avg,
            "sunday_obp": sun_obp,
            "sunday_slg": sun_slg,
            "sunday_ops": sun_ops
        })

print(f"Advanced stats written to {OUTPUT_FILE}")
