import discord
from discord.ext import commands
import asyncio
import random
from hotloader import Hotloader
from thestringsarelongandiamsad import *

#I'll encrypt this at some point I swear
with open('token.txt') as f:
    TOKEN = f.readline()

BOT_ID = 934686804093849661

# For testing
# SCORPIO = 407815751454425088 
# PRISM = 492869347698671618

REFRESH_DELAY = 86400 #1 day

#TODO better emoji
ACCEPT_EMOJI = '<:hotpotatyes:1050319143095783434>'
REJECT_EMOJI = '<:hotpotatno:1050319139853565992>'

IMAGE_FILE = 'images.txt'
IMMUNE_FILE = 'immune.txt'
CHANNELS_FILE = 'channels.txt'
ADMIN_FILE = 'admins.txt'

RAND_PING_WAIT_MIN = 10
RAND_PING_WAIT_MAX = 604800 #one week

#TODO docstrings and typehints
class HotPotatoGame(commands.Cog):
    def __init__(
            self, 
            client: commands.Bot, 
            potato_images: Hotloader, 
            game_channels: Hotloader, 
            immune_list: Hotloader, 
            admin_list: Hotloader
    ) -> None:
        super().__init__()
        self._client = client
        self._potato_images = potato_images
        self._channels = game_channels
        self._immune_ids = immune_list
        self._admins = admin_list

        #Active games
        self._currentVictims = {} 

        #Active image request messages
        self._active_requests = set()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Hot Potato Game Cog Loaded and Ready")

    @commands.Cog.listener()
    async def on_message(self, msg):
        #Gameplay
        chan = msg.channel.id
        if chan in self._currentVictims:
            if msg.author.id == self._currentVictims[chan]: 
                pings = msg.mentions

                
                if len(pings) == 0:
                    await msg.channel.send(NO_PING)

                else:
                    #Find first undefended target
                    newVictim = None
                    for potentialVictim in pings:
                        if potentialVictim.bot or potentialVictim.id in self._immune_ids.get():
                            continue
                        else:
                            newVictim = potentialVictim
                            break                  
 
                    if newVictim == None:
                        await msg.channel.send(IMMUNE_PING)
                    else:
                        #asynch bullshit
                        self._currentVictims[chan] = newVictim.id 

                      

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.id == BOT_ID:
            return
        
        # Image submission response
        mess = reaction.message
        if mess in self._active_requests: #Check if submission confirmation message
            request_info = mess.embeds[0].fields
            requestor = await self._client.fetch_user(request_info[1].value)
            new_image_link = request_info[3].value
            
            if str(reaction.emoji) == ACCEPT_EMOJI:
                await requestor.send(IMAGE_APPROVED.format(new_image_link))
                #Save new link to pool to be updated in hotloader later
                with open(self._potato_images.source, 'a') as f:
                    f.write('\n' + new_image_link)

            if str(reaction.emoji) == REJECT_EMOJI:
                await requestor.send(IMAGE_DENIED.format(new_image_link))

            await mess.delete()
            self._active_requests.remove(mess)

    @discord.slash_command(
                name = "start", 
                description = "Begin hot potato, you know you want to"
    )
    async def start_game(self, ctx, seconds_between_pings: discord.Option(int)):                        
        chan = ctx.channel.id
        
        #Remember HotLoader contents are volitile when working with this
        if (chan in self._channels.get()):
            if chan in self._currentVictims:
                await ctx.respond(ALREADY_STARTED)
            else:
                self._currentVictims[chan] = ctx.author.id
                await ctx.respond(START_GAME)

                #Game loop
                while True:
                    await ctx.channel.send(
                            GAME_PROMPT.format(
                                str(self._currentVictims[chan]), 
                                random.choice(self._potato_images.get())
                            )
                    )
                    await asyncio.sleep(seconds_between_pings)
                    
                    #Game end condition, jank asynchronous bullshit
                    if not chan in self._currentVictims:
                        break
        
        else:
            await ctx.respond(INVALID_CHANNEL)


    @discord.slash_command(
            name = "stop", 
            description = "Publically demonstrate that you are cringe"
    )
    async def stop_game(self, ctx):            
        chan = ctx.channel.id

        if chan in self._currentVictims:
            if ((ctx.author.id == self._currentVictims[chan]) and 
                    (ctx.author.id not in self._admins.get())):
                await ctx.respond(VICTIM_STOP)
            else:
                #will break game loop hosted in start_game
                self._currentVictims.pop(chan) 
                await ctx.respond(STOP_GAME)

        else:
            await ctx.respond(INVALID_STOP)

    @discord.slash_command(
            name = "submit_image", 
            description = "submit a URL to potato image pool (Reviewed by a hooman)"
    )
    async def submit_image(self, ctx, image_link: discord.Option(str)):
        await ctx.respond(IMAGE_SUBMISSION_RESPONSE)

        #fucking bite me
        moderator = await self._client.fetch_user(random.choice(tuple(self._admins.get())))
        
        #Cleanse input strings (blank lines in file would be read + we desire embed)
        image_link = image_link.rstrip('\n').strip()

        #Embed with the specific submission information, allows easy retrieval later
        emb = discord.Embed(title = 'Image Submission', color = 0x00ff00)
        emb.add_field(name = 'User', value = ctx.author, inline = True)
        emb.add_field(name = 'User_ID', value = ctx.author.id, inline = True)
        emb.add_field(name = 'Server', value = ctx.guild, inline = False)
        emb.add_field(name = 'Submission', value = image_link, inline = False)
        emb.set_image(url = image_link) #shows if image will embed correctly
        
        #If url isn't a valid embed then discord will hissy fit
        try:
            moderation_message = await moderator.send(embed = emb)
        except discord.errors.HTTPException as e:
            await ctx.respond(EPIC_EMBED_FAILURE_LAUGH_AT_THIS_USER)
            return

        await ctx.respond(IMAGE_SUBMISSION)

        self._active_requests.add(moderation_message)
        for emo in [ACCEPT_EMOJI, REJECT_EMOJI]:
            #react with emoji for decision
            await moderation_message.add_reaction(emo) 

class PotatoAdmin(commands.Cog):
    def __init__(
            self, 
            client: commands.Bot, 
            admin_list: Hotloader,
            potato_images: Hotloader, 
            game_channels: Hotloader, 
            immune_list: Hotloader 
    ) -> None:
        super().__init__()
        self._client = client
        self._potato_images = potato_images
        self._channels = game_channels
        self._immune_ids = immune_list
        self._admins = admin_list

    @commands.Cog.listener()
    async def on_ready(self):
        print("Potato Admin Cog Loaded and Ready")


    @discord.slash_command(
            name = "refresh", 
            description = "Force parameter refresh"
    )
    async def refresh_all(self,ctx):
        if ctx.author.id in self._admins.get():
            await ctx.respond(REFRESH)
            for loader in (self._potato_images, self._channels, self._immune_ids, self._admins):
                loader.update()
        else:
            await ctx.respond(INVALID_REFRESH)

class PotatoFun(commands.Cog):
    def __init__(self, client) -> None:
        super().__init__()
        self._client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Potato Fun Cog Loaded and Ready")

    @discord.slash_command(
            name = "ping_me",
            description = "Get the bot to ping you"
    )
    async def random_time_ping(self, ctx):
        pingee = ctx.author
        await ctx.respond(RANDOM_TIME_PING.format(pingee.mention))
        #ping after a random length of time
        await asyncio.sleep(random.randint(
                RAND_PING_WAIT_MIN, RAND_PING_WAIT_MAX))
        await ctx.respond(pingee.mention)

class HotPotatoBot(discord.Bot):
    def __init__(
            self, 
            image_file, 
            channel_file, 
            immune_file, 
            admin_file,
            refresh_delay = REFRESH_DELAY, 
            description=None, 
            *args, **options
    ):
        super().__init__(
                description,
                intents = discord.Intents.all(), #TODO restrict intents
                *args, 
                **options)

        set_setter = lambda x: set([int(i) for i in x])
        potato_images = Hotloader(image_file, refresh_delay)
        channels = Hotloader(channel_file, refresh_delay, set_setter)
        immune_ids = Hotloader(immune_file, refresh_delay, set_setter)
        admins = Hotloader(admin_file, refresh_delay, set_setter)

        self.add_cog(
                PotatoAdmin(
                    self,
                    admins,
                    potato_images,
                    channels,
                    immune_ids
                )
        )

        self.add_cog(
                HotPotatoGame(
                    self,
                    potato_images,
                    channels,
                    immune_ids,
                    admins
                )
        )

    #@event decorators just overide respective methods 
    async def on_ready(self):
        print(f"{self.user} is ready and online!")

         

if __name__ == "__main__":
    robuticus = HotPotatoBot(IMAGE_FILE, CHANNELS_FILE, IMMUNE_FILE, ADMIN_FILE)
    robuticus.add_cog(PotatoFun(robuticus))
    robuticus.run(TOKEN)
