from enum import Enum


class PlayStyleType(Enum):
    AGGRESSIVE = 1
    BALANCED = 2
    DEFENSIVE = 3


class Result(Enum):
    TRIPLESCORE = 1
    RETAINSCORE = 2
    SCORE = 3
    RETAINMISS = 4
    MISS = 5
    TURNOVER = 6
    DEFENSIVESCORE = 7
    DEFRETAIN = 8
    TRIPLEDEF = 9


class Team:
    def __init__(self):
        self.name = ""
        self.coach = ""
        self.playStyle = ""
        self.emoji = ""


class Poss:
    def __init__(self):
        self.homePos = False
        self.awayPos = False

    def switch(self):
        if self.homePos:
            self.homePos = False
            self.awayPos = True
        else:
            self.homePos = True
            self.awayPos = False

    def set(self, home):
        if home:
            self.homePos = True
            self.awayPos = False
        else:
            self.homePos = False
            self.awayPos = True


class TeamStats:
    def __init__(self):
        self.possessions = 0
        self.points = 0
        self.goalsScored = 0
        self.shotAttempts = 0
        self.saves = 0
        self.posSaves = 0
        self.offensiveRebounds = 0
        self.defensiveRebounds = 0
        self.turnovers = 0
        self.snitchCaught = False
        self.wonDuel = False


class Game:
    def __init__(self, home, away, channel):
        self.homeID = home
        self.awayID = away

        self.mainChannel = channel

        self.possessionNumber = 1
        self.Possession = Poss()
        self.homeStats = TeamStats()
        self.awayStats = TeamStats()

        self.waitHome = True
        self.waitAway = True
        self.quaffleToss = True
        self.duel = False
        self.snitchCaught = False

        self.location = None

        self.offenseNumber = None
        self.offenseSnitchNumber = None
        self.defenseNumber = None
        self.defenseSnitchNumber = None
        self.snitchMax = 300

        self.winner = None

    def getSnitchMax(self):
        if self.possessionNumber < 9:
            self.snitchMax = 300
        elif self.possessionNumber < 17:
            self.snitchMax = 200
        elif self.possessionNumber < 25:
            self.snitchMax = 100
        elif self.possessionNumber < 43:
            self.snitchMax = 30
        elif self.possessionNumber < 60:
            self.snitchMax = 20
        elif self.possessionNumber > 60:
            self.snitchMax = 10

        return self.snitchMax

    def clearNumbers(self):
        self.offenseNumber = None
        self.offenseSnitchNumber = None
        self.defenseNumber = None
        self.defenseSnitchNumber = None

