import discord
from discord.ext import commands
from discord import app_commands
import logging
import os
from dotenv import load_dotenv
from enum import Enum

from keep_alive import keep_alive

# Load .env
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))

keep_alive()

# Logging
logging.basicConfig(level=logging.INFO)

# Setup intents and bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="am!", intents=intents)
tree = bot.tree

class EffectType(app_commands.Transform, str, Enum):
    HORIZONTAL = "horizontal"
    MIDDLE = "middle"
    THREE_COLOR = "three-color"
    SOLID = "solid"

@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"✅ Logged in as {bot.user}")

# ────────────── /calculate COMMAND ──────────────
@tree.command(name="calculate", description="Calculate BPM based on snap", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    bpm="Base BPM",
    desired_snap="Desired snap value (e.g. 4, 8, 16)",
    base_snap="Base snap value (e.g. 4, 8, 16)"
)
async def slash_calculate(interaction: discord.Interaction, bpm: float, desired_snap: int, base_snap: int):
    if base_snap == 0:
        await interaction.response.send_message("⚠️ base_snap cannot be zero!", ephemeral=True)
        return
    result = (bpm * desired_snap) / base_snap
    await interaction.response.send_message(f"🎵 Result: `{result:.2f} BPM`")

# Prefix version
@bot.command(name="calculate")
async def prefix_calculate(ctx, bpm: float, desired_snap: int, base_snap: int):
    if base_snap == 0:
        await ctx.send("⚠️ base_snap cannot be zero!")
        return
    result = (bpm * desired_snap) / base_snap
    await ctx.send(f"🎵 Result: `{result:.2f} BPM`")

# ────────────── /bbcode COMMAND ──────────────
@tree.command(name="bbcode", description="Generate BBCode with gradient and styling", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    text="The text to style",
    effect="Gradient effect type",
    start_color="Start color hex (e.g. #ff0000)",
    middle_color="Middle color (used in middle/three-color)",
    end_color="End color hex",
    font="Font name (optional)",
    size="Font size (optional)",
    bold="Make text bold?",
    italic="Make text italic?"
)
async def slash_bbcode(
    interaction: discord.Interaction,
    text: str,
    effect: EffectType,
    start_color: str,
    middle_color: str = None,
    end_color: str = None,
    font: str = None,
    size: str = None,
    bold: bool = False,
    italic: bool = False,
):
    await bbcode_common(interaction.response.send_message, text, effect.value, start_color, middle_color, end_color, font, size, bold, italic)

# Prefix version
@bot.command(name="bbcode")
async def prefix_bbcode(ctx, effect: str, start_color: str, text: str, end_color: str = None, middle_color: str = None, font: str = None, size: str = None, bold: bool = False, italic: bool = False):
    await bbcode_common(ctx.send, text, effect.lower(), start_color, middle_color, end_color, font, size, bold, italic)

# ────────────── Shared BBCode Logic ──────────────
async def bbcode_common(send_func, text, effect, start_color, middle_color, end_color, font, size, bold, italic):
    def interpolate(c1, c2, t):
        c1 = [int(c1[i:i+2], 16) for i in (1, 3, 5)]
        c2 = [int(c2[i:i+2], 16) for i in (1, 3, 5)]
        return "#" + "".join(f"{round(c1[i] + (c2[i] - c1[i]) * t):02x}" for i in range(3))

    def apply_gradient(text, colors):
        result = ""
        if len(colors) == 2:
            for i, ch in enumerate(text):
                color = interpolate(colors[0], colors[1], i / max(len(text) - 1, 1))
                result += f"[color={color}]{ch}[/color]"
        elif len(colors) == 3:
            half = len(text) // 2
            for i, ch in enumerate(text):
                if i < half:
                    color = interpolate(colors[0], colors[1], i / max(half - 1, 1))
                else:
                    color = interpolate(colors[1], colors[2], (i - half) / max(len(text) - half - 1, 1))
                result += f"[color={color}]{ch}[/color]"
        return result

    if effect == "solid":
        bbcode_text = f"[color={start_color}]{text}[/color]"
    elif effect == "horizontal":
        if not end_color:
            await send_func("⚠️ You must provide `end_color` for horizontal effect.")
            return
        bbcode_text = apply_gradient(text, [start_color, end_color])
    elif effect == "middle" or effect == "three-color":
        if not middle_color or not end_color:
            await send_func("⚠️ You must provide both `middle_color` and `end_color`.")
            return
        bbcode_text = apply_gradient(text, [start_color, middle_color, end_color])
    else:
        await send_func("⚠️ Unknown effect type. Use one of: solid, horizontal, middle, three-color.")
        return

    if font:
        bbcode_text = f"[font={font}]{bbcode_text}[/font]"
    if size:
        bbcode_text = f"[size={size}]{bbcode_text}[/size]"
    if bold:
        bbcode_text = f"[b]{bbcode_text}[/b]"
    if italic:
        bbcode_text = f"[i]{bbcode_text}[/i]"

    await send_func(f"🎨 Generated BBCode:\n```\n{bbcode_text}\n```")

# ────────────── RUN BOT ──────────────
bot.run(token)
