#Here I import necessary libraries for this file, if it's causing an error do the "pip intall ____" for the missing library
from datetime import date
from pydantic import BaseModel, Field
from typing import Optional

#Here I am basically creating a custom data type to facilitate handling the data, this one represent a single game and the stats we care about. Add whatever fields you need
class GameStats(BaseModel):
    gameDate: Optional[date] = Field(None, description="Date of the game")
    weekday: Optional[str] = Field(None, description="Weekday of the game (Friday, Sunday, etc.)")
    gamePK: Optional[int] = Field(None, description="Unique game identifier")
    team: Optional[str] = Field(None, description="Team name for this game")

    # Batting stats from MLB API
    atBats: Optional[int] = Field(None, ge=0, description="Number of at-bats")
    hits: Optional[int] = Field(None, ge=0, description="Number of hits")
    runs: Optional[int] = Field(None, ge=0, description="Number of runs scored")
    homeRuns: Optional[int] = Field(None, ge=0, description="Number of home runs")
    rbi: Optional[int] = Field(None, ge=0, description="Runs batted in")
    baseOnBalls: Optional[int] = Field(None, ge=0, description="Number of walks/base on balls")
    hitByPitch: Optional[int] = Field(None, ge=0, description="Number of times hit by pitch")
    sacFlies: Optional[int] = Field(None, ge=0, description="Number of sacrifice flies")
    doubles: Optional[int] = Field(None, ge=0, description="Number of doubles")
    triples: Optional[int] = Field(None, ge=0, description="Number of triples")

    # Keep legacy fields for backward compatibility
    at_bats: Optional[int] = Field(None, ge=0, description="Legacy field for at-bats")
    home_runs: Optional[int] = Field(None, ge=0, description="Legacy field for home runs")
    walks: Optional[int] = Field(None, ge=0, description="Legacy field for walks")

'''
Example usage:
example = GameStats(
    gameDate="2024-06-07",
    gamePK=123456,
    at_bats=4,
    hits=2,
    runs=1,
    home_runs=1,
    rbi=3,
    walks=0
)
'''


"""
=== CODING CONCEPTS EXPLAINED FOR BEGINNERS ===

This file is like a recipe card for recording one baseball game!

1. NEW TYPES WE SEE HERE:
   - date = a calendar date (like your birthday: June 7, 2024)
   - int = whole numbers only (like 1, 2, 3... no decimals!)
   - Optional = "this information might be missing, and that's OK"

2. IMPORTS (lines 2-4):
   - We're borrowing the 'date' tool to work with calendar dates
   - It's like borrowing a calendar from your friend!

3. THE GameStats CLASS:
   - Think of this like a baseball scorecard
   - Each field is a different box on the scorecard:
     * gameDate = "What day was this game?"
     * gamePK = "What's this game's special ID number?"
     * at_bats = "How many times did the player try to hit?"
     * hits = "How many times did they actually hit the ball?"
     * And so on...

4. VALIDATION (ge=0):
   - This is like having a grown-up check your math
   - ge=0 means "this number can't be negative"
   - You can't have -3 hits in a game - that doesn't make sense!

5. THE EXAMPLE AT THE BOTTOM:
   - This shows how to fill out the scorecard for a real game
   - It's like showing someone how to fill out a form correctly

Think of GameStats like a single page in a baseball player's diary!
"""