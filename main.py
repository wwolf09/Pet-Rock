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
import pathlib

# Initialize the Discord client
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix=',', intents=intents)

hasPet = pickledb.load('rock', True)
stats = pickledb.load('stats', True)
storage = pickledb.load('storage', True)

cogs_dir = pathlib.Path(__file__).parent / "cogs"

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

async def companionMultiplier(ID):
    authorid = str(ID)
    print(authorid)
    companions_list = storage.dget(authorid, "companions")

    if companions_list:
        pass
    else:
        return
    multiplier = 1.00

    for companion, boost, th1, th2 in companions_list:
        multiplier += 0.050

    print(f"Total Multiplier: {multiplier}")
    return multiplier


async def randomCompanionCheck(id, interaction):
    authorid = str(id)
    companions_list = storage.dget(authorid, "companions")

    if companions_list:
        pass
    else:
        return
    for name, boost, th1, th2 in companions_list:
        rand = random.randrange(1, 100)
        if rand == 1:
            lvl = stats.dget(authorid, "level")
            print(th1, th2)
            defaultReward = random.randrange(th1, th2)
            calculation = await companionMultiplier(authorid)
            newReward = (defaultReward * calculation)
            current_pebbles = stats.dget(authorid, "pebbles")
            new_pebbles = round(current_pebbles + newReward)

            stats.dadd(authorid, ("pebbles", new_pebbles))
            await interaction.channel.send(embed=discord.Embed(title="Working hard, Hardly Working",
                description =f"**{name} ({interaction.author.name}'s companion)** worked really hard and got **{round(newReward)} pebbles** for you! Thank them now!!!", color = discord.Color.green()))

@client.event
async def on_ready():
    await client.tree.sync()
    print('Bot is ready.')

    if not hasPet.exists('hasPet'):
        hasPet.lcreate('hasPet')
        stats.dcreate('stats')
        storage.dcreate('storage')

    for cog_file in cogs_dir.glob("*.py"):
        if cog_file.name != "__init__.py":
            await client.load_extension(f"cogs.{cog_file.stem}")

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
    if message.author.id == 1291704309368750191:
        return
    author_id = str(message.author.id)
    author_name = str(message.author.name)
    print(author_id)
    await companionMultiplier(author_id)

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
            await message.channel.send(content=f'**{author_name} The Rock** received {round(reward)} pebbles! (multiplier included)')

@client.tree.command(name="challenge", description="challenge someone with rock paper scissors to steal their hp and xp!")
async def challenge(interaction: discord.Interaction, member: discord.Member, xp: int):
    challenger = interaction.user.name
    to_be_challenged = member.name
    await interaction.response.send_message(embed= await embed_make("Challenger Approaches!", f"{challenger} challenges {to_be_challenged} for {xp}xp!",discord.Color.red() ))

@client.tree.command(name="multiplier", description="Checks which multipliers you have")
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
        to_print += f"\n- **{name}**: {round(await toPercent(boost))}%"

    # Send the response as an embed
    await interaction.response.send_message(embed=await embed_make(
        f"{interaction.user.name}'s Multipliers",
        to_print,
        discord.Color.green()
    ))

@client.tree.command(name="add", description = "gantimpala.tameimpala")
async def add(interaction: discord.Interaction, member: discord.Member, pebble: int):
    if interaction.user.id == 718445888821002271:
        pass
    else:
        return

    user_id = member.id
    user_name = member.name

    current = stats.dget(str(user_id), "pebbles")
    new_money = pebble
    stats.dadd(str(user_id), ("pebbles", new_money))

@client.tree.command(name="daily", description="daily rewards to be claimed")
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
            await interaction.response.send_message(embed= await embed_make("Daily Claimed!",f'You now have **{round(new_money)}** pebbles!', discord.Color.green()))
        else:
            await interaction.response.send_message(embed = await embed_make("Daily already claimed!", f'Please wait for your next claim!', discord.Color.red()))

class black_red(enum.Enum):
    black = "black"
    red = "red"

@client.tree.command(name="roulette", description = "let's go gambling!")
async def roulette(interaction: discord.Interaction, choice: black_red, bet: int):
    gamble = ["black", "red"]
    rand = random.choice(gamble)
    print(choice)
    print(rand)

    User_Money = stats.dget(str(interaction.user.id), "pebbles")
    if bet > int(User_Money * 0.15) or bet == 0:
        pass
    else:
        await interaction.response.send_message(content = "Can't gamble **less than 15%** of your pebbles", ephemeral = True)
        return

    if 0 > bet:
        await interaction.response.send_message(content= "really?", ephemeral = True)
        return

    if User_Money > bet or User_Money == bet:
        if rand == "red" and choice == black_red.red or rand == "black" and choice == black_red.black:
            current_money = stats.dget(str(interaction.user.id), "pebbles")
            new_money = current_money + (await multiplierCalculator(str(interaction.user.id), (bet*2)))
            stats.dadd(str(interaction.user.id), ("pebbles", new_money))
            await interaction.response.send_message(embed=await embed_make(f"Let's go gambling!", f'Received **{(await multiplierCalculator(str(interaction.user.id), (bet*2)))} pebbles!**', discord.Color.green()))
            print("gambling succeed")
        else:
            current_money = stats.dget(str(interaction.user.id), "pebbles")
            new_money = current_money - bet
            stats.dadd(str(interaction.user.id), ("pebbles", (new_money)))
            print("gambling failed")
            await interaction.response.send_message(embed=await embed_make(f'Aw dang it!', f'Gambling failed. You lost **{bet} pebbles.**',discord.Color.red()))
    else:
        await interaction.response.send_message(embed=await embed_make(f'Not enough pebbles!', f'You need more pebbles to gamble!', discord.Color.red()))


shop_items = {
    "multipliers": [
        {"name": "Quartz", "price": 3000, "description": "Increase pebble gain by 10%", "boost": 1.1},
        {"name": "Manganese", "price": 10000, "description": "Increase pebble gain by 10%", "boost": 1.1},
        {"name": "Iron", "price": 25000, "description": "Increase pebble gain by 25%", "boost": 1.25},
        {"name": "Diamond", "price": 50000, "description": "Increase pebble gain by 50%", "boost": 1.5},
        {"name": "Amethyst", "price": 100000, "description": "Increase pebble gain by 75%", "boost": 1.75}
    ],

    "companions": [
        {"name": "Bato", "price": 10000, "description": "Please do not let this guy run senate.", "boost": 1.1, "threshold1": 250, "threshold2": 500},
        {"name": "The Rock", "price": 50000, "description": "I think this guy knows Kevin Hart!", "boost": 1.1, "threshold1": 300, "threshold2": 600},
        {"name": "Rocky Road", "price": 200000, "description": "Ice cream or the road? Who knows?", "boost": 1.2, "threshold1": 500, "threshold2": 1000},
        {"name": "Rocky Balboa", "price": 1000000, "description": "I'm in good terms with this guy!", "boost": 1.5, "threshold1": 5000, "threshold2": 7500},
        {"name": "Kuwumi", "price": 50000000, "description": "this name sounds familiar.", "boost": 1.7, "threshold1": 100000, "threshold2": 150000}
    ],

    "cosmetics": [
        {"name": "Tophat", "price": 1000, "description": "I look very classy!"},
        {"name": "Uranium Necklace", "price": 1000000000, "description": "Does this explode?"}
    ]
}

@client.tree.command(name="shop", description="Can I buy this?")
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


@client.tree.command(name="buy", description="Let's go buying!")
async def buy(interaction: discord.Interaction, item: str):
    authorid = str(interaction.user.id)

    # Loop through the shop items to find a match
    for category, items in shop_items.items():
        for inItem in items:
            if item.lower() == inItem["name"].lower():
                # Retrieve or initialize the current items as a list
                current_items = storage.dget(authorid, category) or []

                # Ensure the retrieved data is a list
                if not isinstance(current_items, list):
                    current_items = list(current_items)

                # Check if the user has enough money
                if not await checkEnoughMoney(authorid, inItem["price"]):
                    await interaction.response.send_message("You don't have enough pebbles!", ephemeral=True)
                    return

                # Handle the "multipliers" category
                if category == "multipliers":
                    if any(existing_item[0] == inItem["name"] for existing_item in current_items):
                        await interaction.response.send_message(f"You already own the multiplier **{inItem['name']}**!",
                                                                ephemeral=True)
                        return
                    current_items.append((inItem["name"], inItem["boost"]))

                # Handle the "companions" or "cosmetics" category
                elif category == "companions":
                    if any(existing_item[0] == inItem["name"] for existing_item in current_items):
                        await interaction.response.send_message(f"You already own the companion **{inItem['name']}**!", ephemeral=True)
                        return
                    current_items.append((inItem["name"], inItem.get("boost"), inItem["threshold1"], inItem["threshold2"]))

                # Handle invalid categories
                else:
                    await interaction.response.send_message("This item does not exist.", ephemeral=True)
                    return

                # Update the user's inventory
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


@client.tree.command(name="inventory", description="These are priceless!")
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
        # Ensure lists are converted to tuples
        if isinstance(item, list):
            item = tuple(item)

        if isinstance(item, tuple):
            calculated = math.floor(await toPercent(item[1]))
            return f"- {item[0]} (Multiplier: {calculated}%)"
        return f"- {item}"

    # Iterate through user categories and items
    for category, items in user_data.items():
        inventory_message += f"**{category.capitalize()}**\n"
        # Convert any list to a tuple during formatting
        formatted_items = await asyncio.gather(*(format_item(item) for item in items))
        inventory_message += "\n".join(formatted_items) + "\n\n"

    await interaction.channel.send(embed=await embed_make(
        f"{interaction.user.name}'s Inventory",
        inventory_message,
        discord.Color.green()
    ))


@client.tree.command(name="rock-status", description="take a look at the status of your pet rock!")
async def rock_status(interaction: discord.Interaction):
    list_users = hasPet.lgetall('hasPet')
    print(list_users)
    if interaction.user.id in list_users:
        # Send Status
        await interaction.response.send_message(embed= await returnstatus(interaction.user.id))
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