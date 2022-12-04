import discord
import asyncio
import random
from hotloader import Hotloader

with open('token.txt') as f:
    TOKEN = f.readline()

BOT_ID = 934686804093849661
SCORPIO = 407815751454425088
PRISM = 492869347698671618

REFRESH_DELAY = 86400 #1 day

potato_images = Hotloader('images.txt', REFRESH_DELAY)

#keys double as list of valid channels
default_users = Hotloader('defaults.txt', REFRESH_DELAY, lambda x: 
        {int(pair[0]): int(pair[1]) for pair in [s.split() for s in x]}
        )

immune_ids = Hotloader('immune.txt', REFRESH_DELAY, lambda x: 
        set([int(i) for i in x])
        )

#Doubles to count active games by existence, will also stash default on game start
currentVictims = {} 


roboticus = discord.Bot(intents= discord.Intents.all())


@roboticus.event
async def on_ready():
    print(f"{roboticus.user} is ready and online!")
    

@roboticus.event
async def on_message(msg):
    global currentVictims

    chan = msg.channel.id
    if chan in currentVictims:
        if msg.author.id == currentVictims[chan][0]: 
            pings = msg.mentions
            newVictim = None
            try:
                newVictim = pings[0].id
                if newVictim in immune_ids.get():
                    newVictim = currentVictims[chan][1]
                    if msg.author.id == currentVictims[chan][1]:
                        await msg.channel.send("They know where I live, fuck that, ping someone else")
                currentVictims[chan] = (newVictim,currentVictims[chan][1])
            
            except IndexError:
                await msg.channel.send("You aren't getting off the hook that easily smartass")


@roboticus.slash_command(name = "pingscorpio", description = "Exactly what it says on the tin")
async def pingScorpio(ctx):
    await ctx.respond("Yo <@"+str(SCORPIO)+">,  <@"+ str(ctx.author.id) +"> craves your attention")


@roboticus.slash_command(name = "start", description = "Begin hot potato, no there is no stop")
async def start_game(ctx, seconds_between_pings: discord.Option(int)):
    global currentVictims
    
    #we cache the cache as the hotloader contents are volitile
    default_user_cache = default_users.get().copy()
    
    chan = ctx.channel.id
    
    if (chan in default_user_cache):
        if chan in currentVictims:
            await ctx.respond("If you hadn't already noticed we have already started")
        else:
            currentVictims[chan] = (ctx.author.id, default_user_cache[chan])
            await ctx.respond("Beginning Hot Potato!")
            while True:
                await ctx.channel.send("<@" + str(currentVictims[chan][0]) +">, You are the hot potato, ping someone here to pass it on! " + random.choice(potato_images.get()))
                await asyncio.sleep(seconds_between_pings)
                if not chan in currentVictims: #haha funny asynchronous bullshit
                    break
    
    else:
        await ctx.respond("This isn't my channel?!")

@roboticus.slash_command(name = "stop", description = "a command that will be ignored")
async def stop_game(ctx):
    global currentVictims
    
    chan = ctx.channel.id

    if chan in currentVictims:
        if ctx.author.id == currentVictims[chan][0]:
            await ctx.respond("Don't be a spoil sport, pass the potato first!")
        else:
            currentVictims.pop(chan)
            await ctx.respond("Cringe")

    else:
        if (chan in currentVictims[chan][1]):
            await ctx.respond("I'm not even doing anything")  
        else:
            await ctx.respond("This isn't my channel?!")


roboticus.run(TOKEN)

