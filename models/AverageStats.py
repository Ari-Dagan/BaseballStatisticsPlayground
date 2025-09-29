#Here I import necessary libraries for this file, if it's causing an error do the "pip intall ____" for the missing library
from pydantic import BaseModel, Field
from typing import Optional

#Here I am basically creating a custom data type to facilitate handling the data, this one represent a set of averages. What set is up to you, whether it'll be specifically for a weekday, season, or arbitrary stretch of time
class AverageStats(BaseModel):
    # Basic counting stats totals
    atBats: Optional[int] = Field(0, description="Total at-bats")
    hits: Optional[int] = Field(0, description="Total hits")
    runs: Optional[int] = Field(0, description="Total runs")
    homeRuns: Optional[int] = Field(0, description="Total home runs")
    rbi: Optional[int] = Field(0, description="Total RBIs")
    baseOnBalls: Optional[int] = Field(0, description="Total walks")
    hitByPitch: Optional[int] = Field(0, description="Total hit by pitch")
    sacFlies: Optional[int] = Field(0, description="Total sacrifice flies")
    doubles: Optional[int] = Field(0, description="Total doubles")
    triples: Optional[int] = Field(0, description="Total triples")

    # Calculated rate stats
    AVG: Optional[float] = Field(None, description="Batting Average (hits/at-bats)")
    OBP: Optional[float] = Field(None, description="On-Base Percentage")
    SLG: Optional[float] = Field(None, description="Slugging Percentage")
    OPS: Optional[float] = Field(None, description="On-base Plus Slugging")

    def calculate_rates(self) -> None:
        """Calculate advanced batting statistics from counting stats"""
        def safe_divide(numerator, denominator):
            return round(numerator / denominator, 3) if denominator != 0 else 0.0

        # Calculate batting average
        self.AVG = safe_divide(self.hits or 0, self.atBats or 0)

        # Calculate on-base percentage
        numerator = (self.hits or 0) + (self.baseOnBalls or 0) + (self.hitByPitch or 0)
        denominator = (self.atBats or 0) + (self.baseOnBalls or 0) + (self.hitByPitch or 0) + (self.sacFlies or 0)
        self.OBP = safe_divide(numerator, denominator)

        # Calculate slugging percentage
        singles = (self.hits or 0) - (self.doubles or 0) - (self.triples or 0) - (self.homeRuns or 0)
        total_bases = singles + 2*(self.doubles or 0) + 3*(self.triples or 0) + 4*(self.homeRuns or 0)
        self.SLG = safe_divide(total_bases, self.atBats or 0)

        # Calculate OPS
        self.OPS = round((self.OBP or 0) + (self.SLG or 0), 3)


"""
=== CODING CONCEPTS EXPLAINED FOR BEGINNERS ===

Think of coding like giving instructions to a very smart but literal robot!

1. IMPORTING LIBRARIES (lines 1-3):
   - This is like borrowing tools from a toolbox
   - "from pydantic import BaseModel" = "Hey robot, I want to use the BaseModel tool"
   - Libraries are code that other people wrote so we don't have to!

2. CLASS (line 6):
   - A class is like a cookie cutter or blueprint
   - It tells the computer "this is what an AverageStats should look like"
   - Just like how all chocolate chip cookies made from the same cutter look similar!

3. VARIABLES/FIELDS (lines 7-10):
   - These are like boxes with labels on them
   - AVG is a box that can hold a number (like 0.350)
   - Optional means "this box can be empty if we want"

4. TYPES:
   - float = decimal numbers (like 3.14 or 0.250)
   - Optional[float] = "this can be a decimal number OR empty"

5. Field():
   - This is like putting instructions on the box
   - Field(None) = "start with this box empty"
   - description = "a note explaining what goes in this box"
   - ge=0 means "greater than or equal to 0" (no negative numbers allowed!)

When you create an AverageStats, it's like using the cookie cutter to make an actual cookie!
"""
