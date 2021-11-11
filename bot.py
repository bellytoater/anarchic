import asyncio
import discord
from discord.ext import commands, tasks
import datetime
import json
import string
import re
import time
import copy
import os
import random
import dislash
import aiohttp
import logging
from datetime import datetime
from discord.ext.commands import errors, MissingPermissions, BadArgument, MissingRequiredArgument, CommandNotFound
from discord.reaction import Reaction
from discord.utils import get
from dislash import InteractionClient, OptionChoice, ActionRow, Option, Button, ButtonStyle, SelectMenu, OptionType, SelectOption
from enum import Enum
from datetime import timedelta

from dislash.interactions.app_command_interaction import SlashInteraction

class Faction(Enum):
    Town = 1
    Mafia = 2
    Cult = 3
    Neutral = 4

class Defense(Enum):
    Default = 1
    Basic  = 2
    Strong = 3

class DeathReason(Enum):
    NoReason = 1
    GoingInsane = 2
    Unknown = 3
    Suicide = 4
    Mafia = 5
    Enforcer = 6
    Guilt = 7
    JesterGuilt = 8
    Hanged = 9
    Plague = 10
    Psychopath = 11

class EndReason(Enum):
    MafiaWins = 1
    TownWins = 2
    Draw = 3

class GameSize(Enum):
    Small = 1
    Medium = 2
    Large = 3
    TooBig = 4
    TooSmall = 5

class LogType(Enum):
    INFO = 1,
    WARNING = 2,
    LOG = 3,
    ERROR = 4,
    DEBUG = 5

class CannotSendDMError(Exception):
    pass

#Create player vars

class Player(object):
    def __init__(self):
        self.role = ""
        self.dead = False
        self.appearssus = False
        self.islynched = False
        self.isrevealed = False
        self.faction = Faction.Town
        self.docHealedHimself = False
        self.wasrevealed = False
        self.framed = False
        self.detresult = None
        self.death = []
        self.defense = Defense.Default
        self.diedln = False
        self.checked = False
        self.distraction = False
        self.cautious = False
        self.doc = False
        self.jesterwin = False
        self.hhtarget = None
        self.will = []
        self.wins = False
        self.voted = False
        self.ogrole = ""
        self.votedforwho = None
        self.ready = False
        self.id = 0

    def reset(self, will=False):
        self.role = ""
        self.ogrole = ""
        self.dead = False
        self.islynched = False
        self.appearssus = False
        self.isrevealed = False
        self.faction = Faction.Town
        self.hhtarget = None
        self.framed = False
        self.wasrevealed = False
        self.docHealedHimself = False
        self.death = []
        self.jesterwin = False
        self.cautious = False
        self.doc = False
        self.defense = Defense.Default
        self.destraction = False
        self.checked = False
        self.wins = False
        self.ready = False
        self.voted = False
        if (will==False):
            self.will = []
        self.diedln = False
        self.votedforwho = None
        self.detresult = None
        self.id = 0

    def get_player(id, ddict:dict):
        """Get a Player by it's assigned ID. Returns `None` if it cannot be found."""
        for value in ddict.values():
            if (value.id == id):
                return value
        
        return None

class Logger():
    def log(text:str, logtype:LogType=LogType.LOG):
        thing = ""
        if (logtype == LogType.INFO):
            thing = "INFO"
        if (logtype == LogType.WARNING):
            thing = "WARNING"
        if (logtype == LogType.LOG):
            thing = "LOG"
        if (logtype == LogType.ERROR):
            thing = "ERROR"
        if (logtype == LogType.DEBUG):
            thing = "DEBUG"

        now = datetime.now()
        time = now.strftime("%H:%M:%S")

        f = open("log.log", "w")
        f.write(f"{time} [{thing}] : {text}")
        f.close()

        # os.chdir(cwd)

def PlayerSize(size:int):
    if (size >= 5 and size <= 6):
        return GameSize.Small
    elif (size >= 7 and size <= 8):
        return GameSize.Medium
    elif (size >= 9 and size <= 10):
        return GameSize.Large
    elif (size > 10):
        return GameSize.TooBig
    elif (size < 5):
        return GameSize.TooSmall

def reasonToText(reason:DeathReason):
    if (reason == DeathReason.NoReason):
        return "They mysteriously died."
    if (reason == DeathReason.GoingInsane):
        return "They gave up on Anarchic and left the Town."
    if (reason == DeathReason.Unknown):
        return "They were killed of unknown causes."
    if (reason == DeathReason.Suicide):
        return "They commited suicide."
    if (reason == DeathReason.Mafia):
        return "They were attacked by a member of the **Mafia** <:maficon2:890328238029697044>."
    if (reason == DeathReason.Enforcer):
        return "They were shot by an **Enforcer**. <:enficon2:890339050865696798>"
    if (reason == DeathReason.Guilt):
        return "They died from **Guilt**."
    if (reason == DeathReason.JesterGuilt):
        return "They died from **Guilt** over lynching the **Jester** <:jesticon2:889968373612560394>."
    if (reason == DeathReason.Plague):
        return "They were taken by the **Plague**."
    if (reason == DeathReason.Psychopath):
        return "They were psychopathed by a member of the **Psychopath**."

    return "They mysteriously died."

def reasontoColor(reason:DeathReason):
    if (reason == DeathReason.NoReason):
        return 0x7ed321
    if (reason == DeathReason.GoingInsane):
        return 0x7ed321
    if (reason == DeathReason.Unknown):
        return 0x7ed321
    if (reason == DeathReason.Suicide):
        return 0x7ed321
    if (reason == DeathReason.Mafia or reason == DeathReason.Psychopath):
        return 0xd0021b
    if (reason == DeathReason.Enforcer):
        return 0x7ed321
    if (reason == DeathReason.Guilt):
        return 0x7ed321
    if (reason == DeathReason.JesterGuilt):
        return 0xffc3e7
    if (reason == DeathReason.Plague):
        return 0xb8e986

    return 0x7ed321

def reasonToImage(reason:DeathReason):
    if (reason == DeathReason.NoReason):
        return ""
    if (reason == DeathReason.GoingInsane):
        return ""
    if (reason == DeathReason.Unknown):
        return ""
    if (reason == DeathReason.Suicide):
        return ""
    if (reason == DeathReason.Mafia):
        if (random.randint(1, 23845) == 9):
            return "https://cdn.discordapp.com/attachments/765738640554065962/899360428088508426/unknown.png"
        else:
            return "https://media.discordapp.net/attachments/765738640554065962/871849580533268480/unknown.png?width=744&height=634"
    if (reason == DeathReason.Enforcer):
        return "https://cdn.discordapp.com/attachments/867924656219377684/882797114634154014/unknown.png"
    if (reason == DeathReason.Guilt):
        return "https://media.discordapp.net/attachments/765738640554065962/879163761057992744/unknown.png?width=541&height=634"
    if (reason == DeathReason.JesterGuilt):
        return "https://media.discordapp.net/attachments/765738640554065962/895419320140693584/export.png?width=396&height=408"
    if (reason == DeathReason.Psychopath):
        return "https://cdn.discordapp.com/attachments/765738640554065962/899360428088508426/unknown.png"        

    return ""

@tasks.loop(minutes=1.0)
async def shopUpdater():
    now = datetime.now()
    if (now.hour == 16 and now.minute == 0):
        for i in store.values():
            i['dailydeal'] = False

        r = store.values()
        progression = 0

        for _ in range(1000000):
            e = random.choice(list(r))
            well = []

            for i in store.values():
                if (i['dailydeal'] == True):
                    well.append(i)

            if (e not in well):
                progression += 1
                e['dailydeal'] = True

                if (progression >= 3):
                    break

        with open('shop.json', 'w') as jsonf:
            json.dump(store, jsonf)


intents = discord.Intents.all()
bot = commands.Bot(command_prefix=">", intents=intents, case_insensitive=True)
slash = InteractionClient(bot)
logging.basicConfig(level=logging.WARNING)

def getTownies(ctx):
    res = []
    for i in var[ctx.id]["playerdict"].values():
        if (i.faction == Faction.Town and i.dead == False and i.id != 0):
            res.append(i)

    return res

def getMaf(ctx):
    res = []
    for i in var[ctx.id]["playerdict"].values():
        if (i.faction == Faction.Mafia and i.dead == False and i.id != 0):
            res.append(i)

    return res

def getWill(mywill:list):
    message = ""
    for i in mywill:
        if (i == ""):
            continue

        message += i + "\n"

    return message

async def EndGame(reason:EndReason, guild):
    embed = discord.Embed()
    var[guild.id]["endreason"] = reason

    if (reason == EndReason.TownWins):
        embed.title="**__<a:win:878421027703631894> The Town Wins <:townicon2:896431548717473812> <a:win:878421027703631894>!__**"
        embed.color = 0x7ed321
        for i in var[guild.id]["playerdict"].values():
            if (i.faction == Faction.Town):
                i.wins = True

        embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/879065891751464960/unknown.png?width=560&height=701")
    elif (reason == EndReason.MafiaWins):
        embed.title="***__<a:win:878421027703631894> The Mafia Wins <:maficon2:890328238029697044> <a:win:878421027703631894>!__***"
        embed.color = 0xd0021b
        for i in var[guild.id]["playerdict"].values():
            if (i.faction == Faction.Mafia):
                i.wins = True
        embed.set_image(url="https://images-ext-2.discordapp.net/external/8FKjo7N-8O9yztX8HF_1nF-PE-UxoWfsdQuzXcr4koo/%3Fwidth%3D744%26height%3D634/https/media.discordapp.net/attachments/765738640554065962/871849580533268480/unknown.png")
    elif (reason == EndReason.Draw):
        embed = discord.Embed(title="**__Draw :crescent_moon:__**", colour=discord.Colour(0xb0c9c9))

        embed.set_image(url="https://images-ext-2.discordapp.net/external/LlOBlIZEHHfRmfQn8_dhpUD6gN0CUWMecRcDZjd9CTs/%3Fwidth%3D890%26height%3D701/https/media.discordapp.net/attachments/765738640554065962/877706810763657246/unknown.png?width=805&height=634")
        embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png?width=374&height=374")
        for i in var[guild.id]["playerdict"].values():
            i.wins = False

    embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png?width=374&height=374")
    embed.set_footer(text="Use /end to finalize the game and /start to play a new one.", icon_url="https://cdn.discordapp.com/attachments/878437549721419787/883074983759347762/anarpfp.png")

    message = ""
    em = var[guild.id]["emoji"]

    for i in var[guild.id]["playerdict"].values():
        if (i.faction != Faction.Town or i.id == 0):
            continue

        emoji = ""
        if (i.wins == True):
            emoji = "🏆"
        else:
            emoji = "❌"

        message += f"{emoji} "

        if (i.dead == True):
            message += "~~"

        message += "**"

        message += i.ogrole.capitalize()
        message += em[i.ogrole.lower()]

        message += "**"

        if (i.dead == True):
            message += "~~"

        message += f" - {bot.get_user(i.id).mention}\n"
    if (message == ""):
        message = "**:x: None**"

    embed.add_field(name="**__Town <:townicon2:896431548717473812>__**", value=message, inline=False)

    message = ""
    for i in var[guild.id]["playerdict"].values():
        if (i.faction != Faction.Mafia or i.id == 0):
            continue
        
        emoji = ""
        if (i.wins == True):
            emoji = "🏆"
        else:
            emoji = "❌"

        message += f"{emoji} "

        if (i.dead == True):
            message += "~~"

        message += "**"

        message += i.ogrole.capitalize()
        message += em[i.ogrole.lower()]

        message += "**"

        if (i.dead == True):
            message += "~~"

        message += f" - {bot.get_user(i.id).mention}\n"
    
    if (message == ""):
        message = "**:x: None**"

    embed.add_field(name="**__Mafia <:maficon2:890328238029697044>__**", value=message, inline=False)
   
    message = ""
    for i in var[guild.id]["playerdict"].values():
        if (i.faction != Faction.Neutral or i.id == 0):
            continue
        
        emoji = ""
        if (i.wins == True):
            emoji = "🏆"
        else:
            emoji = "❌"

        message += f"{emoji} "

        if (i.dead == True):
            message += "~~"

        message += "**"

        message += i.ogrole.capitalize()
        message += em[i.ogrole.lower()]

        message += "**"

        if (i.dead == True):
            message += "~~"

        message += f" - {bot.get_user(i.id).mention}\n"
    
    if (message == ""):
        message = "**:x: None**"

    embed.add_field(name="**__Neutral 🪓__**", value=message, inline=False)

    return embed

bot.remove_command('help')

temp = {
"buyables" : ["test"],
"roles" : ["Cop", "Detective", "Lookout", "Doctor", "Enforcer", "Psychic", "Mayor", "Mafioso", "Consigliere", "Framer", "Consort", "Headhunter", "Jester",],
"towns" : ["Cop", "Detective", "Lookout", "Doctor", "Enforcer", "Mayor", "Psychic"],
"support" : ["Mayor", "Psychic"],
"mafias" : ["Framer", "Consort", "Consigliere"],
"cults" : ["Cult Leader", "Ritualist"],
"neutrals" : ["Headhunter", "Jester"],
"investigatives" : ["Cop", "Detective", "Lookout"],
"comps" : {"enforced": ["Enforcer", "Doctor", "Mafioso", "RT", "RN"], "classic":["Cop", "Doctor", "Mayor", "Jester", "Mafioso"], "execution":["Cop", "Doctor", "RT", "RT", "Headhunter", "Mafioso"], "legacy":["Cop", "Doctor", "RT", "RT", "RT", "RN", "Mafioso", "RM"], "scattered":["Enforcer", "Doctor", "RT", "RT", "RT", "Mafioso", "RM", "Headhunter"], "duet": ["Enforcer", "Doctor", "TI", "RT", "RT", "Mafioso", "Consort"], "framed": ["Lookout", "Doctor", "TI", "RT", "RT", "Mafioso", "Framer"], "anarchy": ["Mayor", "Doctor", "TI", "TI", "RT", "RT", "Mafioso", "RM", "RN", "A"], "ranked": ["Doctor", "Enforcer", "TI", "TI", "RT", "RT", "RT", "Mafioso", "Consort", "Framer"], "truth" : ["Detective", "Doctor", "RT", "RT", "RT", "Mafioso", "Consigliere"],"delta":["Psychopath", "Tracker", "Mafioso"], "custom" : []},
"data" : {},
"inv" : {},
"dailythings" : {},
"todaystokens" : {},
"voted" : {},
"targets" : {},
"endreason" : EndReason.TownWins,
"votingemoji" : {},
"playeremoji" : {},
"nightd" : 0,
"nightindex" : 0,
"players" : [],
"started" : False,
"emojis" : ["🇦","🇧","🇨","🇩","🇪","🇫","🇬","🇭","🇮","🇯"],
"emojiz" : ["a","b","c","d","e","f","g","h","i","j"],
"playerdict" : {"p1": Player(),  "p2": Player(),  "p3": Player(),  "p4": Player(),  "p5": Player(),  "p6": Player(),  "p7": Player(),  "p8": Player(),  "p9": Player(),  "p10": Player()},
"voting" : False,
"abstainers" : [],
"guiltyers" : [],
"innoers" : [],
"guyontrial" : 0,
"startchannel" : None,
"novotes" : False,
"mayor" : None,
"channel" : None,
"itememoji" : {"Cop Shard" : "<:copshard:896804869820801115>", "Doctor Shard" : "<:docshard:896576968756191273>", "Enforcer Shard" : "<:enfshard:896576814942670899>" ,"Detective Shard" : "<:detshard:896760012729356331>", "Lookout Shard" : "<:loshard:896577050645786655>", "Epic Programmer Trophy" : ":computer:", "Epic Designer Trophy" : ":video_game:", "Epic Artist Trophy" : ":art:", "Mafioso Shard" : "<:mafshard:896801052945449031>", "Headhunter Shard" : "<:hhicon:896903989285777428>", "Jester Shard" : "<:jestshard:896900933307469875>", "Consigliere Shard" : "<:consigshard:896910618051878982>", "Framer Shard" : "<:frameshard:896910673370558464>", "Psychic Shard" : "<:psyshard:896842380618108938>", "Mayor Shard" : "<:mayorshard:897570664209338369>", "Consort Shard" : "<:consshard:896823151307157535>", "Detective Shard" : "<:detshard:896760012729356331>", "Lookout" : "<:loshard:896577050645786655>"},
"emoji" : {"cop": "<:copicon2:889672912905322516>", "doctor": "<:docicon2:890333203959787580>", "mafioso": "<:maficon2:891739940055052328>", "enforcer": "<:enficon2:890339050865696798>", "lookout": "<:loicon2:889673190392078356>", "psychopath" : "<:mario:901229374500655135>", "consort": "<:consicon2:890336628269281350>", "jester": "<:jesticon2:889968373612560394>", "headhunter": "<:hhicon2:891429754643808276>", "mayor": "<:mayoricon2:897570023143518288>", "detective":"<:deticon2:889673135438319637>", "framer": "<:frameicon2:890365634913902602>", "psychic": "<:psyicon2:896159311078780938>", "consigliere" : "<:consigicon2:896154845130666084>", "tracker" : "<:mario:901229374500655135>", "rt": "<:townicon2:896431548717473812>", "rm": "<:maficon2:890328238029697044>", "rn": ":axe:", "ti": ":mag_right:", "ts": "🛠️", "a" : ":game_die:"},
"result" : False,
"targetint" : 0,
"vkickd" : {},
"ind" : 0,
"isresults" : False,
"guiltyinno" : False,
"mafcon" : None,
"diechannel" : None,
"killers" : ["Mafioso", "Godfather",  "Enforcer"],
"guildg" : None,
"resul" : 0,
"test": "OK",
"setupz" : "classic",
"timer" : 0,
"index" : 0,
"trialtimer" : 0,
"trialuser" : 0,
"gday" : 0,
"daysnokill" : 0
}

badcet = False
badtemp = False

var = {}

with open('data.json') as jsonf:
    cur = json.load(jsonf)
with open('inv.json') as jsonf:
    inv = json.load(jsonf)
with open('guilds.json') as jsonf:
    guilds = json.load(jsonf)
with open('shop.json') as jsonf:
    store = json.load(jsonf)

for i in list(guilds.values()):
    i["guild"] == 0
    i["joinedgame"] = False

with open('guilds.json', 'w') as jsonf:
    json.dump(guilds, jsonf)


def intparsable(s):
    try:
        int(s.content)
        return True
    except ValueError:
        return False

def checkIfMidnight():
    now = datetime.now()
    seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    return seconds_since_midnight == 0


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    game = discord.Activity(type=discord.ActivityType.watching, name="chaos | /help")
    await bot.change_presence(status=discord.Status.do_not_disturb, activity=game)
    try:
        shopUpdater.start()
    except:
        pass

    Logger.log("Bot Started", LogType.INFO)


@bot.event
async def on_slash_command_error(interaction, error):
    if (isinstance(error, dislash.application_commands.errors.PrivateMessageOnly)):
        await interaction.reply("This command can only be used in DMs.", ephemeral=True)
    elif (isinstance(error, dislash.application_commands.errors.NoPrivateMessage)):
        await interaction.reply("This command can only be used in a server.", ephemeral=True)
    else:
        raise error

@bot.event
async def on_slash_command(inter):
    try:
        var[inter.guild.id]["test"]
    except:
        try:
            var[inter.guild.id] = copy.deepcopy(temp)
        except:
            pass

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    if isinstance(error, errors.PrivateMessageOnly):
        await ctx.send("This command only works in dms!")
        return
    if isinstance(error, BadArgument):
        return
    if isinstance(error, MissingRequiredArgument):
        return
    if isinstance(error, MissingPermissions):
        return

    raise error

@slash.slash_command(
    name="ping",
    description="Get the latency of the bot"
)
async def ping(ctx):
    latency = bot.latency * 1000
    emb = discord.Embed(title="Pinging...", color=discord.Color.blue())

    emb.add_field(name="Discord WS:", value=f"```yaml\n{str(round(latency))}ms```", inline=False)
    emb.add_field(name = "**Typing**", value = "```yaml\n...```", inline = True)
    emb.add_field(name = "**Message**", value = "```yaml\n...```", inline = True)

    before = time.monotonic()
    message = await ctx.reply(embed=emb)
    ping = (time.monotonic() - before) * 1000

    emb.title = "**Pong!**"
    emb.set_field_at(1, name = "**Message:**", value = f"```yaml\n{str(int((message.created_at - ctx.message.created_at).total_seconds() * 1000))}ms```", inline = True)
    emb.set_field_at(
            2, name = "**Typing:**", value = f"```yaml\n{str(round(ping))}ms```", inline = True)

    await message.edit(embed = emb)

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="**__Anarchic's Commands__**", colour=discord.Colour(0xc4f5ff))

    embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")

    embed.add_field(name="**__Party <a:Tada:841483453044490301>__**", value="`/join` to join the game.\n`/leave` to leave the game.\n`/setup [gamemode]` to change the mode.\n`/party` to view the party.\n`/start` to start the game.\n`/vkick [user]` to vote to kick a player.\n`/kick [user]` to kick a player.\n`/clear` to clear the entire party.", inline=False)
    embed.add_field(name="**__Game :video_game:__**", value="\n`/vote member [player]` to vote a player during the game.\n`/will write [text] [line]` to write and edit your will.\n`/will remove [line]` to remove a line in your will.\n`/will view` to view your will.", inline=False)
    embed.add_field(name="**__Information 💡__**", value="`/help` to see the list of commands.\n`/bal` to see your balance and profile.\n`/roles` to see the list of roles.\n`/role [role name]` to see a specific role.\n`/setups` to see the list of setups.\n`/changelog` to view the lastest updates.\n`/invite` to get an invite to the official server.", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def weafjewiuohfoiuyhibnitjwrleuiog(ctx):
    embed = discord.Embed(title=f"**Jellytoaster** has revealed themselves to be the Bot Developer!", colour=discord.Colour(0xbc9b25), description="They will now have 3 votes in all voting procedures regarding the Anarchic server and bot.")

    embed.set_image(url="https://cdn.discordapp.com/attachments/878437549721419787/882418844424081449/unknown.png")
    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/897570023143518288.png?size=80")
    await ctx.send(embed=embed)
    await ctx.message.delete()

@bot.command()
async def reveal(ctx):
    embed = discord.Embed(title=f"**Cet** has revealed themselves to be the Peasant!", colour=discord.Colour(0xbc9b25), description="They will now have 0 votes in all voting procedures regarding the Anarchic server and bot.")

    embed.set_image(url="https://cdn.discordapp.com/attachments/878437549721419787/882418844424081449/unknown.png")
    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/897570023143518288.png?size=80")
    await ctx.send(embed=embed)
    await ctx.message.delete()

@slash.slash_command(
    name="help",
    description="Get help",
    gulid_ids=[871525831422398494]
)
async def hhelp(inter):
    await inter.reply(type=5)

    embed = discord.Embed(title="**__Anarchic's Commands__**", colour=discord.Colour(0xc4f5ff))

    embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")

    embed.add_field(name="**__Party <a:Tada:841483453044490301>__**", value="`/join` to join the game.\n`/leave` to leave the game.\n`/setup [gamemode]` to change the mode.\n`/party` to view the party.\n`/start` to start the game.\n`/vkick [user]` to vote to kick a player.\n`/kick [user]` to kick a player.\n`/clear` to clear the entire party.", inline=False)
    embed.add_field(name="**__Game :video_game:__**", value="\n`/vote member [player]` to vote a player during the game.\n`/will write [text] [line]` to write and edit your will.\n`/will remove [line]` to remove a line in your will.\n`/will view` to view your will.", inline=False)
    embed.add_field(name="**__Information 💡__**", value="`/help` to see the list of commands.\n`/bal` to see your balance and profile.\n`/roles` to see the list of roles.\n`/role [role name]` to see a specific role.\n`/setups` to see the list of setups.\n`/changelog` to view the lastest updates.\n`/invite` to get an invite to the official server.", inline=False)
    await inter.edit(embed=embed)
@slash.slash_command(
    name="invite",
    description="Add the bot to your server!"
)
async def invi(ctx):
    dev:discord.User = bot.get_user(839842855970275329)
    art:discord.User = bot.get_user(703645091901866044)
    mak:discord.User = bot.get_user(667189788620619826)
    otherart:discord.User = bot.get_user(643566247337787402)


    embed = discord.Embed(title="Anarchic", colour=discord.Colour(0xff8b6c), description="*Hosts games of Anarchic, which are styled similar to the classic party game Mafia!*")

    embed.set_thumbnail(url=ctx.guild.icon_url)
    embed.set_footer(text="Invite me to your server!", icon_url=ctx.author.avatar_url)
    embed.add_field(name="Bot", value="[Click Here](https://discord.com/api/oauth2/authorize?client_id=887118309827432478&permissions=105696980048&scope=bot%20applications.commands)", inline=False)
    embed.add_field(name="Server", value="[Click Here](https://discord.gg/ZHuFPHy7cw)", inline=False)
    embed.add_field(name="Anarchic Staff Team", value=f"**:rage: Bitch - {art.name}#{art.discriminator}\n:art: Other Artist - {otherart.name}#{otherart.discriminator}**\n**:computer: Programmer - {dev.name}#{dev.discriminator}**\n**:video_game: Manager - {mak.name}#{mak.discriminator}**")
    await ctx.send(embed=embed)

@bot.command()
async def invite(ctx):
    await ctx.send("https://discord.com/api/oauth2/authorize?client_id=887118309827432478&permissions=105696980048&scope=bot%20applications.commands")

@dislash.guild_only()
@slash.slash_command(
    name="changelog",
    description="Get the new stuff from the bot"
)
async def chagelog(ctx):
    # New Feature = <:p_ThinDashYellow:878761154887942204>
    # Bug Fixes = <:p_ThinDashGreen:878761154653061141>
    # Visual Updates = <:p_ThinDashPurple:878761154837630986>
    # Quality of Life changes = <:p_ThinDashOrange:878761154451755049>
    # News = <:p_ThinDashPink:878761154846007356>


    embed = discord.Embed(title="Patch Notes 1.1.0: Psychic and Consigliere <:psyicon2:896159311078780938><:consigshard:896910618051878982>", colour=discord.Colour(0xb5ffee), description="A enormous update which contains 2 new roles!")

    embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/897243210177462272/export.png?width=454&height=468")
    embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")
    embed.set_footer(text="October, 11, 2021", icon_url=ctx.author.avatar_url)

    embed.add_field(name="New Roles :performing_arts: ", value="**Psychic <:psyicon2:896159311078780938> - A powerful mystic who can speak to the dead**\n**Consigliere <:consigshard:896910618051878982> - A corrupted detective who gathers information for the Mafia**", inline=False)
    embed.add_field(name="**Bug Fixes :bug:**", value="<:p_ThinDashGreen:878761154653061141> **Fixed bug where bot awkwardly crashes when a player is lynched\n<:p_ThinDashGreen:878761154653061141> Fixed bug where players could see dead chat\n<:p_ThinDashGreen:878761154653061141> Fixed bug where Mafioso was town sided**", inline=False)
    embed.add_field(name="**Shop :shopping_bags:**", value="<:p_ThinDashPurple:878761154837630986> **Anarith - The best place to shop in the town is now open for business! Check it out with `/shop`**", inline=False)
    embed.add_field(name="**Shards <:copshard:896804869820801115>**", value="<:p_ThinDashPurple:878761154837630986> **Shards are out! Shards are items that give you a higher chance of getting a role, but disappear after you get the role. Have fun using them!**", inline=False)
    embed.add_field(name="Miscellaneous :gear:", value="<:p_ThinDashYellow:878761154887942204> **Added 2 new setups, __Truth <:consigshard:896910618051878982>__ and __Scattered__\n<:p_ThinDashYellow:878761154887942204> Removed Circus from playable setups\n<:p_ThinDashYellow:878761154887942204> Updated `/help` to include the new commands\n<:p_ThinDashYellow:878761154887942204> Added currency system to the game\n<:p_ThinDashYellow:878761154887942204> Updated certain role embeds**", inline=False)
    await ctx.send(embed=embed)

#Economy
@dislash.guild_only()
@slash.slash_command(
    name="bal",
    description="Check how many silvers you have",
    options=[
        Option("member", "Check how many silvers your friend has", OptionType.MENTIONABLE, False)
    ],
)
async def bal(inter, member=None):
    try:
        var[inter.guild.id]["test"]
    except:
        var[inter.guild.id] = copy.deepcopy(temp)

    if (member == None):
        if (str(inter.author.id) not in cur):
            cur[str(inter.author.id)] = 0

        balance = str(cur[str(inter.author.id)])
        embed = discord.Embed(title=f"<a:sparkle:894702379851735100> {inter.author.name}'s profile <a:sparkle:894702379851735100>", colour=discord.Colour(0xffddfd), description="*The Townie*")

        if (inter.author.id == 839842855970275329):
            embed.description = "*The Programmer  :computer:*"
        if (inter.author.id == 667189788620619826):
            embed.description = "*The Designer  :video_game:*"
        if (inter.author.id == 703645091901866044):
            embed.description = "*The Artist  :art:*"
        if (inter.author.id == 643566247337787402):
            embed.description = "*The Other Artist  :art:*"

        embed.set_thumbnail(url=inter.author.avatar_url)

        embed.add_field(name="**Currency**", value=f"<:silvers:889667891044167680> **Silvers :** {balance}\n<:gems:889667936304898079> **Gems :** 0")
        await inter.reply(embed=embed)
    else:
        if (str(member.id) not in cur):
            cur[str(member.id)] = 0

        balance = str(cur[str(member.id)])
        embed = discord.Embed(title=f"<a:sparkle:894702379851735100> {member.name}'s profile <a:sparkle:894702379851735100>", colour=discord.Colour(0xffddfd), description="*The Townie*")

        if (member.id == 839842855970275329):
            embed.description = "*The Programmer :computer:*"
        if (member.id == 667189788620619826):
            embed.description = "*The Designer :video_game:*"
        if (member.id == 703645091901866044):
            embed.description = "*The Artist :art:*"
        if (member.id == 643566247337787402):
            embed.description = "*The Other Artist :art:*"

        embed.set_thumbnail(url=member.avatar_url)

        embed.add_field(name="**Currency**", value=f"<:silvers:889667891044167680> **Silvers :** {balance}\n<:gems:889667936304898079> **Gems :** 0")
        await inter.reply(embed=embed)


    with open('data.json', 'w') as jsonf:
        json.dump(cur, jsonf)

@slash.slash_command(
    name="bank",
    description="Check out the latest profits from the shop"
)
async def bank(inter):
    embed = discord.Embed(title="Anarchic Bank", colour=discord.Colour(0x6e7343), description="Check out the latest profits from stores!")

    embed.set_thumbnail(url="https://cdn.discordapp.com/icons/753967387149074543/d77cf3d1192d84e441a5a194fb8ef081.webp?size=1024")
    embed.set_footer(text="Take a look.", icon_url=inter.author.avatar_url)

    e = str(cur["bank"])

    embed.add_field(name="Anarith Market", value=f"**{e}** silvers <:silvers:889667891044167680>")
    await inter.reply(embed=embed)

@dislash.guild_only()
@slash.slash_command(
    name="give",
    description="Give some silvers to your friend",
    options=[
        Option("member", "The member you want to give your silvers to", OptionType.USER, True),
        Option("amount", "How many silvers you want to give", OptionType.INTEGER, True)
    ],
)
async def give(inter, member=None, amount=None):
    if (member.bot == True):
        await inter.reply("You can't give silvers to a bot. Otherwise, how will you get them back?", ephemeral=True)
    else:
        if (amount < 0):
            await inter.reply("<:ehh:869928693814935653>", ephemeral=True)
            return

        if (str(inter.author.id) not in cur):
            cur[str(inter.author.id)] = 0
        if (str(member.id) not in cur):
            cur[str(member.id)] = 0
        
        if (amount <= cur[str(inter.author.id)]):
            cur[str(inter.author.id)] -= amount
            cur[str(member.id)] += amount

            new = cur[str(inter.author.id)] 

            embed = discord.Embed(title=f"**Successfully given {member.name}#{member.discriminator} __{amount}__ silvers <:silvers:889667891044167680>!**", colour=discord.Colour(0xffdffe), description=f"You now have __{new}__ silvers <:silvers:889667891044167680> .")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889667891044167680.png?size=96")
            embed.set_footer(text="Thank you!", icon_url=inter.author.avatar_url)
            
            await inter.reply(embed=embed)

            with open('data.json', 'w') as jsonf:
                json.dump(cur, jsonf)
        else:
            money = cur[str(inter.author.id)] 
            embed = discord.Embed(title="**You don't have enough silvers <:silvers:889667891044167680>!**", colour=discord.Colour(0xff4a87), description=f"You only have __{money}__ silvers <:silvers:889667891044167680> .")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889667891044167680.png?size=96")
            embed.set_footer(text="Better get more money", icon_url=inter.author.avatar_url)
            await inter.reply(embed=embed, ephemeral=True)


@dislash.guild_only()
@slash.slash_command(
    name="shop",
    description="Anarith Market"
)
async def shop(inter:SlashInteraction):
    deals = []

    for key, value in store.items():
        if (value['dailydeal'] == True):
            deals.append(value)

    page1 = discord.Embed(title="Anarith Market", colour=discord.Colour(0xc0c0fb), description="Welcome to Anarith, the biggest hub of shops in the town! To navigate, use the dropdown!")

    page1.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")
    page1.set_footer(text="Daily Deals reset at 8PM UTC.", icon_url=inter.author.avatar_url)

    page1.add_field(name="**<a:sparkle:894702379851735100> Daily Offers <a:sparkle:894702379851735100>**", value="** **", inline=False)
    page1.add_field(name=f"{deals[0]['title']}**| 24** <:silvers:889667891044167680>", value=f"{deals[0]['description']}", inline=False)
    page1.add_field(name=f"{deals[1]['title']}**| 24** <:silvers:889667891044167680>", value=f"{deals[1]['description']}", inline=False)
    page1.add_field(name=f"{deals[2]['title']}**| 24** <:silvers:889667891044167680>", value=f"{deals[2]['description']}", inline=False)
    page1.add_field(name="** **", value="To buy something, use `/buy`!", inline=False)

    page2 = discord.Embed(title="Anarith Market", colour=discord.Colour(0xc0c0fb), description="Welcome to Anarith, the biggest hub of shops in the town! To navigate, use the dropdown!")

    page2.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")
    page2.set_footer(text="Take a look around.", icon_url=inter.author.avatar_url)

    page2.add_field(name="**:star2: Shards :star2:**", value="** **", inline=False)

    deal = []
    for value in store.values():
        if (value['dailydeal'] == True):
            deal.append(24)
        else:
            deal.append(39)

    page2.add_field(name=f"Cop Shard <:copshard:896804869820801115>**| {deal[0]}** <:silvers:889667891044167680>", value=f"Increases your chance of rolling **Cop <:copshard:896804869820801115>** by 3x", inline=False)
    page2.add_field(name=f"Detective Shard <:detshard:896760012729356331>**| {deal[1]}** <:silvers:889667891044167680>", value=f"Increases your chance of rolling **Detective <:detshard:896760012729356331>** by 3x", inline=False)
    page2.add_field(name=f"Lookout Shard <:loshard:896577050645786655>**| {deal[2]}** <:silvers:889667891044167680>", value=f"Increases your chance of rolling **Lookout <:loshard:896577050645786655>** by 3x", inline=False)
    page2.add_field(name=f"Doctor Shard <:docshard:896576968756191273>**| {deal[3]}** <:silvers:889667891044167680>", value=f"Increases your chance of rolling **Doctor <:docshard:896576968756191273>** by 3x", inline=False)
    page2.add_field(name=f"Enforcer Shard <:enfshard:896576814942670899>**| {deal[4]}** <:silvers:889667891044167680>", value=f"Increases your chance of rolling **Enforcer <:enfshard:896576814942670899>** by 3x", inline=False)
    page2.add_field(name="** **", value="To buy something, use `/buy`!", inline=False)

    deal = []
    for value in store.values():
        if (value['dailydeal'] == True):
            deal.append(24)
        else:
            deal.append(39)

    page3 = discord.Embed(title="Anarith Market", colour=discord.Colour(0xc0c0fb), description="Welcome to Anarith, the biggest hub of shops in the town! To navigate, use the dropdown!")

    page3.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")
    page3.set_footer(text="Take a look around.", icon_url=inter.author.avatar_url)

    page3.add_field(name="**:star2: Shards :star2:**", value="** **", inline=False)
    page3.add_field(name=f"Mayor Shard <:mayorshard:897570664209338369>**| 39** <:silvers:889667891044167680>", value=f"Increases your chance of rolling **Mayor <:mayorshard:897570664209338369>** by 3x", inline=False)
    page3.add_field(name=f"Psychic Shard <:psyshard:896842380618108938>**| 39** <:silvers:889667891044167680>", value=f"Increases your chance of rolling **Psychic <:psyshard:896842380618108938>** by 3x", inline=False)
    page3.add_field(name=f"Mafioso Shard <:mafshard:896801052945449031>**| 39** <:silvers:889667891044167680>", value=f"Increases your chance of rolling **Mafioso <:mafshard:896801052945449031>** by 3x", inline=False)
    page3.add_field(name=f"Framer Shard <:frameshard:896910673370558464>**| 39** <:silvers:889667891044167680>", value=f"Increases your chance of rolling **Framer <:frameshard:896910673370558464>** by 3x", inline=False)
    page3.add_field(name=f"Consigliere Shard <:consigshard:896910618051878982>**| 39** <:silvers:889667891044167680>", value=f"Increases your chance of rolling **Consigliere <:consigshard:896910618051878982>** by 3x", inline=False)
    page3.add_field(name="** **", value="To buy something, use `/buy`!", inline=False)

    page4 = discord.Embed(title="Anarith Market", colour=discord.Colour(0xc0c0fb), description="Welcome to Anarith, the biggest hub of shops in the town! To navigate, use the dropdown!")

    page4.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")
    page4.set_footer(text="Take a look around.", icon_url=inter.author.avatar_url)

    page4.add_field(name="**:star2: Shards :star2:**", value="** **", inline=False)
    page4.add_field(name=f"Consort Shard <:consshard:896823151307157535>**| 39** <:silvers:889667891044167680>", value=f"Increases your chance of rolling **Consort <:consshard:896823151307157535>** by 3x", inline=False)
    page4.add_field(name=f"Headhunter Shard <:hhicon:896903989285777428>**| 39** <:silvers:889667891044167680>", value=f"Increases your chance of rolling **Headhunter <:hhicon:896903989285777428>** by 3x", inline=False)
    page4.add_field(name=f"Jester Shard <:jestshard:896900933307469875>**| 39** <:silvers:889667891044167680>", value=f"Increases your chance of rolling **Jester <:jestshard:896900933307469875>** by 3x", inline=False)
    page4.add_field(name="** **", value="To buy something, use `/buy`!", inline=False)

    menu = SelectMenu(
        custom_id="pages",
        placeholder="Page",
        options=[
            SelectOption("Daily Deals", "p1", "Check out the daily deals", None, True),
            SelectOption("Shards Pg. 1", "p2", "First page for shards"),
            SelectOption("Shards Pg. 2", "p3", "Second page for shards"),
            SelectOption("Shards Pg. 3", "p4", "Third page for shards")
        ]
    )

    msg = await inter.reply(embed=page1, components=[menu])

    for _ in range(100):
        try:
            select = await msg.wait_for_dropdown(timeout=60)
        except asyncio.TimeoutError:
            menu.disabled = True
            await msg.edit(components=[menu])
            return
        
        e = select.select_menu.selected_options[0]

        emb = None

        if (e.value == "p1"):
            emb = copy.copy(page1)
            menu = SelectMenu(
                custom_id="pages",
                placeholder="Page",
                options=[
                    SelectOption("Daily Deals", "p1", "Check out the daily deals", None, True),
                    SelectOption("Shards Pg. 1", "p2", "First page for shards"),
                    SelectOption("Shards Pg. 2", "p3", "Second page for shards"),
                    SelectOption("Shards Pg. 3", "p4", "Third page for shards")
                ]
            )
        if (e.value == "p2"):
            emb = copy.copy(page2)
            menu = SelectMenu(
                custom_id="pages",
                placeholder="Page",
                options=[
                    SelectOption("Daily Deals", "p1", "Check out the daily deals"),
                    SelectOption("Shards Pg. 1", "p2", "First page for shards", None, True),
                    SelectOption("Shards Pg. 2", "p3", "Second page for shards"),
                    SelectOption("Shards Pg. 3", "p4", "Third page for shards")
                ]
            )
        if (e.value == "p3"):
            emb = copy.copy(page3)
            menu = SelectMenu(
                custom_id="pages",
                placeholder="Page",
                options=[
                    SelectOption("Daily Deals", "p1", "Check out the daily deals"),
                    SelectOption("Shards Pg. 1", "p2", "First page for shards"),
                    SelectOption("Shards Pg. 2", "p3", "Second page for shards", None, True),
                    SelectOption("Shards Pg. 3", "p4", "Third page for shards")
                ]
            )
        if (e.value == "p4"):
            emb = copy.copy(page4)
            menu = SelectMenu(
                custom_id="pages",
                placeholder="Page",
                options=[
                    SelectOption("Daily Deals", "p1", "Check out the daily deals"),
                    SelectOption("Shards Pg. 1", "p2", "First page for shards"),
                    SelectOption("Shards Pg. 2", "p3", "Second page for shards"),
                    SelectOption("Shards Pg. 3", "p4", "Third page for shards", None, True)
                ]
            )


        await select.create_response(embed=emb, type=7, components=[menu])

@dislash.guild_only()
@slash.slash_command(
    name="buy",
    description="Buy an item from the shop!",
    options=[
        Option("item", "The item you want to buy", OptionType.STRING, True),
        Option("amount", "How many of them you want to buy", OptionType.INTEGER, False)
    ],
)
async def buy(inter, item=None, amount=None):
    if (amount == None):
        amount = 1


    if (str(inter.author.id) not in cur):
        cur[str(inter.author.id)] = 0
    if (str(inter.author.id) not in inv):
        inv[str(inter.author.id)] = {}

    if (item.lower() not in store):
        await inter.reply("Not in the store!", ephemeral=True)
        return

    bal = cur[str(inter.author.id)]
    thing = store[item.lower()]

    embed = discord.Embed()

    price = thing['cost']
    if (thing['dailydeal'] == True):
        price = 24 * amount
    else:
        price = price * amount

    if (item.lower() == 'cop'):
        embed = discord.Embed(title=f"**Cop Shard <:copshard:889672912905322516>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Cop <:copshard:896804869820801115>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896804869820801115.png?size=80")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar_url)
    elif (item.lower() == 'doctor'):
        embed = discord.Embed(title=f"**Doctor Shard <:docicon2:890333203959787580>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Doctor <:docicon2:890333203959787580>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896576968756191273.png?size=96")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar_url) 
    elif (item.lower() == "enforcer"):
        embed = discord.Embed(title=f"**Enforcer Shard <:enficon2:890339050865696798>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Enforcer <:enficon2:890339050865696798>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896576814942670899.png?size=96")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar_url) 
    elif (item.lower() == 'lookout'):
        embed = discord.Embed(title=f"**Lookout Shard <:consshard:896823151307157535>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Lookout <:loicon2:889673190392078356>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896577050645786655.png?size=96")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar_url) 
    elif (item.lower() == 'detective'):
        embed = discord.Embed(title=f"**Detective Shard <:deticon2:889673135438319637>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Detective <:deticon2:889673135438319637>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896760012729356331.png?size=44")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar_url) 
    elif (item.lower() == 'consort'):
        embed = discord.Embed(title=f"**Consort Shard <:consshard:896823151307157535>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Consort <:consshard:896823151307157535>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896823151307157535.png?size=80")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar_url) 
    elif (item.lower() == 'mayor'):
        embed = discord.Embed(title=f"**Mayor Shard <:mayorshard:897570664209338369>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Mayor <:mayorshard:897570664209338369>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/897570664209338369.png?size=80")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar_url) 
    elif (item.lower() == 'psychic'):
        embed = discord.Embed(title=f"**Psychic Shard <:psyshard:896842380618108938>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Psychic <:psyshard:896842380618108938>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896842380618108938.png?size=80")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar_url)
    elif (item.lower() == 'framer'):
        embed = discord.Embed(title=f"**Framer Shard <:frameshard:896910673370558464>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Framer <:frameshard:896910673370558464>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896910673370558464.png?size=80")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar_url) 
    elif (item.lower() in 'consigliere'):
        embed = discord.Embed(title=f"**Consigliere Shard <:consigshard:896910618051878982>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Consigliere <:consigshard:896910618051878982>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896910618051878982.png?size=80")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar_url) 
    elif (item.lower() == 'jester'):
        embed = discord.Embed(title=f"**Jester Shard <:jestshard:896900933307469875>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Jester <:jestshard:896900933307469875>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896900933307469875.png?size=80")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar_url) 
    elif (item.lower() == 'headhunter' or item.lower() == 'hh'):
        embed = discord.Embed(title=f"**Headhunter Shard <:hhicon:896903989285777428>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Headhunter <:hhicon:896903989285777428>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896903989285777428.png?size=80msp")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar_url)  
    elif (item.lower() == 'mafioso' or item.lower() == 'maf'):
        embed = discord.Embed(title=f"**Mafioso Shard <:mafshard:896801052945449031>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Mafioso <:mafshard:896801052945449031>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896801052945449031.png?size=80")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar_url)  

    row = ActionRow(
        Button(style=ButtonStyle.green, label="Yes", custom_id="y"),
        Button(style=ButtonStyle.red, label="No", custom_id="n")
    )

    msg = await inter.reply(embed=embed, components=[row])

    but = msg.create_click_listener(timeout=60)

    @but.not_from_user(inter.author, cancel_others=True, reset_timeout=False)
    async def on_wrong_user(inter):
        await inter.reply("You're not the author", ephemeral=True)

    @but.matching_id("y")
    async def on_yes(inter):
        if (price * amount > bal):
            embed = discord.Embed(title="You don't have enough silvers", colour=discord.Colour(0xad1414), description=f"You only have **{str(bal)} <:silvers:889667891044167680>**.")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889667891044167680.png?size=96")
            embed.set_footer(text="Better get more money.", icon_url=inter.author.avatar_url)
            await inter.reply(embed=embed)
        else:
            cur[str(inter.author.id)] -= price * amount
            try:
                cur["bank"]
            except:
                cur["bank"] = 0

            cur["bank"] += price * amount

            if (item.lower() == 'cop'):
                embed = discord.Embed(title=f"**Cop Shard <:copshard:896804869820801115>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb8ff49), description="This shard increases your chance of rolling **Cop** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889672912905322516.png?size=96")
                embed.set_footer(text=f"Thank your for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar_url)
                try:
                    inv[str(inter.author.id)]["cop"]
                except:
                    inv[str(inter.author.id)]["cop"] = {
                        "amount": 0,
                        "description" : "Use `/equip cop` to equip this item.",
                        "title" : "Cop Shard",
                        "usable" : True
                    }

                for _ in range(amount):
                    inv[str(inter.author.id)]["cop"]["amount"] += 1
            elif (item.lower() == 'doctor'):
                embed = discord.Embed(title=f"**Doctor Shard <:docicon2:890333203959787580>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Doctor <:docicon2:890333203959787580>** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896576968756191273.png?size=96")
                embed.set_footer(text=f"Thank your for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar_url)
                
                try:
                    inv[str(inter.author.id)]["doctor"]
                except:
                    inv[str(inter.author.id)]["doctor"] = {
                        "amount": 0,
                        "description": "Use `/equip doctor` to equip this item.",
                        "title" : "Doctor Shard",
                        "usable" : True
                    }

                for _ in range(amount):
                    inv[str(inter.author.id)]["doctor"]["amount"] += 1

            elif (item.lower() == "enforcer"):
                embed = discord.Embed(title=f"**Enforcer Shard <:enficon2:890339050865696798>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Enforcer <:enficon2:890339050865696798>** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896576814942670899.png?size=96")
                embed.set_footer(text=f"Thank your for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar_url)
                
                try:
                    inv[str(inter.author.id)]["enforcer"]
                except:
                    inv[str(inter.author.id)]["enforcer"] = {
                        "amount": 0,
                        "description" : "Use `/equip enforcer` to equip this item.",
                        "title" : "Enforcer Shard",
                        "usable" : True
                    }

                for _ in range(amount):
                    inv[str(inter.author.id)]["enforcer"]["amount"] += 1         
            elif (item.lower() == 'lookout'):
                embed = discord.Embed(title=f"**Lookout Shard <:loicon2:889673190392078356>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Lookout <:loicon2:889673190392078356>** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896577050645786655.png?size=96")
                embed.set_footer(text=f"Thank your for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar_url)
                
                try:
                    inv[str(inter.author.id)]["lookout"]
                except:
                    inv[str(inter.author.id)]["lookout"] = {
                        "amount": 0,
                        "description" : "Use `/equip lookout` to equip this item.",
                        "title" : "Lookout Shard",
                        "usable" : True
                    }
                
                for _ in range(amount):
                    inv[str(inter.author.id)]["lookout"]["amount"] += 1
            elif (item.lower() == 'detective'):
                embed = discord.Embed(title=f"**Detective Shard <:deticon2:889673135438319637>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Detective <:deticon2:889673135438319637>** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896760012729356331.png?size=44")
                embed.set_footer(text=f"Thank your for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar_url)
                
                try:
                    inv[str(inter.author.id)]["detective"]
                except:
                    inv[str(inter.author.id)]["detective"] = {
                        "amount": 0,
                        "description" : "Use `/equip detective` to equip this item.",
                        "title" : "Detective Shard",
                        "usable" : True
                    }

                for _ in range(amount):
                    inv[str(inter.author.id)]["Detective Shard"]["amount"] += 1
            elif (item.lower() == 'consort'):
                embed = discord.Embed(title=f"**Consort Shard <:consshard:896823151307157535>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Consort <:consshard:896823151307157535>** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896823151307157535.png?size=80")
                embed.set_footer(text=f"Thank your for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar_url)
                
                try:
                    inv[str(inter.author.id)]["consort"]
                except:
                    inv[str(inter.author.id)]["consort"] = {
                        "amount": 0,
                        "description" : "Use `/equip consort` to equip this item.",
                        "title" : "Consort Shard",
                        "usable" : True
                    }

                for _ in range(amount):
                    inv[str(inter.author.id)]["consort"]["amount"] += 1
            elif (item.lower() == 'mayor'):
                embed = discord.Embed(title=f"**Mayor Shard <:mayorshard:897570664209338369>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Mayor <:mayorshard:897570664209338369>** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/897570664209338369.png?size=80")
                embed.set_footer(text=f"Thank your for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar_url)
                
                try:
                    inv[str(inter.author.id)]["mayor"]
                except:
                    inv[str(inter.author.id)]["mayor"] = {
                        "amount": 0,
                        "description" : "Use `/equip mayor` to equip this item.",
                        "title" : "Mayor Shard",
                        "usable" : True
                    }

                for _ in range(amount):
                    inv[str(inter.author.id)]["mayor"]["amount"] += 1
            elif (item.lower() == 'psychic'):
                embed = discord.Embed(title=f"**Psychic Shard <:psyshard:896842380618108938>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Psychic <:psyshard:896842380618108938>** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896842380618108938.png?size=80")
                embed.set_footer(text=f"Thank your for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar_url)
                
                try:
                    inv[str(inter.author.id)]["psychic"]
                except:
                    inv[str(inter.author.id)]["psychic"] = {
                        "amount": 0,
                        "description" : "Use `/equip psychic` to equip this item.",
                        "title" : "Psychic Shard",
                        "usable" : True
                    }

                for _ in range(amount):
                    inv[str(inter.author.id)]["psychic"]["amount"] += 1
            elif (item.lower() == 'framer'):
                embed = discord.Embed(title=f"**Framer Shard <:frameshard:896910673370558464>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Framer <:frameshard:896910673370558464>** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896910673370558464.png?size=80")
                embed.set_footer(text=f"Thank your for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar_url)
                
                try:
                    inv[str(inter.author.id)]["framer"]
                except:
                    inv[str(inter.author.id)]["framer"] = {
                        "amount": 0,
                        "description" : "Use `/equip framer` to equip this item.",
                        "title" : "Framer Shard",
                        "usable" : True
                    }


                for _ in range(amount):
                    inv[str(inter.author.id)]["framer"]["amount"] += 1
            elif (item.lower() in 'consigliere'):
                embed = discord.Embed(title=f"**Consigliere Shard <:consigshard:896910618051878982>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Consigliere <:consigshard:896910618051878982>** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896910618051878982.png?size=80")
                embed.set_footer(text=f"Thank your for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar_url)
                
                try:
                    inv[str(inter.author.id)]["consig"]
                except:
                    inv[str(inter.author.id)]["consig"] = {
                        "amount": 0,
                        "description" : "Use `/equip consig` to equip this item.",
                        "title" : "Consigliere Shard",
                        "usable" : True
                    }

                for _ in range(amount):
                    inv[str(inter.author.id)]["consig"]["amount"] += 1
            elif (item.lower() == 'jester'):
                embed = discord.Embed(title=f"**Jester Shard <:jestshard:896900933307469875>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Jester <:jestshard:896900933307469875>** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896900933307469875.png?size=80")
                embed.set_footer(text=f"Thank your for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar_url)
                
                try:
                    inv[str(inter.author.id)]["jester"]
                except:
                    inv[str(inter.author.id)]["jester"] = {
                        "amount": 0,
                        "description" : "Use `/equip jester` to equip this item.",
                        "title" : "Jester Shard",
                        "usable" : True
                    }

                for _ in range(amount):
                    inv[str(inter.author.id)]["jester"]["amount"] += 1
            elif (item.lower() == 'headhunter' or item.lower() == 'hh'):
                embed = discord.Embed(title=f"**Headhunter Shard <:hhicon:896903989285777428>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Headhunter <:hhicon:896903989285777428>** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896903989285777428.png?size=80msp")
                embed.set_footer(text=f"Thank your for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar_url)
                
                try:
                    inv[str(inter.author.id)]["headhunter"]
                except:
                    inv[str(inter.author.id)]["headhunter"] = {
                        "amount": 0,
                        "description" : "Use `/equip headhunter` to equip this item.",
                        "title" : "Headhunter Shard",
                        "usable" : True
                    }

                for _ in range(amount):
                    inv[str(inter.author.id)]["headhunter"]["amount"] += 1
            elif (item.lower() == "mafioso" or item.lower() == "maf"):
                embed = discord.Embed(title=f"**Mafioso Shard <:mafshard:896801052945449031>** | {price} <:silvers:889667891044167680>", colour=discord.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Mafioso <:mafshard:896801052945449031>** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896801052945449031.png?size=80")
                embed.set_footer(text=f"Thank your for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar_url)
                
                try:
                    inv[str(inter.author.id)]["mafioso"]
                except:
                    inv[str(inter.author.id)]["mafioso"] = {
                        "amount": 0,
                        "description" : "Use `/equip mafioso` to equip this item.",
                        "title" : "Mafioso Shard",
                        "usable" : True
                    }

                for _ in range(amount):
                    inv[str(inter.author.id)]["mafioso"]["amount"] += 1

            row.disable_buttons()
            await inter.reply(components=[row], type=7)

            await inter.reply(embed=embed)

            with open('data.json', 'w') as jsonf:
                json.dump(cur, jsonf)
            with open('inv.json', 'w') as jsonf:
                json.dump(inv, jsonf)

    @but.matching_id("n")
    async def on_no(inter):
        row.disable_buttons()
        await inter.reply(components=[row], type=7)
        return

    @but.timeout
    async def on_timeout():
        row.disable_buttons()
        await inter.edit(components=[row])
        return

@dislash.guild_only()
@slash.slash_command(
    name="unequip",
    description="Unequip the currently equipped item"
)
async def unequip(inter):
    try:
        var[inter.guild.id]["test"]
    except:
        var[inter.guild.id] = copy.deepcopy(temp)

    try:
        guilds[str(inter.author.id)]
    except:
        guilds[str(inter.author.id)] = {"guild" : 0, "joinedgame" : False, "equipped" : None}

    if (guilds[str(inter.author.id)]["equipped"] == None):
        await inter.reply("You have no item equipped...", ephemeral=True)

    thin = inv[str(inter.author.id)][guilds[str(inter.author.id)]["equipped"]]["title"]
    em = var[inter.guild.id]["itememoji"][thin]
    theid = re.sub("[^0-9]", "", em)

    embed = discord.Embed(title="**You have unequipped your item**", colour=discord.Colour(0xff1b1f))

    embed.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{theid}.png?size=96")
    embed.set_footer(text="Rip", icon_url=inter.author.avatar_url)
    await inter.reply(embed=embed, ephemeral=True)

    guilds[str(inter.author.id)]["equipped"] = None

    with open('guilds.json', 'w') as jsonf:
        json.dump(guilds, jsonf)

@dislash.guild_only()
@slash.slash_command(
    name="equip",
    description="Equip an item from your inventory",
    options=[
        Option("item", "The item you want to equip", OptionType.STRING, True)
    ],
)
async def equip(inter, item=None):
    if (str(inter.author.id) not in inv):
        inv[str(inter.author.id)] = {}

    realitem = item.lower().replace(" ", "")
    if (realitem not in inv[str(inter.author.id)]):
        await inter.reply("That item isn't in your inventory...", ephemeral=True)
        return
    if (inv[str(inter.author.id)][realitem]["usable"] == False):
        await inter.reply("That item isn't usable...", ephemeral=True)
        return

    try:
        var[inter.guild.id]["test"]
    except:
        var[inter.guild.id] = copy.deepcopy(temp)

    try:
        guilds[str(inter.author.id)]
    except:
        guilds[str(inter.author.id)] = {"guild" : 0, "joinedgame" : False, "equipped" : None}

    theitem = inv[str(inter.author.id)][realitem]["title"]
    emoji = var[inter.guild.id]["itememoji"][theitem]

    theid = re.sub("[^0-9]", "", emoji)

    embed = discord.Embed(title=f"**You have equipped __{theitem} {emoji}__**!", colour=discord.Colour(0x8aa0ff))

    embed.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{theid}.png?size=96")
    embed.set_footer(text="Have fun!", icon_url=inter.author.avatar_url)
    await inter.reply(embed=embed, ephemeral=True)

    guilds[str(inter.author.id)]["equipped"] = realitem
    
    with open('guilds.json', 'w') as jsonf:
        json.dump(guilds, jsonf)

@dislash.guild_only()
@slash.slash_command(
    name="inv",
    description="Check your inventory",
    options=[
        Option("member", "Check how many silvers your friend has", OptionType.MENTIONABLE, False)
    ],
)
async def inventory(inter, member=None):
    try:
        var[inter.guild.id]["test"]
    except:
        var[inter.guild.id] = copy.deepcopy(temp)

    if (member == None):
        if (str(inter.author.id) not in inv):
            inv[str(inter.author.id)] = {}

        embed = discord.Embed(title=f"**{inter.author.name}'s Inventory**", colour=discord.Colour(0xe3fff2))

        embed.set_thumbnail(url=inter.author.avatar_url)

        try:
            thin = inv[str(inter.author.id)][guilds[str(inter.author.id)]["equipped"]]["title"]
            em = var[inter.guild.id]["itememoji"][thin]
            embed.add_field(name=f"**Currently Equipped: {thin} {em}**", value="** **", inline=False)
        except:
            embed.add_field(name=f"**Currently Equipped: None**", value="** **", inline=False)

        for key, value in inv[str(inter.author.id)].items():
            try:
                r = value["title"]
                eh = var[inter.guild.id]["itememoji"][r]
                e = str(value["amount"])
                if (e != "0"):
                    embed.add_field(name=f"{r} {eh} x{e}", value=value["description"], inline=False)
            except:
                e = str(value["amount"])
                r = value["title"]
                if (e != "0"):
                    embed.add_field(name=f"{r} :grey_question: x{e}", value=value["description"], inline=False)

        embed.add_field(name="**Use the embed to navigate your inventory!**", value="** **", inline=False)
        await inter.reply(embed=embed)
    else:
        if (str(member.id) not in inv):
            inv[str(member.id)] = {}

        embed = discord.Embed(title=f"**{member.name}'s Inventory**", colour=discord.Colour(0xe3fff2))

        embed.set_thumbnail(url=member.avatar_url)

        try:
            thin = inv[str(member.id)][guilds[str(member.id)]["equipped"]]["title"]
            em = var[inter.guild.id]["itememoji"][thin]
            embed.add_field(name=f"**Currently Equipped: ???**", value="** **", inline=False)
        except:
            embed.add_field(name=f"**Currently Equipped: ???**", value="** **", inline=False)

        for key, value in inv[str(member.id)].items():
            try:
                r = value["title"]
                eh = var[inter.guild.id]["itememoji"][r]
                e = str(value["amount"])
                if (e != "0"):
                    embed.add_field(name=f"{r} {eh} x{e}", value=value["description"], inline=False)
            except:
                e = str(value["amount"])
                eh = value["title"]
                if (e != 0):
                    embed.add_field(name=f"{eh} :grey_question: x{e}", value=value["description"], inline=False)
        
        await inter.reply(embed=embed)


    with open('data.json', 'w') as jsonf:
        json.dump(cur, jsonf)

#actual game stuff happening

@slash.slash_command(
    name="guide",
    description="How to play Anarchic"
)
async def info(inter):
    embed = discord.Embed(title="**How to get started with Anarchic**", colour=discord.Colour(0x86b4b6), description="In this guide you will be learning how to get started in Anarchic, so let's get to it! We have a party system in Anarchic for the game to begin so you have to run `/join` to join the party. If the party leader thinks they have enough players, they start the game with `/start`!")

    # embed.set_image(url="https://cdn.discordapp.com/embed/avatars/0.png")
    embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/zvBfC-Hei3zC-NkTa_MJ1t-lx4Fu6dXoB-5uzicvPYE/https/images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%253Fwidth%253D468%2526height%253D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")
    embed.set_footer(text="Have fun", icon_url=inter.author.avatar_url)

    embed.add_field(name="🔹 You need a minimum of 5 players to start the game!", value="** **", inline=False)
    embed.add_field(name="Anarchic also offers different modes in our bot, those modes are : ", value="**:triangular_flag_on_post: Classic (5 players)\n<:enficon2:890339050865696798> Enforced (5 players)\n<:hhicon2:891429754643808276> Execution (6 players)\n<:consicon2:890336628269281350> Duet (7 players)\n<:frameicon2:890365634913902602> Framed (7 players)\n<:consigicon2:896154845130666084> Truth (7 players)\n:sparkles: Legacy (8 players)\n:diamond_shape_with_a_dot_inside: Scattered (9 players)\n:drop_of_blood: Anarchy (10 players)\n:star2: Ranked (10 players)**\n\nYou can run the /setups command to view these, to set the mode to a desired setup run the /setup command. And you can run the /party command after changing the setup to view the roles in the mode!", inline=False)
    embed.add_field(name="Other important commands for the game:", value="🔹 `/leave`  to leave the party, if the leader leaves the second person becomes the leader\n🔹 `/clear` to clear the party if the party is filled with AFKs\n🔹 `/kick` to kick an AFK player from the party, can only be done by the party leader\n🔹 `/help` to view the list of commands", inline=False)
    await inter.reply(embed=embed)

@dislash.guild_only()
@dislash.has_role("Lookout (Lvl 3)")
@slash.slash_command(
    name="game",
    description="Try to get others to play Anarchic",
    options = [
        Option("message", "Your optional message to send along with your game invite", OptionType.STRING, False)
    ],
    guild_ids=[753967387149074543]
)
async def game(inter, message=None):
    if (message == None):
        message = "Use `/join` to join!"

    embed = discord.Embed(title=f"{inter.author.name} wants to play Anarchic!", colour=discord.Colour(0xbfb932), description=message)

    embed.set_thumbnail(url="https://cdn.discordapp.com/icons/753967387149074543/d77cf3d1192d84e441a5a194fb8ef081.webp?size=1024")
    embed.set_footer(text="Use /join to join.", icon_url=inter.author.avatar_url)
    
    await inter.reply(content="<@&867926341876584449>", embed=embed)

@slash.slash_command(
    name="role",
    description="Get info on a role",
    options=[
        Option("role", "Choose a role to get info from", OptionType.STRING, True)
    ]
)
async def rolee(inter:SlashInteraction, role:str):
    embed = await bootyfulembed(role.lower(), inter.author)
    if (embed == None):
        await inter.reply("Not a role, bro", ephemeral=True)
        return

    await inter.reply(embed=embed)

@dislash.guild_only()
@slash.slash_command(
    name="join",
    description="Join the game!"
)
async def jjoin(inter):
    await _join(inter, True)

async def _join(ctx, interaction=False):
    try:
        var[ctx.guild.id]["test"]
    except:
        var[ctx.guild.id] = copy.deepcopy(temp)

    try:
        guilds[str(ctx.author.id)]
    except:
        guilds[str(ctx.author.id)] = {"guild" : 0, "joinedgame" : False, "equipped" : None}

    if (ctx.author.id in var[ctx.guild.id]["players"]):
        if (interaction==True):
            await ctx.reply("You can't join a lobby you're already in.", ephemeral=True)
        else:
            await ctx.channel.send("You can't join a lobby you're already in.")
        return
    elif (len(var[ctx.guild.id]["players"]) >= 10):
        if(interaction == True):
            await ctx.reply("The game is full! Please wait when another player leaves.", ephemeral=True)
        else:
            await ctx.send("The game is full! Please wait when another player leaves.")
        return
    elif (guilds[str(ctx.author.id)]['joinedgame'] == True):
        await ctx.reply("You can't join multiple games at once.", ephemeral=True)
        return


    if (var[ctx.guild.id]["started"] == False):

        if (interaction == True):
            await ctx.reply(type=5)

        var[ctx.guild.id]["players"].append(int(ctx.author.id))
        players = len(var[ctx.guild.id]["players"])

        p = var[ctx.guild.id]["players"]
        var[ctx.guild.id]["playeremoji"][var[ctx.guild.id]["emojis"][var[ctx.guild.id]["index"]]] = ctx.author.id
        var[ctx.guild.id]["votingemoji"][var[ctx.guild.id]["emojiz"][var[ctx.guild.id]["index"]]] = ctx.author.id
        var[ctx.guild.id]["index"] += 1

        s = var[ctx.guild.id]["setupz"]

        if (s.lower() == "delta"):
            s = f"{str(random.randint(10, 99))}.{str(random.randint(100, 999))}.{str(random.randint(10, 99))}.{str(random.randint(100, 999))}"

        embed = discord.Embed(title=f"{ctx.author.name}#{ctx.author.discriminator} has joined the party!", description=f"**Current Players:**`{str(players)}`\n**Current Host:**{bot.get_user(p[0]).mention}\n**Setup:** {string.capwords(str(s))}", colour=discord.Colour(0x8ef3ff))
        embed.set_thumbnail(url=ctx.author.avatar_url)
        if (interaction == True):
            await ctx.edit(embed=embed)
        else:
            await ctx.send(embed=embed)

        guilds[str(ctx.author.id)]["guild"] = ctx.guild.id
        guilds[str(ctx.author.id)]["joinedgame"] = True

        with open('guilds.json', 'w') as jsonf:
            json.dump(guilds, jsonf)
        
    else:
        if(interaction == True):
            await ctx.reply("The game already started! You can't join.", ephemeral=True)
        else:
            await ctx.send("The game already started! You can't join.")
        return

@dislash.guild_only()
@slash.slash_command(
    name="leave",
    description="Leave the game"
)
async def lleave(inter):
    await _leave(inter, True)

async def _leave(ctx, inter=False):
    try:
        var[ctx.guild.id]["test"]
    except:
        var[ctx.guild.id] = copy.deepcopy(temp)

    if (ctx.author.id not in var[ctx.guild.id]["players"]):
        if (inter==True):
            await ctx.reply("You can't leave a lobby you're not in.", ephemeral=True)
        else:
            await ctx.send("You can't leave a lobby you're not in.")

        return

    g = discord.utils.get(ctx.guild.roles, name="[Anarchic] Player")
    d = discord.utils.get(ctx.guild.roles, name="[Anarchic] Dead")

    r:discord.Member = ctx.author
    yea = r.roles
    try:
        yea.remove(g)
    except:
        pass

    try:
        yea.remove(d)
    except:
        pass

    await r.edit(roles=yea)

    if (var[ctx.guild.id]["started"] == False):
        var[ctx.guild.id]["players"].remove(int(ctx.author.id))


        desired_value = ctx.author.id
        for key, value in var[ctx.guild.id]["playeremoji"].items():
            if value == desired_value:
                del var[ctx.guild.id]["playeremoji"][key]
                break

        for key, value in var[ctx.guild.id]["votingemoji"].items():
            if value == desired_value:
                    del var[ctx.guild.id]["votingemoji"][key]
                    break

        var[ctx.guild.id]["index"] -= 1

        embed = discord.Embed()
        try:
            r = var[ctx.guild.id]["players"]


            embed = discord.Embed(title=f"**{ctx.author.name}#{ctx.author.discriminator} has left the party.**", colour=discord.Colour(0xf5cbff), description=f"**Current Players: `{len(r)}`**\n**Current Host:** {bot.get_user(r[0]).mention}")
        except:
            embed = discord.Embed(title=f"**{ctx.author.name}#{ctx.author.discriminator} has left the party.**", colour=discord.Colour(0xf5cbff), description=f"**Current Players: `{len(r)}`**\n**Current Host:** None")
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.set_footer(text="Come back soon.", icon_url=ctx.author.avatar_url)
        if (inter == True):
            await ctx.reply(embed=embed)
        else:
            await ctx.send(embed=embed)

        guilds[str(ctx.author.id)]["guild"] = 0
        guilds[str(ctx.author.id)]["joinedgame"] = False
        guilds[str(ctx.author.id)]["vkicktarget"] = 0
        for i in var[ctx.guild.id]["players"]:
            if (guilds[str(i)]["vkicktarget"] == ctx.author.id):
                guilds[str(i)]["vkicktarget"] = 0
                
        var[ctx.guild.id]["vkickd"][ctx.author.id] = 0

        with open('guilds.json', 'w') as jsonf:
            json.dump(guilds, jsonf)
    else:
        if (inter==True):
            await ctx.reply("The game already started! You can't leave.", ephemeral=True)
        else:
            await ctx.send("The game already started! You can't leave.")


@bot.command()
async def party(ctx):
    await _party(ctx)

@dislash.guild_only()
@slash.slash_command(
    name="party",
    description="View the players in the game"
)
async def pparty(inter):
    await _party(inter, True)

async def _party(ctx, sla=False):
    try:
        var[ctx.guild.id]["test"]
    except:
        var[ctx.guild.id] = copy.deepcopy(temp)
    message = ""
    for i in var[ctx.guild.id]["players"]:
        if (i == var[ctx.guild.id]["players"][0]):
            continue
        user = await ctx.channel.guild.fetch_member(int(i))
        message += f"{user.mention}"
        message += "\n"
    if (message == ""):
        if (len(var[ctx.guild.id]["players"]) < 1):
            if (sla==True):
                await ctx.create_response("There's nobody in the game...", ephemeral=True)
            else:
                await ctx.send("There's nobody in the game...")

            return

    ok = ctx.guild.get_member(int(var[ctx.guild.id]["players"][0]))
    embed = discord.Embed(title=f"`{ok.name}'s Lobby`", colour=discord.Colour(0xccbecb))

    embed.set_thumbnail(url=ctx.channel.guild.icon_url)
    embed.set_footer(text="Use `/start` to start the game.", icon_url=ctx.author.avatar_url)

    b = var[ctx.guild.id]["players"]
    embed.add_field(name=f"Current Players :neutral_face:: `{len(b)}`", value=f"**:crown: Host:** {ok.mention}\n{message}\n\n**Do `/info` to learn how to play.**")
    
    message = ""
    if (var[ctx.guild.id]["setupz"].lower() != "any"):
        c = var[ctx.guild.id]["comps"]
        s = copy.copy(c[var[ctx.guild.id]["setupz"]])
        em = var[ctx.guild.id]["emoji"]
        for i in s:
            if (i == "RT"):
                message += f"**Random Town** {em[i.lower()]}\n"
            elif (i == "RM"):
                message += f"**Random Mafia** {em[i.lower()]}\n"
            elif (i == "RN"):
                message += f"**Random Neutral** {em[i.lower()]}\n"
            elif (i == "TI"):
                message += f"**Town Investigative** {em[i.lower()]}\n"
            elif (i == "TS"):
                message += f"**Town Support** {em[i.lower()]}\n"
            else:
                message += f"**{string.capwords(i)}** {em[i.lower()]}\n"
        
        if (message == ""):
            message = "This setup is empty."

        s = var[ctx.guild.id]["setupz"]
        embed.add_field(name=f"Current Setup :tada:: `{string.capwords(s)}`", value=message)
    else:
        embed.add_field(name=f"Current Setup :tada:: `All Any`", value="**:game_die: Any x the amount of players playing :partying_face:**")

    if (sla == True):
        await ctx.create_response(embed=embed)
    else:
        await ctx.channel.send(embed=embed)

@dislash.guild_only()
@slash.slash_command(
    name="vkick",
    description="Vote to kick users from the game.",
    options=[
        Option("member", "The member you want to votekick", OptionType.MENTIONABLE, True)
    ]
)
async def vdkick(ctx, member=None):
    try:
        var[ctx.guild.id]["test"]
    except:
        var[ctx.guild.id] = copy.deepcopy(temp)
    if (var[ctx.guild.id]["started"] == True):
        await ctx.create_response("You can't kick players during a game.", ephemeral=True)
        return
    if (ctx.author.id not in var[ctx.guild.id]["players"]):
        await ctx.create_response("WHAT WHY ARE YOU KICKING SOMEONE WHEN YOU AREN'T EVEN IN THE GAME", ephemeral=True)
        return
    if (member.id not in var[ctx.guild.id]["players"]):
        await ctx.create_response("You can't kick players that aren't in the game.", ephemeral=True)
        return
    try:
        if (guilds[str(ctx.author.id)]["vkicktarget"] == member.id):
            await ctx.create_response("You can't kick the same player more than once.", ephemeral=True)
            return
    except:
        pass

    if (member.id in var[ctx.guild.id]["vkickd"]):
        var[ctx.guild.id]["vkickd"][member.id] += 1
    else:
        var[ctx.guild.id]["vkickd"][member.id] = 1


    f = var[ctx.guild.id]["vkickd"]
    guilds[str(ctx.author.id)]["vkicktarget"] = member.id
    embed = discord.Embed(title=f"**{ctx.author.name} has voted to kick {member.name}!**", colour=discord.Colour(0xb4ffdc), description=f"**({f[member.id]}/3) votes are needed to vote kick {member.name}.**")

    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896418860427771975/upvote.png")
    embed.set_footer(text="3 votes are needed to vote kick someone.")
    await ctx.create_response(embed=embed)

    if (var[ctx.guild.id]["vkickd"][member.id] >= 3):
        var[ctx.guild.id]["players"].remove(int(member.id))
        embed = discord.Embed(title=f"**{member.name} has been kicked!**", colour=discord.Colour(0xfff4d1))
        if (random.randint(1, 80000) == 9642):
            embed.description = "That's a shame..."

        guilds[str(member.id)]["guild"] = 0
        guilds[str(member.id)]["joinedgame"] = False
        var[ctx.guild.id]["vkickd"][member.id] = 0
        
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.followup(embed=embed)

        guilds[str(member.id)]["vkicktarget"] = 0
        for i in var[ctx.guild.id]["players"]:
            if (guilds[str(i)]["vkicktarget"] == member.id):
                guilds[str(i)]["vkicktarget"] = 0

@dislash.guild_only()
@slash.slash_command(
    name="kick",
    description="Kick users from the game. You have to be the game host to do this.",
    options=[
        Option("member", "The member you want to votekick", OptionType.MENTIONABLE, True)
    ]
)
async def kkick(ctx, member:discord.Member):
    try:
        var[ctx.guild.id]["test"]
    except:
        var[ctx.guild.id] = copy.deepcopy(temp)
    if (var[ctx.guild.id]["started"] == True):
        await ctx.create_response("You can't kick players during a game.", ephemeral=True)
        return
    if (ctx.author.id not in var[ctx.guild.id]["players"]):
        await ctx.create_response("WHAT WHY ARE YOU KICKING SOMEONE WHEN YOU AREN'T EVEN IN THE GAME", ephemeral=True)
        return
    if (member.id not in var[ctx.guild.id]["players"]):
        await ctx.create_response("You can't kick players that aren't in the game.", ephemeral=True)
        return
    if (ctx.author.id != var[ctx.guild.id]["players"][0]):
        await ctx.create_response("You can't kick players when you aren't the host.", ephemeral=True)
        return

    var[ctx.guild.id]["players"].remove(int(member.id))

    desired_value = member.id
    for key, value in var[ctx.guild.id]["playeremoji"].items():
        if value == desired_value:
            del var[ctx.guild.id]["playeremoji"][key]
            break

    for key, value in var[ctx.guild.id]["votingemoji"].items():
        if value == desired_value:
            del var[ctx.guild.id]["votingemoji"][key]
            break

    var[ctx.guild.id]["index"] -= 1
    embed = discord.Embed(title=f"**{member.name} has been kicked by the host!**", colour=discord.Colour(0xfff4d1))
    if (random.randint(1, 80000) == 9642):
        embed.description = "That's a shame..."

    embed.set_thumbnail(url=member.avatar_url)
    var[ctx.guild.id]["vkickd"][member.id] = 0
    await ctx.create_response(embed=embed)

    guilds[str(member.id)]["guild"] = 0
    guilds[str(member.id)]["joinedgame"] = False
    guilds[str(member.id)]["vkicktarget"] = 0
    for i in var[ctx.guild.id]["players"]:
        if (guilds[str(i)]["vkicktarget"] == member.id):
            guilds[str(i)]["vkicktarget"] = 0

@dislash.guild_only()
@slash.slash_command(
    name="clear",
    description="Clears the entire lobby. You must be the host to do this"
)
async def clear(ctx):
    try:
        var[ctx.guild.id]["test"]
    except:
        var[ctx.guild.id] = copy.deepcopy(temp)


    if (len(var[ctx.guild.id]["players"]) == 0):
        embed = discord.Embed(title=f"The game has already been cleared!", colour=discord.Colour(0xfff4d1))
        embed.description = "F"

        embed.set_thumbnail(url=ctx.author.avatar_url)
        await ctx.reply(embed=embed, ephemeral=True)
        return

    if (var[ctx.guild.id]["started"] == True):
        await ctx.reply("You can't clear the game when it already started.", ephemeral=True)
        return

    for i in var[ctx.guild.id]["players"]:
        guilds[str(i)]["guild"] = 0
        guilds[str(i)]["joinedgame"] = False
        guilds[str(i)]["vkicktarget"] = 0

    var[ctx.guild.id]["players"] = None
    var[ctx.guild.id]["players"] = []


    var[ctx.guild.id]["playeremoji"] = None
    var[ctx.guild.id]["playeremoji"] = {}

    var[ctx.guild.id]["votingemoji"] = None
    var[ctx.guild.id]["votingemoji"] = {}

    embed = discord.Embed(title=f"The game has been cleared!", colour=discord.Colour(0xfff4d1))
    if (random.randint(1, 80000) == 6969):
        embed.description = "F"

    embed.set_thumbnail(url=ctx.author.avatar_url)
    await ctx.reply(embed=embed)



@bot.command()
async def start(ctx):
    await _start(ctx)

@dislash.guild_only()
@slash.slash_command(
    name="start",
    description="Start a game of Anarchic"
)
async def sstart(inter):
    await _start(inter, True)

async def _start(ctx, inter=False):
    try:
        var[ctx.guild.id]["test"]
    except:
        var[ctx.guild.id] = copy.deepcopy(temp)

    if (len(var[ctx.guild.id]["players"]) == 0):
        if (inter == True):
            await ctx.reply("How do you expect me to start a game with nobody in it?", ephemeral=True)
        else:
            await ctx.send("How do you expect me to start a game with nobody in it?")
        return

    if (ctx.author.id != var[ctx.guild.id]["players"][0]):
        if (inter == True):
            await ctx.reply("Only the host can start the game!",ephemeral=True)
        else:
            await ctx.send("Only the host can start the game!")
        return

    s = var[ctx.guild.id]["setupz"]
    if (s.lower() != "custom"):
        if (4 >= len(var[ctx.guild.id]["players"]) and s.lower() == "any"):
            if (inter == True):
                await ctx.reply(f"There are too little players in the game! There should be 5 or more players.",ephemeral=True)
            else:
                await ctx.send(f"There are too little players in the game! There should be 5 or more players.")
            return
        else:
            if (s.lower() != "any"):
                c = var[ctx.guild.id]["comps"]

                lines = len(var[ctx.guild.id]["players"])
                if (lines > len(c[s.lower()])):
                        if (inter == True):
                            await ctx.reply(f"There are too many players in the game! There should be {len(c[s])} players.",ephemeral=True)
                        else:
                            await ctx.send(f"There are too many players in the game! There should be {len(c[s])} players.")
                        return

                if (lines < len(c[s.lower()])):
                    if (inter == True):
                        await ctx.reply(f"There aren't enough players in the game! There should be {len(c[s])} players.",ephemeral=True)
                    else:
                        await ctx.send(f"There aren't enough players in the game! There should be {len(c[s])} players.")
                    return
    else:
        c = var[ctx.guild.id]["comps"]
        if (len(c["custom"]) < 2):
            await ctx.reply("The setup is too small to be playable! There should at least 2 roles in the setup.", ephemeral=True)
            return

        if ("Mafioso" not in c["custom"]):
            await ctx.reply("The setup must have a mafioso in the game!", ephemeral=True)
            return

        lines = len(var[ctx.guild.id]["players"])
        if (lines > len(c[s.lower()])):
                if (inter == True):
                    await ctx.reply(f"There are too many players in the game! There should be {len(c[s])} players.",ephemeral=True)
                else:
                    await ctx.send(f"There are too many players in the game! There should be {len(c[s])} players.")
                return

        if (lines < len(c[s.lower()])):
            if (inter == True):
                await ctx.reply(f"There aren't enough players in the game! There should be {len(c[s])} players.",ephemeral=True)
            else:
                await ctx.send(f"There aren't enough players in the game! There should be {len(c[s])} players.")
            return

    if (inter == True):
        await ctx.reply(type=5)

    for i in var[ctx.guild.id]["playerdict"].values():
        i.reset()

    var[ctx.guild.id]["playeremoji"] = None
    var[ctx.guild.id]["playeremoji"] = {}
    var[ctx.guild.id]["index"] = 0

    #Finish off the B bug once and for all!
    for i in var[ctx.guild.id]["players"]:
        var[ctx.guild.id]["playeremoji"][var[ctx.guild.id]["emojis"][var[ctx.guild.id]["index"]]] = i
        var[ctx.guild.id]["index"] += 1

    guild = ctx.guild
    if (var[ctx.guild.id]["started"] == False):
        var[ctx.guild.id]["started"] = True
        var[ctx.guild.id]["result"] = False
        var[ctx.guild.id]["voting"] = False
        var[ctx.guild.id]["guildg"] = ctx.guild
        if (discord.utils.get(ctx.guild.roles, name="[Anarchic] Player") == None):
            await guild.create_role(name="[Anarchic] Player")

        if (discord.utils.get(ctx.guild.roles, name="[Anarchic] Dead") == None):
            await guild.create_role(name="[Anarchic] Dead")

        for i in var[ctx.guild.id]["players"]:
            role = discord.utils.get(ctx.guild.roles, name="[Anarchic] Player")
            user = ctx.guild.get_member(i)
            await user.add_roles(role)

        var[ctx.guild.id]["gday"] = 1
        var[ctx.guild.id]["nightg"] = 1
        var[ctx.guild.id]["daysnokill"] = 0
        if (inter == False):
            await ctx.message.add_reaction("✅")
        overwrites = discord.PermissionOverwrite()
        overwrites.read_messages = False
        overwrites.send_messages = False
        f = await guild.create_category("Anarchic", reason="Game of Anarchic")
        await f.set_permissions(ctx.guild.default_role, overwrite=overwrites)
        overwrites.read_messages = True
        overwrites.send_messages = True
        var[ctx.guild.id]["startchannel"] = ctx.channel

        overwrite = discord.PermissionOverwrite()
        overwrite.read_messages = True

        # for i in var[ctx.guild.id]["players"]:
        #     user = await ctx.guild.fetch_member(i)
        #     await f.set_permissions(user, overwrite=overwrite)

        await f.set_permissions(discord.utils.get(ctx.guild.roles, name="[Anarchic] Player"), overwrite=overwrites)
        
        embed = discord.Embed(title="**Welcome to the Graveyard <:rip:872284978354978867>!**", colour=discord.Colour(0x300036), description="This is a place for dead players to talk, discuss and complain about the living.")

        embed.set_image(url="https://cdn.discordapp.com/attachments/878437549721419787/883854521753813022/unknown.png")
        embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png?width=374&height=374")

        embed.add_field(name="**Rules :pushpin:**", value="Here are some guidelines to follow.", inline=False)
        embed.add_field(name="No Dead Info :newspaper2:.", value="Do not give dead info. Once you're dead, you're dead. You may only talk about the game here.", inline=False)
        embed.add_field(name="Only Preview :eyes:", value="Specators are not allowed to interact in any way with the living .", inline=False)

        chan = await f.create_text_channel("town-square", reason="Anarchic Setup")
        die = await f.create_text_channel("graveyard", reason="Anarchic setup")

        guild = ctx.guild
        overwrites = discord.PermissionOverwrite(read_messages=False)

        maf = await f.create_text_channel("mafia-contacts", reason="Anarchic setup")


        var[ctx.guild.id]["diechannel"] = die
        var[ctx.guild.id]["mafcon"] = maf

        overwrites.read_messages = False
        overwrites.send_messages = False

        await die.set_permissions(discord.utils.get(ctx.guild.roles, name="[Anarchic] Player"), overwrite=overwrites)

        overwrites.read_messages = True
        overwrites.send_messages = True
        await die.set_permissions(discord.utils.get(ctx.guild.roles, name="[Anarchic] Dead"), overwrite=overwrites)

        var[ctx.guild.id]["channel"] = chan
        await var[ctx.guild.id]["diechannel"].send(embed=embed)

        if (inter == True):
            try:
                await ctx.edit(f"A game has started! Everyone in the game should check {chan.mention}.")
            except:
                await ctx.channel.send(f"A game has started! Everyone in the game should check {chan.mention}.")
        else:
            await ctx.channel.send(f"A game has started! Everyone in the game should check {chan.mention}.")        
        await lock(chan)
        embed = discord.Embed(title="**Welcome to Anarchic.**", colour=discord.Colour(0x6efff3), description="Anarchic is game of deceit and deception, based off of the Mafia Party game. To learn how to play, check below.")

        embed.set_image(url="https://cdn.discordapp.com/attachments/878437549721419787/882712063904976926/welcome.png")
        embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png?width=374&height=374")
        embed.set_footer(text="Good luck.")

        embed.add_field(name="**How to Play💡**", value="Each player is secretly assigned a role at the start of the game and has to fulfill their goal. To see the list of roles, try typing `/roles`. The game alternates between a day and night cycle. For more infomation, use `/howtoplay`.", inline=False)
        embed.add_field(name="**Rules :pushpin:**", value="Here are a list of rules to follow.", inline=False)
        embed.add_field(name="**No Screenshoting :camera_with_flash:**", value="Screenshoting is strictly forbidden, as it is cheeating ruins the game for everyone.", inline=False)
        embed.add_field(name="**No Copy And Pasting :pencil:**", value="Copy and pasting is also considered breaking the rules, as it is also cheating.", inline=False)
        embed.add_field(name="No Direct Messaging 💬", value="Direct Messaging is not allowed as it ruins many game mechanics. ",inline=False)
        embed.add_field(name="Names Policy :man_gesturing_no:", value="Names must be set to a typeable english name, for players to be able to select you.",inline=False)

        await chan.send(content=discord.utils.get(ctx.guild.roles, name="[Anarchic] Player").mention, embed=embed)

        await asyncio.sleep(3)

        e = random.randint(1,1000000000)
        random.seed(e)

        try:
            await assignroles(var[ctx.guild.id]["setupz"], ctx.guild)
        except ValueError:
            embed = discord.Embed(title="The bot is lacking permissions to perform an action", colour=discord.Colour(0xea5f61), description="**Either someone disabled DMs with server members, or the bot is missing role permssions to perform an action.**")

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")
            embed.set_footer(text="If this keeps happening, contact support with `/invite`", icon_url=ctx.author.avatar_url)

            await chan.send(embed=embed)
            await asyncio.sleep(2)

            await chan.send("Deleting the channels in 5 seconds...")

            var[guild.id]["started"] = None
            var[guild.id]["voted"] = None
            var[guild.id]["timer"] = None
            var[guild.id]["targets"] = None
            var[guild.id]["gday"] = None
            var[guild.id]["guiltyers"] = None
            var[guild.id]["abstainers"] = None

            var[guild.id]["started"] = False
            var[guild.id]["result"] = False
            var[guild.id]["voted"] = {}
            var[guild.id]["gday"] = 0
            var[guild.id]["timer"] = 0
            var[guild.id]["ind"] = 0
            var[guild.id]["isresults"] = False
            var[guild.id]["diechannel"] = None
            var[guild.id]["mafcon"] =None
            var[guild.id]["chan"] = None
            var[guild.id]["targets"] = {}
            var[guild.id]["guiltyers"] = []
            var[guild.id]["abstainers"] = []

            await asyncio.sleep(5)

            for i in chan.category.channels:
                await i.delete()

            await chan.category.delete()

            g = discord.utils.get(guild.roles, name="[Anarchic] Player")
            d = discord.utils.get(guild.roles, name="[Anarchic] Dead")

            await g.delete()
            await d.delete()
            return

        for i in var[ctx.guild.id]["players"]:
            if (Player.get_player(i, var[chan.guild.id]["playerdict"]).faction == Faction.Mafia):
                overwrites.read_messages = True
                overwrites.send_messages = True
                await maf.set_permissions(ctx.guild.get_member(i), overwrite=overwrites)
            else:
                overwrites.read_messages = False
                overwrites.send_messages = False
                await maf.set_permissions(ctx.guild.get_member(i), overwrite=overwrites)

        overwrites.read_messages = False
        overwrites.send_messages = False

        await maf.set_permissions(discord.utils.get(ctx.guild.roles, name="[Anarchic] Player"), overwrite=overwrites)

        embed = None
        message = ""

        embed = discord.Embed(title="**Your Mafia team for the game <:maficon2:890328238029697044>.**", colour=discord.Colour(0xd0021b))

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/890328238029697044.png?size=80")
        embed.set_footer(text="Good luck.", icon_url="https://cdn.discordapp.com/attachments/878437549721419787/883074983759347762/anarpfp.png")

        for i in var[ctx.guild.id]["players"]:
            if (Player.get_player(i, var[chan.guild.id]["playerdict"]).faction == Faction.Mafia): 
                user = Player.get_player(i, var[chan.guild.id]["playerdict"])
                p = var[ctx.guild.id]["emoji"][user.role.lower()]
                embed.add_field(name=f"**{string.capwords(user.role)} {p}**", value=f"{bot.get_user(i).mention}", inline=False)
                message += bot.get_user(i).mention + " "

        await maf.send(embed=embed, content=message)

        overwrites.read_messages = True
        overwrites.send_messages = True

        var[ctx.guild.id]["voting"] = False

        for i in var[ctx.guild.id]["playerdict"].values():
            if (i.role.lower() == "psychic"):
                user = await ctx.guild.fetch_member(i.id)
                await die.set_permissions(user, overwrite=overwrites)

        await asyncio.sleep(2)

        embed = None
        embed = discord.Embed(title="**It Is Day 1 ☀️.**", colour=discord.Colour(0x7ed321))

        embed.set_image(url="https://images-ext-2.discordapp.net/external/8cFuWNzv5vDa4TbO68gg5Up4DSxguodCGurCAtDpWgU/%3Fwidth%3D936%26height%3D701/https/media.discordapp.net/attachments/765738640554065962/878068703672016968/unknown.png")
        embed.set_footer(text="Talk, Bait, Claim.")

        b = var[ctx.guild.id]["players"]

        message = ""
        for i in var[ctx.guild.id]["players"]:
            user = await ctx.channel.guild.fetch_member(int(i))
            message += f"{user.mention}"
            message += "\n"

        embed.add_field(name=f"Players: `{len(b)}`", value=message, inline=True)

        message = ""
        if (var[ctx.guild.id]["setupz"].lower() != "any"):
            c = var[ctx.guild.id]["comps"]
            s = copy.copy(c[var[ctx.guild.id]["setupz"]])
            em = var[ctx.guild.id]["emoji"]
            for i in s:
                if (i == "RT"):
                    message += f"**Random Town** {em[i.lower()]}\n"
                elif (i == "RM"):
                    message += f"**Random Mafia** {em[i.lower()]}\n"
                elif (i == "RN"):
                    message += f"**Random Neutral** {em[i.lower()]}\n"
                elif (i == "TI"):
                    message += f"**Town Investigative** {em[i.lower()]}\n"
                elif (i == "TS"):
                    message += f"**Town Support** {em[i.lower()]}\n"
                else:
                    message += f"**{string.capwords(i)}** {em[i.lower()]}\n"
            
            s = var[ctx.guild.id]["setupz"]
            embed.add_field(name=f"Setup: `{string.capwords(s)}`", value=message, inline=True)
        else:
            embed.add_field(name=f"Setup: `All Any`", value="**:game_die: Any x the amount of players playing :partying_face:**", inline=True)


        role = discord.utils.get(ctx.guild.roles,name="[Anarchic] Player")

        await chan.send(f"{role.mention}\n━━━━━━━━━━━━━━━━━━━━━━━━━━", embed=embed)
        await asyncio.sleep(1)
        await unlock(chan)
        await asyncio.sleep(15)
        await lock(chan)

        dad = var[ctx.guild.id]["gday"]
        embed = discord.Embed(title=f"**It is Night 1 :crescent_moon:.**", colour=discord.Colour(0x1f0050))

        embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/878070289194426399/unknown.png?width=925&height=701")
        message = ""
        for i in var[ctx.guild.id]["playerdict"].values():
            if (i.dead==False and i.id != 0):
                message += f"{bot.get_user(i.id).mention}\n" 
        if (message == ""):
            message = "** **"

        embed.add_field(name="**Alive Townies <:townicon2:896431548717473812>:**", value=message, inline=True)
        message = ""
        for i in var[ctx.guild.id]["playerdict"].values():
            if (i.dead==True and i.id != 0):
                em = var[ctx.guild.id]["emoji"]
                d = var[ctx.guild.id]["playerdict"]
                if (i.diedln == True):
                    message += f"{bot.get_user(i.id).mention} -  **?**\n" 
                else:
                    message += f"{bot.get_user(i.id).mention} -  **{Player.get_player(i.id, d).role.capitalize()}** {em[Player.get_player(i.id, d).role.lower()]}\n" 
        if (message == ""):
            message = "** **"
        embed.add_field(name="**Graveyard <:rip:872284978354978867>:**", value=message, inline=True)
        
        await chan.send(embed=embed)

        if (len(getTownies(ctx.guild)) == 0 and len(getMaf(ctx.guild)) == 0):
            b = await EndGame(EndReason.Draw, var[ctx.guild.id]["channel"].guild)
            await var[ctx.guild.id]["channel"].send(embed=b)
            await var[ctx.guild.id]["startchannel"].send(embed=b)
            perm = discord.PermissionOverwrite()
            perm.read_messages = True
            perm.send_messages = True

            role = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
            roled = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

            await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
            perm.send_messages = False
            await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

            var[ctx.guild.id]["result"] = True
            return
        if (len(getTownies(ctx.guild)) == 0):
            b = await EndGame(EndReason.MafiaWins, var[ctx.guild.id]["channel"].guild)
            await var[ctx.guild.id]["channel"].send(embed=b)
            await var[ctx.guild.id]["startchannel"].send(embed=b)
            perm = discord.PermissionOverwrite()
            perm.read_messages = True
            perm.send_messages = True

            role = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
            roled = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

            await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
            perm.send_messages = False
            await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

            var[ctx.guild.id]["result"] = True
            return
        elif (len(getMaf(ctx.guild)) == 0):
            b = await EndGame(EndReason.TownWins, var[ctx.guild.id]["channel"].guild)
            await var[ctx.guild.id]["channel"].send(embed=b)
            await var[ctx.guild.id]["startchannel"].send(embed=b)
            perm = discord.PermissionOverwrite()
            perm.read_messages = True
            perm.send_messages = True

            role = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
            roled = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

            await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
            perm.send_messages = False
            await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

            var[ctx.guild.id]["result"] = True
            return

        await night(chan)
    else:
        if (inter == False):
            await ctx.send("A game has already started!")
        else:
            await ctx.reply("A game has already started!")
@bot.command()
async def removeroles(ctx):
    await ctx.send("E")
    if (ctx.author.id == 839842855970275329 or ctx.author.id == 667189788620619826):
        guild:discord.Guild = ctx.guild
        g = discord.utils.get(guild.roles, name="[Anarchic] Player")
        d = discord.utils.get(guild.roles, name="[Anarchic] Dead")

        await ctx.send("Removing roles, please wait!")
        start_time = time.time()

        for f in guild.members:

            r:discord.Member = f
            yea = r.roles
            try:
                yea.remove(g)
            except:
                pass

            try:
                yea.remove(d)
            except:
                pass

            await r.edit(roles=yea)

        end_time = time.time()

        time_elapsed = (end_time - start_time)
        await ctx.send("Took " + str(timedelta(seconds=time_elapsed)))

        await ctx.send("Done!")

@slash.slash_command()
async def will(inter):
    pass

@dislash.guild_only()
@will.sub_command(
    name="write",
    description="Write in your will",
    options=[Option("text", "The text in the inserting part", OptionType.STRING, True), Option("line", "The line you want to insert in", OptionType.INTEGER, False)]
)
async def writeWill(ctx:SlashInteraction, text=None, line=None):
    try:
        var[ctx.guild.id]["test"]
    except:
        var[ctx.guild.id] = copy.deepcopy(temp)

    if (ctx.author.id not in var[ctx.guild.id]["players"]):
        embed = discord.Embed(title="You aren't in the game...", description="Try joining the game and starting it.")
        await ctx.reply(embed=embed, ephemeral=True)
        return
    else:
        if (var[ctx.guild.id]["started"] == False):
            embed = discord.Embed(title="The game hasn't started yet...", description="Start the game then try again.")
            await ctx.reply(embed=embed, ephemeral=True)
            return
        else:
            if ("\\" in text):
                embed = discord.Embed(title="You can't add backslashes in your will.", description="Backslashes will break the game!")
                await ctx.reply(embed=embed, ephemeral=True)
                return

            myPlayer = Player.get_player(ctx.author.id, var[ctx.guild.id]["playerdict"])

            if (myPlayer.dead == True):
                embed = discord.Embed(title="You're dead.", description="Please be alive and try again.")
                await ctx.reply(embed=embed, ephemeral=True)
                return

            if (line == None):
                myPlayer.will.append(text)
            else:
                myPlayer.will.insert(int(line) - 1, text)

            will = getWill(myPlayer.will)

            #Add components
            row = ActionRow(
                Button(
                    style=ButtonStyle.gray,
                    label="Post Will",
                    emoji="🗒️",
                    custom_id="post"
                )
            )

            #Create embed
            embed = discord.Embed(title=f"**:scroll: {ctx.author.name}'s Will :scroll:**", colour=discord.Colour(0x9902b8), description=will)

            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.set_footer(text="Remember to update your will!", icon_url=ctx.author.avatar_url)

            #Send messagse
            msg = await ctx.reply(embed=embed, components=[row], ephemeral=True)
            click = msg.create_click_listener(timeout=60)

            @click.not_from_user(ctx.author, cancel_others=True, reset_timeout=False)
            async def on_wrong_user(inter):
                await inter.reply("Only the message author can post their will. How about posting YOUR OWN will and not someone elses?", ephemeral=True)

            @click.matching_id("post")
            async def postWill(inter):
                row.disable_buttons()
                await ctx.edit(components=[row])
                
                embed = discord.Embed(title=f":scroll: {ctx.author.name}'s Will :scroll:", colour=discord.Colour(0xbd10e0), description=will)

                embed.set_thumbnail(url=ctx.author.avatar_url)
                embed.set_footer(text="Remember to update your will!", icon_url=ctx.author.avatar_url)
                await inter.reply(embed=embed)

            @click.timeout
            async def timeout():
                row.disable_buttons()

                await ctx.edit(components=[row])

@dislash.guild_only()
@will.sub_command(
    name="remove",
    description="Remove a line in your will",
    options=[Option("line", "The line you want to remove", OptionType.INTEGER, True)]
)
async def removeWill(ctx, line=None):
    try:
        var[ctx.guild.id]["test"]
    except:
        var[ctx.guild.id] = copy.deepcopy(temp)

    if (ctx.author.id not in var[ctx.guild.id]["players"] is None):
        embed = discord.Embed(title="You aren't in the game...", description="Try joining the game and starting it.")
        await ctx.reply(embed=embed, ephemeral=True)
        return
    else:
        if (var[ctx.guild.id]["started"] == False):
            embed = discord.Embed(title="The game hasn't started yet...", description="Start the game then try again.")
            await ctx.reply(embed=embed, ephemeral=True)
            return
        else:
            if (int(line) < 1):
                embed = discord.Embed(title="That's an invalid line.", description="Please choose a usable line in the will system.")
                await ctx.reply(embed=embed, ephemeral=True)
                return

            myPlayer = Player.get_player(ctx.author.id, var[ctx.guild.id]["playerdict"])
            
            if (myPlayer.dead == True):
                embed = discord.Embed(title="You're dead.", description="Please be alive and try again.")
                await ctx.reply(embed=embed, ephemeral=True)
                return

            myPlayer.will.pop(int(line) - 1)
            will = getWill(myPlayer.will)

            #Add components
            row = ActionRow(
                Button(
                    style=ButtonStyle.gray,
                    label="Post Will",
                    emoji="🗒️",
                    custom_id="post"
                )
            )

            #Create embed
            embed = discord.Embed(title=f"**:scroll: {ctx.author.name}'s Will :scroll:**", colour=discord.Colour(0x9902b8), description=will)

            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.set_footer(text="Remember to update your will!", icon_url=ctx.author.avatar_url)

            #Send messagse
            msg = await ctx.reply(embed=embed, components=[row], ephemeral=True)
            click = msg.create_click_listener(timeout=60)

            @click.not_from_user(ctx.author, cancel_others=True, reset_timeout=False)
            async def on_wrong_user(inter):
                await inter.reply("Only the message author can post their will. How about posting YOUR OWN will and not someone elses?", ephemeral=True)

            @click.matching_id("post")
            async def postWill(inter):
                row.disable_buttons()
                await ctx.edit(components=[row])
                embed = discord.Embed(title=f":scroll: {ctx.author.name}'s Will :scroll:", colour=discord.Colour(0xbd10e0), description=will)

                embed.set_thumbnail(url=ctx.author.avatar_url)
                embed.set_footer(text="Remember to update your will!", icon_url=ctx.author.avatar_url)
                await inter.reply(embed=embed)

            @click.timeout
            async def timeout():
                row.disable_buttons()
                await ctx.edit(components=[row])

@dislash.guild_only()
@will.sub_command(
    name="view",
    description="See the amount of quality you put into your will",
    options=[
        Option(name="member", description="The user's will you want to view", type=OptionType.MENTIONABLE)
    ]
)
async def viewWill(ctx, member=None):
    try:
        var[ctx.guild.id]["test"]
    except:
        var[ctx.guild.id] = copy.deepcopy(temp)

    if (ctx.author.id not in var[ctx.guild.id]["players"]):
        embed = discord.Embed(title="You aren't in the game...", description="Try joining the game and starting it.")
        await ctx.reply(embed=embed, ephemeral=True)
        return
    else:
        if (var[ctx.guild.id]["started"] == False):
            embed = discord.Embed(title="The game hasn't started yet...", description="Start the game then try again.")
            await ctx.reply(embed=embed,ephemeral=True)
            return
        else:
            if (member == None):
                #Get Player will
                myPlayer = Player.get_player(ctx.author.id, var[ctx.guild.id]["playerdict"])
                mywill = getWill(myPlayer.will)

                #Add components
                row = ActionRow(
                    Button(
                        style=ButtonStyle.gray,
                        label="Post Will",
                        emoji="🗒️",
                        custom_id="post"
                    )
                )

                if (myPlayer.dead == True):
                    row.disable_buttons()

                #Create embed
                embed = discord.Embed(title=f"**:scroll: {ctx.author.name}'s Will :scroll:**", colour=discord.Colour(0x9902b8), description=mywill)

                embed.set_thumbnail(url=ctx.author.avatar_url)
                embed.set_footer(text="Remember to update your will!", icon_url=ctx.author.avatar_url)

                #Send messagse
                msg = await ctx.reply(embed=embed, components=[row], ephemeral=True)
                click = msg.create_click_listener(timeout=60)

                @click.not_from_user(ctx.author, cancel_others=True, reset_timeout=False)
                async def on_wrong_user(inter):
                    await inter.reply("Only the message author can post their will. How about posting YOUR OWN will and not someone elses?", ephemeral=True)

                @click.matching_id("post")
                async def postWill(inter):
                    row.disable_buttons()
                    await ctx.edit(components=[row])

                    embed = discord.Embed(title=f":scroll: {ctx.author.name}'s Will :scroll:", colour=discord.Colour(0xbd10e0), description=mywill)

                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    embed.set_footer(text="Remember to update your will!", icon_url=ctx.author.avatar_url)
                    await inter.reply(embed=embed)

                @click.timeout
                async def timeout():
                    row.disable_buttons()

                    await ctx.edit(components=[row])
            else:
                if (member.id not in var[ctx.guild.id]["players"]):
                    embed = discord.Embed(title="That player isn't in the game...", description="Try getting them to join the game.")
                    await ctx.reply(embed=embed, ephemeral=True)
                    return

                myPlayer = Player.get_player(member.id, var[ctx.guild.id]["playerdict"])
                mywill = getWill(myPlayer.will)

                if (myPlayer.dead == False):
                    if (var[ctx.guild.id]["result"] == False):
                        embed = discord.Embed(title="That player is alive...", description="Try killing them and try again.")
                        await ctx.reply(embed=embed, ephemeral=True)
                        return

                embed = discord.Embed(title=f"**:scroll: {member.name}'s Will :scroll:**", colour=discord.Colour(0x9902b8), description=mywill)

                embed.set_thumbnail(url=member.avatar_url)
                embed.set_footer(text="Remember to update your will!", icon_url=ctx.author.avatar_url)

                await ctx.reply(embed=embed, ephemeral=True)







async def night(ctx):
    var[ctx.guild.id]["trialuser"] = 0 
    var[ctx.guild.id]["guiltyinno"] = False
    r = []
    m = []

    var[ctx.guild.id]["voting"] = False

    var[ctx.guild.id]["resul"] = 0
    var[ctx.guild.id]["targets"]= {}
    var[ctx.guild.id]["nightd"] += 1

    for i in var[ctx.guild.id]["playerdict"].values():
        i.ready = False

        if (i.checked == False):
            i.checked = False
            i.framed = False

        if (i.dead == True):
            continue

        if (i.role.lower() == "mafioso"):
            r.append(i)

        if (i.faction == Faction.Mafia and i.role.lower() != "mafioso"):
            m.append(i)

    if (len(r) == 0):
        play:Player = random.choice(m)
        user = bot.get_user(play.id)
        embed = discord.Embed(title="**You have been promoted to a Mafioso!**", colour=0xd0021b)

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/891739940055052328.png?size=80")
        embed.set_footer(text="Good luck.", icon_url=user.avatar_url)
        await user.send(embed=embed)

        embed = discord.Embed(title=f"**{user.name} has been promoted to a Mafioso!**", colour=0xd0021b)

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/891739940055052328.png?size=80")
        embed.set_footer(text="Good luck.", icon_url=user.avatar_url)

        await var[ctx.guild.id]["mafcon"].send(embed=embed)

        play.reset(True)

        play.id = user.id
        play.role = "Mafioso"
        play.faction = Faction.Mafia #The player's faction (Town, Mafia, Neutral)
        play.appearssus = True #If the player appears sus
        play.detresult = "Your target seeks revenge. They must be a **Cop <:copicon2:889672912905322516>**, **Headhunter <:hhicon2:891429754643808276>**, **Mafioso <:maficon2:891739940055052328>** or **Enforcer <:enficon2:890339050865696798>**." #Det results
        play.defense = Defense.Default #defense
        play.distraction = False #consort

    var[ctx.guild.id]["isresults"] = False

    for i in var[ctx.guild.id]["players"]:
        m = bot.get_user(i)

        asyncio.create_task(
        target(m, ctx.guild.id))

async def day(ctx):
    var[ctx.guild.id]["ind"] += 1

    if (var[ctx.guild.id]["ind"] > 1):
        var[ctx.guild.id]["ind"] -= 1
        return
    var[ctx.guild.id]["gday"] += 1

    for i in var[ctx.guild.id]["playerdict"].values():
        i.doc = False
        i.ready = False
        i.voted = False
        i.votedforwho = None
        i.distraction = False
        if (i.role.lower() == "headhunter"):
            oh = Player.get_player(i.hhtarget, var[ctx.guild.id]["playerdict"])
            if (oh.diedln == True and i.wins == False):
                if (i.dead == False):
                    i.role = "Jester"
                    i.faction = Faction.Neutral
                    i.defense = Defense.Default
                    embed = discord.Embed(title="**Your target has died. You have been converted into a Jester**", colour=discord.Colour(0xffc3e7))

                    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/872187561597075476.png?v=1")
                    embed.set_footer(text="/role jester for more info.", icon_url=bot.get_user(i.id).avatar_url)
                    await bot.get_user(i.id).send(embed=embed)

    r = []
    m = []
    for i in var[ctx.guild.id]["playerdict"].values():
        if (i.dead == True):
            continue

        if (i.role.lower() == "mafioso"):
            r.append(i)

        if (i.faction == Faction.Mafia and i.role.lower() != "mafioso"):
            m.append(i)

    if (len(r) == 0 and len(m) != 0):
        play:Player = random.choice(m)
        user = bot.get_user(play.id)
        embed = discord.Embed(title="**You have been promoted to a Mafioso!**", colour=0xd0021b)

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/891739940055052328.png?size=80")
        embed.set_footer(text="Good luck.", icon_url=user.avatar_url)
        await user.send(embed=embed)

        embed = discord.Embed(title=f"**{user.name} has been promoted to a Mafioso!**", colour=0xd0021b)

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/891739940055052328.png?size=80")
        embed.set_footer(text="Good luck.", icon_url=user.avatar_url)

        await var[ctx.guild.id]["mafcon"].send(embed=embed)

        play.reset(True)

        play.id = user.id
        play.role = "Mafioso"
        play.faction = Faction.Mafia #The player's faction (Town, Mafia, Neutral)
        play.appearssus = True #If the player appears sus
        play.detresult = "Your target seeks revenge. They must be a **Cop <:copicon2:889672912905322516>**, **Headhunter <:hhicon2:891429754643808276>**, **Mafioso <:maficon2:891739940055052328>** or **Enforcer <:enficon2:890339050865696798>**." #Det results
        play.defense = Defense.Default #defense
        play.distraction = False #consort

    died = 0
    role = discord.utils.get(ctx.guild.roles,name="[Anarchic] Player")

    da = var[ctx.guild.id]["gday"]
    r = 0

    for i in var[ctx.guild.id]["playerdict"].values():
        if (i.diedln == True):
            var[ctx.guild.id]["daysnokill"] = 0
            r = 999
            break

    if (r == 0):
        var[ctx.guild.id]["daysnokill"] += 1
        

    if (var[ctx.guild.id]["daysnokill"] == 3):
        for i in var[ctx.guild.id]["playerdict"].values():
            if (i.id != 0):
                if (i.dead == False):
                    i.diedln = True

                i.dead = True
                i.death.append(DeathReason.Plague)



    embed = discord.Embed(title=f"**It is Day {da} ☀️.**", colour=discord.Colour(0xff8900))

    embed.set_image(url="https://images-ext-2.discordapp.net/external/8cFuWNzv5vDa4TbO68gg5Up4DSxguodCGurCAtDpWgU/%3Fwidth%3D936%26height%3D701/https/media.discordapp.net/attachments/765738640554065962/878068703672016968/unknown.png")
    message = ""

    for i in var[ctx.guild.id]["playerdict"].values():
        if (i.dead==False and i.id != 0):
            message += f"{bot.get_user(i.id).mention}\n" 

    if (message == ""):
        message = "** **"

    embed.add_field(name="**Alive Townies <:townicon2:896431548717473812>:**", value=message, inline=True)
    message = ""

    for i in var[ctx.guild.id]["playerdict"].values():
        if (i.dead==True and i.id != 0):
            em = var[ctx.guild.id]["emoji"]
            d = var[ctx.guild.id]["playerdict"]
            if (i.diedln == True):
                message += f"{bot.get_user(i.id).mention} -  **?**\n" 
            else:
                message += f"{bot.get_user(i.id).mention} -  **{Player.get_player(i.id, d).role.capitalize()}** {em[Player.get_player(i.id, d).role.lower()]}\n" 
            

    if (message == ""):
        message = "** **"

    embed.add_field(name="**Graveyard <:rip:872284978354978867>:**", value=message, inline=True)

    r = var[ctx.guild.id]["playerdict"]
    await var[ctx.guild.id]["channel"].send(content=f"{role.mention}", embed=embed)
    await asyncio.sleep(2)

    for i in var[ctx.guild.id]["playerdict"].values():
        if (i.dead == True and i.id != 0):
            u = bot.get_user(i.id)

    for e in var[ctx.guild.id]["playerdict"].values():
        if (e.diedln == True):
            e.diedln = False
            died = 69
            var[ctx.guild.id]["daysnokill"] = 0

            if (len(e.death) == 0):
                e.death[0] == DeathReason.NoReason

            for i in e.death:
                user:discord.User = bot.get_user(e.id)
                embed = discord.Embed(title=f"**{user.name}#{user.discriminator} died last night.**", colour=reasontoColor(i), description=f"{reasonToText(i)}")

                embed.set_image(url=reasonToImage(i))
                embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/vdJanNHxHsByUKqoqKUfpoQVv0S5Ym7cv4uhJbqlv7c/%3Fv%3D1/https/cdn.discordapp.com/emojis/747726596475060286.png")

                if (getWill(Player.get_player(user.id, var[ctx.guild.id]["playerdict"]).will) != ""):
                    embed.add_field(name="**We found a will next to their body :scroll:.**", value=f"**{getWill(Player.get_player(user.id, r).will)}**", inline=False)
                
                p = var[ctx.guild.id]["emoji"]
                embed.add_field(name="**Their role was...**", value=f"**{Player.get_player(user.id, r).role.capitalize()} {p[Player.get_player(user.id, r).role.lower()]}**", inline=False)
                await var[ctx.guild.id]["channel"].send(embed=embed)
                await asyncio.sleep(2)

    if (died == 0):
        await var[ctx.guild.id]["channel"].send("Nobody died last night...")

    await asyncio.sleep(1)
    towns = getTownies(ctx.guild)
    mafs = getMaf(ctx.guild)

    for i in var[ctx.guild.id]["voted"].values():
        i = 0

    var[ctx.guild.id]["voted"] = None
    var[ctx.guild.id]["abstainers"] = None
    var[ctx.guild.id]["guiltyers"] = None

    var[ctx.guild.id]["voting"] = False
    var[ctx.guild.id]["novotes"] = False

    var[ctx.guild.id]["voted"] = {}
    var[ctx.guild.id]["abstainers"] = []
    var[ctx.guild.id]["guiltyers"] = []

    if (len(getTownies(ctx.guild)) == 0 and len(getMaf(ctx.guild)) == 0):
        b = await EndGame(EndReason.Draw, ctx.guild)
        await var[ctx.guild.id]["channel"].send(embed=b)
        await var[ctx.guild.id]["startchannel"].send(embed=b)
        perm = discord.PermissionOverwrite()
        perm.read_messages = True
        perm.send_messages = True

        role = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
        roled = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

        await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
        await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
        perm.send_messages = False
        await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
        await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

        var[ctx.guild.id]["result"] = True
        var[ctx.guild.id]["ind"] -= 1
        return
    if (len(towns) == 0):
        b = await EndGame(EndReason.MafiaWins, ctx.guild)
        await var[ctx.guild.id]["channel"].send(embed=b)
        await var[ctx.guild.id]["startchannel"].send(embed=b)
        perm = discord.PermissionOverwrite()
        perm.read_messages = True
        perm.send_messages = True

        role = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
        roled = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

        await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
        await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
        perm.send_messages = False
        await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
        await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

        var[ctx.guild.id]["result"] = True
        var[ctx.guild.id]["ind"] -= 1
        return
    elif (len(mafs) == 0):
        b = await EndGame(EndReason.TownWins, ctx.guild)
        await var[ctx.guild.id]["channel"].send(embed=b)
        await var[ctx.guild.id]["startchannel"].send(embed=b)
        perm = discord.PermissionOverwrite()
        perm.read_messages = True
        perm.send_messages = True

        role = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
        roled = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

        await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
        await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
        perm.send_messages = False
        await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
        await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

        var[ctx.guild.id]["result"] = True
        var[ctx.guild.id]["ind"] -= 1
        return

    for i in var[ctx.guild.id]["playerdict"].values():
        if (i.wasrevealed == True and i.dead == False):
            i.wasrevealed = False
            us = await ctx.guild.fetch_member(i.id)

            embed = discord.Embed(title=f"**{us.name}** has revealed themselves to be the Mayor!", colour=discord.Colour(0xbc9b25), description="They will now have 3 votes in all future voting procedures.")

            embed.set_image(url="https://cdn.discordapp.com/attachments/878437549721419787/882418844424081449/unknown.png")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/897570023143518288.png?size=80")
            await ctx.send(embed=embed)
            var[ctx.guild.id]["mayor"] = us
            await asyncio.sleep(3)
            break
    
    if (var[ctx.guild.id]["daysnokill"] == 2):
        embed = discord.Embed(title="**A plague has consumed the town!**", colour=discord.Colour(0xb8e986), description="If a player doesn't die by tomorrow, the game will end in a draw.")

        embed.set_image(url="https://o.remove.bg/downloads/9785243e-058d-4c48-a3c7-f116f207b075/unknown-removebg-preview.png")

        await ctx.send(embed=embed)


    i = var[ctx.guild.id]["gday"]
    await var[ctx.guild.id]["channel"].send(f"It's now Day {i}. Talk, Bait, Claim.")
    await unlock(var[ctx.guild.id]["channel"])
    await asyncio.sleep(45)
    aliveplayers = 0
    for i in var[ctx.guild.id]["playerdict"].values():
        if (i.dead == False and i.id != 0):
            aliveplayers += 1

    embed = discord.Embed(title=f"**It is time to vote :ballot_box:. {int(aliveplayers / 2 + 1)} votes are needed to send someone to trial :judge:.**", colour=discord.Colour(0xf5a623))

    embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/876183728953655306/unknown.png?width=679&height=701")
    embed.set_footer(text="Use `vote (@user)` to vote.")
    await ctx.send(embed=embed)

    var[ctx.guild.id]["voting"] = True
    timer = 45.0
    while (timer >= 0.0):
        await asyncio.sleep(0.1)
        timer = timer - 0.1

    if (var[ctx.guild.id]["novotes"] == False):
        dad = var[ctx.guild.id]["gday"]
        embed = discord.Embed(title=f"**It is Night {dad} :crescent_moon:.**", colour=discord.Colour(0x1f0050))

        embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/878070289194426399/unknown.png?width=925&height=701")
        message = ""
        for i in var[ctx.guild.id]["playerdict"].values():
            if (i.dead==False and i.id != 0):
                message += f"{bot.get_user(i.id).mention}\n" 
        if (message == ""):
            message = "** **"

        embed.add_field(name="**Alive Townies <:townicon2:896431548717473812>:**", value=message, inline=True)
        message = ""
        for i in var[ctx.guild.id]["playerdict"].values():
            if (i.dead==True and i.id != 0):
                em = var[ctx.guild.id]["emoji"]
                d = var[ctx.guild.id]["playerdict"]
                if (i.diedln == True):
                    message += f"{bot.get_user(i.id).mention} -  **?**\n" 
                else:
                    message += f"{bot.get_user(i.id).mention} -  **{Player.get_player(i.id, d).role.capitalize()}** {em[Player.get_player(i.id, d).role.lower()]}\n" 
        if (message == ""):
            message = "** **"
        embed.add_field(name="**Graveyard <:rip:872284978354978867>:**", value=message, inline=True)
        
        await ctx.send(embed=embed)

        await lock(ctx)
        if (len(getTownies(ctx.guild)) == 0 and len(getMaf(ctx.guild)) == 0):
            b = await EndGame(EndReason.Draw, ctx.guild)
            perm = discord.PermissionOverwrite()
            perm.read_messages = True
            perm.send_messages = True

            await var[ctx.guild.id]["startchannel"].send(embed=b)
            await var[ctx.guild.id]["channel"].send(embed=b)

            role = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
            roled = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

            await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
            perm.send_messages = False
            await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

            var[ctx.guild.id]["result"] = True
            var[ctx.guild.id]["ind"] -= 1
            return
        if (len(getTownies(ctx.guild)) == 0):
            b = await EndGame(EndReason.MafiaWins, ctx.guild)
            await var[ctx.guild.id]["channel"].send(embed=b)
            await var[ctx.guild.id]["startchannel"].send(embed=b)
            perm = discord.PermissionOverwrite()
            perm.read_messages = True
            perm.send_messages = True

            role = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
            roled = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

            await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
            perm.send_messages = False
            await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

            var[ctx.guild.id]["result"] = True
            var[ctx.guild.id]["ind"] -= 1
            return
        elif (len(getMaf(ctx.guild)) == 0):
            b = await EndGame(EndReason.TownWins, ctx.guild)
            await var[ctx.guild.id]["startchannel"].send(embed=b)
            await var[ctx.guild.id]["channel"].send(embed=b)
            perm = discord.PermissionOverwrite()
            perm.read_messages = True
            perm.send_messages = True

            role = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
            roled = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

            await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
            perm.send_messages = False
            await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

            var[ctx.guild.id]["result"] = True
            var[ctx.guild.id]["ind"] -= 1
            return
        var[ctx.guild.id]["ind"] -= 1
        var[ctx.guild.id]["targetint"] = 0

        for i in var[ctx.guild.id]["playerdict"].values():
            i.jesterwin = False

        await night(ctx)

@bot.command()
async def getouttahere(ctx):
    if (ctx.author.id == 839842855970275329):
        await ctx.send("lmao")
        await ctx.guild.leave()

@dislash.guild_only()
@slash.slash_command(
    title="guilty",
    description="Mark the current player on trial as guilty"
)
async def guilty(inter:SlashInteraction):
    r = inter.guild.id
    if (var[r]["guiltyinno"] == False):
        await inter.reply("Now's not the right time to mark someone as guilty...", ephemeral=True)
        return

    if (inter.author.id == var[r]["trialuser"]):
        await inter.reply("You can't mark yourself as guilty. Why would you, anyway?", ephemeral=True)
        return
    if (inter.author.id not in var[r]["players"]):
        await inter.reply("YOU'RE NOT EVEN IN THE GAME--", ephemeral=True)
        return

    if (inter.author.id in var[r]["abstainers"]):
        var[r]["abstainers"].remove(inter.author.id)
    elif (inter.author.id in var[r]["innoers"]):
        var[r]["innoers"].remove(inter.author.id)
    elif (inter.author.id in var[r]["guiltyers"]):
        var[r]["guiltyers"].remove(inter.author.id)

    var[r]["guiltyers"].append(inter.author.id)
    b = bot.get_user(var[r]["guyontrial"]).name 
    await inter.reply(f"You have marked {b} as **Guilty.**", ephemeral=True)
    await var[r]["channel"].send(f"{inter.author.name} has voted.")

@dislash.guild_only()
@slash.slash_command(
    title="inno",
    description="Mark the current player on trial as innocent"
)
async def innocent(inter:SlashInteraction):
    r = inter.guild.id
    if (var[r]["guiltyinno"] == False):
        await inter.reply("Now's not the right time to mark someone as innocent...", ephemeral=True)
        return

    if (inter.author.id == var[r]["trialuser"]):
        await inter.reply("You can't mark yourself as innocent.", ephemeral=True)
        return

    if (inter.author.id not in var[r]["players"]):
        await inter.reply("YOU'RE NOT EVEN IN THE GAME--", ephemeral=True)
        return

    if (inter.author.id in var[r]["abstainers"]):
        var[r]["abstainers"].remove(inter.author.id)
    elif (inter.author.id in var[r]["guiltyers"]):
        var[r]["guiltyers"].remove(inter.author.id)
    if (inter.author.id in var[r]["innoers"]):
        var[r]["innoers"].remove(inter.author.id)

    var[r]["innoers"].append(inter.author.id)

    b = bot.get_user(var[r]["guyontrial"]).name 
    await inter.reply(f"You have marked {b} as **Innocent.**", ephemeral=True)
    await var[r]["channel"].send(f"{inter.author.name} has voted.")

@dislash.guild_only()
@slash.slash_command(    
    description="Vote a player to lynch them"
    #  registration takes up to 1 hour
    )
async def vote(ctx:SlashInteraction):
    pass

@vote.sub_command(
    name="member",
    description="Vote a user to lynch them",
    options=[
        Option('member', 'The player to lynch', OptionType.USER, True)
        ]
)
async def voteMember(ctx, member=None):
    try:
        var[ctx.guild.id]["test"]
    except:
        var[ctx.guild.id] = copy.deepcopy(temp)

    if (member is None):
        embed = discord.Embed(title="**Sorry, that isn't a valid member.**", colour=discord.Colour(0xcce0ff), description="**Please choose a valid player that is alive in the game.**")

        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896419059988578344/downvote.png")
        embed.set_footer(text="Type `/vote` to vote.", icon_url=ctx.author.avatar_url)
        await ctx.create_response(embed=embed, ephemeral=True)
        return

    if (member.id in var[ctx.guild.id]["players"]):
        if (ctx.channel.name == "town-square"):
            e = random.uniform(0.2, 0.8)
            await asyncio.sleep(e)
            if (var[ctx.guild.id]["voting"] == True and var[ctx.guild.id]["gday"] != 1 and var[ctx.guild.id]["started"] == True and var[ctx.guild.id]["novotes"] == False):
                if (Player.get_player(member.id, var[ctx.guild.id]["playerdict"]).dead == True):
                    embed = discord.Embed(title="**Sorry, you can't vote someone dead.**", colour=discord.Colour(0xcce0ff), description="**Please choose a valid player that is alive in the game.**")

                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896419059988578344/downvote.png")
                    embed.set_footer(text="Type `/vote` to vote.", icon_url=ctx.author.avatar_url)
                    await ctx.create_response(embed=embed, ephemeral=True)
                    return
                mm = Player.get_player(ctx.author.id, var[ctx.guild.id]["playerdict"])

                if (mm.dead == True):
                    embed = discord.Embed(title="**Sorry, you can't vote being dead.**", colour=discord.Colour(0xcce0ff), description="**Please be alive then vote.**")

                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896419059988578344/downvote.png")
                    embed.set_footer(text="Type `/vote` to vote.", icon_url=ctx.author.avatar_url)
                    await ctx.create_response(embed=embed, ephemeral=True)
                    return
                if (mm.id in var[ctx.guild.id]["guiltyers"] == True):
                    await ctx.reply("You're too guilty to vote.", ephemeral=True)
                    return

                aliveplayers = 0
                for i in var[ctx.guild.id]["playerdict"].values():
                    if (i.dead == False and i.id != 0):
                        aliveplayers += 1

                if (mm.voted == True):
                    if (mm.isrevealed == True and Player.get_player(ctx.author.id, var[ctx.guild.id]["playerdict"]).role.lower() == "mayor"):
                        if (int(mm.votedforwho) in var[ctx.guild.id]["voted"]):
                            var[ctx.guild.id]["voted"][mm.votedforwho] -= 3
                        else:
                            var[ctx.guild.id]["voted"][mm.votedforwho] = 0
                    else:
                        if (int(mm.votedforwho) in var[ctx.guild.id]["voted"]):
                            var[ctx.guild.id]["voted"][mm.votedforwho] -= 1
                        else:
                            var[ctx.guild.id]["voted"][mm.votedforwho] = 0

                mm.voted = True
                mm.votedforwho = int(member.id)
                if (int(member.id) in var[ctx.guild.id]["voted"]):
                    if (mm.isrevealed == True and Player.get_player(ctx.author.id, var[ctx.guild.id]["playerdict"]).role.lower() == "mayor"):
                        var[ctx.guild.id]["voted"][int(member.id)] += 3
                    else:
                        var[ctx.guild.id]["voted"][int(member.id)] += 1
                else:
                    if (mm.isrevealed == True and Player.get_player(ctx.author.id, var[ctx.guild.id]["playerdict"]).role.lower() == "mayor"):
                        var[ctx.guild.id]["voted"][int(member.id)] = 3
                    else:
                        var[ctx.guild.id]["voted"][int(member.id)] = 1

                q = var[ctx.guild.id]["voted"]
                embed = discord.Embed(title=f"**{ctx.author.name} has voted against {member.name}**", colour=discord.Colour(0xcce0ff), description=f"**{member.name} now has {str(q[int(member.id)])} vote(s) on them.**")

                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896418860427771975/upvote.png")
                embed.set_footer(text=f"{str(int(aliveplayers / 2) + 1)} votes are needed to send someone to trial.", icon_url=ctx.author.avatar_url)
                await ctx.create_response(embed=embed)
            else:
                embed = discord.Embed(title="**Sorry, you can't vote right now.**", colour=discord.Colour(0xcce0ff), description="**Please vote someone during the allocated time period.**")

                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896419059988578344/downvote.png")
                embed.set_footer(text="Type /vote to vote.", icon_url=ctx.author.avatar_url)
                await ctx.create_response(embed=embed, ephemeral=True)
                return

            if (var[ctx.guild.id]["voted"][int(member.id)] >= int(aliveplayers / 2 + 1)):
                var[ctx.guild.id]["novotes"] = True
                embed = discord.Embed(title=f"{member.name} has been put on trial.", colour=discord.Colour(0xfd9f03), description="**You have 20 seconds to defend yourself.**")

                embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/878813918284361768/unknown.png")
                embed.set_thumbnail(url=member.avatar_url)
                
                await ctx.channel.send(embed=embed)
                await asyncio.sleep(20)

                var[ctx.guild.id]["trialuser"] = member.id
                var[ctx.guild.id]["guiltyinno"] = True
                var[ctx.guild.id]["guyontrial"] = member.id
                
                embed = discord.Embed(title=f"**It is time to decide on the fate of {member.name}.**", colour=discord.Colour(0xffdea4), description="Use `/guilty` and `/inno` to mark the player.")

                embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/879072513643151375/unknown.png")
                embed.set_thumbnail(url=member.avatar_url)
                await ctx.channel.send(embed=embed)
                
                for i in var[ctx.guild.id]["players"]:
                    var[ctx.guild.id]["abstainers"].append(i)   

                trialtimer = 10.00
                while (trialtimer >= 0.0):
                    await asyncio.sleep(0.1)
                    trialtimer -= 0.1

                y = len(var[ctx.guild.id]["guiltyers"])
                x = len(var[ctx.guild.id]["innoers"])

                # print(y)
                # print(x)

                if (y > x):
                    embed = discord.Embed()
                    if (Player.get_player(member.id, var[ctx.guild.id]["playerdict"]).role == "Jester"):
                        embed = discord.Embed(title=f"**{member.name}#{member.discriminator} has been lynched**", description="Their role was, **Jester** <:jesticon2:889968373612560394>.", colour=discord.Colour(0x90ecff))
                        
                        Player.get_player(member.id, var[ctx.guild.id]["playerdict"]).death = DeathReason.Hanged
                        
                        if (getWill(Player.get_player(member.id, var[ctx.guild.id]["playerdict"]).will) != ""):
                            embed.add_field(name="We found a will next to their body :scroll:.", value=getWill(Player.get_player(member.id, var[ctx.guild.id]["playerdict"]).will), inline=False)

                        message = ""
                        for i in copy.copy(var[ctx.guild.id]["innoers"]):

                            if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).id in var[ctx.guild.id]["guiltyers"] == True):
                                continue
                            if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).dead == True):
                                continue
                            if (i == var[ctx.guild.id]["mayor"]):
                                message += f"{bot.get_user(i).mention} - **Mayor** <:mayoricon2:897570023143518288>\n"
                            else:
                                message += f"{bot.get_user(i).mention}\n"

                        if (message == ""):
                            message = ":x: None"
                            

                        embed.add_field(name="Guilty ✅", value=message)

                        message = ""
                        mchmmm = copy.copy(var[ctx.guild.id]["innoers"])
                        for i in mchmmm:
                            if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).dead == True):
                                continue
                            if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).id in var[ctx.guild.id]["guiltyers"] == True):
                                continue

                            if (i == var[ctx.guild.id]["mayor"]):
                                message += f"{bot.get_user(i).mention} - **Mayor** <:mayoricon2:897570023143518288>\n"
                            else:
                                message += f"{bot.get_user(i).mention}\n"


                        if (message == ""):
                            message = ":x: None"

                        embed.add_field(name="Innocent ❌", value=message)

                        message = ""
                        for i in var[ctx.guild.id]["players"]:
                            if (bot.get_user(i) in var[ctx.guild.id]["abstainers"]):
                                if (i == member.id):
                                    continue
                                if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).dead == True):
                                    continue
                                if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).id in var[ctx.guild.id]["guiltyers"] == True):
                                    continue

                                if (bot.get_user(i) == var[ctx.guild.id]["mayor"]):
                                    message += f"{bot.get_user(i).mention} - **Mayor** <:mayoricon2:897570023143518288>\n"
                                else:
                                    message += f"{bot.get_user(i).mention}\n"

                        if (message == ""):
                            message = ":x: None"

                        embed.add_field(name="Abstained ❓", value=message)

                        embed.set_image(url="https://images-ext-2.discordapp.net/external/LlOBlIZEHHfRmfQn8_dhpUD6gN0CUWMecRcDZjd9CTs/%3Fwidth%3D890%26height%3D701/https/media.discordapp.net/attachments/765738640554065962/877706810763657246/unknown.png")
                        embed.set_thumbnail(url=member.avatar_url)

                        for i in var[ctx.guild.id]["players"]:
                            play = await ctx.guild.fetch_member(i)
                            if (play.id == member.id):
                                continue

                            if (play in var[ctx.guild.id]["guiltyers"]):
                                var[ctx.guild.id]["guiltyers"].append(play.id) 

                        for i in var[ctx.guild.id]["players"]:
                            play = await ctx.guild.fetch_member(i)

                            if (play.id == member.id):
                                continue

                            if (play not in var[ctx.guild.id]["guiltyers"] and play not in var[ctx.guild.id]["innoers"]):
                                var[ctx.guild.id]["guiltyers"].append(play.id) 


                    else:

                        for i in var[ctx.guild.id]["playerdict"].values():
                            if (i.role.lower() == "headhunter"):
                                if (i.hhtarget == member.id):
                                    embed = discord.Embed(title="**You have successfully gotten your target lynched!**", colour=discord.Colour(0x39556b))

                                    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/873940243219361792.png?v=1")
                                    embed.set_footer(text="Your win condition has now been fulfilled.", icon_url=bot.get_user(i.id).avatar_url)
                                    await bot.get_user(i.id).send(embed=embed)
                                    i.wins = True

                        ijf = var[ctx.guild.id]["playerdict"]
                        a = var[ctx.guild.id]["emoji"][Player.get_player(member.id, ijf).role.lower()]
                        
                        embed = discord.Embed(title=f"**{member.name}#{member.discriminator} has been lynched**", description = f"Their role was, **{Player.get_player(member.id, ijf).role.capitalize()} {a}**.", colour=discord.Colour(0x90ecff))
                        Player.get_player(member.id, var[ctx.guild.id]["playerdict"]).death = DeathReason.Hanged

                        for i in var[ctx.guild.id]["playerdict"].values():
                            i.jesterwin = False

                        if (getWill(Player.get_player(member.id, ijf).will) != ""):
                            embed.add_field(name="We found a will next to their body :scroll:.", value=getWill(Player.get_player(member.id, ijf).will), inline=False)

                        message = ""
                        for i in var[ctx.guild.id]["guiltyers"]:
                            if (i == member.id):
                                continue
                            if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).dead == True):
                                continue
                            if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).id in var[ctx.guild.id]["guiltyers"] == True):
                                continue

                            if (i == var[ctx.guild.id]["mayor"]):
                                message += f"{bot.get_user(i).mention} - **Mayor** <:mayoricon2:897570023143518288>\n"
                            else:
                                message += f"{bot.get_user(i).mention}\n"

                        if (message == ""):
                            message = ":x: None"

                        embed.add_field(name="Guilty ✅", value=message)

                        message = ""
                        for i in var[ctx.guild.id]["innoers"]:
                            if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).dead == True):
                                continue
                            if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).id in var[ctx.guild.id]["guiltyers"] == True):
                                continue

                            if (i == var[ctx.guild.id]["mayor"]):
                                message += f"{bot.get_user(i).mention} - **Mayor** <:mayoricon2:897570023143518288>\n"
                            else:
                                message += f"{bot.get_user(i).mention}\n"

                        if (message == ""):
                            message = ":x: None"

                        embed.add_field(name="Innocent ❌", value=message)

                        message = ""
                        for i in var[ctx.guild.id]["players"]:
                            if (bot.get_user(i) in var[ctx.guild.id]["abstainers"]):
                                if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).dead == True):
                                    continue
                                if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).id in var[ctx.guild.id]["guiltyers"] == True):
                                    continue

                                if (bot.get_user(i) == var[ctx.guild.id]["mayor"]):
                                    message += f"{bot.get_user(i).mention} - **Mayor** <:mayoricon2:897570023143518288>\n"
                                else:
                                    message += f"{bot.get_user(i).mention}\n"

                        if (message == ""):
                            message = ":x: None"

                        embed.add_field(name="Abstained ❓", value=message)

                        embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/877706810763657246/unknown.png?width=890&height=701")
                        embed.set_thumbnail(url=member.avatar_url)


                    await ctx.channel.send(embed=embed)
                    
                    embed = discord.Embed(title="**You were lynched by the Town :knot:.**", colour=discord.Colour(0x207aac), description="**You have died <:rip:878415658885480468>**.")

                    embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/LlOBlIZEHHfRmfQn8_dhpUD6gN0CUWMecRcDZjd9CTs/%3Fwidth%3D890%26height%3D701/https/media.discordapp.net/attachments/765738640554065962/877706810763657246/unknown.png?width=805&height=634")
                    embed.set_footer(text="Rest in peace.", icon_url=member.avatar_url)
                    await member.send(embed=embed)
                    var[ctx.guild.id]["daysnokill"] = 0
                    if (Player.get_player(member.id, var[ctx.guild.id]["playerdict"]).role == "Jester"):
                        await asyncio.sleep(2)
                        embed = discord.Embed(title="**The Jester will get their revenge!!!**", colour=discord.Colour(0xffc3e7), description="**All guilties and abstainers will be distracted the following night and will be unable to vote tomorrow.**")

                        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/872187561597075476.png?v=1")
                        embed.set_footer(text="Don't lynch the Jester.")
                        Player.get_player(member.id, var[ctx.guild.id]["playerdict"]).wins = True
                        Player.get_player(member.id, var[ctx.guild.id]["playerdict"]).jesterwin = True
                        await ctx.channel.send(embed=embed)

                    Player.get_player(member.id, var[ctx.guild.id]["playerdict"]).dead = True
                    await member.add_roles(discord.utils.get(var[ctx.guild.id]["guildg"].roles, name="[Anarchic] Dead"))
                    await member.remove_roles(discord.utils.get(var[ctx.guild.id]["guildg"].roles, name="[Anarchic] Player"))

                elif (y < x):
                    embed = discord.Embed(title=f"**{member.name}** has been pardoned.", colour=discord.Colour(0x79021), description="**Hopefully the town doesnt regret this decision later...**")
                    
                    for i in var[ctx.guild.id]["playerdict"].values():
                        i.jesterwin = False

                    message = ""
                    for i in var[ctx.guild.id]["guiltyers"]:
                        if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).dead == True):
                            continue
                        if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).id in var[ctx.guild.id]["guiltyers"] == True):
                                continue

                        if (i == var[ctx.guild.id]["mayor"]):
                            message += f"{bot.get_user(i).mention} - **Mayor** <:mayoricon2:897570023143518288>\n"
                        else:
                            message += f"{bot.get_user(i).mention}\n"

                    if (message == ""):
                        message = ":x: None"

                    embed.add_field(name="Guilty ✅", value=message)

                    message = ""
                    for i in var[ctx.guild.id]["innoers"]:
                        if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).id in var[ctx.guild.id]["guiltyers"] == True):
                            continue

                        if (i.id == var[ctx.guild.id]["mayor"]):
                            message += f"{bot.get_user(i).mention} - **Mayor** <:mayoricon2:897570023143518288>\n"
                        else:
                            message += f"{bot.get_user(i).mention}\n"

                    if (message == ""):
                        message = ":x: None"

                    embed.add_field(name="Innocent ❌", value=message)

                    message = ""
                    for i in var[ctx.guild.id]["players"]:
                        if (bot.get_user(i) in var[ctx.guild.id]["abstainers"]):
                            if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).dead == True):
                                continue
                            if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).id in var[ctx.guild.id]["guiltyers"] == True):
                                continue

                            if (i == var[ctx.guild.id]["mayor"]):
                                message += f"{bot.get_user(i).mention} - **Mayor** <:mayoricon2:897570023143518288>\n"
                            else:
                                message += f"{bot.get_user(i).mention}\n"

                    if (message == ""):
                        message = ":x: None"

                    embed.add_field(name="Abstained ❓", value=message)

                    embed.set_thumbnail(url=member.avatar_url)
                    await ctx.channel.send(embed=embed)
                elif (y == x):
                    embed = discord.Embed(title=f"**{member.name}** has been pardoned by a tie.", colour=discord.Colour(0x79021), description="**Hopefully the town doesnt regret this decision later...**")
                        
                    for i in var[ctx.guild.id]["playerdict"].values():
                        i.jesterwin = False

                    message = ""
                    for i in var[ctx.guild.id]["guiltyers"]:
                        if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).dead == True):
                            continue
                        if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).id in var[ctx.guild.id]["guiltyers"] == True):
                            continue
                        if (i == var[ctx.guild.id]["mayor"]):
                            message += f"{bot.get_user(i).mention} - **Mayor** <:mayoricon2:897570023143518288>\n"
                        else:
                            message += f"{bot.get_user(i).mention}\n"

                    if (message == ""):
                        message = ":x: None"

                    embed.add_field(name="Guilty ✅", value=message)

                    message = ""
                    for i in var[ctx.guild.id]["innoers"]:
                        if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).dead == True):
                            continue
                        if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).id in var[ctx.guild.id]["guiltyers"] == True):
                            continue
                        if (i == var[ctx.guild.id]["mayor"]):
                            message += f"{bot.get_user(i).mention} - **Mayor** <:mayoricon2:897570023143518288>\n"
                        else:
                            message += f"{bot.get_user(i).mention}\n"

                    if (message == ""):
                        message = ":x: None"

                    embed.add_field(name="Innocent ❌", value=message)

                    message = ""
                    for i in var[ctx.guild.id]["players"]:
                        if (bot.get_user(i) in var[ctx.guild.id]["abstainers"]):
                            if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).dead == True):
                                continue
                            if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).id in var[ctx.guild.id]["guiltyers"] == True):
                                continue
                            if (i == var[ctx.guild.id]["mayor"]):
                                message += f"{bot.get_user(i).mention} - **Mayor** <:mayoricon2:897570023143518288>\n"
                            else:
                                message += f"{bot.get_user(i).mention}\n"

                    if (message == ""):
                        message = ":x: None"

                    embed.add_field(name="Abstained ❓", value=message)
                    
                    embed.set_thumbnail(url=member.avatar_url)
                    await ctx.channel.send(embed=embed)

                await asyncio.sleep(2)
                if (len(getTownies(ctx.guild)) == 0 and len(getMaf(ctx.guild)) == 0):
                    b = await EndGame(EndReason.Draw, ctx.guild)
                    await var[ctx.guild.id]["startchannel"].send(embed=b)
                    await var[ctx.guild.id]["channel"].send(embed=b)
                    perm = discord.PermissionOverwrite()
                    perm.read_messages = True
                    perm.send_messages = True

                    role = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
                    roled = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

                    await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
                    await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
                    perm.send_messages = False
                    await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
                    await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

                    var[ctx.guild.id]["result"] = True
                    return
                if (len(getTownies(ctx.guild)) == 0):
                    b = await EndGame(EndReason.MafiaWins, ctx.guild)
                    await var[ctx.guild.id]["channel"].send(embed=b)
                    await var[ctx.guild.id]["startchannel"].send(embed=b)
                    perm = discord.PermissionOverwrite()
                    perm.read_messages = True
                    perm.send_messages = True

                    role = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
                    roled = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

                    await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
                    await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
                    perm.send_messages = False
                    await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
                    await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

                    var[ctx.guild.id]["result"] = True
                    return
                elif (len(getMaf(ctx.guild)) == 0):
                    b = await EndGame(EndReason.TownWins, ctx.guild)
                    await var[ctx.guild.id]["channel"].send(embed=b)
                    await var[ctx.guild.id]["startchannel"].send(embed=b)
                    perm = discord.PermissionOverwrite()
                    perm.read_messages = True
                    perm.send_messages = True

                    role = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
                    roled = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

                    await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
                    await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
                    perm.send_messages = False
                    await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
                    await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

                    var[ctx.guild.id]["result"] = True
                    return

                dad = var[ctx.guild.id]["gday"]
                embed = discord.Embed(title=f"**It is Night {dad} :crescent_moon:.**", colour=discord.Colour(0x1f0050))

                embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/878070289194426399/unknown.png?width=925&height=701")
                message = ""
                for i in var[ctx.guild.id]["playerdict"].values():
                    if (i.dead==False and i.id != 0):
                        message += f"{bot.get_user(i.id).mention}\n" 
                if (message == ""):
                    message = "** **"

                embed.add_field(name="**Alive Townies <:townicon2:896431548717473812>:**", value=message, inline=True)
                message = ""
                for i in var[ctx.guild.id]["playerdict"].values():
                    if (i.dead==True and i.id != 0):
                        em = var[ctx.guild.id]["emoji"]
                        d = var[ctx.guild.id]["playerdict"]
                        if (i.diedln == True):
                            message += f"{bot.get_user(i.id).mention} -  **?**\n" 
                        else:
                            message += f"{bot.get_user(i.id).mention} -  **{Player.get_player(i.id, d).role.capitalize()}** {em[Player.get_player(i.id, d).role.lower()]}\n" 
                if (message == ""):
                    message = "** **"
                embed.add_field(name="**Graveyard <:rip:872284978354978867>:**", value=message, inline=True)
                
                await ctx.channel.send(embed=embed)
                await lock(ctx.channel)
                for value in var[ctx.guild.id]["playerdict"].values():
                    value.voted = False
                
                var[ctx.guild.id]["voting"] = False
                var[ctx.guild.id]["ind"] -= 1
                await night(ctx)
        else:
            return
    else:
        embed = discord.Embed(title="**Sorry, that player isn't in the game.**", colour=discord.Colour(0xcce0ff), description="**Please choose a valid player that is alive in the game.**")

        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896419059988578344/downvote.png")
        embed.set_footer(text="Type `/vote` to vote.", icon_url=ctx.author.avatar_url)
        await ctx.create_response(embed=embed, ephemeral=True)
        return

# @vote.sub_command(
#     name="letter",
#     description="Vote a player's letter to lynch them",
#     options=[
#         Option('letter', 'The player\'s letter', OptionType.STRING, True)
#         ]
# )
# async def voteLetter(ctx, letter=None):
#     try:
#         var[ctx.guild.id]["test"]
#     except:
#         var[ctx.guild.id] = copy.deepcopy(temp)


#     if (letter is None or letter not in var[ctx.guild.id]["votingemoji"]):
#         embed = discord.Embed(title="**Sorry, that isn't a valid letter.**", colour=discord.Colour(0xcce0ff), description="**Please choose a valid player that is alive in the game.**")

#         embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896419059988578344/downvote.png")
#         embed.set_footer(text="Type `/vote` to vote.", icon_url=ctx.author.avatar_url)
#         await ctx.create_response(embed=embed, ephemeral=True)
#         return

#     realletter = var[ctx.guild.id]["votingemoji"][letter]

#     if (realletter in var[ctx.guild.id]["players"]):
#         if (ctx.channel.name == "town-square"):
#             e = random.uniform(0.2, 0.8)
#             await asyncio.sleep(e)
#             if (var[ctx.guild.id]["voting"] == True and var[ctx.guild.id]["gday"] != 1 and var[ctx.guild.id]["started"] == True and var[ctx.guild.id]["novotes"] == False):
#                 if (Player.get_player(realletter.id, var[ctx.guild.id]["playerdict"]).dead == True):
#                     embed = discord.Embed(title="**Sorry, you can't vote someone dead.**", colour=discord.Colour(0xcce0ff), description="**Please choose a valid player that is alive in the game.**")

#                     embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896419059988578344/downvote.png")
#                     embed.set_footer(text="Type `/vote` to vote.", icon_url=ctx.author.avatar_url)
#                     await ctx.create_response(embed=embed, ephemeral=True)
#                     return
#                 mm = Player.get_player(ctx.author.id, var[ctx.guild.id]["playerdict"])

#                 if (mm.dead == True):
#                     embed = discord.Embed(title="**Sorry, you can't vote being dead.**", colour=discord.Colour(0xcce0ff), description="**Please choose a valid player that is alive in the game.**")

#                     embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896419059988578344/downvote.png")
#                     embed.set_footer(text="Type `/vote` to vote.", icon_url=ctx.author.avatar_url)
#                     await ctx.create_response(embed=embed, ephemeral=True)
#                     return

#                 aliveplayers = 0
#                 for i in var[ctx.guild.id]["playerdict"].values():
#                     if (i.dead == False and i.id != 0):
#                         aliveplayers += 1

#                 if (mm.voted == True):
#                     if (mm.isrevealed == True and Player.get_player(ctx.author.id, var[ctx.guild.id]["playerdict"]).role.lower() == "mayor"):
#                         if (int(mm.votedforwho) in var[ctx.guild.id]["voted"]):
#                             var[ctx.guild.id]["voted"][mm.votedforwho] -= 3
#                         else:
#                             var[ctx.guild.id]["voted"][mm.votedforwho] = 0
#                     else:
#                         if (int(mm.votedforwho) in var[ctx.guild.id]["voted"]):
#                             var[ctx.guild.id]["voted"][mm.votedforwho] -= 1
#                         else:
#                             var[ctx.guild.id]["voted"][mm.votedforwho] = 0

#                 mm.voted = True
#                 mm.votedforwho = int(realletter)
#                 if (int(realletter) in var[ctx.guild.id]["voted"]):
#                     if (mm.isrevealed == True and Player.get_player(ctx.author.id, var[ctx.guild.id]["playerdict"]).role.lower() == "mayor"):
#                         var[ctx.guild.id]["voted"][int(realletter)] += 3
#                     else:
#                         var[ctx.guild.id]["voted"][int(realletter)] += 1
#                 else:
#                     if (mm.isrevealed == True and Player.get_player(ctx.author.id, var[ctx.guild.id]["playerdict"]).role.lower() == "mayor"):
#                         var[ctx.guild.id]["voted"][int(realletter)] = 3
#                     else:
#                         var[ctx.guild.id]["voted"][int(realletter)] = 1

#                 q = var[ctx.guild.id]["voted"]
#                 us = bot.get_user(realletter)

#                 embed = discord.Embed(title=f"**{ctx.author.name} has voted against {us.name}**", colour=discord.Colour(0xcce0ff), description=f"**{us.name} now has {str(q[int(us.id)])} vote(s) on them.**")

#                 embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896418860427771975/upvote.png")
#                 embed.set_footer(text=f"{str(int(aliveplayers / 2) + 1)} votes are needed to send someone to trial.", icon_url=ctx.author.avatar_url)
#                 await ctx.create_response(embed=embed)
#             else:
#                 embed = discord.Embed(title="**Sorry, you can't vote right now.**", colour=discord.Colour(0xcce0ff), description="**Please choose a valid player that is alive in the game.**")

#                 embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896419059988578344/downvote.png")
#                 embed.set_footer(text="Type `/vote` to vote.", icon_url=ctx.author.avatar_url)
#                 await ctx.create_response(embed=embed, ephemeral=True)
#                 return

#             if (var[ctx.guild.id]["voted"][int(us.id)] >= int(aliveplayers / 2 + 1)):
#                 us = bot.get_user(realletter)
#                 var[ctx.guild.id]["novotes"] = True
#                 embed = discord.Embed(title=f"{us.name}has been put on trial.", colour=discord.Colour(0xfd9f03), description="**You have 20 seconds to defend yourself.**")

#                 embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/878813918284361768/unknown.png")
#                 embed.set_thumbnail(url=us.avatar_url)
                
#                 await ctx.channel.send(embed=embed)
#                 trialtimer = 20.0
#                 while (trialtimer >= 0.0):
#                     await asyncio.sleep(0.1)
#                     trialtimer = trialtimer - 0.1
                    
#                 embed = discord.Embed(title=f"**It is time to decide on the fate of {us.name}.**", colour=discord.Colour(0xffdea4), description=":white_check_mark: **- Guilty**\n:x: **- Innocent**")

#                 embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/879072513643151375/unknown.png")
#                 embed.set_thumbnail(url=us.avatar_url)
#                 msg = await ctx.channel.send(embed=embed)
#                 await msg.add_reaction("✅")
#                 await msg.add_reaction("❌")
#                 trialtimer = 20.00
#                 while (trialtimer >= 0.0):
#                     await asyncio.sleep(0.1)
#                     trialtimer -= 0.1

#                 msgg = await ctx.channel.fetch_message(msg.id)
#                 reaction:discord.Reaction = get(msgg.reactions, emoji="✅")
#                 y = reaction.count - 1

#                 if (var[ctx.guild.id]["mayor"] in await reaction.users().flatten()):
#                     y += 2

#                 if (bot.get_user(us.id) in await reaction.users().flatten()):
#                     y -= 1



#                 no = get(msgg.reactions, emoji="❌")
#                 x = no.count - 1

#                 if (bot.get_user(us.id) in await no.users().flatten()):
#                     x -= 1
#                 if (var[ctx.guild.id]["mayor"] in await reaction.users().flatten()):
#                     x += 2
                
#                 for i in var[ctx.guild.id]["players"]:
#                     play = bot.get_user(i)
#                     if (play not in await no.users().flatten() and play not in await reaction.users().flatten()):
#                         var[ctx.guild.id]["abstainers"].append(play.id) 


#                 if (y > x):
#                     embed = discord.Embed()
#                     if (Player.get_player(us.id, var[ctx.guild.id]["playerdict"]).role == "Jester"):
#                         embed = discord.Embed(title=f"**{us.name}#{us.discriminator} has been lynched**", description="Their role was, **Jester**.", colour=discord.Colour(0x90ecff))

#                         embed.set_image(url="https://images-ext-2.discordapp.net/external/LlOBlIZEHHfRmfQn8_dhpUD6gN0CUWMecRcDZjd9CTs/%3Fwidth%3D890%26height%3D701/https/media.discordapp.net/attachments/765738640554065962/877706810763657246/unknown.png")
#                         embed.set_thumbnail(url=us.avatar_url)
#                         for i in var[ctx.guild.id]["players"]:
#                             reaction:discord.Reaction = get(msgg.reactions, emoji="✅")
#                             if (bot.get_user(i) in await reaction.users().flatten()):
#                                 Player.get_player(i, var[ctx.guild.id]["playerdict"]).guiltyvoter = True           
#                                 print(Player.get_player(i, var[ctx.guild.id]["playerdict"]).guiltyvoter)      
                    
#                     else:

#                         for i in var[ctx.guild.id]["playerdict"].values():
#                             if (i.role.lower() == "headhunter"):
#                                 if (i.hhtarget == Player.get_player(us.id, var[ctx.guild.id]["playerdict"])):
#                                     embed = discord.Embed(title="**You have successfully gotten your target lynched!**", colour=discord.Colour(0x39556b))

#                                     embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/873940243219361792.png?v=1")
#                                     embed.set_footer(text="Your win condition has now been fulfilled.", icon_url=bot.get_user(i.id).avatar_url)
#                                     await bot.get_user(i.id).send(embed=embed)
#                                     i.wins = True

#                         ijf = var[ctx.guild.id]["playerdict"]
#                         em = var[ctx.guild.id]["emoji"]
#                         embed = discord.Embed(title=f"**{us.name}#{us.discriminator} has been lynched**", description = f"Their role was, **{Player.get_player(us.id, ijf).role.capitalize()} {em[Player.get_player(us.id, ijf).role.lower()]}**.", colour=discord.Colour(0x90ecff))

#                         embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/877706810763657246/unknown.png?width=890&height=701")
#                         embed.set_thumbnail(url=us.avatar_url)


#                     await ctx.channel.send(embed=embed)
                    
#                     embed = discord.Embed(title="**You were lynched by the Town :knot:.**", colour=discord.Colour(0x207aac), description="**You have died <:rip:878415658885480468>**.")

#                     embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/LlOBlIZEHHfRmfQn8_dhpUD6gN0CUWMecRcDZjd9CTs/%3Fwidth%3D890%26height%3D701/https/media.discordapp.net/attachments/765738640554065962/877706810763657246/unknown.png?width=805&height=634")
#                     embed.set_footer(text="Rest in peace.", icon_url=us.avatar_url)
#                     await us.send(embed=embed)
#                     if (Player.get_player(us.id, var[ctx.guild.id]["playerdict"]).role == "Jester"):
#                         await asyncio.sleep(2)
#                         embed = discord.Embed(title="**The Jester will get their revenge!!!**", colour=discord.Colour(0xffc3e7), description="**All guilties and abstainers will be distracted the following night and will be unable to vote tomorrow.**")

#                         embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/872187561597075476.png?v=1")
#                         embed.set_footer(text="Don't lynch the Jester.")
#                         Player.get_player(us.id, var[ctx.guild.id]["playerdict"]).wins = True
#                         Player.get_player(us.id, var[ctx.guild.id]["playerdict"]).jesterwin = True
#                         await ctx.channel.send(embed=embed)

#                     Player.get_player(us.id, var[ctx.guild.id]["playerdict"]).dead = True
#                     await us.add_roles(discord.utils.get(var[ctx.guild.id]["guildg"].roles, name="[Anarchic] Dead"))
#                     await us.remove_roles(discord.utils.get(var[ctx.guild.id]["guildg"].roles, name="[Anarchic] Player"))

#                 elif (y < x):
#                     embed = discord.Embed(title=f"**{us.name}** has been pardoned.", colour=discord.Colour(0x79021), description="**Hopefully the town doesnt regret this decision later...**")
#                     embed.set_thumbnail(url=us.avatar_url)
#                     await ctx.channel.send(embed=embed)
#                 elif (y == x):
#                     embed = discord.Embed(title=f"**{us.name}** has been pardoned by a tie.", colour=discord.Colour(0x79021), description="**Hopefully the town doesnt regret this decision later...**")
#                     embed.set_thumbnail(url=us.avatar_url)
#                     await ctx.channel.send(embed=embed)

#                 await asyncio.sleep(2)
#                 if (len(getTownies(ctx.guild)) == 0 and len(getMaf(ctx.guild)) == 0):
#                     b = await EndGame(EndReason.Draw, ctx.guild)
#                     await var[ctx.guild.id]["channel"].send(embed=b)
#                     perm = discord.PermissionOverwrite()
#                     perm.read_messages = True
#                     perm.send_messages = True

#                     role = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
#                     roled = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

#                     await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
#                     await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
#                     perm.send_messages = False
#                     await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
#                     await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

#                     var[ctx.guild.id]["result"] = True
#                     return
#                 if (len(getTownies(ctx.guild)) == 0):
#                     b = await EndGame(EndReason.MafiaWins, ctx.guild)
#                     await var[ctx.guild.id]["channel"].send(embed=b)
#                     perm = discord.PermissionOverwrite()
#                     perm.read_messages = True
#                     perm.send_messages = True

#                     role = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
#                     roled = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

#                     await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
#                     await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
#                     perm.send_messages = False
#                     await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
#                     await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

#                     var[ctx.guild.id]["result"] = True
#                     return
#                 elif (len(getMaf(ctx.guild)) == 0):
#                     b = await EndGame(EndReason.TownWins, ctx.guild)
#                     await var[ctx.guild.id]["channel"].send(embed=b)
#                     perm = discord.PermissionOverwrite()
#                     perm.read_messages = True
#                     perm.send_messages = True

#                     role = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
#                     roled = discord.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

#                     await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
#                     await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
#                     perm.send_messages = False
#                     await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
#                     await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

#                     var[ctx.guild.id]["result"] = True
#                     return
#                 await ctx.channel.send("It's too late to continue voting.")
#                 for value in var[ctx.guild.id]["playerdict"].values():
#                     value.voted = False
                
#                 var[ctx.guild.id]["voting"] = False
#                 var[ctx.guild.id]["ind"] -= 1
#                 await night()
#         else:
#             return
#     else:
#         embed = discord.Embed(title="**Sorry, that player isn't in the game.**", colour=discord.Colour(0xcce0ff), description="**Please choose a valid player that is alive in the game.**")

#         embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896419059988578344/downvote.png")
#         embed.set_footer(text="Type `/vote` to vote.", icon_url=ctx.author.avatar_url)
#         await ctx.create_response(embed=embed, ephemeral=True)
#         return

@dislash.guild_only()
@slash.slash_command(
    name="end",
    description="Finalize the game to start a new one"
)
async def endGame(ctx:SlashInteraction):

    try:
        var[ctx.guild.id]["test"]
    except:
        var[ctx.guild.id] = copy.deepcopy(temp)

    if (var[ctx.guild.id]["started"] == True):
        if (var[ctx.guild.id]["result"] == True):
            if (ctx.channel.category.name == "Anarchic"):
                if (ctx.channel.name == "town-square"):
                    if (ctx.channel == var[ctx.guild.id]["channel"]):
                        embed = discord.Embed(title="Thanks for playing **Anarchic**!", colour=discord.Colour(0x166617), description=":clock10: Deleting the channels in 5 seconds")

                        embed.set_footer(text="Use /start to start another game.")

                        if (var[ctx.guild.id]["setupz"].lower() == "custom"):
                            embed.add_field(name=":warning: Warning", value="*You are on a custom setup, you will not get silvers from playing this game*")
                        
                        await ctx.reply(embed=embed)
                        
                        guild:discord.Guild = ctx.guild     

                        #Hand out the silvers
                        if (var[ctx.guild.id]["setupz"].lower() != "custom"):
                            size = PlayerSize(len(var[guild.id]["players"]))
                            reason = var[guild.id]["endreason"]

                            mafaward = 0
                            neutralaward = 0
                            townaward = 0

                            if (reason == EndReason.MafiaWins):
                                if (size == GameSize.Small):
                                    mafaward = 12

                                    for i in var[guild.id]["playerdict"].values():
                                        if (i.death == DeathReason.Hanged and i.faction == Faction.Town):
                                            mafaward += 1
                                        if (i.faction == Faction.Mafia and i.dead == False):
                                            mafaward += 1

                                    townaward = 2
                                    for i in var[guild.id]["playerdict"].values():
                                        if (i.dead == True and i.faction == Faction.Mafia):
                                            townaward += 1
                                        if (i.dead == True and i.role.lower() == "headhunter"):
                                            townaward += 1
                                        if (i.wins == True and i.role.lower() == "jester"):
                                            townaward -= 1
                                        if (i.wins == True and i.role.lower() == "headhunter"):
                                            townaward -= 1
                                if (size == GameSize.Medium):
                                    mafaward = 13

                                    for i in var[guild.id]["playerdict"].values():
                                        if (i.death == DeathReason.Hanged and i.faction == Faction.Town):
                                            mafaward += 1
                                        if (i.faction == Faction.Mafia and i.dead == False):
                                            mafaward += 1

                                    townaward = 3
                                    for i in var[guild.id]["playerdict"].values():
                                        if (i.dead == True and i.faction == Faction.Mafia):
                                            townaward += 1
                                        if (i.dead == True and i.role.lower() == "headhunter"):
                                            townaward += 1
                                        if (i.wins == True and i.role.lower() == "jester"):
                                            townaward -= 1
                                        if (i.wins == True and i.role.lower() == "headhunter"):
                                            townaward -= 1
                                if (size == GameSize.Large):
                                    mafaward = 15

                                    for i in var[guild.id]["playerdict"].values():
                                        if (i.death == DeathReason.Hanged and i.faction == Faction.Town):
                                            mafaward += 1
                                        if (i.faction == Faction.Mafia and i.dead == False):
                                            mafaward += 1

                                    townaward = 4
                                    for i in var[guild.id]["playerdict"].values():
                                        if (i.dead == True and i.faction == Faction.Mafia):
                                            townaward += 1
                                        if (i.dead == True and i.role.lower() == "headhunter"):
                                            townaward += 1
                                        if (i.wins == True and i.role.lower() == "jester"):
                                            townaward -= 2
                                        if (i.wins == True and i.role.lower() == "headhunter"):
                                            townaward -= 2
                            if (reason == EndReason.TownWins):
                                if (size == GameSize.Small):
                                    mafaward = 3

                                    for i in var[guild.id]["playerdict"].values():
                                        if (i.death == DeathReason.Hanged and i.faction == Faction.Town):
                                            mafaward += 1

                                    townaward = 9
                                    for i in var[guild.id]["playerdict"].values():
                                        if (i.dead == True and i.faction == Faction.Mafia):
                                            townaward += 1
                                        if (i.dead == True and i.role.lower() == "headhunter"):
                                            townaward += 1
                                        if (i.wins == True and i.role.lower() == "jester"):
                                            townaward -= 1
                                        if (i.wins == True and i.role.lower() == "headhunter"):
                                            townaward -= 1
                                if (size == GameSize.Medium):
                                    mafaward = 4

                                    for i in var[guild.id]["playerdict"].values():
                                        if (i.death == DeathReason.Hanged and i.faction == Faction.Town):
                                            mafaward += 1

                                    townaward = 12
                                    deadtown = 0
                                    for i in var[guild.id]["playerdict"].values():
                                        if (i.dead == True and i.faction == Faction.Mafia):
                                            townaward += 1
                                        if (i.dead == True and i.role.lower() == "headhunter"):
                                            townaward += 1
                                        if (i.wins == True and i.role.lower() == "jester"):
                                            townaward -= 1
                                        if (i.wins == True and i.role.lower() == "headhunter"):
                                            townaward -= 2
                                        if (i.dead == True and i.faction == Faction.Town):
                                            deadtown += 1

                                    townaward -= deadtown -1
                                if (size == GameSize.Large):
                                    mafaward = 5

                                    for i in var[guild.id]["playerdict"].values():
                                        if (i.death == DeathReason.Hanged and i.faction == Faction.Town):
                                            mafaward += 1

                                    townaward = 14
                                    for i in var[guild.id]["playerdict"].values():
                                        if (i.dead == True and i.faction == Faction.Mafia):
                                            townaward += 1
                                        if (i.dead == True and i.role.lower() == "headhunter"):
                                            townaward += 1
                                        if (i.wins == True and i.role.lower() == "jester"):
                                            townaward -= 2
                                        if (i.wins == True and i.role.lower() == "headhunter"):
                                            townaward -= 2
                            if (reason == EndReason.Draw):
                                if (size == GameSize.Small):
                                    mafaward = 3

                                    for i in var[guild.id]["playerdict"].values():
                                        if (i.death == DeathReason.Hanged and i.faction == Faction.Town):
                                            mafaward += 1

                                    townaward = 2
                                    for i in var[guild.id]["playerdict"].values():
                                        if (i.dead == True and i.faction == Faction.Mafia):
                                            townaward += 1
                                        if (i.dead == True and i.role.lower() == "headhunter"):
                                            townaward += 1
                                        if (i.wins == True and i.role.lower() == "jester"):
                                            townaward -= 1
                                        if (i.wins == True and i.role.lower() == "headhunter"):
                                            townaward -= 1
                                if (size == GameSize.Medium):
                                    mafaward = 4

                                    for i in var[guild.id]["playerdict"].values():
                                        if (i.death == DeathReason.Hanged and i.faction == Faction.Town):
                                            mafaward += 1

                                    townaward = 3
                                    deadtown = 0
                                    for i in var[guild.id]["playerdict"].values():
                                        if (i.dead == True and i.faction == Faction.Mafia):
                                            townaward += 1
                                        if (i.dead == True and i.role.lower() == "headhunter"):
                                            townaward += 1
                                        if (i.wins == True and i.role.lower() == "jester"):
                                            townaward -= 1
                                        if (i.wins == True and i.role.lower() == "headhunter"):
                                            townaward -= 2
                                        if (i.dead == True and i.faction == Faction.Town):
                                            deadtown += 1

                                    townaward -= deadtown -1
                                if (size == GameSize.Large):
                                    mafaward = 5

                                    for i in var[guild.id]["playerdict"].values():
                                        if (i.death == DeathReason.Hanged and i.faction == Faction.Town):
                                            mafaward += 1
                                        if (i.faction == Faction.Mafia and i.dead == False):
                                            mafaward += 1

                                    townaward = 4
                                    for i in var[guild.id]["playerdict"].values():
                                        if (i.dead == True and i.faction == Faction.Mafia):
                                            townaward += 1
                                        if (i.dead == True and i.role.lower() == "headhunter"):
                                            townaward += 1
                                        if (i.wins == True and i.role.lower() == "jester"):
                                            townaward -= 2
                                        if (i.wins == True and i.role.lower() == "headhunter"):
                                            townaward -= 2
                        
                            for i in var[guild.id]["players"]:
                                if (str(i) not in cur):
                                    cur[str(i)] = 0

                            for i in var[guild.id]["playerdict"].values():
                                if (i.faction == Faction.Neutral):
                                    if (i.wins == True):
                                        if (size == GameSize.Small):
                                            neutaward = 12
                                            neutaward -= var[guild.id]["gday"]
                                            cur[str(i.id)] += neutaward
                                        elif (size == GameSize.Medium):
                                            neutaward = 14
                                            neutaward -= var[guild.id]["gday"]
                                            cur[str(i.id)] += neutaward
                                        elif (size == GameSize.Large):
                                            neutaward = 16
                                            neutaward -= var[guild.id]["gday"]
                                            cur[str(i.id)] += neutaward
                                    else:
                                        if (size == GameSize.Small):
                                            neutaward = 3
                                            cur[str(i.id)] += neutaward
                                        elif (size == GameSize.Medium):
                                            neutaward = 4
                                            cur[str(i.id)] += neutaward
                                        elif (size == GameSize.Large):
                                            neutaward = 5
                                            cur[str(i.id)] += neutaward

                            #Award to each player
                            for i in var[guild.id]["players"]:
                                if (str(i) not in cur):
                                    cur[str(i)] = 0

                                if (Player.get_player(i, var[guild.id]["playerdict"]).faction == Faction.Mafia):
                                    cur[str(i)] += mafaward
                                if (Player.get_player(i, var[guild.id]["playerdict"]).faction == Faction.Town):
                                    cur[str(i)] += townaward


                            with open('data.json', 'w') as jsonf:
                                json.dump(cur, jsonf)

                        var[guild.id]["started"] = None
                        var[guild.id]["voted"] = None
                        var[guild.id]["timer"] = None
                        var[guild.id]["targets"] = None
                        var[guild.id]["gday"] = None
                        var[guild.id]["guiltyers"] = None
                        var[guild.id]["abstainers"] = None

                        var[guild.id]["started"] = False
                        var[guild.id]["result"] = False
                        var[guild.id]["voted"] = {}
                        var[guild.id]["gday"] = 0
                        var[guild.id]["timer"] = 0
                        var[guild.id]["ind"] = 0
                        var[guild.id]["isresults"] = False
                        var[guild.id]["diechannel"] = None
                        var[guild.id]["mafcon"] =None
                        var[guild.id]["chan"] = None
                        var[guild.id]["targets"] = {}
                        var[guild.id]["guiltyers"] = []
                        var[guild.id]["abstainers"] = []


                        await asyncio.sleep(5)

                        for i in ctx.channel.category.channels:
                            await i.delete()

                        await ctx.channel.category.delete()

                        g = discord.utils.get(guild.roles, name="[Anarchic] Player")
                        d = discord.utils.get(guild.roles, name="[Anarchic] Dead")

                        await g.delete()
                        await d.delete()
                    else:
                        await ctx.reply("I--", ephemeral=True)
                else:
                    await ctx.reply("NO.", ephemeral=True)
            else:
                await ctx.reply("There isn't a game in this channel.", ephemeral=True)
        else:
            await ctx.reply("You can't forcibly end a game.", ephemeral=True)
    else:
        if (ctx.author.id == 839842855970275329):
            if (ctx.channel.name == "town-square"):
                row_of_buttons = ActionRow(
                    Button(
                        style=ButtonStyle.red,
                        label="Yes",
                        custom_id="endyesyes"
                    ),
                    Button(
                        style=ButtonStyle.green,
                        label="No",
                        custom_id="endnono"
                    )
                )
                p = await ctx.reply("This category may not be for Anarchic. Are you sure you want to continue?", components=[row_of_buttons])
                inter = p.create_click_listener()

                @inter.matching_id("endyesyes")
                async def endyes(inter):
                    if (inter.clicked_button.label.lower() == "yes"):
                        for i in ctx.channel.category.channels:
                            await i.delete()

                        await ctx.channel.category.delete()
                @inter.matching_id("endnono")
                async def endno(inter):
                    return
        else:
            try:
                await ctx.edit("You can't end a non-existent game.")
            except:
                pass

@dislash.guild_only()
@slash.slash_command(    
    name="setup", # Defaults to function name
    description="Change the setup to have more fun",
    #  registration takes up to 1 hour
    options=[
        Option('setup', 'The setup\'s name', OptionType.STRING, True, choices=[
            OptionChoice("Classic", "classic"),
            OptionChoice("Enforced", "enforced"),
            OptionChoice("Execution", "execution"),
            OptionChoice("Duet", "duet"),
            OptionChoice("Framed", "framed"),
            OptionChoice("Truthed", "truth"),
            OptionChoice("Legacy", "legacy"),
            OptionChoice("Scattered", "scattered"),
            OptionChoice("Anarchy", "anarchy"),
            OptionChoice("Ranked", "ranked"),
            OptionChoice("Custom", "custom")
        ])
        ]
    )
async def ssetup(inter, setup=None):
    try:
        var[inter.guild.id]["test"]
    except:
        var[inter.guild.id] = copy.deepcopy(temp)
    if (setup is None):
        await inter.create_response("That isn't a setup...", ephemeral=True)
        return
    else:
        await _setup(inter, setup, True)

async def _setup(ctx, setup:str, inter=False):


    if (len(var[ctx.guild.id]["players"]) == 0):
        await ctx.send("There's nobody in the game!")

        return
    if (ctx.author.id != var[ctx.guild.id]["players"][0]):
        await ctx.send("Only the host can change the setup!")

        return

    if (setup.lower().replace(" ", "") in var[ctx.guild.id]["comps"]):
        embed = discord.Embed(title="Somethings wrong here...", description="Contact the developer about this bug.")
        if (setup.lower().replace(" ", "") == "enforced"):
            embed = discord.Embed(title="**Gamemode has been set to __Enforced <:enficon2:890339050865696798>__!**", description="", colour=discord.Colour(0xcd95ff))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/O3tABe1id1w0dcI-B8MMo-DgXI9Co9xNaS6QSbjKU2o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/753967387149074543/c908a07ef8d6165ab31770e4b47f38ca.webp")
            embed.set_footer(text="Try /setups for a list of setups.", icon_url=ctx.author.avatar_url)

            embed.add_field(name="__**Enforced <:enficon2:890339050865696798> `(5P)`**__", value="**<:enficon2:890339050865696798> Enforcer**\n**<:docicon2:890333203959787580> Doctor**\n**<:townicon2:896431548717473812> Random Town**\n**:axe: Neutral Evil**\n**<:maficon2:891739940055052328> Mafioso**")
        elif (setup.lower().replace(" ", "") == "classic"):
            embed = discord.Embed(title="**Gamemode has been set to __Classic :triangular_flag_on_post:__!**", colour=discord.Colour(0xcd95ff))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/O3tABe1id1w0dcI-B8MMo-DgXI9Co9xNaS6QSbjKU2o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/753967387149074543/c908a07ef8d6165ab31770e4b47f38ca.webp")
            embed.set_footer(text="Try /setups for a list of setups.", icon_url=ctx.author.avatar_url)

            embed.add_field(name="__**Classic 🚩 `(5P)`**__", value="**<:copicon2:889672912905322516> Cop**\n**<:docicon2:890333203959787580> Doctor**\n**<:mayoricon2:897570023143518288> Mayor**\n**<:jesticon2:889968373612560394> Jester**\n**<:maficon2:891739940055052328> Mafioso**")
        elif (setup.lower().replace(" ", "") == "execution"):
            embed = discord.Embed(title="**Gamemode has been set to __Execution <:hhicon2:891429754643808276>__!**", colour=discord.Colour(0xcd95ff))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/O3tABe1id1w0dcI-B8MMo-DgXI9Co9xNaS6QSbjKU2o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/753967387149074543/c908a07ef8d6165ab31770e4b47f38ca.webp")
            embed.set_footer(text="Try /setups for a list of setups.", icon_url=ctx.author.avatar_url)

            embed.add_field(name="**__Execution <:hhicon2:891429754643808276> `(6P)`__**", value="**<:copicon2:889672912905322516> Cop**\n**<:docicon2:890333203959787580> Doctor**\n**<:townicon2:896431548717473812> Random Town**\n**<:townicon2:896431548717473812> Random Town**\n**<:hhicon2:891429754643808276> Headhunter**\n**<:maficon2:891739940055052328> Mafioso**")
        elif (setup.lower().replace(" ", "") == "duet"):
            embed = discord.Embed(title="**Gamemode has been set to __Duet :musical_note:__!**", colour=discord.Colour(0xcd95ff))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/O3tABe1id1w0dcI-B8MMo-DgXI9Co9xNaS6QSbjKU2o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/753967387149074543/c908a07ef8d6165ab31770e4b47f38ca.webp")
            embed.set_footer(text="Try /setups for a list of setups.", icon_url=ctx.author.avatar_url)

            embed.add_field(name="__**Duet :musical_note: `(7P)`**__", value="**<:enficon2:890339050865696798> Enforcer**\n**<:docicon2:890333203959787580> Doctor**\n**:mag_right: Town Investigative**\n**<:townicon2:896431548717473812> Random Town**\n**<:townicon2:896431548717473812> Random Town**\n**<:maficon2:891739940055052328> Mafioso**\n**<:consicon2:890336628269281350> Consort**")
        elif (setup.lower().replace(" ", "") == "framed"):
            embed = discord.Embed(title="**Gamemode has been set to __Framed <:frameicon2:890365634913902602>__**", colour=discord.Colour(0xcd95ff))

            embed.set_footer(text="Try /setups for a list of setups.", icon_url=ctx.author.avatar_url)

            embed.add_field(name="**__Framed <:frameicon2:890365634913902602> `(7P)`__**", value="**<:loicon2:889673190392078356> Lookout\n<:docicon2:890333203959787580> Doctor\n:mag_right: Town Investigative\n<:townicon2:896431548717473812> Random Town\n<:townicon2:896431548717473812> Random Town\n<:maficon2:891739940055052328> Mafioso\n<:frameicon2:890365634913902602> Framer**", inline=True)
        elif (setup.lower().replace(" ", "") == "legacy"):
            embed = discord.Embed(title="**Gamemode has been set to __Legacy :sparkles:__!**", colour=discord.Colour(0xcd95ff))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/O3tABe1id1w0dcI-B8MMo-DgXI9Co9xNaS6QSbjKU2o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/753967387149074543/c908a07ef8d6165ab31770e4b47f38ca.webp")
            embed.set_footer(text="Try /setups for a list of setups.", icon_url=ctx.author.avatar_url)

            embed.add_field(name="**__Legacy :circus: `(8P)`__**", value="**<:copicon2:889672912905322516> Cop**\n**<:docicon2:890333203959787580> Doctor**\n**<:townicon2:896431548717473812> Random Town**\n**<:townicon2:896431548717473812> Random Town**\n**<:townicon2:896431548717473812> Random Town**\n**:axe: Neutral Evil**\n**<:maficon2:891739940055052328> Mafioso**\n**<:maficon2:890328238029697044> Random Mafia**")
        elif (setup.lower().replace(" ", "") == "scattered"):
            embed = discord.Embed(title="**Gamemode has been set to __Scattered :diamond_shape_with_a_dot_inside:__!**", colour=discord.Colour(0xcd95ff))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/O3tABe1id1w0dcI-B8MMo-DgXI9Co9xNaS6QSbjKU2o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/753967387149074543/c908a07ef8d6165ab31770e4b47f38ca.webp")
            embed.set_footer(text="Try /setups for a list of setups.", icon_url=ctx.author.avatar_url)

            embed.add_field(name="__**Scattered :diamond_shape_with_a_dot_inside: `(9P)`**__", value="**<:enficon2:890339050865696798> Enforcer**\n**<:docicon2:890333203959787580>  Doctor**\n**<:townicon2:896431548717473812> Random Town**\n**<:townicon2:896431548717473812> Random Town**\n**<:townicon2:896431548717473812> Random Town**\n**<:townicon2:896431548717473812> Random Town**\n**<:maficon2:891739940055052328> Mafioso**\n**<:maficon2:890328238029697044> Random Mafia**\n**<:hhicon2:891429754643808276> Headhunter**")
        elif (setup.lower().replace(" ", "") == "anarchy"):
            embed = discord.Embed(title="**Gamemode has been set to __Anarchy :drop_of_blood:__!**", colour=discord.Colour(0xcd95ff))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/O3tABe1id1w0dcI-B8MMo-DgXI9Co9xNaS6QSbjKU2o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/753967387149074543/c908a07ef8d6165ab31770e4b47f38ca.webp")
            embed.set_footer(text="Try /setups for a list of setups.", icon_url=ctx.author.avatar_url)

            embed.add_field(name="__**Anarchy :drop_of_blood: `(10P)`**__", value="**<:mayoricon2:897570023143518288> Mayor**\n**<:docicon2:890333203959787580> Doctor**\n**:mag_right: Town Investigative**\n**:mag_right: Town Investigative**\n**<:townicon2:896431548717473812> Random Town**\n**<:townicon2:896431548717473812> Random Town**\n**<:maficon2:891739940055052328> Mafioso**\n**<:maficon2:890328238029697044> Random Mafia**\n**:axe: Neutral Evil**\n**:game_die: Any**")
        elif (setup.lower().replace(" ", "") == "ranked"):
            embed = discord.Embed(title="**Gamemode has been set to __Ranked :star2:__!**", colour=discord.Colour(0xcd95ff))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/O3tABe1id1w0dcI-B8MMo-DgXI9Co9xNaS6QSbjKU2o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/753967387149074543/c908a07ef8d6165ab31770e4b47f38ca.webp")
            embed.set_footer(text="Try /setups for a list of setups.", icon_url=ctx.author.avatar_url)

            embed.add_field(name="__**Ranked :star2: `(10P)`**__", value="**<:docicon2:890333203959787580> Doctor**\n**<:enficon2:890339050865696798> Enforcer**\n**:mag_right: Town Investigative**\n**:mag_right: Town Investigative**\n**<:townicon2:896431548717473812> Random Town**\n**<:townicon2:896431548717473812> Random Town**\n**<:townicon2:896431548717473812> Random Town**\n**<:maficon2:891739940055052328> Mafioso**\n**<:consicon2:890336628269281350> Consort**\n**<:frameicon2:890365634913902602> Framer**")
        elif (setup.lower().replace(" ", "") == "truth"):
            embed = discord.Embed(title="**Gamemode has been set to __Truth <:consigicon2:896154845130666084>__!**", colour=discord.Colour(0xcd95ff))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/O3tABe1id1w0dcI-B8MMo-DgXI9Co9xNaS6QSbjKU2o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/753967387149074543/c908a07ef8d6165ab31770e4b47f38ca.webp")
            embed.set_footer(text="Try /setups for a list of setups.", icon_url=ctx.author.avatar_url)

            embed.add_field(name="__**Truth <:consigicon2:896154845130666084> `(7P)`**__", value="**<:deticon2:889673135438319637> Detective**\n**<:docicon2:890333203959787580>  Doctor**\n**<:townicon2:896431548717473812> Random Town**\n**<:townicon2:896431548717473812> Random Town**\n**<:townicon2:896431548717473812> Random Town**\n**<:maficon2:890328238029697044> Mafioso**\n**<:consigicon2:896154845130666084> Consigliere**")
        elif (setup.lower().replace(" ", "") == "delta"):
            embed = discord.Embed(title="You've accessed the secret beta gamemode.", description="wow thats really cool")
        else:
            embed = discord.Embed(title=f"**Gamemode has been set to __{string.capwords(setup)} :triangular_flag_on_post:__!**", colour=discord.Colour(0xcd95ff))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/O3tABe1id1w0dcI-B8MMo-DgXI9Co9xNaS6QSbjKU2o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/753967387149074543/c908a07ef8d6165ab31770e4b47f38ca.webp")
            embed.set_footer(text="Try /setups for a list of setups.", icon_url=ctx.author.avatar_url)
            message = ""
            c = var[ctx.guild.id]["comps"]
            for i in c[setup.lower()]:
                if (i == "RT"):
                    message += "Random Town\n"
                elif (i == "RM"):
                    message += "Random Mafia\n"
                elif (i == "RN"):
                    message += "Neutral Evil\n"
                elif (i == "TI"):
                    message += "Town Investigative\n"
                elif (i == "TS"):
                    message += f"**Town Support**\n"
                elif (i == "A"):
                    message += "Any\n"
                else:
                    message += f"{i}\n"

            if (message == ""):
                message = "The setup is empty."

            embed.add_field(name=f"__**{string.capwords(setup)} 🚩 **__", value=message)

        if (embed.title == "Something's wrong here..." and inter == True):
            await ctx.reply(embed=embed, ephemeral=True)

        
        await ctx.reply(embed=embed)

        var[ctx.guild.id]["setupz"] = setup

    else:
        if (setup.lower().replace(" ", "") == "any" or setup.lower().replace(" ", "") == "allany"):
            var[ctx.guild.id]["setupz"] = "Any"
            embed = discord.Embed(title="**Gamemode has been set to __All Any :game_die:__!**", color=0xCd95ff)
            embed.add_field(name="__**All Any :game_die: `(?P)`**__", value="**:game_die: Any x the amount of players playing :partying_face:**", inline=False)
            embed.add_field(name="**__Note :notepad_spiral:__**", value="**Night factions in a `5-6` player lobby can have up to `1` member.**\n\n**Night factions in a `7-9` player lobby can have up to `2` members.**\n\n**Night factions in a `10` player lobby can have up to `3` members.**", inline=False)
            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/O3tABe1id1w0dcI-B8MMo-DgXI9Co9xNaS6QSbjKU2o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/753967387149074543/c908a07ef8d6165ab31770e4b47f38ca.webp")
            embed.set_footer(text="Try /setups for a list of setups.")
            # embed = discord.Embed(title="**All Any is under maintainiance**", description="Please wait until we make All Any availiable again.", color=0xCd95ff)
            # embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/O3tABe1id1w0dcI-B8MMo-DgXI9Co9xNaS6QSbjKU2o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/753967387149074543/c908a07ef8d6165ab31770e4b47f38ca.webp")
            # embed.set_footer(text="Try /setups for a list of setups.")
            if (inter == False):
                await ctx.send(embed=embed)
            else:
                await ctx.reply(embed=embed)
        else:
            if (inter == False):
                await ctx.send("That setup doesn't exist. Get the setups using `/setups`.")
            else:
                await ctx.reply("That setup doesn't exist. Get the setups using `/setups`.", ephemeral=True)

@dislash.guild_only()
@slash.slash_command()
async def custom(inter):
    pass

@dislash.guild_only()
@custom.sub_command(
    name="view",
    description="View the roles in your custom setup",
    guild_ids=[871525831422398494]
)
async def viewCustom(inter):
    try:
        var[inter.guild.id]["test"]
    except:
        var[inter.guild.id] = copy.deepcopy(temp)

    embed = discord.Embed(title=f"**Your current custom setup :art::paintbrush:**", colour=discord.Colour(0xb3ffdd))

    embed.set_footer(text="You don't get silvers in a custom setup.", icon_url=inter.author.avatar_url)
    message = ""
    c = var[inter.guild.id]["comps"]
    em = var[inter.guild.id]["emoji"]

    for i in c["custom"]:
        if (i == "RT"):
            message += "Random Town <:townicon2:896431548717473812>\n"
        elif (i == "RM"):
            message += "Random Mafia <:maficon2:890328238029697044>\n"
        elif (i == "NE"):
            message = "Neutral Evil :axe:\n"
        elif (i == "TI"):
            message = "Town Investigative :mag_right:\n"
        elif (i == "TS"):
            message = f"**Town Support 🛠️**\n"
        elif (i == "NK"):
            message = f"**Neutral Killing :dagger:**\n"
        elif (i == "A"):
            message = "**Any** :game_die:\n"
        else:
            message += f"**{i}** {em[i.lower()]}\n"

    if (message == ""):
        message = "The setup is empty."

    embed.add_field(name=f"__**Custom :art::paintbrush: `(?P)`**__", value=message)

    try:
        await inter.reply(embed=embed)
    except:
        await inter.reply("The custom setup is empty.", ephemeral=True)

@dislash.guild_only()
@custom.sub_command(
    description="Add a role to your setup",
    options=[
        Option("role", "The role you want to add", OptionType.STRING, True, choices=[
            OptionChoice("Cop", "Cop"),
            OptionChoice("Detective", "Detective"),
            OptionChoice("Lookout", "Lookout"),
            OptionChoice("Doctor", "Doctor"),
            OptionChoice("Enforcer", "Enforcer"),
            OptionChoice("Mayor", "Mayor"),
            OptionChoice("Tracker", "Tracker"),
            OptionChoice("Psychic", "Psychic"),
            OptionChoice("Mafioso", "Mafioso"),
            OptionChoice("Consigliere", "Consigliere"),
            OptionChoice("Framer", "Framer"),
            OptionChoice("Consort", "Consort"),
            OptionChoice("Headhunter", "Headhunter"),
            OptionChoice("Jester", "Jester"),
            OptionChoice("Psychopath", "Psychopath"),
            OptionChoice("Random Town", "RT"),
            OptionChoice("Town Investigative", "TI"),
            OptionChoice("Town Support", "TS"),
            OptionChoice("Neutral Evil", "NE"),
            OptionChoice("Neutral Killing", "NK"),
            OptionChoice("Random Mafia", "RM"),
            OptionChoice("Any", "A")
        ])
    ],
    guild_ids=[871525831422398494]
)
async def add(inter, role=None):
    try:
        var[inter.guild.id]["test"]
    except:
        var[inter.guild.id] = copy.deepcopy(temp)

    try:
        if (inter.author.id != var[inter.guild.id]["players"][0]):
            await inter.reply("Only the host can add roles to a custom setup.", ephemeral=True)
            return
    except:
        await inter.reply("The game is empty.", ephemeral=True)
        return

    

    c = var[inter.guild.id]["comps"]

    if (c["custom"].count("Mafioso") == 1 and role == "Mafioso"):
        await inter.reply("There can't be more than 1 Mafioso in a game.", ephemeral=True)
        return
    if (c["custom"].count("Mayor") == 1 and role == "Mayor"):
        await inter.reply("There can't be more than 1 Mayor in a game.", ephemeral=True)
        return
        
    c["custom"].append(str(role))

    c = var[inter.guild.id]["comps"]

    message = ""
    thing = ""
    em = var[inter.guild.id]["emoji"]

    for i in c["custom"]:
        if (i == "RT"):
            message += "Random Town <:townicon2:896431548717473812>\n"
        elif (i == "RM"):
            message += "Random Mafia <:maficon2:890328238029697044>\n"
        elif (i == "NE"):
            message = "Neutral Evil :axe:\n"
        elif (i == "TI"):
            message = "Town Investigative :mag_right:\n"
        elif (i == "TS"):
            message = f"**Town Support 🛠️**\n"
        elif (i == "NK"):
            message = f"**Neutral Killing :dagger:**\n"
        elif (i == "A"):
            message = "Any :game_die:\n"
        else:
            message += f"{i} {em[i.lower()]}\n"

    if (role == "RT"):
        thing = "Random Town <:townicon2:896431548717473812>"
    elif (role == "RM"):
        thing = "Random Mafia <:maficon2:890328238029697044>"
    elif (role == "NE"):
        thing = "Neutral Evil :axe:"
    elif (role == "TI"):
        thing = "Town Investigative :mag_right:"
    elif (role == "TS"):
        thing = f"**Town Support 🛠️**"
    elif (role == "NK"):
        thing = f"**Neutral Killing :dagger:**"
    elif (role == "A"):
        thing = "Any :game_die:"
    else:
        thing += f"{i}"

    embed = discord.Embed(title=f"{thing} has been added to the setup!", colour=discord.Colour(0xb3ffdd), description=f"__**Custom :art::paintbrush: `(?P)`**__\n**{message}**")

    embed.set_footer(text="You need at least 2 roles for a custom setup.", icon_url=inter.author.avatar_url)

    await inter.create_response(embed=embed)

@dislash.guild_only()
@custom.sub_command(
    description="Remove a role to your setup",
    options=[
        Option("role", "The role you want to remove", OptionType.STRING, True, choices=[
            OptionChoice("Cop", "Cop"),
            OptionChoice("Detective", "Detective"),
            OptionChoice("Lookout", "Lookout"),
            OptionChoice("Doctor", "Doctor"),
            OptionChoice("Enforcer", "Enforcer"),
            OptionChoice("Mayor", "Mayor"),
            OptionChoice("Tracker", "Tracker"),
            OptionChoice("Psychic", "Psychic"),
            OptionChoice("Mafioso", "Mafioso"),
            OptionChoice("Consigliere", "Consigliere"),
            OptionChoice("Framer", "Framer"),
            OptionChoice("Consort", "Consort"),
            OptionChoice("Headhunter", "Headhunter"),
            OptionChoice("Jester", "Jester"),
            OptionChoice("Psychopath", "Psychopath"),
            OptionChoice("Random Town", "RT"),
            OptionChoice("Town Investigative", "TI"),
            OptionChoice("Town Support", "TS"),
            OptionChoice("Neutral Evil", "RN"),
            OptionChoice("Random Mafia", "RM"),
            OptionChoice("Any", "A")
        ])
    ],
    guild_ids=[871525831422398494]
)
async def remove(inter, role=None):
    try:
        var[inter.guild.id]["test"]
    except:
        var[inter.guild.id] = copy.deepcopy(temp)

    try:
        if (inter.author.id != var[inter.guild.id]["players"][0]):
            await inter.reply("Only the host can remove roles to a custom setup.", ephemeral=True)
    except:
        await inter.reply("The game is empty.", ephemeral=True)

    c = var[inter.guild.id]["comps"]

    if (role not in c["custom"]):
        await inter.reply("That role isn't in the setup.")
        return

    c["custom"].remove(str(role))

    em = var[inter.guild.id]["emoji"]
    message = ""
    thing = ""

    for i in c["custom"]:
        if (i == "RT"):
            message += "Random Town <:townicon2:896431548717473812>\n"
        elif (i == "RM"):
            message += "Random Mafia <:maficon2:890328238029697044>\n"
        elif (i == "NE"):
            message = "Neutral Evil :axe:\n"
        elif (i == "TI"):
            message = "Town Investigative :mag_right:\n"
        elif (i == "TS"):
            message = f"**Town Support 🛠️**\n"
        elif (i == "NK"):
            message = f"**Neutral Killing :dagger:**\n"
        elif (i == "A"):
            message = "**Any** :game_die:\n"
        else:
            message += f"**{i}** {em[i.lower()]}\n"

    if (role == "RT"):
        thing = "**Random Town** <:townicon2:896431548717473812>"
    elif (role == "RM"):
        thing = "**Random Mafia** <:maficon2:890328238029697044>"
    elif (role == "NE"):
        thing = "**Neutral Evil** :axe:"
    elif (role == "TI"):
        thing = "**Town Investigative** :mag_right:"
    elif (role == "TS"):
        thing = f"**Town Support 🛠️**"
    elif (role == "NK"):
        thing = f"**Neutral Killing :dagger:**"
    elif (role == "A"):
        thing = "**Any** :game_die:"
    else:
        thing = f"**{i}**"

    if (message == ""):
        message = "The setup is empty."

    embed = discord.Embed(title=f"{thing} has been removed from the setup", colour=discord.Colour(0xffc6c6), description=f"__**Custom :art::paintbrush: `(?P)`**__\n{message}")

    embed.set_footer(text="You need at least 2 roles in a custom setup.", icon_url=inter.author.avatar_url)

    await inter.create_response(embed=embed)

@dislash.guild_only()
@slash.slash_command(
    name="roles",
    description="View the roles of Anarchic"
)
async def rolez(inter):
    await inter.reply(type=5)
    try:
        var[inter.guild.id]["test"]
    except:
        var[inter.guild.id] = copy.deepcopy(temp)
    embed = discord.Embed(title="**__List of Roles :performing_arts:__**", colour=discord.Colour(0x8266dc), description="Here are a list of roles that are playable in **Anarchic 1.0.0**.")

    embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/S8kYnDiF37aks-RBlGNZVz6gbTasCOJy1R7IB9iE3NQ/%3F5765650006/https/www12.lunapic.com/editor/working/163036526867946112")

    embed.add_field(name="__**Town <:townicon2:896431548717473812>**__", value="<:copicon2:889672912905322516> **Cop (Cop)**\n<:deticon2:889673135438319637> **Detective (Det)**\n<:loicon2:889673190392078356> **Lookout (LO)**\n<:docicon2:890333203959787580> **Doctor (Doc)**\n<:enficon2:890339050865696798> **Enforcer (Enf)**\n<:mayoricon2:897570023143518288> **Mayor (Mayor)**\n<:psyicon2:896159311078780938> **Psychic (Psy**)")
    embed.add_field(name="__**Mafia <:maficon2:890328238029697044>**__", value="<:maficon2:891739940055052328> **Mafioso (Maf)**\n<:frameicon2:890365634913902602> **Framer (Frame)**\n<:consigicon2:896154845130666084> **Consigliere (Consig)**\n<:consicon2:890336628269281350> **Consort (Cons)**")
    embed.add_field(name="__**Neutrals :axe:**__", value="<:hhicon2:891429754643808276> **Headhunter (HH)**\n<:jesticon2:889968373612560394> **Jester (Jest)**")
    await inter.edit(embed=embed)

@dislash.guild_only()
@slash.slash_command(
    name="setups",
    description="View the setups of Anarchic"
)
async def ssetups(inter):
    await inter.reply(type=5)
    try:
        var[inter.guild.id]["test"]
    except:
        var[inter.guild.id] = copy.deepcopy(temp)
    await _setups(inter, True)

@bot.command()
async def setups(ctx):
    await _setups(ctx)

async def _setups(ctx, inter=False):
    embed = discord.Embed(title="__**<a:Tada:841483453044490301> List of playable setups! <a:Tada:841483453044490301>**__", description="", color=0x7eafa4)
    embed.add_field(name="**__5 Players__**", value="""**(5P) Classic :triangular_flag_on_post:**
**(5P) Enforced <:enficon2:890339050865696798>**""")
    embed.add_field(name="**__6 Players__**", value="""**(6P) Execution <:hhicon2:891429754643808276>**""")
    embed.add_field(name="**__7 Players__**", value="""**(7P) Duet <:consicon2:890336628269281350>**
**(7P) Framed <:frameicon2:890365634913902602>**
**(7P) Truth <:consigicon2:896154845130666084>**""")
    embed.add_field(name="**__8 Players__**", value="""**(8P) Legacy <a:sparkles:833870572923650068>**""")
    embed.add_field(name="**__9 Players__**", value="""**(9P) Scattered :diamond_shape_with_a_dot_inside:**""")
    embed.add_field(name="**__10 Players__**", value="""**(10P) Anarchy :drop_of_blood:**
**(10P) Ranked :star2:**""")
    embed.add_field(name="**__Any__**", value="""**(?P) All Any :game_die:**""")
    embed.set_footer(text="Try playing one of our setups.")
    embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")

    if (inter == True):
        await ctx.edit(embed=embed)
        return

    await ctx.send(embed=embed)

@bot.command()
@commands.guild_only()
async def dad(ctx):
    await ctx.send("wtf")

@bot.command()
@commands.guild_only()
async def babyframer(ctx):
    await ctx.send("MAO")

@bot.command()
@commands.guild_only()
async def cows(ctx):
    await ctx.send("literally")

#utils
async def lock(channel):
    overwrite = discord.PermissionOverwrite()
    overwrite.send_messages = False
    overwrite.read_messages = True

    for i in var[channel.guild.id]["players"]:
        user = await channel.guild.fetch_member(i)
        await channel.set_permissions(user, overwrite=overwrite)

async def unlock(channel):
    overwrite = discord.PermissionOverwrite()
    overwrite.send_messages = False
    overwrite.read_messages = True

    for i in var[channel.guild.id]["players"]:
        user = await channel.guild.fetch_member(i)
        if (Player.get_player(i, var[channel.guild.id]["playerdict"]).dead == True):
            overwrite.send_messages = False
            overwrite.read_messages = True
            await channel.set_permissions(user, overwrite=overwrite)
        else:
            overwrite.send_messages = True
            overwrite.read_messages = True
            await channel.set_permissions(user, overwrite=overwrite)

async def assignroles(comp:str, ctx):
    c = []
    my = []

    if (comp.lower() == "any"):
        for _ in range(len(var[ctx.id]["players"])):
            my.append("A")

    while True:
        if (comp.lower() != "any"):
            c = var[ctx.id]["comps"][var[ctx.id]["setupz"]]
        else:
            c = copy.copy(my)

        co:list = copy.copy(c)
        mafs = 0
        mafiosos = 0
        id = 1

        for i in var[ctx.id]["players"]:
            var[ctx.id]["playerdict"]["p" + str(id)].id = int(i)
            user:discord.User = bot.get_user(i)
            item = ""

            if (guilds[str(i)]["equipped"] != None):
                item = guilds[str(i)]["equipped"]
                print(item)

                if (item == "cop"):
                    if ("Cop" in co or "RT" in co or "TI" in co):
                        for _ in range(2):
                            co.append("Cop")
                elif (item == "mafioso"):
                    if ("Mafioso" in co):
                        for _ in range(2):
                            co.append("Mafioso")
                elif (item == "doctor"):
                    if ("Doctor" in co or "RT" in co):
                        for _ in range(2):
                            co.append("Doctor")
                elif (item == "enforcer"):
                    if ("Enforcer" in co or "RT" in co):
                        for _ in range(2):
                            co.append("Enforcer")
                elif (item == "consig"):
                    if ("Consigliere" in co or "RM" in co):
                        for _  in range(2):
                            co.append("Consigliere")
                elif (item == "framer"):
                    if ("Framer" in co or "RM" in co):
                        for _ in range(2):
                            co.append("Framer")
                elif (item == "headhunter"):
                    if ("Headhunter" in co or "RN" in co):
                        for _ in range(2):
                            co.append("Headhunter")
                elif (item == "jester"):
                    if ("Jester" in co or "RN" in co):
                        for _ in range(2):
                            co.append("Jester")
                elif (item == "lookout"):
                    if ("Lookout" in co or "RT" in co or "TI" in co):
                        for _ in range(2):
                            co.append("Lookout")
                elif (item == "detective"):
                    if ("Detective" in co or "RT" in co or "TI" in co):
                        for _ in range(2):
                            co.append("Detective")
                elif (item == "psychic"):
                    if ("Psychic" in co or "RT" in co or "TS" in co):
                        for _ in range(2):
                            co.append("Psychic")
                elif (item == "mayor"):
                    if ("Mayor" in co or "RT" in co or "TS" in co):
                        for _ in range(2):
                            co.append("Mayor")
                elif (item == "consort"):
                    if ("Consort" in co or "RM" in co):
                        for _ in range(2):
                            co.append("Consort")

            hisrole = random.choice(co)
            thing = item
            if (thing == "consig"):
                thing = "consigliere"



            if (hisrole == string.capwords(thing)):
                guilds[str(i)]["equipped"] = None
                inv[str(i)][item]["amount"] -= 1

                for _ in range(2):
                    co.remove(string.capwords(item))

            try:
                co.remove(hisrole)
            except:
                pass

            if (hisrole == "RT"):
                hisrole = random.choice(var[ctx.id]["towns"])

                for i in var[ctx.id]["playerdict"].values():
                    if (i.role.lower() == "mayor" and hisrole.lower() == "mayor"):
                        while True:
                            hisrole = random.choice(var[ctx.id]["towns"])
                            
                            if (hisrole.lower() != "mayor"):
                                break

            elif (hisrole == "RM"):
                hisrole = random.choice(var[ctx.id]["mafias"])
            elif (hisrole == "RC"):
                hisrole = random.choice(var[ctx.id]["cults"])
            elif (hisrole == "RN"):
                hisrole = random.choice(var[ctx.id]["neutrals"])
            elif (hisrole == "TI"):
                hisrole = random.choice(var[ctx.id]["investigatives"])
            elif (hisrole == "TS"):
                hisrole = random.choice(var[ctx.id]["support"])
                for i in var[ctx.id]["playerdict"].values():
                    if (i.role.lower() == "mayor" and hisrole.lower() == "mayor"):
                        while True:
                            hisrole = random.choice(var[ctx.id]["support"])
                            
                            if (hisrole.lower() != "mayor"):
                                break
            elif (hisrole == "A"):
                hisrole:str = random.choice(var[ctx.id]["roles"])

                for i in var[ctx.id]["playerdict"].values():
                    if (i.role.lower() == "mayor" and hisrole.lower() == "mayor"):
                        while True:
                            hisrole = random.choice(var[ctx.id]["roles"])
                            
                            if (hisrole.lower() != "mayor"):
                                break

            idd = "p" + str(id)
            ll = hisrole.lower()


            if (ll == "mafioso" or ll == "consigliere" or ll == "framer" or ll == "consort"):
                mafs += 1
            
            if (ll == "mafioso"):
                mafiosos += 1

            var[ctx.id]["playerdict"]["p" + str(id)].role = hisrole
            id += 1

        if (mafs > 0 and mafiosos == 1):
            amount = PlayerSize(len(var[ctx.id]["players"]))
            if (amount == GameSize.Small):
                if (mafs == 1):
                    break
            if (amount == GameSize.Medium):
                if (mafs <= 2):
                    break
            if (amount == GameSize.Large):
                if (mafs <= 3):
                    break
            if (amount == GameSize.TooSmall or amount == GameSize.TooBig):
                break

    targetembed = None

    for i in var[ctx.id]["playerdict"].values():
        if (i.role.lower() == "headhunter"):
            for o in var[ctx.id]["players"]:
                play = Player.get_player(o, var[ctx.id]["playerdict"])

                if (play.role.lower() != "mayor" and play.role.lower() in var[ctx.id]["towns"] and i.hhtarget == None):
                    i.hhtarget = play.id
                    user = bot.get_user(i.id)
                    targetembed = discord.Embed(title=f"**Your target is {bot.get_user(play.id).name}#{bot.get_user(play.id).discriminator}.**", colour=discord.Colour(0x39556b), description="Your target has wronged you and now it's their time to pay. Get them lynch in order to win.")

                    targetembed.set_thumbnail(url=bot.get_user(play.id).avatar_url)
                    targetembed.set_footer(text="If your target dies at night, you will be converted into a Jester.", icon_url=bot.get_user(i.id).avatar_url)

            if (i.hhtarget == None):
                i.role = "Jester"
                i.faction = Faction.Neutral
                i.defense = Defense.Default

    for i in (var[ctx.id]["playerdict"].values()):
        if (i.id != 0):
            emb = await bootyfulembed(i.role, bot.get_user(i.id), Player.get_player(i.id, var[ctx.id]["playerdict"]))
            
            if (839842855970275329 in var[ctx.id]["players"]):
                print(f"{bot.get_user(i.id).name}#{bot.get_user(i.id).discriminator}, role is {string.capwords(i.role)}")

            Player.get_player(i.id, var[ctx.id]["playerdict"]).ogrole = string.capwords(i.role)

            try:
                await bot.get_user(i.id).send(embed=emb)
            except discord.Forbidden as e:
                print(e)
                # raise ValueError()
                pass

            if (i.role.lower() == "headhunter"):
                await bot.get_user(i.id).send(embed=targetembed)




    with open('inv.json', 'w') as jsonf:
        json.dump(inv, jsonf)

    with open('guilds.json', 'w') as jsonf:
        json.dump(guilds, jsonf)

async def bootyfulembed(roled:str, author, player:Player=None):
    role = roled.lower()
    embed = None
    try:
        if (role == "cop"):
            embed = discord.Embed(title="**Your role is Cop**", colour=discord.Colour(0x7ed321), description="A reliable law enforcer, skilled in keeping evildoers in check.")

            embed.set_image(url="https://images-ext-2.discordapp.net/external/lxy0B33My7VTF8-DAztYa8qUyl5TYxeXEuGmqRnxGCY/%3Fwidth%3D493%26height%3D634/https/media.discordapp.net/attachments/765738640554065962/871777631798964294/unknown.png")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889672912905322516.png?size=80")
            embed.set_footer(text="Town Investigative 🔎", icon_url=author.avatar_url)

            embed.add_field(name="**Atk ⚔️:**", value="None", inline=True)
            embed.add_field(name="**Res 🛡️:**", value="None", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Town", inline=False)
            embed.add_field(name="**Action :man_running::**", value="Interrogate a player each night", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="You will learn if your target is **Innocent <:inno:873636640227205160>** or **Suspicious <:sus:873637612571746324>**", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Eliminate all the criminals who may try to harm the **Town** <:townicon2:896431548717473812>", inline=False)
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon2:889672912905322516>:** Your target seems **Innocent <:inno:873636640227205160>**\n**Detective <:deticon2:889673135438319637>:** Your target seeks revenge. They must be a **Cop <:copicon2:889672912905322516>**, **Headhunter <:hhicon2:891429754643808276>**, **Mafioso <:maficon2:891739940055052328>** or **Enforcer <:enficon2:890339050865696798>**\n**Consigliere <:consigicon2:896154845130666084>:** Your target is the law enforcer of the town. They must be a **Cop <:copicon2:889672912905322516>**", inline=False)
            if (player != None):
                player.faction = Faction.Town #The player's faction (Town, Mafia, Neutral)
                player.appearssus = False #If the player appears sus
                player.detresult = "Your target seeks revenge.>EThey must be a **Cop <:copicon2:889672912905322516>**>E**Headhunter <:hhicon2:891429754643808276>**>E**Mafioso <:maficon2:891739940055052328>**>E**Enforcer <:enficon2:890339050865696798>**." #Det results
                player.defense = Defense.Default #defense
                player.distraction = False #consort
        elif (role == "tracker"):
            embed = discord.Embed(title="**Your role is Tracker**", colour=discord.Colour(0x7ed321), description="A skilled pathfinder who scouts the night.")

            embed.set_image(url="https://images-ext-2.discordapp.net/external/vxOShXchGrPMHJEcrLhW914asNZollLv-GvV70esn8Y/%3Fwidth%3D562%26height%3D634/https/media.discordapp.net/attachments/765738640554065962/872225776211202068/unknown.png")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/871525831422398497/890339048097456148/EnfIcon.png")
            embed.set_footer(text="Town Investigative 🔎", icon_url=author.avatar_url)

            embed.add_field(name="**Atk ⚔️:**", value="None", inline=True)
            embed.add_field(name="**Res 🛡️:**", value="None", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Town", inline=False)
            embed.add_field(name="**Action :man_running::**", value="Track a player each night", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="You will know who your target visits", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Eliminate all the criminals who may try to harm the **Town** <:townicon2:896431548717473812>", inline=False)
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon2:889672912905322516>:** Your target seems **Innocent <:inno:873636640227205160>**\n**Detective <:deticon2:889673135438319637>:** Your target works with sensitive information. They must be a Detective <:deticon2:889673135438319637>, Consigliere <:consigicon:871527176527315025>, Tracker :trackicon2: or Lookout <:loicon2:889673190392078356>**\n**Consigliere <:consigicon2:896154845130666084>:** Your target keeps track of others. They must be a **Tracker :trackicon2:**", inline=False)
        
            if (player != None):
                player.faction = Faction.Town #The player's faction (Town, Mafia, Neutral)
                player.appearssus = False #If the player appears sus
                player.detresult = "Your target seeks revenge.>EThey must be a **Cop <:copicon2:889672912905322516>**>E**Headhunter <:hhicon2:891429754643808276>**>E**Mafioso <:maficon2:891739940055052328>**>E**Enforcer <:enficon2:890339050865696798>**." #Det results
                player.defense = Defense.Default #defense
                player.distraction = False #consort
        elif (role == "detective"):
            embed = discord.Embed(title="**Your role is Detective**", colour=discord.Colour(0x7ed321), description="A private investigator who uncovers one's secrets")

            embed.set_image(url="https://media.discordapp.net/attachments/878437549721419787/882410811241414696/unknown.png?width=411&height=468")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889673135438319637.png?size=80")
            embed.set_footer(text="Town Investigative 🔎", icon_url=author.avatar_url)

            embed.add_field(name="**Atk ⚔️:**", value="None", inline=True)
            embed.add_field(name="**Res 🛡️:**", value="None", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Town", inline=False)
            embed.add_field(name="**Action :man_running::**", value="Investigate a player each night", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="You will learn what possible roles your target might be", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Eliminate all the criminals who may try to harm the **Town** <:townicon2:896431548717473812>", inline=False)
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon2:889672912905322516>:** Your target seems **Innocent <:inno:873636640227205160>**\n**Detective <:deticon2:889673135438319637>:** Your target works with sensitive information. They must be a **Detective <:deticon2:889673135438319637>**, **Consigliere <:consigicon:871527176527315025>** or **Lookout <:loicon2:889673190392078356>**\n**Consigliere <:consigicon2:896154845130666084>:**Your target secretly gathers infomation. They must be a **Detective <:deticon2:889673135438319637>**", inline=False)
            if (player != None):
                player.faction = Faction.Town #The player's faction (Town, Mafia, Neutral)
                player.appearssus = False #If the player appears sus
                player.detresult = "Your target hides in the shadows. They must be a **Doctor <:docicon2:890333203959787580>**, **Lookout <:loicon2:889673190392078356>**, **Consort <:consicon2:890336628269281350>** or **Detective <:deticon2:889673135438319637>**." #Det results
                player.defense = Defense.Default #defense
                player.distraction = False #consort
        elif (role == "doctor"):
            embed = discord.Embed(title="**Your role is Doctor**", colour=discord.Colour(0x7ed321), description="A secret surgeon who heals people at night")

            embed.set_image(url="https://images-ext-2.discordapp.net/external/a_EBqbeOJpbdk-Cwmg0ECTonyvRrMVqHHnJBEaiAQig/https/media.discordapp.net/attachments/887804073024299008/891814142984454155/DocImage.png?width=326&height=383")
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/871525831422398497/890333113572548719/DocIcon.png?width=701&height=701")
            embed.set_footer(text="Town Protective 💉", icon_url=author.avatar_url)

            embed.add_field(name="**Atk ⚔️:**", value="None", inline=True)
            embed.add_field(name="**Res 🛡️:**", value="None", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Town", inline=False)
            embed.add_field(name="**Action :man_running::**", value="Heal a player each night", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="You will grant your target **powerful** defense.\nYou and your target will be notified of a successful heal\nYou may heal yourself once", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Eliminate all the criminals who may try to harm the **Town** <:townicon2:896431548717473812>", inline=False)
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon2:889672912905322516>:** Your target seems **Innocent <:inno:873636640227205160>**\n**Detective <:deticon2:889673135438319637>:** Your target hides in shadows. They must be a **Doctor <:docicon2:890333203959787580>**, **Psychic <:psyicon2:896159311078780938>** or **Consort <:consicon2:890336628269281350>**\n**Consigliere <:consigicon2:896154845130666084>:** Your target is a profound surgeon. They must be a **Doctor <:docicon2:890333203959787580>**", inline=False)
            if (player != None):
                player.faction = Faction.Town #The player's faction (Town, Mafia, Neutral)
                player.appearssus = False #If the player appears sus
                player.detresult = "Your target hides in the shadows. They must be a **Doctor <:docicon2:890333203959787580>**, **Lookout <:loicon2:889673190392078356>**, **Consort <:consicon2:890336628269281350>** or **Detective <:deticon2:889673135438319637>**." #Det results
                player.defense = Defense.Default #defense
                player.distraction = False #consort
        elif (role == "enforcer"):
            embed = discord.Embed(title="**Your role is Enforcer**", colour=discord.Colour(0x7ed321), description="A rogue vigilante with an eye out for justice.")

            embed.set_image(url="https://images-ext-2.discordapp.net/external/vxOShXchGrPMHJEcrLhW914asNZollLv-GvV70esn8Y/%3Fwidth%3D562%26height%3D634/https/media.discordapp.net/attachments/765738640554065962/872225776211202068/unknown.png")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/871525831422398497/890339048097456148/EnfIcon.png")
            embed.set_footer(text="Town Killing 🔫", icon_url=author.avatar_url)

            embed.add_field(name="**Atk ⚔️:**", value="Basic", inline=True)
            embed.add_field(name="**Res 🛡️:**", value="None", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Town", inline=False)
            embed.add_field(name="**Action :man_running::**", value="You may choose to shoot a player", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="You may not shoot night one\nIf you kill a **Town** member, you will commit **suicide** and be dealt a piercing attack", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Eliminate all the criminals who may try to harm the **Town** <:townicon2:896431548717473812>", inline=False)
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon2:889672912905322516>:** Your target seems **Innocent <:inno:873636640227205160>**\n**Detective <:deticon2:889673135438319637>:** Your target seeks revenge. They must be a **Cop <:copicon2:889672912905322516>**, **Headhunter <:hhicon2:891429754643808276>**, **Mafioso <:maficon2:891739940055052328>** or **Enforcer <:enficon2:890339050865696798>**\n**Consigliere <:consigicon2:896154845130666084>:** Your target is willing to bend the law to entact justice. They must be an **Enforcer <:enficon2:890339050865696798>**", inline=False)
            if (player != None):
                player.faction = Faction.Town #The player's faction (Town, Mafia, Neutral)
                player.appearssus = False #If the player appears sus
                player.detresult = "Your target seeks revenge. They must be a **Cop <:copicon2:889672912905322516>**, **Headhunter <:hhicon2:891429754643808276>**, **Mafioso <:maficon2:891739940055052328>** or **Enforcer <:enficon2:890339050865696798>**." #Det results
                player.defense = Defense.Default #defense
                player.distraction = False #consort
        elif (role == "mafioso"):
            embed = discord.Embed(title="**Your role is Mafioso**", colour=discord.Colour(0xd0021b), description="The right hand man of organized crime.")
            
            embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/899413050602446898/unknown.png?width=371&height=383")
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/897585492562964531/MafIcon2.png?width=676&height=676")
            embed.set_footer(text="Mafia Killing 🗡️", icon_url=author.avatar_url)

            embed.add_field(name="**Atk ⚔️:**", value="Basic", inline=True)
            embed.add_field(name="**Res 🛡️:**", value="None", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Mafia", inline=False)
            embed.add_field(name="**Action :man_running::**", value="Attack a player each night", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="If you die, a random **Mafia** member will be promoted to the new **Mafioso <:maficon2:891739940055052328>**", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Kill all those who may rival the **Mafia <:maficon2:890328238029697044>**.", inline=False)
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon2:889672912905322516>:** Your target is **Suspicious <:sus:873637612571746324>**\n**Detective <:deticon2:889673135438319637>:** Your target seeks revenge. They must be a **Cop <:copicon2:889672912905322516>**, **Headhunter <:hhicon2:891429754643808276>**, **Mafioso <:maficon2:891739940055052328>** or **Enforcer <:enficon2:890339050865696798>**", inline=False)
            if (player != None):
                player.faction = Faction.Mafia #The player's faction (Town, Mafia, Neutral)
                player.appearssus = True #If the player appears sus
                player.detresult = "Your target seeks revenge. They must be a **Cop <:copicon2:889672912905322516>**, **Headhunter <:hhicon2:891429754643808276>**, **Mafioso <:maficon2:891739940055052328>** or **Enforcer <:enficon2:890339050865696798>**." #Det results
                player.defense = Defense.Default #defense
                player.distraction = False #consort
        elif (role == "psychopath"):
            embed = discord.Embed(title="**Your role is Psychopath**", colour=discord.Colour(0x5865f2), description="A bloodthirsty killer who wishes to dye the town in blood.")

            embed.set_image(url="https://images-ext-2.discordapp.net/external/eycqJUxdoIUdEfWh2VUlbsk3hmOVLjv92msbMRIu7SE/https/images-ext-1.discordapp.net/external/0pxLaxbZeGoPqcm5dBEX5Xi_vP_pjTfn8LZdDeW3phs/%253Fwidth%253D455%2526height%253D634/https/media.discordapp.net/attachments/765738640554065962/871819221061992469/unknown.png")
            embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/887shAVNNehLzrnYya8OdUqTz_je39AFLICYfHXs3uM/https/images-ext-2.discordapp.net/external/6hXqEUIrXTeZZU8Zl1rxdmVm7CvdsOsGtUJfd9jO49I/https/media.discordapp.net/attachments/765738640554065962/871862910073315348/imageedit_1_5372740602.png")
            embed.set_footer(text="Neutral Killing 🔪", icon_url=author.avatar_url)

            embed.add_field(name="**Atk ⚔️:**", value="Basic", inline=True)
            embed.add_field(name="**Res 🛡️:**", value="Basic", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Neutral", inline=False)
            embed.add_field(name="**Action :man_running::**", value="Stab a player each night", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="None", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Kill all who would oppose you.", inline=False)
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon:871526445619482634>:** Your target is acting **Psychotic <:psycho:877584821180825691>**\n**Detective <:deticon:871526928799129651>:** Your target hides in shadows. They must be a **Doctor <:docicon2:890333203959787580>**, **Medium <:jesticon:872187561597075476>** **Psychopath**, or **Consort <:consicon2:890336628269281350>**\n**Consigliere <:consigicon2:896154845130666084>:** Your target is a cold blooded murderer. They must be a **Psychopath**", inline=False) 
            if (player != None):
                player.faction = Faction.Neutral #The player's faction (Town, Mafia, Neutral)
                player.appearssus = True #If the player appears sus
                player.detresult = "Your target seeks revenge. They must be a **Cop <:copicon2:889672912905322516>**, **Headhunter <:hhicon2:891429754643808276>**, **Mafioso <:maficon2:891739940055052328>** or **Enforcer <:enficon2:890339050865696798>**." #Det results
                player.defense = Defense.Basic #defense
                player.distraction = False #consort
        elif (role == "mayor"):
            embed = discord.Embed(title="**Your role is Mayor**", colour=discord.Colour(0x7ed321), description="The leader of the town")

            embed.set_image(url="https://cdn.discordapp.com/attachments/765738640554065962/886652670230790214/unknown.png")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/897570023143518288.png?size=80")
            embed.set_footer(text="Town Support 🛠️", icon_url=author.avatar_url)

            embed.add_field(name="**Atk ⚔️:**", value="None", inline=True)
            embed.add_field(name="**Res 🛡️:**", value="None", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Town", inline=False)
            embed.add_field(name="**Action :man_running::**", value="Reveal yourself as **Mayor <:mayoricon2:897570023143518288>** to the rest of the town", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="You will have 3 votes once you reveal", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Eliminate all the criminals who may try to harm the **Town <:townicon2:896431548717473812>**", inline=False)	
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon2:889672912905322516>:** Your target seems **Innocent <:inno:873636640227205160>**\n**Detective <:deticon2:889673135438319637>:** Your target may not be what they seem at first glance. They must be a **Framer <:frameicon2:890365634913902602>**, **Jester <:jesticon2:889968373612560394>** or **Mayor <:mayoricon2:897570023143518288>**\n**Consigliere <:consigicon2:896154845130666084>:** Your target is the leader of the town. They must be the **Mayor <:mayoricon2:897570023143518288>**", inline=False)
            if (player != None):
                player.faction = Faction.Town #The player's faction (Town, Mafia, Neutral)
                player.appearssus = False #If the player appears sus
                player.detresult = "Your target might not be what they seem at first glance. They must be a **Framer <:frameicon2:890365634913902602>**, **Jester <:jesticon2:889968373612560394>** or **Mayor <:mayoricon2:897570023143518288>**." #Det results
                player.defense = Defense.Default #defense
                player.distraction = False #consort
        elif (role == "psychic"):
            embed = discord.Embed(title="**Your role is Psychic**", colour=discord.Colour(0x7ed321), description="A powerful mystic who speaks with the dead.")

            embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/896172274716127272/image0.png?width=451&height=528")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896159311078780938.png?size=80")
            embed.set_footer(text="Town Support 🛠️", icon_url=author.avatar_url)

            embed.add_field(name="**Atk ⚔️:**", value="None", inline=True)
            embed.add_field(name="**Res 🛡️:**", value="None", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Town", inline=False)
            embed.add_field(name="**Action :man_running::**", value="None", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="You can speak to the dead", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Eliminate all the criminals who may try to harm the **Town <:townicon2:896431548717473812>**", inline=False)	
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon2:889672912905322516>:** Your target seems **Innocent <:inno:873636640227205160>**\n**Detective <:deticon2:889673135438319637>:** Your target hides in shadows. They must be a **Doctor <:docicon2:890333203959787580>**, **Psychic <:psyicon2:896159311078780938>** or **Consort <:consicon2:890336628269281350>**", inline=False)

            if (player != None):
                player.faction = Faction.Town #The player's faction (Town, Mafia, Neutral)
                player.appearssus = False #If the player appears sus
                player.detresult = "Your target might not be what they seem at first glance. They must be a **Framer <:frameicon2:890365634913902602>**, **Jester <:jesticon2:889968373612560394>** or **Mayor <:mayoricon2:897570023143518288>**." #Det results
                player.defense = Defense.Default #defense
                player.distraction = False #consort
        elif (role == "consort"):
            embed = discord.Embed(title="**Your role is Consort**", colour=discord.Colour(0xd0021b), description="A hooker who works for organized crime")

            embed.set_image(url="https://media.discordapp.net/attachments/879064140285620315/882069060517503006/unknown.png?width=309&height=468")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/873954973556293632.png?v=1")
            embed.set_footer(text="Mafia Support 🧲", icon_url=author.avatar_url)

            embed.add_field(name="**Atk ⚔️:**", value="None", inline=True)
            embed.add_field(name="**Res 🛡️:**", value="None", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Mafia", inline=False)
            embed.add_field(name="**Action :man_running::**", value="Distract a player each night", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="You are immune to **distractions**", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Kill all those who may rival the **Mafia <:maficon2:890328238029697044>**.", inline=False)
            embed.add_field(name="""**Investigation Results :mag_right::**""", value="**Cop <:copicon2:889672912905322516>:** Your target is **Suspicious <:sus:873637612571746324>**\n**Detective <:deticon2:889673135438319637>:** Your target hides in shadows. They must be a **Doctor <:docicon2:890333203959787580>**, **Psychic <:psyicon2:896159311078780938>** or **Consort <:consicon2:890336628269281350>**", inline=False)
            if (player != None):
                player.faction = Faction.Mafia #The player's faction (Town, Mafia, Neutral)
                player.appearssus = True #If the player appears sus
                player.detresult = "Your target hides in the shadows. They must be a **Doctor <:docicon2:890333203959787580>**, **Lookout <:loicon2:889673190392078356>**, **Consort <:consicon2:890336628269281350>** or **Detective <:deticon2:889673135438319637>**." #Det results
                player.defense = Defense.Default #defense
                player.distraction = False #consort
        elif (role == "framer"):
            embed = discord.Embed(title="**Your role is Framer**", colour=discord.Colour(0xd0021b), description="A skilled deceiver who sets investigations astray")

            embed.set_image(url="https://cdn.discordapp.com/attachments/765738640554065962/886032651465654312/unknown.png")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/874056995165044836.png?v=1")
            embed.set_footer(text="Mafia Deception 🎭", icon_url=author.avatar_url)

            embed.add_field(name="**Atk ⚔️:**", value="None", inline=True)
            embed.add_field(name="**Res 🛡️:**", value="None", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Mafia", inline=False)
            embed.add_field(name="**Action :man_running::**", value="Frame a player each night", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="Frames last until an investigation is preformed on your target\nFramed players show as **Suspicious <:sus:873637612571746324>** to a **Cop <:copicon2:889672912905322516>**\nFramed players show as **Framer <:frameicon2:890365634913902602>**, **Jester <:jesticon2:889968373612560394>** or **Mayor <:mayoricon2:897570023143518288>** to a **Detective <:deticon2:889673135438319637>**", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Kill all those who may rival the **Mafia <:maficon2:890328238029697044>**.", inline=False)	
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon2:889672912905322516>:** Your target is **Suspicious <:sus:873637612571746324>**\n**Detective <:deticon2:889673135438319637>:** Your target may not be what they seem at first glance. They must be a **Framer <:frameicon2:890365634913902602>**, **Jester <:jesticon2:889968373612560394>** or **Mayor <:mayoricon2:897570023143518288>**", inline=False)
            if (player != None):
                player.faction = Faction.Mafia #The player's faction (Town, Mafia, Neutral)
                player.appearssus = True #If the player appears sus
                player.detresult = "Your target might not be what they seem at first glance.>EFramer <:frameicon2:890365634913902602>>EJester <:jesticon2:889968373612560394>** or **Mayor <:mayoricon2:897570023143518288>**." #Det results
                player.defense = Defense.Default #defense
                player.distraction = False #consort
        elif (role == "jester"):
            embed = discord.Embed(title="**Your role is Jester**", colour=discord.Colour(0xffc3e7), description="A crazed lunatic who wants to be publicly executed")

            embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/892532613682700338/unknown.png?width=460&height=459")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889968373612560394.png?size=80")
            embed.set_footer(text="Neutral Evil 🪓", icon_url=author.avatar_url)

            embed.add_field(name="**Atk ⚔️:**", value="Piercing", inline=True)
            embed.add_field(name="**Res 🛡️:**", value="None", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Neutral", inline=False)
            embed.add_field(name="**Action :man_running::**", value="None", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="Upon being lynched, you will **distract** all of your guilty and abstaining voters the following night and **passively** attack one of them.", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Get yourself **lynched :axe:**.", inline=False)	
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon2:889672912905322516>:** Your target seems **Innocent <:inno:873636640227205160>**\n**Detective <:deticon2:889673135438319637>:** Your target may not be what they seem at first glance. They must be a **Framer <:frameicon2:890365634913902602>**, **Jester <:jesticon2:889968373612560394>** or **Mayor <:mayoricon2:897570023143518288>**\n**Consigliere <:consigicon2:896154845130666084>:** Your target is a crazed lunatic waiting to be hung. They must be a **Jester <:jesticon2:889968373612560394>**", inline=False)
            if (player != None):
                player.faction = Faction.Neutral #The player's faction (Town, Mafia, Neutral)
                player.appearssus = False #If the player appears sus
                player.detresult = "Your target might not be what they seem at first glance. They must be a **Framer <:frameicon2:890365634913902602>**, **Jester <:jesticon2:889968373612560394>** or **Mayor <:mayoricon2:897570023143518288>**." #Det results
                player.defense = Defense.Default #defense
                player.distraction = False #consort
        elif (role == "lookout"):
            embed = discord.Embed(title="**Your role is Lookout**", colour=discord.Colour(0x7ed321), description="A skilled observer who keeps an eye on the evils")

            embed.set_image(url="https://images-ext-2.discordapp.net/external/ZSuddOq5kHT2oP-S459OAJA__Son3GH88-mClJokmnc/https/media.discordapp.net/attachments/765738640554065962/873244464196493332/unknown.png?width=401&height=468")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889673190392078356.png?size=80")
            embed.set_footer(text="Town Investigative 🔎", icon_url=author.avatar_url)

            embed.add_field(name="**Atk ⚔️:**", value="None", inline=True)
            embed.add_field(name="**Res 🛡️:**", value="None", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Town", inline=False)
            embed.add_field(name="**Action :man_running::**", value="Watch over a player each night", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="You will learn who visits your target", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Eliminate all the criminals who may try to harm the **Town** <:townicon2:896431548717473812>", inline=False)
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon2:889672912905322516>:** Your target seems **Innocent <:inno:873636640227205160>**\n**Detective <:deticon2:889673135438319637>:** Your target works with sensitive information. They must be a **Detective <:deticon2:889673135438319637>**, **Consigliere <:consigicon:871527176527315025>** or **Lookout <:loicon2:889673190392078356>**\n**Consigliere <:consigicon2:896154845130666084>:** Your target watches other people's houses at night. They must be a **Lookout <:loicon2:889673190392078356>**", inline=False)
            if (player != None):
                player.faction = Faction.Town #The player's faction (Town, Mafia, Neutral)
                player.appearssus = False #If the player appears sus
                player.defense = Defense.Default #defense
                player.distraction = False #consort
        elif (role == "consigliere"):
            embed = discord.Embed(title="**Your role is Consigliere**", colour=discord.Colour(0xd0021b), description="A corrupted detective who gathers information for the mafia")

            embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/897240498329239582/image0.png?width=570&height=676")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896154845130666084.png?size=80")
            embed.set_footer(text="Mafia Support 🧲", icon_url=author.avatar_url)

            embed.add_field(name="**Atk ⚔️:**", value="None", inline=True)
            embed.add_field(name="**Def 🛡️:**", value="None", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Mafia", inline=False)
            embed.add_field(name="**Action :man_running::**", value="Investigate a player each night", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="You will learn your target's exact role", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Kill all those who may rival the **Mafia :rose:**.", inline=False)
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon2:889672912905322516>:** Your target is **Suspicious <:sus:873637612571746324>**\n**Detective <:deticon2:889673135438319637>:** Your target works with sensitive information. They must be a **Detective <:deticon2:889673135438319637>**, **Consigliere <:consigicon:871527176527315025>** or **Lookout <:loicon2:889673190392078356>**", inline=False)
            if (player != None):
                player.faction = Faction.Mafia #The player's faction (Town, Mafia, Neutral)
                player.appearssus = True #If the player appears sus
                player.detresult = "Your target seeks revenge. They must be a **Cop <:copicon2:889672912905322516>**, **Headhunter <:hhicon2:891429754643808276>**, **Mafioso <:maficon2:891739940055052328>** or **Enforcer <:enficon2:890339050865696798>**." #Det results
                player.defense = Defense.Default #defense 
                player.distraction = False #consort
        elif (role == "headhunter"):
            embed = discord.Embed(title="**Your role is Headhunter**", colour=discord.Colour(0x334f64), description="An obsessed executioner who wants a certain someone killed in front of the town.")

            embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/874089000250531860/unknown.png?width=574&height=701")
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/891416747582840842/hh_icon.png")
            embed.set_footer(text="Neutral Evil 🪓", icon_url=author.avatar_url)

            embed.add_field(name="**Atk ⚔️:**", value="None", inline=True)
            embed.add_field(name="**Res 🛡️:**", value="Basic", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Neutral", inline=False)
            embed.add_field(name="**Action :man_running::**", value="You are assigned a **Town** target at the start of the game", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="If your target is killed at night, you will be converted into a **Jester <:jesticon2:889968373612560394>**", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Get your target **lynched 🪓**.", inline=False)
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon2:889672912905322516>:** Your target seems **Innocent <:inno:873636640227205160>**\n**Detective <:deticon2:889673135438319637>:** Your target seeks revenge. They must be a **Cop <:copicon2:889672912905322516>**, **Headhunter <:hhicon2:891429754643808276>**, **Mafioso <:maficon2:891739940055052328>** or **Enforcer <:enficon2:890339050865696798>**\n**Consigliere <:consigicon2:896154845130666084>:** Your target wants someone hung at all costs. They must be a **Headhunter <:hhicon2:891429754643808276>**", inline=False)
            if (player != None):
                player.faction = Faction.Neutral #The player's faction (Town, Mafia, Neutral)
                player.appearssus = False #If the player appears sus
                player.detresult = "Your target seeks revenge. They must be a **Cop <:copicon2:889672912905322516>**, **Headhunter <:hhicon2:891429754643808276>**, **Mafioso <:maficon2:891739940055052328>** or **Enforcer <:enficon2:890339050865696798>**." #Det results
                player.defense = Defense.Basic #defense 
                player.distraction = False #consort
        elif (role == "tracker"):
            embed = discord.Embed(title="**Your role is Tracker**", colour=discord.Colour(0x7ed321), description="A skilled pathfinder who scouts the night.")

            embed.set_image(url="https://images-ext-2.discordapp.net/external/vxOShXchGrPMHJEcrLhW914asNZollLv-GvV70esn8Y/%3Fwidth%3D562%26height%3D634/https/media.discordapp.net/attachments/765738640554065962/872225776211202068/unknown.png")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/871525831422398497/890339048097456148/EnfIcon.png")
            embed.set_footer(text="Town Investigative 🔎", icon_url=author.avatar_url)

            embed.add_field(name="**Atk ⚔️:**", value="None", inline=True)
            embed.add_field(name="**Res 🛡️:**", value="None", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Town", inline=False)
            embed.add_field(name="**Action :man_running::**", value="Track a player each night", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="You will know who your target visits", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Eliminate all the criminals who may try to harm the **Town** <:townicon2:896431548717473812>", inline=False)
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon2:889672912905322516>:** Your target seems **Innocent <:inno:873636640227205160>**\n**Detective <:deticon2:889673135438319637>:** Your target works with sensitive information. They must be a Detective <:deticon2:889673135438319637>, Consigliere <:consigicon:871527176527315025>, Tracker :trackicon2: or Lookout <:loicon2:889673190392078356>**\n**Consigliere <:consigicon2:896154845130666084>:** Your target keeps track of others. They must be a **Tracker :trackicon2:**", inline=False)
        else:
            embed = None
        
        if (embed == None):
            return None
        else:
            return embed
    except:
        embed = discord.Embed("Looks like something went wrong with the embeds...", description="blame cet not me /shrug")
        embed.set_footer(text=f"For debugging: the role was {roled}")
        return embed

async def check(e:discord.User, guild):
    for value in var[guild]["playerdict"].values():
        if (value.id == e.id):
            if (value.framed == True):
                value.checked = True
                return True

            if (value.role == "Psychopath"):
                if (value.cautious == True):
                    return False
                else:
                    return None

            return value.appearssus

async def detcheck(idd, guild):
    thing = Player.get_player(idd, var[guild]["playerdict"])
    if (thing.framed == True):
        thing.checked = True
        return True
    else:
        return False

async def reveal(ctx, guild):
    if (Player.get_player((ctx.id), var[guild]["playerdict"]).isrevealed == False):
        Player.get_player((ctx.id), var[guild]["playerdict"]).isrevealed = True
        Player.get_player((ctx.id), var[guild]["playerdict"]).wasrevealed = True
    else:
        return

async def nighttargets(ctx):

    # Manipulative Roles
    for i in var[ctx]["targets"].keys():
        if (Player.get_player(i, var[ctx]["playerdict"]).role.lower() == "consort"):
            if (Player.get_player(i, var[ctx]["playerdict"]).dead == True):
                if (Player.get_player(i, var[ctx]["playerdict"]).diedln == False):
                    continue
            await results(bot.get_user(i), var[ctx]["targets"][i], ctx)
    for i in var[ctx]["targets"].keys():
        if (Player.get_player(i, var[ctx]["playerdict"]).role.lower() == "framer"):
            if (Player.get_player(i, var[ctx]["playerdict"]).dead == True):
                if (Player.get_player(i, var[ctx]["playerdict"]).diedln == False):
                    continue                    
            await results(bot.get_user(i), var[ctx]["targets"][i], ctx)

    # Healing Roles
    for i in var[ctx]["targets"].keys():
        if (Player.get_player(i, var[ctx]["playerdict"]).role.lower() == "doctor"):
            if (Player.get_player(i, var[ctx]["playerdict"]).dead == True):
                if (Player.get_player(i, var[ctx]["playerdict"]).diedln == False):
                    continue                    
            await results(bot.get_user(i), var[ctx]["targets"][i], ctx)

    # Investigative roles
    for i in var[ctx]["targets"].keys():
        if (Player.get_player(i, var[ctx]["playerdict"]).role.lower() == "tracker"):
            if (Player.get_player(i, var[ctx]["playerdict"]).dead == True):
                if (Player.get_player(i, var[ctx]["playerdict"]).diedln == False):
                    continue  
            await results(bot.get_user(i), var[ctx]["targets"][i], ctx)
    for i in var[ctx]["targets"].keys():
        if (Player.get_player(i, var[ctx]["playerdict"]).role.lower() == "cop"):
            if (Player.get_player(i, var[ctx]["playerdict"]).dead == True):
                if (Player.get_player(i, var[ctx]["playerdict"]).diedln == False):
                    continue                    
            await results(bot.get_user(i), var[ctx]["targets"][i], ctx)
    for i in var[ctx]["targets"].keys():
        if (Player.get_player(i, var[ctx]["playerdict"]).role.lower() == "detective"):
            if (Player.get_player(i, var[ctx]["playerdict"]).dead == True):
                if (Player.get_player(i, var[ctx]["playerdict"]).diedln == False):
                    continue                    
            await results(bot.get_user(i), var[ctx]["targets"][i], ctx)
    for i in var[ctx]["targets"].keys():
        if (Player.get_player(i, var[ctx]["playerdict"]).role.lower() == "consigliere"):
            if (Player.get_player(i, var[ctx]["playerdict"]).dead == True):
                if (Player.get_player(i, var[ctx]["playerdict"]).diedln == False):
                    continue                    
            await results(bot.get_user(i), var[ctx]["targets"][i], ctx)
    for i in var[ctx]["targets"].keys():
        if (Player.get_player(i, var[ctx]["playerdict"]).role.lower() == "lookout"):
            if (Player.get_player(i, var[ctx]["playerdict"]).dead == True):
                if (Player.get_player(i, var[ctx]["playerdict"]).diedln == False):
                    continue
            await results(bot.get_user(i), var[ctx]["targets"][i], ctx)

    # Killing Roles
    for i in var[ctx]["targets"].keys():
        if (Player.get_player(i, var[ctx]["playerdict"]).role.lower() == "mafioso"):
            if (Player.get_player(i, var[ctx]["playerdict"]).dead == True):
                if (Player.get_player(i, var[ctx]["playerdict"]).diedln == False):
                    continue 
            await results(bot.get_user(i), var[ctx]["targets"][i], ctx)
    for i in var[ctx]["targets"].keys():
        if (Player.get_player(i, var[ctx]["playerdict"]).role.lower() == "enforcer"):
            if (Player.get_player(i, var[ctx]["playerdict"]).dead == True):
                if (Player.get_player(i, var[ctx]["playerdict"]).diedln == False):
                    continue
            await results(bot.get_user(i), var[ctx]["targets"][i], ctx)
    for i in var[ctx]["targets"].keys():
        if (Player.get_player(i, var[ctx]["playerdict"]).role.lower() == "psychopath"):
            if (Player.get_player(i, var[ctx]["playerdict"]).dead == True):
                if (Player.get_player(i, var[ctx]["playerdict"]).diedln == False):
                    continue 
            await results(bot.get_user(i), var[ctx]["targets"][i], ctx)

    # Other Roles
    for i in var[ctx]["targets"].keys():
        if (Player.get_player(i, var[ctx]["playerdict"]).role.lower() == "mayor"):
            if (Player.get_player(i, var[ctx]["playerdict"]).dead == True):
                if (Player.get_player(i, var[ctx]["playerdict"]).diedln == False):
                    continue
            await results(bot.get_user(i), var[ctx]["targets"][i], ctx)
    for i in var[ctx]["targets"].keys():
        if (Player.get_player(i, var[ctx]["playerdict"]).role.lower() == "jester"):
            await results(bot.get_user(i), var[ctx]["targets"][i], ctx)

    await asyncio.sleep(4)
    asyncio.create_task(day(var[ctx]["channel"]))

async def results(ctx, targ, g):
    """Sends the player in `ctx` (discord.User) a result after using their action on `targ`'s id."""
    role = ""
    var[g]["resul"] += 1
    if (var[g]["resul"] > len(var[g]["players"])):
        return



    for value in var[g]["playerdict"].values():
        if (value.id == ctx.id):
            role = value.role.lower()

    if (targ == 0):
        return
    
    jestered = False

    for i in var[g]["playerdict"].values():
        if (i.jesterwin == True):
            jestered = True

    oo = jestered
    o = ctx.id in var[g]["guiltyers"]

    if (o and oo):
        role = Player.get_player(ctx.id, var[g]["playerdict"]).role.lower()
        if (role != "jester"):
            var[g]["targets"][ctx.id] = 0
            embed = discord.Embed(title="**You feel too guilty to do anything tonight.**", colour=discord.Colour(0xffc3e7))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/F8o5Mi5dYJDvkfQ3B98JCbUYmdmdnupZQyNa2wXpEBk/https/media.discordapp.net/attachments/765738640554065962/872147798336893019/imageedit_4_4906520050.png")
            embed.set_footer(text="Don't lynch the Jester.", icon_url=ctx.avatar_url)     

            await ctx.send(embed=embed)
            return

    if (Player.get_player(ctx.id, var[g]["playerdict"]).distraction == True):
        var[g]["targets"][ctx.id] = 0
        embed = discord.Embed(title="**Somebody Distracted :revolving_hearts: you last night, so you did not perform your night ability.**", colour=discord.Colour(0xb6d4ff))

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/873954973556293632.png?v=1")
        embed.set_footer(text="Gotta stay focused.", icon_url=ctx.avatar_url)
        await ctx.send(embed=embed)
        return

    if (role == "mayor"):
        if (targ == False):
            return
        elif (targ == True):
            await reveal(ctx, g)
            return

    if (role == "cop"):
        if (await check(bot.get_user(targ), g) == True):
            embed = discord.Embed(title="**Your target is Suspicious!**", colour=discord.Colour(0xd0021b), description=f"**{bot.get_user(targ).name} is either... \n --A member of the Mafia <:maficon2:890328238029697044>. \n --Or an Innocent who has been Framed <:frameicon2:890365634913902602>.**")

            embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/871791911072067594/suspicious__-removebg-preview.png")
            embed.set_author(name="Interrogation Results")
            embed.set_footer(text="Try convincing the others with your info.", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)
        elif (await check(bot.get_user(targ), g) == False):
            embed = discord.Embed(title="**Your target seems Innocent.**", colour=discord.Colour(0x7ed321), description=f"**{bot.get_user(targ).name} is either... \n --An Innocent Townie <:townicon2:896431548717473812>. \n --Or an evil Neutral 🪓.**")

            embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/871791900003282964/seems_innocent_-removebg-preview.png")
            embed.set_author(name="Interrogation Results")
            embed.set_footer(text="Try convincing the others with your info.", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="**Your target is acting Psychotic!**", colour=discord.Colour(0x4a90e2), description=f"**{bot.get_user(targ).name} must be... \n --A Psychopath :knife:.**")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/877584821180825691.png?size=96")
            embed.set_author(name="Interrogation Results")
            embed.set_footer(text="Try convincing the others with your info.", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)

    elif (role == "mafioso"):
        if (await attack(ctx.id, bot.get_user(targ), g) == True):
            member:discord.Member = var[g]["guildg"].get_member(targ)
            await member.add_roles(discord.utils.get(var[g]["guildg"].roles, name="[Anarchic] Dead"))
            await member.remove_roles(discord.utils.get(var[g]["guildg"].roles, name="[Anarchic] Player"))
            Player.get_player(targ, var[g]["playerdict"]).diedln = True
            Player.get_player(targ, var[g]["playerdict"]).death.append(DeathReason.Mafia)
            user = bot.get_user(targ)
            embed = discord.Embed(title="**You were attacked by a member of the Mafia <:maficon2:890328238029697044>.**", colour=discord.Colour(0xd0021b), description="**You have died <:rip:878415658885480468>**.")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/890328238029697044.png?size=80")
            embed.set_footer(text="Rest in peace.", icon_url=user.avatar_url)
            await user.send(embed=embed)
        else:
            embed = discord.Embed(title="**Your target was too strong to be killed.**", colour=discord.Colour(0xfff68a))


            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/878379179106787359.png?v=1")
            embed.set_footer(text="Strange...", icon_url=ctx.avatar_url)
            
            await ctx.send(embed=embed)
    elif (role == "psychopath"):
        if (await attack(ctx.id, bot.get_user(targ), g) == True):
            member:discord.Member = var[g]["guildg"].get_member(targ)
            await member.add_roles(discord.utils.get(var[g]["guildg"].roles, name="[Anarchic] Dead"))
            await member.remove_roles(discord.utils.get(var[g]["guildg"].roles, name="[Anarchic] Player"))
            Player.get_player(targ, var[g]["playerdict"]).diedln = True
            Player.get_player(targ, var[g]["playerdict"]).death.append(DeathReason.Psychopath)
            user = bot.get_user(targ)
            embed = discord.Embed(title="**You were attacked by a member of the Psychopath <:maficon2:890328238029697044>.**", colour=discord.Colour(0xd0021b), description="**You have died <:rip:878415658885480468>**.")

            embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/871849580533268480/unknown.png?width=744&height=634")
            embed.set_footer(text="Rest in peace.", icon_url=user.avatar_url)
            await user.send(embed=embed)
        else:
            embed = discord.Embed(title="**Your target was too strong to be killed.**", colour=discord.Colour(0xfff68a))


            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/878379179106787359.png?v=1")
            embed.set_footer(text="Strange...", icon_url=ctx.avatar_url)
            
            await ctx.send(embed=embed)
    elif (role == "enforcer"):
        if (await attack(ctx.id, bot.get_user(targ), g) == True):
            member:discord.Member = var[g]["guildg"].get_member(targ)
            us:discord.Member = var[g]["guildg"].get_member(ctx.id)
            await member.add_roles(discord.utils.get(var[g]["guildg"].roles, name="[Anarchic] Dead"))
            await member.remove_roles(discord.utils.get(var[g]["guildg"].roles, name="[Anarchic] Player"))
            Player.get_player(targ, var[g]["playerdict"]).diedln = True
            Player.get_player(targ, var[g]["playerdict"]).death.append(DeathReason.Enforcer)
            user = bot.get_user(targ)
            embed = discord.Embed(title="**You were shot by an Enforcer <:enficon2:890339050865696798>.**", colour=discord.Colour(0x7ed321), description="**You have died <:rip:878415658885480468>**.")

            embed.set_thumbnail(url="https://media.discordapp.net/attachments/867924656219377684/882797114634154014/unknown.png")
            embed.set_footer(text="Rest in peace.", icon_url=user.avatar_url)
            await user.send(embed=embed)
            if (Player.get_player(targ, var[g]["playerdict"]).faction == Faction.Town):
                embed = discord.Embed(title="**You could not get over the guilt and shot yourself <:enficon2:890339050865696798>.**", colour=discord.Colour(0x7ed321), description="**You have died <:rip:878415658885480468>**.")

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/879163761057992744/unknown.png?width=598&height=701")
                embed.set_footer(text="Rest in peace.", icon_url=us.avatar_url)
                
                await us.send(embed=embed)

                await us.add_roles(discord.utils.get(var[g]["guildg"].roles, name="[Anarchic] Dead"))
                await us.remove_roles(discord.utils.get(var[g]["guildg"].roles, name="[Anarchic] Player"))
                Player.get_player(us.id, var[g]["playerdict"]).diedln = True
                Player.get_player(us.id, var[g]["playerdict"]).dead = True
                Player.get_player(us.id, var[g]["playerdict"]).death.append(DeathReason.Guilt)
        else:
            embed = discord.Embed(title="**Your target was too strong to be killed.**", colour=discord.Colour(0xfff68a))

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/878379179106787359.png?v=1")
            embed.set_footer(text="Strange...", icon_url=ctx.avatar_url)
            
            await ctx.send(embed=embed)
    elif (role == "doctor"):
        if (await protecc(bot.get_user(targ), g)):
            if (targ == ctx.id):
                Player.get_player(ctx.id, var[g]["playerdict"]).docHealedHimself = True
        else:
            pass
    elif (role == "lookout"):
        mister = []
        for key, value in var[g]["targets"].items():
            if (key == ctx.id or value == 0):
                continue

            if (value in mister):
                continue

            if (value == targ):
                user = bot.get_user(int(key))
                embed = discord.Embed(title=f"**{user.name} visited your target last night!**", colour=discord.Colour(0x7ed321))

                embed.set_thumbnail(url=user.avatar_url)
                embed.set_footer(text="What were they doing there?", icon_url=ctx.avatar_url)
                await ctx.send(embed=embed)
                mister.append(int(key))
    elif (role == "tracker"):
        if (var[g]["targets"][int(targ)] != 0 and Player.get_player(int(targ), var[g]["playerdict"]).distraction == False):
            user = bot.get_user(int(var[g]["targets"][int(targ)]))
            embed = discord.Embed(title=f"**Your target visited {user.name} last night!**", colour=discord.Colour(0x7ed321))

            embed.set_thumbnail(url=user.avatar_url)
            embed.set_footer(text="What were they doing there?", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)
    elif (role == "consort"):
        if (Player.get_player(targ.id, var[ctx]["playerdict"]).role == "Psychopath" and Player.get_player(targ.id, var[ctx]["playerdict"]).cautious == False):
            k = Player.get_player(ctx.id, var[ctx]["playerdict"])
            k.dead = True
            k.deathreason.append(DeathReason.Psychopath)
            k.will = []
            k.will.append("Their last will was too bloody to be read.")

            embed = discord.Embed(title="**You were stabbed by the **Psychopath :knife:** you distracted.", colour=discord.Colour(0x4a90e2), description="**You have died :rip:.**")

            embed.set_thumbnail(url="https://discord.com/assets/9f89170e2913a534d3dc182297c44c87.svg")
            embed.set_footer(text="Rest in peace.", icon_url="https://cdn.discordapp.com/avatars/667189788620619826/f4c9e87dde54e0e2d14db69b9d60deb9.png?size=128")
            await ctx.send(embed=embed)

            return
        Player.get_player(targ, var[g]["playerdict"]).distraction = True
    elif (role == "jester"):
            member:discord.Member = var[g]["guildg"].get_member(targ)
            await member.add_roles(discord.utils.get(var[g]["guildg"].roles, name="[Anarchic] Dead"))
            await member.remove_roles(discord.utils.get(var[g]["guildg"].roles, name="[Anarchic] Player"))
            Player.get_player(targ, var[g]["playerdict"]).diedln = True
            Player.get_player(targ, var[g]["playerdict"]).dead = True
            Player.get_player(targ, var[g]["playerdict"]).death.append(DeathReason.JesterGuilt)
            
            embed = discord.Embed(title="**You were haunted by the Jester <:jesticon2:889968373612560394>.**", colour=discord.Colour(0xffc3e7), description="**You have died <:rip:872284978354978867>.**")

            embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/895419320140693584/export.png?width=396&height=408")
            embed.set_footer(text="Rest in peace.", icon_url=ctx.avatar_url)
            us = bot.get_user(targ)
            await us.send(embed=embed)
    elif (role == "framer"):
        Player.get_player(targ, var[g]["playerdict"]).framed = True
        Player.get_player(targ, var[g]["playerdict"]).checked = False
    elif (role == "detective"):
        if (await detcheck(targ, g) == True):
            embed = discord.Embed(title="**Your target might not be what they seem at first glance.**", colour=discord.Colour(0x7ed321), description="**They must be either...\n-A Framer <:frameicon2:890365634913902602>\n-A Jester <:jesticon2:889968373612560394>\n-The Mayor <:mayoricon2:897570023143518288>\n-Or they're Framed <:frameicon2:890365634913902602>**")

            embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/896553626770755584/export.png")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Try convincing the others with your info.", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)
        else:
            play = Player.get_player(targ, var[g]["playerdict"])
            embed = discord.Embed()

            if (play.role in ["Framer", "Jester", "Mayor"]):
                embed = discord.Embed(title="**Your target might not be what they seem at first glance.**", colour=discord.Colour(0x7ed321), description="**They must be either...\n-A Framer <:frameicon2:890365634913902602>\n-A Jester <:jesticon2:889968373612560394>\n-The Mayor <:mayoricon2:897570023143518288>\n-Or they're Framed <:frameicon2:890365634913902602>**")

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/896553626770755584/export.png")
                embed.set_author(name="Investigation Results")
                embed.set_footer(text="Try convincing the others with your info.", icon_url=ctx.avatar_url)
            elif (play.role in ["Cop", "Headhunter", "Mafioso", "Enforcer"]):
                embed = discord.Embed(title="**Your target seeks revenge.**", colour=discord.Colour(0x7ed321), description="**They must be either...\n-A Cop <:copicon2:889672912905322516>\n-A Headhunter <:hhicon2:891429754643808276>\n-A Mafioso <:maficon2:891739940055052328>\n-Or an Enforcer <:enficon2:890339050865696798>**")

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/897585565795491900/hides_in_the_shadows.png?width=676&height=676")
                embed.set_author(name="Investigation Results")
                embed.set_footer(text="Try convincing the others with your info.", icon_url=ctx.avatar_url)
            elif(play.role in ["Doctor", "Consort", "Psychic"]):
                embed = discord.Embed(title="**Your target hides in the shadows.**", colour=discord.Colour(0x7ed321), description="**They must be either...\n-A Doctor <:docicon2:890333203959787580>\n-A Psychic <:psyicon2:896159311078780938>\n-Or a Consort <:consicon2:890336628269281350>**")

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/896551764466225182/export.png")
                embed.set_author(name="Investigation Results")
                embed.set_footer(text="Try convincing the others with your info.", icon_url=ctx.avatar_url)
            elif (play.role in ["Detective", "Consigliere", "Lookout"]):
                embed = discord.Embed(title="**Your target works with sensitive information.**", colour=discord.Colour(0x7ed321), description="**They must be either...\n-A Detective <:deticon2:889673135438319637>\n-A Consigliere <:consigicon2:896154845130666084>\n-Or a Lookout <:loicon2:889673190392078356>**")

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/897585591397539860/works_with_sensitive_info.png?width=676&height=676")
                embed.set_author(name="Investigation Results")
                embed.set_footer(text="Try convincing the others with your info.", icon_url=ctx.avatar_url)
            else:
                embed = discord.Embed(title="**Your target is mysterious.**", colour=discord.Colour(0x7ed321), description="**They must be either...\n-A ???\nA ???\nOr a ???")

                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/878437549721419787/884534469225242634/unknown-removebg-preview.png")
                embed.set_author(name="Investigation Results")
                embed.set_footer(text="Try convincing the others with this weird info.", icon_url=ctx.avatar_url)

            await ctx.send(embed=embed)        
    elif (role == "consigliere"):
        play = Player.get_player(targ, var[g]["playerdict"])
        embed = discord.Embed()

        if (play.role == "Cop"):
            embed = discord.Embed(title="**Your target is the law enforcer of the town**", colour=discord.Colour(0xd0021b), description="**They must be a Cop <:copicon2:889672912905322516>**")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889672912905322516.png?size=96")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Interesting", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)
        elif (play.role == "Doctor"):
            embed = discord.Embed(title="**Your target is a profound surgeon**", colour=discord.Colour(0xd0021b), description="**They must be a Doctor <:docicon2:890333203959787580>**")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/890333203959787580.png?size=44")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Interesting", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)
        elif(play.role == "Lookout"):
            embed = discord.Embed(title="**Your target watches other people's houses at night**", colour=discord.Colour(0xd0021b), description="**They must be a Lookout <:loicon2:889673190392078356>**")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889673190392078356.png?size=44")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Interesting", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)
        elif (play.role == "Mayor"):
            embed = discord.Embed(title="**Your target is the leader of the town.**", colour=discord.Colour(0xd0021b), description="**They must be the Mayor <:mayoricon2:891719324509831168>**")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/891719324509831168.png?size=44")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Interesting", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)
        elif (play.role == "Enforcer"):
            embed = discord.Embed(title="**Your target is willing to bend the law to enact justice.**", colour=discord.Colour(0xd0021b), description="**They must be a Enforcer <:enficon2:890339050865696798>**")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/890339050865696798.png?size=44")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Interesting", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)
        elif (play.role == "Detective"):
            embed = discord.Embed(title="**Your target secretly gathers infomation.**", colour=discord.Colour(0xd0021b), description="**They must be a Detective <:deticon2:889673135438319637>**")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889673135438319637.png?size=44")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Interesting", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)
        elif (play.role == "Psychic"):
            embed = discord.Embed(title="**Your target can hear the voices of the dead.**", colour=discord.Colour(0xd0021b), description="**They must be a Psychic <:psyicon2:896159311078780938>**")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896159311078780938.png?size=80")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Interesting", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)
        elif (play.role == "Headhunter"):
            embed = discord.Embed(title="**Your target wants someone hung at all costs.**", colour=discord.Colour(0xd0021b), description="**They must be a Headhunter <:hhicon2:891429754643808276>**")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/891429754643808276.png?size=96")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Interesting", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)
        elif (play.role == "Jester"):
            embed = discord.Embed(title="**Your target is a crazed lunatic waiting to be hung.**", colour=discord.Colour(0xd0021b), description="**They must be a Jester <:jesticon2:889968373612560394>**")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889968373612560394.png?size=44")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Interesting", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="**Your target is mysterious.**", colour=discord.Colour(0x7ed321), description="**They must be either...\n-A ???\nA ???\nOr a ???")

            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/878437549721419787/884534469225242634/unknown-removebg-preview.png")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Try convincing the others with this weird info.", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)
    else:
        await ctx.send("No results, sorry man")

    var[g]["resul"] -= 1

async def target(ctx:discord.User, r):
    var[r]["isresults"] = False
    var[r]["targets"] = {}

    if (Player.get_player(ctx.id, var[r]["playerdict"]).dead):
        if (Player.get_player(ctx.id, var[r]["playerdict"]).jesterwin == False):
            return


    role = ""

    for value in var[r]["playerdict"].values():
        if (value.id == ctx.id):
            role = value.role.lower()


    if (role == "cop"):
        embed = discord.Embed(title="Who do you interrogate tonight?", description="", color=0x7ed321)
        
        for key, value in var[r]["playeremoji"].items():
            if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                
                continue
            else:
                user:discord.User = bot.get_user(value)
                embed.add_field(name=f"{key} - {user.name}#{user.discriminator} :mag_right:", value="** **", inline=False)

        embed.add_field(name="Time :hourglass::", value="You have 30 seconds to choose.")

        embed.description = "**Your targets are...**"
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/871524614914834432/IconCop-removebg-preview.png")
        embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/871511037743071232/unknown.png?width=677&height=634")
        embed.set_footer(text="React with who you want to interrogate.", icon_url=ctx.avatar_url)
        b = await ctx.send(embed=embed)



        for key, value in var[r]["playeremoji"].items():
                    if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                        continue
                    else:
                       await b.add_reaction(key)


        def check(reaction:Reaction, user):
            return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]

        try:
            reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
            target = var[r]["playeremoji"][reaction.emoji]
            var[r]["targets"][ctx.id] = target
            targetuser = bot.get_user(target)
            embed = discord.Embed(title=f"**You have decided to interrogate {targetuser.name} tonight.**", color=0x7ed321)
            embed.set_thumbnail(url=targetuser.avatar_url)
            embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar_url)
            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
            await ctx.send(embed=embed)
        except asyncio.TimeoutError:
            var[r]["targets"][ctx.id] = 0
            embed = discord.Embed(title="**You did not perform your night ability.**", colour=discord.Colour(0xd3d3d3))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
            embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)
            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
        except Exception as e:
            print(e)
        
        af = 0
        max = 0
        for value in var[r]["playerdict"].values():
            if (value.id != 0 and value.dead == False):
                max += 1
            else:
                if (value.dead == True and value.role.lower() == "jester" and value.jesterwin == True):
                    max += 1

        for value in var[r]["playerdict"].values():
            if (value.ready == True and value.dead == False):
                af += 1
            else:
                if (value.dead == True and value.dead == True and value.role.lower() == "jester" and value.jesterwin == True):
                    af += 1

        if (af >= max):
            var[r]["isresults"] = True
            await nighttargets(r)
            return
        else:
            return
    elif (role == "tracker"):
        embed = discord.Embed(title="Who do you track tonight?", description="", color=0x7ed321)
        
        for key, value in var[r]["playeremoji"].items():
            if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                
                continue
            else:
                user:discord.User = bot.get_user(value)
                embed.add_field(name=f"{key} - {user.name}#{user.discriminator} :mag_right:", value="** **", inline=False)

        embed.add_field(name="Time :hourglass::", value="You have 30 seconds to choose.")

        embed.description = "**Your targets are...**"
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/871524614914834432/IconCop-removebg-preview.png")
        embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/871511037743071232/unknown.png?width=677&height=634")
        embed.set_footer(text="React with who you want to track.", icon_url=ctx.avatar_url)
        b = await ctx.send(embed=embed)



        for key, value in var[r]["playeremoji"].items():
                    if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                        continue
                    else:
                       await b.add_reaction(key)


        def check(reaction:Reaction, user):
            return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]

        try:
            reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
            target = var[r]["playeremoji"][reaction.emoji]
            var[r]["targets"][ctx.id] = target
            targetuser = bot.get_user(target)
            embed = discord.Embed(title=f"**You have decided to track {targetuser.name} tonight.**", color=0x7ed321)
            embed.set_thumbnail(url=targetuser.avatar_url)
            embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar_url)
            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
            await ctx.send(embed=embed)
        except asyncio.TimeoutError:
            var[r]["targets"][ctx.id] = 0
            embed = discord.Embed(title="**You did not perform your night ability.**", colour=discord.Colour(0xd3d3d3))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
            embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)
            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
        except Exception as e:
            print(e)
        
        af = 0
        max = 0
        for value in var[r]["playerdict"].values():
            if (value.id != 0 and value.dead == False):
                max += 1
            else:
                if (value.dead == True and value.role.lower() == "jester" and value.jesterwin == True):
                    max += 1

        for value in var[r]["playerdict"].values():
            if (value.ready == True and value.dead == False):
                af += 1
            else:
                if (value.dead == True and value.dead == True and value.role.lower() == "jester" and value.jesterwin == True):
                    af += 1

        if (af >= max):
            var[r]["isresults"] = True
            await nighttargets(r)
            return
        else:
            return
    elif (role == "mafioso"):
        message = "**Your targets are...**"
        embed = discord.Embed(title="**Who would you like to attack tonight?**", colour=discord.Colour(0xd0021b), description="**Your targets are...**")

        if (random.randint(1, 384759034) == 4535):
            embed.set_image(url="https://cdn.discordapp.com/attachments/765738640554065962/899313643274010644/unknown.png")
        else:
            embed.set_image(url="https://images-ext-1.discordapp.net/external/MHSYSxBlhJcGfqEVLdj1h1AkLF-Q5MRD9VESaxZ1mz4/%3Fwidth%3D798%26height%3D634/https/media.discordapp.net/attachments/765738640554065962/871823862755622962/unknown.png")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/897585492562964531/MafIcon2.png?width=676&height=676")
        embed.set_footer(text="React with who you want to attacked.", icon_url=ctx.avatar_url)
        for key, value in var[r]["playeremoji"].items():
            if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True or Player.get_player(value, var[r]["playerdict"]).faction == Faction.Mafia):
                continue
            else:
                user:discord.User = bot.get_user(value)
                embed.add_field(name=f"{key} - {user.name}#{user.discriminator} :dagger:", value="** **", inline=False)

        b = await ctx.send(embed=embed)

        for key, value in var[r]["playeremoji"].items():
                    if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True or Player.get_player(value, var[r]["playerdict"]).faction == Faction.Mafia):
                        continue
                    else:
                       await b.add_reaction(key)

        def check(reaction:Reaction, user):
            return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]

        try:
            reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
            target = var[r]["playeremoji"][reaction.emoji]
            var[r]["targets"][ctx.id] = target
            targetuser:discord.User = bot.get_user(target)
            embed = discord.Embed(title=f"**You have decided to kill {targetuser.name} tonight.**", colour=discord.Colour(0xd0021b))

            embed.set_thumbnail(url=targetuser.avatar_url)
            embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar_url)
            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
                    
            

            await ctx.send(embed=embed)

            embed = discord.Embed(title=f"**{ctx.name} has decided to kill {targetuser.name}#{targetuser.discriminator} tonight.**", colour=discord.Colour(0xd0021b))

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/891739940055052328.png?size=80")
            await var[r]["mafcon"].send(embed=embed)
        
        except asyncio.TimeoutError:
            var[r]["targets"][ctx.id] = 0
            embed = discord.Embed(title="**You did not perform your night ability.**", colour=discord.Colour(0xd3d3d3))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
            embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)
            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True

            embed = discord.Embed(title=f"**{ctx.name} did not preform their night ability.**", colour=discord.Colour(0xd0021b))

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/891739940055052328.png?size=80")
            await var[r]["mafcon"].send(embed=embed)
        except Exception as e:
            print(e)


        af = 0
        max = 0
        for value in var[r]["playerdict"].values():
            if (value.id != 0 and value.dead == False):
                max += 1

        for value in var[r]["playerdict"].values():
            if (value.ready == True and value.dead == False):
                af += 1

        if (af >= max):
            var[r]["isresults"] = True
            await nighttargets(r)
            return
        else:
            return
    elif (role == "psychopath"):
        embed = discord.Embed(title="Would you like to go cautious tonight?", description="", color=0x4a90e2)
        embed.add_field(name="Time :hourglass::", value="You have 30 seconds to choose.")

        embed.set_thumbnail(url="https://discord.com/assets/9f89170e2913a534d3dc182297c44c87.svg")
        embed.set_image(url="https://cdn.discordapp.com/attachments/878437549721419787/882418844424081449/unknown.png")
        embed.set_footer(text="React yes or no.", icon_url=ctx.avatar_url)

        o = await ctx.send(embed=embed)
        await o.add_reaction("✅")
        await o.add_reaction("❌") 

        def check(reaction:Reaction, user):
            return user.id == ctx.id and str(reaction.emoji) in ["✅", "❌"]

        try:
            reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
            

            if (reaction.emoji == "✅"):
                Player.get_player(ctx.id, var[r]["playerdict"]).cautious = True
                embed = discord.Embed(title=f"**You have decided to cautious tonight.**", color=0x7ed321)
                embed.set_thumbnail(url=ctx.avatar_url)
                embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar_url)
                await ctx.send(embed=embed)
            else:
                Player.get_player(ctx.id, var[r]["playerdict"]).cautious = False
                embed = discord.Embed(title=f"**You have decided to not cautious tonight.**", color=0x7ed321)
                embed.set_thumbnail(url=ctx.avatar_url)
                embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar_url)
                await ctx.send(embed=embed)
            embed = discord.Embed(title="**Who would you like to psychopath tonight?**", colour=discord.Colour(0xd0021b), description="**Your targets are...**")

            embed.set_image(url="https://images-ext-1.discordapp.net/external/MHSYSxBlhJcGfqEVLdj1h1AkLF-Q5MRD9VESaxZ1mz4/%3Fwidth%3D798%26height%3D634/https/media.discordapp.net/attachments/765738640554065962/871823862755622962/unknown.png")
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/897585492562964531/MafIcon2.png?width=676&height=676")
            embed.set_footer(text="React with who you want to psychopathed.", icon_url=ctx.avatar_url)
            for key, value in var[r]["playeremoji"].items():
                if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                    continue
                else:
                    user:discord.User = bot.get_user(value)
                    embed.add_field(name=f"{key} - {user.name}#{user.discriminator} :dagger:", value="** **", inline=False)

            b = await ctx.send(embed=embed)

            for key, value in var[r]["playeremoji"].items():
                        if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                            continue
                        else:
                            await b.add_reaction(key)

            if (Player.get_player(ctx.id, var[r]["playerdict"]).cautious == True):
                    embed = discord.Embed(title=f"**DID YOU KNOW????**", description="You were cautious last night!", color=0x7ed321)
                    embed.set_thumbnail(url=ctx.avatar_url)
                    embed.set_footer(text="fuck you :)", icon_url=ctx.avatar_url)
                    await ctx.send(embed=embed)
            elif (Player.get_player(ctx.id, var[r]["playerdict"]).cautious == False):
                    embed = discord.Embed(title=f"**DID YOU KNOW????**", description="You were NOT cautious last night!", color=0x7ed321)
                    embed.set_thumbnail(url=ctx.avatar_url)
                    embed.set_footer(text="fuck you :)", icon_url=ctx.avatar_url)
                    await ctx.send(embed=embed)

            def check(reaction:Reaction, user):
                return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]

            Player.get_player(ctx.id, var[r]["playerdict"]).cautious = False

            try:
                reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
                target = var[r]["playeremoji"][reaction.emoji]
                var[r]["targets"][ctx.id] = target
                targetuser:discord.User = bot.get_user(target)
                embed = discord.Embed(title=f"**You have decided to psychopath {targetuser.name} tonight.**", colour=discord.Colour(0xd0021b))

                embed.set_thumbnail(url=targetuser.avatar_url)
                embed.set_footer(text="Please wait for other players to choose their actions.", icon_url=ctx.avatar_url)
                await ctx.send(embed=embed)
            
            except asyncio.TimeoutError:
                var[r]["targets"][ctx.id] = 0
                embed = discord.Embed(title="**You did not perform your night ability.**", colour=discord.Colour(0xd3d3d3))

                embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
                embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar_url)
                await ctx.send(embed=embed)
                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
            except Exception as e:
                print(e)
                
            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
    
        except asyncio.TimeoutError:
            var[r]["targets"][ctx.id] = 0
            embed = discord.Embed(title="**You did not perform your night ability.**", colour=discord.Colour(0xd3d3d3))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
            embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)
            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
        except Exception as e:
            print(e)




        af = 0
        max = 0

        for value in var[r]["playerdict"].values():
            if (value.id != 0 and value.dead == False):
                max += 1

        for value in var[r]["playerdict"].values():
            if (value.ready == True and value.dead == False):
                af += 1

        if (af >= max):
            var[r]["isresults"] = True
            await nighttargets(r)
            return
        else:
            return
    elif (role == "doctor"):
        message = "**Your targets are...**"
        embed = discord.Embed(title="**Who do you heal tonight?**", colour=discord.Colour(0x7ed321), description="**Y឵our targets are...**")

        embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/892916234654474290/DocTargeting.png?width=371&height=383")
        embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/z-NBaQM3t7KvWEy9hUjDQcmgdecDVw8TmTy8mCwzSwA/https/media.discordapp.net/attachments/765738640554065962/871898167845720134/doctoricon-removebg-preview.png")
        for key, value in var[r]["playeremoji"].items():
            if (Player.get_player(value, var[r]["playerdict"]).dead == True):
                continue
            else:
                if (value == ctx.id):
                    if (Player.get_player(ctx.id, var[r]["playerdict"]).docHealedHimself):
                        continue

                user:discord.User = bot.get_user(value)
                embed.add_field(name=f"{key} - {user.name}#{user.discriminator} :syringe:", value="** **", inline=False)

        embed.add_field(name="Time :hourglass::", value="You have 30 seconds to choose.")

        b = await ctx.send(embed=embed)

        for key, value in var[r]["playeremoji"].items():
            if (Player.get_player(value, var[r]["playerdict"]).dead == True):
                continue
            else:
                if (value == ctx.id):
                    if (Player.get_player(ctx.id, var[r]["playerdict"]).docHealedHimself):
                        continue

                await b.add_reaction(key)  

        def check(reaction:Reaction, user):
            return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]
        try:
            reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
            target = var[r]["playeremoji"][reaction.emoji]
            var[r]["targets"][ctx.id] = target
            targetuser = bot.get_user(target)
            embed = discord.Embed(title=f"**You have decided to heal {targetuser.name} tonight.**", colour=discord.Colour(0x7ed321))

            embed.set_thumbnail(url=targetuser.avatar_url)
            embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar_url)
            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
                    
            await ctx.send(embed=embed)
            
        except asyncio.TimeoutError:
            var[r]["targets"][ctx.id] = 0
            embed = discord.Embed(title="**You did not perform your night ability.**", colour=discord.Colour(0xd3d3d3))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
            embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)
            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
        except Exception as e:
            print(e)


        af = 0
        max = 0
        for value in var[r]["playerdict"].values():
            if (value.id != 0 and value.dead == False):
                max += 1

        for value in var[r]["playerdict"].values():
            if (value.ready == True and value.dead == False):
                af += 1

        if (af >= max):
            var[r]["isresults"] = True
            await nighttargets(r)
            return
    elif (role == "enforcer"):
        if (var[r]["gday"] == 1):
            embed = discord.Embed(title="**You are reloading your gun.**", colour=discord.Colour(0x7ed321), description="**You may not shoot anyone on the first night.**")

            embed.set_image(url="https://media.discordapp.net/attachments/879156984807559228/879161044092739685/unknown.png?width=598&height=634")
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/872955907967942664/p-trans.png")
            embed.set_footer(text="You must wait a night before shooting.", icon_url=ctx.avatar_url)

            await ctx.send(embed=embed)
            var[r]["targets"][ctx.id] = 0
            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
        else:
            message = "**Your targets are...**"
            embed = discord.Embed(title="**Who do you shoot tonight?**", colour=discord.Colour(0x7ed321), description="**Your targets are...**")

            embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/872233227140603944/unknown.png?width=560&height=634")
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/872955907967942664/p-trans.png")
            embed.set_footer(text="React with who you want to shoot.", icon_url=ctx.avatar_url)

            for key, value in var[r]["playeremoji"].items():
                if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                    continue
                else:
                    user:discord.User = bot.get_user(value)
                    embed.add_field(name=f"{key} - {user.name}#{user.discriminator} :gun:", value="** **", inline=False)

            b = await ctx.send(embed=embed)

            for key, value in var[r]["playeremoji"].items():
                        if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                            continue
                        else:
                            await b.add_reaction(key)  

            def check(reaction:Reaction, user):
                return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]
            try:
                reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
                target = var[r]["playeremoji"][reaction.emoji]
                var[r]["targets"][ctx.id] = target
                targetuser = bot.get_user(target)
                embed = discord.Embed(title=f"**You have decided to shoot {targetuser.name} tonight.**", colour=discord.Colour(0x7ed321))

                embed.set_thumbnail(url=targetuser.avatar_url)
                embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar_url)
                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
                        
                await ctx.send(embed=embed)
                
            except asyncio.TimeoutError:
                var[r]["targets"][ctx.id] = 0
                embed = discord.Embed(title="**You did not perform your night ability.**", colour=discord.Colour(0xd3d3d3))

                embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
                embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar_url)
                await ctx.send(embed=embed)
                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
            except Exception as e:
                print(e)


            af = 0
            max = 0
            for value in var[r]["playerdict"].values():
                if (value.id != 0 and value.dead == False):
                    max += 1

            for value in var[r]["playerdict"].values():
                if (value.ready == True and value.dead == False):
                    af += 1

            if (af >= max):
                var[r]["isresults"] = True
                await nighttargets(r)
                return
    elif (role == "lookout"):
        message = "**Your targets are...**"
        embed = discord.Embed(title="**Who do you watch over tonight?**", colour=discord.Colour(0x7ed321), description="**Your targets are...**")

        embed.set_image(url="https://images-ext-2.discordapp.net/external/LeVUTk0nutucMC5NAnvFMKh_fxm8MHclkGojmefTN6c/%3Fwidth%3D856%26height%3D634/https/media.discordapp.net/attachments/765738640554065962/873604432858861578/unknown.png")
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/873351736662847549.png?v=1")
        embed.set_footer(text="React with who you want to watch over.", icon_url=ctx.avatar_url)


        for key, value in var[r]["playeremoji"].items():
            if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                continue
            else:
                user:discord.User = bot.get_user(value)
                embed.add_field(name=f"{key} - {user.name}#{user.discriminator} :telescope:", value="** **", inline=False)

        b = await ctx.send(embed=embed)

        for key, value in var[r]["playeremoji"].items():
                    if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                        continue
                    else:
                        await b.add_reaction(key)  

        def check(reaction:Reaction, user):
            return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]
        try:
            reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
            target = var[r]["playeremoji"][reaction.emoji]
            var[r]["targets"][ctx.id] = target
            targetuser = bot.get_user(target)
            embed = discord.Embed(title=f"**You have decided to watch over {targetuser.name} tonight.**", colour=discord.Colour(0x7ed321))

            embed.set_thumbnail(url=targetuser.avatar_url)
            embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar_url)
            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
                    
            await ctx.send(embed=embed)
            
        except asyncio.TimeoutError:
            var[r]["targets"][ctx.id] = 0
            embed = discord.Embed(title="**You did not perform your night ability.**", colour=discord.Colour(0xd3d3d3))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
            embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)
            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
        except Exception as e:
            print(e)


        af = 0
        max = 0
        for value in var[r]["playerdict"].values():
            if (value.id != 0 and value.dead == False):
                max += 1

        for value in var[r]["playerdict"].values():
            if (value.ready == True and value.dead == False):
                af += 1

        if (af >= max):
            var[r]["isresults"] = True
            await nighttargets(r)
            return
    elif (role == "consort"):
        embed = discord.Embed(title="**Who do you distract tonight?**", colour=discord.Colour(0xd0021b), description="**Your targets are...**")

        embed.set_image(url="https://cdn.discordapp.com/attachments/878437549721419787/882739145762545714/unknown-removebg-preview.png")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/871525831422398497/890335792772313098/ConsIcon.png?width=701&height=701")
        embed.set_footer(text="React with who you want to distract.", icon_url=ctx.avatar_url)

        for key, value in var[r]["playeremoji"].items():
            if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                continue
            else:
                user:discord.User = bot.get_user(value)
                embed.add_field(name=f"{key} - {user.name}#{user.discriminator} :lipstick:", value="** **", inline=False)

        embed.add_field(name="Time :hourglass::", value="You have 30 seconds to choose.")

        b = await ctx.send(embed=embed)


        for key, value in var[r]["playeremoji"].items():
                    if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True or Player.get_player(value, var[r]["playerdict"]).faction == Faction.Mafia):
                        continue
                    else:
                        await b.add_reaction(key)  



        def check(reaction:Reaction, user):
            return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]

        try:
            reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
            target = var[r]["playeremoji"][reaction.emoji]
            var[r]["targets"][ctx.id] = 0

            targetuser = bot.get_user(target)
            embed = discord.Embed(title=f"**You have decided to distract {targetuser.name} tonight.**", colour=discord.Colour(0xd0021b))

            embed.set_thumbnail(url=targetuser.avatar_url)
            embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar_url)
            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
            await ctx.send(embed=embed)

            embed = discord.Embed(title=f"**{ctx.name} has decided to distract {targetuser.name}#{targetuser.discriminator} tonight.**", colour=discord.Colour(0xd0021b))

            embed.set_thumbnail(url="https://media.discordapp.net/attachments/871525831422398497/890335792772313098/ConsIcon.png?width=701&height=701")

            await var[r]["mafcon"].send(embed=embed)
        except asyncio.TimeoutError:
            var[r]["targets"][ctx.id] = 0
            embed = discord.Embed(title="**You did not perform your night ability.**", colour=discord.Colour(0xd3d3d3))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
            embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)
            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True

            embed = discord.Embed(title=f"**{ctx.name} has did not preform their night ability.**", colour=discord.Colour(0xd0021b))

            embed.set_thumbnail(url="https://media.discordapp.net/attachments/871525831422398497/890335792772313098/ConsIcon.png?width=701&height=701")
            await var[r]["mafcon"].send(embed=embed)

        except Exception as e:
            print(e)
        af = 0
        max = 0
        for value in var[r]["playerdict"].values():
            if (value.id != 0 and value.dead == False):
                max += 1

        for value in var[r]["playerdict"].values():
            if (value.ready == True and value.dead == False):
                af += 1

        if (af >= max):
            var[r]["isresults"] = True
            await nighttargets(r)
            return
    elif (role == "jester"):
        if (Player.get_player(ctx.id, var[r]["playerdict"]).jesterwin == True):
            message = "**Your targets are...**"
            embed = discord.Embed(title="**Who do you wish to haunt?**", colour=discord.Colour(0xffc3e7), description="**Your targets are...**")

            embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/895419320140693584/export.png?width=396&height=408")
            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/F8o5Mi5dYJDvkfQ3B98JCbUYmdmdnupZQyNa2wXpEBk/https/media.discordapp.net/attachments/765738640554065962/872147798336893019/imageedit_4_4906520050.png")
            embed.set_footer(text="React with who you to take your revenge on.", icon_url=ctx.avatar_url)
            index = 0

            for key, value in var[r]["playeremoji"].items():
                if (value != ctx.id):
                    if (Player.get_player(value, var[r]["playerdict"]).dead == True):
                        continue
                    else:
                        if (Player.get_player(value, var[r]["playerdict"]).id in var[r]["guiltyers"] == False):
                            index += 1
                            continue

                        user:discord.User = bot.get_user(value)
                        embed.add_field(name=f"{key} - {user.name}#{user.discriminator} :ghost:", value="** **", inline=False)


            embed.add_field(name="Time :hourglass::", value="You have 30 seconds to choose.")

            b = await ctx.send(embed=embed)

            index=0

            for i in var[r]["playeremoji"].keys():
                if (var[r]["playeremoji"][i] != ctx.id):
                    if (i == ctx.id or Player.get_player(var[r]["playeremoji"][i], var[r]["playerdict"]).id in var[r]["guiltyers"] == False or Player.get_player(var[r]["playeremoji"][i], var[r]["playerdict"]).dead == True):
                        index += 1
                        continue
                    else:
                        await b.add_reaction(i)
                        index += 1

            def check(reaction:Reaction, user):
                return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]

            try:
                reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
                target = var[r]["playeremoji"][reaction.emoji]
                var[r]["targets"][ctx.id] = target
                targetuser = bot.get_user(target)
                embed = discord.Embed(title=f"**You have decided to haunt {targetuser.name} tonight.**", colour=discord.Colour(0xffc3e7))

                embed.set_thumbnail(url=targetuser.avatar_url)
                embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar_url)
                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
                        
                await ctx.send(embed=embed)
            except asyncio.TimeoutError:
                tcf = []

                for i in var[r]["playerdict"].values():
                    if (i.id in var[r]["guiltyers"]):
                        tcf.append(i.id)

                var[r]["targets"][ctx.id] = random.choice(tcf)

                e = bot.get_user(var[r]["targets"][ctx.id])
                member:discord.Member = var[r]["guildg"].get_member(e.id)

                embed = discord.Embed(title="**You have not chosen anyone so a random target was selected instead.**", colour=discord.Colour(0xffc3e7))

                embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/F8o5Mi5dYJDvkfQ3B98JCbUYmdmdnupZQyNa2wXpEBk/https/media.discordapp.net/attachments/765738640554065962/872147798336893019/imageedit_4_4906520050.png")
                embed.set_footer(text="Who is the unlucky fellow?", icon_url=ctx.avatar_url)
                await ctx.send(embed=embed)
                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
                await haunt(member, r)
                embed = discord.Embed(title="**You were haunted by the Jester <:jesticon2:889968373612560394>.**", colour=discord.Colour(0xffc3e7), description="**You have died <:rip:747726596475060286>.**")

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/895419320140693584/export.png?width=396&height=408")
                embed.set_footer(text="Rest in peace.", icon_url=ctx.avatar_url)
                await e.send(embed=embed)

                var[r]["targets"][ctx.id] = 0


            af = 0
            max = 0
            for value in var[r]["playerdict"].values():
                if (value.id != 0 and value.dead == False):
                    max += 1

            for value in var[r]["playerdict"].values():
                if (value.ready == True and value.dead == False):
                    af += 1

            if (af >= max):
                var[r]["isresults"] = True
                await nighttargets(r)
                return
            else:
                return
        else:
            var[r]["targets"][ctx.id] = 0
            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True

            af = 0
            max = 0
            for value in var[r]["playerdict"].values():
                if (value.id != 0 and value.dead == False):
                    max += 1

            for value in var[r]["playerdict"].values():
                if (value.ready == True and value.dead == False):
                    af += 1

            if (af >= max):
                var[r]["isresults"] = True
                await nighttargets(r)
                return
            else:
                return
    elif (role=="consigliere"):
        embed = discord.Embed(title="**Who do you investigate tonight?**", colour=discord.Colour(0xd0021b), description="**Your targets are...**")

        embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/899070109002379315/image0.png?width=396&height=408")
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/871527176527315025.png?size=96")
        embed.set_footer(text="React with who you want to investigate.", icon_url=ctx.avatar_url)
        
        for key, value in var[r]["playeremoji"].items():
            if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True or Player.get_player(value, var[r]["playerdict"]).faction == Faction.Mafia):
                continue
            else:
                user:discord.User = bot.get_user(value)
                embed.add_field(name=f"{key} - {user.name}#{user.discriminator} :mag_right:", value="** **", inline=False)

        embed.add_field(name="Time :hourglass::", value="You have 30 seconds to choose.")
        b = await ctx.send(embed=embed)



        for key, value in var[r]["playeremoji"].items():
                    if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True or Player.get_player(value, var[r]["playerdict"]).faction == Faction.Mafia):
                        continue
                    else:
                       await b.add_reaction(key)


        def check(reaction:Reaction, user):
            return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]

        try:
            reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
            target = var[r]["playeremoji"][reaction.emoji]
            var[r]["targets"][ctx.id] = target
            targetuser = bot.get_user(target)
            embed = discord.Embed(title=f"**You have decided to investigate {targetuser.name} tonight.**", colour=discord.Colour(0xd0021b))
            embed.set_thumbnail(url=targetuser.avatar_url)
            embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar_url)
            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
            await ctx.send(embed=embed)

            embed = discord.Embed(title=f"**{ctx.name} has decided to investigate {targetuser.name}#{targetuser.discriminator} tonight.**", colour=discord.Colour(0xd0021b))

            embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/896154319747944468/ConsigIcon.png?width=468&height=468")
            await var[r]["mafcon"].send(embed=embed)
        except asyncio.TimeoutError:
            var[r]["targets"][ctx.id] = 0
            embed = discord.Embed(title="**You did not perform your night ability.**", colour=discord.Colour(0xd3d3d3))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
            embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)

            embed = discord.Embed(title=f"**{ctx.name} did not preform their night ability.**", colour=discord.Colour(0xd0021b))

            embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/896154319747944468/ConsigIcon.png?width=468&height=468")
            await var[r]["mafcon"].send(embed=embed)

            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
        except Exception as e:
            print(e)
        
        af = 0
        max = 0
        for value in var[r]["playerdict"].values():
            if (value.id != 0 and value.dead == False):
                max += 1
            else:
                if (value.dead == True and value.role.lower() == "jester" and value.jesterwin == True):
                    max += 1

        for value in var[r]["playerdict"].values():
            if (value.ready == True and value.dead == False):
                af += 1
            else:
                if (value.dead == True and value.dead == True and value.role.lower() == "jester" and value.jesterwin == True):
                    af += 1

        if (af >= max):
            var[r]["isresults"] = True
            await nighttargets(r)
            return
        else:
            return

    elif (role == "mayor"):
        if (Player.get_player(ctx.id, var[r]["playerdict"]).isrevealed == False):
            embed = discord.Embed(title="Would you like to reveal?", description="", color=0x7ed321)
            embed.add_field(name="Time :hourglass::", value="You have 30 seconds to choose.")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/897570023143518288.png?size=80")
            embed.set_image(url="https://cdn.discordapp.com/attachments/878437549721419787/882418844424081449/unknown.png")
            embed.set_footer(text="React yes or no.", icon_url=ctx.avatar_url)
            b = await ctx.send(embed=embed)

            await b.add_reaction("✅")
            await b.add_reaction("❌")



            def check(reaction:Reaction, user):
                return user.id == ctx.id and str(reaction.emoji) in ["✅", "❌"]

            try:
                reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
                if (reaction.emoji == "✅"):
                    var[r]["targets"][ctx.id] = True
                    embed = discord.Embed(title=f"**You have decided to reveal tonight.**", color=0x7ed321)
                    embed.set_thumbnail(url=ctx.avatar_url)
                    embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar_url)
                else:
                    embed = discord.Embed(title=f"**You have decided to not reveal tonight.**", color=0x7ed321)
                    embed.set_thumbnail(url=ctx.avatar_url)
                    embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar_url)
                
                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
                await ctx.send(embed=embed)
            except asyncio.TimeoutError:
                var[r]["targets"][ctx.id] = 0
                embed = discord.Embed(title="**You did not perform your night ability.**", colour=discord.Colour(0xd3d3d3))

                embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
                embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar_url)
                await ctx.send(embed=embed)
                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
            except Exception as e:
                print(e)
            
            af = 0
            max = 0
            for value in var[r]["playerdict"].values():
                if (value.id != 0 and value.dead == False):
                    max += 1

            for value in var[r]["playerdict"].values():
                if (value.ready == True and value.dead == False):
                    af += 1

            if (af >= max):
                var[r]["isresults"] = True
                await nighttargets(r)
                return
            else:
                return
        else:
            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
            var[r]["targets"][ctx.id] = 0

            af = 0
            max = 0
            for value in var[r]["playerdict"].values():
                if (value.id != 0 and value.dead == False):
                    max += 1

            for value in var[r]["playerdict"].values():
                if (value.ready == True and value.dead == False):
                    af += 1

            if (af >= max):
                var[r]["isresults"] = True
                await nighttargets(r)
                return
            else:
                return
    elif (role == "framer"):
        embed = discord.Embed(title="**Who do you frame tonight?**", colour=discord.Colour(0xd0021b), description="**Your targets are...**")

        embed.set_image(url="https://cdn.discordapp.com/attachments/765738640554065962/886034880503382056/unknown.png")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/871525831422398497/890365126866251796/FrameIcon_3.png?width=701&height=701")
        embed.set_footer(text="React with who you want to frame.", icon_url=ctx.avatar_url)
        for key, value in var[r]["playeremoji"].items():
            if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True or Player.get_player(value, var[r]["playerdict"]).faction == Faction.Mafia):
                continue
            else:
                user:discord.User = bot.get_user(value)
                embed.add_field(name=f"{key} - {user.name}#{user.discriminator} :receipt:", value="** **", inline=False)

        embed.add_field(name="Time :hourglass::", value="You have 30 seconds to choose.")

        b = await ctx.send(embed=embed)


        for key, value in var[r]["playeremoji"].items():
                    if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True or Player.get_player(value, var[r]["playerdict"]).faction == Faction.Mafia):
                        continue
                    else:
                        await b.add_reaction(key)  



        def check(reaction:Reaction, user):
            return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]

        try:
            reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
            target = var[r]["playeremoji"][reaction.emoji]
            var[r]["targets"][ctx.id] = target
            targetuser = bot.get_user(target)
            embed = discord.Embed(title=f"**You have decided to frame {targetuser.name} tonight.**", colour=discord.Colour(0xd0021b))

            embed.set_thumbnail(url=targetuser.avatar_url)
            embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar_url)
            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
            await ctx.send(embed=embed)

            embed = discord.Embed(title=f"**{ctx.name} has decided to frame {targetuser.name}#{targetuser.discriminator} tonight.**", colour=discord.Colour(0xd0021b))

            embed.set_thumbnail(url="https://media.discordapp.net/attachments/871525831422398497/890365126866251796/FrameIcon_3.png?width=701&height=701")
            await var[r]["mafcon"].send(embed=embed)
        except asyncio.TimeoutError:
            var[r]["targets"][ctx.id] = 0
            embed = discord.Embed(title="**You did not perform your night ability.**", colour=discord.Colour(0xd3d3d3))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
            embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)
            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True

            embed = discord.Embed(title=f"**{ctx.name} did not preform their night ability.**", colour=discord.Colour(0xd0021b))

            embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/-3Xcutx_NAdq8vfvtL1PgZiavCrfhdBfu5V3TIorcpo/%3Fv%3D1/https/cdn.discordapp.com/emojis/871863934557224960.png")
            await var[r]["mafcon"].send(embed=embed)
        except Exception as e:
            print(e)
        
        af = 0
        max = 0
        for value in var[r]["playerdict"].values():
            if (value.id != 0 and value.dead == False):
                max += 1

        for value in var[r]["playerdict"].values():
            if (value.ready == True and value.dead == False):
                af += 1

        if (af >= max):
            var[r]["isresults"] = True
            await nighttargets(r)
            return
        else:
            return
    elif (role == "detective"):
        embed = discord.Embed(title="**Who do you investigate tonight?**", colour=discord.Colour(0x7ed321), description="**Your targets are...**")

        embed.set_image(url="https://cdn.discordapp.com/attachments/878437549721419787/882427985012080681/unknown.png")
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/871526928799129651.png?v=1")
        embed.set_footer(text="React with who you want to investigate.", icon_url=ctx.avatar_url)

        for key, value in var[r]["playeremoji"].items():
            if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                continue
            else:
                user:discord.User = bot.get_user(value)
                embed.add_field(name=f"{key} - {user.name}#{user.discriminator} :mag_right:", value="** **", inline=False)

        embed.add_field(name="Time :hourglass::", value="You have 30 seconds to choose.")
        b = await ctx.send(embed=embed)


        for key, value in var[r]["playeremoji"].items():
                    if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                        continue
                    else:
                       await b.add_reaction(key)



        def check(reaction:Reaction, user):
            return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]

        try:
            reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
            target = var[r]["playeremoji"][reaction.emoji]
            var[r]["targets"][ctx.id] = target
            targetuser = bot.get_user(target)
            embed = discord.Embed(title=f"**You have decided to investigate {targetuser.name} tonight.**", color=0x7ed321)
            embed.set_thumbnail(url=targetuser.avatar_url)
            embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar_url)
            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
            await ctx.send(embed=embed)
        except asyncio.TimeoutError:
            var[r]["targets"][ctx.id] = 0
            embed = discord.Embed(title="**You did not perform your night ability.**", colour=discord.Colour(0xd3d3d3))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
            embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar_url)
            await ctx.send(embed=embed)
            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
        except Exception as e:
            print(e)
        
        af = 0
        max = 0
        for value in var[r]["playerdict"].values():
            if (value.id != 0 and value.dead == False):
                max += 1

        for value in var[r]["playerdict"].values():
            if (value.ready == True and value.dead == False):
                af += 1

        
        if (af >= max):
            var[r]["isresults"] = True
            await nighttargets(r)
            return
        else:
            return
    elif (role ==  "headhunter"):
        var[r]["targets"][ctx.id] = 0
        Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
    elif (role == "psychic"):
        var[r]["targets"][ctx.id] = 0
        Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
    else:
        return

async def protecc(member:discord.User, guild):
    mem = Player.get_player(member.id, var[guild]["playerdict"])
    mem.doc = True
    return True

async def attack(me, member:discord.User, ctx):
    if (Player.get_player(me, var[ctx]["playerdict"]).role == "Mafioso" or Player.get_player(me, var[ctx]["playerdict"]).role == "Godfather" or Player.get_player(me, var[ctx]["playerdict"]).role == "Enforcer" or Player.get_player(me, var[ctx]["playerdict"]).role == "Psychopath"):
        if (Player.get_player(member.id, var[ctx]["playerdict"]).defense != Defense.Default):
            if (Player.get_player(member.id, var[ctx]["playerdict"]).doc == True):
                embed = discord.Embed(title="**You were attacked but someone healed you!**", colour=discord.Colour(0x7ed321))

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/871899679766511666/Target_attacked-removebg-preview.png")
                embed.set_footer(text="Who do you think attacked you?", icon_url=member.avatar_url)
                await member.send(embed=embed)

                embed = discord.Embed(title="**Your target was attacked last night!**", colour=discord.Colour(0x7ed321))

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/871899679766511666/Target_attacked-removebg-preview.png")
                embed.set_footer(text="Who do you think attacked them?", icon_url=member.avatar_url)
                for i in var[ctx]["targets"].keys():
                    if (var[ctx]["targets"][i] == member.id and Player.get_player(i, var[ctx]["playerdict"]).role.lower() == "doctor"):
                        await bot.get_user(i).send(embed=embed)

                        if (Player.get_player(me, var[ctx]["playerdict"]).role == "Psychopath" and Player.get_player(me, var[ctx]["playerdict"]).cautious == False):
                            k = Player.get_player(member.id, var[ctx]["playerdict"])
                            k.dead = True
                            k.deathreason.append(DeathReason.Psychopath)
                            k.will = []
                            k.will.append("Their last will was too bloody to be read.")

                            embed = discord.Embed(title="**You were stabbed by a **Psychopath :knife:** while healing your target.", colour=discord.Colour(0x4a90e2), description="**You have died :rip:.**")

                            embed.set_thumbnail(url="https://discord.com/assets/9f89170e2913a534d3dc182297c44c87.svg")
                            embed.set_footer(text="Rest in peace.", icon_url="https://cdn.discordapp.com/avatars/667189788620619826/f4c9e87dde54e0e2d14db69b9d60deb9.png?size=128")

                            await bot.get_user(i).send(embed=embed)

                return False
            else:
                embed = discord.Embed(title="**Someone attacked you last night but you resisted it.**", colour=discord.Colour(0xfff68a))

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/878379179106787359.png?v=1")
                embed.set_footer(text="Who would attack you?...", icon_url=member.avatar_url)
                await member.send(embed=embed)
                
                return False
        else:
            if (Player.get_player(member.id, var[ctx]["playerdict"]).doc == True):
                embed = discord.Embed(title="**You were attacked but someone healed you!**", colour=discord.Colour(0x7ed321))

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/871899679766511666/Target_attacked-removebg-preview.png")
                embed.set_footer(text="Who do you think attacked you?", icon_url=member.avatar_url)
                await member.send(embed=embed)



                embed = discord.Embed(title="**Your target was attacked last night!**", colour=discord.Colour(0x7ed321))

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/871899679766511666/Target_attacked-removebg-preview.png")
                embed.set_footer(text="Who do you think attacked them?", icon_url=member.avatar_url)
                for i in var[ctx]["targets"].keys():
                    if (var[ctx]["targets"][i] == member.id and Player.get_player(i, var[ctx]["playerdict"]).role.lower() == "doctor"):
                        await bot.get_user(i).send(embed=embed)

                        if (Player.get_player(me, var[ctx]["playerdict"]).role == "Psychopath" and Player.get_player(me, var[ctx]["playerdict"]).cautious == False):
                            k = Player.get_player(member.id, var[ctx]["playerdict"])
                            k.dead = True
                            k.deathreason.append(DeathReason.Psychopath)
                            k.will = []
                            k.will.append("Their last will was too bloody to be read.")

                            embed = discord.Embed(title="**You were stabbed by a **Psychopath :knife:** while healing your target.", colour=discord.Colour(0x4a90e2), description="**You have died :rip:.**")

                            embed.set_thumbnail(url="https://discord.com/assets/9f89170e2913a534d3dc182297c44c87.svg")
                            embed.set_footer(text="Rest in peace.", icon_url="https://cdn.discordapp.com/avatars/667189788620619826/f4c9e87dde54e0e2d14db69b9d60deb9.png?size=128")

                            await bot.get_user(i).send(embed=embed)

                return False

            Player.get_player(member.id, var[ctx]["playerdict"]).dead = True
            return True
    else:
        print("Not working, f")
            

async def haunt(player:discord.Member, guild):
    play = Player.get_player(player.id, var[guild]["playerdict"])
    play.dead = True
    play.diedln = True
    Logger.log("HAUNT SUCESSFULL", LogType.DEBUG)

@bot.command()
async def lmao(ctx):
    await ctx.send("https://images-ext-2.discordapp.net/external/-MOtTDoNH8I7CkxXfNXYxaZc8wRyCTwejBbj6TPfKCw/%3Fwidth%3D375%26height%3D634/https/media.discordapp.net/attachments/765738640554065962/872274879309836408/unknown.png")

@bot.command()
async def cryat(ctx, bad):
    global badtemp
    global badcet
    if (bad == "temp"):
        if (badtemp == True):
            badtemp = False
        else:
            badtemp = True

        await ctx.send(f"Temp has been set to {str(badtemp)}.")
    if (bad == "cet"):
        if (badcet == True):
            badcet = False
        else:
            badcet = True

        await ctx.send(f"Cet has been set to {str(badcet)}.")

@bot.event
async def on_message(message:discord.Message):
    if (message.content.startswith(">")):
        try:
            var[message.guild.id]["test"]
        except:
            try:
                var[message.guild.id] = copy.deepcopy(temp)
            except:
                pass

    if (message.author.id == 703645091901866044 and badtemp == True): #Check if the user is Tempoary_Virus19
        await message.delete() #Delete the message
        return

    if (message.author.id == 667189788620619826 and badcet == True): #Check if the user is Tempoary_Virus19
        await message.delete() #Delete the message
        return


    await bot.process_commands(message)
            
@bot.command()
async def supergive(ctx, user:discord.Member, amount):
    if (ctx.author.id == 839842855970275329):
        if (str(ctx.author.id) not in cur):
            cur[str(ctx.author.id)] = 0
        if (str(user.id) not in cur):
            cur[str(user.id)] = 0

        cur[str(user.id)] += int(amount)

        embed = discord.Embed(title=f"**Successfully given {user.name}#{user.discriminator} __{amount}__ silvers <:silvers:889667891044167680>!**", colour=discord.Colour(0xffdffe), description=f"You now have __idk 69????__ silvers <:silvers:889667891044167680> .")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889667891044167680.png?size=96")
        embed.set_footer(text="Thank you!", icon_url=ctx.author.avatar_url)
        
        await ctx.reply(embed=embed)

        with open('data.json', 'w') as jsonf:
            json.dump(cur, jsonf)
    else:
        await ctx.send("sorry man your not super enough yet")



try:
    bot.run(os.environ("TOKEN"))
except aiohttp.client_exceptions.ClientConnectorError:
    print("when you realize the wifi failed")
