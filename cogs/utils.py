import discord
from discord import app_commands
from discord.ext import commands
import math
import asyncio
import pickledb

class utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(utility(bot))