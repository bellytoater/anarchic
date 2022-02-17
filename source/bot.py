# -*- coding: UTF-8 -*-

import asyncio
from pickle import FALSE
import disnake as disnake
from disnake.ext import commands, tasks
import datetime
import json
import string
import re
import demoji
import time
import copy
import os
import random
import time
import aiohttp
import requests
import topgg
import logging
from datetime import datetime
from disnake import Option, ButtonStyle, OptionType, SelectOption, SelectMenu, OptionChoice, ActionRow, MessageInteraction
from disnake.ui import Button
from disnake.ext.commands import errors, MissingPermissions, BadArgument, MissingRequiredArgument, CommandNotFound
from disnake.reaction import Reaction
from disnake.utils import get
from enum import Enum
from datetime import timedelta
from disnake.interactions.application_command import ApplicationCommandInteraction

class Faction(Enum):
    Town = 1
    Mafia = 2
    Cult = 3
    Neutral = 4

class Defense(Enum):
    Default = 1
    Basic  = 2
    Strong = 3

class Attack(Enum):
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
    Cleaned = 12

class EndReason(Enum):
    MafiaWins = 1
    TownWins = 2
    Draw = 3
    Psychopath = 4

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
        self.charges = 3
        self.votedforwho = None
        self.ready = False
        self.id = 0

    def reset(self, will=False):
        self.__init__()

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

achivements = []

class Achievement:
    def __init__(self, name:str, des:str, secret:str, hidden:bool=False, obtainable:bool=True):
        self.name = name
        self.description = des
        self.secret = secret
        self.hidden = hidden
        self.obtainable = obtainable

        achivements.append(self)
        self.id = achivements.index(self)

    def getAch(name:str):
        for i in achivements:
            if (i.secret == name):
                return i
        
        return None

    def getAchById(id:int):
        for i in achivements:
            if (i.id == id):
                return i
        
        return None

    async def unlock(self, user:int, ctx, dm=False):
        try:
            guilds[str(user)]["achivements"]
        except:
            guilds[str(user)]["achivements"] = []

        if (self.id in guilds[str(user)]["achivements"] or self.obtainable == False):
            return

        guilds[str(user)]["achivements"].append(self.id)
        if (ctx != None):
            member = await ctx.guild.fetch_member(user)
        
        if (dm == True):
            embed = disnake.Embed(title="**Achivement unlocked!**", description="You've earned the achievement:", colour=disnake.Colour(0x30ed76))
        else:
            embed = disnake.Embed(title="**Achivement unlocked!**", description=f"{member.mention} earned the achievement:", colour=disnake.Colour(0x30ed76))

        embed.set_author(name=member.name, icon_url=member.avatar.url)
        embed.set_footer(text=f"Congratulations!", icon_url=member.avatar.url)

        embed.add_field(name=self.name, value=self.description)
        if (dm != True):
            await ctx.send(embed=embed)
        else:
            bot.get_user(user).send(embed=embed)

        with open('guilds.json', 'w') as jsonf:
            json.dump(guilds, jsonf)

#init achivements
Achievement("Test", "This is a test achivement.", "simpleTest", False, False)
Achievement("The Beginning", "Everything must start somewhere...", "firstGame")
Achievement("Wealthy Fellow", "Get rich!", "richPlayer")
Achievement("Unstoppable", "Blood shall not be spilled", "nobodyIsDead")
Achievement("Justice", "Truth may come to sight", "hasSeenSuspicous")
Achievement("Natural remedies", "Heal a wounded player", "hasHealedPlayer")
Achievement("Plot Twist", "The greatest one.", "1v1", True)
Achievement("Pacifist", "Without violence, there is only peace", "onlyLynchPlayer", True)
Achievement("Quick Execution", "Secure your victory as soon as possible", "hhDay2")
Achievement("Legendary", "As th ey were a livng legend", "1000Games", True)

#util functions/stuff

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
        return "They were killed by a member of the **Psychopath**."
    if (reason == DeathReason.Cleaned):
        return "We could not determine how they died."

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
    if (reason == DeathReason.Cleaned):
        return 0x4a4a4a

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
            
            try:
                if (e not in well and e["dailyable"] == True):
                    progression += 1
                    e['dailydeal'] = True

                    if (progression >= 3):
                        break
            except:
                pass

        with open('shop.json', 'w') as jsonf:
            json.dump(store, jsonf)

    if (now.hour == 0 and now.minute == 0):
        for i in guilds.values():
            try:
                i["claimed"] = False
            except:
                i["claimed"] = False

            try:
                i["voted"] = False
            except:
                i["voted"] = False

    with open('data.json', 'w') as jsonf:
        json.dump(cur, jsonf)

    with open('guilds.json', 'w') as jsonf:
        json.dump(guilds, jsonf)

intents = disnake.Intents.all()
bot = commands.Bot(command_prefix=">", intents=intents, case_insensitive=True)
bot.topggpy = topgg.DBLClient(bot, "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Ijg4NzExODMwOTgyNzQzMjQ3OCIsImJvdCI6dHJ1ZSwiaWF0IjoxNjM3NDI2MzA2fQ.k8ufWIHlJIeK1xgpXPWlm1LswoKyb5-r86gkcMOjqgg")
logging.basicConfig(level=logging.WARNING)

def tryGetValue(id:int, value):
    try:
        guilds[str(id)]
    except:
        guilds[str(id)] = {"guild" : 0, "joinedgame" : False, "equipped" : None}

    try:
        return guilds[str(id)][value]
    except:
        guilds[str(id)][value] = None

        return guilds[str(id)][value]
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

def noImpsNoCrews(ctx):
    t = []
    m = []
    p = []
    
    for i in var[ctx.id]["playerdict"].values():
        if (i.faction == Faction.Mafia and i.dead == False and i.id != 0):
            m.append(i)
    
    for i in var[ctx.id]["playerdict"].values():
        if (i.faction == Faction.Town and i.dead == False and i.id != 0):
            t.append(i)

    for i in var[ctx.id]["playerdict"].values():
        if (i.role == "Psychopath" and i.dead == False and i.id != 0):
            p.append(i)

    res = False
    if (len(t) == 0 and len(m) == 0 and len(p) == 1):
        res = True

    return res

def getPsychos(ctx):
    p = []
    for i in var[ctx.id]["playerdict"].values():
        if (i.role == "Psychopath" and i.dead == False and i.id != 0):
            p.append(i)

    return p

def getWill(mywill:list):
    message = ""
    for i in mywill:
        if (i == ""):
            continue

        message += i + "\n"

    return message

async def EndGame(reason:EndReason, guild):
    await completeunlock(var[guild.id]["channel"])
    embed = disnake.Embed()
    var[guild.id]["endreason"] = reason

    for i in var[guild.id]["playerdict"].values():
        if (i.role == "Psychopath"):
            if (len(getMaf(guild)) == 0 and len(getTownies(guild)) == 0):
                i.wins = True

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
        embed = disnake.Embed(title="**__Draw :crescent_moon:__**", colour=disnake.Colour(0xb0c9c9))

        embed.set_image(url="https://images-ext-2.discordapp.net/external/LlOBlIZEHHfRmfQn8_dhpUD6gN0CUWMecRcDZjd9CTs/%3Fwidth%3D890%26height%3D701/https/media.discordapp.net/attachments/765738640554065962/877706810763657246/unknown.png?width=805&height=634")
        embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png?width=374&height=374")
        for i in var[guild.id]["playerdict"].values():
            i.wins = False
    elif (reason == EndReason.Psychopath):
        embed = disnake.Embed(title="***__<a:win:878421027703631894> The Psychopath Wins <a:win:878421027703631894>!__***", colour=disnake.Colour(0xb0c9c9))

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
        try:
            message += em[i.ogrole.lower()]
        except:
            message += "???"

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
"roles" : ["Cop", "Detective", "Lookout", "Doctor", "Enforcer", "Psychic", "Mayor", "Mafioso", "Consigliere", "Framer", "Consort", "Headhunter", "Jester", "Tracker", "Psychopath", "Janitor"],
"towns" : ["Cop", "Detective", "Lookout", "Doctor", "Enforcer", "Mayor", "Psychic", "Tracker", "Attendant"],
"support" : ["Mayor", "Psychic", "Attendant"],
"mafias" : ["Framer", "Consort", "Consigliere", "Janitor"],
"cults" : ["Cult Leader", "Ritualist"],
"neutrals" : ["Headhunter", "Jester", "Psychopath"],
"uniques" : ["Janitor", "Framer", "Consigliere", "Consort"],
"investigatives" : ["Cop", "Detective", "Lookout", "Tracker"],
"comps" : {"enforced": ["Enforcer", "Doctor", "Mafioso", "RT", "RN"], "classic":["Cop", "Doctor", "Mayor", "Jester", "Mafioso"], "execution":["Cop", "Doctor", "RT", "RT", "Headhunter", "Mafioso"], "legacy":["Cop", "Doctor", "RT", "RT", "RT", "RN", "Mafioso", "RM"], "scattered":["Enforcer", "Doctor", "RT", "RT", "RT", "Mafioso", "RM", "Headhunter"], "duet": ["Enforcer", "Doctor", "TI", "RT", "RT", "Mafioso", "Consort"], "framed": ["Cop", "Doctor", "TI", "RT", "RT", "Mafioso", "Framer"], "anarchy": ["Mayor", "Doctor", "TI", "TI", "RT", "RT", "Mafioso", "RM", "RN", "A"], "ranked": ["Doctor", "Enforcer", "TI", "TI", "RT", "RT", "RT", "Mafioso", "Consort", "Framer"], "truth" : ["Detective", "Doctor", "RT", "RT", "RT", "Mafioso", "Consigliere"],"delta":["Psychopath", "Tracker", "Mafioso"], "custom" : []},
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
"night" : False,
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
"itememoji" : {"Cop Shard" : "<:copshard:924295242566467584>", "Doctor Shard" : "<:docshard:896576968756191273>", "Enforcer Shard" : "<:enfshard:896576814942670899>" ,"Detective Shard" : "<:detshard:924299675891290173>", "Lookout Shard" : "<:loshard:896577050645786655>", "Epic Programmer Trophy" : ":computer:", "Epic Designer Trophy" : ":video_game:", "Epic Artist Trophy" : ":art:", "Mafioso Shard" : "<:mafshard:923934147402162227>", "Headhunter Shard" : "<:hhshard:923934411219681361>", "Jester Shard" : "<:jestshard:923933880833146910>", "Consigliere Shard" : "<:consigshard:924295501795446844>", "Framer Shard" : "<:frameshard:924299361565966406>", "Psychic Shard" : "<:psyshard:924298902058987540>", "Mayor Shard" : "<:mayorshard:924300251869888552>", "Consort Shard" : "<:consshard:924299559168008222>", "Detective Shard" : "<:detshard:924299675891290173>", "Lookout" : "<:loshard:896577050645786655>"},
"emoji" : {"cop": "<:copicon2:889672912905322516>", "doctor": "<:docicon2:890333203959787580>", "mafioso": "<:maficon2:891739940055052328>", "enforcer": "<:enficon2:890339050865696798>", "lookout": "<:loicon2:889673190392078356>", "psychopath" : "<:psychoicon:922564838897627166>", "consort": "<:consicon2:890336628269281350>", "jester": "<:jesticon2:889968373612560394>", "headhunter": "<:hhicon2:891429754643808276>", "mayor": "<:mayoricon:922566007946629131>", "detective":"<:deticon2:889673135438319637>", "framer": "<:frameicon2:890365634913902602>", "psychic": "<:psyicon2:896159311078780938>", "consigliere" : "<:consigicon2:896154845130666084>", "tracker" : "<:trackicon:922885543812005949>", "janitor" : "<:janiicon:923219547325091840>", "attendant" : "<:mario:901229374500655135>", "rt": "<:townicon2:896431548717473812>", "rm": "<:maficon2:890328238029697044>", "rn": ":axe:", "ti": ":mag_right:", "ts": "🛠️", "a" : ":game_die:"},
"result" : False,
"targetint" : 0,
"vkickd" : {},
"ind" : 0,
"isresults" : False,
"guiltyinno" : False,
"mafcon" : None,
"votethreads" : 0,
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
"daysnokill" : 0,
"leaveq" : [],
"joinq" : [],
"maftarget" : 0
}

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
    i["guild"] = 0
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
    print('Logged in as:')
    print(bot.user.name)
    print('With a bot ID of ' + str(bot.user.id))
    print('------')
    game = disnake.Activity(type=disnake.ActivityType.watching, name="chaos | /help")
    await bot.change_presence(status=disnake.Status.do_not_disturb, activity=game)
    try:
        shopUpdater.start()
    except:
        pass



@bot.event
async def on_slash_command_error(interaction, error):
    if (isinstance(error, disnake.ext.commands.errors.PrivateMessageOnly)):
        await interaction.response.send_message("This command can only be used in DMs.", ephemeral=True)
        return     

    elif (isinstance(error, disnake.ext.commands.errors.NoPrivateMessage)):
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return
    if (isinstance(error, disnake.errors.NotFound)):
        embed = disnake.Embed(title="**There was an error processing your command**", colour=disnake.Colour(0xff6752), description="**Try running your command again!**")

        embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/zvBfC-Hei3zC-NkTa_MJ1t-lx4Fu6dXoB-5uzicvPYE/https/images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%253Fwidth%253D468%2526height%253D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")
        embed.set_footer(text="If this keeps happening, contact support at `/invite`", icon_url=interaction.author.avatar.url)
        await interaction.channel.send(content=interaction.author.mention, embed=embed, ephemeral=True)
    elif (isinstance(error, disnake.errors.Forbidden)):
        embed = disnake.Embed(title="The bot is lacking permissions to perform an action", colour=disnake.Colour(0xea5f61), description="**The bot is missing role permissions to preform an action. Make sure that the bot has the following permissions:\nManage Roles\nManage Channels\nManage Nicknames\nChange Nickname\nRead Messages\nSend Messages\nManage Messages\nEmbed Links\nAttatch Files\nRead Message History\nMention Everyone\nAdd Reactions\nUse External Emojis**")

        embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")
        embed.set_footer(text="If this keeps happening, contact support with `/invite`")
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

    try:
        guilds[str(inter.author.id)]
    except:
        guilds[str(inter.author.id)] = {"guild" : 0, "joinedgame" : False, "equipped" : None}

    random.seed(time.time())

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

@bot.slash_command(
    name="ping",
    description="Get the latency of the bot"
)
async def ping(ctx:ApplicationCommandInteraction):
    latency = bot.latency * 1000
    emb = disnake.Embed(title="Pinging...", color=disnake.Color.blue())

    emb.add_field(name="Discord WS:", value=f"```yaml\n{str(round(latency))}ms```", inline=False)
    emb.add_field(name = "**Typing**", value = "```yaml\n...```", inline = True)
    emb.add_field(name = "**Message**", value = "```yaml\n...```", inline = True)

    before = time.monotonic()

    await ctx.response.send_message(embed=emb)

    ping = (time.monotonic() - before) * 1000
    create = await ctx.original_message()
    create = create.created_at

    emb.title = "**Pong!**"
    emb.set_field_at(1, name = "**Message:**", value = f"```yaml\n{str(int((create - ctx.created_at).total_seconds() * 1000))}ms```", inline = True)
    emb.set_field_at(
            2, name = "**Typing:**", value = f"```yaml\n{str(round(ping))}ms```", inline = True)

    msg = await ctx.original_message()
    await msg.edit(embed = emb)

@bot.command()
async def help(ctx):
    embed = disnake.Embed(title="**__Anarchic's Commands__**", colour=disnake.Colour(0xc4f5ff), description="**:pushpin: Note: **The bot mainly uses slash commands as a form of input. You'll need to use slash commands if you want to join a game, collect silvers, etc.")

    embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")

    embed.add_field(name="**__Party <a:Tada:841483453044490301>__**", value="`/join` to join the game.\n`/leave` to leave the game.\n`/setup [gamemode]` to change the mode.\n`/party` to view the party.\n`/start` to start the game.\n`/vkick [user]` to vote to kick a player.\n`/kick [user]` to kick a player.\n`/clear` to clear the entire party.", inline=False)
    embed.add_field(name="**__Game :video_game:__**", value="\n`/vote member [player]` to vote a player during the game.\n`/will write [text] [line]` to write and edit your will.\n`/will remove [line]` to remove a line in your will.\n`/will view` to view your will.", inline=False)
    embed.add_field(name="**__Information 💡__**", value="`/help` to see the list of commands.\n`/bal` to see your balance and profile.\n`/roles` to see the list of roles.\n`/role [role name]` to see a specific role.\n`/setups` to see the list of setups.\n`/changelog` to view the lastest updates.\n`/invite` to get an invite to the official server.", inline=False)
    embed.add_field(name="**Invite**", value="Invite the bot to your server [here](https://discord.com/api/oauth2/authorize?client_id=887118309827432478&permissions=105696980048&scope=bot%20applications.commands)!")

    await ctx.send(embed=embed)

class Tag(disnake.ui.Modal):
    def __init__(self) -> None:

        components = [
            disnake.ui.TextInput(
                style=disnake.TextInputStyle.single_line,
                label="YOUR MOM",
                placeholder="YOUR MOM",
                custom_id="name",
                max_length=50,
            ),
            disnake.ui.TextInput(
                style=disnake.TextInputStyle.long,
                label="YOUR MOM",
                placeholder="YOUR MOM",
                custom_id="content",
            )
        ]

        super().__init__(title="YOUR MOM", custom_id="tag_creation", components=components)

    async def callback(self, inter: disnake.ModalInteraction) -> None:
        await inter.response.send_message("cool")

    async def on_error(self, error: Exception, inter: disnake.ModalInteraction) -> None:
        await inter.response.send_message("Oops, something went wrong.", ephemeral=True)

@bot.slash_command(
    name="your_mom",
    description="your_mom",
    guild_ids=[753967387149074543]
)
async def your_mom(inter: disnake.AppCmdInter) -> None:
    await inter.response.send_modal(Tag())

# @bot.command()
# async def test_achivement(ctx):
#     await Achievement.getAch("simpleTest").unlock(ctx.author.id, ctx.channel)

@bot.slash_command(
    name="help",
    description="Get help",
    gulid_ids=[871525831422398494]
)
async def hhelp(inter): 

    await inter.response.defer()

    embed = disnake.Embed(title="**__Anarchic's Commands__**", colour=disnake.Colour(0xc4f5ff))

    embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")

    embed.add_field(name="**__Party <a:Tada:841483453044490301>__**", value="`/join` to join the game.\n`/leave` to leave the game.\n`/setup [gamemode]` to change the mode.\n`/party` to view the party.\n`/start` to start the game.\n`/vkick [user]` to vote to kick a player.\n`/kick [user]` to kick a player.\n`/clear` to clear the entire party.", inline=False)
    embed.add_field(name="**__Game :video_game:__**", value="\n`/vote member [player]` to vote a player during the game.\n`/will write [text] [line]` to write and edit your will.\n`/will remove [line]` to remove a line in your will.\n`/will view` to view your will.", inline=False)
    embed.add_field(name="**__Information 💡__**", value="`/help` to see the list of commands.\n`/bal` to see your balance and profile.\n`/roles` to see the list of roles.\n`/role [role name]` to see a specific role.\n`/setups` to see the list of setups.\n`/changelog` to view the lastest updates.\n`/invite` to get an invite to the official server.", inline=False)
    await inter.edit_original_message(embed=embed)

@bot.command()
async def invite(ctx):
    await invite(ctx)

@bot.slash_command(
    name="invite",
    description="Add the bot to your server!"
)
async def invite(ctx):
    dev:disnake.User = bot.get_user(839842855970275329)
    art:disnake.User = bot.get_user(643566247337787402)
    mak:disnake.User = bot.get_user(667189788620619826)


    embed = disnake.Embed(title="Anarchic", colour=disnake.Colour(0xff8b6c), description="*Hosts games of Anarchic, which are styled similar to the classic party game Mafia!*")

    embed.set_thumbnail(url=ctx.guild.icon.url)
    embed.set_footer(text="Invite me to your server!", icon_url=ctx.author.avatar.url)
    embed.add_field(name="Bot", value="[Click Here](https://discord.com/api/oauth2/authorize?client_id=887118309827432478&permissions=105696980048&scope=bot%20applications.commands)", inline=False)
    embed.add_field(name="Server", value="[Click Here](https://disnake.gg/ZHuFPHy7cw)", inline=False)
    embed.add_field(name="Anarchic Staff Team", value=f"**:art: Artist - {art.name}#{art.discriminator}**\n**:computer: Programmer - {dev.name}#{dev.discriminator}**\n**:video_game: Manager - {mak.name}#{mak.discriminator}**")
    await ctx.send(embed=embed)


@bot.command()
async def inviteurl(ctx):
    await ctx.send("https://discord.com/api/oauth2/authorize?client_id=887118309827432478&permissions=105696980048&scope=bot%20applications.commands")

@commands.guild_only()
@bot.slash_command(
    name="changelog",
    description="Get the new stuff from the bot"
)
async def chagelog(ctx):
    # New Feature = <:p_ThinDashYellow:878761154887942204>
    # Bug Fixes = <:p_ThinDashGreen:878761154653061141>
    # Visual Updates = <:p_ThinDashPurple:878761154837630986>
    # Quality of Life changes = <:p_ThinDashOrange:878761154451755049>
    # News = <:p_ThinDashPink:878761154846007356>


    two = disnake.Embed(title="Patch Notes 1.1.0: Psychic and Consigliere <:psyicon2:896159311078780938><:consigshard:924295501795446844>", colour=disnake.Colour(0xb5ffee), description="A enormous update which contains 2 new roles!")

    two.set_image(url="https://media.discordapp.net/attachments/765738640554065962/897243210177462272/export.png?width=454&height=468")
    two.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")
    two.set_footer(text="October 11, 2021", icon_url=ctx.author.avatar.url)

    two.add_field(name="New Roles :performing_arts: ", value="**Psychic <:psyicon2:896159311078780938> - A powerful mystic who can speak to the dead**\n**Consigliere <:consigshard:924295501795446844> - A corrupted detective who gathers information for the Mafia**", inline=False)
    two.add_field(name="**Bug Fixes :bug:**", value="<:p_ThinDashGreen:878761154653061141> **Fixed bug where bot awkwardly crashes when a player is lynched\n<:p_ThinDashGreen:878761154653061141> Fixed bug where players could see dead chat\n<:p_ThinDashGreen:878761154653061141> Fixed bug where Mafioso was town sided**", inline=False)
    two.add_field(name="**Shop :shopping_bags:**", value="<:p_ThinDashPurple:878761154837630986> **Anarith - The best place to shop in the town is now open for business! Check it out with `/shop`**", inline=False)
    two.add_field(name="**Shards <:copshard:924295242566467584>**", value="<:p_ThinDashPurple:878761154837630986> **Shards are released! Shards are items that give you a higher chance of getting a role, but disappear after you get the role. Have fun using them!**", inline=False)
    two.add_field(name="Miscellaneous :gear:", value="<:p_ThinDashYellow:878761154887942204> **Added 2 new setups, __Truth <:consigshard:924295501795446844>__ and __Scattered__\n<:p_ThinDashYellow:878761154887942204> Removed Circus from playable setups\n<:p_ThinDashYellow:878761154887942204> Updated `/help` to include the new commands\n<:p_ThinDashYellow:878761154887942204> Added currency system to the game\n<:p_ThinDashYellow:878761154887942204> Updated certain role embeds**", inline=False)
    
    one = disnake.Embed(title="Patch Notes 1.0.1: Bug Hunting :saxophone::bug:", colour=disnake.Colour(0xb5ffee), description="Just a short bug fixing update with some visuals :paintbrush:")

    one.set_image(url="https://media.discordapp.net/attachments/765738640554065962/893258411658055730/unknown.png?width=463&height=468")
    one.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")
    one.set_footer(text="The fresh and latest update", icon_url=ctx.author.avatar.url)

    one.add_field(name="**Bug Fixes :bug:**", value="<:p_ThinDashGreen:878761154653061141> **Bug where you couldn't target certain players has been fixed**", inline=False)
    one.add_field(name="**Visual Updates :art:**", value="<:p_ThinDashPurple:878761154837630986> **New Doctor Picture** <:docicon2:890333203959787580>\n<:p_ThinDashPurple:878761154837630986> **New Doctor Targeting** <:docicon2:890333203959787580>\n<:p_ThinDashPurple:878761154837630986> **New Jester Image** <:jesticon2:889968373612560394>", inline=False)
    one.add_field(name="Quality of Life Changes :palm_tree:", value="<:p_ThinDashOrange:878761154451755049> **Game results will now be displayed in the channel `/start` was used in**", inline=False)
    one.add_field(name="News :newspaper2:", value="<:p_ThinDashPink:878761154846007356> **Are you feeling confused about the bot? Check out our wiki here! It's not fully complete yet but it should give you a pretty good stance on Cop <:copicon2:889672912905322516>. For more infomation, do `/invite`!**")
    
    class Dropdown(disnake.ui.Select):
        def __init__(self):
            # Set the options that will be presented inside the dropdown
            options = [
                disnake.SelectOption(
                    label="1.1.0", description="Check out the changelog for Anarchic 1.1.0", value="110", emoji='<:consigicon2:896154845130666084>'
                ),
                disnake.SelectOption(
                    label="1.0.1", description="Check out the changelog for Anarchic 1.0.1", value="101", emoji="<:bugg:924306467325112352>"
                )
            ]

            # The placeholder is what will be shown when no option is chosen
            # The min and max values indicate we can only pick one of the three options
            # The options parameter defines the dropdown options. We defined this above
            super().__init__(
                placeholder="Version",
                min_values=1,
                max_values=1,
                options=options,
            )

        async def callback(self, interaction: disnake.MessageInteraction):
            e = self.values[0]

            emb = None

            if (e == "110"):
                emb = copy.copy(two)
            if (e == "101"):
                emb = copy.copy(one)

            #r.children[int(e.replace("p", ""))].default = True

            await interaction.response.edit_message(embed=emb)

    class DropdownView(disnake.ui.View):
        def __init__(self):
            super().__init__()

            self.add_item(Dropdown())
    
    await ctx.send(embed=two, view=DropdownView())

#Economy
@commands.guild_only()
@bot.slash_command(
    name="bal",
    description="Check how many silvers you have",
    options=[
        Option("member", "Check how many silvers your friend has", OptionType.user, False)
    ],
)
async def bal(inter, member=None):
    try:
        var[inter.guild.id]["test"]
    except:
        var[inter.guild.id] = copy.deepcopy(temp)

    try:
        guilds[str(inter.author.id)]["title"]
    except:
        guilds[str(inter.author.id)] = {"guild": 0, "joinedgame": False, "equipped": None, "vkicktarget": 0, "claimed": False, "voted": False, "title": "The Townie"}

    if (member == None):
        if (str(inter.author.id) not in cur):
            cur[str(inter.author.id)] = 0

        balance = str(cur[str(inter.author.id)])
        tit = guilds[str(inter.author.id)]["title"]
        r = tit.replace("The ", "").replace("the ", "")
        embed = disnake.Embed(title=f"<a:sparkle:894702379851735100> {inter.author.name}'s profile <a:sparkle:894702379851735100>", colour=disnake.Colour(0xffddfd), description=f"*The {string.capwords(r)}*")

        # if (inter.author.id == 839842855970275329):
        #     embed.description = "*The Programmer  :computer:*"
        # if (inter.author.id == 667189788620619826):
        #     embed.description = "*The Designer :video_game:*"
        # if (inter.author.id == 703645091901866044):
        #     embed.description = "*The Artist  :art:*"
        # if (inter.author.id == 643566247337787402):
        #     embed.description = "*The Artist  :art:*"

        embed.set_thumbnail(url=inter.author.avatar.url)

        embed.add_field(name="**Currency**", value=f"<:silvers:889667891044167680> **Silvers :** {balance}\n<:gems:889667936304898079> **Gems :** 0")
        await inter.response.send_message(embed=embed)
    else:
        try:
            guilds[str(member.id)]["title"]
        except:
            guilds[str(member.id)]["title"] = "The Townie"

        if (str(member.id) not in cur):
            cur[str(member.id)] = 0

        balance = str(cur[str(member.id)])
        tit = guilds[str(member.id)]["title"]
        r = tit.replace("The ", "")
        embed = disnake.Embed(title=f"<a:sparkle:894702379851735100> {member.name}'s profile <a:sparkle:894702379851735100>", colour=disnake.Colour(0xffddfd), description=f"*The {string.capwords(r)}*")

        # if (member.id == 839842855970275329):
        #     embed.description = "*The Programmer :computer:*"
        # if (member.id == 667189788620619826):
        #     embed.description = "*The Designer :video_game:*"
        # if (member.id == 703645091901866044):
        #     embed.description = "*The Artist :art:*"
        # if (member.id == 643566247337787402):
        #     embed.description = "*The Artist :art:*"

        embed.set_thumbnail(url=member.avatar.url)

        embed.add_field(name="**Currency**", value=f"<:silvers:889667891044167680> **Silvers :** {balance}\n<:gems:889667936304898079> **Gems :** 0")
        await inter.response.send_message(embed=embed)


    with open('data.json', 'w') as jsonf:
        json.dump(cur, jsonf)

@bot.slash_command(
    name="bank",
    description="Check out the latest profits from the shop"
)
async def bank(inter):
    embed = disnake.Embed(title="Anarchic Bank", colour=disnake.Colour(0x6e7343), description="Check out the latest profits from stores!")

    embed.set_thumbnail(url="https://cdn.discordapp.com/icons/753967387149074543/d77cf3d1192d84e441a5a194fb8ef081.webp?size=1024")
    embed.set_footer(text="Take a look.", icon_url=inter.author.avatar.url)

    e = str(cur["bank"])

    embed.add_field(name="Anarith Market", value=f"**{e}** silvers <:silvers:889667891044167680>")
    await inter.response.send_message(embed=embed)

@commands.guild_only()
@bot.slash_command(
    name="give",
    description="Give some silvers to your friend",
    options=[
        Option("member", "The member you want to give your silvers to", OptionType.user, True),
        Option("amount", "How many silvers you want to give", OptionType.integer, True)
    ],
)
async def give(inter, member=None, amount=None):
    if (member.bot == True):
        await inter.response.send_message("You can't give silvers to a bot. Otherwise, how will you get them back?", ephemeral=True)
    else:
        if (amount < 0):
            await inter.response.send_message("<:ehh:869928693814935653>", ephemeral=True)
            return

        if (str(inter.author.id) not in cur):
            cur[str(inter.author.id)] = 0
        if (str(member.id) not in cur):
            cur[str(member.id)] = 0
        
        if (amount <= cur[str(inter.author.id)]):
            cur[str(inter.author.id)] -= amount
            cur[str(member.id)] += amount

            new = cur[str(inter.author.id)] 

            embed = disnake.Embed(title=f"**Successfully given {member.name}#{member.discriminator} __{amount}__ silvers <:silvers:889667891044167680>!**", colour=disnake.Colour(0xffdffe), description=f"You now have __{new}__ silvers <:silvers:889667891044167680> .")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889667891044167680.png?size=96")
            embed.set_footer(text="Thank you!", icon_url=inter.author.avatar.url)
            
            await inter.response.send_message(embed=embed)

            if (cur[str(member.id)] >= 5000):
                Achievement.getAch("richPlayer").unlock(member.id, inter.channel, False)

            with open('data.json', 'w') as jsonf:
                json.dump(cur, jsonf)
        else:
            money = cur[str(inter.author.id)] 
            embed = disnake.Embed(title="**You don't have enough silvers <:silvers:889667891044167680>!**", colour=disnake.Colour(0xff4a87), description=f"You only have __{money}__ silvers <:silvers:889667891044167680> .")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889667891044167680.png?size=96")
            embed.set_footer(text="Better get more money", icon_url=inter.author.avatar.url)
            await inter.response.send_message(embed=embed, ephemeral=True)

async def addPlayerSilvers(userid, amount):
    if (str(userid) not in cur):
        cur[str(userid)] = 0

    cur[str(id)] += amount

@commands.guild_only()
@bot.slash_command(
    name="shop",
    description="Anarith Market"
)
async def shop(inter:ApplicationCommandInteraction):
    deals = []

    for key, value in store.items():
        if (value['dailydeal'] == True):
            deals.append(value)

    page1 = disnake.Embed(title="Anarith Market", colour=disnake.Colour(0xc0c0fb), description="Welcome to Anarith, the biggest hub of shops in the town! To navigate, use the dropdown!")

    page1.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")
    page1.set_footer(text="Daily Deals reset at 8PM UTC.", icon_url=inter.author.avatar.url)

    page1.add_field(name="**<a:sparkle:894702379851735100> Daily Offers <a:sparkle:894702379851735100>**", value="** **", inline=False)
    page1.add_field(name=f"{deals[0]['title']}**| 24** <:silvers:889667891044167680>", value=f"{deals[0]['description']}", inline=False)
    page1.add_field(name=f"{deals[1]['title']}**| 24** <:silvers:889667891044167680>", value=f"{deals[1]['description']}", inline=False)
    page1.add_field(name=f"{deals[2]['title']}**| 24** <:silvers:889667891044167680>", value=f"{deals[2]['description']}", inline=False)
    page1.add_field(name="** **", value="To buy something, use `/buy`!", inline=False)

    page2 = disnake.Embed(title="Anarith Market", colour=disnake.Colour(0xc0c0fb), description="Welcome to Anarith, the biggest hub of shops in the town! To navigate, use the dropdown!")

    page2.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")
    page2.set_footer(text="Take a look around.", icon_url=inter.author.avatar.url)

    page2.add_field(name="**:star2: Shards :star2:**", value="** **", inline=False)

    deal = []
    for value in store.values():
        if (value['dailydeal'] == True):
            deal.append(24)
        else:
            deal.append(39)

    page2.add_field(name=f"Cop Shard <:copshard:924295242566467584>**| {deal[0]}** <:silvers:889667891044167680>", value=f"Increases your chance of rolling **Cop <:copshard:924295242566467584>** by 3x", inline=False)
    page2.add_field(name=f"Detective Shard <:detshard:924299675891290173>**| {deal[1]}** <:silvers:889667891044167680>", value=f"Increases your chance of rolling **Detective <:detshard:924299675891290173>** by 3x", inline=False)
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

    page3 = disnake.Embed(title="Anarith Market", colour=disnake.Colour(0xc0c0fb), description="Welcome to Anarith, the biggest hub of shops in the town! To navigate, use the dropdown!")

    page3.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")
    page3.set_footer(text="Take a look around.", icon_url=inter.author.avatar.url)

    page3.add_field(name="**:star2: Shards :star2:**", value="** **", inline=False)
    page3.add_field(name=f"Mayor Shard <:mayorshard:924300251869888552>**| 39** <:silvers:889667891044167680>", value=f"Increases your chance of rolling **Mayor <:mayorshard:924300251869888552>** by 3x", inline=False)
    page3.add_field(name=f"Psychic Shard <:psyshard:924298902058987540>**| 39** <:silvers:889667891044167680>", value=f"Increases your chance of rolling **Psychic <:psyshard:924298902058987540>** by 3x", inline=False)
    page3.add_field(name=f"Mafioso Shard <:mafshard:923934147402162227>**| 39** <:silvers:889667891044167680>", value=f"Increases your chance of rolling **Mafioso <:mafshard:923934147402162227>** by 3x", inline=False)
    page3.add_field(name=f"Framer Shard <:frameshard:924299361565966406>**| 39** <:silvers:889667891044167680>", value=f"Increases your chance of rolling **Framer <:frameshard:924299361565966406>** by 3x", inline=False)
    page3.add_field(name=f"Consigliere Shard <:consigshard:924295501795446844>**| 39** <:silvers:889667891044167680>", value=f"Increases your chance of rolling **Consigliere <:consigshard:924295501795446844>** by 3x", inline=False)
    page3.add_field(name="** **", value="To buy something, use `/buy`!", inline=False)

    page4 = disnake.Embed(title="Anarith Market", colour=disnake.Colour(0xc0c0fb), description="Welcome to Anarith, the biggest hub of shops in the town! To navigate, use the dropdown!")

    page4.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")
    page4.set_footer(text="Take a look around.", icon_url=inter.author.avatar.url)

    page4.add_field(name="**:star2: Shards :star2:**", value="** **", inline=False)
    page4.add_field(name=f"Consort Shard <:consshard:924299559168008222>**| 39** <:silvers:889667891044167680>", value=f"Increases your chance of rolling **Consort <:consshard:924299559168008222>** by 3x", inline=False)
    page4.add_field(name=f"Headhunter Shard <:hhshard:923934411219681361>**| 39** <:silvers:889667891044167680>", value=f"Increases your chance of rolling **Headhunter <:hhshard:923934411219681361>** by 3x", inline=False)
    page4.add_field(name=f"Jester Shard <:jestshard:923933880833146910>**| 39** <:silvers:889667891044167680>", value=f"Increases your chance of rolling **Jester <:jestshard:923933880833146910>** by 3x", inline=False)
    page4.add_field(name="** **", value="To buy something, use `/buy`!", inline=False)

    page5 = disnake.Embed(title="Anarith Market", colour=disnake.Colour(0xc0c0fb), description="Welcome to Anarith, the biggest hub of shops in the town! To navigate, use the dropdown!")

    page5.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")
    page5.set_footer(text="Take a look around.", icon_url=inter.author.avatar.url)

    page5.add_field(name="**<:titles:922568821624147999> Titles <:titles:922568821624147999>**", value="** **", inline=False)
    page5.add_field(name=f"The Interrogator <:titles:922568821624147999>**| 50** <:silvers:889667891044167680>", value=f"Allows you to equip `The Interrogator` title", inline=False)
    page5.add_field(name=f"The Confused <:titles:922568821624147999>**| 50** <:silvers:889667891044167680>", value=f"Allows you to equip `The Confused` title", inline=False)
    page5.add_field(name=f"The Hero <:titles:922568821624147999>**| 79** <:silvers:889667891044167680>", value=f"Allows you to equip `The Hero` title", inline=False)
    page5.add_field(name="** **", value="To buy something, use `/buy`!", inline=False)

    page6 = disnake.Embed(title="Anarith Market", colour=disnake.Colour(0xc0c0fb), description="Welcome to Anarith, the biggest hub of shops in the town! To navigate, use the dropdown!")

    page6.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")
    page6.set_footer(text="Take a look around.", icon_url=inter.author.avatar.url)

    page6.add_field(name="**<:titles:922568821624147999> Titles <:titles:922568821624147999>**", value="** **", inline=False)
    page6.add_field(name=f"The Slayer <:titles:922568821624147999>**| 79** <:silvers:889667891044167680>", value=f"Allows you to equip `The Slayer` title", inline=False)
    page6.add_field(name=f"The Sheep <:titles:922568821624147999>**| 149** <:silvers:889667891044167680>", value=f"Allows you to equip `The Sheep` title", inline=False)
    page6.add_field(name=f"The Veteran <:titles:922568821624147999>**| 199** <:silvers:889667891044167680>", value=f"Allows you to equip `The Veteran` title", inline=False)
    page6.add_field(name="** **", value="To buy something, use `/buy`!", inline=False)

    page7 = disnake.Embed(title="Anarith Market", colour=disnake.Colour(0xc0c0fb), description="Welcome to Anarith, the biggest hub of shops in the town! To navigate, use the dropdown!")

    page7.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")
    page7.set_footer(text="Take a look around.", icon_url=inter.author.avatar.url)

    page7.add_field(name="**<:titles:922568821624147999> Titles <:titles:922568821624147999>**", value="** **", inline=False)
    page7.add_field(name=f"The Paranoid <:titles:922568821624147999>**| 239** <:silvers:889667891044167680>", value=f"Allows you to equip `The Paranoid` title", inline=False)
    page7.add_field(name=f"The Fool <:titles:922568821624147999>**| 529** <:silvers:889667891044167680>", value=f"Allows you to equip `The Fool` title", inline=False)
    page7.add_field(name=f"The Nightmare <:titles:922568821624147999>**| 529** <:silvers:889667891044167680>", value=f"Allows you to equip `The Nightmare` title", inline=False)
    page7.add_field(name="** **", value="To buy something, use `/buy`!", inline=False)

    page8 = disnake.Embed(title="Anarith Market", colour=disnake.Colour(0xc0c0fb), description="Welcome to Anarith, the biggest hub of shops in the town! To navigate, use the dropdown!")

    page8.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")
    page8.set_footer(text="Take a look around.", icon_url=inter.author.avatar.url)

    page8.add_field(name="**<:titles:922568821624147999> Titles <:titles:922568821624147999>**", value="** **", inline=False)
    page8.add_field(name=f"The Chaotic <:titles:922568821624147999>**| 999** <:silvers:889667891044167680>", value=f"Allows you to equip `The Chaotic` title", inline=False)
    page8.add_field(name="** **", value="To buy something, use `/buy`!", inline=False)

    class Dropdown(disnake.ui.Select):
        def __init__(self):

            # Set the options that will be presented inside the dropdown
            options = [
                disnake.SelectOption(
                    label="Daily Deals", description="Check out the daily deals", value="p1"
                ),
                disnake.SelectOption(
                    label="Shards Pg. 1", description="First page for shards", value="p2"
                ),
                disnake.SelectOption(
                    label="Shards Pg.2", description="Second page for shards", value="p3"
                ),
                disnake.SelectOption(
                    label="Shards Pg.3", description="Third page for shards", value="p4"
                ),
                disnake.SelectOption(
                    label="Titles Pg. 1", description="First page for titles", value="p5"
                ),
                disnake.SelectOption(
                    label="Titles Pg. 2", description="Second page for titles", value="p6"
                ),
                disnake.SelectOption(
                    label="Titles Pg. 3", description="Third page for titles", value="p7"
                ),
                disnake.SelectOption(
                    label="Titles Pg. 4", description="Fourth page for titles", value="p8"
                ),
            ]

            # The placeholder is what will be shown when no option is chosen
            # The min and max values indicate we can only pick one of the three options
            # The options parameter defines the dropdown options. We defined this above
            super().__init__(
                placeholder="Page",
                min_values=1,
                max_values=1,
                options=options,
            )

        async def callback(self, interaction: disnake.MessageInteraction):
            e = self.values[0]

            emb = None

            if (e == "p1"):
                emb = copy.copy(page1)
            if (e == "p2"):
                emb = copy.copy(page2)
            if (e == "p3"):
                emb = copy.copy(page3)
            if (e == "p4"):
                emb = copy.copy(page4)
            if (e == "p5"):
                emb = copy.copy(page5)
            if (e == "p6"):
                emb = copy.copy(page6)
            if (e == "p7"):
                emb = copy.copy(page7)
            if (e == "p8"):
                emb = copy.copy(page8)

            #r.children[int(e.replace("p", ""))].default = True

            await interaction.response.edit_message(embed=emb, view=DropdownView())

    class DropdownView(disnake.ui.View):
        def __init__(self):
            super().__init__()

            self.add_item(Dropdown())

    await inter.response.send_message(embed=page1, view=DropdownView())

@commands.guild_only()
@bot.slash_command(
    name="buy",
    description="Buy an item from the shop!",
    options=[
        Option("item", "The item you want to buy", OptionType.string, True),
        Option("amount", "How many of them you want to buy", OptionType.integer, False)
    ],
)
async def buy(inter:disnake.ApplicationCommandInteraction, item=None, amount=None):
    if (amount == None):
        amount = 1

    if (item.lower() not in store):
        await inter.response.send_message("Not in the store!", ephemeral=True)
        return

    if (str(inter.author.id) not in cur):
        cur[str(inter.author.id)] = 0
    if (str(inter.author.id) not in inv):
        inv[str(inter.author.id)] = {"titles" : ["The Townie"]}

    thing = store[item.lower()]
    
    price = thing['cost']
    if (thing['dailydeal'] == True):
        price = 24 * amount
    else:
        if ("<:titles:922568821624147999>" in thing['title']):
            amount = 1

        price = price * amount
    bal = cur[str(inter.author.id)]

    if (item.lower() == 'cop'):
        embed = disnake.Embed(title=f"**Cop Shard <:copshard:889672912905322516>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Cop <:copshard:924295242566467584>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896804869820801115.png?size=80")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar.url)
    elif (item.lower() == 'doctor'):
        embed = disnake.Embed(title=f"**Doctor Shard <:docicon2:890333203959787580>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Doctor <:docicon2:890333203959787580>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896576968756191273.png?size=96")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar.url) 
    elif (item.lower() == "enforcer"):
        embed = disnake.Embed(title=f"**Enforcer Shard <:enficon2:890339050865696798>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Enforcer <:enficon2:890339050865696798>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896576814942670899.png?size=96")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar.url) 
    elif (item.lower() == 'lookout'):
        embed = disnake.Embed(title=f"**Lookout Shard <:consshard:924299559168008222>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Lookout <:loicon2:889673190392078356>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896577050645786655.png?size=96")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar.url) 
    elif (item.lower() == 'detective'):
        embed = disnake.Embed(title=f"**Detective Shard <:deticon2:889673135438319637>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Detective <:deticon2:889673135438319637>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896760012729356331.png?size=44")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar.url) 
    elif (item.lower() == 'consort'):
        embed = disnake.Embed(title=f"**Consort Shard <:consshard:924299559168008222>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Consort <:consshard:924299559168008222>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896823151307157535.png?size=80")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar.url) 
    elif (item.lower() == 'mayor'):
        embed = disnake.Embed(title=f"**Mayor Shard <:mayorshard:924300251869888552>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Mayor <:mayorshard:924300251869888552>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/897570664209338369.png?size=80")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar.url) 
    elif (item.lower() == 'psychic'):
        embed = disnake.Embed(title=f"**Psychic Shard <:psyshard:924298902058987540>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Psychic <:psyshard:924298902058987540>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896842380618108938.png?size=80")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar.url)
    elif (item.lower() == 'framer'):
        embed = disnake.Embed(title=f"**Framer Shard <:frameshard:924299361565966406>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Framer <:frameshard:924299361565966406>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896910673370558464.png?size=80")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar.url) 
    elif (item.lower() in 'consigliere'):
        embed = disnake.Embed(title=f"**Consigliere Shard <:consigshard:924295501795446844>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Consigliere <:consigshard:924295501795446844>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896910618051878982.png?size=80")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar.url) 
    elif (item.lower() == 'jester'):
        embed = disnake.Embed(title=f"**Jester Shard <:jestshard:923933880833146910>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Jester <:jestshard:923933880833146910>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896900933307469875.png?size=80")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar.url) 
    elif (item.lower() == 'headhunter' or item.lower() == 'hh'):
        embed = disnake.Embed(title=f"**Headhunter Shard <:hhshard:923934411219681361>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Headhunter <:hhshard:923934411219681361>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896903989285777428.png?size=80msp")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar.url)  
    elif (item.lower() == 'mafioso' or item.lower() == 'maf'):
        embed = disnake.Embed(title=f"**Mafioso Shard <:mafshard:923934147402162227>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Mafioso <:mafshard:923934147402162227>** by x3.")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896801052945449031.png?size=80")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar.url)  
    elif (item.lower() == 'interrogator' or item.lower() == 'the interrogator'):
        embed = disnake.Embed(title=f"** The Interrogator <:titles:922568821624147999>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="Allows you to equip `The Interrogator` title")

        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar.url)  
    elif (item.lower() == 'confused' or item.lower() == 'the confused'):
        embed = disnake.Embed(title=f"** The Confused <:titles:922568821624147999>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="Allows you to equip `The Confused` title")

    
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar.url)  
    elif (item.lower() == 'hero' or item.lower() == 'the hero'):
        embed = disnake.Embed(title=f"** The Hero <:titles:922568821624147999>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="Allows you to equip `The Hero` title")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar.url)
    elif (item.lower() == 'slayer' or item.lower() == 'the slayer'):
        embed = disnake.Embed(title=f"** The Slayer <:titles:922568821624147999>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="Allows you to equip `The Slayer` title")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar.url)  
    elif (item.lower() == 'sheep' or item.lower() == 'the sheep'):
        embed = disnake.Embed(title=f"** The Sheep <:titles:922568821624147999>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="Allows you to equip `The Sheep` title")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar.url)  
    elif (item.lower() == 'vetran' or item.lower() == 'the vetran'):
        embed = disnake.Embed(title=f"** The Vetran <:titles:922568821624147999>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="Allows you to equip `The Vetran` title")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar.url)  
    elif (item.lower() == 'paranoid' or item.lower() == 'the paranoid'):
        embed = disnake.Embed(title=f"** The Paranoid <:titles:922568821624147999>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="Allows you to equip `The Paranoid` title")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar.url)  
    elif (item.lower() == 'fool' or item.lower() == 'the fool'):
        embed = disnake.Embed(title=f"** The Fool <:titles:922568821624147999>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="Allows you to equip `The Fool` title")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar.url)  
    elif (item.lower() == 'nightmare' or item.lower() == 'the nightmare'):
        embed = disnake.Embed(title=f"** The Nightmare <:titles:922568821624147999>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="Allows you to equip `The Nightmare` title")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar.url)  
    elif (item.lower() == 'chaotic' or item.lower() == 'the chaotic'):
        embed = disnake.Embed(title=f"** The Chaotic <:titles:922568821624147999>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="WHAT IS THIS????!!!!1!!11!!!1!")
        embed.set_footer(text="Click to confirm your purchase.", icon_url=inter.author.avatar.url)  

    class Buttons(disnake.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
            self.value = None

        @disnake.ui.button(label="Yes", style=disnake.ButtonStyle.green)
        async def confirm(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
            self.value = True
            await interaction.response.pong()
            self.stop()

        # This one is similar to the confirmation button except sets the inner value to `False`
        @disnake.ui.button(label="No", style=disnake.ButtonStyle.grey)
        async def cancel(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
            self.value = False
            await interaction.response.pong()
            self.stop()

    b = Buttons()
    await inter.response.send_message(embed=embed, view=b)

    await b.wait()


    if (b.value):
        if (price * amount > bal):
            embed = disnake.Embed(title="You don't have enough silvers", colour=disnake.Colour(0xad1414), description=f"You only have **{str(bal)} <:silvers:889667891044167680>**.")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889667891044167680.png?size=96")
            embed.set_footer(text="Better get more money.", icon_url=inter.author.avatar.url)
            await inter.response.send_message(embed=embed)
        else:
            cur[str(inter.author.id)] -= price * amount
            try:
                cur["bank"]
            except:
                cur["bank"] = 0

            cur["bank"] += price * amount

            e = "The " + string.capwords(item).replace("The ", "")
            if (e in inv[str(inter.author.id)]["titles"]):
                await inter.followup.send("Fuck you :') (Oh, and by the way, your punishment is getting scammed", ephemeral=True)

            if (item.lower() == 'cop'):
                embed = disnake.Embed(title=f"**Cop Shard <:copshard:924295242566467584>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb8ff49), description="This shard increases your chance of rolling **Cop** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889672912905322516.png?size=96")
                embed.set_footer(text=f"Thank you for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar.url)
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
                embed = disnake.Embed(title=f"**Doctor Shard <:docicon2:890333203959787580>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Doctor <:docicon2:890333203959787580>** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896576968756191273.png?size=96")
                embed.set_footer(text=f"Thank you for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar.url)
                
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
                embed = disnake.Embed(title=f"**Enforcer Shard <:enficon2:890339050865696798>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Enforcer <:enficon2:890339050865696798>** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896576814942670899.png?size=96")
                embed.set_footer(text=f"Thank you for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar.url)
                
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
                embed = disnake.Embed(title=f"**Lookout Shard <:loicon2:889673190392078356>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Lookout <:loicon2:889673190392078356>** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896577050645786655.png?size=96")
                embed.set_footer(text=f"Thank you for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar.url)
                
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
                embed = disnake.Embed(title=f"**Detective Shard <:deticon2:889673135438319637>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Detective <:deticon2:889673135438319637>** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896760012729356331.png?size=44")
                embed.set_footer(text=f"Thank you for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar.url)
                
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
                embed = disnake.Embed(title=f"**Consort Shard <:consshard:924299559168008222>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Consort <:consshard:924299559168008222>** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896823151307157535.png?size=80")
                embed.set_footer(text=f"Thank you for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar.url)
                
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
                embed = disnake.Embed(title=f"**Mayor Shard <:mayorshard:924300251869888552>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Mayor <:mayorshard:924300251869888552>** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/897570664209338369.png?size=80")
                embed.set_footer(text=f"Thank you for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar.url)
                
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
                embed = disnake.Embed(title=f"**Psychic Shard <:psyshard:924298902058987540>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Psychic <:psyshard:924298902058987540>** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896842380618108938.png?size=80")
                embed.set_footer(text=f"Thank you for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar.url)
                
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
                embed = disnake.Embed(title=f"**Framer Shard <:frameshard:924299361565966406>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Framer <:frameshard:924299361565966406>** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896910673370558464.png?size=80")
                embed.set_footer(text=f"Thank you for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar.url)
                
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
                embed = disnake.Embed(title=f"**Consigliere Shard <:consigshard:924295501795446844>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Consigliere <:consigshard:924295501795446844>** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896910618051878982.png?size=80")
                embed.set_footer(text=f"Thank you for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar.url)
                
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
                embed = disnake.Embed(title=f"**Jester Shard <:jestshard:923933880833146910>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Jester <:jestshard:923933880833146910>** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896900933307469875.png?size=80")
                embed.set_footer(text=f"Thank you for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar.url)
                
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
                embed = disnake.Embed(title=f"**Headhunter Shard <:hhshard:923934411219681361>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Headhunter <:hhshard:923934411219681361>** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896903989285777428.png?size=80msp")
                embed.set_footer(text=f"Thank you for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar.url)
                
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
                embed = disnake.Embed(title=f"**Mafioso Shard <:mafshard:923934147402162227>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="This shard increases your chance of rolling **Mafioso <:mafshard:923934147402162227>** by x3.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896801052945449031.png?size=80")
                embed.set_footer(text=f"Thank you for your purchase! | Cost: {str(price * amount)})", icon_url=inter.author.avatar.url)
                
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
            elif (item.lower() == "interrogator" or item.lower() == "the interrogator"):
                embed = disnake.Embed(title=f"** The Interrogator <:titles:922568821624147999>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="Allows you to equip `The Interrogator` title")

               
                embed.set_footer(text="Thank you for your purchase!", icon_url=inter.author.avatar.url)  
                
                try:
                    inv[str(inter.author.id)]["titles"]
                except:
                    inv[str(inter.author.id)]["titles"] = ["The Townie"]

                inv[str(inter.author.id)]["titles"].append("The Interrogator")
            elif (item.lower() == "confused" or item.lower() == "the confused"):
                embed = disnake.Embed(title=f"** The Confused <:titles:922568821624147999>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="Allows you to equip `The Confused` title")

      
                embed.set_footer(text="Thank you for your purchase!", icon_url=inter.author.avatar.url)  
                
                try:
                    inv[str(inter.author.id)]["titles"]
                except:
                    inv[str(inter.author.id)]["titles"] = ["The Townie"]

                inv[str(inter.author.id)]["titles"].append("The Confused")
            elif (item.lower() == "hero" or item.lower() == "the hero"):
                embed = disnake.Embed(title=f"**The Hero <:titles:922568821624147999>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="Allows you to equip `The Hero` title")

                
                embed.set_footer(text="Thank you for your purchase!", icon_url=inter.author.avatar.url)  
                
                try:
                    inv[str(inter.author.id)]["titles"]
                except:
                    inv[str(inter.author.id)]["titles"] = ["The Townie"]

                inv[str(inter.author.id)]["titles"].append("The Hero")
            elif (item.lower() == "slayer" or item.lower() == "the slayer"):
                embed = disnake.Embed(title=f"**The Slayer <:titles:922568821624147999>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="Allows you to equip `The Slayer` title")
                embed.set_footer(text="Thank you for your purchase!", icon_url=inter.author.avatar.url)  
                try:
                    inv[str(inter.author.id)]["titles"]
                except:
                    inv[str(inter.author.id)]["titles"] = ["The Townie"]
                inv[str(inter.author.id)]["titles"].append("The Slayer")
            elif (item.lower() == "sheep" or item.lower() == "the sheep"):
                embed = disnake.Embed(title=f"**The Sjeep <:titles:922568821624147999>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="Allows you to Sheep `The Hero` title")
                embed.set_footer(text="Thank you for your purchase!", icon_url=inter.author.avatar.url)  
                try:
                    inv[str(inter.author.id)]["titles"]
                except:
                    inv[str(inter.author.id)]["titles"] = ["The Townie"]
                inv[str(inter.author.id)]["titles"].append("The Sheep")
            elif (item.lower() == "vetran" or item.lower() == "the vetran"):
                embed = disnake.Embed(title=f"**The Vetran <:titles:922568821624147999>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="Allows you to equip `The Vetran` title")
                embed.set_footer(text="Thank you for your purchase!", icon_url=inter.author.avatar.url)  
                try:
                    inv[str(inter.author.id)]["titles"]
                except:
                    inv[str(inter.author.id)]["titles"] = ["The Townie"]
                inv[str(inter.author.id)]["titles"].append("The Vetran")
            elif (item.lower() == "paranoid" or item.lower() == "the paranoid"):
                embed = disnake.Embed(title=f"**The Paranoid <:titles:922568821624147999>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="Allows you to equip `The Paranoid` title")
                embed.set_footer(text="Thank you for your purchase!", icon_url=inter.author.avatar.url)  
                try:
                    inv[str(inter.author.id)]["titles"]
                except:
                    inv[str(inter.author.id)]["titles"] = ["The Townie"]
                inv[str(inter.author.id)]["titles"].append("The Paranoid")
            elif (item.lower() == "fool" or item.lower() == "the fool"):
                embed = disnake.Embed(title=f"**The Fool <:titles:922568821624147999>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="Allows you to equip `The Fool` title")
                embed.set_footer(text="Thank you for your purchase!", icon_url=inter.author.avatar.url)  
                try:
                    inv[str(inter.author.id)]["titles"]
                except:
                    inv[str(inter.author.id)]["titles"] = ["The Townie"]
                inv[str(inter.author.id)]["titles"].append("The Fool")
            elif (item.lower() == "chaotic" or item.lower() == "the chaotic"):
                embed = disnake.Embed(title=f"**The Chaotic <:titles:922568821624147999>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="Allows you to equip `The Chaotic` title")
                embed.set_footer(text="Thank you for your purchase!", icon_url=inter.author.avatar.url)  
                try:
                    inv[str(inter.author.id)]["titles"]
                except:
                    inv[str(inter.author.id)]["titles"] = ["The Townie"]
                inv[str(inter.author.id)]["titles"].append("The Chaotic")
            elif (item.lower() == "nightmare" or item.lower() == "the nightmare"):
                embed = disnake.Embed(title=f"**The Nightmare <:titles:922568821624147999>** | {price} <:silvers:889667891044167680>", colour=disnake.Colour(0xb9c9ff), description="Allows you to equip `The Nightmare` title")
                embed.set_footer(text="Thank you for your purchase!", icon_url=inter.author.avatar.url)  
                try:
                    inv[str(inter.author.id)]["titles"]
                except:
                    inv[str(inter.author.id)]["titles"] = ["The Townie"]
                inv[str(inter.author.id)]["titles"].append("The Nightmare")

            await inter.followup.send(embed=embed, username="AMOGUS", avatar_url="https://i.kym-cdn.com/photos/images/newsfeed/001/944/128/515.jpg")

            with open('data.json', 'w') as jsonf:
                json.dump(cur, jsonf)
            with open('inv.json', 'w') as jsonf:
                json.dump(inv, jsonf)
    else:
        await inter.followup.send("Canceled...", username="AMOGUS", ephemeral=True, avatar_url="https://i.kym-cdn.com/photos/images/newsfeed/001/944/128/515.jpg")

@commands.guild_only()
@bot.slash_command(
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
        embed = disnake.Embed(title="You have no item equipped", colour=disnake.Colour(0x50e3c2), description="*If you're trying to unequip a title, use* `/equip townie`.")
        await inter.response.send_message(embed=embed, ephemeral=True)

    thin = inv[str(inter.author.id)][guilds[str(inter.author.id)]["equipped"]]["title"]
    em = var[inter.guild.id]["itememoji"][thin]
    theid = re.sub("[^0-9]", "", em)

    embed = disnake.Embed(title="**You have unequipped your item**", colour=disnake.Colour(0xff1b1f))

    embed.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{theid}.png?size=96")
    embed.set_footer(text="Rip", icon_url=inter.author.avatar.url)
    await inter.response.send_message(embed=embed, ephemeral=True)

    guilds[str(inter.author.id)]["equipped"] = None

    with open('guilds.json', 'w') as jsonf:
        json.dump(guilds, jsonf)

@commands.guild_only()
@bot.slash_command(
    name="guessgame",
    description="Guess a number!",
    guild_ids=[913544429703405608]
)
async def guessgame(inter:ApplicationCommandInteraction):
    answer = random.randint(1, 10)
    players = []
    players.append(inter.author)
    p1answer = 0
    p2answer = 0

    class Buttons(disnake.ui.View):
        def __init__(self):
            super().__init__()
            self.value=None
    
        @disnake.ui.button(label="1 Player", style=ButtonStyle.blurple, emoji="🧍")
        async def onep(self, button, interaction):
            if (interaction.author != inter.author):
                await interaction.followup.send("No.", ephemeral=True)
                return
            self.value="1"
            self.stop()

        @disnake.ui.button(label="2 Player", style=ButtonStyle.blurple, emoji="🧑‍🤝‍🧑")
        async def twop(self, button, interaction):
            if (interaction.author != inter.author):
                await interaction.followup.send("No.", ephemeral=True)
                return
            self.value="2"
            self.stop()
    
    view = Buttons()

    embed = disnake.Embed(title="Guessing Game", colour=disnake.Colour(0x4a90e2), description="There is a number randomly generated from 1 to 10. Try to correctly guess the number to win!\n\nFor now, lets decide how many players are in the game.")

    embed.set_footer(text="Click a button as your input.", icon_url=inter.author.avatar.url)
    await inter.response.send_message(embed=embed, view=view)
    await view.wait()

    newview = disable_buttons(view)
    await inter.edit_original_message(view=newview)



    if (view.value == "2"):
        class Join(disnake.ui.View):
            def __init__(self):
                super().__init__()
                self.player=None
        
            @disnake.ui.button(label="Join", style=ButtonStyle.green, emoji="👋")
            async def onep(self, button, interaction):
                if (interaction.author == inter.author):
                    return
                self.value = interaction.author
                self.stop()

        embed = disnake.Embed(title="Who's the second player?", colour=disnake.Colour(0x4a90e2), description="To play with two players, you have to have another player to play with! The second player will have to click the \"Join\" button at the bottom of this message.")
        embed.set_footer(text="Click `Join`.", icon_url=inter.author.avatar.url)

        view = Join()

        await inter.followup.send(embed=embed, view=view)
        await view.wait()
        
        newview = disable_buttons(view)
        await inter.edit_original_message(view=newview)

        players.append(view.value)

        embed = disnake.Embed(title=f"{players[0].name} (Player 1), its your turn!", colour=disnake.Colour(0x4a90e2), description="It's time to guess the number! You can guess by sending a message in chat.")

        embed.set_footer(text="Send a message as your input.", icon_url=players[0].avatar.url)
        await inter.followup.send(embed=embed)
        
        def check(m):
            return m.author == players[0]

        def closest(lst, number):
            return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-number))]

        try:
            message = await bot.wait_for("message", check=check, timeout=60)
            p1answer = int(message.content)

            embed = disnake.Embed(title=f"{players[1].name} (Player 2), its your turn!", colour=disnake.Colour(0x4a90e2), description="It's time to guess the number! You can guess by sending a message in chat.")
            embed.set_footer(text="Send a message as your input.", icon_url=players[1].avatar.url)

            await inter.followup.send(embed=embed)

            try:

                message = await bot.wait_for("message", check=check, timeout=60)
                p2answer = int(message.content)

                answerList:dict = {players[0]: p1answer, players[1]: p2answer}
                winnernumber = closest(answerList.values(), answer)

                def get_key(val):
                    for key, value in answerList.items():
                        if (val == value):
                            return key

                embed = disnake.Embed(title=f"{get_key(winnernumber).name} wins!", colour=disnake.Colour(0x4a90e2), description="The number was...\n\n")

                embed.set_footer(text="Congratulations!", icon_url=inter.author.avatar.url)

                embed.add_field(name="Answer", value=answer)
                embed.add_field(name=f"{players[0].name}'s Answer", value=str(p1answer))
                embed.add_field(name=f"{players[1].name}'s Answer", value=str(p2answer))

                await inter.followup.send(embed=embed)


                
            except asyncio.TimeoutError:
                embed = disnake.Embed(title=f"The command timed out.", colour=disnake.Colour(0x4a90e2), description="Try running the command again.")

                embed.set_footer(text="Try running the command again.", icon_url=players[0].avatar.url)
                await inter.followup.send(embed=embed)
                return
        except asyncio.TimeoutError:
            embed = disnake.Embed(title=f"The command timed out.", colour=disnake.Colour(0x4a90e2), description="Try running the command again.")

            embed.set_footer(text="Try running the command again.", icon_url=players[0].avatar.url)
            await inter.followup.send(embed=embed)
            return
        except:
            embed = disnake.Embed(title=f"There was an invalid input.", colour=disnake.Colour(0x4a90e2), description="Try running the command again.")

            embed.set_footer(text="Try running the command again.", icon_url=players[0].avatar.url)
            await inter.followup.send(embed=embed)
            return
    else:

        def check(m):
            return m.author.id == players[0].id
        embed = disnake.Embed(title=f"{players[0].name}, its time to go!", colour=disnake.Colour(0x4a90e2), description="It's time to guess the number! You can guess by sending a message in chat.")

        embed.set_footer(text="Send a message as your input.", icon_url=players[0].avatar.url)
        await inter.followup.send(embed=embed)
        message = await bot.wait_for("message", check=check)


        embed = disnake.Embed(title="The answer was...", colour=disnake.Colour(0x4a90e2), description=str(answer))

        embed.set_footer(text="Cool!", icon_url=inter.author.avatar.url)


def disable_buttons(view: disnake.ui.View):
    for child in view.children:
        if isinstance(child, disnake.ui.Button):
            child.disabled = True

    return view




@commands.guild_only()
@bot.slash_command(
    name="equip",
    description="Equip an item from your inventory",
    options=[
        Option("item", "The item you want to equip", OptionType.string, True)
    ],
)
async def equip(inter, item=None):
    if (str(inter.author.id) not in inv):
        inv[str(inter.author.id)] = {}

    realitem = item.lower().replace(" ", "")
    
    e = "the " + item.lower()
    e = demoji.replace(e, "")
    e = e.strip()
    titles = []
    for i in inv[str(inter.author.id)]["titles"]:
        titles.append(re.sub(r'[^a-zA-Z0-9]', ' ', i.lower()).strip())

    if (realitem not in inv[str(inter.author.id)] and e not in titles):
        await inter.response.send_message("That item isn't in your inventory...", ephemeral=True)
        return

    try:
        if (inv[str(inter.author.id)][realitem]["usable"] == False):
                await inter.response.send_message("That item isn't usable...", ephemeral=True)
                return
    except:
        pass

    
    def getThing(thing:str):
        for i in inv[str(inter.author.id)]["titles"]:
            if (thing in i.lower()):
                return thing

    tbetitle = getThing(item.lower())


    title = e not in titles

    try:
        var[inter.guild.id]["test"]
    except:
        var[inter.guild.id] = copy.deepcopy(temp)

    try:
        guilds[str(inter.author.id)]
    except:
        guilds[str(inter.author.id)] = {"guild" : 0, "joinedgame" : False, "equipped" : None, "title" : ""}

    try:
        guilds[str(inter.author.id)]["title"]
    except:
        guilds[str(inter.author.id)]["title"] = ""

    theid = ""
    theitem = ""
    emoji = ""
    if (title):
        theitem = inv[str(inter.author.id)][realitem]["title"]
        emoji = var[inter.guild.id]["itememoji"][theitem]

        theid = re.sub("[^0-9]", "", emoji)
    else:
   
        theitem = string.capwords(realitem)
        theid = "914621157154639923"


    embed = disnake.Embed(title=f"**You have equipped __{theitem} {emoji}__**!", colour=disnake.Colour(0x8aa0ff))

    embed.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{theid}.png?size=96")
    embed.set_footer(text="Have fun!", icon_url=inter.author.avatar.url)
    await inter.response.send_message(embed=embed, ephemeral=True)

    if (title):
        guilds[str(inter.author.id)]["equipped"] = realitem
    else:
        guilds[str(inter.author.id)]["title"] = tbetitle
    
    with open('guilds.json', 'w') as jsonf:
        json.dump(guilds, jsonf)

@commands.guild_only()
@bot.slash_command(
    name="achievements",
    description="View achievements",
    guild_ids=[753967387149074543]
)
async def ach(inter):
    await inter.response.defer()
    achievementembed = disnake.Embed(title=f"**{inter.author.name}'s Achievements**", colour=disnake.Colour(0xe3fff2))

    achievementembed.set_thumbnail(url=inter.author.avatar.url)

    achievementembed.add_field(name=f"**Achievements Unlocked :trophy:**", value="** **", inline=False)

    try:
        guilds[str(inter.author.id)]["achivements"]
    except:
        guilds[str(inter.author.id)]["achivements"] = []

    e = False

    for i in guilds[str(inter.author.id)]["achivements"]:
        e = True
        achievement = Achievement.getAchById(i)
        achievementembed.add_field(name=f"**{achievement.name}**", value="**{0}**".format(achievement.description))
    
    if (e != True):
        achievementembed.add_field(":x: **None**", value="** **", inline=False)

    achievementembed.add_field(name=f"**Locked Achievements :x:**", value="** **", inline=False)
    
    e = False
    for i in achivements:
        if (i.id in guilds[str(inter.author.id)]["achivements"] or i.hidden == True or i.obtainable == False):
            continue

        e = True            
        achievementembed.add_field(f"**{i.name}**", value=f"**{i.description}**", inline=False)

    for i in achivements:
        if (i.id in guilds[str(inter.author.id)]["achivements"] or i.hidden != True or i.obtainable == False):
            continue

        e = True            
        achievementembed.add_field(f"**???**", value=f"**???**", inline=False)

    if (e == False):
        achievementembed.add_field(":trophy: You've unlocked all the achievements!", inline=False)
    
    await inter.edit_original_message(embed=achievementembed)


@commands.guild_only()
@bot.slash_command(
    name="inv",
    description="Check your inventory"
)
async def inventory(inter):
    try:
        var[inter.guild.id]["test"]
    except:
        var[inter.guild.id] = copy.deepcopy(temp)

        if (str(inter.author.id) not in inv):
            inv[str(inter.author.id)] = {"titles" : ["The Townie"]}

    embed = disnake.Embed(title=f"**{inter.author.name}'s Inventory**", colour=disnake.Colour(0xe3fff2))

    embed.set_thumbnail(url=inter.author.avatar.url)

    try:
        thin = inv[str(inter.author.id)][guilds[str(inter.author.id)]["equipped"]]["title"]
        em = var[inter.guild.id]["itememoji"][thin]
        embed.add_field(name=f"**Currently Equipped: {thin} {em}**", value="** **", inline=False)
    except:
        embed.add_field(name=f"**Currently Equipped: None**", value="** **", inline=False)

    for key, value in inv[str(inter.author.id)].items():
        try:
            if (key.lower() != "titles"):
                r = value["title"]
                eh = var[inter.guild.id]["itememoji"][r]
                e = str(value["amount"])
                if (e != "0"):
                    embed.add_field(name=f"{r} {eh} x{e}", value=value["description"], inline=False)
        except:
            if (key.lower() != "titles"):
                e = str(value["amount"])
                r = value["title"]
                if (e != "0"):
                    embed.add_field(name=f"{r} :grey_question: x{e}", value=value["description"], inline=False)

    titleass = disnake.Embed(title=f"**{inter.author.name}'s Inventory**", colour=disnake.Colour(0xe3fff2))

    titleass.set_thumbnail(url=inter.author.avatar.url)

    titleass.add_field(name=f"**Titles <:titles:922568821624147999>**", value="** **", inline=False)

    try:
        inv[str(inter.author.id)]["titles"]
        guilds[str(inter.author.id)]["title"] = "The Townie"
        for i in inv[str(inter.author.id)]["titles"]:
            titleass.add_field(name=f"{i} <:titles:922568821624147999>", value="** **", inline=False)
    except:
        inv[str(inter.author.id)]["titles"] = ["The Townie"]
        guilds[str(inter.author.id)]["title"] = "The Townie"
        for i in inv[str(inter.author.id)]["titles"]:
            titleass.add_field(name=f"{i} <:titles:922568821624147999>", value="** **", inline=False)


    achievements = disnake.Embed(title=f"**{inter.author.name}'s Inventory**", colour=disnake.Colour(0xe3fff2))

    achievements.set_thumbnail(url=inter.author.avatar.url)
    achievements.set_footer(text="To view all achievements, use /achievements")

    achievements.add_field(name=f"**Achievements :trophy:**", value="** **", inline=False)

    try:
        guilds[str(inter.author.id)]["achivements"]
    except:
        guilds[str(inter.author.id)]["achivements"] = []

    e = False

    for i in guilds[str(inter.author.id)]["achivements"]:
        e = True
        achievement = Achievement.getAchById(i)
        achievements.add_field(name=f"**{achievement.name}**", value="**{0}**".format(achievement.description))
    
    if (e != True):
        achievements.add_field(":x: **None**", value="** **")

    class Dropdown(disnake.ui.Select):
        def __init__(self):

            # Set the options that will be presented inside the dropdown
            options = [
                disnake.SelectOption(
                    label="Shards", description="Check out your shards", value="p1"
                ),
                disnake.SelectOption(
                    label="Titles", description="Check out your titles", value="p2"
                ),
                disnake.SelectOption(
                    label="Achievements", description="Check out your achievements", value="p3"
                )
            ]

            # The placeholder is what will be shown when no option is chosen
            # The min and max values indicate we can only pick one of the three options
            # The options parameter defines the dropdown options. We defined this above
            super().__init__(
                placeholder="Page",
                min_values=1,
                max_values=1,
                options=options,
            )

        async def callback(self, interaction: disnake.MessageInteraction):
            e = self.values[0]

            emb = None

            if (e == "p1"):
                emb = copy.copy(embed)
            if (e == "p2"):
                emb = copy.copy(titleass)
            if (e == "p3"):
                emb = copy.copy(achievements)

            #r.children[int(e.replace("p", ""))].default = True

            await interaction.response.edit_message(embed=emb, view=DropdownView())

    class DropdownView(disnake.ui.View):
        def __init__(self):
            super().__init__()

            self.add_item(Dropdown())

    embed.add_field(name="**Use the dropdown to navigate your inventory!**", value="** **", inline=False)
    await inter.response.send_message(embed=embed, view=DropdownView())

    with open('data.json', 'w') as jsonf:
        json.dump(cur, jsonf)

#actual game stuff happening

@bot.slash_command(
    name="guide",
    description="How to play Anarchic"
)
async def info(inter):
    embed = disnake.Embed(title="**How to get started with Anarchic**", colour=disnake.Colour(0x86b4b6), description="In this guide you will be learning how to get started in Anarchic, so let's get to it! We have a party system in Anarchic for the game to begin so you have to run `/join` to join the party. If the party leader thinks they have enough players, they start the game with `/start`!")

    # embed.set_image(url="https://cdn.discordapp.com/embed/avatars/0.png")
    embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/zvBfC-Hei3zC-NkTa_MJ1t-lx4Fu6dXoB-5uzicvPYE/https/images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%253Fwidth%253D468%2526height%253D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")
    embed.set_footer(text="Have fun", icon_url=inter.author.avatar.url)

    embed.add_field(name="🔹 You need a minimum of 5 players to start the game!", value="** **", inline=False)
    embed.add_field(name="Anarchic also offers different modes in our bot, those modes are : ", value="**:triangular_flag_on_post: Classic (5 players)\n<:enficon2:890339050865696798> Enforced (5 players)\n<:hhicon2:891429754643808276> Execution (6 players)\n<:consicon2:890336628269281350> Duet (7 players)\n<:frameicon2:890365634913902602> Framed (7 players)\n<:consigicon2:896154845130666084> Truth (7 players)\n:sparkles: Legacy (8 players)\n:diamond_shape_with_a_dot_inside: Scattered (9 players)\n:drop_of_blood: Anarchy (10 players)\n:star2: Ranked (10 players)**\n\nYou can run the /setups command to view these, to set the mode to a desired setup run the /setup command. And you can run the /party command after changing the setup to view the roles in the mode!", inline=False)
    embed.add_field(name="Other important commands for the game:", value="🔹 `/leave`  to leave the party, if the leader leaves the second person becomes the leader\n🔹 `/clear` to clear the party if the party is filled with AFKs\n🔹 `/kick` to kick an AFK player from the party, can only be done by the party leader\n🔹 `/help` to view the list of commands", inline=False)
    await inter.response.send_message(embed=embed)

@commands.guild_only()
@bot.slash_command(
    name="role",
    description="Get info on a role",
    options=[
        Option("role", "Choose a role to get info from", OptionType.string, True)
    ]
)
async def role(inter:ApplicationCommandInteraction, role:str):
    try:
        var[inter.guild.id]["test"]
    except:
        var[inter.guild.id] = copy.deepcopy(temp)

    if (string.capwords(role) not in var[inter.guild.id]["roles"]):
        await inter.response.send_message("That's not a role!", ephemeral=True)
        return

    embed = await bootyfulembed(role.lower(), inter.author)
    await inter.response.defer()

    await inter.edit_original_message(embed=embed)


@commands.guild_only()
@bot.slash_command(
    name="whisper",
    description="Whisper to a player",
    options=[
        Option("member", "Who you wanna whipser to", OptionType.user, True),
        Option("message", "The message", OptionType.string, True)
    ]
)
async def whisper(inter:ApplicationCommandInteraction, member:disnake.User, message:str):
    try:
        var[inter.guild.id]["test"]
    except:
        var[inter.guild.id] = copy.deepcopy(temp)
    await inter.response.defer(ephemeral=True)

    try:
        Player.get_player(member.id, var[inter.guild.id]["playerdict"]).role
    except:
        await inter.edit_original_message(content="That's an invalid member.")
        return

    if (inter.author.id not in var[inter.guild.id]["players"]):
        await inter.edit_original_message(content="You're not in the game.")
        return
    if (var[inter.guild.id]["started"] == False):
        await inter.edit_original_message(content="The game hasn't started yet.")
        return
    if (Player.get_player(inter.author.id, var[inter.guild.id]["playerdict"]).dead == True):
        await inter.edit_original_message(content="You're dead.")
        return
    if (inter.channel != var[inter.guild.id]["channel"]):
        chan = var[inter.guild.id]["channel"].mention
        await inter.edit_original_message(content=f"Try using this command again in {chan}.")
        return
    if (var[inter.guild.id]["night"] == True):
        await inter.edit_original_message(content="You can only whisper during the day.")
        return

    embed = disnake.Embed(title=f"**{inter.author.name} has whispered to you <:whisper:917131981895127040>**", description=f"**{message}**", colour=disnake.Colour(0xcce0ff))

    embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/917129470064853012/whisper.png?width=482&height=482")
    embed.set_footer(text="Use `/whisper` to whisper", icon_url=inter.author.avatar.url)
    await member.send(embed=embed)

    embed.title = f"**You have whispered to {member.name} <:whisper:917131981895127040>**"

    await inter.edit_original_message(embed=embed)
    embed.title = f"**{inter.author.name} is whispering to {member.name}**"
    embed.description= "** **"
    await inter.channel.send(embed=embed)


@commands.guild_only()
@bot.slash_command(
    name="promote",
    description="Give your epicly awesome gamehosting powers to a friend of yours",
    options=[
        Option("member", "The guy you wanna give your epicly awesome gamehosting powers", OptionType.user, True)
    ],
    guild_ids=[753967387149074543]
)
async def promote(inter, member:disnake.Member):
    try:
        var[inter.guild.id]["test"]
    except:
        var[inter.guild.id] = copy.deepcopy(temp)
        var[inter.guild.id]["index"] = 0

    plist = var[inter.guild.id]["players"]

    if (inter.author.id not in plist):
        await inter.response.send_message("You're not in the game.", ephemeral=True)
        return
    if (member.id not in plist):
        await inter.response.send_message("The person you're promoting isn't in the game.", ephemeral=True)
        return
    if (member.bot):
        await inter.response.send_message("Stop trying to break the game!", ephemeral=True)
        return
    if (inter.author.id != plist[0]):
        await inter.response.send_message("You're not the host.", ephemeral=True)
        return

    embed = disnake.Embed(title="Host tranferred!", colour=disnake.Colour(0xb084b5), description=f"**Your host powers have been transferred to {member.name}!**")

    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text="Use `/party` to see the new host.", icon_url=inter.author.avatar.url)

    mainindex = plist.index(inter.author.id)
    secondaryindex = plist.index(member.id)
    plist[mainindex], plist[secondaryindex] = plist[secondaryindex], plist[mainindex]

    await inter.response.send_message(embed=embed)

@commands.guild_only()
@bot.slash_command(
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
        var[ctx.guild.id]["index"] = 0

    try:
        guilds[str(ctx.author.id)]
        guilds[str(ctx.author.id)]["joinedgame"]
        guilds[str(ctx.author.id)]["equipped"]
        guilds[str(ctx.author.id)]["guild"]
    except:
        guilds[str(ctx.author.id)] = {"guild" : 0, "joinedgame" : False, "equipped" : None}

    
    if (ctx.author.id in var[ctx.guild.id]["players"]):
        if (interaction==True):
            await ctx.response.send_message("You can't join a lobby you're already in.", ephemeral=True)
        else:
            await ctx.channel.send("You can't join a lobby you're already in.")
        return
    elif (len(var[ctx.guild.id]["players"]) >= 10):
        if(interaction == True):
            await ctx.response.send_message("The game is full! Please wait when another player leaves.", ephemeral=True)
        else:
            await ctx.send("The game is full! Please wait when another player leaves.")
        return
    elif (guilds[str(ctx.author.id)]['joinedgame'] == True):
        await ctx.response.send_message("You can't join multiple games at once.", ephemeral=True)
        return


    if (var[ctx.guild.id]["started"] == False):
        if (interaction == True):
            await ctx.response.defer()

        var[ctx.guild.id]["players"].append(int(ctx.author.id))
        players = len(var[ctx.guild.id]["players"])

        p = var[ctx.guild.id]["players"]
        var[ctx.guild.id]["playeremoji"][var[ctx.guild.id]["emojis"][var[ctx.guild.id]["index"]]] = ctx.author.id
        var[ctx.guild.id]["votingemoji"][var[ctx.guild.id]["emojiz"][var[ctx.guild.id]["index"]]] = ctx.author.id
        var[ctx.guild.id]["index"] += 1

        s = var[ctx.guild.id]["setupz"]

        if (s.lower() == "delta"):
            s = f"{str(random.randint(10, 99))}.{str(random.randint(100, 999))}.{str(random.randint(10, 99))}.{str(random.randint(100, 999))}"

        embed = disnake.Embed(title=f"{ctx.author.name}#{ctx.author.discriminator} has joined the party!", description=f"**Current Players:**`{str(players)}`\n**Current Host:**{bot.get_user(p[0]).mention}\n**Setup:** {string.capwords(str(s))}", colour=disnake.Colour(0x8ef3ff))
        embed.set_thumbnail(url=ctx.author.avatar.url)
        if (interaction == True):
            await ctx.edit_original_message(embed=embed)
        else:
            await ctx.send(embed=embed)

        guilds[str(ctx.author.id)]["guild"] = ctx.guild.id
        guilds[str(ctx.author.id)]["joinedgame"] = True
        guilds[str(ctx.author.id)]["vkicktarget"] = 0

        with open('guilds.json', 'w') as jsonf:
            json.dump(guilds, jsonf)
        
    else:
        var[ctx.guild.id]["joinq"].append(ctx.author.id)
        if(interaction == True):
            embed = disnake.Embed(title=f"**{ctx.author.name}#{ctx.author.discriminator} has joined the joined queue.**", colour=disnake.Colour(0xf5cbff), description="**You will automatically join the game once the game ends.**")
            await ctx.response.send_message(embed=embed)
        else:
            embed = disnake.Embed(title=f"**{ctx.author.name}#{ctx.author.discriminator} has joined the join queue.**", colour=disnake.Colour(0xf5cbff), description="**You will automatically join the game once the game ends.**")
            await ctx.send(embed=embed)
        return

@commands.guild_only()
@bot.slash_command(
    name="leave",
    description="Leave the game"
)
async def lleave(inter):
    await _leave(inter, True)

async def _leave(ctx:ApplicationCommandInteraction, inter=False):
    try:
        var[ctx.guild.id]["test"]
    except:
        var[ctx.guild.id] = copy.deepcopy(temp)

    if (ctx.author.id not in var[ctx.guild.id]["players"]):
        if (inter==True):
            await ctx.response.send_message("You can't leave a lobby you're not in.", ephemeral=True)
        else:
            await ctx.send("You can't leave a lobby you're not in.")

        return

    if (inter == True):
        await ctx.response.defer()

    g = disnake.utils.get(ctx.guild.roles, name="[Anarchic] Player")
    d = disnake.utils.get(ctx.guild.roles, name="[Anarchic] Dead")

    r:disnake.Member = ctx.author
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

        embed = disnake.Embed()
        try:
            r = var[ctx.guild.id]["players"]


            embed = disnake.Embed(title=f"**{ctx.author.name}#{ctx.author.discriminator} has left the party.**", colour=disnake.Colour(0xf5cbff), description=f"**Current Players: `{len(r)}`**\n**Current Host:** {bot.get_user(r[0]).mention}")
        except:
            embed = disnake.Embed(title=f"**{ctx.author.name}#{ctx.author.discriminator} has left the party.**", colour=disnake.Colour(0xf5cbff), description=f"**Current Players: `{len(r)}`**\n**Current Host:** None")
        embed.set_thumbnail(url=ctx.author.avatar.url)
        embed.set_footer(text="Come back soon.", icon_url=ctx.author.avatar.url)
        if (inter == True):
            await ctx.edit_original_message(embed=embed)
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
        var[ctx.guild.id]["leaveq"].append(ctx.author.id)
        if (inter==True):
            embed = disnake.Embed(title=f"**{ctx.author.name}#{ctx.author.discriminator} has joined the leave queue.**", colour=disnake.Colour(0xf5cbff), description="**You will automatically leave the game once the game ends.**")
            await ctx.edit_original_message(content="", embed=embed)
        else:
            embed = disnake.Embed(title=f"**{ctx.author.name}#{ctx.author.discriminator} has joined the leave queue.**", colour=disnake.Colour(0xf5cbff), description="**You will automatically leave the game once the game ends.**")
            await ctx.send(embed=embed)


@bot.command()
async def party(ctx):
    await _party(ctx)

@commands.guild_only()
@bot.slash_command(
    name="party",
    description="View the players in the game"
)
async def pparty(inter):
    await _party(inter, True)

async def _party(ctx:ApplicationCommandInteraction, sla=False):

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

    if (message == "" and len(var[ctx.guild.id]["players"]) != 1):
        if (len(var[ctx.guild.id]["players"]) < 1):
            if (sla==True):
                await ctx.response.send_message("There's nobody in the game...", ephemeral=True)
            else:
                await ctx.send("There's nobody in the game...")
            return

    await ctx.response.defer()


    ok = ctx.guild.get_member(int(var[ctx.guild.id]["players"][0]))
    embed = disnake.Embed(title=f"`{ok.name}'s Lobby`", colour=disnake.Colour(0xccbecb))

    embed.set_thumbnail(url=ctx.channel.guild.icon.url)
    embed.set_footer(text="Use `/start` to start the game.", icon_url=ctx.author.avatar.url)

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
            elif (i == "NE"):
                message += f"**Neutral Evil** {em[i.lower()]}\n"
            elif (i == "TI"):
                message += f"**Town Investigative** {em[i.lower()]}\n"
            elif (i == "TS"):
                message += f"**Town Support** {em[i.lower()]}\n"
            elif (i == "NK"):
                message += f"**Neutral Killing** {em[i.lower()]}\n"
            else:
                message += f"**{string.capwords(i)}** {em[i.lower()]}\n"
        
        if (message == ""):
            message = "This setup is empty."

        s = var[ctx.guild.id]["setupz"]
        embed.add_field(name=f"Current Setup :tada:: `{string.capwords(s)}`", value=message)
    else:
        embed.add_field(name=f"Current Setup :tada:: `All Any`", value="**:game_die: Any x the amount of players playing :partying_face:**")

    if (sla == True):
        await ctx.edit_original_message(embed=embed)
    else:
        await ctx.channel.send(embed=embed)

@commands.guild_only()
@bot.slash_command(
    name="vkick",
    description="Vote to kick users from the game.",
    options=[
        Option("member", "The member you want to votekick", OptionType.user, True)
    ]
)
async def vdkick(ctx, member=None):
    try:
        var[ctx.guild.id]["test"]
    except:
        var[ctx.guild.id] = copy.deepcopy(temp)
    if (var[ctx.guild.id]["started"] == True):
        await ctx.response.send_message("You can't kick players during a game.", ephemeral=True)
        return
    if (ctx.author.id not in var[ctx.guild.id]["players"]):
        await ctx.response.send_message("WHAT WHY ARE YOU KICKING SOMEONE WHEN YOU AREN'T EVEN IN THE GAME", ephemeral=True)
        return
    if (member.id not in var[ctx.guild.id]["players"]):
        await ctx.response.send_message("You can't kick players that aren't in the game.", ephemeral=True)
        return
    try:
        if (guilds[str(ctx.author.id)]["vkicktarget"] == member.id):
            await ctx.response.send_message("You can't kick the same player more than once.", ephemeral=True)
            return
    except:
        pass

    if (member.id in var[ctx.guild.id]["vkickd"]):
        var[ctx.guild.id]["vkickd"][member.id] += 1
    else:
        var[ctx.guild.id]["vkickd"][member.id] = 1


    f = var[ctx.guild.id]["vkickd"]
    guilds[str(ctx.author.id)]["vkicktarget"] = member.id
    embed = disnake.Embed(title=f"**{ctx.author.name} has voted to kick {member.name}!**", colour=disnake.Colour(0xb4ffdc), description=f"**({f[member.id]}/3) votes are needed to vote kick {member.name}.**")

    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896418860427771975/upvote.png")
    embed.set_footer(text="3 votes are needed to vote kick someone.")
    await ctx.response.send_message(embed=embed)

    if (var[ctx.guild.id]["vkickd"][member.id] >= 3):
        var[ctx.guild.id]["players"].remove(int(member.id))
        embed = disnake.Embed(title=f"**{member.name} has been kicked!**", colour=disnake.Colour(0xfff4d1))
        if (random.randint(1, 80000) == 9642):
            embed.description = "That's a shame..."

        guilds[str(member.id)]["guild"] = 0
        guilds[str(member.id)]["joinedgame"] = False
        var[ctx.guild.id]["vkickd"][member.id] = 0
        
        embed.set_thumbnail(url=member.avatar.url)
        await ctx.followup.send(embed=embed)

        guilds[str(member.id)]["vkicktarget"] = 0
        for i in var[ctx.guild.id]["players"]:
            if (guilds[str(i)]["vkicktarget"] == member.id):
                guilds[str(i)]["vkicktarget"] = 0

@commands.guild_only()
@bot.slash_command(
    name="kick",
    description="Kick users from the game. You have to be the game host to do this.",
    options=[
        Option("member", "The member you want to votekick", OptionType.user, True)
    ]
)
async def kkick(ctx, member:disnake.Member):
    try:
        var[ctx.guild.id]["test"]
    except:
        var[ctx.guild.id] = copy.deepcopy(temp)
    if (var[ctx.guild.id]["started"] == True):
        await ctx.response.send_message("You can't kick players during a game.", ephemeral=True)
        return
    if (ctx.author.id not in var[ctx.guild.id]["players"]):
        await ctx.response.send_message("WHAT WHY ARE YOU KICKING SOMEONE WHEN YOU AREN'T EVEN IN THE GAME", ephemeral=True)
        return
    if (member.id not in var[ctx.guild.id]["players"]):
        await ctx.response.send_message("You can't kick players that aren't in the game.", ephemeral=True)
        return
    if (ctx.author.id != var[ctx.guild.id]["players"][0]):
        await ctx.response.send_message("You can't kick players when you aren't the host.", ephemeral=True)
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
    embed = disnake.Embed(title=f"**{member.name} has been kicked by the host!**", colour=disnake.Colour(0xfff4d1))
    if (random.randint(1, 80000) == 9642):
        embed.description = "That's a shame..."

    embed.set_thumbnail(url=member.avatar.url)
    var[ctx.guild.id]["vkickd"][member.id] = 0
    await ctx.response.send_message(embed=embed)

    guilds[str(member.id)]["guild"] = 0
    guilds[str(member.id)]["joinedgame"] = False
    guilds[str(member.id)]["vkicktarget"] = 0
    for i in var[ctx.guild.id]["players"]:
        if (guilds[str(i)]["vkicktarget"] == member.id):
            guilds[str(i)]["vkicktarget"] = 0

@commands.guild_only()
@bot.slash_command(
    name="clear",
    description="Clears the entire lobby. You must be the host to do this"
)
async def clear(ctx):
    try:
        var[ctx.guild.id]["test"]
    except:
        var[ctx.guild.id] = copy.deepcopy(temp)


    if (len(var[ctx.guild.id]["players"]) == 0):
        embed = disnake.Embed(title=f"The game has already been cleared!", colour=disnake.Colour(0xfff4d1))
        embed.description = "F"

        embed.set_thumbnail(url=ctx.author.avatar.url)
        await ctx.response.send_message(embed=embed, ephemeral=True)
        return

    if (var[ctx.guild.id]["started"] == True):
        await ctx.response.send_message("You can't clear the game when it already started.", ephemeral=True)
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

    embed = disnake.Embed(title=f"The game has been cleared!", colour=disnake.Colour(0xfff4d1))
    if (random.randint(1, 80000) == 6969):
        embed.description = "F"

    embed.set_thumbnail(url=ctx.author.avatar.url)
    await ctx.response.send_message(embed=embed)

@commands.guild_only()
@bot.slash_command(
    name="upvote",
    description="Vote for the bot on top.gg"
)
async def votebot(inter:ApplicationCommandInteraction):
    if (str(inter.author.id) not in cur):
        cur[str(inter.author.id)] = 0

    auth = str(inter.author.id)
    try:
        guilds[auth]["voted"]
    except:
        guilds[auth]["voted"] = False

    class VotedButton(disnake.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
        
        @disnake.ui.button(label="I voted", style=disnake.ButtonStyle.grey, emoji="📪")
        async def voted(self, button:disnake.ui.Button, interaction:disnake.MessageInteraction):
            req = requests.get(f"https://top.gg/api/bots/887118309827432478/check?userId={inter.author.id}", headers = {"Authorization" : "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Ijg4NzExODMwOTgyNzQzMjQ3OCIsImJvdCI6dHJ1ZSwiaWF0IjoxNjM3NDI2MzA2fQ.k8ufWIHlJIeK1xgpXPWlm1LswoKyb5-r86gkcMOjqgg"})
            data:dict = json.loads(req.text)
         
            if (interaction.author.id != inter.author.id):
                await interaction.response.send_message("Stop being lazy.", ephemeral=True)
                return

            if (data.get("voted") == 1 and guilds[auth]["voted"] == False):
                cur[str(inter.author.id)] += 20
                embed = disnake.Embed(title="**Thank you for voting for the bot!**", colour=disnake.Colour(0xe9ffcf), description="**Remember that you can vote again in 12 hours**")

                embed.set_footer(text="Thank you!", icon_url=inter.author.avatar.url)

                embed.add_field(name="**You have received:**", value="**20 silvers <:silvers:889667891044167680>**")
                await inter.followup.send(embed=embed)
                guilds[auth]["voted"] = True

                with open('data.json', 'w') as jsonf:
                    json.dump(cur, jsonf)
            elif (data.get("voted") == 0):
                embed = disnake.Embed(title="**Failed to get your voting reward**", colour=disnake.Colour(0xff5e5e), description="**It looks like you haven't voted for the bot yet. You can vote for the bot [here](https://top.gg/bot/887118309827432478/vote).**")

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/872274879309836408/unknown.png?width=375&height=634")
                embed.set_footer(text="Thank you!", icon_url=inter.author.avatar.url)
                await inter.followup.send(embed=embed, ephemeral=True)
            elif(guilds[auth]["voted"] == True):
                embed = disnake.Embed(title="**Failed to get your voting reward**", colour=disnake.Colour(0xff5e5e), description="**It looks like you've already voted for the bot. You can vote for the bot again in 12 hours.**")

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/872274879309836408/unknown.png?width=375&height=634")
                embed.set_footer(text="Thank you!", icon_url=inter.author.avatar.url)
                await inter.followup.send(embed=embed, ephemeral=True)

    embed = disnake.Embed(title="**Consider voting for the bot!**", colour=disnake.Colour(0xe9ffcf), description="**You can vote for the bot [here](https://top.gg/bot/887118309827432478/vote)**")

    embed.set_footer(text="Thank you!", icon_url=inter.author.avatar.url)

    embed.add_field(name="**Rewards:**", value="**20 silvers <:silvers:889667891044167680>**")

    await inter.response.send_message(embed=embed, view=VotedButton())

    
@commands.guild_only()
@bot.slash_command(
    name="spectate",
    description="Spectate the current game of Anarchic"
)
async def spectate(inter):
    try:
        var[inter.guild.id]["test"]
    except:
        var[inter.guild.id] = copy.deepcopy(temp)

    guild = var[inter.guild.id]
    if (guild["started"] == False):
        await inter.response.send_message("There isn't any game going on right now...", ephemeral=True)
        return
    if (inter.author.id in guild["players"]):
        await inter.response.send_message("You're already in the game. You don't NEED to spectate...", ephemral=True)
        return
    
@bot.command()
async def sus(ctx):
    await ctx.send("imagine being sus")


@commands.guild_only()
@bot.slash_command(
    name="start",
    description="Start a game of Anarchic"
)
async def sstart(inter):
    await _start(inter, True)

async def _start(ctx:ApplicationCommandInteraction, inter=False):
    try:
        var[ctx.guild.id]["test"]
    except:
        var[ctx.guild.id] = copy.deepcopy(temp)
    if (len(var[ctx.guild.id]["players"]) == 0):
        if (inter == True):
            await ctx.response.send_message("How do you expect me to start a game with nobody in it?", ephemeral=True)
        else:
            await ctx.send("How do you expect me to start a game with nobody in it?")
        return

    if (ctx.author.id != var[ctx.guild.id]["players"][0]):
        if (inter == True):
            await ctx.response.send_message("Only the host can start the game!",ephemeral=True)
        else:
            await ctx.send("Only the host can start the game!")
        return

    if (var[ctx.guild.id]["started"] == True):
        await ctx.response.send_message("A game has already started!", ephemeral=True)
        return

    s = var[ctx.guild.id]["setupz"]
    if (s.lower() != "custom"):
        if (4 >= len(var[ctx.guild.id]["players"]) and s.lower() == "any"):
            if (inter == True):
                await ctx.response.send_message(f"There are too little players in the game! There should be 5 or more players.",ephemeral=True)
            else:
                await ctx.send(f"There are too little players in the game! There should be 5 or more players.")
            return
        else:
            if (s.lower() != "any"):
                c = var[ctx.guild.id]["comps"]

                lines = len(var[ctx.guild.id]["players"])
                if (lines > len(c[s.lower()])):
                        if (inter == True):
                            await ctx.response.send_message(f"There are too many players in the game! There should be {len(c[s])} players.",ephemeral=True)
                        else:
                            await ctx.send(f"There are too many players in the game! There should be {len(c[s])} players.")
                        return

                if (lines < len(c[s.lower()])):
                    if (inter == True):
                        await ctx.response.send_message(f"There aren't enough players in the game! There should be {len(c[s])} players.",ephemeral=True)
                    else:
                        await ctx.send(f"There aren't enough players in the game! There should be {len(c[s])} players.")
                    return
    else:
        c = var[ctx.guild.id]["comps"]
        if (len(c["custom"]) < 2):
            await ctx.response.send_message("The setup is too small to be playable! There should at least 2 roles in the setup.", ephemeral=True)
            return


        canStart = False
        musthave = ["Mafioso", "Psychopath", "Framer", "Janitor", "Consort", "Consigliere"]
        for i in musthave:
            if (i in c["custom"]):
                canStart = True
                break

        if (canStart == False):
            await ctx.response.send_message("The setup must have an evil role in the game!", ephemeral=True)
            return

        lines = len(var[ctx.guild.id]["players"])
        if (lines > len(c[s.lower()])):
                if (inter == True):
                    await ctx.response.send_message(f"There are too many players in the game! There should be {len(c[s])} players.",ephemeral=True)
                else:
                    await ctx.send(f"There are too many players in the game! There should be {len(c[s])} players.")
                return

        if (lines < len(c[s.lower()])):
            if (inter == True):
                await ctx.response.send_message(f"There aren't enough players in the game! There should be {len(c[s])} players.",ephemeral=True)
            else:
                await ctx.send(f"There aren't enough players in the game! There should be {len(c[s])} players.")
            return

    embed = disnake.Embed(title="Starting game...", colour=disnake.Colour(0xd7b1f9), description="The bot is currently setting up the required channels and roles for the game to operate. Please stand by...")

    embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")

    await ctx.response.send_message(embed=embed)
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
    
    var[ctx.guild.id]["started"] = True
    var[ctx.guild.id]["result"] = False
    var[ctx.guild.id]["voting"] = False
    var[ctx.guild.id]["guildg"] = ctx.guild
    if (disnake.utils.get(ctx.guild.roles, name="[Anarchic] Player") == None):
        await guild.create_role(name="[Anarchic] Player")

    if (disnake.utils.get(ctx.guild.roles, name="[Anarchic] Dead") == None):
        await guild.create_role(name="[Anarchic] Dead")

    if (disnake.utils.get(ctx.guild.roles, name="[Anarchic] Spectator") == None):
        await guild.create_role(name="[Anarchic] Spectator")

    for i in var[ctx.guild.id]["players"]:
        role = disnake.utils.get(ctx.guild.roles, name="[Anarchic] Player")
        user = ctx.guild.get_member(i)
        await user.add_roles(role)

    print("---------------")

    var[ctx.guild.id]["gday"] = 1
    var[ctx.guild.id]["nightg"] = 1
    var[ctx.guild.id]["daysnokill"] = 0
    if (inter == False):
        await ctx.message.add_reaction("✅")
    overwrites = disnake.PermissionOverwrite()
    overwrites.read_messages = False
    overwrites.send_messages = False
    f = await guild.create_category("Anarchic", reason="Game of Anarchic")
    await f.set_permissions(ctx.guild.default_role, overwrite=overwrites)
    overwrites.read_messages = True
    overwrites.send_messages = True
    var[ctx.guild.id]["startchannel"] = ctx.channel

    overwrite = disnake.PermissionOverwrite()
    overwrite.read_messages = True

    # for i in var[ctx.guild.id]["players"]:
    #     user = await ctx.guild.fetch_member(i)
    #     await f.set_permissions(user, overwrite=overwrite)

    chan = await f.create_text_channel("town-square", reason="Anarchic Setup")
    die = await f.create_text_channel("graveyard", reason="Anarchic setup")
    maf = await f.create_text_channel("mafia-contacts", reason="Anarchic setup")


    if (inter == True):
        try:
            embed = disnake.Embed(title="A game has started!", colour=disnake.Colour(0xd7b1f9), description=f"Everyone in the game should go to {chan.mention} for the game to begin.")

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")

            await ctx.edit_original_message(embed=embed)
        except Exception as e:
            print(e)
            await ctx.channel.send(f"A game has started! Everyone in the game should check {chan.mention}.")
    else:
        await ctx.channel.send(f"A game has started! Everyone in the game should check {chan.mention}.")    

    await f.set_permissions(disnake.utils.get(ctx.guild.roles, name="[Anarchic] Player"), overwrite=overwrites)
    
    embed = disnake.Embed(title="**Welcome to the Graveyard <:rip:872284978354978867>!**", colour=disnake.Colour(0x300036), description="This is a place for dead players to talk, discuss and complain about the living.")

    embed.set_image(url="https://cdn.discordapp.com/attachments/878437549721419787/883854521753813022/unknown.png")
    embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png?width=374&height=374")

    embed.add_field(name="**Rules :pushpin:**", value="Here are some guidelines to follow.", inline=False)
    embed.add_field(name="No Dead Info :newspaper2:.", value="Do not give dead info. Once you're dead, you're dead. You may only talk about the game here.", inline=False)
    embed.add_field(name="Only Preview :eyes:", value="Specators are not allowed to interact in any way with the living .", inline=False)

    guild = ctx.guild
    overwrites = disnake.PermissionOverwrite(read_messages=False)



    var[ctx.guild.id]["diechannel"] = die
    var[ctx.guild.id]["mafcon"] = maf

    overwrites.read_messages = False
    overwrites.send_messages = False

    await die.set_permissions(disnake.utils.get(ctx.guild.roles, name="[Anarchic] Player"), overwrite=overwrites)

    overwrites.read_messages = True
    overwrites.send_messages = True
    await die.set_permissions(disnake.utils.get(ctx.guild.roles, name="[Anarchic] Dead"), overwrite=overwrites)

    overwrites.read_messages = True
    overwrites.send_messages = False

    await die.set_permissions(disnake.utils.get(ctx.guild.roles, name="[Anarchic] Spectator"), overwrite=overwrites)

    overwrites.read_messages = False
    await chan.set_permissions(disnake.utils.get(ctx.guild.roles, name="[Anarchic] Spectator"), overwrite=overwrites)
    await maf.set_permissions(disnake.utils.get(ctx.guild.roles, name="[Anarchic] Spectator"), overwrite=overwrites)

    var[ctx.guild.id]["channel"] = chan
    await var[ctx.guild.id]["diechannel"].send(embed=embed)    
    await lock(chan)
    embed = disnake.Embed(title="**Welcome to Anarchic.**", colour=disnake.Colour(0x6efff3), description="Anarchic is game of deceit and deception, based off of the Mafia Party game. To learn how to play, check below.")

    embed.set_image(url="https://cdn.discordapp.com/attachments/878437549721419787/882712063904976926/welcome.png")
    embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png?width=374&height=374")
    embed.set_footer(text="Good luck.")

    embed.add_field(name="**How to Play💡**", value="Each player is secretly assigned a role at the start of the game and has to fulfill their goal. To see the list of roles, try typing `/roles`. The game alternates between a day and night cycle. For more infomation, use `/howtoplay`.", inline=False)
    embed.add_field(name="**Rules :pushpin:**", value="Here are a list of rules to follow.", inline=False)
    embed.add_field(name="**No Screenshoting :camera_with_flash:**", value="Screenshoting is strictly forbidden, as it is cheeating ruins the game for everyone.", inline=False)
    embed.add_field(name="**No Copy And Pasting :pencil:**", value="Copy and pasting is also considered breaking the rules, as it is also cheating.", inline=False)
    embed.add_field(name="No Direct Messaging 💬", value="Direct Messaging is not allowed as it ruins many game mechanics. ",inline=False)
    embed.add_field(name="Names Policy :man_gesturing_no:", value="Names must be set to a typeable english name, for players to be able to select you.",inline=False)

    await chan.send(content=disnake.utils.get(ctx.guild.roles, name="[Anarchic] Player").mention, embed=embed)

    await asyncio.sleep(3)

    e = time.time()
    random.seed(e)

    try:
        await assignroles(var[ctx.guild.id]["setupz"], ctx.guild)
    except ValueError:
        embed = disnake.Embed(title="The bot is lacking permissions to perform an action", colour=disnake.Colour(0xea5f61), description="**Either someone disabled DMs with server members, or the bot is missing role permssions to perform an action.**")

        embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")
        embed.set_footer(text="If this keeps happening, contact support with `/invite`", icon_url=ctx.author.avatar.url)

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

        g = disnake.utils.get(guild.roles, name="[Anarchic] Player")
        d = disnake.utils.get(guild.roles, name="[Anarchic] Dead")

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

    await maf.set_permissions(disnake.utils.get(ctx.guild.roles, name="[Anarchic] Player"), overwrite=overwrites)

    embed = None
    message = ""

    embed = disnake.Embed(title="**Your Mafia team for the game <:maficon2:890328238029697044>.**", colour=disnake.Colour(0xd0021b))

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
    embed = disnake.Embed(title="**It Is Day 1 ☀️.**", colour=disnake.Colour(0x7ed321))

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


    role = disnake.utils.get(ctx.guild.roles,name="[Anarchic] Player")

    await chan.send(f"{role.mention}\n━━━━━━━━━━━━━━━━━━━━━━━━━━", embed=embed)
    await asyncio.sleep(1)
    await unlock(chan)
    await asyncio.sleep(15)
    await lock(chan)

    dad = var[ctx.guild.id]["gday"]
    embed = disnake.Embed(title=f"**It is Night 1 :crescent_moon:.**", colour=disnake.Colour(0x1f0050))

    embed.set_image(url="https://cdn.discordapp.com/attachments/765738640554065962/912890903545397258/IMG_0089.png")
    message = ""
    for i in var[ctx.guild.id]["playerdict"].values():
        if (i.dead==False and i.id != 0):
            message += f"{bot.get_user(i.id).mention}\n" 
    if (message == ""):
        message = ":x: None"

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
        message = ":x: **None**"
    embed.add_field(name="**Graveyard <:rip:872284978354978867>:**", value=message, inline=True)
    
    await chan.send(embed=embed)

    if (noImpsNoCrews(ctx.guild) and len(getPsychos(ctx.guild)) == 1):
        b = await EndGame(EndReason.Psychopath, var[ctx.guild.id]["channel"].guild)
        await var[ctx.guild.id]["channel"].send(embed=b)
        await var[ctx.guild.id]["startchannel"].send(embed=b)
        perm = disnake.PermissionOverwrite()
        perm.read_messages = True
        perm.send_messages = True

        role = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
        roled = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

        await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
        await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
        perm.send_messages = False
        await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
        await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

        var[ctx.guild.id]["result"] = True
        return
    if (len(getTownies(ctx.guild)) == 0 and len(getMaf(ctx.guild)) == 0 and len(getPsychos(ctx.guild)) == 0):
        b = await EndGame(EndReason.Draw, var[ctx.guild.id]["channel"].guild)
        await var[ctx.guild.id]["channel"].send(embed=b)
        await var[ctx.guild.id]["startchannel"].send(embed=b)
        perm = disnake.PermissionOverwrite()
        perm.read_messages = True
        perm.send_messages = True

        role = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
        roled = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

        await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
        await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
        perm.send_messages = False
        await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
        await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

        var[ctx.guild.id]["result"] = True
        return
    if (len(getTownies(ctx.guild)) == 0  and len(getPsychos(ctx.guild)) == 0):
        b = await EndGame(EndReason.MafiaWins, var[ctx.guild.id]["channel"].guild)
        await var[ctx.guild.id]["channel"].send(embed=b)
        await var[ctx.guild.id]["startchannel"].send(embed=b)
        perm = disnake.PermissionOverwrite()
        perm.read_messages = True
        perm.send_messages = True

        role = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
        roled = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

        await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
        await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
        perm.send_messages = False
        await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
        await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

        var[ctx.guild.id]["result"] = True
        return
    elif (len(getMaf(ctx.guild)) == 0 and len(getPsychos(ctx.guild)) == 0):
        b = await EndGame(EndReason.TownWins, var[ctx.guild.id]["channel"].guild)
        await var[ctx.guild.id]["channel"].send(embed=b)
        await var[ctx.guild.id]["startchannel"].send(embed=b)
        perm = disnake.PermissionOverwrite()
        perm.read_messages = True
        perm.send_messages = True

        role = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
        roled = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

        await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
        await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
        perm.send_messages = False
        await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
        await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

        var[ctx.guild.id]["result"] = True
        return

    await night(chan)
    
@bot.command()
async def removeroles(ctx):
    await ctx.send("E")
    if (ctx.author.id == 839842855970275329 or ctx.author.id == 667189788620619826):
        guild:disnake.Guild = ctx.guild
        g = disnake.utils.get(guild.roles, name="[Anarchic] Player")
        d = disnake.utils.get(guild.roles, name="[Anarchic] Dead")

        await ctx.send("Removing roles, please wait!")
        start_time = time.time()

        for f in guild.members:

            r:disnake.Member = f
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

@bot.slash_command()
async def will(inter):
    pass

@commands.guild_only()
@will.sub_command(
    name="write",
    description="Write in your will",
    options=[Option("text", "The text in the inserting part", OptionType.string, True), Option("line", "The line you want to insert in", OptionType.integer, False)]
)
async def writeWill(ctx:ApplicationCommandInteraction, text=None, line=None):
    try:
        var[ctx.guild.id]["test"]
    except:
        var[ctx.guild.id] = copy.deepcopy(temp)

    if (ctx.author.id not in var[ctx.guild.id]["players"]):
        embed = disnake.Embed(title="You aren't in the game...", description="Try joining the game and starting it.")
        await ctx.response.send_message(embed=embed, ephemeral=True)
        return
    else:
        if (var[ctx.guild.id]["started"] == False):
            embed = disnake.Embed(title="The game hasn't started yet...", description="Start the game then try again.")
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
        else:
            if ("\\" in text):
                embed = disnake.Embed(title="You can't add backslashes in your will.", description="Backslashes will break the game!")
                await ctx.response.send_message(embed=embed, ephemeral=True)
                return

            myPlayer = Player.get_player(ctx.author.id, var[ctx.guild.id]["playerdict"])

            if (myPlayer.dead == True):
                embed = disnake.Embed(title="You're dead.", description="Please be alive and try again.")
                await ctx.response.send_message(embed=embed, ephemeral=True)
                return

            if (line == None):
                myPlayer.will.append(text)
            else:
                myPlayer.will.insert(int(line) - 1, text)

            will = getWill(myPlayer.will)

            #Add components
            class PostButton(disnake.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)

                @disnake.ui.button(label="Post Will", style=ButtonStyle.gray, emoji="🗒️")
                async def post(self, button, inter:MessageInteraction):
                    embed = disnake.Embed(title=f":scroll: {ctx.author.name}'s Will :scroll:", colour=disnake.Colour(0xbd10e0), description=will)

                    embed.set_thumbnail(url=ctx.author.avatar.url)
                    embed.set_footer(text="Remember to update your will!", icon_url=ctx.author.avatar.url)
                    await inter.channel.send(embed=embed)

            #Create embed
            embed = disnake.Embed(title=f"**:scroll: {ctx.author.name}'s Will :scroll:**", colour=disnake.Colour(0x9902b8), description=will)

            embed.set_thumbnail(url=ctx.author.avatar.url)
            embed.set_footer(text="Remember to update your will!", icon_url=ctx.author.avatar.url)

            #Send messagse
            await ctx.response.send_message(embed=embed, view=PostButton(), ephemeral=True)

@commands.guild_only()
@will.sub_command(
    name="remove",
    description="Remove a line in your will",
    options=[Option("line", "The line you want to remove", OptionType.integer, True)]
)
async def removeWill(ctx, line=None):
    try:
        var[ctx.guild.id]["test"]
    except:
        var[ctx.guild.id] = copy.deepcopy(temp)

    if (ctx.author.id not in var[ctx.guild.id]["players"] is None):
        embed = disnake.Embed(title="You aren't in the game...", description="Try joining the game and starting it.")
        await ctx.response.send_message(embed=embed, ephemeral=True)
        return
    else:
        if (var[ctx.guild.id]["started"] == False):
            embed = disnake.Embed(title="The game hasn't started yet...", description="Start the game then try again.")
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
        else:
            if (int(line) < 1):
                embed = disnake.Embed(title="That's an invalid line.", description="Please choose a usable line in the will system.")
                await ctx.response.send_message(embed=embed, ephemeral=True)
                return

            myPlayer = Player.get_player(ctx.author.id, var[ctx.guild.id]["playerdict"])
            
            if (myPlayer.dead == True):
                embed = disnake.Embed(title="You're dead.", description="Please be alive and try again.")
                await ctx.response.send_message(embed=embed, ephemeral=True)
                return

            myPlayer.will.pop(int(line) - 1)
            will = getWill(myPlayer.will)

            #Add components
            class PostButton(disnake.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)

                @disnake.ui.button(label="Post Will", style=ButtonStyle.gray, emoji="🗒️")
                async def post(self, button, inter:MessageInteraction):
                    embed = disnake.Embed(title=f":scroll: {ctx.author.name}'s Will :scroll:", colour=disnake.Colour(0xbd10e0), description=will)

                    embed.set_thumbnail(url=ctx.author.avatar.url)
                    embed.set_footer(text="Remember to update your will!", icon_url=ctx.author.avatar.url)
                    await inter.channel.send(embed=embed)

            #Create embed
            embed = disnake.Embed(title=f"**:scroll: {ctx.author.name}'s Will :scroll:**", colour=disnake.Colour(0x9902b8), description=will)

            embed.set_thumbnail(url=ctx.author.avatar.url)
            embed.set_footer(text="Remember to update your will!", icon_url=ctx.author.avatar.url)

            #Send messagse
            msg = await ctx.response.send_message(embed=embed, view=PostButton(), ephemeral=True)

@commands.guild_only()
@will.sub_command(
    name="view",
    description="Look at your will",
    options=[
        Option(name="member", description="The user's will you want to view", type=OptionType.user)
    ]
)
async def viewWill(ctx, member=None):
    try:
        var[ctx.guild.id]["test"]
    except:
        var[ctx.guild.id] = copy.deepcopy(temp)

    if (ctx.author.id not in var[ctx.guild.id]["players"]):
        embed = disnake.Embed(title="You aren't in the game...", description="Try joining the game and starting it.")
        await ctx.response.send_message(embed=embed, ephemeral=True)
        return
    else:
        if (var[ctx.guild.id]["started"] == False):
            embed = disnake.Embed(title="The game hasn't started yet...", description="Start the game then try again.")
            await ctx.response.send_message(embed=embed,ephemeral=True)
            return
        else:
            if (member == None):
                #Get Player will
                myPlayer = Player.get_player(ctx.author.id, var[ctx.guild.id]["playerdict"])
                mywill = getWill(myPlayer.will)

                #Add components
                class PostButton(disnake.ui.View):
                    def __init__(self):
                        super().__init__(timeout=None)

                    @disnake.ui.button(label="Post Will", style=ButtonStyle.gray, emoji="🗒️")
                    async def post(self, button, inter:MessageInteraction):
                        embed = disnake.Embed(title=f":scroll: {ctx.author.name}'s Will :scroll:", colour=disnake.Colour(0xbd10e0), description=mywill)

                        embed.set_thumbnail(url=ctx.author.avatar.url)
                        embed.set_footer(text="Remember to update your will!", icon_url=ctx.author.avatar.url)
                        await inter.channel.send(embed=embed)

                #Create embed
                embed = disnake.Embed(title=f"**:scroll: {ctx.author.name}'s Will :scroll:**", colour=disnake.Colour(0x9902b8), description=mywill)

                embed.set_thumbnail(url=ctx.author.avatar.url)
                embed.set_footer(text="Remember to update your will!", icon_url=ctx.author.avatar.url)

                #Send messagse

                view = None
                if (myPlayer.dead == False):
                    view = PostButton()

                msg = await ctx.response.send_message(embed=embed, view=view, ephemeral=True)

            else:
                if (member.id not in var[ctx.guild.id]["players"]):
                    embed = disnake.Embed(title="That player isn't in the game...", description="Try getting them to join the game.")
                    await ctx.response.send_message(embed=embed, ephemeral=True)
                    return

                myPlayer = Player.get_player(member.id, var[ctx.guild.id]["playerdict"])
                mywill = getWill(myPlayer.will)

                if (myPlayer.dead == False):
                    if (var[ctx.guild.id]["result"] == False):
                        embed = disnake.Embed(title="That player is alive...", description="Try killing them and try again.")
                        await ctx.response.send_message(embed=embed, ephemeral=True)
                        return

                embed = disnake.Embed(title=f"**:scroll: {member.name}'s Will :scroll:**", colour=disnake.Colour(0x9902b8), description=mywill)

                embed.set_thumbnail(url=member.avatar.url)
                embed.set_footer(text="Remember to update your will!", icon_url=ctx.author.avatar.url)

                await ctx.response.send_message(embed=embed, ephemeral=True)







async def night(ctx):
    await unlock(var[ctx.guild.id]["mafcon"], True)
    var[ctx.guild.id]["trialuser"] = 0
    var[ctx.guild.id]["night"] = True
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

    if (len(r) == 0 and len(m) > 0):
        play:Player = random.choice(m)
        user = bot.get_user(play.id)
        embed = disnake.Embed(title="**You have been promoted to a Mafioso!**", colour=0xd0021b)

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/891739940055052328.png?size=80")
        embed.set_footer(text="Good luck.", icon_url=user.avatar.url)
        await user.send(embed=embed)

        embed = disnake.Embed(title=f"**{user.name} has been promoted to a Mafioso!**", colour=0xd0021b)

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/891739940055052328.png?size=80")
        embed.set_footer(text="Good luck.", icon_url=user.avatar.url)

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
    var[ctx.guild.id]["night"] = False

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
                    embed = disnake.Embed(title="**Your target has died. You have been converted into a Jester**", colour=disnake.Colour(0xffc3e7))

                    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/872187561597075476.png?v=1")
                    embed.set_footer(text="/role jester for more info.", icon_url=bot.get_user(i.id).avatar.url)
                    await bot.get_user(i.id).send(embed=embed)

        if (i.dead == True):
                await var[ctx.guild.id]["channel"].set_permissions(await ctx.guild.fetch_member(i.id), read_messages=True, send_messages=False)

    await lock(var[ctx.guild.id]["mafcon"], True)

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
        embed = disnake.Embed(title="**You have been promoted to a Mafioso!**", colour=0xd0021b)

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/891739940055052328.png?size=80")
        embed.set_footer(text="Good luck.", icon_url=user.avatar.url)
        await user.send(embed=embed)

        embed = disnake.Embed(title=f"**{user.name} has been promoted to a Mafioso!**", colour=0xd0021b)

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/891739940055052328.png?size=80")
        embed.set_footer(text="Good luck.", icon_url=user.avatar.url)

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
    role = disnake.utils.get(ctx.guild.roles,name="[Anarchic] Player")

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



    embed = disnake.Embed(title=f"**It is Day {da} ☀️.**", colour=disnake.Colour(0xff8900))

    embed.set_image(url="https://images-ext-2.discordapp.net/external/8cFuWNzv5vDa4TbO68gg5Up4DSxguodCGurCAtDpWgU/%3Fwidth%3D936%26height%3D701/https/media.discordapp.net/attachments/765738640554065962/878068703672016968/unknown.png")
    message = ""

    for i in var[ctx.guild.id]["playerdict"].values():
        if (i.dead==False and i.id != 0):
            message += f"{bot.get_user(i.id).mention}\n" 

    if (message == ""):
        message = ":x: **Non--WAIT WHAT THE**"

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
                e.death = [DeathReason.NoReason]

            if (e.death.count(DeathReason.Mafia) > 1):
                for i in range(e.death.count(DeathReason.Mafia) - 1):
                    e.death.remove(DeathReason.Mafia)

            for i in e.death:
                user:disnake.User = bot.get_user(e.id)
                embed = disnake.Embed(title=f"**{user.name}#{user.discriminator} died last night.**", colour=reasontoColor(i), description=f"{reasonToText(i)}")

                embed.set_image(url=reasonToImage(i))
                embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/vdJanNHxHsByUKqoqKUfpoQVv0S5Ym7cv4uhJbqlv7c/%3Fv%3D1/https/cdn.discordapp.com/emojis/747726596475060286.png")

                if (getWill(Player.get_player(user.id, var[ctx.guild.id]["playerdict"]).will) != ""):
                    embed.add_field(name="**We found a will next to their body :scroll:.**", value=f"**{getWill(Player.get_player(user.id, r).will)}**", inline=False)
                
                p = var[ctx.guild.id]["emoji"]
                if (i == DeathReason.Cleaned):
                    embed.add_field(name="**We could not determine their role.**", value=f"** **", inline=False)
                else:
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

    if (noImpsNoCrews(ctx.guild) and len(getPsychos(ctx.guild)) == 1):
        b = await EndGame(EndReason.Psychopath, var[ctx.guild.id]["channel"].guild)
        await var[ctx.guild.id]["channel"].send(embed=b)
        await var[ctx.guild.id]["startchannel"].send(embed=b)
        perm = disnake.PermissionOverwrite()
        perm.read_messages = True
        perm.send_messages = True

        role = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
        roled = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

        await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
        await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
        perm.send_messages = False
        await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
        await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

        var[ctx.guild.id]["result"] = True
        return
    if (len(getTownies(ctx.guild)) == 0 and len(getMaf(ctx.guild)) == 0 and len(getPsychos(ctx.guild)) == 0):
        b = await EndGame(EndReason.Draw, var[ctx.guild.id]["channel"].guild)
        await var[ctx.guild.id]["channel"].send(embed=b)
        await var[ctx.guild.id]["startchannel"].send(embed=b)
        perm = disnake.PermissionOverwrite()
        perm.read_messages = True
        perm.send_messages = True

        role = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
        roled = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

        await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
        await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
        perm.send_messages = False
        await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
        await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

        var[ctx.guild.id]["result"] = True
        return
    if (len(getTownies(ctx.guild)) == 0  and len(getPsychos(ctx.guild)) == 0):
        b = await EndGame(EndReason.MafiaWins, var[ctx.guild.id]["channel"].guild)
        await var[ctx.guild.id]["channel"].send(embed=b)
        await var[ctx.guild.id]["startchannel"].send(embed=b)
        perm = disnake.PermissionOverwrite()
        perm.read_messages = True
        perm.send_messages = True

        role = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
        roled = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

        await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
        await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
        perm.send_messages = False
        await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
        await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

        var[ctx.guild.id]["result"] = True
        return
    elif (len(getMaf(ctx.guild)) == 0 and len(getPsychos(ctx.guild)) == 0):
        b = await EndGame(EndReason.TownWins, var[ctx.guild.id]["channel"].guild)
        await var[ctx.guild.id]["channel"].send(embed=b)
        await var[ctx.guild.id]["startchannel"].send(embed=b)
        perm = disnake.PermissionOverwrite()
        perm.read_messages = True
        perm.send_messages = True

        role = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
        roled = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

        await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
        await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
        perm.send_messages = False
        await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
        await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

        var[ctx.guild.id]["result"] = True
        return

    for i in var[ctx.guild.id]["playerdict"].values():
        if (i.wasrevealed == True and i.dead == False):
            i.wasrevealed = False
            us = await ctx.guild.fetch_member(i.id)

            embed = disnake.Embed(title=f"**{us.name}** has revealed themselves to be the Mayor!", colour=disnake.Colour(0xbc9b25), description="They will now have 3 votes in all future voting procedures.")

            embed.set_image(url="https://cdn.discordapp.com/attachments/878437549721419787/882418844424081449/unknown.png")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/897570023143518288.png?size=80")
            await ctx.send(embed=embed)
            var[ctx.guild.id]["mayor"] = us
            await asyncio.sleep(3)
            break
    
    if (var[ctx.guild.id]["daysnokill"] == 2):
        embed = disnake.Embed(title="**A plague has consumed the town!**", colour=disnake.Colour(0xb8e986), description="If a player doesn't die by tomorrow, the game will end in a draw.")

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


    votedict = {}
    options = []
    for i in var[ctx.guild.id]["players"]:
        v = Player.get_player(i, var[ctx.guild.id]["playerdict"])
        if (v.dead):
            continue

        user = bot.get_user(i)
        votedict[f"{user.name}#{user.discriminator}"] = i
        options.append(SelectOption(label=f"{user.name}#{user.discriminator}", description=f"Click here to vote against {user.name}#{user.discriminator}"))

    class DD(disnake.ui.Select):
        def __init__(self, opt:list):
            super().__init__(
                placeholder="Vote someone...",
                options = opt    
            )

        async def callback(self, interaction:MessageInteraction):
            user = bot.get_user(votedict[self.values[0]])
            await voteMember(interaction, user)

    class DDV(disnake.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(DD(options))


    embed = disnake.Embed(title=f"**It is time to vote :ballot_box:. {int(aliveplayers / 2 + 1)} votes are needed to send someone to trial :judge:.**", colour=disnake.Colour(0xf5a623))

    embed.set_image(url="https://cdn.discordapp.com/attachments/765738640554065962/913554920416874506/IMG_0097.png")
    embed.set_footer(text="Use the dropdown to vote.")
    await ctx.send(embed=embed, view=DDV())

    var[ctx.guild.id]["voting"] = True
    timer = 45.0
    while (timer >= 0.0):
        await asyncio.sleep(0.1)
        timer = timer - 0.1

    if (var[ctx.guild.id]["novotes"] == False):
        dad = var[ctx.guild.id]["gday"]
        embed = disnake.Embed(title=f"**It is Night {dad} :crescent_moon:.**", colour=disnake.Colour(0x1f0050))

        embed.set_image(url="https://cdn.discordapp.com/attachments/765738640554065962/912890903545397258/IMG_0089.png")
        message = ""
        for i in var[ctx.guild.id]["playerdict"].values():
            if (i.dead==False and i.id != 0):
                message += f"{bot.get_user(i.id).mention}\n" 
        if (message == ""):
            message = ":x: **None**"

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
            message = ":x: **None**"
        embed.add_field(name="**Graveyard <:rip:872284978354978867>:**", value=message, inline=True)
        
        await ctx.send(embed=embed)

        await lock(ctx)
        if (noImpsNoCrews(ctx.guild) and len(getPsychos(ctx.guild)) == 1):
            b = await EndGame(EndReason.Psychopath, var[ctx.guild.id]["channel"].guild)
            await var[ctx.guild.id]["channel"].send(embed=b)
            await var[ctx.guild.id]["startchannel"].send(embed=b)
            perm = disnake.PermissionOverwrite()
            perm.read_messages = True
            perm.send_messages = True

            role = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
            roled = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

            await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
            perm.send_messages = False
            await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

            var[ctx.guild.id]["result"] = True
            var[ctx.guild.id]["ind"] -= 1
            return
        if (len(getTownies(ctx.guild)) == 0 and len(getMaf(ctx.guild)) == 0 and len(getPsychos(ctx.guild)) == 0):
            b = await EndGame(EndReason.Draw, var[ctx.guild.id]["channel"].guild)
            await var[ctx.guild.id]["channel"].send(embed=b)
            await var[ctx.guild.id]["startchannel"].send(embed=b)
            perm = disnake.PermissionOverwrite()
            perm.read_messages = True
            perm.send_messages = True

            role = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
            roled = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

            await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
            perm.send_messages = False
            await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

            var[ctx.guild.id]["result"] = True
            var[ctx.guild.id]["ind"] -= 1
            return
        if (len(getTownies(ctx.guild)) == 0  and len(getPsychos(ctx.guild)) == 0):
            b = await EndGame(EndReason.MafiaWins, var[ctx.guild.id]["channel"].guild)
            await var[ctx.guild.id]["channel"].send(embed=b)
            await var[ctx.guild.id]["startchannel"].send(embed=b)
            perm = disnake.PermissionOverwrite()
            perm.read_messages = True
            perm.send_messages = True

            role = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
            roled = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

            await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
            perm.send_messages = False
            await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

            var[ctx.guild.id]["result"] = True
            var[ctx.guild.id]["ind"] -= 1
            return
        elif (len(getMaf(ctx.guild)) == 0 and len(getPsychos(ctx.guild)) == 0):
            b = await EndGame(EndReason.TownWins, var[ctx.guild.id]["channel"].guild)
            await var[ctx.guild.id]["channel"].send(embed=b)
            await var[ctx.guild.id]["startchannel"].send(embed=b)
            perm = disnake.PermissionOverwrite()
            perm.read_messages = True
            perm.send_messages = True

            role = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
            roled = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

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


async def voteMember(ctx, member):
  
    try:
        var[ctx.guild.id]["test"]
    except:
        var[ctx.guild.id] = copy.deepcopy(temp)

    mm = Player.get_player(ctx.author.id, var[ctx.guild.id]["playerdict"])


    if (mm.dead == True):
        embed = disnake.Embed(title="**Sorry, you can't vote being dead.**", colour=disnake.Colour(0xcce0ff), description="**Please be alive then vote.**")

        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896419059988578344/downvote.png")
        embed.set_footer(text="Type `/vote` to vote.", icon_url=ctx.author.avatar.url)
        await ctx.response.send_message(embed=embed, ephemeral=True)
        return
    if (mm.id in var[ctx.guild.id]["guiltyers"] == True):
        embed = disnake.Embed(title="**You're too guilty to vote.**", colour=disnake.Colour(0xcce0ff), description="**You can vote again tomorrrow.**")

        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896419059988578344/downvote.png")
        embed.set_footer(text="Don't lynch the Jester.", icon_url=ctx.author.avatar.url)
        await ctx.response.send_message(embed=embed, ephemeral=True)
        return

    if (var[ctx.guild.id]["night"] == True or var[ctx.guild.id]["voting"] == False or var[ctx.guild.id]["gday"] == 1 or var[ctx.guild.id]["started"] == False or var[ctx.guild.id]["novotes"] == True):
        embed = disnake.Embed(title="**Sorry, you can't vote right now.**", colour=disnake.Colour(0xcce0ff), description="**Please vote someone during the allocated time period.**")

        embed.set_thumbnail(url="https://cdn.disordapp.com/attachments/765738640554065962/896419059988578344/downvote.png")
        embed.set_footer(text="Type /vote to vote.", icon_url=ctx.author.avatar.url)
        await ctx.response.send_message(embed=embed, ephemeral=True)
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
    embed = disnake.Embed(title=f"**{ctx.author.name} has voted against {member.name}**", colour=disnake.Colour(0xcce0ff), description=f"**{member.name} now has {str(q[int(member.id)])} vote(s) on them.**")

    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896418860427771975/upvote.png")
    embed.set_footer(text=f"{str(int(aliveplayers / 2) + 1)} votes are needed to send someone to trial.", icon_url=ctx.author.avatar.url)
    await ctx.response.send_message(embed=embed)

    var[ctx.guild.id]["votethreads"] += 1

    if (var[ctx.guild.id]["votethreads"] > 1):
        return


    if (var[ctx.guild.id]["voted"][int(member.id)] >= int(aliveplayers / 2 + 1)):
        var[ctx.guild.id]["novotes"] = True
        embed = disnake.Embed(title=f"{member.name} has been put on trial.", colour=disnake.Colour(0xfd9f03), description="**You have 20 seconds to defend yourself.**")

        embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/878813918284361768/unknown.png")
        embed.set_thumbnail(url=member.avatar.url)
        
        if (var[ctx.guild.id]["night"] == True):
            await ctx.channel.send("someone voted.")
            return
        await ctx.channel.send(embed=embed)
        await asyncio.sleep(20)

        var[ctx.guild.id]["trialuser"] = member.id
        var[ctx.guild.id]["guyontrial"] = member.id
        var[ctx.guild.id]["innoers"] = []
        var[ctx.guild.id]["guiltyers"] = []
        
        class Confirm(disnake.ui.View):
            def __init__(self):
               super().__init__(timeout=10)

            @disnake.ui.button(label="Guilty", style=ButtonStyle.red)
            async def guilty(self, button, inter):
                r = inter.guild.id
                if (inter.author.id == var[r]["trialuser"]):
                    await inter.response.send_message(content="You can't mark yourself as guilty. Why would you, anyway?", ephemeral=True)
                    return
                if (inter.author.id not in var[r]["players"]):
                    await inter.response.send_message(content="YOU'RE NOT EVEN IN THE GAME--", ephemeral=True)
                    return
                if (Player.get_player(inter.author.id, var[inter.guild.id]["playerdict"]).dead == True):
                    await inter.response.send_message(content="You're dead.", ephemeral=True)
                    return

                if (inter.author.id in var[r]["abstainers"]):
                    var[r]["abstainers"].remove(inter.author.id)
                elif (inter.author.id in var[r]["innoers"]):
                    var[r]["innoers"].remove(inter.author.id)
                elif (inter.author.id in var[r]["guiltyers"]):
                    var[r]["guiltyers"].remove(inter.author.id)

                var[r]["guiltyers"].append(inter.author.id)
                b = bot.get_user(var[r]["guyontrial"]).name 
                await inter.response.send_message(content=f"You have marked {b} as **Guilty.**", ephemeral=True)

                embed = disnake.Embed(title=f"{inter.author.name} has voted.", colour=disnake.Colour(0xcce0ff))

                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896418860427771975/upvote.png")
                embed.set_footer(text="What did they vote for?", icon_url=inter.author.avatar.url)
                await var[r]["channel"].send(embed=embed)
             
            @disnake.ui.button(label="Innocent", style=ButtonStyle.green)
            async def inno(self, button, inter):
                r = inter.guild.id
                if (inter.author.id == var[r]["trialuser"]):
                    await inter.response.send_message(content="You can't mark yourself as innocent.", ephemeral=True)
                    return
                if (inter.author.id not in var[r]["players"]):
                    await inter.response.send_message(content="YOU'RE NOT EVEN IN THE GAME--", ephemeral=True)
                    return
                if (Player.get_player(inter.author.id, var[inter.guild.id]["playerdict"]).dead == True):
                    await inter.response.send_message(content="You're dead.", ephemeral=True)
                    return

                if (inter.author.id in var[r]["abstainers"]):
                    var[r]["abstainers"].remove(inter.author.id)
                elif (inter.author.id in var[r]["innoers"]):
                    var[r]["innoers"].remove(inter.author.id)
                elif (inter.author.id in var[r]["guiltyers"]):
                    var[r]["guiltyers"].remove(inter.author.id)

                var[r]["innoers"].append(inter.author.id)
                b = bot.get_user(var[r]["guyontrial"]).name 
                await inter.response.send_message(content=f"You have marked {b} as **Innocent.**", ephemeral=True)

                embed = disnake.Embed(title=f"{inter.author.name} has voted.", colour=disnake.Colour(0xcce0ff))

                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896418860427771975/upvote.png")
                embed.set_footer(text="What did they vote for?", icon_url=inter.author.avatar.url)
                await var[r]["channel"].send(embed=embed)

            @disnake.ui.button(label="Neat button :)", style=ButtonStyle.blurple)
            async def idiotic(self, button, inter):
                await inter.response.send_message("Check your DMs.", ephemeral=True)
                embed = disnake.Embed(title="Doing neat Discord magic...", description="Do not leave this page, as it's doing some epic Discord magic.")
                msg = await inter.author.send(embed=embed)
                embed.title="Success!"
                embed.description="The bot has succesfully wasted 15 seconds of an idiot's life."
                await asyncio.sleep(15)
                await msg.edit(embed=embed)

        embed = disnake.Embed(title=f"**It is time to decide on the fate of {member.name}.**", colour=disnake.Colour(0xffdea4), description="Use the buttons to mark the player.")

        embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/879072513643151375/unknown.png")
        embed.set_thumbnail(url=member.avatar.url)
        await ctx.channel.send(embed=embed, view=Confirm())
        
        var[ctx.guild.id]["guiltyinno"] = True
        for i in var[ctx.guild.id]["players"]:
            var[ctx.guild.id]["abstainers"].append(i)   

        trialtimer = 10.00
        while (trialtimer >= 0.0):
            await asyncio.sleep(0.1)
            trialtimer -= 0.1

        var[ctx.guild.id]["votethreads"] -= 1

        y = len(var[ctx.guild.id]["guiltyers"])
        x = len(var[ctx.guild.id]["innoers"])

        # print(y)
        # print(x)

        if (y > x):
            embed = disnake.Embed()
            if (Player.get_player(member.id, var[ctx.guild.id]["playerdict"]).role == "Jester"):
                embed = disnake.Embed(title=f"**{member.name}#{member.discriminator} has been lynched**", description="Their role was, **Jester** <:jesticon2:889968373612560394>.", colour=disnake.Colour(0x90ecff))
                
                Player.get_player(member.id, var[ctx.guild.id]["playerdict"]).death = DeathReason.Hanged
                
                if (getWill(Player.get_player(member.id, var[ctx.guild.id]["playerdict"]).will) != ""):
                    embed.add_field(name="We found a will next to their body :scroll:.", value=getWill(Player.get_player(member.id, var[ctx.guild.id]["playerdict"]).will), inline=False)

                message = ""
                for i in copy.copy(var[ctx.guild.id]["guiltyers"]):

                    if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).id in var[ctx.guild.id]["guiltyers"] == True):
                        continue
                    if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).dead == True):
                        continue
                    if (i == var[ctx.guild.id]["mayor"]):
                        message += f"{bot.get_user(i).mention} - **Mayor** <:mayoricon:922566007946629131>\n"
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
                        message += f"{bot.get_user(i).mention} - **Mayor** <:mayoricon:922566007946629131>\n"
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
                            message += f"{bot.get_user(i).mention} - **Mayor** <:mayoricon:922566007946629131>\n"
                        else:
                            message += f"{bot.get_user(i).mention}\n"

                if (message == ""):
                    message = ":x: None"

                embed.add_field(name="Abstained ❓", value=message)

                embed.set_image(url="https://images-ext-2.discordapp.net/external/LlOBlIZEHHfRmfQn8_dhpUD6gN0CUWMecRcDZjd9CTs/%3Fwidth%3D890%26height%3D701/https/media.discordapp.net/attachments/765738640554065962/877706810763657246/unknown.png")
                embed.set_thumbnail(url=member.avatar.url)

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
                            embed = disnake.Embed(title="**You have successfully gotten your target lynched!**", colour=disnake.Colour(0x39556b))

                            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/873940243219361792.png?v=1")
                            embed.set_footer(text="Your win condition has now been fulfilled.", icon_url=bot.get_user(i.id).avatar.url)
                            await bot.get_user(i.id).send(embed=embed)
                            i.wins = True

                ijf = var[ctx.guild.id]["playerdict"]
                a = var[ctx.guild.id]["emoji"][Player.get_player(member.id, ijf).role.lower()]
                
                embed = disnake.Embed(title=f"**{member.name}#{member.discriminator} has been lynched**", description = f"Their role was, **{Player.get_player(member.id, ijf).role.capitalize()} {a}**.", colour=disnake.Colour(0x90ecff))
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
                        message += f"{bot.get_user(i).mention} - **Mayor** <:mayoricon:922566007946629131>\n"
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
                        message += f"{bot.get_user(i).mention} - **Mayor** <:mayoricon:922566007946629131>\n"
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
                            message += f"{bot.get_user(i).mention} - **Mayor** <:mayoricon:922566007946629131>\n"
                        else:
                            message += f"{bot.get_user(i).mention}\n"

                if (message == ""):
                    message = ":x: None"

                embed.add_field(name="Abstained ❓", value=message)

                embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/877706810763657246/unknown.png?width=890&height=701")
                embed.set_thumbnail(url=member.avatar.url)


            await ctx.channel.send(embed=embed)
            
            embed = disnake.Embed(title="**You were lynched by the Town :knot:.**", colour=disnake.Colour(0x207aac), description="**You have died <:rip:878415658885480468>**.")

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/LlOBlIZEHHfRmfQn8_dhpUD6gN0CUWMecRcDZjd9CTs/%3Fwidth%3D890%26height%3D701/https/media.discordapp.net/attachments/765738640554065962/877706810763657246/unknown.png?width=805&height=634")
            embed.set_footer(text="Rest in peace.", icon_url=member.avatar.url)
            await member.send(embed=embed)
            var[ctx.guild.id]["daysnokill"] = 0
            if (Player.get_player(member.id, var[ctx.guild.id]["playerdict"]).role == "Jester"):
                await asyncio.sleep(2)
                embed = disnake.Embed(title="**The Jester will get their revenge!!!**", colour=disnake.Colour(0xffc3e7), description="**All guilties and abstainers will be distracted the following night and will be unable to vote tomorrow.**")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/872187561597075476.png?v=1")
                embed.set_footer(text="Don't lynch the Jester.")
                Player.get_player(member.id, var[ctx.guild.id]["playerdict"]).wins = True
                Player.get_player(member.id, var[ctx.guild.id]["playerdict"]).jesterwin = True
                await ctx.channel.send(embed=embed)

            member = await ctx.guild.fetch_member(member.id)

            Player.get_player(member.id, var[ctx.guild.id]["playerdict"]).dead = True
            await member.add_roles(disnake.utils.get(var[ctx.guild.id]["guildg"].roles, name="[Anarchic] Dead"))
            await member.remove_roles(disnake.utils.get(var[ctx.guild.id]["guildg"].roles, name="[Anarchic] Player"))

        elif (y < x):
            embed = disnake.Embed(title=f"**{member.name}** has been pardoned.", colour=disnake.Colour(0x79021), description="**Hopefully the town doesnt regret this decision later...**")
            
            for i in var[ctx.guild.id]["playerdict"].values():
                i.jesterwin = False

            message = ""
            for i in var[ctx.guild.id]["guiltyers"]:
                if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).dead == True):
                    continue
                if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).id in var[ctx.guild.id]["guiltyers"] == True):
                        continue

                if (i == var[ctx.guild.id]["mayor"]):
                    message += f"{bot.get_user(i).mention} - **Mayor** <:mayoricon:922566007946629131>\n"
                else:
                    message += f"{bot.get_user(i).mention}\n"

            if (message == ""):
                message = ":x: None"

            embed.add_field(name="Guilty ✅", value=message)

            message = ""
            for i in var[ctx.guild.id]["innoers"]:
                if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).id in var[ctx.guild.id]["guiltyers"] == True):
                    continue

                if (i == var[ctx.guild.id]["mayor"]):
                    message += f"{bot.get_user(i).mention} - **Mayor** <:mayoricon:922566007946629131>\n"
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
                        message += f"{bot.get_user(i).mention} - **Mayor** <:mayoricon:922566007946629131>\n"
                    else:
                        message += f"{bot.get_user(i).mention}\n"

            if (message == ""):
                message = ":x: None"

            embed.add_field(name="Abstained ❓", value=message)

            embed.set_thumbnail(url=member.avatar.url)
            await ctx.channel.send(embed=embed)
        elif (y == x):
            embed = disnake.Embed(title=f"**{member.name}** has been pardoned by a tie.", colour=disnake.Colour(0x79021), description="**Hopefully the town doesnt regret this decision later...**")
                
            for i in var[ctx.guild.id]["playerdict"].values():
                i.jesterwin = False

            message = ""
            for i in var[ctx.guild.id]["guiltyers"]:
                if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).dead == True):
                    continue
                if (Player.get_player(i, var[ctx.guild.id]["playerdict"]).id in var[ctx.guild.id]["guiltyers"] == True):
                    continue
                if (i == var[ctx.guild.id]["mayor"]):
                    message += f"{bot.get_user(i).mention} - **Mayor** <:mayoricon:922566007946629131>\n"
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
                    message += f"{bot.get_user(i).mention} - **Mayor** <:mayoricon:922566007946629131>\n"
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
                        message += f"{bot.get_user(i).mention} - **Mayor** <:mayoricon:922566007946629131>\n"
                    else:
                        message += f"{bot.get_user(i).mention}\n"

            if (message == ""):
                message = ":x: None"

            embed.add_field(name="Abstained ❓", value=message)
            
            embed.set_thumbnail(url=member.avatar.url)
            await ctx.channel.send(embed=embed)

        await asyncio.sleep(2)
        if (noImpsNoCrews(ctx.guild) and len(getPsychos(ctx.guild)) == 1):
            b = await EndGame(EndReason.Psychopath, var[ctx.guild.id]["channel"].guild)
            await var[ctx.guild.id]["channel"].send(embed=b)
            await var[ctx.guild.id]["startchannel"].send(embed=b)
            perm = disnake.PermissionOverwrite()
            perm.read_messages = True
            perm.send_messages = True

            role = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
            roled = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

            await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
            perm.send_messages = False
            await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

            var[ctx.guild.id]["result"] = True
            return
        if (len(getTownies(ctx.guild)) == 0 and len(getMaf(ctx.guild)) == 0 and len(getPsychos(ctx.guild)) == 0):
            b = await EndGame(EndReason.Draw, var[ctx.guild.id]["channel"].guild)
            await var[ctx.guild.id]["channel"].send(embed=b)
            await var[ctx.guild.id]["startchannel"].send(embed=b)
            perm = disnake.PermissionOverwrite()
            perm.read_messages = True
            perm.send_messages = True

            role = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
            roled = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

            await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
            perm.send_messages = False
            await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

            var[ctx.guild.id]["result"] = True
            return
        if (len(getTownies(ctx.guild)) == 0  and len(getPsychos(ctx.guild)) == 0):
            b = await EndGame(EndReason.MafiaWins, var[ctx.guild.id]["channel"].guild)
            await var[ctx.guild.id]["channel"].send(embed=b)
            await var[ctx.guild.id]["startchannel"].send(embed=b)
            perm = disnake.PermissionOverwrite()
            perm.read_messages = True
            perm.send_messages = True

            role = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
            roled = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

            await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
            perm.send_messages = False
            await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

            var[ctx.guild.id]["result"] = True
            return
        elif (len(getMaf(ctx.guild)) == 0 and len(getPsychos(ctx.guild)) == 0):
            b = await EndGame(EndReason.TownWins, var[ctx.guild.id]["channel"].guild)
            await var[ctx.guild.id]["channel"].send(embed=b)
            await var[ctx.guild.id]["startchannel"].send(embed=b)
            perm = disnake.PermissionOverwrite()
            perm.read_messages = True
            perm.send_messages = True

            role = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
            roled = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

            await var[ctx.guild.id]["channel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["channel"].set_permissions(roled, overwrite=perm)
            perm.send_messages = False
            await var[ctx.guild.id]["diechannel"].set_permissions(role, overwrite=perm)
            await var[ctx.guild.id]["diechannel"].set_permissions(roled, overwrite=perm)

            var[ctx.guild.id]["result"] = True
            return

        dad = var[ctx.guild.id]["gday"]
        embed = disnake.Embed(title=f"**It is Night {dad} :crescent_moon:.**", colour=disnake.Colour(0x1f0050))

        embed.set_image(url="https://cdn.discordapp.com/attachments/765738640554065962/912890903545397258/IMG_0089.png")
        message = ""
        for i in var[ctx.guild.id]["playerdict"].values():
            if (i.dead==False and i.id != 0):
                message += f"{bot.get_user(i.id).mention}\n" 
        if (message == ""):
            message = ":x: **None**"

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
            message = ":x: **None**"
        embed.add_field(name="**Graveyard <:rip:872284978354978867>:**", value=message, inline=True)
        
        await ctx.channel.send(embed=embed)
        await lock(ctx.channel)
        for value in var[ctx.guild.id]["playerdict"].values():
            value.voted = False
        
        var[ctx.guild.id]["voting"] = False
        var[ctx.guild.id]["ind"] -= 1
        await night(ctx)

# @vote.sub_command(
#     name="letter",
#     description="Vote a player's letter to lynch them",
#     options=[
#         Option('letter', 'The player\'s letter', OptionType.string, True)
#         ]
# )
# async def voteLetter(ctx, letter=None):
#     try:
#         var[ctx.guild.id]["test"]
#     except:
#         var[ctx.guild.id] = copy.deepcopy(temp)


#     if (letter is None or letter not in var[ctx.guild.id]["votingemoji"]):
#         embed = disnake.Embed(title="**Sorry, that isn't a valid letter.**", colour=disnake.Colour(0xcce0ff), description="**Please choose a valid player that is alive in the game.**")

#         embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896419059988578344/downvote.png")
#         embed.set_footer(text="Type `/vote` to vote.", icon_url=ctx.author.avatar.url)
#         await ctx.response.send_message(embed=embed, ephemeral=True)
#         return

#     realletter = var[ctx.guild.id]["votingemoji"][letter]

#     if (realletter in var[ctx.guild.id]["players"]):
#         if (ctx.channel.name == "town-square"):
#             e = random.uniform(0.2, 0.8)
#             await asyncio.sleep(e)
#             if (var[ctx.guild.id]["voting"] == True and var[ctx.guild.id]["gday"] != 1 and var[ctx.guild.id]["started"] == True and var[ctx.guild.id]["novotes"] == False):
#                 if (Player.get_player(realletter.id, var[ctx.guild.id]["playerdict"]).dead == True):
#                     embed = disnake.Embed(title="**Sorry, you can't vote someone dead.**", colour=disnake.Colour(0xcce0ff), description="**Please choose a valid player that is alive in the game.**")

#                     embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896419059988578344/downvote.png")
#                     embed.set_footer(text="Type `/vote` to vote.", icon_url=ctx.author.avatar.url)
#                     await ctx.response.send_message(embed=embed, ephemeral=True)
#                     return
#                 mm = Player.get_player(ctx.author.id, var[ctx.guild.id]["playerdict"])

#                 if (mm.dead == True):
#                     embed = disnake.Embed(title="**Sorry, you can't vote being dead.**", colour=disnake.Colour(0xcce0ff), description="**Please choose a valid player that is alive in the game.**")

#                     embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896419059988578344/downvote.png")
#                     embed.set_footer(text="Type `/vote` to vote.", icon_url=ctx.author.avatar.url)
#                     await ctx.response.send_message(embed=embed, ephemeral=True)
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

#                 embed = disnake.Embed(title=f"**{ctx.author.name} has voted against {us.name}**", colour=disnake.Colour(0xcce0ff), description=f"**{us.name} now has {str(q[int(us.id)])} vote(s) on them.**")

#                 embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896418860427771975/upvote.png")
#                 embed.set_footer(text=f"{str(int(aliveplayers / 2) + 1)} votes are needed to send someone to trial.", icon_url=ctx.author.avatar.url)
#                 await ctx.response.send_message(embed=embed)
#             else:
#                 embed = disnake.Embed(title="**Sorry, you can't vote right now.**", colour=disnake.Colour(0xcce0ff), description="**Please choose a valid player that is alive in the game.**")

#                 embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896419059988578344/downvote.png")
#                 embed.set_footer(text="Type `/vote` to vote.", icon_url=ctx.author.avatar.url)
#                 await ctx.response.send_message(embed=embed, ephemeral=True)
#                 return

#             if (var[ctx.guild.id]["voted"][int(us.id)] >= int(aliveplayers / 2 + 1)):
#                 us = bot.get_user(realletter)
#                 var[ctx.guild.id]["novotes"] = True
#                 embed = disnake.Embed(title=f"{us.name}has been put on trial.", colour=disnake.Colour(0xfd9f03), description="**You have 20 seconds to defend yourself.**")

#                 embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/878813918284361768/unknown.png")
#                 embed.set_thumbnail(url=us.avatar.url)
                
#                 await ctx.channel.send(embed=embed)
#                 trialtimer = 20.0
#                 while (trialtimer >= 0.0):
#                     await asyncio.sleep(0.1)
#                     trialtimer = trialtimer - 0.1
                    
#                 embed = disnake.Embed(title=f"**It is time to decide on the fate of {us.name}.**", colour=disnake.Colour(0xffdea4), description=":white_check_mark: **- Guilty**\n:x: **- Innocent**")

#                 embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/879072513643151375/unknown.png")
#                 embed.set_thumbnail(url=us.avatar.url)
#                 msg = await ctx.channel.send(embed=embed)
#                 await msg.add_reaction("✅")
#                 await msg.add_reaction("❌")
#                 trialtimer = 20.00
#                 while (trialtimer >= 0.0):
#                     await asyncio.sleep(0.1)
#                     trialtimer -= 0.1

#                 msgg = await ctx.channel.fetch_message(msg.id)
#                 reaction:disnake.Reaction = get(msgg.reactions, emoji="✅")
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
#                     embed = disnake.Embed()
#                     if (Player.get_player(us.id, var[ctx.guild.id]["playerdict"]).role == "Jester"):
#                         embed = disnake.Embed(title=f"**{us.name}#{us.discriminator} has been lynched**", description="Their role was, **Jester**.", colour=disnake.Colour(0x90ecff))

#                         embed.set_image(url="https://images-ext-2.discordapp.net/external/LlOBlIZEHHfRmfQn8_dhpUD6gN0CUWMecRcDZjd9CTs/%3Fwidth%3D890%26height%3D701/https/media.discordapp.net/attachments/765738640554065962/877706810763657246/unknown.png")
#                         embed.set_thumbnail(url=us.avatar.url)
#                         for i in var[ctx.guild.id]["players"]:
#                             reaction:disnake.Reaction = get(msgg.reactions, emoji="✅")
#                             if (bot.get_user(i) in await reaction.users().flatten()):
#                                 Player.get_player(i, var[ctx.guild.id]["playerdict"]).guiltyvoter = True           
#                                 print(Player.get_player(i, var[ctx.guild.id]["playerdict"]).guiltyvoter)      
                    
#                     else:

#                         for i in var[ctx.guild.id]["playerdict"].values():
#                             if (i.role.lower() == "headhunter"):
#                                 if (i.hhtarget == Player.get_player(us.id, var[ctx.guild.id]["playerdict"])):
#                                     embed = disnake.Embed(title="**You have successfully gotten your target lynched!**", colour=disnake.Colour(0x39556b))

#                                     embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/873940243219361792.png?v=1")
#                                     embed.set_footer(text="Your win condition has now been fulfilled.", icon_url=bot.get_user(i.id).avatar.url)
#                                     await bot.get_user(i.id).send(embed=embed)
#                                     i.wins = True

#                         ijf = var[ctx.guild.id]["playerdict"]
#                         em = var[ctx.guild.id]["emoji"]
#                         embed = disnake.Embed(title=f"**{us.name}#{us.discriminator} has been lynched**", description = f"Their role was, **{Player.get_player(us.id, ijf).role.capitalize()} {em[Player.get_player(us.id, ijf).role.lower()]}**.", colour=disnake.Colour(0x90ecff))

#                         embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/877706810763657246/unknown.png?width=890&height=701")
#                         embed.set_thumbnail(url=us.avatar.url)


#                     await ctx.channel.send(embed=embed)
                    
#                     embed = disnake.Embed(title="**You were lynched by the Town :knot:.**", colour=disnake.Colour(0x207aac), description="**You have died <:rip:878415658885480468>**.")

#                     embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/LlOBlIZEHHfRmfQn8_dhpUD6gN0CUWMecRcDZjd9CTs/%3Fwidth%3D890%26height%3D701/https/media.discordapp.net/attachments/765738640554065962/877706810763657246/unknown.png?width=805&height=634")
#                     embed.set_footer(text="Rest in peace.", icon_url=us.avatar.url)
#                     await us.send(embed=embed)
#                     if (Player.get_player(us.id, var[ctx.guild.id]["playerdict"]).role == "Jester"):
#                         await asyncio.sleep(2)
#                         embed = disnake.Embed(title="**The Jester will get their revenge!!!**", colour=disnake.Colour(0xffc3e7), description="**All guilties and abstainers will be distracted the following night and will be unable to vote tomorrow.**")

#                         embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/872187561597075476.png?v=1")
#                         embed.set_footer(text="Don't lynch the Jester.")
#                         Player.get_player(us.id, var[ctx.guild.id]["playerdict"]).wins = True
#                         Player.get_player(us.id, var[ctx.guild.id]["playerdict"]).jesterwin = True
#                         await ctx.channel.send(embed=embed)

#                     Player.get_player(us.id, var[ctx.guild.id]["playerdict"]).dead = True
#                     await us.add_roles(disnake.utils.get(var[ctx.guild.id]["guildg"].roles, name="[Anarchic] Dead"))
#                     await us.remove_roles(disnake.utils.get(var[ctx.guild.id]["guildg"].roles, name="[Anarchic] Player"))

#                 elif (y < x):
#                     embed = disnake.Embed(title=f"**{us.name}** has been pardoned.", colour=disnake.Colour(0x79021), description="**Hopefully the town doesnt regret this decision later...**")
#                     embed.set_thumbnail(url=us.avatar.url)
#                     await ctx.channel.send(embed=embed)
#                 elif (y == x):
#                     embed = disnake.Embed(title=f"**{us.name}** has been pardoned by a tie.", colour=disnake.Colour(0x79021), description="**Hopefully the town doesnt regret this decision later...**")
#                     embed.set_thumbnail(url=us.avatar.url)
#                     await ctx.channel.send(embed=embed)

#                 await asyncio.sleep(2)
#                 if (len(getTownies(ctx.guild)) == 0 and len(getMaf(ctx.guild)) == 0):
#                     b = await EndGame(EndReason.Draw, ctx.guild)
#                     await var[ctx.guild.id]["channel"].send(embed=b)
#                     perm = disnake.PermissionOverwrite()
#                     perm.read_messages = True
#                     perm.send_messages = True

#                     role = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
#                     roled = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

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
#                     perm = disnake.PermissionOverwrite()
#                     perm.read_messages = True
#                     perm.send_messages = True

#                     role = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
#                     roled = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

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
#                     perm = disnake.PermissionOverwrite()
#                     perm.read_messages = True
#                     perm.send_messages = True

#                     role = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Player")
#                     roled = disnake.utils.get(var[ctx.guild.id]["channel"].guild.roles,name="[Anarchic] Dead")

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
#         embed = disnake.Embed(title="**Sorry, that player isn't in the game.**", colour=disnake.Colour(0xcce0ff), description="**Please choose a valid player that is alive in the game.**")

#         embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/765738640554065962/896419059988578344/downvote.png")
#         embed.set_footer(text="Type `/vote` to vote.", icon_url=ctx.author.avatar.url)
#         await ctx.response.send_message(embed=embed, ephemeral=True)
#         return

@commands.guild_only()
@bot.slash_command(
    name="end",
    description="Finalize the game to start a new one"
)
async def endGame(ctx:ApplicationCommandInteraction):

    try:
        var[ctx.guild.id]["test"]
    except:
        var[ctx.guild.id] = copy.deepcopy(temp)

    if (var[ctx.guild.id]["started"] == True):
        if (var[ctx.guild.id]["result"] == True):
            if (ctx.channel.category.name == "Anarchic"):
                if (ctx.channel.name == "town-square"):
                    if (ctx.channel == var[ctx.guild.id]["channel"]):
                        await ctx.response.defer()

                        embed = disnake.Embed(title="Thanks for playing **Anarchic**!", colour=disnake.Colour(0xe07d7e), description="**:clock10: Deleting the channels in 5 seconds. Enjoying the bot? Consider voting for us [here](https://top.gg/bot/887118309827432478/vote)!**")
                        embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/cBq_CGTA8KOw8vWobvuhZ3AKTEe0zii9yV2f7jZuLe0/%3Fwidth%3D374%26height%3D374/https/images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%253Fwidth%253D468%2526height%253D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")


                        embed.set_footer(text="Use /start to start another game.", icon_url=ctx.author.avatar.url)
                        
                        if (var[ctx.guild.id]["setupz"].lower() == "custom"):
                            embed.add_field(name="**__Note :pushpin:__**", value="*You don't earn silvers from custom games.*")
                        
                        await ctx.edit_original_message(embed=embed)
                        
                        guild:disnake.Guild = ctx.guild     

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

                        townsalive = 0
                        towns = 0

                        #Award to each player
                        for i in var[guild.id]["players"]:
                            if (str(i) not in cur):
                                cur[str(i)] = 0
                            if (var[guild.id]["setupz"].lower() != "custom"):
                                if (Player.get_player(i, var[guild.id]["playerdict"]).faction == Faction.Mafia):
                                    cur[str(i)] += mafaward
                                if (Player.get_player(i, var[guild.id]["playerdict"]).faction == Faction.Town):
                                    cur[str(i)] += townaward

                            if (Player.get_player(i, var[guild.id]["playerdict"]).faction == Faction.Town):
                                towns += 1
                                if (Player.get_player(i, var[guild.id]["playerdict"]).dead == False):
                                      townsalive += 1

                            if (cur[str(i)] >= 5000):
                                await Achievement.getAch("richPlayer").unlock(i, None, True)

                            val = tryGetValue(i, "gamesPlayed")
                            if (val == None):
                                val = 0

                            val += 1
                            if (val == 1):
                                await Achievement.getAch("firstGame").unlock(i, None, True)
                            if (val == 1000):
                                await Achievement.getAch("1000Games").unlock(i, None, True)

                        if (townsalive == towns):
                            for i in var[guilds.id]["players"]:
                                if (Player.get_player(i, var[guild.id]["playerdict"]).faction == Faction.Town):
                                    await Achievement.getAch("nobodyIsDead").unlock(i, None, True)

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
                            try:
                                await i.delete()
                            except:
                                pass

                        await ctx.channel.category.delete()

                        g = disnake.utils.get(guild.roles, name="[Anarchic] Player")
                        d = disnake.utils.get(guild.roles, name="[Anarchic] Dead")
                        s = disnake.utils.get(guild.roles, name="[Anarchic] Spectator")

                        await g.delete()
                        await s.delete()
                        await d.delete()

                        for i in var[ctx.guild.id]["joinq"]:
                            if (len(var[ctx.guild.id]["players"]) >= 10):
                                await bot.get_user(i).send("You were unable to join the game because it was full.")
                                continue
                            
                            var[ctx.guild.id]["players"].append(i)

                            var[ctx.guild.id]["playeremoji"][var[ctx.guild.id]["emojis"][var[ctx.guild.id]["index"]]] = ctx.author.id
                            var[ctx.guild.id]["votingemoji"][var[ctx.guild.id]["emojiz"][var[ctx.guild.id]["index"]]] = ctx.author.id
                            var[ctx.guild.id]["index"] += 1

                            guilds[str(ctx.author.id)]["guild"] = ctx.guild.id
                            guilds[str(ctx.author.id)]["joinedgame"] = True

                        for i in var[ctx.guild.id]["leaveq"]:
                            var[ctx.guild.id]["players"].remove(i)

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

                            guilds[str(ctx.author.id)]["guild"] = 0
                            guilds[str(ctx.author.id)]["vkicktarget"] = 0
                            guilds[str(ctx.author.id)]["joinedgame"] = False
                            for i in var[ctx.guild.id]["players"]:
                                if (guilds[str(i)]["vkicktarget"] == ctx.author.id):
                                    guilds[str(i)]["vkicktarget"] = 0


                        var[ctx.guild.id]["joinq"].clear()
                        var[ctx.guild.id]["leaveq"].clear()
                    else:
                        await ctx.response.send_message("I--", ephemeral=True)
                else:
                    await ctx.response.send_message("NO.", ephemeral=True)
            else:
                await ctx.response.send_message("There isn't a game in this channel.", ephemeral=True)
        else:
            await ctx.response.send_message("You can't forcibly end a game.", ephemeral=True)
    else:
        if (ctx.author.id == 839842855970275329 or ctx.author.id == 667189788620619826):
            if (ctx.channel.name == "town-square"):
                class Buttons(disnake.ui.View):
                    def __init__(self):
                        super().__init__()

                    @disnake.ui.button(label="Yes", style=ButtonStyle.red)
                    async def yes(self, button, inter):
                        for i in ctx.channel.category.channels:
                            await i.delete()

                        await ctx.channel.category.delete()

                    @disnake.ui.button(label="No", style=ButtonStyle.green)
                    async def no(self, button, inter):
                        return

                await ctx.response.send_message(content="This category may not be for Anarchic. Are you sure you want to continue?", view=Buttons())
        else:
            try:
                await ctx.response.send_message("You can't end a non-existent game.", ephemeral=True)
            except:
                pass

@commands.guild_only()
@bot.slash_command(    
    name="setup", # Defaults to function name
    description="Change the setup to have more fun",
    #  registration takes up to 1 hour
    options=[
        Option('setup', 'The setup\'s name', OptionType.string, True, choices=[
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
            OptionChoice("All Any", "any"),
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
        await inter.response.send_message("That isn't a setup...", ephemeral=True)
        return
    else:
        await _setup(inter, setup, True)

async def _setup(ctx, setup:str, inter=False):
    if (len(var[ctx.guild.id]["players"]) == 0):
        await ctx.response.send_message("There's nobody in the game!")

        return
    if (ctx.author.id != var[ctx.guild.id]["players"][0]):
        await ctx.response.send_message("Only the host can change the setup!")

        return

    await ctx.response.defer()

    if (setup.lower().replace(" ", "") in var[ctx.guild.id]["comps"]):
        embed = disnake.Embed(title="Somethings wrong here...", description="Contact the developer about this bug.")
        if (setup.lower().replace(" ", "") == "enforced"):
            embed = disnake.Embed(title="**Gamemode has been set to __Enforced <:enficon2:890339050865696798>__!**", description="", colour=disnake.Colour(0xcd95ff))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/O3tABe1id1w0dcI-B8MMo-DgXI9Co9xNaS6QSbjKU2o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/753967387149074543/c908a07ef8d6165ab31770e4b47f38ca.webp")
            embed.set_footer(text="Try /setups for a list of setups.", icon_url=ctx.author.avatar.url)

            embed.add_field(name="__**Enforced <:enficon2:890339050865696798> `(5P)`**__", value="**<:enficon2:890339050865696798> Enforcer**\n**<:docicon2:890333203959787580> Doctor**\n**<:townicon2:896431548717473812> Random Town**\n**:axe: Neutral Evil**\n**<:maficon2:891739940055052328> Mafioso**")
        elif (setup.lower().replace(" ", "") == "classic"):
            embed = disnake.Embed(title="**Gamemode has been set to __Classic :triangular_flag_on_post:__!**", colour=disnake.Colour(0xcd95ff))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/O3tABe1id1w0dcI-B8MMo-DgXI9Co9xNaS6QSbjKU2o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/753967387149074543/c908a07ef8d6165ab31770e4b47f38ca.webp")
            embed.set_footer(text="Try /setups for a list of setups.", icon_url=ctx.author.avatar.url)

            embed.add_field(name="__**Classic 🚩 `(5P)`**__", value="**<:copicon2:889672912905322516> Cop**\n**<:docicon2:890333203959787580> Doctor**\n**<:mayoricon:922566007946629131> Mayor**\n**<:jesticon2:889968373612560394> Jester**\n**<:maficon2:891739940055052328> Mafioso**")
        elif (setup.lower().replace(" ", "") == "execution"):
            embed = disnake.Embed(title="**Gamemode has been set to __Execution <:hhicon2:891429754643808276>__!**", colour=disnake.Colour(0xcd95ff))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/O3tABe1id1w0dcI-B8MMo-DgXI9Co9xNaS6QSbjKU2o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/753967387149074543/c908a07ef8d6165ab31770e4b47f38ca.webp")
            embed.set_footer(text="Try /setups for a list of setups.", icon_url=ctx.author.avatar.url)

            embed.add_field(name="**__Execution <:hhicon2:891429754643808276> `(6P)`__**", value="**<:copicon2:889672912905322516> Cop**\n**<:docicon2:890333203959787580> Doctor**\n**<:townicon2:896431548717473812> Random Town**\n**<:townicon2:896431548717473812> Random Town**\n**<:hhicon2:891429754643808276> Headhunter**\n**<:maficon2:891739940055052328> Mafioso**")
        elif (setup.lower().replace(" ", "") == "duet"):
            embed = disnake.Embed(title="**Gamemode has been set to __Duet <:consicon2:890336628269281350>__!**", colour=disnake.Colour(0xcd95ff))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/O3tABe1id1w0dcI-B8MMo-DgXI9Co9xNaS6QSbjKU2o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/753967387149074543/c908a07ef8d6165ab31770e4b47f38ca.webp")
            embed.set_footer(text="Try /setups for a list of setups.", icon_url=ctx.author.avatar.url)

            embed.add_field(name="__**Duet <:consicon2:890336628269281350> `(7P)`**__", value="**<:enficon2:890339050865696798> Enforcer**\n**<:docicon2:890333203959787580> Doctor**\n**:mag_right: Town Investigative**\n**<:townicon2:896431548717473812> Random Town**\n**<:townicon2:896431548717473812> Random Town**\n**<:maficon2:891739940055052328> Mafioso**\n**<:consicon2:890336628269281350> Consort**")
        elif (setup.lower().replace(" ", "") == "framed"):
            embed = disnake.Embed(title="**Gamemode has been set to __Framed <:frameicon2:890365634913902602>__**", colour=disnake.Colour(0xcd95ff))

            embed.set_footer(text="Try /setups for a list of setups.", icon_url=ctx.author.avatar.url)

            embed.add_field(name="**__Framed <:frameicon2:890365634913902602> `(7P)`__**", value="**<:copicon2:889672912905322516> Cop\n<:docicon2:890333203959787580> Doctor\n:mag_right: Town Investigative\n<:townicon2:896431548717473812> Random Town\n<:townicon2:896431548717473812> Random Town\n<:maficon2:891739940055052328> Mafioso\n<:frameicon2:890365634913902602> Framer**", inline=True)
        elif (setup.lower().replace(" ", "") == "legacy"):
            embed = disnake.Embed(title="**Gamemode has been set to __Legacy :sparkles:__!**", colour=disnake.Colour(0xcd95ff))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/O3tABe1id1w0dcI-B8MMo-DgXI9Co9xNaS6QSbjKU2o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/753967387149074543/c908a07ef8d6165ab31770e4b47f38ca.webp")
            embed.set_footer(text="Try /setups for a list of setups.", icon_url=ctx.author.avatar.url)

            embed.add_field(name="**__Legacy 🎪 `(8P)`__**", value="**<:copicon2:889672912905322516> Cop**\n**<:docicon2:890333203959787580> Doctor**\n**<:townicon2:896431548717473812> Random Town**\n**<:townicon2:896431548717473812> Random Town**\n**<:townicon2:896431548717473812> Random Town**\n**:axe: Neutral Evil**\n**<:maficon2:891739940055052328> Mafioso**\n**<:maficon2:890328238029697044> Random Mafia**")
        elif (setup.lower().replace(" ", "") == "scattered"):
            embed = disnake.Embed(title="**Gamemode has been set to __Scattered :diamond_shape_with_a_dot_inside:__!**", colour=disnake.Colour(0xcd95ff))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/O3tABe1id1w0dcI-B8MMo-DgXI9Co9xNaS6QSbjKU2o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/753967387149074543/c908a07ef8d6165ab31770e4b47f38ca.webp")
            embed.set_footer(text="Try /setups for a list of setups.", icon_url=ctx.author.avatar.url)

            embed.add_field(name="__**Scattered :diamond_shape_with_a_dot_inside: `(9P)`**__", value="**<:enficon2:890339050865696798> Enforcer**\n**<:docicon2:890333203959787580>  Doctor**\n**<:townicon2:896431548717473812> Random Town**\n**<:townicon2:896431548717473812> Random Town**\n**<:townicon2:896431548717473812> Random Town**\n**<:townicon2:896431548717473812> Random Town**\n**<:maficon2:891739940055052328> Mafioso**\n**<:maficon2:890328238029697044> Random Mafia**\n**<:hhicon2:891429754643808276> Headhunter**")
        elif (setup.lower().replace(" ", "") == "anarchy"):
            embed = disnake.Embed(title="**Gamemode has been set to __Anarchy :drop_of_blood:__!**", colour=disnake.Colour(0xcd95ff))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/O3tABe1id1w0dcI-B8MMo-DgXI9Co9xNaS6QSbjKU2o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/753967387149074543/c908a07ef8d6165ab31770e4b47f38ca.webp")
            embed.set_footer(text="Try /setups for a list of setups.", icon_url=ctx.author.avatar.url)

            embed.add_field(name="__**Anarchy :drop_of_blood: `(10P)`**__", value="**<:mayoricon:922566007946629131> Mayor**\n**<:docicon2:890333203959787580> Doctor**\n**:mag_right: Town Investigative**\n**:mag_right: Town Investigative**\n**<:townicon2:896431548717473812> Random Town**\n**<:townicon2:896431548717473812> Random Town**\n**<:maficon2:891739940055052328> Mafioso**\n**<:maficon2:890328238029697044> Random Mafia**\n**:axe: Neutral Evil**\n**:game_die: Any**")
        elif (setup.lower().replace(" ", "") == "ranked"):
            embed = disnake.Embed(title="**Gamemode has been set to __Ranked :star2:__!**", colour=disnake.Colour(0xcd95ff))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/O3tABe1id1w0dcI-B8MMo-DgXI9Co9xNaS6QSbjKU2o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/753967387149074543/c908a07ef8d6165ab31770e4b47f38ca.webp")
            embed.set_footer(text="Try /setups for a list of setups.", icon_url=ctx.author.avatar.url)

            embed.add_field(name="__**Ranked :star2: `(10P)`**__", value="**<:docicon2:890333203959787580> Doctor**\n**<:enficon2:890339050865696798> Enforcer**\n**:mag_right: Town Investigative**\n**:mag_right: Town Investigative**\n**<:townicon2:896431548717473812> Random Town**\n**<:townicon2:896431548717473812> Random Town**\n**<:townicon2:896431548717473812> Random Town**\n**<:maficon2:891739940055052328> Mafioso**\n**<:consicon2:890336628269281350> Consort**\n**<:frameicon2:890365634913902602> Framer**")
        elif (setup.lower().replace(" ", "") == "truth"):
            embed = disnake.Embed(title="**Gamemode has been set to __Truth <:consigicon2:896154845130666084>__!**", colour=disnake.Colour(0xcd95ff))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/O3tABe1id1w0dcI-B8MMo-DgXI9Co9xNaS6QSbjKU2o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/753967387149074543/c908a07ef8d6165ab31770e4b47f38ca.webp")
            embed.set_footer(text="Try /setups for a list of setups.", icon_url=ctx.author.avatar.url)

            embed.add_field(name="__**Truth <:consigicon2:896154845130666084> `(7P)`**__", value="**<:deticon2:889673135438319637> Detective**\n**<:docicon2:890333203959787580>  Doctor**\n**<:townicon2:896431548717473812> Random Town**\n**<:townicon2:896431548717473812> Random Town**\n**<:townicon2:896431548717473812> Random Town**\n**<:maficon2:890328238029697044> Mafioso**\n**<:consigicon2:896154845130666084> Consigliere**")
        elif (setup.lower().replace(" ", "") == "delta"):
            embed = disnake.Embed(title="You've accessed the secret beta gamemode.", description="wow thats really cool")
        elif (setup.lower().replace(" ", "") == "custom"):
            embed = disnake.Embed(title=f"**Gamemode has been set to __Custom__ :art: :paintbrush:!**", colour=disnake.Colour(0xb3ffdd))

            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/O3tABe1id1w0dcI-B8MMo-DgXI9Co9xNaS6QSbjKU2o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/753967387149074543/c908a07ef8d6165ab31770e4b47f38ca.webp")
            embed.set_footer(text="Try /setups for a list of setups.", icon_url=ctx.author.avatar.url)
            message = ""

            c = var[ctx.guild.id]["comps"]
            em = var[ctx.guild.id]["emoji"]
            for i in c["custom"]:
                if (i == "RT"):
                    message += "Random Town <:townicon2:896431548717473812>\n"
                elif (i == "RM"):
                    message += "Random Mafia <:maficon2:890328238029697044>\n"
                elif (i == "NE"):
                    message += "Neutral Evil :axe:\n"
                elif (i == "TI"):
                    message += "Town Investigative :mag_right:\n"
                elif (i == "TS"):
                    message += f"**Town Support 🛠️**\n"
                elif (i == "NK"):
                    message += f"**Neutral Killing :dagger:**\n"
                elif (i == "A"):
                    message += "**Any** :game_die:\n"
                else:
                    message += f"**{string.capwords(i)}** {em[i.lower()]}\n"

            if (message == ""):
                message = "**This setup is empty.**"

            embed.add_field(name=f"__**Custom**__ :art: :paintbrush:", value=message)

        if (embed.title == "Something's wrong here..." and inter == True):
            await ctx.edit_original_message(embed=embed, ephemeral=True)

        
        await ctx.edit_original_message(embed=embed)

        var[ctx.guild.id]["setupz"] = setup

    else:
        if (setup.lower().replace(" ", "") == "any" or setup.lower().replace(" ", "") == "allany"):
            var[ctx.guild.id]["setupz"] = "Any"
            embed = disnake.Embed(title="**Gamemode has been set to __All Any :game_die:__!**", color=0xCd95ff)
            embed.add_field(name="__**All Any :game_die: `(?P)`**__", value="**:game_die: Any x the amount of players playing :partying_face:**", inline=False)
            embed.add_field(name="**__Note :notepad_spiral:__**", value="**Night factions in a `5-6` player lobby can have up to `1` member.**\n\n**Night factions in a `7-9` player lobby can have up to `2` members.**\n\n**Night factions in a `10` player lobby can have up to `3` members.**", inline=False)
            embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/O3tABe1id1w0dcI-B8MMo-DgXI9Co9xNaS6QSbjKU2o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/753967387149074543/c908a07ef8d6165ab31770e4b47f38ca.webp")
            embed.set_footer(text="Try /setups for a list of setups.")
            # embed = disnake.Embed(title="**All Any is under maintainiance**", description="Please wait until we make All Any availiable again.", color=0xCd95ff)
            # embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/O3tABe1id1w0dcI-B8MMo-DgXI9Co9xNaS6QSbjKU2o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/753967387149074543/c908a07ef8d6165ab31770e4b47f38ca.webp")
            # embed.set_footer(text="Try /setups for a list of setups.")
            if (inter == False):
                await ctx.send(embed=embed)
            else:
                await ctx.edit_original_message(embed=embed)
        else:
            if (inter == False):
                await ctx.send("That setup doesn't exist. Get the setups using `/setups`.")
            else:
                await ctx.edit_original_message("That setup doesn't exist. Get the setups using `/setups`.", ephemeral=True)

@commands.guild_only()
@bot.slash_command()
async def custom(inter):
    pass

@commands.guild_only()
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

    embed = disnake.Embed(title=f"**Your current custom setup :art::paintbrush:**", colour=disnake.Colour(0xb3ffdd))

    embed.set_footer(text="You don't get silvers in a custom setup.", icon_url=inter.author.avatar.url)
    message = ""
    c = var[inter.guild.id]["comps"]
    em = var[inter.guild.id]["emoji"]

    for i in c["custom"]:
        if (i == "RT"):
            message += "Random Town <:townicon2:896431548717473812>\n"
        elif (i == "RM"):
            message += "Random Mafia <:maficon2:890328238029697044>\n"
        elif (i == "NE"):
            message += "Neutral Evil :axe:\n"
        elif (i == "TI"):
            message += "Town Investigative :mag_right:\n"
        elif (i == "TS"):
            message += f"**Town Support 🛠️**\n"
        elif (i == "NK"):
            message += f"**Neutral Killing :dagger:**\n"
        elif (i == "A"):
            message += "**Any** :game_die:\n"
        else:
            message += f"**{i}** {em[i.lower()]}\n"

    if (message == ""):
        message = "The setup is empty."

    embed.add_field(name=f"__**Custom :art::paintbrush: `(?P)`**__", value=message)

    try:
        await inter.response.send_message(embed=embed)
    except:
        await inter.response.send_message("The custom setup is empty.", ephemeral=True)

@commands.guild_only()
@custom.sub_command(
    description="Add a role to your setup",
    options=[
        Option("role", "The role you want to add", OptionType.string, True, choices=[
            OptionChoice("Cop", "Cop"),
            OptionChoice("Detective", "Detective"),
            OptionChoice("Lookout", "Lookout"),
            OptionChoice("Doctor", "Doctor"),
            OptionChoice("Enforcer", "Enforcer"),
            OptionChoice("Mayor", "Mayor"),
            OptionChoice("Tracker", "Tracker"),
            OptionChoice("Psychic", "Psychic"),
            OptionChoice("Attendant", "Attendant"),
            OptionChoice("Mafioso", "Mafioso"),
            OptionChoice("Janitor", "Janitor"),
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


    if (len(var[inter.guild.id]["players"]) == 0):
        await inter.response.send_message("The game is empty.", ephemeral=True)
        return

    if (inter.author.id != var[inter.guild.id]["players"][0]):
        await inter.response.send_message("Only the host can add roles to a custom setup.", ephemeral=True)
        return

    

    c = var[inter.guild.id]["comps"]

    if (c["custom"].count("Mafioso") == 1 and role == "Mafioso"):
        await inter.response.send_message("There can't be more than 1 Mafioso in a game.", ephemeral=True)
        return
    if (c["custom"].count("Mayor") == 1 and role == "Mayor"):
        await inter.response.send_message("There can't be more than 1 Mayor in a game.", ephemeral=True)
        return

    await inter.response.defer()

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
            message += "Neutral Evil :axe:\n"
        elif (i == "TI"):
            message += "Town Investigative :mag_right:\n"
        elif (i == "TS"):
            message += f"**Town Support 🛠️**\n"
        elif (i == "NK"):
            message += f"**Neutral Killing :dagger:**\n"
        elif (i == "A"):
            message += "Any :game_die:\n"
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

    embed = disnake.Embed(title=f"{thing} has been added to the setup!", colour=disnake.Colour(0xb3ffdd), description=f"__**Custom :art::paintbrush: `(?P)`**__\n**{message}**")

    embed.set_footer(text="You need at least 2 roles for a custom setup.", icon_url=inter.author.avatar.url)

    await inter.edit_original_message(embed=embed)

@commands.guild_only()
@custom.sub_command(
    description="Remove a role to your setup",
    options=[
        Option("role", "The role you want to remove", OptionType.string, True, choices=[
            OptionChoice("Cop", "Cop"),
            OptionChoice("Detective", "Detective"),
            OptionChoice("Lookout", "Lookout"),
            OptionChoice("Doctor", "Doctor"),
            OptionChoice("Enforcer", "Enforcer"),
            OptionChoice("Mayor", "Mayor"),
            OptionChoice("Tracker", "Tracker"),
            OptionChoice("Attendant", "Attendant"),
            OptionChoice("Psychic", "Psychic"),
            OptionChoice("Mafioso", "Mafioso"),
            OptionChoice("Janitor", "Janitor"),
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

    await inter.response.defer()

    try:
        if (inter.author.id != var[inter.guild.id]["players"][0]):
            await inter.response.send_message("Only the host can remove roles to a custom setup.", ephemeral=True)
    except:
        await inter.response.send_message("The game is empty.", ephemeral=True)

    c = var[inter.guild.id]["comps"]

    if (role not in c["custom"]):
        await inter.edit_original_message("That role isn't in the setup.")
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
            message += "Neutral Evil :axe:\n"
        elif (i == "TI"):
            message += "Town Investigative :mag_right:\n"
        elif (i == "TS"):
            message += f"**Town Support 🛠️**\n"
        elif (i == "NK"):
            message += f"**Neutral Killing :dagger:**\n"
        elif (i == "A"):
            message += "**Any** :game_die:\n"
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
        thing = f"**{string.capwords(role)}**"

    if (message == ""):
        message = "The setup is empty."

    embed = disnake.Embed(title=f"{thing} has been removed from the setup", colour=disnake.Colour(0xffc6c6), description=f"__**Custom :art::paintbrush: `(?P)`**__\n{message}")

    embed.set_footer(text="You need at least 2 roles in a custom setup.", icon_url=inter.author.avatar.url)

    await inter.edit_original_message(embed=embed)

@commands.guild_only()
@bot.slash_command(
    name="roles",
    description="View the roles of Anarchic"
)
async def roles(inter): 
    try:
        var[inter.guild.id]["test"]
    except:
        var[inter.guild.id] = copy.deepcopy(temp)

    await inter.response.defer()

    origin = disnake.Embed(title="**__List of Roles :performing_arts:__**", colour=disnake.Colour(0x8266dc), description="Here are a list of roles that are playable in **Anarchic 1.0.0**.")

    origin.set_thumbnail(url="https://images-ext-1.discordapp.net/external/S8kYnDiF37aks-RBlGNZVz6gbTasCOJy1R7IB9iE3NQ/%3F5765650006/https/www12.lunapic.com/editor/working/163036526867946112")

    origin.add_field(name="__**Town <:townicon2:896431548717473812>**__", value="<:copicon2:889672912905322516> **Cop (Cop)**\n<:deticon2:889673135438319637> **Detective (Det)**\n<:loicon2:889673190392078356> **Lookout (LO)**\n<:docicon2:890333203959787580> **Doctor (Doc)**\n<:enficon2:890339050865696798> **Enforcer (Enf)**\n<:mayoricon:922566007946629131> **Mayor (Mayor)**")
    origin.add_field(name="__**Mafia <:maficon2:890328238029697044>**__", value="<:maficon2:891739940055052328> **Mafioso (Maf)**\n<:frameicon2:890365634913902602> **Framer (Frame)**\n<:consicon2:890336628269281350> **Consort (Cons)**")
    origin.add_field(name="__**Neutrals :axe:**__", value="<:hhicon2:891429754643808276> **Headhunter (HH)**\n<:jesticon2:889968373612560394> **Jester (Jest)**")
    
    two = disnake.Embed(title="**__List of Roles :performing_arts:__**", colour=disnake.Colour(0x8266dc), description="Here are a list of roles that are playable in **Anarchic 1.1.0**.")

    two.set_thumbnail(url="https://images-ext-1.discordapp.net/external/S8kYnDiF37aks-RBlGNZVz6gbTasCOJy1R7IB9iE3NQ/%3F5765650006/https/www12.lunapic.com/editor/working/163036526867946112")

    two.add_field(name="__**Town <:townicon2:896431548717473812>**__", value="<:copicon2:889672912905322516> **Cop (Cop)**\n<:deticon2:889673135438319637> **Detective (Det)**\n<:loicon2:889673190392078356> **Lookout (LO)**\n<:docicon2:890333203959787580> **Doctor (Doc)**\n<:enficon2:890339050865696798> **Enforcer (Enf)**\n<:mayoricon:922566007946629131> **Mayor (Mayor)**\n<:psyicon2:896159311078780938> **Psychic (Psy**)")
    two.add_field(name="__**Mafia <:maficon2:890328238029697044>**__", value="<:maficon2:891739940055052328> **Mafioso (Maf)**\n<:frameicon2:890365634913902602> **Framer (Frame)**\n<:consigicon2:896154845130666084> **Consigliere (Consig)**\n<:consicon2:890336628269281350> **Consort (Cons)**")
    two.add_field(name="__**Neutrals :axe:**__", value="<:hhicon2:891429754643808276> **Headhunter (HH)**\n<:jesticon2:889968373612560394> **Jester (Jest)**")
    
    current = disnake.Embed(title="**__List of Roles :performing_arts:__**", colour=disnake.Colour(0x8266dc), description="Here are a list of roles that are playable in **Anarchic 1.2.0**.")

    current.set_thumbnail(url="https://images-ext-1.discordapp.net/external/S8kYnDiF37aks-RBlGNZVz6gbTasCOJy1R7IB9iE3NQ/%3F5765650006/https/www12.lunapic.com/editor/working/163036526867946112")

    current.add_field(name="__**Town <:townicon2:896431548717473812>**__", value="<:copicon2:889672912905322516> **Cop (Cop)**\n<:deticon2:889673135438319637> **Detective (Det)**\n<:loicon2:889673190392078356> **Lookout (LO)**\n<:docicon2:890333203959787580> **Doctor (Doc)**\n<:enficon2:890339050865696798> **Enforcer (Enf)**\n<:mayoricon:922566007946629131> **Mayor (Mayor)**\n<:psyicon2:896159311078780938> **Psychic (Psy)**\n<:trackicon:922885543812005949> **Tracker (Track)**\n<:lego:939315708146372658> **Attendant (Att)**")
    current.add_field(name="__**Mafia <:maficon2:890328238029697044>**__", value="<:maficon2:891739940055052328> **Mafioso (Maf)**\n<:frameicon2:890365634913902602> **Framer (Frame)**\n<:consigicon2:896154845130666084> **Consigliere (Consig)**\n<:consicon2:890336628269281350> **Consort (Cons)**\n<:janiicon:923219547325091840> **Janitor (Jani)**")
    current.add_field(name="__**Neutrals :axe:**__", value="<:hhicon2:891429754643808276> **Headhunter (HH)**\n<:jesticon2:889968373612560394> **Jester (Jest)**\n<:psychoicon:922564838897627166> **Psychopath (Psycho)**")
    

    class Dropdown(disnake.ui.Select):
        def __init__(self):

            # Set the options that will be presented inside the dropdown
            options = [
                disnake.SelectOption(
                    label="1.2.0", description="Check out the roles in Anarchic 1.2.0", value="120", emoji='<:psychoicon:922564838897627166>'
                ),
                disnake.SelectOption(
                    label="1.1.0", description="Check out the roles in Anarchic 1.1.0", value="110", emoji='<:consigicon2:896154845130666084>'
                ),
                disnake.SelectOption(
                    label="1.0.0", description="Check out the roles in Anarchic 1.0.0", value="100", emoji="<:copicon2:889672912905322516>"
                )
            ]

            # The placeholder is what will be shown when no option is chosen
            # The min and max values indicate we can only pick one of the three options
            # The options parameter defines the dropdown options. We defined this above
            super().__init__(
                placeholder="Version",
                min_values=1,
                max_values=1,
                options=options,
            )

        async def callback(self, interaction: disnake.MessageInteraction):
            e = self.values[0]

            emb = None

            if (e == "120"):
                emb = copy.copy(current)
            if (e == "100"):
                emb = copy.copy(origin)
            if (e == "110"):
                emb = copy.copy(two)

            #r.children[int(e.replace("p", ""))].default = True

            await interaction.response.edit_message(embed=emb)

    class DropdownView(disnake.ui.View):
        def __init__(self):
            super().__init__()

            self.add_item(Dropdown())

    await inter.edit_original_message(embed=current, view=DropdownView())

@commands.guild_only()
@bot.slash_command(
    name="setups",
    description="View the setups of Anarchic"
)
async def ssetups(inter): 
    try:
        var[inter.guild.id]["test"]
    except:
        var[inter.guild.id] = copy.deepcopy(temp)
    await _setups(inter, True)

@bot.command()
async def setups(ctx):
    await _setups(ctx)

async def _setups(ctx, inter=False):
    await ctx.response.defer()
    embed = disnake.Embed(title="__**<a:Tada:841483453044490301> List of playable setups! <a:Tada:841483453044490301>**__", description="", color=0x7eafa4)
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
        await ctx.edit_original_message(embed=embed)
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
async def lock(channel, maf=False):
    if (maf == True):
        overwrite = disnake.PermissionOverwrite()
        overwrite.send_messages = False
        overwrite.read_messages = True

        for i in var[channel.guild.id]["players"]:
            if (Player.get_player(i, var[channel.guild.id]["playerdict"]).faction == Faction.Mafia):
                user = await channel.guild.fetch_member(i)
                await channel.set_permissions(user, overwrite=overwrite)
    else:
        overwrite = disnake.PermissionOverwrite()
        overwrite.send_messages = False
        overwrite.read_messages = True

        for i in var[channel.guild.id]["players"]:
            user = await channel.guild.fetch_member(i)
            await channel.set_permissions(user, overwrite=overwrite)

async def unlock(channel, maf=False):
    overwrite = disnake.PermissionOverwrite()
    overwrite.send_messages = False
    overwrite.read_messages = True

    if (maf == True):
        for i in var[channel.guild.id]["players"]:
            user = await channel.guild.fetch_member(i)
            if (Player.get_player(i, var[channel.guild.id]["playerdict"]).faction == Faction.Mafia):
                overwrite.send_messages = True
                overwrite.read_messages = True

                await channel.set_permissions(user, overwrite=overwrite)

    else:
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

async def completeunlock(channel):
    overwrite = disnake.PermissionOverwrite()
    overwrite.send_messages = True
    overwrite.read_messages = True

    for i in var[channel.guild.id]["players"]:
        user = await channel.guild.fetch_member(i)
        await channel.set_permissions(user, overwrite=overwrite)

async def assignroles(comp:str, ctx):
    c = []
    my = []
    setup = []

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
            user:disnake.User = bot.get_user(i)
            item = ""

            try:
                guilds[str(i)]["equipped"]
            except:
                guilds[str(i)]["equipped"] = None


            if (guilds[str(i)]["equipped"] != None):
                item = guilds[str(i)]["equipped"]
            

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
                while True:
                    hisrole = random.choice(var[ctx.id]["mafias"])
                    if (hisrole in var[ctx.id]["uniques"] and hisrole in setup):
                        continue

                    break
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
            setup.append(hisrole)


            if (ll in var[ctx.id]["mafias"]):
                mafs += 1
            
            if (ll == "mafioso"):
                mafiosos += 1

            var[ctx.id]["playerdict"]["p" + str(id)].role = hisrole
            id += 1

        if (mafs > 0 and mafiosos == 1 and len(co) == 0):
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
            e = []
            for o in var[ctx.id]["players"]:
                play = None
                while True:
                    play = Player.get_player(random.choice(var[ctx.id]["players"]), var[ctx.id]["playerdict"])
                    if (play not in e):
                        break

                if (play.role.lower() != "mayor" and string.capwords(play.role) in var[ctx.id]["towns"] and i.hhtarget == None):
                    i.hhtarget = play.id

                    badmessages = ["has called you \"Bad at Anarchic\"",
                    "has bullied you",
                    "played Fortnite",
                    "ate chocolate pizza",
                    "has threw", 
                    "has wronged you", 
                    "played Fall Guys", 
                    "watched amogus drip", 
                    "got you lynched when you were revealed mayor", 
                    "killed you as Mafia",
                    "said no"]

                    targetembed = disnake.Embed(title=f"**Your target is {bot.get_user(play.id).name}#{bot.get_user(play.id).discriminator}.**", colour=disnake.Colour(0x39556b), description=f"Your target {random.choice(badmessages)} and now it's time for them to pay. Get them lynched in order to win.")

                    targetembed.set_thumbnail(url=bot.get_user(play.id).avatar.url)
                    targetembed.set_footer(text="If your target dies at night, you will be converted into a Jester.", icon_url=bot.get_user(i.id).avatar.url)
                    break
                
                e.append(play)

            if (i.hhtarget == None):
                i.role = "Jester"
                i.ogrole = "Jester"
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
            except disnake.Forbidden as e:
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
            embed = disnake.Embed(title="**Your role is Cop**", colour=disnake.Colour(0x7ed321), description="A reliable law enforcer, skilled in keeping evildoers in check.")

            embed.set_image(url="https://images-ext-2.discordapp.net/external/lxy0B33My7VTF8-DAztYa8qUyl5TYxeXEuGmqRnxGCY/%3Fwidth%3D493%26height%3D634/https/media.discordapp.net/attachments/765738640554065962/871777631798964294/unknown.png")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889672912905322516.png?size=80")
            embed.set_footer(text="Town Investigative 🔎", icon_url=author.avatar.url)

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
            embed = disnake.Embed(title="**Your role is Tracker**", colour=disnake.Colour(0x7ed321), description="A skilled pathfinder who scouts the night.")

            embed.set_image(url="https://cdn.discordapp.com/attachments/884176934878191646/924148641994776576/IMG_0108.png")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/922885543812005949.png?size=160")
            embed.set_footer(text="Town Investigative 🔎", icon_url=author.avatar.url)

            embed.add_field(name="**Atk ⚔️:**", value="None", inline=True)
            embed.add_field(name="**Res 🛡️:**", value="None", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Town", inline=False)
            embed.add_field(name="**Action :man_running::**", value="Track a player each night", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="You will know who your target visits", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Eliminate all the criminals who may try to harm the **Town** <:townicon2:896431548717473812>", inline=False)
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon2:889672912905322516>:** Your target seems **Innocent <:inno:873636640227205160>**\n**Detective <:deticon2:889673135438319637>:** Your target works with sensitive information. They must be a Detective <:deticon2:889673135438319637>, Consigliere <:consigicon2:896154845130666084>, Tracker <:trackicon:922885543812005949> or Lookout <:loicon2:889673190392078356>\n**Consigliere <:consigicon2:896154845130666084>:** Your target keeps track of others. They must be a **Tracker <:trackicon:922885543812005949>**", inline=False)
        
            if (player != None):
                player.faction = Faction.Town #The player's faction (Town, Mafia, Neutral)
                player.appearssus = False #If the player appears sus
                player.detresult = "Your target seeks revenge.>EThey must be a **Cop <:copicon2:889672912905322516>**>E**Headhunter <:hhicon2:891429754643808276>**>E**Mafioso <:maficon2:891739940055052328>**>E**Enforcer <:enficon2:890339050865696798>**." #Det results
                player.defense = Defense.Default #defense
                player.distraction = False #consort
        elif (role == "detective"):
            embed = disnake.Embed(title="**Your role is Detective**", colour=disnake.Colour(0x7ed321), description="A private investigator who uncovers one's secrets")

            embed.set_image(url="https://media.discordapp.net/attachments/878437549721419787/882410811241414696/unknown.png?width=411&height=468")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889673135438319637.png?size=80")
            embed.set_footer(text="Town Investigative 🔎", icon_url=author.avatar.url)

            embed.add_field(name="**Atk ⚔️:**", value="None", inline=True)
            embed.add_field(name="**Res 🛡️:**", value="None", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Town", inline=False)
            embed.add_field(name="**Action :man_running::**", value="Investigate a player each night", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="You will learn what possible roles your target might be", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Eliminate all the criminals who may try to harm the **Town** <:townicon2:896431548717473812>", inline=False)
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon2:889672912905322516>:** Your target seems **Innocent <:inno:873636640227205160>**\n**Detective <:deticon2:889673135438319637>:** Your target works with sensitive information. They must be a **Detective <:deticon2:889673135438319637>**, **Consigliere <:consigicon2:896154845130666084>** or **Lookout <:loicon2:889673190392078356>**\n**Consigliere <:consigicon2:896154845130666084>:**Your target secretly gathers infomation. They must be a **Detective <:deticon2:889673135438319637>**", inline=False)
            if (player != None):
                player.faction = Faction.Town #The player's faction (Town, Mafia, Neutral)
                player.appearssus = False #If the player appears sus
                player.detresult = "Your target hides in the shadows. They must be a **Doctor <:docicon2:890333203959787580>**, **Lookout <:loicon2:889673190392078356>**, **Consort <:consicon2:890336628269281350>** or **Detective <:deticon2:889673135438319637>**." #Det results
                player.defense = Defense.Default #defense
                player.distraction = False #consort
        elif (role == "janitor"):
            embed = disnake.Embed(title="**Your role is Janitor**", colour=disnake.Colour(0xd0021b), description="A tired custodian who cleans up bodies.")

            embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/874775072001359953/unknown.png")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/874056995165044836.png?v=1")
            embed.set_footer(text="Mafia Deception 🎭", icon_url=author.avatar.url)

            embed.add_field(name="**Atk ⚔️:**", value="None", inline=True)
            embed.add_field(name="**Res 🛡️:**", value="None", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Mafia", inline=False)
            embed.add_field(name="**Action :man_running::**", value="**Clean** a player at night `3 charges`", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="If your target dies that night, their role, will, and cause of death will be hidden to the rest of the town\nYou will learn the cleaned target's role, will, and cause of death", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Kill all those who may rival the **Mafia :rose:**.", inline=False)    
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon:871526445619482634>:** Your target is **Suspicious <:sus:873637612571746324>**\n**Detective <:deticon:871526928799129651>:** Your target associates themselves near the border of death. They must be either a **Doctor <:docicon2:890333203959787580>**, **Psychic <:psyicon2:896159311078780938>** or **Janitor :broom:**\n**Consigliere <:consigicon2:896154845130666084>:** Your target is a sanitation expert for the mafia. They must be a **Janitor :broom:**!", inline=False)
            if (player != None):
                player.faction = Faction.Mafia #The player's faction (Town, Mafia, Neutral)
                player.appearssus = True #If the player appears sus
                player.detresult = "Your target hides in the shadows. They must be a **Doctor <:docicon2:890333203959787580>**, **Lookout <:loicon2:889673190392078356>**, **Consort <:consicon2:890336628269281350>** or **Detective <:deticon2:889673135438319637>**." #Det results
                player.defense = Defense.Default #defense
                player.distraction = False #consort
        elif (role == "doctor"):
            embed = disnake.Embed(title="**Your role is Doctor**", colour=disnake.Colour(0x7ed321), description="A secret surgeon who heals people at night")

            embed.set_image(url="https://images-ext-2.discordapp.net/external/a_EBqbeOJpbdk-Cwmg0ECTonyvRrMVqHHnJBEaiAQig/https/media.discordapp.net/attachments/887804073024299008/891814142984454155/DocImage.png?width=326&height=383")
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/871525831422398497/890333113572548719/DocIcon.png?width=701&height=701")
            embed.set_footer(text="Town Protective 💉", icon_url=author.avatar.url)

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
            embed = disnake.Embed(title="**Your role is Enforcer**", colour=disnake.Colour(0x7ed321), description="A rogue vigilante with an eye out for justice.")

            embed.set_image(url="https://images-ext-2.discordapp.net/external/vxOShXchGrPMHJEcrLhW914asNZollLv-GvV70esn8Y/%3Fwidth%3D562%26height%3D634/https/media.discordapp.net/attachments/765738640554065962/872225776211202068/unknown.png")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/871525831422398497/890339048097456148/EnfIcon.png")
            embed.set_footer(text="Town Killing 🔫", icon_url=author.avatar.url)

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
            embed = disnake.Embed(title="**Your role is Mafioso**", colour=disnake.Colour(0xd0021b), description="The right hand man of organized crime.")
            
            embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/899413050602446898/unknown.png?width=371&height=383")
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/897585492562964531/MafIcon2.png?width=676&height=676")
            embed.set_footer(text="Mafia Killing 🗡️", icon_url=author.avatar.url)

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
            embed = disnake.Embed(title="**Your role is Psychopath**", colour=disnake.Colour(0x070569), description="A bloodthirsty killer who wishes to dye the town in blood.")

            embed.set_image(url="https://media.discordapp.net/attachments/888555153064611860/911044426078502912/PsychoProfile.png?width=378&height=534")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/909908333635440680.png?size=80")
            embed.set_footer(text="Neutral Killing 🔪", icon_url=author.avatar.url)

            embed.add_field(name="**Atk ⚔️:**", value="Basic", inline=True)
            embed.add_field(name="**Res 🛡️:**", value="Basic", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Neutral", inline=False)
            embed.add_field(name="**Action :man_running::**", value="Stab a player at night\nChoose to go **cautious** or **incautious**", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="While **cautious**, you will appear innocent to **Cops <:copicon:871526445619482634>**\nWhile **incautious**, you become immune to **distractions**\nWhile **incautious**, you will attack **Consorts <:consicon2:890336628269281350>** who visit you with a **piercing astral** attack and bloody their will :drop_of_blood::scroll:\nWhile **incautious**, you will attack **Doctors <:docicon2:890333203959787580>** who heal your target with a **piercing astral** attack and bloody their will :drop_of_blood::scroll:", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Kill all who would oppose **you <:psychoicon:909908333635440680>**.", inline=False)
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon:871526445619482634>:** Your target is acting **Psychotic <:psycho:877584821180825691>**\n**Detective <:deticon:871526928799129651>:** Your target hides in shadows. They must be a **Doctor <:docicon2:890333203959787580>**, **Psychic <:psyicon2:896159311078780938>** **Psychopath <:psychoicon:909908333635440680> **, or **Consort <:consicon2:890336628269281350>**\n**Consigliere <:consigicon2:896154845130666084>:** Your target is a cold blooded murderer. They must be a **Psychopath <:psychoicon:909908333635440680> **", inline=False) 
            if (player != None):
                player.faction = Faction.Neutral #The player's faction (Town, Mafia, Neutral)
                player.appearssus = True #If the player appears sus
                player.detresult = "Your target seeks revenge. They must be a **Cop <:copicon2:889672912905322516>**, **Headhunter <:hhicon2:891429754643808276>**, **Mafioso <:maficon2:891739940055052328>** or **Enforcer <:enficon2:890339050865696798>**." #Det results
                player.defense = Defense.Basic #defense
                player.distraction = False #consort
        elif (role == "mayor"):
            embed = disnake.Embed(title="**Your role is Mayor**", colour=disnake.Colour(0x7ed321), description="The leader of the town")

            embed.set_image(url="https://cdn.discordapp.com/attachments/765738640554065962/886652670230790214/unknown.png")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/897570023143518288.png?size=80")
            embed.set_footer(text="Town Support 🛠️", icon_url=author.avatar.url)

            embed.add_field(name="**Atk ⚔️:**", value="None", inline=True)
            embed.add_field(name="**Res 🛡️:**", value="None", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Town", inline=False)
            embed.add_field(name="**Action :man_running::**", value="Reveal yourself as **Mayor <:mayoricon:922566007946629131>** to the rest of the town", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="You will have 3 votes once you reveal", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Eliminate all the criminals who may try to harm the **Town <:townicon2:896431548717473812>**", inline=False)	
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon2:889672912905322516>:** Your target seems **Innocent <:inno:873636640227205160>**\n**Detective <:deticon2:889673135438319637>:** Your target may not be what they seem at first glance. They must be a **Framer <:frameicon2:890365634913902602>**, **Jester <:jesticon2:889968373612560394>** or **Mayor <:mayoricon:922566007946629131>**\n**Consigliere <:consigicon2:896154845130666084>:** Your target is the leader of the town. They must be the **Mayor <:mayoricon:922566007946629131>**", inline=False)
            if (player != None):
                player.faction = Faction.Town #The player's faction (Town, Mafia, Neutral)
                player.appearssus = False #If the player appears sus
                player.detresult = "Your target might not be what they seem at first glance. They must be a **Framer <:frameicon2:890365634913902602>**, **Jester <:jesticon2:889968373612560394>** or **Mayor <:mayoricon:922566007946629131>**." #Det results
                player.defense = Defense.Default #defense
                player.distraction = False #consort
        elif (role == "psychic"):
            embed = disnake.Embed(title="**Your role is Psychic**", colour=disnake.Colour(0x7ed321), description="A powerful mystic who speaks with the dead.")

            embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/896172274716127272/image0.png?width=451&height=528")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896159311078780938.png?size=80")
            embed.set_footer(text="Town Support 🛠️", icon_url=author.avatar.url)

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
                player.detresult = "Your target might not be what they seem at first glance. They must be a **Framer <:frameicon2:890365634913902602>**, **Jester <:jesticon2:889968373612560394>** or **Mayor <:mayoricon:922566007946629131>**." #Det results
                player.defense = Defense.Default #defense
                player.distraction = False #consort
        elif (role == "consort"):
            embed = disnake.Embed(title="**Your role is Consort**", colour=disnake.Colour(0xd0021b), description="A hooker who works for organized crime")

            embed.set_image(url="https://media.discordapp.net/attachments/879064140285620315/882069060517503006/unknown.png?width=309&height=468")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/890336628269281350.webp?size=80&quality=lossless")
            embed.set_footer(text="Mafia Support 🧲", icon_url=author.avatar.url)

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
        elif (role == "attendant"):
            embed = disnake.Embed(title="**Your role is Attendant**", colour=disnake.Colour(0x7ed321), description="An attractive companion with a soothing aura.")

            embed.set_image(url="https://images-ext-2.discordapp.net/external/-MOtTDoNH8I7CkxXfNXYxaZc8wRyCTwejBbj6TPfKCw/%3Fwidth%3D375%26height%3D634/https/media.discordapp.net/attachments/765738640554065962/872274879309836408/unknown.png?width=285&height=482")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/890336628269281350.png?size=96")
            embed.set_footer(text="Town Support 🛠️", icon_url=author.avatar.url)

            embed.add_field(name="**Atk ⚔️:**", value="None", inline=True)
            embed.add_field(name="**Res 🛡️:**", value="None", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Town", inline=False)
            embed.add_field(name="**Action :man_running::**", value="Distract a player at night", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="You are immune to **distractions**", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Eliminate all the criminals who may try to harm the **Town :house:**", inline=False)	
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon:871526445619482634>:** Your target seems **Innocent <:inno:873636640227205160>**\n**Detective <:deticon:871526928799129651>:** Your target works from shadows. They must be a **Attendant <:consicon2:890336628269281350>**, or **Lookout <:loicon2:889673190392078356>**", inline=False)
            if (player != None):
                player.faction = Faction.Town #The player's faction (Town, Mafia, Neutral)
                player.appearssus = False #If the player appears sus
                player.detresult = "Your target hides in the shadows. They must be a **Doctor <:docicon2:890333203959787580>**, **Lookout <:loicon2:889673190392078356>**, **Consort <:consicon2:890336628269281350>** or **Detective <:deticon2:889673135438319637>**." #Det results
                player.defense = Defense.Default #defense
                player.distraction = False #consort
        elif (role == "framer"):
            embed = disnake.Embed(title="**Your role is Framer**", colour=disnake.Colour(0xd0021b), description="A skilled deceiver who sets investigations astray")

            embed.set_image(url="https://cdn.discordapp.com/attachments/765738640554065962/886032651465654312/unknown.png")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/874056995165044836.png?v=1")
            embed.set_footer(text="Mafia Deception 🎭", icon_url=author.avatar.url)

            embed.add_field(name="**Atk ⚔️:**", value="None", inline=True)
            embed.add_field(name="**Res 🛡️:**", value="None", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Mafia", inline=False)
            embed.add_field(name="**Action :man_running::**", value="Frame a player each night", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="Frames last until an investigation is preformed on your target\nFramed players show as **Suspicious <:sus:873637612571746324>** to a **Cop <:copicon2:889672912905322516>**\nFramed players show as **Framer <:frameicon2:890365634913902602>**, **Jester <:jesticon2:889968373612560394>** or **Mayor <:mayoricon:922566007946629131>** to a **Detective <:deticon2:889673135438319637>**", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Kill all those who may rival the **Mafia <:maficon2:890328238029697044>**.", inline=False)	
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon2:889672912905322516>:** Your target is **Suspicious <:sus:873637612571746324>**\n**Detective <:deticon2:889673135438319637>:** Your target may not be what they seem at first glance. They must be a **Framer <:frameicon2:890365634913902602>**, **Jester <:jesticon2:889968373612560394>** or **Mayor <:mayoricon:922566007946629131>**", inline=False)
            if (player != None):
                player.faction = Faction.Mafia #The player's faction (Town, Mafia, Neutral)
                player.appearssus = True #If the player appears sus
                player.detresult = "Your target might not be what they seem at first glance.>EFramer <:frameicon2:890365634913902602>>EJester <:jesticon2:889968373612560394>** or **Mayor <:mayoricon:922566007946629131>**." #Det results
                player.defense = Defense.Default #defense
                player.distraction = False #consort
        elif (role == "jester"):
            embed = disnake.Embed(title="**Your role is Jester**", colour=disnake.Colour(0xffc3e7), description="A crazed lunatic who wants to be publicly executed")

            embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/892532613682700338/unknown.png?width=460&height=459")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889968373612560394.png?size=80")
            embed.set_footer(text="Neutral Evil 🪓", icon_url=author.avatar.url)

            embed.add_field(name="**Atk ⚔️:**", value="Piercing", inline=True)
            embed.add_field(name="**Res 🛡️:**", value="None", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Neutral", inline=False)
            embed.add_field(name="**Action :man_running::**", value="None", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="You will **distract** all of your guilty or abstaining voter the night following your lynch\nYou will **passively** attack a guilty or abstaining voter the night following your lynch.", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Get yourself **lynched :axe:**.", inline=False)	
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon2:889672912905322516>:** Your target seems **Innocent <:inno:873636640227205160>**\n**Detective <:deticon2:889673135438319637>:** Your target may not be what they seem at first glance. They must be a **Framer <:frameicon2:890365634913902602>**, **Jester <:jesticon2:889968373612560394>** or **Mayor <:mayoricon:922566007946629131>**\n**Consigliere <:consigicon2:896154845130666084>:** Your target is a crazed lunatic waiting to be hung. They must be a **Jester <:jesticon2:889968373612560394>**", inline=False)
            if (player != None):
                player.faction = Faction.Neutral #The player's faction (Town, Mafia, Neutral)
                player.appearssus = False #If the player appears sus
                player.detresult = "Your target might not be what they seem at first glance. They must be a **Framer <:frameicon2:890365634913902602>**, **Jester <:jesticon2:889968373612560394>** or **Mayor <:mayoricon:922566007946629131>**." #Det results
                player.defense = Defense.Default #defense
                player.distraction = False #consort
        elif (role == "lookout"):
            embed = disnake.Embed(title="**Your role is Lookout**", colour=disnake.Colour(0x7ed321), description="A skilled observer who keeps an eye on the evils")

            embed.set_image(url="https://cdn.discordapp.com/attachments/765738640554065962/904161876286521374/IMG_0059.png")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889673190392078356.png?size=80")
            embed.set_footer(text="Town Investigative 🔎", icon_url=author.avatar.url)

            embed.add_field(name="**Atk ⚔️:**", value="None", inline=True)
            embed.add_field(name="**Res 🛡️:**", value="None", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Town", inline=False)
            embed.add_field(name="**Action :man_running::**", value="Watch over a player each night", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="You will learn who visits your target", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Eliminate all the criminals who may try to harm the **Town** <:townicon2:896431548717473812>", inline=False)
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon2:889672912905322516>:** Your target seems **Innocent <:inno:873636640227205160>**\n**Detective <:deticon2:889673135438319637>:** Your target works with sensitive information. They must be a **Detective <:deticon2:889673135438319637>**, **Consigliere <:consigicon2:896154845130666084>** or **Lookout <:loicon2:889673190392078356>**\n**Consigliere <:consigicon2:896154845130666084>:** Your target watches other people's houses at night. They must be a **Lookout <:loicon2:889673190392078356>**", inline=False)
            if (player != None):
                player.faction = Faction.Town #The player's faction (Town, Mafia, Neutral)
                player.appearssus = False #If the player appears sus
                player.defense = Defense.Default #defense
                player.distraction = False #consort
        elif (role == "consigliere"):
            embed = disnake.Embed(title="**Your role is Consigliere**", colour=disnake.Colour(0xd0021b), description="A corrupted detective who gathers information for the mafia")

            embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/897240498329239582/image0.png?width=570&height=676")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896154845130666084.png?size=80")
            embed.set_footer(text="Mafia Support 🧲", icon_url=author.avatar.url)

            embed.add_field(name="**Atk ⚔️:**", value="None", inline=True)
            embed.add_field(name="**Def 🛡️:**", value="None", inline=True)
            embed.add_field(name="**Faction :pushpin::**", value="Mafia", inline=False)
            embed.add_field(name="**Action :man_running::**", value="Investigate a player each night", inline=False)
            embed.add_field(name="**Attributes :star2::**", value="You will learn your target's exact role", inline=False)
            embed.add_field(name="**Win Condition :trophy::**", value="Kill all those who may rival the **Mafia :rose:**.", inline=False)
            embed.add_field(name="**Investigation Results :mag_right::**", value="**Cop <:copicon2:889672912905322516>:** Your target is **Suspicious <:sus:873637612571746324>**\n**Detective <:deticon2:889673135438319637>:** Your target works with sensitive information. They must be a **Detective <:deticon2:889673135438319637>**, **Consigliere <:consigicon2:896154845130666084>** or **Lookout <:loicon2:889673190392078356>**", inline=False)
            if (player != None):
                player.faction = Faction.Mafia #The player's faction (Town, Mafia, Neutral)
                player.appearssus = True #If the player appears sus
                player.detresult = "Your target seeks revenge. They must be a **Cop <:copicon2:889672912905322516>**, **Headhunter <:hhicon2:891429754643808276>**, **Mafioso <:maficon2:891739940055052328>** or **Enforcer <:enficon2:890339050865696798>**." #Det results
                player.defense = Defense.Default #defense 
                player.distraction = False #consort
        elif (role == "headhunter"):
            embed = disnake.Embed(title="**Your role is Headhunter**", colour=disnake.Colour(0x334f64), description="An obsessed executioner who wants a certain someone killed in front of the town.")

            embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/874089000250531860/unknown.png?width=574&height=701")
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/891416747582840842/hh_icon.png")
            embed.set_footer(text="Neutral Evil 🪓", icon_url=author.avatar.url)

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
        else:
            embed = None
        
        if (embed == None):
            return None
        else:
            return embed
    except:
        embed = disnake.Embed(title="Looks like something went wrong with the embeds...", description="blame cet not me /shrug")
        embed.set_footer(text=f"For debugging: the role was {roled}")
        return embed



async def check(e:disnake.User, guild):
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
        if (Player.get_player(i, var[ctx]["playerdict"]).role.lower() == "attendant"):
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
        if (Player.get_player(i, var[ctx]["playerdict"]).role.lower() == "psychic"):
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
    for i in var[ctx]["targets"].keys():
        if (Player.get_player(i, var[ctx]["playerdict"]).role.lower() == "janitor"):
            await results(bot.get_user(i), var[ctx]["targets"][i], ctx)
    for i in var[ctx]["targets"].keys():
        if (Player.get_player(i, var[ctx]["playerdict"]).role.lower() == "headhunter"):
            if (Player.get_player(i, var[ctx]["playerdict"]).dead == True):
                if (Player.get_player(i, var[ctx]["playerdict"]).diedln == False):
                    continue                    
            await results(bot.get_user(i), var[ctx]["targets"][i], ctx)

    await asyncio.sleep(4)
    asyncio.create_task(day(var[ctx]["channel"]))

async def results(ctx, targ, g):
    """Sends the player in `ctx` (disnake.User) a result after using their action on `targ`'s id."""
    role = ""
    var[g]["resul"] += 1
    if (var[g]["resul"] > len(var[g]["players"])):
        return



    for value in var[g]["playerdict"].values():
        if (value.id == ctx.id):
            role = value.role.lower()
    
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
            embed = disnake.Embed(title="**You feel too guilty to do anything tonight.**", colour=disnake.Colour(0xffc3e7))

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889968373612560394.png?size=80")
            embed.set_footer(text="Shouldn't lynch the Jester.", icon_url=ctx.avatar.url)     

            await ctx.send(embed=embed)
            return

    if (Player.get_player(ctx.id, var[g]["playerdict"]).distraction == True):
        var[g]["targets"][ctx.id] = 0
        embed = disnake.Embed(title="**Somebody Distracted :revolving_hearts: you last night, so you did not perform your night ability.**", colour=disnake.Colour(0xb6d4ff))

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/890336628269281350.webp?size=80&quality=lossless")
        embed.set_footer(text="Gotta stay focused.", icon_url=ctx.avatar.url)
        await ctx.send(embed=embed)
        return

    if (targ == 0):
        return

    if (role == "mayor"):
        if (targ == False):
            return
        elif (targ == True):
            await reveal(ctx, g)
            return

    if (role == "cop"):
        if (await check(bot.get_user(targ), g) == True):
            embed = disnake.Embed(title="**Your target is Suspicious!**", colour=disnake.Colour(0xd0021b), description=f"**{bot.get_user(targ).name} is either... \n --A member of the Mafia <:maficon2:890328238029697044>. \n --Or an Innocent who has been Framed <:frameicon2:890365634913902602>.**")

            embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/871791911072067594/suspicious__-removebg-preview.png")
            embed.set_author(name="Interrogation Results")
            embed.set_footer(text="Try convincing the others with your info.", icon_url=ctx.avatar.url)
            await ctx.send(embed=embed)
        elif (await check(bot.get_user(targ), g) == False):
            embed = disnake.Embed(title="**Your target seems Innocent.**", colour=disnake.Colour(0x7ed321), description=f"**{bot.get_user(targ).name} is either... \n --An Innocent Townie <:townicon2:896431548717473812>. \n --Or an evil Neutral 🪓.**")

            embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/871791900003282964/seems_innocent_-removebg-preview.png")
            embed.set_author(name="Interrogation Results")
            embed.set_footer(text="Try convincing the others with your info.", icon_url=ctx.avatar.url)
            await ctx.send(embed=embed)
        else:
            embed = disnake.Embed(title="**Your target is acting Psychotic!**", colour=disnake.Colour(0x4a90e2), description=f"**{bot.get_user(targ).name} must be... \n --A Psychopath <:psychoicon:909908333635440680>.**")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/877584821180825691.png?size=96")
            embed.set_author(name="Interrogation Results")
            embed.set_footer(text="Try convincing the others with your info.", icon_url=ctx.avatar.url)
            await ctx.send(embed=embed)

    elif (role == "mafioso"):
        if (await attack(ctx.id, bot.get_user(targ), g, Attack.Default) == True):
            member:disnake.Member = var[g]["guildg"].get_member(targ)
            await member.add_roles(disnake.utils.get(var[g]["guildg"].roles, name="[Anarchic] Dead"))
            await member.remove_roles(disnake.utils.get(var[g]["guildg"].roles, name="[Anarchic] Player"))
            Player.get_player(targ, var[g]["playerdict"]).diedln = True
            Player.get_player(targ, var[g]["playerdict"]).death.append(DeathReason.Mafia)
            user = bot.get_user(targ)
            embed = disnake.Embed(title="**You were attacked by a member of the Mafia <:maficon2:890328238029697044>.**", colour=disnake.Colour(0xd0021b), description="**You have died <:rip:878415658885480468>**.")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/890328238029697044.png?size=80")
            embed.set_footer(text="Rest in peace.", icon_url=user.avatar.url)
            await user.send(embed=embed)
        else:
            embed = disnake.Embed(title="**Your target was too strong to be killed.**", colour=disnake.Colour(0xfff68a))


            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/878379179106787359.png?v=1")
            embed.set_footer(text="Strange...", icon_url=ctx.avatar.url)
            
            await ctx.send(embed=embed)
    elif (role == "janitor"):
        player = Player.get_player(targ, var[g]["playerdict"])
        if (player.diedln == True):
            user = bot.get_user(player.id)
            ctxuser = bot.get_user(ctx.id)
            player.charges -= 1
            
            embed = disnake.Embed(title="Whilst cleaning your target, you learned:", colour=disnake.Colour(0xd0021b))

            embed.set_thumbnail(url=user.avatar.url)
            embed.set_footer(text=f"You have {player.charges} charges left.", icon_url=ctxuser.avatar.url)

            em = var[g]["emoji"]
            embed.add_field(name="Role", value=f"**{player.role}** {em[player.role.lower()]}", inline=False)

            if (getWill(player.will) == ""):
                embed.add_field(name="Will", value=f"**:x: No will**", inline=False)
            else:
                embed.add_field(name="Will", value=f"**{getWill(player.will)}**", inline=False)

            await ctxuser.send(embed=embed)
        
            player.death = [DeathReason.Cleaned]
            player.will = []
    elif (role == "psychopath"):
        if (await attack(ctx.id, bot.get_user(targ), g, Attack.Default) == True):
            member:disnake.Member = var[g]["guildg"].get_member(targ)
            await member.add_roles(disnake.utils.get(var[g]["guildg"].roles, name="[Anarchic] Dead"))
            await member.remove_roles(disnake.utils.get(var[g]["guildg"].roles, name="[Anarchic] Player"))
            Player.get_player(targ, var[g]["playerdict"]).diedln = True
            Player.get_player(targ, var[g]["playerdict"]).death.append(DeathReason.Psychopath)
            user = bot.get_user(targ)
            embed = disnake.Embed(title="**You were attacked by a member of the Psychopath <:maficon2:890328238029697044>.**", colour=disnake.Colour(0xd0021b), description="**You have died <:rip:878415658885480468>**.")

            embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/871849580533268480/unknown.png?width=744&height=634")
            embed.set_footer(text="Rest in peace.", icon_url=user.avatar.url)
            await user.send(embed=embed)
        else:
            embed = disnake.Embed(title="**Your target was too strong to be killed.**", colour=disnake.Colour(0xfff68a))


            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/878379179106787359.png?v=1")
            embed.set_footer(text="Strange...", icon_url=ctx.avatar.url)
            
            await ctx.send(embed=embed)
    elif (role == "enforcer"):
        if (await attack(ctx.id, bot.get_user(targ), g, Attack.Default) == True):
            member:disnake.Member = var[g]["guildg"].get_member(targ)
            us:disnake.Member = var[g]["guildg"].get_member(ctx.id)
            await member.add_roles(disnake.utils.get(var[g]["guildg"].roles, name="[Anarchic] Dead"))
            await member.remove_roles(disnake.utils.get(var[g]["guildg"].roles, name="[Anarchic] Player"))
            Player.get_player(targ, var[g]["playerdict"]).diedln = True
            Player.get_player(targ, var[g]["playerdict"]).death.append(DeathReason.Enforcer)
            user = bot.get_user(targ)
            embed = disnake.Embed(title="**You were shot by an Enforcer <:enficon2:890339050865696798>.**", colour=disnake.Colour(0x7ed321), description="**You have died <:rip:878415658885480468>**.")

            embed.set_thumbnail(url="https://media.discordapp.net/attachments/867924656219377684/882797114634154014/unknown.png")
            embed.set_footer(text="Rest in peace.", icon_url=user.avatar.url)
            await user.send(embed=embed)
            if (Player.get_player(targ, var[g]["playerdict"]).faction == Faction.Town):
                embed = disnake.Embed(title="**You could not get over the guilt and shot yourself <:enficon2:890339050865696798>.**", colour=disnake.Colour(0x7ed321), description="**You have died <:rip:878415658885480468>**.")

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/879163761057992744/unknown.png?width=598&height=701")
                embed.set_footer(text="Rest in peace.", icon_url=us.avatar.url)
                
                await us.send(embed=embed)

                await us.add_roles(disnake.utils.get(var[g]["guildg"].roles, name="[Anarchic] Dead"))
                await us.remove_roles(disnake.utils.get(var[g]["guildg"].roles, name="[Anarchic] Player"))
                Player.get_player(us.id, var[g]["playerdict"]).diedln = True
                Player.get_player(us.id, var[g]["playerdict"]).dead = True
                Player.get_player(us.id, var[g]["playerdict"]).death.append(DeathReason.Guilt)
        else:
            embed = disnake.Embed(title="**Your target was too strong to be killed.**", colour=disnake.Colour(0xfff68a))

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/878379179106787359.png?v=1")
            embed.set_footer(text="Strange...", icon_url=ctx.avatar.url)
            
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

            if (value == targ and Player.get_player(targ, var[g]["playerdict"]).role != "Jester"):
                user = bot.get_user(int(key))
                embed = disnake.Embed(title=f"**{user.name} visited your target last night!**", colour=disnake.Colour(0x7ed321))

                embed.set_thumbnail(url=user.avatar.url)
                embed.set_footer(text="What were they doing there?", icon_url=ctx.avatar.url)
                await ctx.send(embed=embed)
                mister.append(int(key))
    elif (role == "tracker"):
        try:
            visited = var[g]["targets"][int(targ)]
            if (Player.get_player(int(targ), var[g]["playerdict"]).framed == True and var[g]["maftarget"] != 0):
                theuser = bot.get_user(var[g]["maftarget"])

                if (theuser != None):
                    embed = disnake.Embed(title=f"**Your target visited {theuser.name} last night!**", colour=disnake.Colour(0x7ed321))
                    embed.set_thumbnail(url=theuser.avatar.url)
                else:
                    embed = disnake.Embed(title="**Your target visited *someone* last night...**", colour = disnake.Colour(0x7ed321))

            
                embed.set_footer(text="What were they doing there?", icon_url=ctx.avatar.url)
                await ctx.send(embed=embed)
            elif (visited != 0 and Player.get_player(int(targ), var[g]["playerdict"]).distraction == False):
                user = bot.get_user(int(var[g]["targets"][targ]))
                embed = None	

                if (user != None):
                    embed = disnake.Embed(title=f"**Your target visited {user.name} last night!**", colour=disnake.Colour(0x7ed321))
                else:
                    embed = disnake.Embed(title="**Your target visited *someone* last night...**", colour = disnake.Colour(0x7ed321))

                embed.set_thumbnail(url=user.avatar.url)
                embed.set_footer(text="What were they doing there?", icon_url=ctx.avatar.url)
                await ctx.send(embed=embed)
        except Exception as e:
            print(e)
            return
    elif (role == "consort" or role == "attendant"):
        if (Player.get_player(targ, var[g]["playerdict"]).role == "Psychopath" and Player.get_player(targ, var[g]["playerdict"]).cautious == False):
            k = Player.get_player(ctx.id, var[g]["playerdict"])
            k.dead = True
            k.death.append(DeathReason.Psychopath)
            k.will = []
            k.will.append("Their last will was too bloody to be read.")
           
            embed = disnake.Embed(title="**You were stabbed by the **Psychopath <:psychoicon:909908333635440680>** you distracted.", colour=disnake.Colour(0x4a90e2), description="**You have died :rip:.**")

            embed.set_thumbnail(url="https://discord.com/assets/9f89170e2913a534d3dc182297c44c87.svg")
            embed.set_footer(text="Rest in peace.", icon_url="https://cdn.discordapp.com/avatars/667189788620619826/f4c9e87dde54e0e2d14db69b9d60deb9.png?size=128")
            await ctx.send(embed=embed)

            return
        else:
            if (Player.get_player(targ, var[g]["playerdict"]).role != "Attendant" and Player.get_player(targ, var[g]["playerdict"]).role != "Consort"):
                Player.get_player(targ, var[g]["playerdict"]).distraction = True
            
    elif (role == "jester"):
            member:disnake.Member = var[g]["guildg"].get_member(targ)
            await member.add_roles(disnake.utils.get(var[g]["guildg"].roles, name="[Anarchic] Dead"))
            await member.remove_roles(disnake.utils.get(var[g]["guildg"].roles, name="[Anarchic] Player"))
            await haunt(member, g)            
            embed = disnake.Embed(title="**You were haunted by the Jester <:jesticon2:889968373612560394>.**", colour=disnake.Colour(0xffc3e7), description="**You have died <:rip:872284978354978867>.**")

            embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/895419320140693584/export.png?width=396&height=408")
            embed.set_footer(text="Rest in peace.", icon_url=ctx.avatar.url)
            us = bot.get_user(targ)
            await us.send(embed=embed)
    elif (role == "framer"):
        Player.get_player(targ, var[g]["playerdict"]).framed = True
        Player.get_player(targ, var[g]["playerdict"]).checked = False
    elif (role == "detective"):
        if (await detcheck(targ, g) == True):
            embed = disnake.Embed(title="**Your target might not be what they seem at first glance.**", colour=disnake.Colour(0x7ed321), description="**They must be either...\n-A Framer <:frameicon2:890365634913902602>\n-A Jester <:jesticon2:889968373612560394>\n-The Mayor <:mayoricon:922566007946629131>\n-Or they're Framed <:frameicon2:890365634913902602>**")

            embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/896553626770755584/export.png")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Try convincing the others with your info.", icon_url=ctx.avatar.url)
            await ctx.send(embed=embed)
        else:
            play = Player.get_player(targ, var[g]["playerdict"])
            embed = disnake.Embed()

            if (play.role in ["Framer", "Jester", "Mayor"]):
                embed = disnake.Embed(title="**Your target might not be what they seem at first glance.**", colour=disnake.Colour(0x7ed321), description="**They must be either...\n-A Framer <:frameicon2:890365634913902602>\n-A Jester <:jesticon2:889968373612560394>\n-The Mayor <:mayoricon:922566007946629131>\n-Or they're Framed <:frameicon2:890365634913902602>**")

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/896553626770755584/export.png")
                embed.set_author(name="Investigation Results")
                embed.set_footer(text="Try convincing the others with your info.", icon_url=ctx.avatar.url)
            elif (play.role in ["Cop", "Headhunter", "Psychopath"]):
                embed = disnake.Embed(title="**Your target takes charge.**", colour=disnake.Colour(0x7ed321), description="**They must be either...\n-A Cop <:copicon2:889672912905322516>\n-A Headhunter <:hhicon2:891429754643808276>\n-A Mafioso <:maficon2:891739940055052328>\n-Or an Psychopath <:psychoicon:922564838897627166>**")

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/909911765851176981/export.png?width=120&height=120")
                embed.set_author(name="Investigation Results")
                embed.set_footer(text="Try convincing the others with your info.", icon_url=ctx.avatar.url)
            elif(play.role in ["Enforcer", "Mafioso", "Bodyguard"]):
                embed = disnake.Embed(title="**Your target bends the law to get what they want.**", colour=disnake.Colour(0x7ed321), description="**They must be either...\n-An Enforcer <:enficon2:890339050865696798>\n-A Mafioso <:maficon2:891739940055052328>\n-Or a [beta role!!!]**")

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/909911765851176981/export.png?width=120&height=120")
                embed.set_author(name="Investigation Results")
                embed.set_footer(text="Try convincing the others with your info.", icon_url=ctx.avatar.url)
            elif (play.role in ["Detective", "Consigliere", "Tracker"]):
                embed = disnake.Embed(title="**Your target works with sensitive information.**", colour=disnake.Colour(0x7ed321), description="**They must be either...\n-A Detective <:deticon2:889673135438319637>\n-A Consigliere <:consigicon2:896154845130666084>\nOr a Tracker <:trackicon:922885543812005949>**")

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/897585591397539860/works_with_sensitive_info.png?width=676&height=676")
                embed.set_author(name="Investigation Results")
                embed.set_footer(text="Try convincing the others with your info.", icon_url=ctx.avatar.url)
            elif (play.role in ["Attendant", "Consort", "Lookout"]):
                embed = disnake.Embed(title="**Your target works in the shadows.**", colour=disnake.Colour(0x7ed321), description="**They must be either...\n-An [insert secret beta role here]\n-A Consort <:consicon:873954973556293632>\n-Or a Lookout <:loicon2:889673190392078356>**")

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/897585591397539860/works_with_sensitive_info.png?width=676&height=676")
                embed.set_author(name="Investigation Results")
                embed.set_footer(text="Try convincing the others with your info.", icon_url=ctx.avatar.url)
            elif (play.role in ["Doctor", "Psychic", "Janitor"]):
                embed = disnake.Embed(title="**Your target associates themselves with the dead.**", colour=disnake.Colour(0x7ed321), description="**They must be either...\n-A Doctor <:docicon2:890333203959787580>\n-A Psychic <:psyicon2:896159311078780938>\n-Or a Janitor <:janiicon:923219547325091840>**")

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/897585591397539860/works_with_sensitive_info.png?width=676&height=676")
                embed.set_author(name="Investigation Results")
                embed.set_footer(text="Try convincing the others with your info.", icon_url=ctx.avatar.url)
            else:
                embed = disnake.Embed(title="**Your target is mysterious.**", colour=disnake.Colour(0x7ed321), description="**They must be either...\n-A ???\nA ???\nOr a ???")

                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/878437549721419787/884534469225242634/unknown-removebg-preview.png")
                embed.set_author(name="Investigation Results")
                embed.set_footer(text="Try convincing the others with this weird info.", icon_url=ctx.avatar.url)

            await ctx.send(embed=embed)        
    elif (role == "consigliere"):
        play = Player.get_player(targ, var[g]["playerdict"])
        embed = disnake.Embed()

        if (play.role == "Cop"):
            embed = disnake.Embed(title="**Your target is the law enforcer of the town.**", colour=disnake.Colour(0xd0021b), description="**They must be a Cop <:copicon2:889672912905322516>**")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889672912905322516.png?size=96")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Interesting", icon_url=ctx.avatar.url)
            await ctx.send(embed=embed)
        elif (play.role == "Doctor"):
            embed = disnake.Embed(title="**Your target is a profound surgeon.**", colour=disnake.Colour(0xd0021b), description="**They must be a Doctor <:docicon2:890333203959787580>**")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/890333203959787580.png?size=44")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Interesting", icon_url=ctx.avatar.url)
            await ctx.send(embed=embed)
        elif(play.role == "Lookout"):
            embed = disnake.Embed(title="**Your target watches other people's houses at night.**", colour=disnake.Colour(0xd0021b), description="**They must be a Lookout <:loicon2:889673190392078356>**")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889673190392078356.png?size=44")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Interesting", icon_url=ctx.avatar.url)
            await ctx.send(embed=embed)
        elif (play.role == "Mayor"):
            embed = disnake.Embed(title="**Your target leads the town in trials.**", colour=disnake.Colour(0xd0021b), description="**They must be the Mayor <:mayoricon2:891719324509831168>**")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/891719324509831168.png?size=44")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Interesting", icon_url=ctx.avatar.url)
            await ctx.send(embed=embed)
        elif (play.role == "Enforcer"):
            embed = disnake.Embed(title="**Your target is willing to bend the law to enact justice.**", colour=disnake.Colour(0xd0021b), description="**They must be a Enforcer <:enficon2:890339050865696798>**")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/890339050865696798.png?size=44")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Interesting", icon_url=ctx.avatar.url)
            await ctx.send(embed=embed)
        elif (play.role == "Detective"):
            embed = disnake.Embed(title="**Your target gathers intel for the town.**", colour=disnake.Colour(0xd0021b), description="**They must be a Detective <:deticon2:889673135438319637>**")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889673135438319637.png?size=44")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Interesting", icon_url=ctx.avatar.url)
            await ctx.send(embed=embed)
        elif (play.role == "Psychic"):
            embed = disnake.Embed(title="**Your target is vessel for the deceased.**", colour=disnake.Colour(0xd0021b), description="**They must be a Psychic <:psyicon2:896159311078780938>**")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/896159311078780938.png?size=80")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Interesting", icon_url=ctx.avatar.url)
            await ctx.send(embed=embed)
        elif (play.role == "Headhunter"):
            embed = disnake.Embed(title="**Your target wants someone hung at all costs.**", colour=disnake.Colour(0xd0021b), description="**They must be a Headhunter <:hhicon2:891429754643808276>**")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/891429754643808276.png?size=96")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Interesting", icon_url=ctx.avatar.url)
            await ctx.send(embed=embed)
        elif (play.role == "Jester"):
            embed = disnake.Embed(title="**Your target is a crazed lunatic waiting to be hung.**", colour=disnake.Colour(0xd0021b), description="**They must be a Jester <:jesticon2:889968373612560394>**")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889968373612560394.png?size=44")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Interesting", icon_url=ctx.avatar.url)
            await ctx.send(embed=embed)
        elif (play.role == "Janitor"):
            embed = disnake.Embed(title="**Your target cleans up the dead.**", colour=disnake.Colour(0xd0021b), description="**They must be a Janitor <:janiicon:923219547325091840>**")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/923219547325091840.png?size=80")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Interesting", icon_url=ctx.avatar.url)
            await ctx.send(embed=embed)
        elif (play.role == "Psychopath"):
            embed = disnake.Embed(title="**Your target wants everyone in shallow graves.**", colour=disnake.Colour(0xd0021b), description="**They must be a Psychopath <:psychoicon:922564838897627166>**")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/922564838897627166.png?size=80")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Interesting", icon_url=ctx.avatar.url)
            await ctx.send(embed=embed)
        elif (play.role == "Tracker"):
            embed = disnake.Embed(title="**Your target stalks others for information.**", colour=disnake.Colour(0xd0021b), description="**They must be a Tracker <:trackicon:922885543812005949>**")

            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/922885543812005949.png?size=80")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Interesting", icon_url=ctx.avatar.url)
            await ctx.send(embed=embed)
        else:
            embed = disnake.Embed(title="**Your target is mysterious.**", colour=disnake.Colour(0x7ed321), description="**They must be either...\n-A ???\nA ???\nOr a ???")

            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/878437549721419787/884534469225242634/unknown-removebg-preview.png")
            embed.set_author(name="Investigation Results")
            embed.set_footer(text="Try convincing the others with this weird info.", icon_url=ctx.avatar.url)
            await ctx.send(embed=embed)
    else:
        await ctx.send("No results, sorry man")

    var[g]["resul"] -= 1

#Main function for targeting embeds
async def target(ctx:disnake.User, r):
    try:
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
            embed = disnake.Embed(title="Who do you interrogate tonight?", description="", color=0x7ed321)
            
            for key, value in var[r]["playeremoji"].items():
                if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                    
                    continue
                else:
                    user:disnake.User = bot.get_user(value)
                    embed.add_field(name=f"{key} - {user.name}#{user.discriminator} :mag_right:", value="** **", inline=False)

            embed.add_field(name="Time :hourglass::", value="You have 30 seconds to choose.")

            embed.description = "**Your targets are...**"
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/871524614914834432/IconCop-removebg-preview.png")
            
            if (random.randint(1, 50) == 47):
                embed.set_image(url="https://media.discordapp.net/attachments/887803391466680360/943672619176169472/LOL.png?width=480&height=485")
            else:
                embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/871511037743071232/unknown.png?width=677&height=634")
            
            embed.set_footer(text="React with who you want to interrogate.", icon_url=ctx.avatar.url)
            b = await ctx.send(embed=embed)



            for key, value in var[r]["playeremoji"].items():
                        if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                            continue
                        else:
                            await b.add_reaction(key)


            reactions = b.reactions        
            def check(reaction:Reaction, user):
                    return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]  

            try:
                reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
                target = var[r]["playeremoji"][reaction.emoji]
                var[r]["targets"][ctx.id] = target
                targetuser = bot.get_user(target)
                embed = disnake.Embed(title=f"**You have decided to interrogate {targetuser.name} tonight.**", color=0x7ed321)
                embed.set_thumbnail(url=targetuser.avatar.url)
                embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar.url)
                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
                await ctx.send(embed=embed)
            except asyncio.TimeoutError:
                var[r]["targets"][ctx.id] = 0
                embed = disnake.Embed(title="**You did not perform your night ability.**", colour=disnake.Colour(0xd3d3d3))

                embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
                embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar.url)
                await ctx.send(embed=embed)
                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True

            
            af = 0
            max = 0
            for key, value in var[r]["playerdict"].items():
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
            embed = disnake.Embed(title="Who do you track tonight?", description="", color=0x7ed321)
            
            for key, value in var[r]["playeremoji"].items():
                if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                    
                    continue
                else:
                    user:disnake.User = bot.get_user(value)
                    embed.add_field(name=f"{key} - {user.name}#{user.discriminator} :mag_right:", value="** **", inline=False)

            embed.add_field(name="Time :hourglass::", value="You have 30 seconds to choose.")

            embed.description = "**Your targets are...**"
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/871524614914834432/IconCop-removebg-preview.png")
            embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/926296181192163368/unknown.png")
            embed.set_footer(text="React with who you want to track.", icon_url=ctx.avatar.url)
            b = await ctx.send(embed=embed)



            for key, value in var[r]["playeremoji"].items():
                        if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                            continue
                        else:
                            await b.add_reaction(key)


            reactions = b.reactions        
            def check(reaction:Reaction, user):
                    return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]  

            try:
                reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
                target = var[r]["playeremoji"][reaction.emoji]
                var[r]["targets"][ctx.id] = target
                targetuser = bot.get_user(target)
                embed = disnake.Embed(title=f"**You have decided to track {targetuser.name} tonight.**", color=0x7ed321)
                embed.set_thumbnail(url=targetuser.avatar.url)
                embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar.url)
                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
                await ctx.send(embed=embed)
            except asyncio.TimeoutError:
                var[r]["targets"][ctx.id] = 0
                embed = disnake.Embed(title="**You did not perform your night ability.**", colour=disnake.Colour(0xd3d3d3))

                embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
                embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar.url)
                await ctx.send(embed=embed)
                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
            
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
            var[r]["maftarget"] = 0
            message = "**Your targets are...**"
            embed = disnake.Embed(title="**Who would you like to attack tonight?**", colour=disnake.Colour(0xd0021b), description="**Your targets are...**")

            if (random.randint(1, 384759034) == 4535):
                embed.set_image(url="https://cdn.discordapp.com/attachments/765738640554065962/899313643274010644/unknown.png")
            else:
                embed.set_image(url="https://images-ext-1.discordapp.net/external/MHSYSxBlhJcGfqEVLdj1h1AkLF-Q5MRD9VESaxZ1mz4/%3Fwidth%3D798%26height%3D634/https/media.discordapp.net/attachments/765738640554065962/871823862755622962/unknown.png")
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/897585492562964531/MafIcon2.png?width=676&height=676")
            embed.set_footer(text="React with who you want to attack.", icon_url=ctx.avatar.url)
            for key, value in var[r]["playeremoji"].items():
                if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True or Player.get_player(value, var[r]["playerdict"]).faction == Faction.Mafia):
                    continue
                else:
                    user:disnake.User = bot.get_user(value)
                    embed.add_field(name=f"{key} - {user.name}#{user.discriminator} :dagger:", value="** **", inline=False)

            b = await ctx.send(embed=embed)

            for key, value in var[r]["playeremoji"].items():
                        if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True or Player.get_player(value, var[r]["playerdict"]).faction == Faction.Mafia):
                            continue
                        else:
                            await b.add_reaction(key)

            reactions = b.reactions        
            def check(reaction:Reaction, user):
                    return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]  

            try:
                reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
                target = var[r]["playeremoji"][reaction.emoji]
                var[r]["targets"][ctx.id] = target
                targetuser:disnake.User = bot.get_user(target)
                embed = disnake.Embed(title=f"**You have decided to kill {targetuser.name} tonight.**", colour=disnake.Colour(0xd0021b))

                embed.set_thumbnail(url=targetuser.avatar.url)
                embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar.url)
                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
                var[r]["maftarget"] = target
                        
                

                await ctx.send(embed=embed)

                embed = disnake.Embed(title=f"**{ctx.name} has decided to kill {targetuser.name}#{targetuser.discriminator} tonight.**", colour=disnake.Colour(0xd0021b))

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/891739940055052328.png?size=80")
                await var[r]["mafcon"].send(embed=embed)
            
            except asyncio.TimeoutError:
                var[r]["targets"][ctx.id] = 0
                embed = disnake.Embed(title="**You did not perform your night ability.**", colour=disnake.Colour(0xd3d3d3))

                embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
                embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar.url)
                await ctx.send(embed=embed)
                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True

                embed = disnake.Embed(title=f"**{ctx.name} did not preform their night ability.**", colour=disnake.Colour(0xd0021b))

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/891739940055052328.png?size=80")
                await var[r]["mafcon"].send(embed=embed)



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
        elif (role == "janitor"):
            if (Player.get_player(ctx.id, var[r]["playerdict"]).charges > 0):
                message = "**Your targets are...**"
                embed = disnake.Embed(title="**Who would you like to clean tonight?**", colour=disnake.Colour(0xd0021b), description="**Your targets are...**")

                embed.set_image(url="https://cdn.discordapp.com/attachments/765738640554065962/916689134377140254/unknown.png")
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/897585492562964531/MafIcon2.png?width=676&height=676")
                embed.set_footer(text="React with who you want to attack.", icon_url=ctx.avatar.url)
                for key, value in var[r]["playeremoji"].items():
                    if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True or Player.get_player(value, var[r]["playerdict"]).faction == Faction.Mafia):
                        continue
                    else:
                        user:disnake.User = bot.get_user(value)
                        embed.add_field(name=f"{key} - {user.name}#{user.discriminator} :dagger:", value="** **", inline=False)

                b = await ctx.send(embed=embed)

                for key, value in var[r]["playeremoji"].items():
                            if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True or Player.get_player(value, var[r]["playerdict"]).faction == Faction.Mafia):
                                continue
                            else:
                                await b.add_reaction(key)

                reactions = b.reactions        
                def check(reaction:Reaction, user):
                        return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]  

                try:
                    reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
                    target = var[r]["playeremoji"][reaction.emoji]
                    var[r]["targets"][ctx.id] = target
                    targetuser:disnake.User = bot.get_user(target)
                    embed = disnake.Embed(title=f"**You have decided to clean {targetuser.name} tonight.**", colour=disnake.Colour(0xd0021b))

                    embed.set_thumbnail(url=targetuser.avatar.url)
                    embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar.url)
                    Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
                            
                    

                    await ctx.send(embed=embed)

                    embed = disnake.Embed(title=f"**{ctx.name} has decided to clean {targetuser.name}#{targetuser.discriminator} tonight.**", colour=disnake.Colour(0xd0021b))

                    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/891739940055052328.png?size=80")
                    await var[r]["mafcon"].send(embed=embed)
                
                except asyncio.TimeoutError:
                    var[r]["targets"][ctx.id] = 0
                    embed = disnake.Embed(title="**You did not perform your night ability.**", colour=disnake.Colour(0xd3d3d3))

                    embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
                    embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar.url)
                    await ctx.send(embed=embed)
                    Player.get_player(ctx.id, var[r]["playerdict"]).ready = True

                    embed = disnake.Embed(title=f"**{ctx.name} did not preform their night ability.**", colour=disnake.Colour(0xd0021b))

                    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/891739940055052328.png?size=80")
                    await var[r]["mafcon"].send(embed=embed)



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
                return
        elif (role == "psychopath"):
            embed = disnake.Embed(title="Would you like to go cautious tonight?", description="", color=0x070569)
            embed.add_field(name="Time :hourglass::", value="You have 30 seconds to choose.")

            embed.set_thumbnail(url="https://discord.com/assets/9f89170e2913a534d3dc182297c44c87.svg")
            embed.set_image(url="https://cdn.discordapp.com/attachments/878437549721419787/882418844424081449/unknown.png")
            embed.set_footer(text="React yes or no.", icon_url=ctx.avatar.url)

            o = await ctx.send(embed=embed)
            await o.add_reaction("✅")
            await o.add_reaction("❌") 

            def check(reaction:Reaction, user):
                return user.id == ctx.id and str(reaction.emoji) in ["✅", "❌"]

            try:
                reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
                

                if (reaction.emoji == "✅"):
                    Player.get_player(ctx.id, var[r]["playerdict"]).cautious = True

                else:
                    Player.get_player(ctx.id, var[r]["playerdict"]).cautious = False

                embed = disnake.Embed(title="**Who would you stab tonight?**", colour=disnake.Colour(0x070569), description="**Your targets are...**")

                embed.set_image(url="https://images-ext-1.discordapp.net/external/MHSYSxBlhJcGfqEVLdj1h1AkLF-Q5MRD9VESaxZ1mz4/%3Fwidth%3D798%26height%3D634/https/media.discordapp.net/attachments/765738640554065962/871823862755622962/unknown.png")
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/897585492562964531/MafIcon2.png?width=676&height=676")
                embed.set_footer(text="React with who you want to stab.", icon_url=ctx.avatar.url)
                for key, value in var[r]["playeremoji"].items():
                    if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                        continue
                    else:
                        user:disnake.User = bot.get_user(value)
                        embed.add_field(name=f"{key} - {user.name}#{user.discriminator} 🔪", value="** **", inline=False)

                b = await ctx.send(embed=embed)

                for key, value in var[r]["playeremoji"].items():
                            if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                                continue
                            else:
                                await b.add_reaction(key)

                reactions = b.reactions

                def check(reaction:Reaction, user):
                        return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"] and str(reaction.emoji) in var[r]["emojis"] 

                player = Player.get_player(ctx.id, var[r]["playerdict"])

                try:
                    reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
                    target = var[r]["playeremoji"][reaction.emoji]
                    var[r]["targets"][ctx.id] = target
                    targetuser:disnake.User = bot.get_user(target)

                    cc = ""
                    if (player.cautious):
                        cc = ":warning: **- Go cautious tonight**"
                    else:
                        cc = ":man_running: **- Go incautious tonight**"

                    embed = disnake.Embed(title=f"**You have decided to:**", colour=disnake.Colour(0x070569), description=f"{cc}\n:knife: **- Stab {targetuser.name}")

                    embed.set_thumbnail(url=targetuser.avatar.url)
                    embed.set_footer(text="Please wait for other players to choose their actions.", icon_url=ctx.avatar.url)
                    await ctx.send(embed=embed)
                
                except asyncio.TimeoutError:
                    var[r]["targets"][ctx.id] = 0
                    embed = disnake.Embed(title="**You did not perform your night ability.**", colour=disnake.Colour(0xd3d3d3))

                    embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
                    embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar.url)
                    await ctx.send(embed=embed)
                    Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
                    
                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
        
            except asyncio.TimeoutError:
                var[r]["targets"][ctx.id] = 0
                embed = disnake.Embed(title="**You did not perform your night ability.**", colour=disnake.Colour(0xd3d3d3))

                embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
                embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar.url)
                await ctx.send(embed=embed)
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
        elif (role == "doctor"):
            message = "**Your targets are...**"
            embed = disnake.Embed(title="**Who do you heal tonight?**", colour=disnake.Colour(0x7ed321), description="**Y឵our targets are...**")

            embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/892916234654474290/DocTargeting.png?width=371&height=383")
            embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/z-NBaQM3t7KvWEy9hUjDQcmgdecDVw8TmTy8mCwzSwA/https/media.discordapp.net/attachments/765738640554065962/871898167845720134/doctoricon-removebg-preview.png")
            for key, value in var[r]["playeremoji"].items():
                if (Player.get_player(value, var[r]["playerdict"]).dead == True):
                    continue
                else:
                    if (value == ctx.id):
                        if (Player.get_player(ctx.id, var[r]["playerdict"]).docHealedHimself):
                            continue

                    user:disnake.User = bot.get_user(value)
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
            
            reactions = b.reactions        
            def check(reaction:Reaction, user):
                    return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]  

            try:
                reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
                target = var[r]["playeremoji"][reaction.emoji]
                var[r]["targets"][ctx.id] = target
                targetuser = bot.get_user(target)
                embed = disnake.Embed(title=f"**You have decided to heal {targetuser.name} tonight.**", colour=disnake.Colour(0x7ed321))

                embed.set_thumbnail(url=targetuser.avatar.url)
                embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar.url)
                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
                        
                await ctx.send(embed=embed)
                
            except asyncio.TimeoutError:
                var[r]["targets"][ctx.id] = 0
                embed = disnake.Embed(title="**You did not perform your night ability.**", colour=disnake.Colour(0xd3d3d3))

                embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
                embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar.url)
                await ctx.send(embed=embed)
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
        elif (role == "enforcer"):
            if (var[r]["gday"] == 1):
                embed = disnake.Embed(title="**You are reloading your gun.**", colour=disnake.Colour(0x7ed321), description="**You may not shoot anyone on the first night.**")

                embed.set_image(url="https://media.discordapp.net/attachments/879156984807559228/879161044092739685/unknown.png?width=598&height=634")
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/872955907967942664/p-trans.png")
                embed.set_footer(text="You must wait a night before shooting.", icon_url=ctx.avatar.url)

                await ctx.send(embed=embed)
                var[r]["targets"][ctx.id] = 0
                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
            else:
                message = "**Your targets are...**"
                embed = disnake.Embed(title="**Who do you shoot tonight?**", colour=disnake.Colour(0x7ed321), description="**Your targets are...**")

                embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/872233227140603944/unknown.png?width=560&height=634")
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/872955907967942664/p-trans.png")
                embed.set_footer(text="React with who you want to shoot.", icon_url=ctx.avatar.url)

                for key, value in var[r]["playeremoji"].items():
                    if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                        continue
                    else:
                        user:disnake.User = bot.get_user(value)
                        embed.add_field(name=f"{key} - {user.name}#{user.discriminator} :gun:", value="** **", inline=False)

                b = await ctx.send(embed=embed)

                for key, value in var[r]["playeremoji"].items():
                            if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                                continue
                            else:
                                await b.add_reaction(key)  

                reactions = b.reactions
                def check(reaction:Reaction, user):
                    return user.id == ctx.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]

                try:
                    reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
                    target = var[r]["playeremoji"][reaction.emoji]
                    var[r]["targets"][ctx.id] = target
                    targetuser = bot.get_user(target)
                    embed = disnake.Embed(title=f"**You have decided to shoot {targetuser.name} tonight.**", colour=disnake.Colour(0x7ed321))

                    embed.set_thumbnail(url=targetuser.avatar.url)
                    embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar.url)
                    Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
                            
                    await ctx.send(embed=embed)
                    
                except asyncio.TimeoutError:
                    var[r]["targets"][ctx.id] = 0
                    embed = disnake.Embed(title="**You did not perform your night ability.**", colour=disnake.Colour(0xd3d3d3))

                    embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
                    embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar.url)
                    await ctx.send(embed=embed)
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
        elif (role == "lookout"):
            message = "**Your targets are...**"
            embed = disnake.Embed(title="**Who do you watch over tonight?**", colour=disnake.Colour(0x7ed321), description="**Your targets are...**")

            embed.set_image(url="https://images-ext-2.discordapp.net/external/LeVUTk0nutucMC5NAnvFMKh_fxm8MHclkGojmefTN6c/%3Fwidth%3D856%26height%3D634/https/media.discordapp.net/attachments/765738640554065962/873604432858861578/unknown.png")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/873351736662847549.png?v=1")
            embed.set_footer(text="React with who you want to watch over.", icon_url=ctx.avatar.url)


            for key, value in var[r]["playeremoji"].items():
                if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                    continue
                else:
                    user:disnake.User = bot.get_user(value)
                    embed.add_field(name=f"{key} - {user.name}#{user.discriminator} :telescope:", value="** **", inline=False)

            b = await ctx.send(embed=embed)

            for key, value in var[r]["playeremoji"].items():
                        if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                            continue
                        else:
                            await b.add_reaction(key)  

            reactions = b.reactions

            reactions = b.reactions        
            def check(reaction:Reaction, user):
                    return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]   
            try:
                reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
                target = var[r]["playeremoji"][reaction.emoji]
                var[r]["targets"][ctx.id] = target
                targetuser = bot.get_user(target)
                embed = disnake.Embed(title=f"**You have decided to watch over {targetuser.name} tonight.**", colour=disnake.Colour(0x7ed321))

                embed.set_thumbnail(url=targetuser.avatar.url)
                embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar.url)
                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
                        
                await ctx.send(embed=embed)
                
            except asyncio.TimeoutError:
                var[r]["targets"][ctx.id] = 0
                embed = disnake.Embed(title="**You did not perform your night ability.**", colour=disnake.Colour(0xd3d3d3))

                embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
                embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar.url)
                await ctx.send(embed=embed)
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
        elif (role == "consort"):
            embed = disnake.Embed(title="**Who do you distract tonight?**", colour=disnake.Colour(0xd0021b), description="**Your targets are...**")

            embed.set_image(url="https://cdn.discordapp.com/attachments/878437549721419787/882739145762545714/unknown-removebg-preview.png")
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/871525831422398497/890335792772313098/ConsIcon.png?width=701&height=701")
            embed.set_footer(text="React with who you want to distract.", icon_url=ctx.avatar.url)

            for key, value in var[r]["playeremoji"].items():
                if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True or Player.get_player(value, var[r]["playerdict"]).faction == Faction.Mafia):
                    continue
                else:
                    user:disnake.User = bot.get_user(value)
                    embed.add_field(name=f"{key} - {user.name}#{user.discriminator} :lipstick:", value="** **", inline=False)

            embed.add_field(name="Time :hourglass::", value="You have 30 seconds to choose.")

            b = await ctx.send(embed=embed)


            for key, value in var[r]["playeremoji"].items():
                        if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True or Player.get_player(value, var[r]["playerdict"]).faction == Faction.Mafia):
                            continue
                        else:
                            await b.add_reaction(key)  



            reactions = b.reactions        
            def check(reaction:Reaction, user):
                    return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]   

            try:
                reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
                target = var[r]["playeremoji"][reaction.emoji]
                var[r]["targets"][ctx.id] = target

                targetuser = bot.get_user(target)
                embed = disnake.Embed(title=f"**You have decided to distract {targetuser.name} tonight.**", colour=disnake.Colour(0xd0021b))

                embed.set_thumbnail(url=targetuser.avatar.url)
                embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar.url)
                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
                await ctx.send(embed=embed)

                embed = disnake.Embed(title=f"**{ctx.name} has decided to distract {targetuser.name}#{targetuser.discriminator} tonight.**", colour=disnake.Colour(0xd0021b))

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/871525831422398497/890335792772313098/ConsIcon.png?width=701&height=701")

                await var[r]["mafcon"].send(embed=embed)
            except asyncio.TimeoutError:
                var[r]["targets"][ctx.id] = 0
                embed = disnake.Embed(title="**You did not perform your night ability.**", colour=disnake.Colour(0xd3d3d3))

                embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
                embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar.url)
                await ctx.send(embed=embed)
                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True

                embed = disnake.Embed(title=f"**{ctx.name} has did not preform their night ability.**", colour=disnake.Colour(0xd0021b))

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/871525831422398497/890335792772313098/ConsIcon.png?width=701&height=701")
                await var[r]["mafcon"].send(embed=embed)


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
        elif (role == "attendant"):
            embed = disnake.Embed(title="**Who do you attend dto tonight?**", colour=disnake.Colour(0xd0021b), description="**Your targets are...**")

            embed.set_image(url="https://cdn.discordapp.com/attachments/878437549721419787/882739145762545714/unknown-removebg-preview.png")
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/871525831422398497/890335792772313098/ConsIcon.png?width=701&height=701")
            embed.set_footer(text="React with who you want to distract.", icon_url=ctx.avatar.url)

            for key, value in var[r]["playeremoji"].items():
                if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                    continue
                else:
                    user:disnake.User = bot.get_user(value)
                    embed.add_field(name=f"{key} - {user.name}#{user.discriminator} :lipstick:", value="** **", inline=False)

            embed.add_field(name="Time :hourglass::", value="You have 30 seconds to choose.")

            b = await ctx.send(embed=embed)


            for key, value in var[r]["playeremoji"].items():
                        if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                            continue
                        else:
                            await b.add_reaction(key)  



            reactions = b.reactions        
            def check(reaction:Reaction, user):
                    return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]  

            try:
                reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
                target = var[r]["playeremoji"][reaction.emoji]
                var[r]["targets"][ctx.id] = target

                targetuser = bot.get_user(target)
                embed = disnake.Embed(title=f"**You have decided to distract {targetuser.name} tonight.**", colour=disnake.Colour(0xd0021b))

                embed.set_thumbnail(url=targetuser.avatar.url)
                embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar.url)
                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
                await ctx.send(embed=embed)
            except asyncio.TimeoutError:
                var[r]["targets"][ctx.id] = 0
                embed = disnake.Embed(title="**You did not perform your night ability.**", colour=disnake.Colour(0xd3d3d3))

                embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
                embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar.url)
                await ctx.send(embed=embed)
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
        elif (role == "jester"):
            if (Player.get_player(ctx.id, var[r]["playerdict"]).jesterwin == True):
                message = "**Your targets are...**"
                embed = disnake.Embed(title="**Who do you wish to haunt?**", colour=disnake.Colour(0xffc3e7), description="**Your targets are...**")

                embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/895419320140693584/export.png?width=396&height=408")
                embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/F8o5Mi5dYJDvkfQ3B98JCbUYmdmdnupZQyNa2wXpEBk/https/media.discordapp.net/attachments/765738640554065962/872147798336893019/imageedit_4_4906520050.png")
                embed.set_footer(text="React with who you to take your revenge on.", icon_url=ctx.avatar.url)
                index = 0

                for key, value in var[r]["playeremoji"].items():
                    if (value != ctx.id):
                        if (Player.get_player(value, var[r]["playerdict"]).dead == True):
                            continue
                        else:
                            if (Player.get_player(value, var[r]["playerdict"]).id in var[r]["guiltyers"] == False):
                                index += 1
                                continue

                            user:disnake.User = bot.get_user(value)
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
                            
                reactions = b.reactions

                def check(reaction:Reaction, user):
                    return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]

                try:
                    reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
                    target = var[r]["playeremoji"][reaction.emoji]
                    var[r]["targets"][ctx.id] = target
                    targetuser = bot.get_user(target)
                    embed = disnake.Embed(title=f"**You have decided to haunt {targetuser.name} tonight.**", colour=disnake.Colour(0xffc3e7))

                    embed.set_thumbnail(url=targetuser.avatar.url)
                    embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar.url)
                    Player.get_player(ctx.id, var[r]["playerdict"]).ready = True

                    await ctx.send(embed=embed)
                except asyncio.TimeoutError:
                    tcf = []

                    for i in var[r]["playerdict"].values():
                        if (i.id in var[r]["guiltyers"]):
                            tcf.append(i.id)

                    var[r]["targets"][ctx.id] = random.choice(tcf)

                    e = bot.get_user(var[r]["targets"][ctx.id])
                    member:disnake.Member = var[r]["guildg"].get_member(e.id)

                    embed = disnake.Embed(title="**You have not chosen anyone so a random target was selected instead.**", colour=disnake.Colour(0xffc3e7))

                    embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/F8o5Mi5dYJDvkfQ3B98JCbUYmdmdnupZQyNa2wXpEBk/https/media.discordapp.net/attachments/765738640554065962/872147798336893019/imageedit_4_4906520050.png")
                    embed.set_footer(text="Who is the unlucky fellow?", icon_url=ctx.avatar.url)
                    await ctx.send(embed=embed)
                    Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
                    await haunt(member, r)
                    embed = disnake.Embed(title="**You were haunted by the Jester <:jesticon2:889968373612560394>.**", colour=disnake.Colour(0xffc3e7), description="**You have died <:rip:747726596475060286>.**")

                    embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/895419320140693584/export.png?width=396&height=408")
                    embed.set_footer(text="Rest in peace.", icon_url=ctx.avatar.url)
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
            embed = disnake.Embed(title="**Who do you investigate tonight?**", colour=disnake.Colour(0xd0021b), description="**Your targets are...**")

            embed.set_image(url="https://media.discordapp.net/attachments/765738640554065962/899070109002379315/image0.png?width=396&height=408")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/871527176527315025.png?size=96")
            embed.set_footer(text="React with who you want to investigate.", icon_url=ctx.avatar.url)
            
            for key, value in var[r]["playeremoji"].items():
                if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True or Player.get_player(value, var[r]["playerdict"]).faction == Faction.Mafia):
                    continue
                else:
                    user:disnake.User = bot.get_user(value)
                    embed.add_field(name=f"{key} - {user.name}#{user.discriminator} :mag_right:", value="** **", inline=False)

            embed.add_field(name="Time :hourglass::", value="You have 30 seconds to choose.")
            b = await ctx.send(embed=embed)



            for key, value in var[r]["playeremoji"].items():
                        if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True or Player.get_player(value, var[r]["playerdict"]).faction == Faction.Mafia):
                            continue
                        else:
                            await b.add_reaction(key)


            reactions = b.reactions        
            def check(reaction:Reaction, user):
                    return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]  

            try:
                reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
                target = var[r]["playeremoji"][reaction.emoji]
                var[r]["targets"][ctx.id] = target
                targetuser = bot.get_user(target)
                embed = disnake.Embed(title=f"**You have decided to investigate {targetuser.name} tonight.**", colour=disnake.Colour(0xd0021b))
                embed.set_thumbnail(url=targetuser.avatar.url)
                embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar.url)
                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
                await ctx.send(embed=embed)

                embed = disnake.Embed(title=f"**{ctx.name} has decided to investigate {targetuser.name}#{targetuser.discriminator} tonight.**", colour=disnake.Colour(0xd0021b))

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/896154319747944468/ConsigIcon.png?width=468&height=468")
                await var[r]["mafcon"].send(embed=embed)
            except asyncio.TimeoutError:
                var[r]["targets"][ctx.id] = 0
                embed = disnake.Embed(title="**You did not perform your night ability.**", colour=disnake.Colour(0xd3d3d3))

                embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
                embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar.url)
                await ctx.send(embed=embed)

                embed = disnake.Embed(title=f"**{ctx.name} did not preform their night ability.**", colour=disnake.Colour(0xd0021b))

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/896154319747944468/ConsigIcon.png?width=468&height=468")
                await var[r]["mafcon"].send(embed=embed)

                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True

            
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
                embed = disnake.Embed(title="Would you like to reveal?", description="", color=0x7ed321)
                embed.add_field(name="Time :hourglass::", value="You have 30 seconds to choose.")

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/897570023143518288.png?size=80")
                embed.set_image(url="https://cdn.discordapp.com/attachments/878437549721419787/882418844424081449/unknown.png")
                embed.set_footer(text="React yes or no.", icon_url=ctx.avatar.url)
                b = await ctx.send(embed=embed)

                await b.add_reaction("✅")
                await b.add_reaction("❌")



                def check(reaction:Reaction, user):
                    return user.id == ctx.id and str(reaction.emoji) in ["✅", "❌"]

                try:
                    reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
                    if (reaction.emoji == "✅"):
                        var[r]["targets"][ctx.id] = True
                        embed = disnake.Embed(title=f"**You have decided to reveal tonight.**", color=0x7ed321)
                        embed.set_thumbnail(url=ctx.avatar.url)
                        embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar.url)
                    else:
                        embed = disnake.Embed(title=f"**You have decided to not reveal tonight.**", color=0x7ed321)
                        embed.set_thumbnail(url=ctx.avatar.url)
                        embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar.url)
                    
                    Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
                    await ctx.send(embed=embed)
                except asyncio.TimeoutError:
                    var[r]["targets"][ctx.id] = 0
                    embed = disnake.Embed(title="**You did not perform your night ability.**", colour=disnake.Colour(0xd3d3d3))

                    embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
                    embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar.url)
                    await ctx.send(embed=embed)
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
            embed = disnake.Embed(title="**Who do you frame tonight?**", colour=disnake.Colour(0xd0021b), description="**Your targets are...**")

            embed.set_image(url="https://cdn.discordapp.com/attachments/765738640554065962/886034880503382056/unknown.png")
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/871525831422398497/890365126866251796/FrameIcon_3.png?width=701&height=701")
            embed.set_footer(text="React with who you want to frame.", icon_url=ctx.avatar.url)
            for key, value in var[r]["playeremoji"].items():
                if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True or Player.get_player(value, var[r]["playerdict"]).faction == Faction.Mafia):
                    continue
                else:
                    user:disnake.User = bot.get_user(value)
                    embed.add_field(name=f"{key} - {user.name}#{user.discriminator} :receipt:", value="** **", inline=False)

            embed.add_field(name="Time :hourglass::", value="You have 30 seconds to choose.")

            b = await ctx.send(embed=embed)


            for key, value in var[r]["playeremoji"].items():
                        if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True or Player.get_player(value, var[r]["playerdict"]).faction == Faction.Mafia):
                            continue
                        else:
                            await b.add_reaction(key)  



            reactions = b.reactions        
            def check(reaction:Reaction, user):
                    return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]  

            try:
                reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
                target = var[r]["playeremoji"][reaction.emoji]
                var[r]["targets"][ctx.id] = target
                targetuser = bot.get_user(target)
                embed = disnake.Embed(title=f"**You have decided to frame {targetuser.name} tonight.**", colour=disnake.Colour(0xd0021b))

                embed.set_thumbnail(url=targetuser.avatar.url)
                embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar.url)
                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
                await ctx.send(embed=embed)

                embed = disnake.Embed(title=f"**{ctx.name} has decided to frame {targetuser.name}#{targetuser.discriminator} tonight.**", colour=disnake.Colour(0xd0021b))

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/871525831422398497/890365126866251796/FrameIcon_3.png?width=701&height=701")
                await var[r]["mafcon"].send(embed=embed)
            except asyncio.TimeoutError:
                var[r]["targets"][ctx.id] = 0
                embed = disnake.Embed(title="**You did not perform your night ability.**", colour=disnake.Colour(0xd3d3d3))

                embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
                embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar.url)
                await ctx.send(embed=embed)
                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True

                embed = disnake.Embed(title=f"**{ctx.name} did not preform their night ability.**", colour=disnake.Colour(0xd0021b))

                embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/-3Xcutx_NAdq8vfvtL1PgZiavCrfhdBfu5V3TIorcpo/%3Fv%3D1/https/cdn.discordapp.com/emojis/871863934557224960.png")
                await var[r]["mafcon"].send(embed=embed)

            
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
            embed = disnake.Embed(title="**Who do you investigate tonight?**", colour=disnake.Colour(0x7ed321), description="**Your targets are...**")

            embed.set_image(url="https://cdn.discordapp.com/attachments/878437549721419787/882427985012080681/unknown.png")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/871526928799129651.png?v=1")
            embed.set_footer(text="React with who you want to investigate.", icon_url=ctx.avatar.url)

            for key, value in var[r]["playeremoji"].items():
                if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                    continue
                else:
                    user:disnake.User = bot.get_user(value)
                    embed.add_field(name=f"{key} - {user.name}#{user.discriminator} :mag_right:", value="** **", inline=False)

            embed.add_field(name="Time :hourglass::", value="You have 30 seconds to choose.")
            b = await ctx.send(embed=embed)


            for key, value in var[r]["playeremoji"].items():
                        if (value == ctx.id or Player.get_player(value, var[r]["playerdict"]).dead == True):
                            continue
                        else:
                            await b.add_reaction(key)


            reactions = b.reactions        
            def check(reaction:Reaction, user):
                    return user.id == ctx.id and str(reaction.emoji) in var[r]["emojis"]  

            try:
                reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
                target = var[r]["playeremoji"][reaction.emoji]
                var[r]["targets"][ctx.id] = target
                targetuser = bot.get_user(target)
                embed = disnake.Embed(title=f"**You have decided to investigate {targetuser.name} tonight.**", color=0x7ed321)
                embed.set_thumbnail(url=targetuser.avatar.url)
                embed.set_footer(text="Please wait for other players to choose their action.", icon_url=ctx.avatar.url)
                Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
                await ctx.send(embed=embed)
            except asyncio.TimeoutError:
                var[r]["targets"][ctx.id] = 0
                embed = disnake.Embed(title="**You did not perform your night ability.**", colour=disnake.Colour(0xd3d3d3))

                embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/Jo6YKDv-BLtSsARJpe3YIU1BE6i6PUeref_J5iLJCLA/%3F5084118588/https/www5.lunapic.com/editor/working/162949230098060059")
                embed.set_footer(text="Accidental? Or intentional?", icon_url=ctx.avatar.url)
                await ctx.send(embed=embed)
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

        elif (role == "headhunter"):
            var[r]["targets"][ctx.id] = 0
            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
        elif (role == "psychic"):
            var[r]["targets"][ctx.id] = 0
            Player.get_player(ctx.id, var[r]["playerdict"]).ready = True
        else:
            return
    except disnake.Forbidden:
        embed = disnake.Embed(title="The bot is lacking permissions to perform an action", colour=disnake.Colour(0xea5f61), description="**Either someone disabled DMs with server members, or the bot is missing role permssions to perform an action.**")

        embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/EedL1z9T7uNxVlYBIUQzc_rvdcYeTJpDC_4fm7TQZBo/%3Fwidth%3D468%26height%3D468/https/media.discordapp.net/attachments/765738640554065962/893661449216491540/Anarchic.png")
        embed.set_footer(text="For now, ask a server admin for help.")
        
        var[r]["started"] = None
        var[r]["voted"] = None
        var[r]["timer"] = None
        var[r]["targets"] = None
        var[r]["gday"] = None
        var[r]["guiltyers"] = None
        var[r]["abstainers"] = None

        var[r]["started"] = False
        var[r]["result"] = False
        var[r]["voted"] = {}
        var[r]["gday"] = 0
        var[r]["timer"] = 0
        var[r]["ind"] = 0
        var[r]["isresults"] = False
        var[r]["diechannel"] = None
        var[r]["mafcon"] =None
        var[r]["chan"] = None
        var[r]["targets"] = {}
        var[r]["guiltyers"] = []
        var[r]["abstainers"] = []

def resetGame(guild):
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


async def protecc(member:disnake.User, guild):
    mem = Player.get_player(member.id, var[guild]["playerdict"])
    mem.doc = True
    return True

def stronger(defense:Defense, attack:Attack):
    if (defense.value > attack.value):
        return True
    else:
        return False

async def attack(me, member:disnake.User, ctx, attack:Attack):
    if (Player.get_player(me, var[ctx]["playerdict"]).role == "Mafioso" or Player.get_player(me, var[ctx]["playerdict"]).role == "Godfather" or Player.get_player(me, var[ctx]["playerdict"]).role == "Enforcer" or Player.get_player(me, var[ctx]["playerdict"]).role == "Psychopath"):
        if (stronger(Player.get_player(member.id, var[ctx]["playerdict"]).defense, attack)):
            if (Player.get_player(member.id, var[ctx]["playerdict"]).doc == True):
                embed = disnake.Embed(title="**You were attacked but someone healed you!**", colour=disnake.Colour(0x7ed321))

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/871899679766511666/Target_attacked-removebg-preview.png")
                embed.set_footer(text="Who do you think attacked you?", icon_url=member.avatar.url)
                await member.send(embed=embed)

                embed = disnake.Embed(title="**Your target was attacked last night!**", colour=disnake.Colour(0x7ed321))

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/871899679766511666/Target_attacked-removebg-preview.png")
                embed.set_footer(text="Who do you think attacked them?", icon_url=member.avatar.url)
                for i in var[ctx]["targets"].keys():
                    if (var[ctx]["targets"][i] == member.id and Player.get_player(i, var[ctx]["playerdict"]).role.lower() == "doctor"):
                        await bot.get_user(i).send(embed=embed)

                        if (Player.get_player(me, var[ctx]["playerdict"]).role == "Psychopath" and Player.get_player(me, var[ctx]["playerdict"]).cautious == False):
                            if (stronger(Player.get_player(i, var[ctx]["playerdict"]).defense, Attack.Default)):
                                k = Player.get_player(member.id, var[ctx]["playerdict"])
                                k.dead = True
                                k.death.append(DeathReason.Psychopath)
                                k.will = []
                                k.will.append("Their last will was too bloody to be read.")

                                embed = disnake.Embed(title="**You were stabbed by a **Psychopath <:psychoicon:909908333635440680>** while healing your target.", colour=disnake.Colour(0x4a90e2), description="**You have died :rip:.**")

                                embed.set_thumbnail(url="https://discord.com/assets/9f89170e2913a534d3dc182297c44c87.svg")
                                embed.set_footer(text="Rest in peace.", icon_url="https://cdn.discordapp.com/avatars/667189788620619826/f4c9e87dde54e0e2d14db69b9d60deb9.png?size=128")

                                await bot.get_user(i).send(embed=embed)

                return False
            else:
                embed = disnake.Embed(title="**Someone attacked you last night but you resisted it.**", colour=disnake.Colour(0xfff68a))

                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/878379179106787359.png?v=1")
                embed.set_footer(text="Who do you think attacked you?", icon_url=member.avatar.url)
                await member.send(embed=embed)
                
                return False
        else:
            if (Player.get_player(member.id, var[ctx]["playerdict"]).doc == True):
                embed = disnake.Embed(title="**You were attacked but someone healed you!**", colour=disnake.Colour(0x7ed321))

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/871899679766511666/Target_attacked-removebg-preview.png")
                embed.set_footer(text="Who do you think attacked you?", icon_url=member.avatar.url)
                await member.send(embed=embed)



                embed = disnake.Embed(title="**Your target was attacked last night!**", colour=disnake.Colour(0x7ed321))

                embed.set_thumbnail(url="https://media.discordapp.net/attachments/765738640554065962/871899679766511666/Target_attacked-removebg-preview.png")
                embed.set_footer(text="Who do you think attacked them?", icon_url=member.avatar.url)
                for i in var[ctx]["targets"].keys():
                    if (var[ctx]["targets"][i] == member.id and Player.get_player(i, var[ctx]["playerdict"]).role.lower() == "doctor"):
                        await bot.get_user(i).send(embed=embed)

                        if (Player.get_player(me, var[ctx]["playerdict"]).role == "Psychopath" and Player.get_player(me, var[ctx]["playerdict"]).cautious == False):
                            k = Player.get_player(member.id, var[ctx]["playerdict"])
                            k.dead = True
                            k.death.append(DeathReason.Psychopath)
                            k.will = []
                            k.will.append("Their last will was too bloody to be read.")

                            embed = disnake.Embed(title="**You were stabbed by a **Psychopath <:psychoicon:909908333635440680>** while healing your target.", colour=disnake.Colour(0x4a90e2), description="**You have died :rip:.**")

                            embed.set_thumbnail(url="https://discord.com/assets/9f89170e2913a534d3dc182297c44c87.svg")
                            embed.set_footer(text="Rest in peace.", icon_url="https://cdn.discordapp.com/avatars/667189788620619826/f4c9e87dde54e0e2d14db69b9d60deb9.png?size=128")

                            await bot.get_user(i).send(embed=embed)

                return False

            Player.get_player(member.id, var[ctx]["playerdict"]).dead = True
            return True
    else:
        print("Not working, f")
            

@bot.slash_command(
    name="daily",
    description="Claim your daily silvers"
)
async def daily(inter):
    auth = str(inter.author.id)
    try:
        guilds[auth]["claimed"]
    except:
        guilds[auth] = {"claimed" : False}
        guilds[auth]["claimed"] = False

    try:
        cur[str(inter.author.id)]
    except:
        cur[str(inter.author.id)] = 0

    embed = None

    if (guilds[auth]["claimed"] == False):
        embed = disnake.Embed(title="**Daily reward!**", color=0xddffaa, description="You have claimed your daily __**20**__ silvers <:silvers:889667891044167680>!")
        embed.set_thumbnail(url="")
        embed.set_footer(text="Come back tomorrow for more rewards!", icon_url=inter.author.avatar.url)
        guilds[auth]["claimed"] = True
        cur[str(inter.author.id)] += 20

        with open('data.json', 'w') as jsonf:
            json.dump(cur, jsonf)
    else:
        embed = disnake.Embed(title="**Failed to get your daily reward**", color=0xff5e5e, description="It appears that you have already claimed your daily.")
        embed.set_thumbnail(url="")
        embed.set_footer(text="Come back tomorrow for more rewards!", icon_url=inter.author.avatar.url)

    await inter.response.send_message(embed=embed)

async def haunt(player:disnake.Member, guild):
    play = Player.get_player(player.id, var[guild]["playerdict"])
    play.dead = True
    play.death.append(DeathReason.JesterGuilt)
    play.diedln = True

@bot.command()
async def lmao(ctx):
    await ctx.send("https://images-ext-2.discordapp.net/external/-MOtTDoNH8I7CkxXfNXYxaZc8wRyCTwejBbj6TPfKCw/%3Fwidth%3D375%26height%3D634/https/media.discordapp.net/attachments/765738640554065962/872274879309836408/unknown.png")

@bot.command()
async def ROFL(ctx):
    await ctx.send("https://cdn.discordapp.com/attachments/765738640554065962/913958133137829928/IMG_0100.png")

@bot.event
async def on_message(message:disnake.Message):
    if (message.content.startswith(">")):
        try:
            var[message.guild.id]["test"]
        except:
            try:
                var[message.guild.id] = copy.deepcopy(temp)
            except:
                pass

    await bot.process_commands(message)
            
@bot.command()
async def supergive(ctx, user:disnake.Member, amount):
    if (ctx.author.id == 839842855970275329 or ctx.author.id == 667189788620619826):
        if (str(ctx.author.id) not in cur):
            cur[str(ctx.author.id)] = 0
        if (str(user.id) not in cur):
            cur[str(user.id)] = 0

        cur[str(user.id)] += int(amount)

        embed = disnake.Embed(title=f"**Successfully supergave {user.name}#{user.discriminator} __{amount}__ silvers <:silvers:889667891044167680>!**", colour=disnake.Colour(0xffdffe), description=f"Have fun with your silvers <:silvers:889667891044167680> .")

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/889667891044167680.png?size=96")
        embed.set_footer(text="Thank you!", icon_url=ctx.author.avatar.url)
        
        await ctx.send(embed=embed)

        with open('data.json', 'w') as jsonf:
            json.dump(cur, jsonf)
    else:
        await ctx.send("sorry man your not super enough yet")



try:
    bot.run("TOKEN")
except aiohttp.client_exceptions.ClientConnectorError:
    print("Internet Error")
