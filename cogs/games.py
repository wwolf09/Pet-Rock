from math import trunc
import time
import discord
from Cryptodome.SelfTest.Hash.test_cSHAKE import descr
from discord import app_commands
from discord.ext import commands
import random
from datetime import datetime
import pytz
import pickledb
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(command_prefix=',', intents=intents)
tree = app_commands.CommandTree(client)
hasPet = pickledb.load('rock', True)
stats = pickledb.load('stats', True)

