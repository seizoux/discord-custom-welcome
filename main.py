import os # library
import discord # library
from discord import client  # library
import asyncpg # library
import os # library

# THIS IS THE TRIGGER PREFIX OF UR COMMANDS, LIKE ".BAN" "/BAN" "!BAN" "?BAN" "$BAN"
intents=discord.Intents.default()
intents.members=True
client = commands.Bot(command_prefix="PREFIX HERE", intents=intents)

#LOADING COGS
for filename in os.listdir("./cogs"):
    if filename.endswith(".py") and not filename.startswith("_"):
        client.load_extension(f"cogs.{filename[:-3]}")

#CONNECT TO THE POSTGRESQL DATABASE
async def create_db_pool():
    client.pg_con = await asyncpg.create_pool(database="postgres", user="postgres", password="postgres")



# WARNING: HERE PUT THE TOKEN OF UR BOT!!
token="TOKEN HERE"



# RUN CLIENT -- IF U DELETE THIS, THE BOT DOESN'T WORK!!
client.loop.run_until_complete(create_db_pool())
client.run(token)
