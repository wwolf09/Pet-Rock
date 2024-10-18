import discord
from discord import app_commands
from discord.ext import commands
import math
import asyncio
import pickledb
import random
import enum

class games(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.stats = stats

    class black_red(enum.Enum):
        black = "black"
        red = "red"

    @commands.command(name="roulette", description = "let's go gambling!")
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



async def setup(bot):
    await bot.add_cog(games(bot))