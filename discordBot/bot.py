import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os
import socket

def connect(command):
    ip = '54.79.26.131'
    port = 4570
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((ip, port))

    server.send(command.encode())
    response = server.recv(4096).decode()
    server.close()
    return response

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

@bot.tree.command(name="getinfo", description="Get info of cow")
@app_commands.describe(text="The cow's name")
async def getInfo(interaction: discord.Interaction, text:str):
    await interaction.response.send_message("Attempting to get info...")

    info = connect(f":GETINFO\n{text}")
    
    # Send the result as a code block (for formatting)
    await interaction.followup.send(f"```{info}```")

@bot.tree.command(name="listcows", description="List all machines that have ever run cow.py")
async def listCows(interaction: discord.Interaction):
    await interaction.response.send_message("Listing all cows ever seen...")
    machines = connect(":LISTCOWS")
    await interaction.followup.send(f"```{machines}```")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
