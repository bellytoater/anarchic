# Anarchic :fire:
A feature rich Discord bot including party, economy, and voting features with 13 different [roles](#roles) you can play as!

### Invite the bot [here](https://discord.com/api/oauth2/authorize?client_id=887118309827432478&permissions=105696980048&scope=bot%20applications.commands)
<p align="center" width="100%">
  <a href="https://discord.gg/ApvrUsXFxk"><img src="./images/jointhediscord.png"></a>
</p>


# Changelog :memo:
**Version 1.1.0** :ghost:
- Two new roles: The [Psychic](#psychic) and The [Consigliere](#consigliere)
- New shop in town! Check out [Anarith](#anarith) selling the newest items, [Shards](#shards)!
- Two new setups: __**Truth**__ and __**Scattered**__
- Removed __**Circus**__ from the available setups
- Added economy system
- New role embeds
- New `/help` command
- Fixed bug where bot awkwardly crashes when a player is lynched
- Fixed bug where players could see dead chat
- Fixed bug where Mafioso was town sided

<details>
  <summary>Click to view older changelogs</summary>
  
**Version 1.0.1** :camera:
- Targeting bug fix
- New Doctor image
- New Doctor targeting image
- New Jester image
- Game results will now be shown in the channel `/start` was used

**Version 1.0.0** :computer:
- Added the following roles: Cop, Detective, Lookout, Doctor, Enforcer, Mayor, Headhunter, Jester, Mafioso, Consort, Framer
- Created party system (Wills, Voting, Joining, Leaving, Starting, Changing the setup, The actual game)
- Added help commands (Role info, List of all roles, List of all setups)

</details>

# Roles :performing_arts:
## Town :house:
The faction of *most* of the players in the game. To win, get rid of all the roles that may harm the **Town**.

### Cop :mag_right:
**Faction: Town**

A reliable law enforcer, skilled in keeping evildoers in check.
- You can interrogate a player each night
- You will learn if they are **Suspicious** or not


### Detective :detective:
**Faction: Town**

A private investigator who uncovers one's secrets

- You can investigate a player each night
- You will learn what possible roles your target might be


### Lookout 🔭
**Faction: Town**

A skilled observer who keeps an eye on the evils

- You can watch over a player each night
- You will learn who visits your target


### Doctor 🧑‍⚕️
**Faction: Town**

A secret surgeon who heals people at night


- Heal a player each night
- You will grant your target a **powerful** defense.
- You and your target will be notified of a successful heal
- You may only heal yourself once


### Enforcer 🔫
**Faction: Town**

A rogue vigilante with an eye out for justice.

- You may choose to shoot a player
- You may not shoot on the first night
- If you kill a Town member, you will commit suicide and be dealt a **piercing** attack


### Mayor 🎩
**Faction: Town**

The leader of the town.

- You may reveal yourself as **Mayor** to the rest of the town
- You will have 3 votes on all voting procedures once you reveal


## Mafia :wilted_flower:
The opposing faction of the **Town** :house:. You must kill everyone who rivals the **Mafia** :wilted_flower:.

### Mafioso :wilted_flower:
**Faction: Mafia**

The right hand man of organized crime.

- You can attack a player each night
- If you die, a random Mafia member will be promoted to the new Mafioso 🥀.

### Framer :framed_picture:
**Faction: Mafia**

A skilled deceiver who sets investigations astray.

- You can frame a player each night
- Frames last until an investigation is preformed on your target
- Framed players show as **Suspicious** to a **Cop**
- Framed players show as **Framer**, **Jester** or **Mayor** to a **Detective**.

### Consigliere :magnet:
**Faction: Mafia**

A corrupted detective who gathers information for the mafia.

- Investigate a player each night
- You will learn your target's exact role

### Consort :revolving_hearts:
**Faction: Mafia**

A hooker who works for organized crime

- Distract a player each night
- You are immune to **distractions**

## Neutral 🪓
The neutrals. They are their own faction, and they have their own win condition.

### Jester :clown_face:
**Faction: Neutral**

A crazed lunatic who wants to be publicly executed

**Your goal: Get yourself lynched :axe:**

When you are lynched:
- You will **distract** all of your guilty or abstaining voter the night following your lynch
- You will **passively** attack a guilty or abstaining voter the night following your lynch.

### Headhunter :axe:

An obsessed executioner who wants a certain someone killed in front of the town.

**You will be assigned a player that is a member of the Town :house:. Your goal is to get them lynched, not kill them.**

- If your target is killed at night, you will become a **Jester** :clown_face:

# FAQ
Q: Are there questions here?

A: No.

# Building
To build the bot and use it for yourself, you need to have the dependencies from `requirements.txt` installed (located in the source folder). If you're too lazy to go look for it, here's the list of libraries:

- aiofiles
- aiohttp
- asyncio
- disnake
- humanize
- requests
- topggpy

Copy the example config file in the source folder and rename it to `config.py`, change the desired settings, and you're good to go!

❗ **NOTE: Even though this project is open-source, you are not allowed to go around and claim it is yours.**
