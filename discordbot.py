import discord
import asyncio
from discord.ext import commands
from discord import Webhook

# Will need to move this somewhere other than a source file in the future
TOKEN = 'MTA1MjczNjg1NDM2Mjk0NzcwNA.GGb4vM.UzAaoxUGySjvAVPLarupHTePKUyhI8ChOjYzvg'

# may want to limit the intents in the future
intents = discord.Intents.all()

# bot (subclass of the discord client class)
bot = commands.Bot(
        command_prefix='/',
        case_insensitive=True,
        intents=intents
    )

# ensures the bot is working/connected
@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))


# Command -- /hello-world
@bot.command('hello-world')
async def helloWorld(ctx):
    message = ctx.message

    # only look at messages that are not sent by this bot
    if message.author != bot.user:
        await message.channel.send('hello world')


bot.run(TOKEN);
