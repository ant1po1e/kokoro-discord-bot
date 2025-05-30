import discord
from discord.ext import commands
from discord import app_commands
import logging
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))  # Add GUILD_ID in .env for faster testing

# Logging
logging.basicConfig(level=logging.INFO)

# Setup intents and bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Sync to a specific guild for faster command registration during development
        await self.tree.sync(guild=discord.Object(id=GUILD_ID))

client = MyClient()

@client.tree.command(name="calculate", description="Calculate BPM based on snap", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    bpm="Base BPM",
    desired_snap="Desired snap value (e.g. 4, 8, 16)",
    base_snap="Base snap value (e.g. 4, 8, 16)"
)
async def calculate(interaction: discord.Interaction, bpm: float, desired_snap: int, base_snap: int):
    if base_snap == 0:
        await interaction.response.send_message("⚠️ base_snap cannot be zero!", ephemeral=True)
        return

    result = (bpm * desired_snap) / base_snap
    await interaction.response.send_message(f"🎵 Result: `{result:.2f} BPM`")

# Run the bot
client.run(token)
