import discord
import asyncio
from discord.ext import commands
from discord.ext.commands import Bot
from discord import Webhook

# Will need to move this somewhere other than a source file in the future
TOKEN = 'MTA1MjczNjg1NDM2Mjk0NzcwNA.GGb4vM.UzAaoxUGySjvAVPLarupHTePKUyhI8ChOjYzvg'

# may want to limit the intents in the future
intents = discord.Intents.all()

#client
client = commands.Bot(command_prefix='/', intents=intents)

#Makes sure Bot is Getting Response
@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))


#Commands -- /hello-world
@client.event
async def on_message(message):
    # ignore messages sent by the bot
    if message.author == client.user:
        return

    content = str(message.content)

    # case insensitive command 
    if content.lower() == "/hello-world":
        await msg.channel.send('hello world')

client.run(TOKEN);
