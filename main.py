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
storage = pickledb.load('storage', True)

async def embed_make(title, description, color):
    return_this = discord.Embed(description=description, colour= color, title=title)
    return return_this

async def multiplierCalculator(ID, reward):
    userMultiplier = storage.dget(str(ID), "multipliers")
    multiplier_values = [item[1] for item in userMultiplier if isinstance(item, tuple)]

    finalreward = round(reward)

    for num in multiplier_values:
        finalreward *= num

    return finalreward

async def toPercent(multiplier):
    return (multiplier - 1) * 100


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

    return_this_nerd_lmao = (f'**Level**: {rock_level} \n**HP**: {rock_hp} \n**XP**:{rock_xp} \n**Pebbles**:{pebbles} '
                             f'\n**Total Multiplier:**{total_multi}')
    return return_this_nerd_lmao

@client.event
async def on_message(message: discord.Message):
    author_id = str(message.author.id)
    author_name = str(message.author.name)
    print(author_id)

    if message.author.id in hasPet.lgetall('hasPet'):
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
        {"name": "Quartz", "price": 3000, "description": "Increase pebble gain by 10%", "boost": 1.1}
    ],

    "companions": [
        {"name": "Bato", "price": 1000, "description": "Gives you idk"},
        {"name": "The Rock", "price": 5000, "description": "I think this guy knows Kevin Hart!"},
        {"name": "Rocky Road", "price": 20000, "description": "Ice cream or the road? Who knows?"},
        {"name": "Rocky Balboa", "price": 100000, "description": "I'm in good terms with this guy!"}
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

    # Loop through categories and create individual embeds
    for category, items in shop_items.items():
        embed_color = category_colors.get(category.lower(), discord.Color.green())  # Default to green if not found

        embed = discord.Embed(
            title=f"{category.capitalize()} - Miner David's Shop",
            description="Take a look inside!",
            color=embed_color
        )

        # Add items to the embed
        for item in items:
            embed.add_field(
                name=f"**{item['name']}** - {item['price']} pebbles",
                value=f"*{item['description']}*",
                inline=False
            )

        # Send each category embed individually
        await interaction.channel.send(embed=embed)


@tree.command(name="buy", description="Let's go buying!")
async def buy(interaction: discord.Interaction, item: str):
    authorid = str(interaction.user.id)

    # Loop through the shop items to find a match
    for category, items in shop_items.items():
        for inItem in items:
            if item.lower() == inItem["name"].lower():
                # Retrieve current items for the category from storage, or initialize an empty list
                current_items = storage.dget(authorid, category) or []

                # Handle multipliers category
                if category == "multipliers":
                    # Check if the user already owns the multiplier
                    if any(existing_item[0] == inItem["name"] for existing_item in current_items):
                        await interaction.response.send_message(f"You already own the multiplier **{inItem['name']}**!", ephemeral=True)
                        return
                    else:
                        current_items.append((inItem["name"], inItem["boost"]))


                # Handle companions category
                elif category == "companions":
                    if inItem["name"] in current_items:
                        await interaction.response.send_message(f"You already own the companion **{inItem['name']}**!", ephemeral=True)
                        return
                    else:
                        current_items.append(inItem["name"])

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
        stats.dadd(str(interaction.user.id), ("XP", 1))
        stats.dadd(str(interaction.user.id), ("pebbles", 0))
        stats.dadd(str(interaction.user.id), ("multiplier", [1.5,1.5,1.5,1.5,1.5]))
        storage.dadd(str(interaction.user.id), ("multipliers", {}))
        storage.dadd(str(interaction.user.id), ("utilities", []))
        storage.dadd(str(interaction.user.id), ("companions", []))
        print(stats.dget(str(interaction.user.id), "level"))
        print(stats.dget(str(interaction.user.id), "hp"))
        print(stats.dget(str(interaction.user.id), "XP"))
























client.run(dctoken.dc_token)