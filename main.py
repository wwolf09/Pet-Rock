import enum
from math import trunc
import math
import time
from operator import truediv

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
storage = pickledb.load('storage', True)

async def checkEnoughMoney(id, itemCost):
    user_money = stats.dget(str(id), "pebbles")

    if user_money >= itemCost:
        new_money = (user_money - itemCost)
        stats.dadd(str(id), ("pebbles", new_money))
        return True
    else:
        return False

async def embed_make(title, description, color):
    return_this = discord.Embed(description=description, colour= color, title=title)
    return return_this

async def multiplierCalculator(ID, reward):
    userMultiplier = storage.dget(str(ID), "multipliers")
    print(f'{userMultiplier} : brother')
    # List comprehension with filtering
    boost = []
    for item in userMultiplier:
        boost.append(item[1])
    ##initialize stuff lol
    finalreward = reward
    ## multiply values
    for num in boost:
        finalreward *= num

    return finalreward

async def toPercent(multiplier):
    return  (multiplier - 1) * 100

async def randomCompanionCheck(id, interaction):
    authorid = str(id)
    rand = random.randrange(1, 15)
    companions_list = storage.dget(authorid, "companions")

    if companions_list:
        pass
    else:
        return
    for name, boost in companions_list:
        if rand == 1:
            lvl = stats.dget(authorid, "lvl")
            lvl_formula = (lvl/5) * 1000
            calculation = await multiplierCalculator(authorid, lvl_formula)
            current_pebbles = stats.dget(authorid, "pebbles")
            new_pebbles = current_pebbles + calculation

            stats.dadd(authorid, ("pebbles", new_pebbles))
            await interaction.channel.send(embed=discord.Embed(title="Working hard, Hardly Working",
                description =f"**{name}** worked really hard and got **{calculation}** for you! Thank them now!!!"))

@client.event
async def on_ready():
    await tree.sync()
    print('Bot is ready.')

    if not hasPet.exists('hasPet'):
        hasPet.lcreate('hasPet')
        stats.dcreate('stats')
        storage.dcreate('storage')

async def returnstatus(id):
    name = await client.fetch_user(id)
    return_this = discord.Embed(description= await returnStats(id),colour=discord.Color.blue(),title=((f'{name} The Rock')))
    return_this.set_image(url="https://media.discordapp.net/attachments/769117147653210133/1291718080212369499/rock-vector-icon-on-white-background-rock-emoji-illustration-isolated-rock-stone-vector.png?ex=67011db5&is=66ffcc35&hm=c3ca212cb8b489556d258b4ea176325a7c9efef5e6932e0e1b57f71e511e5d87&=&format=webp&quality=lossless")
    return return_this

async def returnStats(ID):
    print(str(ID))
    rock_level = stats.dget(str(ID), "level")
    rock_hp = stats.dget(str(ID), "hp")
    print(stats.dexists(str(ID), "XP"))
    rock_xp = stats.dget(str(ID), "XP")
    pebbles = stats.dget(str(ID), "pebbles")

    return_this_nerd_lmao = (f'**Level**: {rock_level} \n**HP**: {rock_hp} \n**XP**:{round(rock_xp)} \n**Pebbles**:{round(pebbles)}')
    return return_this_nerd_lmao

@client.event
async def on_message(message: discord.Message):
    author_id = str(message.author.id)
    author_name = str(message.author.name)
    print(author_id)

    if message.author.id in hasPet.lgetall('hasPet'):
        await randomCompanionCheck(author_id, message)
        current_xp = stats.dget(str(author_id), "XP")
        current_level = stats.dget(str(author_id), "level")
        current_pebbles = stats.dget(author_id, "pebbles")
        required_next_xp = 100 * (current_level/2)

        newxp = current_xp + await multiplierCalculator(author_id, 3)
        print(newxp)
        stats.dadd(author_id, ("XP", newxp))
        print(stats.dget(str(author_id),"XP"))

        if newxp >= required_next_xp:
            reward_pebbles = 1000 * (current_level/2)
            reward = await multiplierCalculator(author_id, reward_pebbles)
            stats.dadd(author_id, ("level", (current_level + 1)))
            stats.dadd(author_id, ("pebbles", (current_pebbles + reward)))
            new_level = stats.dget(str(author_id), "level")

            await message.channel.send(content=f'**{author_name} The Rock** has leveled up to lvl {new_level}!')
            await message.channel.send(content=f'**{author_name} The Rock** received {reward} pebbles! (multiplier included)')

@tree.command(name="challenge", description="challenge someone with rock paper scissors to steal their hp and xp!")
async def challenge(interaction: discord.Interaction, member: discord.Member, xp: int):
    challenger = interaction.user.name
    to_be_challenged = member.name
    await interaction.channel.send(embed= await embed_make("Challenger Approaches!", f"{challenger} challenges {to_be_challenged} for {xp}xp!",discord.Color.red() ))

@tree.command(name="multiplier", description="Checks which multipliers you have")
async def checkmultiplier(interaction: discord.Interaction):
    ID = str(interaction.user.id)

    # Safely retrieve multipliers or set to an empty list if not found
    userMultiplier = storage.dget(ID, "multipliers")

    multiplier_values = []

    for item in userMultiplier:
        multiplier_values.append(item[1])

    # Handle the case where no multipliers exist
    if not multiplier_values:
        await interaction.response.send_message(
            f"{interaction.user.name}, you don't have any multipliers yet.",
            ephemeral=True
        )
        return

    # Format the multiplier list for display
    to_print = ""
    for name, boost in userMultiplier:
        to_print += f"- **{name}**: {round(await toPercent(boost))}%"

    # Send the response as an embed
    await interaction.response.send_message(embed=await embed_make(
        f"{interaction.user.name}'s Multipliers",
        to_print,
        discord.Color.green()
    ))

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
            new_money = money + 100 * (stats.dget(str(author_id), "level") / 1.1)
            stats.dadd(str(interaction.user.id), ("pebbles", new_money))
            print("sent")
            stats.dadd(str(interaction.user.id), ("last_daily_claim", current_time))
            await interaction.channel.send(embed= await embed_make("Daily Claimed!",f'You now have **{round(new_money)}** pebbles!', discord.Color.green()))
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


shop_items = {
    "multipliers": [
        {"name": "Quartz", "price": 3000, "description": "Increase pebble gain by 10%", "boost": 1.1},
        {"name": "Manganese", "price": 10000, "description": "Increase pebble gain by 10%", "boost": 1.1},
        {"name": "Iron", "price": 25000, "description": "Increase pebble gain by 25%", "boost": 1.25},
        {"name": "Diamond", "price": 50000, "description": "Increase pebble gain by 50%", "boost": 1.5},
        {"name": "Amethyst", "price": 100000, "description": "Increase pebble gain by 75%", "boost": 1.75}
    ],

    "companions": [
        {"name": "Bato", "price": 1000, "description": "Gives you idk", "boost": 1.1},
        {"name": "The Rock", "price": 5000, "description": "I think this guy knows Kevin Hart!", "boost": 1.1},
        {"name": "Rocky Road", "price": 20000, "description": "Ice cream or the road? Who knows?", "boost": 1.2},
        {"name": "Rocky Balboa", "price": 100000, "description": "I'm in good terms with this guy!", "boost": 1.5}
    ],

    "cosmetics": [
        {"name": "Tophat", "price": 1000, "description": "I look very classy!"}
    ]
}

@tree.command(name="shop", description="Can I buy this?")
async def view(interaction: discord.Interaction):
    # Define colors for each category
    category_colors = {
        "multipliers": discord.Color.blue(),
        "companions": discord.Color.purple(),
        "cosmetics": discord.Color.gold(),
    }

    embeds = []  # Collect all embeds here

    # Loop through categories and create individual embeds
    for category, items in shop_items.items():
        embed_color = category_colors.get(category.lower(), discord.Color.green())  # Default to green if not found

        embed = discord.Embed(
            title=f"{category.capitalize()}",
            color=embed_color
        )

        # Add items with prettified prices to the embed
        for item in items:
            price = f"🪨 {item['price']:,.0f} pebbles"  # Adds emoji and comma separators
            embed.add_field(
                name=f"**{item['name']}** \n— {price}",
                value=f"*{item['description']}*",
                inline=True
            )

        embeds.append(embed)  # Add embed to the list

    # Send all embeds in one message
    await interaction.response.send_message(embeds=embeds)


@tree.command(name="buy", description="Let's go buying!")
async def buy(interaction: discord.Interaction, item: str):
    authorid = str(interaction.user.id)

    # Loop through the shop items to find a match
    for category, items in shop_items.items():
        for inItem in items:
            if item.lower() == inItem["name"].lower():
                # Retrieve current items for the category from storage, or initialize an empty list
                current_items = storage.dget(authorid, category) or []
                if await checkEnoughMoney(authorid, inItem["price"]):
                    pass
                else:
                    await interaction.response.send_message(f"You don't have enough pebbles!", ephemeral=True)
                    return

                # Handle multipliers category
                if category == "multipliers":
                    # Check if the user already owns the multiplier
                    if any(existing_item[0] == inItem["name"] for existing_item in current_items):
                        await interaction.response.send_message(f"You already own the multiplier **{inItem['name']}**!", ephemeral=True)
                        return
                    else:
                        current_items.append((inItem["name"], inItem["boost"]))

                # Handle companions category
                elif category == "companions" or category == "cosmetics":
                    if inItem["name"] in current_items:
                        await interaction.response.send_message(f"You already own the companion **{inItem['name']}**!", ephemeral=True)
                        return
                    else:
                        current_items.append((inItem["name"], inItem["boost"]))
                else:
                    # Invalid category, return error
                    await interaction.response.send_message("This item does not exist.", ephemeral=True)
                    return

                # Update the user's inventory in storage
                storage.dadd(authorid, (category, current_items))

                # Send confirmation message
                await interaction.response.send_message(embed=await embed_make(
                    f"{interaction.user.name} bought {inItem['name']}",
                    f"*{inItem['description']}*",
                    discord.Color.green()
                ))
                return

    # If no item matches, send an error message
    await interaction.response.send_message(f"Item '{item}' not found in the shop.", ephemeral=True)


@tree.command(name="inventory", description="These are priceless!")
async def inv(interaction: discord.Interaction):
    authorid = str(interaction.user.id)

    # Check if the user has any items in storage
    if not storage.exists(authorid):
        await interaction.channel.send("You don't have any items yet!")
        return

    user_data = storage.get(authorid)  # Retrieve user data
    inventory_message = ""

    # Helper async function to format item entries
    async def format_item(item):
        if isinstance(item, tuple):
            calculated = math.floor(await toPercent(item[1]))
            return f"- {item[0]} (Multiplier: {calculated}%)"
        return f"- {item}"

    # Iterate through user categories and items
    for category, items in user_data.items():
        inventory_message += f"**{category.capitalize()}**\n"
        formatted_items = await asyncio.gather(*(format_item(item) for item in items))  # Use asyncio.gather for concurrency
        inventory_message += "\n".join(formatted_items) + "\n\n"

    await interaction.channel.send(embed=await embed_make(
        f"{interaction.user.name}'s Inventory",
        inventory_message,
        discord.Color.green()
    ))

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
        storage.dcreate(str(interaction.user.id))
        stats.dadd(str(interaction.user.id), ("last_daily_claim", 0))
        stats.dadd(str(interaction.user.id), ("level", 1))
        stats.dadd(str(interaction.user.id), ("hp", 100))
        stats.dadd(str(interaction.user.id), ("XP", 0))
        stats.dadd(str(interaction.user.id), ("pebbles", 0))
        storage.dadd(str(interaction.user.id), ("multipliers", {}))
        storage.dadd(str(interaction.user.id), ("cosmetics", []))
        storage.dadd(str(interaction.user.id), ("companions", []))
        print(stats.dget(str(interaction.user.id), "level"))
        print(stats.dget(str(interaction.user.id), "hp"))
        print(stats.dget(str(interaction.user.id), "XP"))
























client.run(dctoken.dc_token)