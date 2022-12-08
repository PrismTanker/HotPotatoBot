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

#TODO add bot to emergency backup server and provide better emoji
ACCEPT_EMOJI = '<:hotpotatyes:1050319143095783434>'
REJECT_EMOJI = '<:hotpotatno:1050319139853565992>'

IMAGE_FILE = 'images.txt'
DEFAULT_FILE = 'defaults.txt'
IMMUNE_FILE = 'immune.txt'
ADMIN_FILE = 'admins.txt'


potato_images = Hotloader(IMAGE_FILE, REFRESH_DELAY)

#keys double as list of valid channels
default_users = Hotloader(DEFAULT_FILE, REFRESH_DELAY, lambda x: 
        {int(pair[0]): int(pair[1]) for pair in [s.split() for s in x]}
        )

immune_ids = Hotloader(IMMUNE_FILE, REFRESH_DELAY, lambda x: 
        set([int(i) for i in x])
        )

admins = Hotloader(ADMIN_FILE, REFRESH_DELAY, lambda x:
        set([int(i) for i in x])
)

#Doubles to count active games by existence, will also stash default on game start
currentVictims = {} 

#Active image request messages
active_requests = set()

roboticus = discord.Bot(intents= discord.Intents.all())



@roboticus.event
async def on_ready():
    print(f"{roboticus.user} is ready and online!")
    

@roboticus.event
async def on_message(msg):
    #TODO Comment this one
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

@roboticus.slash_command(name = "refresh", description = "Force parameter refresh")
async def refresh_all(ctx):
    global potato_images
    global default_users
    global immune_ids
    global admins

    if ctx.author.id in admins.get():
        await ctx.respond("Ugh, Fiiiiiiiine")
        for loader in (potato_images, default_users, immune_ids, admins):
            loader.update()
    else:
        await ctx.respond("You're not my dad!")

@roboticus.slash_command(name = "submit_image", description = "submit a URL to a potato image to be added to the image pool (Reviewed by a hooman)")
async def submit_image(ctx, image_link: discord.Option(str)): 

    moderator = await roboticus.fetch_user(random.choice(tuple(admins.get())))#its a one off niche, admins being a set makes sense everywhere else fucking bite me

    #Embed with the specific submission information, allows easy retrieval later
    emb = discord.Embed(title = 'Image Submission', color = 0x00ff00)
    emb.add_field(name = 'User', value = ctx.author, inline = True)
    emb.add_field(name = 'User_ID', value = ctx.author.id, inline = True)
    emb.add_field(name = 'Server', value = ctx.guild, inline = False)
    emb.add_field(name = 'Submission', value = image_link, inline = False)
    emb.set_image(url = image_link) #test as if the image will embed correctly from link
    
    #If the given link isn't a url then discord will hissy fit trying to embed
    try:
        moderation_message = await moderator.send(embed = emb)
    except discord.errors.HTTPException as e:
        await ctx.respond("Look Buckaroo, I don't have time for shitpost requests that aren\'t even links. You could be spending your time far more wisely, like prank calling the european space agency")
        return

    await ctx.respond("I'll ask my boss")

    active_requests.add(moderation_message)
    for emo in [ACCEPT_EMOJI, REJECT_EMOJI]:
        #react with emoji for decision
        await moderation_message.add_reaction(emo) 

@roboticus.event
async def on_reaction_add(reaction, user):
    if user.id == BOT_ID:
        return

    mess = reaction.message
    if mess in active_requests: #Check if message is a submission confirmation message
        request_info = mess.embeds[0].fields
        requestor = await roboticus.fetch_user(request_info[1].value)
        new_image_link = request_info[3].value
        
        if str(reaction.emoji) == ACCEPT_EMOJI:
            await requestor.send("I had a look at your image submission ({}). \n I found it to be, as the kids say, exceedingly 'pog champion' and added it to my collection".format(new_image_link))
            #Save new link to pool to be updated in hotloader later
            with open(IMAGE_FILE, 'a') as f:
                f.write('\n' + new_image_link)

        if str(reaction.emoji) == REJECT_EMOJI:
            await requestor.send("I asked my employer about your image submission ({}). \n They told me, and I quote: \"No.\" \n Ensure your submissions are valid links to images of potatos, such that discord will auto-embed the image into a message that includes them".format(new_image_link))

        await mess.delete()
        active_requests.remove(mess)
        


roboticus.run(TOKEN)

