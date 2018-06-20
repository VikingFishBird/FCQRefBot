import re
import wiki
import random
from classes import Game
from classes import Result

games = []


# start game Horton Hogwarts [station]
def startGame(messageText, channel, custom=False):
    global games
    games = []

    items = messageText.split(" ")
    if custom:
        return

    homeTeamName = items[2]
    awayTeamName = items[3]

    homeID = findTeamIDByName(homeTeamName)
    awayID = findTeamIDByName(awayTeamName)

    if homeID is None or awayID is None:
        print("Invalid Start Game Command")
        return

    games.append(Game(homeID, awayID, channel))

    return wiki.teams[homeID].coach, wiki.teams[awayID].coach


def abandonGame(message):
    splitter = message.content.split(' ')
    if len(splitter) < 4:
        return

    for x in range(games.__len__()):
        if splitter[2].lower() == wiki.teams[games[x].homeID].name.lower() and splitter[3].lower() == wiki.teams[games[x].awayID].name.lower():
            del games[x]
            return

    print("Couldn't find game")


def findTeamIDByName(name):
    for x in range(wiki.teams.__len__()):
        if wiki.teams[x].name.lower() == name:
            return x

    return None


def getNumDif(offNum, defNum):
    difference = abs(offNum-defNum)
    if difference > 500:
        difference = 1000-difference

    return difference


def processMessage(message):
    gameID = None
    isHome = None

    if games.__len__() == 0:
        return False, "There are currently no games running!", -1

    for x in range(games.__len__()):
        if str(message.author) == wiki.teams[games[x].homeID].coach:
            gameID = x
            isHome = True
        elif str(message.author) == wiki.teams[games[x].awayID].coach:
            gameID = x
            isHome = False
        else:
            return False, "Not a valid coach. You are not in a game.", -1

    if isHome:
        if not games[gameID].waitHome:
            return False, "I am not waiting on a number from you.", gameID
    else:
        if not games[gameID].waitAway:
            return False, "I am not waiting on a number from you.", gameID

    if games[gameID].quaffleToss:
        if re.search(r'\d+', message.content) is not None:
            if re.search(r'[a-zA-Z]+', message.content) is None:
                split = message.content.split(" ")
                if len(split) > 1:
                    return False, "Too many numbers", gameID
                tossNum = int(message.content)
                if tossNum > 1000 or tossNum < 1:
                    return False, "The quaffle toss number must be within 1-1000", gameID

                if isHome:
                    games[gameID].waitHome = False
                    games[gameID].offenseNumber = tossNum
                else:
                    games[gameID].waitAway = False
                    games[gameID].defenseNumber = tossNum

                return True, "I got {} as your quaffle toss number.".format(tossNum), gameID
            else:
                return False, "The quaffle toss number must be within 1-1000 - No numbers please", gameID
        return False, "Invalid Number Submission. Please use the format: 500 (QuaffleToss).", gameID

    if games[gameID].duel:
        if re.search(r'\d+', message.content) is not None and re.search(r'[a-zA-Z]', message.content) is None:
            split = message.content.split(" ")
            if len(split) > 1:
                return False, "Too many numbers", gameID
            tossNum = int(message.content)
            if tossNum > 1000 or tossNum < 1:
                return False, "The duel number must be within 1-1000", gameID

            if isHome:
                games[gameID].waitHome = False
                games[gameID].offenseNumber = tossNum
            else:
                games[gameID].waitAway = False
                games[gameID].defenseNumber = tossNum

            return True, "I got {} as your duel toss number.".format(tossNum), gameID
        return False, "Invalid Number Submission. Please use the format: 500 (Duel).", gameID

    if re.search(r'\d+\s\d+', message.content) is not None and re.search(r'[a-zA-Z]+', message.content) is None:
        nums = message.content.split(' ')
        quaffleNumber = int(nums[0])
        snitchNumber = int(nums[1])

        if quaffleNumber > 1000 or quaffleNumber < 1 or snitchNumber > games[gameID].getSnitchMax() or snitchNumber < 1:
            return False, "The quaffle number must be within 1-1000 and the snitch number must be 1-{}".format(games[gameID].getSnitchMax()), gameID

        if (isHome and games[gameID].Possession.homePos) or (not isHome and games[gameID].Possession.awayPos):
            games[gameID].offenseNumber = quaffleNumber
            games[gameID].offenseSnitchNumber = snitchNumber
        else:
            games[gameID].defenseNumber = quaffleNumber
            games[gameID].defenseSnitchNumber = snitchNumber

        if isHome:
            games[gameID].waitHome = False
        else:
            games[gameID].waitAway = False

        return True, "I got {} as your quaffle number and {} as your snitch number.".format(quaffleNumber, snitchNumber), gameID

    else:
        print("Invalid Number Submission")
        return False, "Invalid Number Submission. Please use the format: 500 50 (QuaffleNum SnitchNum).", gameID


def getEnds(rangeString):
    rangeEnds = rangeString.split('-')
    return int(rangeEnds[0]), int(rangeEnds[1])


def getResult(gameID):
    difference = getNumDif(games[gameID].offenseNumber, games[gameID].defenseNumber)
    offense = None
    defense = None
    result = None
    offenseID = None
    ishome = games[gameID].Possession.homePos
    if ishome:
        offenseID = games[gameID].homeID
        offense = wiki.teams[games[gameID].homeID].playStyle
        defense = wiki.teams[games[gameID].awayID].playStyle
    else:
        offenseID = games[gameID].awayID
        offense = wiki.teams[games[gameID].awayID].playStyle
        defense = wiki.teams[games[gameID].homeID].playStyle

    for key in wiki.ranges[offense][defense]:
        rangeStart, rangeEnd = getEnds(key)
        if rangeStart <= difference <= rangeEnd:
            result = wiki.ranges[offense][defense][key]

    resultString = None
    if result == Result.TRIPLESCORE:
        resultString = "scores *three* times!"
        games[gameID].possessionNumber = games[gameID].possessionNumber + 1
        if ishome:
            games[gameID].homeStats.possessions = games[gameID].homeStats.possessions + 1
            games[gameID].homeStats.points = games[gameID].homeStats.points + 30
            games[gameID].homeStats.goalsScored = games[gameID].homeStats.goalsScored + 3
            games[gameID].homeStats.shotAttempts = games[gameID].homeStats.shotAttempts + 3
            games[gameID].homeStats.offensiveRebounds = games[gameID].homeStats.offensiveRebounds + 2

            games[gameID].awayStats.defensiveRebounds = games[gameID].awayStats.defensiveRebounds + 1
            games[gameID].awayStats.posSaves = games[gameID].awayStats.posSaves + 3
        else:
            games[gameID].awayStats.possessions = games[gameID].awayStats.possessions + 1
            games[gameID].awayStats.points = games[gameID].awayStats.points + 30
            games[gameID].awayStats.goalsScored = games[gameID].awayStats.goalsScored + 3
            games[gameID].awayStats.shotAttempts = games[gameID].awayStats.shotAttempts + 3
            games[gameID].awayStats.offensiveRebounds = games[gameID].awayStats.offensiveRebounds + 2

            games[gameID].homeStats.defensiveRebounds = games[gameID].homeStats.defensiveRebounds + 1
            games[gameID].homeStats.posSaves = games[gameID].homeStats.posSaves + 3

        games[gameID].Possession.switch()

    elif result == Result.RETAINSCORE:
        resultString = "scores and retains possession!"
        games[gameID].possessionNumber = games[gameID].possessionNumber + 1
        if ishome:
            games[gameID].homeStats.possessions = games[gameID].homeStats.possessions + 1
            games[gameID].homeStats.points = games[gameID].homeStats.points + 10
            games[gameID].homeStats.goalsScored = games[gameID].homeStats.goalsScored + 1
            games[gameID].homeStats.shotAttempts = games[gameID].homeStats.shotAttempts + 1
            games[gameID].homeStats.offensiveRebounds = games[gameID].homeStats.offensiveRebounds + 1

            games[gameID].awayStats.posSaves = games[gameID].awayStats.posSaves + 1
        else:
            games[gameID].awayStats.possessions = games[gameID].awayStats.possessions + 1
            games[gameID].awayStats.points = games[gameID].awayStats.points + 10
            games[gameID].awayStats.goalsScored = games[gameID].awayStats.goalsScored + 1
            games[gameID].awayStats.shotAttempts = games[gameID].awayStats.shotAttempts + 1
            games[gameID].awayStats.offensiveRebounds = games[gameID].awayStats.offensiveRebounds + 1

            games[gameID].homeStats.posSaves = games[gameID].homeStats.posSaves + 1

    elif result == Result.SCORE:
        resultString = "scored!"
        games[gameID].possessionNumber = games[gameID].possessionNumber + 1
        if ishome:
            games[gameID].homeStats.possessions = games[gameID].homeStats.possessions + 1
            games[gameID].homeStats.points = games[gameID].homeStats.points + 10
            games[gameID].homeStats.goalsScored = games[gameID].homeStats.goalsScored + 1
            games[gameID].homeStats.shotAttempts = games[gameID].homeStats.shotAttempts + 1

            games[gameID].awayStats.defensiveRebounds = games[gameID].awayStats.defensiveRebounds + 1
            games[gameID].awayStats.posSaves = games[gameID].awayStats.posSaves + 1
        else:
            games[gameID].awayStats.possessions = games[gameID].awayStats.possessions + 1
            games[gameID].awayStats.points = games[gameID].awayStats.points + 10
            games[gameID].awayStats.goalsScored = games[gameID].awayStats.goalsScored + 1
            games[gameID].awayStats.shotAttempts = games[gameID].awayStats.shotAttempts + 1

            games[gameID].homeStats.defensiveRebounds = games[gameID].homeStats.defensiveRebounds + 1
            games[gameID].homeStats.posSaves = games[gameID].homeStats.posSaves + 1

        games[gameID].Possession.switch()

    elif result == Result.RETAINMISS:
        resultString = "missed their shot but retained possession."
        games[gameID].possessionNumber = games[gameID].possessionNumber + 1
        if ishome:
            games[gameID].homeStats.possessions = games[gameID].homeStats.possessions + 1
            games[gameID].homeStats.shotAttempts = games[gameID].homeStats.shotAttempts + 1
            games[gameID].homeStats.offensiveRebounds = games[gameID].homeStats.offensiveRebounds + 2

            games[gameID].awayStats.saves = games[gameID].awayStats.saves + 1
            games[gameID].awayStats.posSaves = games[gameID].awayStats.posSaves + 1
        else:
            games[gameID].awayStats.possessions = games[gameID].awayStats.possessions + 1
            games[gameID].awayStats.shotAttempts = games[gameID].awayStats.shotAttempts + 1
            games[gameID].awayStats.offensiveRebounds = games[gameID].awayStats.offensiveRebounds + 1

            games[gameID].homeStats.saves = games[gameID].homeStats.saves + 1
            games[gameID].homeStats.posSaves = games[gameID].homeStats.posSaves + 1

    elif result == Result.MISS:
        resultString = "missed their shot."
        games[gameID].possessionNumber = games[gameID].possessionNumber + 1
        if ishome:
            games[gameID].homeStats.possessions = games[gameID].homeStats.possessions + 1
            games[gameID].homeStats.shotAttempts = games[gameID].homeStats.shotAttempts + 1

            games[gameID].awayStats.defensiveRebounds = games[gameID].awayStats.defensiveRebounds + 1
            games[gameID].awayStats.saves = games[gameID].awayStats.saves + 1
            games[gameID].awayStats.posSaves = games[gameID].awayStats.posSaves + 1
        else:
            games[gameID].awayStats.possessions = games[gameID].awayStats.possessions + 1
            games[gameID].awayStats.shotAttempts = games[gameID].awayStats.shotAttempts + 1

            games[gameID].homeStats.defensiveRebounds = games[gameID].homeStats.defensiveRebounds + 1
            games[gameID].homeStats.saves = games[gameID].homeStats.saves + 1
            games[gameID].homeStats.posSaves = games[gameID].homeStats.posSaves + 1

        games[gameID].Possession.switch()

    elif result == Result.TURNOVER:
        resultString = "turned it over."
        games[gameID].possessionNumber = games[gameID].possessionNumber + 1
        if ishome:
            games[gameID].homeStats.possessions = games[gameID].homeStats.possessions + 1
            games[gameID].homeStats.turnovers = games[gameID].homeStats.turnovers + 1

        else:
            games[gameID].awayStats.possessions = games[gameID].awayStats.possessions + 1
            games[gameID].awayStats.turnovers = games[gameID].awayStats.turnovers + 1

        games[gameID].Possession.switch()

    elif result == Result.DEFENSIVESCORE:
        resultString = "turned it over and the defense scored!"
        games[gameID].possessionNumber = games[gameID].possessionNumber + 1
        if ishome:
            games[gameID].homeStats.possessions = games[gameID].homeStats.possessions + 1
            games[gameID].homeStats.posSaves = games[gameID].homeStats.posSaves + 1
            games[gameID].homeStats.turnovers = games[gameID].homeStats.turnovers + 1

            games[gameID].awayStats.points = games[gameID].awayStats.points + 10
            games[gameID].awayStats.goalsScored = games[gameID].awayStats.goalsScored + 1
            games[gameID].awayStats.shotAttempts = games[gameID].awayStats.shotAttempts + 1
            games[gameID].awayStats.defensiveRebounds = games[gameID].awayStats.defensiveRebounds + 1
        else:
            games[gameID].awayStats.possessions = games[gameID].awayStats.possessions + 1
            games[gameID].awayStats.posSaves = games[gameID].awayStats.posSaves + 1
            games[gameID].awayStats.turnovers = games[gameID].awayStats.turnovers + 1

            games[gameID].homeStats.points = games[gameID].homeStats.points + 10
            games[gameID].homeStats.goalsScored = games[gameID].homeStats.goalsScored + 1
            games[gameID].homeStats.shotAttempts = games[gameID].homeStats.shotAttempts + 1
            games[gameID].homeStats.defensiveRebounds = games[gameID].homeStats.defensiveRebounds + 1

    elif result == Result.DEFRETAIN:
        resultString = "turned it over and the defense scored *and* retained possession!"
        games[gameID].possessionNumber = games[gameID].possessionNumber + 1
        if ishome:
            games[gameID].homeStats.possessions = games[gameID].homeStats.possessions + 1
            games[gameID].homeStats.posSaves = games[gameID].homeStats.posSaves + 1
            games[gameID].homeStats.turnovers = games[gameID].homeStats.turnovers + 1

            games[gameID].awayStats.points = games[gameID].awayStats.points + 10
            games[gameID].awayStats.goalsScored = games[gameID].awayStats.goalsScored + 1
            games[gameID].awayStats.shotAttempts = games[gameID].awayStats.shotAttempts + 1
            games[gameID].awayStats.offensiveRebounds = games[gameID].awayStats.offensiveRebounds + 1
        else:
            games[gameID].awayStats.possessions = games[gameID].awayStats.possessions + 1
            games[gameID].awayStats.posSaves = games[gameID].awayStats.posSaves + 1
            games[gameID].awayStats.turnovers = games[gameID].awayStats.turnovers + 1

            games[gameID].homeStats.points = games[gameID].homeStats.points + 10
            games[gameID].homeStats.goalsScored = games[gameID].homeStats.goalsScored + 1
            games[gameID].homeStats.shotAttempts = games[gameID].homeStats.shotAttempts + 1
            games[gameID].homeStats.offensiveRebounds = games[gameID].homeStats.offensiveRebounds + 1

        games[gameID].Possession.switch()

    elif result == Result.TRIPLEDEF:
        resultString = "turned it over and the defense scored *three* times!"
        games[gameID].possessionNumber = games[gameID].possessionNumber + 1
        if ishome:
            games[gameID].homeStats.possessions = games[gameID].homeStats.possessions + 1
            games[gameID].homeStats.posSaves = games[gameID].homeStats.posSaves + 3
            games[gameID].homeStats.turnovers = games[gameID].homeStats.turnovers + 1
            games[gameID].homeStats.defensiveRebounds = games[gameID].homeStats.defensiveRebounds + 1

            games[gameID].awayStats.points = games[gameID].awayStats.points + 30
            games[gameID].awayStats.goalsScored = games[gameID].awayStats.goalsScored + 3
            games[gameID].awayStats.shotAttempts = games[gameID].awayStats.shotAttempts + 3
            games[gameID].awayStats.offensiveRebounds = games[gameID].awayStats.offensiveRebounds + 2
        else:
            games[gameID].awayStats.possessions = games[gameID].awayStats.possessions + 1
            games[gameID].awayStats.posSaves = games[gameID].awayStats.posSaves + 3
            games[gameID].awayStats.turnovers = games[gameID].awayStats.turnovers + 1
            games[gameID].awayStats.defensiveRebounds = games[gameID].awayStats.defensiveRebounds + 1

            games[gameID].homeStats.points = games[gameID].homeStats.points + 30
            games[gameID].homeStats.goalsScored = games[gameID].homeStats.goalsScored + 3
            games[gameID].homeStats.shotAttempts = games[gameID].homeStats.shotAttempts + 3
            games[gameID].homeStats.offensiveRebounds = games[gameID].homeStats.offensiveRebounds + 2


    defenseName = None
    if wiki.teams[offenseID].name == wiki.teams[games[gameID].homeID].name:
        defenseName = wiki.teams[games[gameID].awayID].name
    else:
        defenseName = wiki.teams[games[gameID].homeID].name

    snitchNum = random.randint(1, games[gameID].getSnitchMax())
    oSnitch = games[gameID].offenseSnitchNumber
    dSnitch = games[gameID].defenseSnitchNumber
    snitchString = """"""

    if not oSnitch == dSnitch:
        if oSnitch == snitchNum:
            games[gameID].snitchCaught = True
            snitchString = """
**{} CAUGHT THE SNITCH**!
""".format(wiki.teams[offenseID].name.upper())
            if ishome:
                games[gameID].homeStats.snitchCaught = True
                games[gameID].homeStats.points = games[gameID].homeStats.points + 30
            else:
                games[gameID].awayStats.snitchCaught = True
                games[gameID].awayStats.points = games[gameID].awayStats.points + 30

        elif dSnitch == snitchNum:
            games[gameID].snitchCaught = True
            snitchString = """
**{} CAUGHT THE SNITCH!**
""".format(defenseName.upper())
            if ishome:
                games[gameID].awayStats.snitchCaught = True
                games[gameID].awayStats.points = games[gameID].awayStats.points + 30
            else:
                games[gameID].homeStats.snitchCaught = True
                games[gameID].homeStats.points = games[gameID].homeStats.points + 30

        if games[gameID].snitchCaught:
            if games[gameID].homeStats.points > games[gameID].awayStats.points:
                games[gameID].winner = wiki.teams[games[gameID].homeID].name
            elif games[gameID].homeStats.points < games[gameID].awayStats.points:
                games[gameID].winner = wiki.teams[games[gameID].awayID].name
            else:
                games[gameID].duel = True
                snitchString = snitchString + "\nThe match is now tied and will be determined by a duel!"

    message = buildMessage(gameID, wiki.teams[offenseID].emoji, wiki.teams[offenseID].name, defenseName,
                           resultString, difference, snitchNum, snitchString)
    games[gameID].clearNumbers()
    games[gameID].getSnitchMax()
    games[gameID].waitHome = True
    games[gameID].waitAway = True

    return message


def getQuaffleResult(gameID):
    homeNum = games[gameID].offenseNumber
    awayNum = games[gameID].defenseNumber
    quaffleNum = random.randint(1, 1000)
    homedif = getNumDif(homeNum, quaffleNum)
    awayDif = getNumDif(awayNum, quaffleNum)

    tossWinner = None
    if homedif < awayDif:
        tossWinner = wiki.teams[games[gameID].homeID].name
        games[gameID].Possession.set(True)

    else:
        tossWinner = wiki.teams[games[gameID].awayID].name
        games[gameID].Possession.set(False)

    resultString = """{} wins the toss! Both coaches must submit a number for the next possession.
    
    {}: {}
    {}: {}
    Toss Number: {}
    """.format(tossWinner, wiki.teams[games[gameID].homeID].name, homeNum, wiki.teams[games[gameID].awayID].name, awayNum, quaffleNum)

    games[gameID].clearNumbers()
    games[gameID].getSnitchMax()
    games[gameID].waitHome = True
    games[gameID].waitAway = True

    return resultString


def getDuelResult(gameID):
    homeNum = games[gameID].offenseNumber
    awayNum = games[gameID].defenseNumber
    duelNum = random.randint(1, 1000)
    homedif = getNumDif(homeNum, duelNum)
    awayDif = getNumDif(awayNum, duelNum)

    tossWinner = None
    if homedif < awayDif:
        tossWinner = wiki.teams[games[gameID].homeID].name
        games[gameID].Possession.set(True)
        games[gameID].homeStats.points = games[gameID].homeStats.points + 10
        games[gameID].homeStats.wonDuel = True
        games[gameID].winner = wiki.teams[games[gameID].homeID].name
    else:
        tossWinner = wiki.teams[games[gameID].awayID].name
        games[gameID].Possession.set(False)
        games[gameID].awayStats.points = games[gameID].awayStats.points + 10
        games[gameID].awayStats.wonDuel = True
        games[gameID].winner = wiki.teams[games[gameID].awayID].name

    resultString = """{} wins the duel!

    {}: {}
    {}: {}
    Duel Number: {}
    """.format(tossWinner, wiki.teams[games[gameID].homeID].name, homeNum, wiki.teams[games[gameID].awayID].name,
               awayNum, duelNum)

    return resultString


def buildMessage(gameID, emoji, offenseName, defenseName, result, difference, snitchNum, snitchString):
    homeName = wiki.teams[games[gameID].homeID].name
    awayName = wiki.teams[games[gameID].awayID].name
    homePoints = games[gameID].homeStats.points
    awayPoints = games[gameID].awayStats.points

    msg = """
-------------------
**POSSESSION #{}**
{} {} {}

Offense: {}
Defense: {}
Difference: {}

{} Snitch: {}
{} Snitch: {}
Snitch Number: **{}**

SCORE:
{}: {}
{}: {}
{}-------------------""".format(games[gameID].possessionNumber-1, emoji, offenseName, result,
                                  games[gameID].offenseNumber, games[gameID].defenseNumber, difference, offenseName,
                                  games[gameID].offenseSnitchNumber, defenseName, games[gameID].defenseSnitchNumber,
                                  snitchNum, homeName, homePoints, awayName, awayPoints, snitchString)

    return msg


def printFinal(gameID):
    winner = games[gameID].winner
    winnerPoints = None
    winnerSnitch = ""
    loserPoints = None
    loser = None
    loserSnitch = ""
    if wiki.teams[games[gameID].homeID].name == winner:
        loser = wiki.teams[games[gameID].awayID].name
        loserPoints = games[gameID].awayStats.points
        winnerPoints = games[gameID].homeStats.points
        if games[gameID].awayStats.snitchCaught:
            loserSnitch = "s"
        else:
            winnerSnitch = "s"


    else:
        loser = wiki.teams[games[gameID].homeID].name
        loserPoints = games[gameID].homeStats.points
        winnerPoints = games[gameID].awayStats.points
        if games[gameID].homeStats.snitchCaught:
            loserSnitch = "s"
        else:
            winnerSnitch = "s"

    homeStats = games[gameID].homeStats
    awayStats = games[gameID].awayStats

    duelString = ""
    if homeStats.wonDuel or awayStats.wonDuel:
        duelString = "/D"
    fScoreMsg = "{} defeats {} {}{}-{}{}{} ({})".format(winner, loser, winnerPoints, winnerSnitch, loserPoints,
                                                        loserSnitch, duelString, games[gameID].possessionNumber)

    msg = """**FINAL:** {} defeats {} {}{}-{}{}{} ({})

Stats:
*{}:*
Poessessions: {}
Shooting: {}/{}
Saves: {}/{}
OR/DR: {}/{}
Turnovers: {}

*{}:*
Poessessions: {}
Shooting: {}/{}
Saves: {}/{}
OR/DR: {}/{}
Turnovers: {}


""".format(winner, loser, winnerPoints, winnerSnitch, loserPoints, loserSnitch, duelString, games[gameID].possessionNumber,
           wiki.teams[games[gameID].homeID].name, homeStats.possessions, homeStats.goalsScored, homeStats.shotAttempts,
           homeStats.saves, homeStats.posSaves, homeStats.offensiveRebounds, homeStats.defensiveRebounds,
           homeStats.turnovers, wiki.teams[games[gameID].awayID].name, awayStats.possessions, awayStats.goalsScored,
           awayStats.shotAttempts, awayStats.saves, awayStats.posSaves, awayStats.offensiveRebounds,
           awayStats.defensiveRebounds, awayStats.turnovers)

    return msg, fScoreMsg


"""
def printLog():
"""