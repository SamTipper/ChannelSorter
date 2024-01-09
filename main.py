import discord
import pytz
from os import environ
from discord.ext import bridge, tasks
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Feel free to rename these env variables to suit your programming needs
TOKEN = environ['TOKEN']
GUILD_ID = int(environ['GUILD_ID'])
CAT1_ID = int(environ['CAT1_ID'])
CAT2_ID = int(environ['CAT2_ID'])

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Instantiate a discord client
client = bridge.Bot(command_prefix = '&', help_command=None, intents=intents)


@client.event
async def on_message(message):
    if message.guild.id != GUILD_ID:
        return None

    if message.channel.category.id == CAT2_ID:
        cat = discord.utils.get(message.guild.categories, id=CAT1_ID)
        channel = await client.fetch_channel(int(message.channel.id))
        await channel.edit(position=0, category=cat, sync_permissions=True)


async def move_inactive_channel(channel):
    channel = await client.fetch_channel(channel)
    cat = discord.utils.get(channel.guild.categories, id=CAT2_ID)
    await channel.edit(position=0, category=cat, sync_permissions=True)


@tasks.loop(hours=1)
async def check_for_unused_channels():
    guild = client.get_guild(GUILD_ID)
    category = discord.utils.get(guild.categories, id=CAT1_ID)

    for channel in category.channels:
        channel = await client.fetch_channel(channel.id)
        messages = await channel.history(limit=1).flatten()

        if not messages: 
            await move_inactive_channel(channel.id)
            continue

        last_message = messages[-1]
        time = pytz.UTC.localize(datetime.now())

        if time >= last_message.created_at + timedelta(days=7):
            await move_inactive_channel(channel.id)

            
# On ready
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for activity"))
    print('You have logged in as {0.user}'.format(client))
    check_for_unused_channels.start()


if __name__ == "__main__":
    client.run(TOKEN)
