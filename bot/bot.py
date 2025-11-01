import discord
from discord.ext import commands
from config.config import BOT_TOKEN

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'logged in as {bot.user}')

if __name__ == "__main__":
    bot.run(BOT_TOKEN)