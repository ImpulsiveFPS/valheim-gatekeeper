import discord
from discord.ext import commands
from config import BOT_TOKEN
from commands import registration, profile, applications, tickets

# Set up intents
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Load modules
registration.setup(bot)
profile.setup(bot)
applications.setup(bot)
tickets.setup(bot)

# Event: Bot Ready
@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}.")
    await bot.tree.sync()

# Run the bot
bot.run(BOT_TOKEN)
