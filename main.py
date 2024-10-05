from math import trunc
import time
import discord
from Cryptodome.SelfTest.Hash.test_cSHAKE import descr
from discord import app_commands
from discord.ext import commands
import random
import dctoken
from datetime import datetime
import pytz
import pickledb
import asyncio

# Initialize the Discord client
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(command_prefix=',', intents=intents)
tree = app_commands.CommandTree(client)
hasPet = pickledb.load('rock', True)
stats = pickledb.load('stats', True)

async def embed_make(title, description, color):
    return_this = discord.Embed(description=description, colour= color, title=title)
    return return_this

@client.event
async def on_ready():
    await tree.sync()
    print('Bot is ready.')

    if not hasPet.exists('hasPet'):
        hasPet.lcreate('hasPet')
        stats.dcreate('stats')

async def returnstatus(id):
    name = await client.fetch_user(id)
    return_this = discord.Embed(description= await returnStats(id),colour=discord.Color.blue(), title=((f'{name} The Rock')))
    return_this.set_image(url="https://media.discordapp.net/attachments/769117147653210133/1291718080212369499/rock-vector-icon-on-white-background-rock-emoji-illustration-isolated-rock-stone-vector.png?ex=67011db5&is=66ffcc35&hm=c3ca212cb8b489556d258b4ea176325a7c9efef5e6932e0e1b57f71e511e5d87&=&format=webp&quality=lossless")
    return return_this

async def returnStats(ID):
    print(str(ID))
    rock_level = stats.dget(str(ID), "level")
    rock_hp = stats.dget(str(ID), "hp")
    print(stats.dexists(str(ID), "XP"))
    rock_xp = stats.dget(str(ID), "XP")

    return_this_nerd_lmao = f'**Level**: {rock_level} \n**HP**: {rock_hp} \nXP:{rock_xp}'
    return return_this_nerd_lmao

@client.event
async def on_message(message: discord.Message):
    author_id = str(message.author.id)
    author_name = str(message.author.name)
    print(author_id)

    if message.author.id in hasPet.lgetall('hasPet'):
        current_xp = stats.dget(str(author_id), "XP")
        current_level = stats.dget(str(author_id), "level")
        required_next_xp = 100 * (current_level/2)

        newxp = current_xp + 3
        print(newxp)
        stats.dadd(author_id, ("XP", newxp))
        print(stats.dget(str(author_id),"XP"))

        if newxp >= required_next_xp:
            stats.dadd(author_id, ("level", (current_level + 1)))
            new_level = stats.dget(str(author_id), "level")
            await message.channel.send(content=f'**{author_name} The Rock** has leveled up to lvl {new_level}!')

@tree.command(name="challenge", description="challenge someone with rock paper scissors to steal their hp and xp!")
async def challenge(interaction: discord.Interaction, member: discord.Member, xp: int):
    challenger = interaction.user.name
    to_be_challenged = member.name
    await interaction.channel.send(embed= await embed_make("Challenger Approaches!", f"{challenger} challenges {to_be_challenged} for {xp}xp!",discord.Color.red() ))

@tree.command(name="daily", description="daily rewards to be claimed")
async def daily(interaction: discord.Interaction):
    author_id = interaction.user.id
    current_time = int(time.time())

    if hasPet.exists(author_id):
        last_claim = stats.dget(author_id, 'last_daily_claim')


@tree.command(name="rock-status", description="take a look at the status of your pet rock!")
async def rock_status(interaction: discord.Interaction):
    list_users = hasPet.lgetall('hasPet')
    print(list_users)
    if interaction.user.id in list_users:
        # Send Status
        await interaction.channel.send(embed= await returnstatus(interaction.user.id))
        print(stats.dget(str(interaction.user.id), "level"))
        print(stats.dget(str(interaction.user.id), "hp"))
        print(stats.dget(str(interaction.user.id), "XP"))
    else:
        hasPet.ladd('hasPet', interaction.user.id)
        stats.dcreate(str(interaction.user.id))
        stats.dadd(str(interaction.user.id), ("last_daily_claim", 0))
        stats.dadd(str(interaction.user.id), ("level", 1))
        stats.dadd(str(interaction.user.id), ("hp", 100))
        stats.dadd(str(interaction.user.id), ("XP", 1))
        print(stats.dget(str(interaction.user.id), "level"))
        print(stats.dget(str(interaction.user.id), "hp"))
        print(stats.dget(str(interaction.user.id), "XP"))
























client.run(dctoken.dc_token)