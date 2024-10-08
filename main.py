import enum
from math import trunc
import math
import time
import discord
from Cryptodome.SelfTest.Hash.test_cSHAKE import descr
from Cryptodome.Util.number import ceil_div
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

async def multiplierCalculator(ID, reward):
    userMultiplier = stats.dget(str(ID), "multiplier")

    finalreward = round(reward)

    for num in userMultiplier:
        finalreward *= num

    return finalreward

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
    pebbles = stats.dget(str(ID), "pebbles")
    multiplier = stats.dget(str(ID), "multiplier")

    total_multi = math.prod(multiplier)

    return_this_nerd_lmao = f'**Level**: {rock_level} \n**HP**: {rock_hp} \n**XP**:{rock_xp} \n**Pebbles**:{pebbles} \n**Total Multiplier:**{total_multi}'
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

        newxp = current_xp + await multiplierCalculator(author_id, 3)
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

    if author_id in hasPet.lgetall('hasPet'):
        last_claim = int(stats.dget(str(author_id), 'last_daily_claim'))
        money = stats.dget(str(author_id), 'pebbles')
        print(current_time)
        print(last_claim)
        if current_time - last_claim >= 86400:
            print("true")
            new_money = money + 100 * (stats.dget(str(author_id), "level") / 2)
            stats.dadd(str(interaction.user.id), ("pebbles", new_money))
            print("sent")
            stats.dadd(str(interaction.user.id), ("last_daily_claim", current_time))

            await interaction.channel.send(embed= await embed_make("Daily Claimed!",f'You have gained your **{new_money}** pebbles!', discord.Color.green()))
        else:
            await interaction.channel.send(embed = await embed_make("Daily already claimed!", f'Please wait for your next claim!', discord.Color.red()))

class black_red(enum.Enum):
    black = "black"
    red = "red"

@tree.command(name="roulette", description = "let's go gambling!")
async def roulette(interaction: discord.Interaction, choice: black_red, bet: int):
    gamble = ["black", "red"]
    rand = random.choice(gamble)
    print(choice)
    print(rand)

    User_Money = stats.dget(str(interaction.user.id), "pebbles")

    if User_Money > bet or User_Money == bet:
        if rand == "red" and choice == black_red.red or rand == "black" and choice == black_red.black:
            current_money = stats.dget(str(interaction.user.id), "pebbles")
            new_money = current_money + (await multiplierCalculator(str(interaction.user.id), (bet*2)))
            stats.dadd(str(interaction.user.id), ("pebbles", new_money))
            await interaction.channel.send(embed=await embed_make(f"Let's go gambling!", f'Received **{(await multiplierCalculator(str(interaction.user.id), (bet*2)))} pebbles!**', discord.Color.green()))
            print("gambling succeed")
        else:
            current_money = stats.dget(str(interaction.user.id), "pebbles")
            new_money = current_money - bet
            stats.dadd(str(interaction.user.id), ("pebbles", (new_money)))
            print("gambling failed")
            await interaction.channel.send(embed=await embed_make(f'Aw dang it!', f'Gambling failed. You lost **{bet} pebbles.**',discord.Color.red()))
    else:
        await interaction.channel.send(embed=await embed_make(f'Not enough pebbles!', f'You need more pebbles to gamble!', discord.Color.red()))

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
        stats.dadd(str(interaction.user.id), ("pebbles", 0))
        stats.dadd(str(interaction.user.id), ("multiplier", [1.5,1.5,1.5,1.5,1.5]))
        print(stats.dget(str(interaction.user.id), "level"))
        print(stats.dget(str(interaction.user.id), "hp"))
        print(stats.dget(str(interaction.user.id), "XP"))
























client.run(dctoken.dc_token)