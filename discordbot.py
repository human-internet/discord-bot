import discord
import asyncio
from discord.ext import commands
from discord import Webhook
import requests
import pyshorteners as ps

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
    sender = message.author

    # only look at messages that are not sent by this bot
    if sender != bot.user:
        # grabs the id that represents the Verified role
        roles = discord.utils.get(ctx.guild.roles, name='Verified')

        # add the role to the user if the role exists
        if roles:
            await sender.add_roles(roles)
            await message.channel.send('Added the role')


# used to remove the verified role for testing
@bot.command('remove-verified')
async def removeVerify(ctx):
    message = ctx.message
    sender = message.author

    if sender != bot.user:
        roles = discord.utils.get(ctx.guild.roles, name='Verified')
        await sender.remove_roles(roles)
        await message.channel.send('Removed the role')


@bot.command('redirect')
async def redirect(ctx):
    message = ctx.message


    #print(dir(ctx.guild))
    print(message.id)
    return
    # unsure what this represents
    CLIENT_ID = 'SERVER_4R3QUQRNQOSK9TOTWHD7Q2'
    secret = 'g_zsgbW00owFeQHKmfyXP7p6_iUJ9U797_iThf19AsP-jeZu7DWeGqJ.V3aLRRzm'
    headers = {
        'client-id': 'SERVER_4R3QUQRNQOSK9TOTWHD7Q2',
        'client-secret': secret,
        'Content-Type' : 'application/json'
    }

    # gets the humanID url that verifies the user and sends a shortened version to the user
    response = requests.post('https://core.human-id.org/v0.0.3/server/users/web-login', headers=headers)
    return_url = response.json()['data']['webLoginUrl']
    short_url = ps.Shortener().tinyurl.short(return_url)
    await message.channel.send(short_url)


bot.run(TOKEN);
