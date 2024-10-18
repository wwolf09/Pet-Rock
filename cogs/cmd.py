import discord
from discord import app_commands
from discord.ext import commands
import math
import asyncio

sentences = [
    "The body piercing didn't go exactly as he expected.",
    "Lets all be unique together until we realise we are all the same.",
    "Kevin embraced his ability to be at the wrong place at the wrong time.",
    "In the end, he realized he could see sound and hear words.",
    "Situps are a terrible way to end your day.",
    "The bird had a belief that it was really a groundhog.",
    "She borrowed the book from him many years ago and hasn't yet returned it.",
    "I liked their first two albums but changed my mind after that charity gig.",
    "We should play with legos at camp.",
    "Tomatoes make great weapons when water balloons aren’t available."
]

class RandomMoment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(RandomMoment(bot))