import discord
import asyncio
import random

TOKEN = "OTM0Njg2ODA0MDkzODQ5NjYx.GAaf_W.fYTAvzV_8qK4mQSJpHyDPrCzCUGIhHkImwYQjI"

BOT_ID = 934686804093849661

SCORPIO = 407815751454425088
PRISM = 492869347698671618

POTATO_IMAGE_URLS = ["https://media.discordapp.net/attachments/1001718360825921616/1002171863025328138/unknown.png",
    "https://i.imgur.com/3ik5tXG.png",
    "https://i.imgur.com/xZmkowH.jpeg",
    "https://i.imgur.com/AYjFiwb.jpeg",
    "https://i.imgur.com/1DIl775.jpeg",
    "https://i.imgur.com/FKWWBXz.jpeg",
    "https://i.imgur.com/SvUauEO.jpeg",
    "https://i.imgur.com/g9julEy.jpeg",
    "https://i.imgur.com/nJKpzVp.png",
    "https://i.imgur.com/1eFtIHy.jpeg",
    "https://i.imgur.com/TwH2N8D.jpeg",
    "https://i.imgur.com/ZVKY4yK.jpeg",
    "https://i.imgur.com/FdecYCl.jpeg",
    "https://i.imgur.com/bEcV612.jpeg"]

default_users = {1001718360825921616: SCORPIO, 1004713311885066240: 253841151851888640}
immune_ids = set([BOT_ID,155149108183695360,471091072546766849,697107653821726730,184405311681986560,356065937318871041,510016054391734273])

gamesStarted = {chan: False for chan in default_users}
currentVictims = {chan: None for chan in default_users}

roboticus = discord.Bot(intents= discord.Intents.all())


@roboticus.event
async def on_ready():
    print(f"{roboticus.user} is ready and online!")
    

@roboticus.event
async def on_message(msg):
    global gamesStarted
    global currentVictims

    chan = msg.channel.id
    if chan in default_users:#Keys for defaults are valid channels
        if gamesStarted[chan] == True:
            if msg.author.id == currentVictims[chan]: 
                pings = msg.mentions
                newVictim = None
                try:
                    newVictim = pings[0].id
                    if newVictim in immune_ids:
                        newVictim = default_users[chan]
                        if msg.author.id == default_users[chan]:
                            await msg.channel.send("They have an analogous gun to my head, fuck that, ping someone else")
                    currentVictims[chan] = newVictim
                
                except IndexError:
                    await msg.channel.send("You aren't getting off the hook that easily smartass")


@roboticus.slash_command(name = "pingscorpio", description = "Exactly what it says on the tin")
async def pingScorpio(ctx):
    await ctx.respond("Yo <@"+str(SCORPIO)+">,  <@"+ str(ctx.author.id) +"> craves your attention")


@roboticus.slash_command(name = "start", description = "Begin hot potato, no there is no stop")
async def start_game(ctx, seconds_between_pings: discord.Option(int)):
    global gamesStarted
    global currentVictims
    
    chan = ctx.channel.id
    
    if (chan in default_users):
        if gamesStarted[chan]:
            await ctx.respond("If you hadn't already noticed we have already started")
        else:
            gamesStarted[chan] = True
            currentVictims[chan] = ctx.author.id
            await ctx.respond("Beginning Hot Potato!")
            while True:
                await ctx.channel.send("<@" + str(currentVictims[chan]) +">, You are the hot potato, ping someone here to pass it on! " + random.choice(POTATO_IMAGE_URLS))
                await asyncio.sleep(seconds_between_pings)
                if not gamesStarted[chan]: #haha funny asynchronous bullshit
                    break
    
    else:
        await ctx.respond("This isn't my channel?!")

@roboticus.slash_command(name = "stop", description = "a command that will be ignored")
async def stop_game(ctx):
    global gamesStarted
    
    chan = ctx.channel.id
    if (chan in default_users):
        if not gamesStarted[chan]:
            await ctx.respond("I'm not even doing anything")
        else:
            if chan in default_users:
                if ctx.author.id == currentVictims[chan]:
                    await ctx.respond("Don't be a spoil sport, pass the potato first!")
                else:
                    gamesStarted[chan] = False
                    await ctx.respond("Cringe")
        
    else:
        await ctx.respond("This isn't my channel?!")


roboticus.run(TOKEN)

