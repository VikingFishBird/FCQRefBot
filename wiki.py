from classes import Result
from classes import PlayStyleType
from classes import Team

rangeString = """aggressive|aggressive|0-28,triplescore|29-112,retainscore|113-280,score|281-334,retainmiss|335-394,miss|395-430,turnover|431-472,defensivescore|473-493,defretain|494-500,tripledef
aggressive|balanced|0-24,triplescore|25-96,retainscore|96-240,score|241-312,retainmiss|313-392,miss|393-440,turnover|441-476,defensivescore|477-494,defretain|495-500,tripledef
aggressive|defensive|0-20,triplescore|21-80,retainscore|81-200,score|201-290,retainmiss|291-390,miss|391-450,turnover|451-480,defensivescore|481-495,defretain|496-500,tripledef
balanced|aggressive|0-24,triplescore|25-96,retainscore|96-240,score|241-312,retainmiss|313-392,miss|393-440,turnover|441-476,defensivescore|477-494,defretain|495-500,tripledef
balanced|balanced|0-20,triplescore|21-80,retainscore|81-200,score|201-290,retainmiss|291-390,miss|391-450,turnover|451-480,defensivescore|481-495,defretain|496-500,tripledef
balanced|defensive|0-16,triplescore|17-64,retainscore|65-160,score|161-268,retainmiss|269-388,miss|389-460,turnover|461-484,defensivescore|485-496,defretain|497-500,tripledef
defensive|aggressive|0-20,triplescore|21-80,retainscore|81-200,score|201-290,retainmiss|291-390,miss|391-450,turnover|451-480,defensivescore|481-495,defretain|496-500,tripledef
defensive|balanced|0-16,triplescore|17-64,retainscore|65-160,score|161-268,retainmiss|269-388,miss|389-460,turnover|461-484,defensivescore|485-496,defretain|497-500,tripledef
defensive|defensive|0-12,triplescore|13-48,retainscore|49-120,score|121-246,retainmiss|247-386,miss|387-470,turnover|471-488,defensivescore|489-497,defretain|498-500,tripledef"""
teamString = """Horton|VikingFishBird#8715|aggressive|:flag_ca:
Beauxbatons|Kurt Anger#7171|balanced|:flag_fr:
Ilvermorny|byu#9318|aggressive|:flag_us:
Koldovstoretz|YellowSkarmory#7549|aggressive|:flag_ru: 
Hogwarts|A.Ham#4965|defensive|:flag_gb:
Mahoutokoro|Max#6067|balanced|:flag_ja: 
Uluru|deghlanj#6615|defensive|:flag_au: 
Castelobruxo|Babatunde Oladotun#6470|aggressive|:flag_br: 
Uagadou|сука блять!#9884|aggressive|:flag_ug: 
Durmstrang|amesker#3310|aggressive|:flag_no:
Mofa|HorribelSpelling#6152|defensive|:flag_cn:"""
adminString = """byu#9318
VikingFishBird#8715
A.Ham#4965"""

teams = []
admins = []
ranges = {}


def loadPages():
    print("Loading Pages")
    loadTeams()
    loadAdmins()
    loadRanges()


def loadAdmins():
    global admins
    admins = adminString.splitlines()


def loadTeams():
    global teams
    teams = []
    teamLines = teamString.splitlines()
    for x in range(teamLines.__len__()):
        items = teamLines[x].split('|')
        style = parseStyle(items[2])
        name = items[0]
        coach = items[1]
        emoji = items[3]

        teams.append(Team())
        teams[-1].name = name
        teams[-1].coach = coach
        teams[-1].playStyle = style
        teams[-1].emoji = emoji


def loadRanges():
    global ranges
    ranges = {}

    ranges[PlayStyleType.AGGRESSIVE] = {}
    ranges[PlayStyleType.BALANCED] = {}
    ranges[PlayStyleType.DEFENSIVE] = {}
    for rangeLines in rangeString.splitlines():
        items = rangeLines.split('|')

        offense = parseStyle(items[0])
        if offense is None:
            print("WARNING: Bad offense item: {}".format(items[0]))
            continue

        defense = parseStyle(items[1])
        if defense is None:
            print("WARNING: Bad offense item: {}".format(items[1]))
            continue

        playParts = {}
        for x in range(items.__len__()):
            if x < 2:
                continue

            play, result = parsePlayPart(items[x])
            if result is None:
                continue
            playParts[play] = result

        ranges[offense][defense] = playParts


def parsePlayPart(playPart):
    parts = playPart.split(',')
    range = parts[0]

    if parts.__len__() < 2:
        return None, None

    result = parseResult(parts[1])

    return range, result


def parseStyle(styleString):
    styleString = styleString.lower()
    if "aggressive" in styleString:
        return PlayStyleType.AGGRESSIVE
    elif "balanced" in styleString:
        return PlayStyleType.BALANCED
    elif "defensive" in styleString:
        return PlayStyleType.DEFENSIVE


def parseResult(resultstring):
    resultstring = resultstring.lower()
    if resultstring == "triplescore":
        return Result.TRIPLESCORE
    elif resultstring == "retainscore":
        return Result.RETAINSCORE
    elif resultstring == "score":
        return Result.SCORE
    elif resultstring == "retainmiss":
        return Result.RETAINMISS
    elif resultstring == "miss":
        return Result.MISS
    elif resultstring == "turnover":
        return Result.TURNOVER
    elif resultstring == "defensivescore":
        return Result.DEFENSIVESCORE
    elif resultstring == "defretain":
        return Result.DEFRETAIN
    elif resultstring == "tripledef":
        return Result.TRIPLEDEF
    else:
        return None
