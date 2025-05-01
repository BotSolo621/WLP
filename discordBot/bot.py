import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready!")
    await bot.tree.sync()
    

@bot.tree.command(name="boos", description="boos?")
async def boos(interaction: discord.Interaction):
    await interaction.response.send_message("ur boos")

@bot.tree.command(name="cows", description="list out the list of cows available.")
async def listRats(interaction: discord.Interaction):
    #grab a list of rats later
    await interaction.response.send_message("Not ready yet")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
