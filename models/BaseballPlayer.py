#Here I import necessary libraries for this file, if it's causing an error do the "pip intall ____" for the missing library
from pydantic import BaseModel, Field
from typing import Optional, Dict
from models.GameStats import GameStats
from models.AverageStats import AverageStats
import logging


#Here I am basically creating a custom data type to facilitate handling the data, this one represent a single baseball player and will store all of the stats we care about
class BaseballPlayer(BaseModel):
    # Configure logging
    logging.basicConfig(level=logging.ERROR)

    #Fields to fill during the FIRST endpoint call, all the baseline player info, you may*** want to tinker with this as I don't have the exact endpoint data in front of me.
    #Try to think of what fields we'll need for later. Does NOT have to be everything
    name: Optional[str] = Field(None, description="Player's full name")
    team: Optional[str] = Field(None, description="Team name")
    team_id: Optional[int] = Field(None, description="Team ID")
    position: Optional[str] = Field(None, description="Player's position")
    id: Optional[str] = Field(None, description="Player's ID")

    #Fields to fill during second Endpoint Call, every stat from every game
    gameStats: Optional[list[GameStats]] = Field(None, description="A list of every game the player has played in and the stats during that game")

    #Fields that will be filled to store the data calculated during the weekday specif stats load process
    statsOnWeekday: Dict[str, AverageStats] = Field(
        default_factory=lambda: {
            "Monday": AverageStats(),
            "Tuesday": AverageStats(),
            "Wednesday": AverageStats(),
            "Thursday": AverageStats(),
            "Friday": AverageStats(),
            "Saturday": AverageStats(),
            "Sunday": AverageStats()
        },
        description="Stats organized by weekday"
    )

    #This is a function, basically going to delegate a blob of code to this space that serves a specific purpose. Kind of like a variable for chunks of code
    #This one will be for calculating the stats for each weekday
    def calculateWeekdayStats(self) -> None: #Some functions return data, this one does not so I put 'None'
        if not self.gameStats or len(self.gameStats) == 0: #Doing a spot check to make sure the gameStats exist before doing any calculations. Should work as long as you properly fill the gameStats field after the second endpoint call
            logging.error("GAME STATS FIELD HAS NOT BEEN POPULATED YET")
            return

        # Clear existing stats
        for day in self.statsOnWeekday.keys():
            self.statsOnWeekday[day] = AverageStats()

        # Aggregate stats by weekday
        for game in self.gameStats:
            if game.weekday and game.weekday in self.statsOnWeekday:
                day_stats = self.statsOnWeekday[game.weekday]

                # Add counting stats
                day_stats.atBats = (day_stats.atBats or 0) + (game.atBats or 0)
                day_stats.hits = (day_stats.hits or 0) + (game.hits or 0)
                day_stats.runs = (day_stats.runs or 0) + (game.runs or 0)
                day_stats.homeRuns = (day_stats.homeRuns or 0) + (game.homeRuns or 0)
                day_stats.rbi = (day_stats.rbi or 0) + (game.rbi or 0)
                day_stats.baseOnBalls = (day_stats.baseOnBalls or 0) + (game.baseOnBalls or 0)
                day_stats.hitByPitch = (day_stats.hitByPitch or 0) + (game.hitByPitch or 0)
                day_stats.sacFlies = (day_stats.sacFlies or 0) + (game.sacFlies or 0)
                day_stats.doubles = (day_stats.doubles or 0) + (game.doubles or 0)
                day_stats.triples = (day_stats.triples or 0) + (game.triples or 0)

        # Calculate rate stats for each day
        for day_stats in self.statsOnWeekday.values():
            day_stats.calculate_rates()

        return


"""
=== CODING CONCEPTS EXPLAINED FOR BEGINNERS ===

This file is like creating a SUPER detailed baseball card for each player!

1. MORE ADVANCED IMPORTS:
   - Dict = dictionary, like a phone book that connects names to phone numbers
   - Here it connects weekday names ("Monday") to stats (AverageStats)

2. LISTS (line 22):
   - list[GameStats] = a shopping list, but for game statistics
   - It can hold many GameStats objects in order
   - Like having a stack of scorecards from every game the player played

3. DICTIONARIES (line 25):
   - Dict[str, AverageStats] = like a filing cabinet with labeled drawers
   - str (string) = the label on the drawer ("Monday", "Tuesday", etc.)
   - AverageStats = what's inside each drawer (the stats for that day)

4. DEFAULT FACTORY:
   - default_factory=lambda = "here's how to set up the filing cabinet when it's brand new"
   - Lambda is like a mini-instruction that creates all 7 weekday drawers automatically

5. FUNCTIONS/METHODS (line 36):
   - def calculateWeekdayStats(self) = "here's a set of instructions the player can follow"
   - self = "hey, I'm talking about THIS specific player"
   - -> None = "this function does work but doesn't give back any information"

6. IF STATEMENTS (line 37):
   - if (condition) = "only do this IF something is true"
   - Like saying "IF it's raining, THEN bring an umbrella"

7. LOGGING:
   - logging.error() = like writing in a diary when something goes wrong
   - It helps us figure out problems later

8. RETURN:
   - return = "I'm done with this function now"
   - Like saying "The End" in a story

Think of BaseballPlayer like a really detailed baseball card that can also do math!
"""