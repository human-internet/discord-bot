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
    sender = ctx.message.author

    # only look at messages that are not sent by this bot
    if sender != bot.user:
        # grabs the id that represents the verified role
        roles = discord.utils.get(ctx.guild.roles, name='Verified')

        # add the role to the user if the role exists
        if roles:
            await sender.add_roles(roles)


# used to remove the verified role for testing
@bot.command('remove-verified')
async def removeVerify(ctx):
    sender = ctx.message.author

    if sender != bot.user:
        roles = discord.utils.get(ctx.guild.roles, name='Verified')
        await sender.remove_roles(roles)


bot.run(TOKEN);
