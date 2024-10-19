import discord
from discord import app_commands
from discord.ext import commands
import pickledb

# Initialize your databases
hasPet = pickledb.load('cogs/rock', True)
stats = pickledb.load('cogs/stats', True)
storage = pickledb.load('cogs/storage', True)

class Games(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="explore", description="Lets a companion of yours go exploring.")
    async def explore(self, interaction: discord.Interaction, companion: str):
        if not stats.exists('stats'):
            print('stats not existing')
            stats.dcreate('stats')

        authorid = str(interaction.user.id)
        user_companion = storage.dget(authorid, "companions")

        for name, boost, th1, th2 in user_companion:
            if companion.lower() == str(name).lower():
                await interaction.response.send_message(embed = discord.Embed(title="Exploration Time!", description=f"**{name}** ({interaction.user.name}'s companion) went exploring!", colour=discord.Color.green()))
                return

        await interaction.response.send_message(content=f"you don't have {companion}!", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Games(bot))
