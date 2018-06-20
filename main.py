import discord
import wiki
import utils

# NEED TO AD
# GameLog
# customStart

SERVERID = '433101832089501696'

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    # Basic Commands
    if message.content.startswith('!hello'):
        print("Command: !hello")
        msg = 'Hello {}'.format(message.author.mention)
        await client.send_message(message.channel, msg)

    elif message.content.startswith('!henlo'):
        print("Command: !henlo")
        msg = 'Henlo {}'.format(message.author.mention)
        await client.send_message(message.channel, msg)

    elif message.content.lower().startswith('best team'):
        print("Command: Best Team by {}".format(str(message.author)))
        await client.send_message(message.channel, "Horton! They have never lost and won the previous championship!")

    elif message.content.lower().startswith('choke'):
        print("Command: Choke {}".format(str(message.author)))
        await client.send_message(message.channel, "A choke a day keeps the rankings away")

    elif message.content.lower().startswith('cookie'):
        print("Command: Cookie by {}".format(str(message.author)))
        await client.send_message(message.channel, ":cookie:")

    elif message.content.lower().startswith('worst team'):
        print("Command: Worst Team by {}".format(str(message.author)))
        await client.send_message(message.channel, "Well, last year it was Mofa but their head coach left to Illvermorny. Therefore, we can assume Illvermorny is the worst team.")

    elif "loona" in message.content.lower() or "k-pop" in message.content.lower():
        print("Command: LOONASUX by {}".format(str(message.author)))
        await client.send_message(message.channel, "Every Other Genre > K-Pop")

    #Team Commands
    elif message.content.lower().startswith('!koldovstoretz') or message.content.lower().startswith('!kol'):
        print("Command: Kol by {}".format(str(message.author)))
        await client.send_message(message.channel, "Koldovstoretzmory Go!")


    # Start Game
    elif message.content.lower().startswith('start game') and str(message.author) in wiki.admins:
        print("Starting Game")
        home, away = utils.startGame(message.content.lower(), message.channel)
        await client.send_message(message.channel, "Started Game")
        homeMention = client.get_server(SERVERID).get_member_named(home).mention
        awayMention = client.get_server(SERVERID).get_member_named(away).mention
        await client.send_message(message.channel,
                                  "Submit your number for the Quaffle Toss! \n{} {}".format(homeMention,
                                                                                            awayMention))
        await client.send_message(client.get_server(SERVERID).get_member_named(home),
                                  "Submit your number for the Quaffle Toss (1-1000).")
        await client.send_message(client.get_server(SERVERID).get_member_named(away),
                                  "Submit your number for the Quaffle Toss (1-1000).")

    elif message.content.lower().startswith('stat start game') and str(message.author) in wiki.admins:
        print("Starting Game with Custom Start")
        utils.startGame(client, message.content.lower(), message.channel, True)
        await client.send_message(message.channel, "Started Game")

    elif message.content.lower().startswith('abandon game') and str(message.author) in wiki.admins:
        print("Abandoning Game")
        utils.abandonGame(message)
        await client.send_message(message.channel, "Abandoned Game")

    # Process Message
    elif message.server is None:
        success, reply, gameID = utils.processMessage(message)

        if success:
            print("Sent Confirmation Message")
            await client.send_message(message.channel, reply)

            if not utils.games[gameID].waitHome and not utils.games[gameID].waitAway:
                reply = None
                print("Game Ready for Result")
                if utils.games[gameID].quaffleToss:
                    reply = utils.getQuaffleResult(gameID)
                    await client.send_message(utils.games[gameID].mainChannel, reply)
                elif utils.games[gameID].duel:
                    reply = utils.getDuelResult(gameID)
                    await client.send_message(utils.games[gameID].mainChannel, reply)
                else:
                    reply = utils.getResult(gameID)
                    await client.send_message(utils.games[gameID].mainChannel, reply)

                utils.games[gameID].quaffleToss = False

                if utils.games[gameID].winner is None:
                    home = wiki.teams[utils.games[gameID].homeID].coach
                    away = wiki.teams[utils.games[gameID].awayID].coach
                    if utils.games[gameID].Possession.homePos:
                        await client.send_message(client.get_server(SERVERID).get_member_named(home),
                                                  reply + "\n\nSubmit your **offensive** number (1-1000) and snitch number (1-{}).".format(
                                                utils.games[gameID].getSnitchMax()))
                        await client.send_message(client.get_server(SERVERID).get_member_named(away),
                                                  reply + "\n\nSubmit your **defensive** number (1-1000) and snitch number (1-{}).".format(
                                                utils.games[gameID].getSnitchMax()))
                    else:
                        await client.send_message(client.get_server(SERVERID).get_member_named(away),
                                                  reply + "\n\nSubmit your **offensive** number (1-1000) and snitch number (1-{}).".format(
                                                utils.games[gameID].getSnitchMax()))
                        await client.send_message(client.get_server(SERVERID).get_member_named(home),
                                                  reply + "\n\nSubmit your **defensive** number (1-1000) and snitch number (1-{}).".format(
                                                utils.games[gameID].getSnitchMax()))

                else:
                    reply, fscoreMsg = utils.printFinal(gameID)
                    homeMention = client.get_server(SERVERID).get_member_named(wiki.teams[utils.games[gameID].homeID].coach)
                    awayMention = client.get_server(SERVERID).get_member_named(
                        wiki.teams[utils.games[gameID].awayID].coach)

                    await client.send_message(client.get_channel('458363196735094784'), reply)
                    await client.send_message(client.get_channel('435918596611506186'), fscoreMsg)
                    reply = reply + homeMention.mention + " " + awayMention.mention
                    await client.send_message(utils.games[gameID].mainChannel, reply)

        else:
            print("Processing Error in Game {}".format(gameID))
            await client.send_message(message.channel, reply)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')




wiki.loadPages()

client.run([REDACTED])
