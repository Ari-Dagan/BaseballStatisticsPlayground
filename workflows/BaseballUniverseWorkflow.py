#Here I import necessary libraries for this file, if it's causing an error do the "pip intall ____" for the missing library
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from models.BaseballPlayer import BaseballPlayer
from models.GameStats import GameStats
from models.AverageStats import AverageStats
import logging
import requests
import csv
from datetime import date, timedelta
import ast
from collections import defaultdict
import os
import pandas as pd

#Here I am creating a place where we can store all the information on every player, and also have the logic for creating them / calling the endpoints
class BaseballUniverseWorkflow(BaseModel):
    Players: Optional[list[BaseballPlayer]] = Field(default_factory=list, description="A list of every baseball player and their stats")
    Teams: Optional[Dict[int, str]] = Field(default_factory=dict, description="Dictionary of team_id -> team_name")
    season: Optional[int] = Field(2025, description="Year of season")
    files_dir: str = Field("files", description="Directory to store CSV files")

    #This function will call the first endpoint, and then fill the first round of fields for each Baseball Player (name,PK, etc)
    def FillPlayerList(self) -> None:
        """Step 3: Get all teams and their rosters, save to CSV and build Player objects"""
        # Ensure files directory exists
        os.makedirs(self.files_dir, exist_ok=True)

        # 1. Get all teams
        teams_url = "https://statsapi.mlb.com/api/v1/teams?sportId=1"
        resp = requests.get(teams_url).json()
        teams = resp.get("teams", [])

        print(f"Found {len(teams)} MLB teams")

        # 2. Open a CSV file to save data
        csv_file = f"{self.files_dir}/mlb_rosters_{self.season}.csv"
        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            # Write header row
            writer.writerow(["teamId", "teamName", "playerId", "playerName", "position"])

            # 3. Loop through teams and collect players
            for t in teams:
                team_id = t["id"]
                team_name = t["name"]

                # Store team in our Teams dict
                self.Teams[team_id] = team_name

                roster_url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster?season={self.season}"
                roster_resp = requests.get(roster_url).json()

                roster = roster_resp.get("roster", [])


                for player in roster:
                    player_id = str(player["person"]["id"])
                    player_name = player["person"]["fullName"]
                    position = player["position"]["abbreviation"]

                    # Write a row to CSV
                    writer.writerow([team_id, team_name, player_id, player_name, position])

                    # Create BaseballPlayer object
                    baseball_player = BaseballPlayer(
                        id=player_id,
                        name=player_name,
                        team=team_name,
                        team_id=team_id,
                        position=position,
                        gameStats=[]
                    )
                    self.Players.append(baseball_player)

        print(f"Roster data saved to {csv_file}")
        print(f"Created {len(self.Players)} BaseballPlayer objects")
        return

    #This function will call the second endpoint and third over and over for each BaseballPlayer.id and store each game info in the list BaseballPlayer.gameStats
    def FillGameStats(self) -> None:
        """Step 5: Get game stats for all players on specific dates and save to CSV"""
        # Get all Fridays + Sundays in 2025
        start = date(2025, 3, 27)   # MLB season start buffer
        end   = date(2025, 5, 27)   # MLB season end buffer

        dates = []
        d = start
        while d <= end:
            if d.weekday() in [4, 6]:  # 4 = Friday, 6 = Sunday
                dates.append(d)
            d += timedelta(days=1)

        print(f"Found {len(dates)} Fridays/Sundays in 2025")

        # Open CSV to save all raw data
        csv_file = f"{self.files_dir}/mlb_game_stats_{self.season}.csv"
        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date","weekday","gamePk","team","playerId","playerName","position","stats"])

            # Loop through all dates
            for game_date in dates:
                # Figure out weekday label
                weekday_label = "Friday" if game_date.weekday() == 4 else "Sunday"

                schedule_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={game_date.isoformat()}&gameTypes=R"
                schedule = requests.get(schedule_url).json()
                games = [g["gamePk"] for d in schedule.get("dates", []) for g in d.get("games", [])]

                print(f"{game_date} ({weekday_label}): {len(games)} games")

                # Loop through each game and pull boxscore
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
                            stats = pdata.get("stats", {}).get("batting", {})

                            # Write to CSV
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

                            # Find the player in our Players list and add GameStats
                            player_id_str = player_id.replace("ID", "")  # Remove "ID" prefix
                            for player in self.Players:
                                if player.id == player_id_str:
                                    # Create GameStats object
                                    game_stats = GameStats(
                                        gameDate=game_date,
                                        weekday=weekday_label,
                                        gamePK=gamePk,
                                        team=team_name,
                                        atBats=stats.get("atBats", 0),
                                        hits=stats.get("hits", 0),
                                        runs=stats.get("runs", 0),
                                        homeRuns=stats.get("homeRuns", 0),
                                        rbi=stats.get("rbi", 0),
                                        baseOnBalls=stats.get("baseOnBalls", 0),
                                        hitByPitch=stats.get("hitByPitch", 0),
                                        sacFlies=stats.get("sacFlies", 0),
                                        doubles=stats.get("doubles", 0),
                                        triples=stats.get("triples", 0)
                                    )
                                    player.gameStats.append(game_stats)
                                    break

        print(f"Game stats saved to {csv_file}")
        return

    #This function simply calls each players calculateWeekdayStats function so that each players statsOnWeekday field is filled with data, then saves to CSVs
    def executeCalculateWeekdayStats(self) -> None:
        """Step 6 & 7: Calculate weekday stats for all players and save to summary and rates CSVs"""
        if self.Players:
            # Calculate stats for each player
            for player in self.Players:
                if player.gameStats and len(player.gameStats) > 0:
                    player.calculateWeekdayStats() #This is how you call the function of a object. and Object is an instance of a "class"

            # Step 6: Write summary CSV with aggregated counting stats
            summary_file = f"{self.files_dir}/mlb_weekday_summary_{self.season}.csv"

            # Determine which stats to include (all stats from the first player)
            all_stats = ["atBats", "hits", "runs", "homeRuns", "rbi", "baseOnBalls", "hitByPitch", "sacFlies", "doubles", "triples"]
            weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

            with open(summary_file, "w", newline="") as f:
                writer = csv.writer(f)

                # Header: player info + stat columns split by weekday
                header = ["playerId", "playerName", "team"]
                for day in weekdays:
                    for stat in all_stats:
                        header.append(f"{day.lower()}_{stat}")
                writer.writerow(header)

                # Write row for each player
                for player in self.Players:
                    row = [player.id, player.name, player.team]
                    for day in weekdays:
                        day_stats = player.statsOnWeekday.get(day, AverageStats())
                        for stat in all_stats:
                            row.append(getattr(day_stats, stat, 0) or 0)
                    writer.writerow(row)

            print(f"Summary stats written to {summary_file}")

            # Step 7: Write rates CSV with calculated advanced stats
            rates_file = f"{self.files_dir}/mlb_weekday_rates_{self.season}.csv"

            with open(rates_file, "w", newline="") as f:
                writer = csv.writer(f)

                # Header: player info + rate stats for each weekday
                header = ["playerId", "playerName", "team"]
                for day in weekdays:
                    header.extend([f"{day.lower()}_avg", f"{day.lower()}_obp", f"{day.lower()}_slg", f"{day.lower()}_ops"])
                writer.writerow(header)

                # Write row for each player
                for player in self.Players:
                    row = [player.id, player.name, player.team]
                    for day in weekdays:
                        day_stats = player.statsOnWeekday.get(day, AverageStats())
                        row.extend([
                            day_stats.AVG or 0.0,
                            day_stats.OBP or 0.0,
                            day_stats.SLG or 0.0,
                            day_stats.OPS or 0.0
                        ])
                    writer.writerow(row)

            print(f"Rate stats written to {rates_file}")

    #This Function will put it all together, also likely no need to touch this one
    def startWorkflow(self) -> None:
        self.FillPlayerList()
        self.FillGameStats()
        self.executeCalculateWeekdayStats()

    #This function will get a player based on a name, we'll probably make more functions like this
    def getPlayer(self, name: str) -> BaseballPlayer | None:
       if self.Players:
             for player in self.Players:
                if player.name.lower() == name.lower(): #I put both strings in lower case so that casing doesn't matter
                   return player
       logging.error("Either Player does not exist or has not been loaded into the workflow")
       return

    # ============ HELPER FUNCTIONS FOR DATA ANALYSIS ============

    def get_players_with_min_games(self, min_games: int, weekdays: list[str] = None) -> list[BaseballPlayer]:
        """
        Get players who have played at least min_games on specified weekdays.

        Args:
            min_games: Minimum number of games required
            weekdays: List of weekday names to check (default: ["Friday", "Sunday"])

        Returns:
            List of BaseballPlayer objects meeting the criteria
        """
        if weekdays is None:
            weekdays = ["Friday", "Sunday"]

        eligible_players = []

        for player in self.Players:
            if not player.gameStats:
                continue

            # Count games per weekday
            game_counts = {day: 0 for day in weekdays}
            for game in player.gameStats:
                if game.weekday in game_counts:
                    game_counts[game.weekday] += 1

            # Check if player meets minimum games requirement for all specified weekdays
            meets_criteria = all(game_counts[day] >= min_games for day in weekdays)

            if meets_criteria:
                eligible_players.append(player)

        return eligible_players

    def get_stats_dataframe(self, players: list[BaseballPlayer] = None, weekdays: list[str] = None, stats: list[str] = None):
        """
        Get player stats as a pandas DataFrame for easy analysis and visualization.

        Args:
            players: List of BaseballPlayer objects (default: all players)
            weekdays: List of weekday names (default: all weekdays)
            stats: List of stat names to include (default: ['AVG', 'OBP', 'SLG', 'OPS'])

        Returns:
            pandas DataFrame with player info and stats
        """
        

        if players is None:
            players = self.Players

        if weekdays is None:
            weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        if stats is None:
            stats = ['AVG', 'OBP', 'SLG', 'OPS']

        player_data = []

        for player in players:
            row = {
                'playerId': player.id,
                'playerName': player.name,
                'team': player.team
            }

            # Add counting stats for game counts
            for day in weekdays:
                game_count = sum(1 for game in player.gameStats if game.weekday == day) if player.gameStats else 0
                row[f'{day}_games'] = game_count

            # Add requested stats for each weekday
            for day in weekdays:
                day_stats = player.statsOnWeekday.get(day)
                if day_stats:
                    for stat in stats:
                        row[f'{day}_{stat}'] = getattr(day_stats, stat, None)
                else:
                    for stat in stats:
                        row[f'{day}_{stat}'] = None

            player_data.append(row)

        return pd.DataFrame(player_data)

    def get_league_average_by_weekday(self, min_games: int = 5, weekdays: list[str] = None):
        """
        Calculate league-wide batting average for specified weekdays.
        Only includes players who have played at least min_games on each specified weekday.

        Args:
            min_games: Minimum number of games required for a player to be included
            weekdays: List of weekday names (default: ["Friday", "Sunday"])

        Returns:
            pandas DataFrame with weekday and league-wide AVG, OBP, SLG, OPS
        """
        if weekdays is None:
            weekdays = ["Friday", "Sunday"]

        # Get eligible players
        eligible_players = self.get_players_with_min_games(min_games, weekdays)

        league_stats = []

        for day in weekdays:
            # Aggregate all counting stats across all eligible players for this day
            total_atBats = 0
            total_hits = 0
            total_baseOnBalls = 0
            total_hitByPitch = 0
            total_sacFlies = 0
            total_doubles = 0
            total_triples = 0
            total_homeRuns = 0

            for player in eligible_players:
                day_stats = player.statsOnWeekday.get(day)
                if day_stats:
                    total_atBats += day_stats.atBats or 0
                    total_hits += day_stats.hits or 0
                    total_baseOnBalls += day_stats.baseOnBalls or 0
                    total_hitByPitch += day_stats.hitByPitch or 0
                    total_sacFlies += day_stats.sacFlies or 0
                    total_doubles += day_stats.doubles or 0
                    total_triples += day_stats.triples or 0
                    total_homeRuns += day_stats.homeRuns or 0

            # Calculate league-wide rate stats
            def safe_divide(numerator, denominator):
                return round(numerator / denominator, 3) if denominator != 0 else 0.0

            avg = safe_divide(total_hits, total_atBats)
            obp = safe_divide(
                total_hits + total_baseOnBalls + total_hitByPitch,
                total_atBats + total_baseOnBalls + total_hitByPitch + total_sacFlies
            )

            singles = total_hits - total_doubles - total_triples - total_homeRuns
            total_bases = singles + 2*total_doubles + 3*total_triples + 4*total_homeRuns
            slg = safe_divide(total_bases, total_atBats)
            ops = round(obp + slg, 3)

            league_stats.append({
                'weekday': day,
                'AVG': avg,
                'OBP': obp,
                'SLG': slg,
                'OPS': ops,
                'total_atBats': total_atBats,
                'total_hits': total_hits,
                'num_players': len(eligible_players)
            })

        return pd.DataFrame(league_stats)



"""
=== CODING CONCEPTS EXPLAINED FOR BEGINNERS ===

This file is like the MANAGER of all the baseball players - it tells everyone what to do!

1. WORKFLOW CONCEPT:
   - A workflow is like a recipe with steps that must be done in order
   - Step 1: Get all player names
   - Step 2: Get all their game stats
   - Step 3: Calculate their weekday averages

2. MANAGING OTHER OBJECTS:
   - This class holds a list of BaseballPlayer objects
   - It's like being the coach of a whole team
   - The coach tells each player when to do their individual tasks

3. FOR LOOPS (line 28):
   - for player in self.Players = "for each player on my team, do this:"
   - It's like saying "Everyone on the team, do 10 jumping jacks!"
   - The computer will repeat the same instruction for every player

4. CALLING METHODS ON OBJECTS:
   - player.calculateWeekdayStats() = "Hey player, do your math homework!"
   - The dot (.) is like tapping someone on the shoulder to get their attention

5. DEFENSIVE PROGRAMMING (line 27):
   - if self.Players: = "only do this if I actually have players on my team"
   - It's like checking if your backpack has books before trying to do homework

6. WORKFLOW ORCHESTRATION:
   - startWorkflow() calls three functions IN ORDER
   - It's like a conductor leading an orchestra
   - Everyone has to do their part at the right time

7. FUNCTION ORGANIZATION:
   - Each function has ONE job (like having different workers at a factory)
   - FillPlayerList = the person who makes the list of players
   - FillGameStats = the person who collects all the scorecards
   - executeCalculateWeekdayStats = the person who does all the math

Think of this like being the manager of a baseball team's statistics department!
The manager tells everyone what to do and when to do it, but doesn't do all the work themselves.
"""