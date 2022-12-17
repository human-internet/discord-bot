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

    # unsure what this represents
    # TODO
    # 1) need to figure out what client_id and secret represents
    #   a) have tried guild id, bot id
    #   b) haven't been able to find any id that starts with SERVER

    CLIENT_ID = 'SERVER_4R3QUQRNQOSK9TOTWHD7Q2'
    secret = 'g_zsgbW00owFeQHKmfyXP7p6_iUJ9U797_iThf19AsP-jeZu7DWeGqJ.V3aLRRzm'
    headers = {
        'client-id': CLIENT_ID,
        'client-secret': secret,
        'Content-Type' : 'application/json'
    }

    # gets the humanID url that verifies the user and sends a shortened version to the user
    response = requests.post('https://core.human-id.org/v0.0.3/server/users/web-login', headers=headers)
    return_url = response.json()['data']['webLoginUrl']
    short_url = ps.Shortener().tinyurl.short(return_url)
    await message.channel.send(short_url)

    CLIENT_ID = '982430908281933865'
    cs = '6fJVAg9lYw9MtrLYF0DZM-67-W_aDC6A'
    headers = {'client-id': CLIENT_ID, 'client-secret': cs , 'Content-Type' : 'application/json' }
    response = requests.post('https://s-api.human-id.org/v1', headers=headers)
    return

    # Unsure what the post request is doing (maybe storing the user that is logging in?) 
    """
    CLIENT_ID = '982430908281933865'
    cs = '6fJVAg9lYw9MtrLYF0DZM-67-W_aDC6A'
    headers = {'client-id': CLIENT_ID, 'client-secret': cs , 'Content-Type' : 'application/json' }
    response = requests.post('https://s-api.human-id.org/v1', headers=headers)
    """

    # Unsure what the point of this code is supposed to do
    # It seems like it simply uses a discord webhook to send a message, but why not just send it manually
    """
    connect to #async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url('url-here', session=session)
        await webhook.send('Hello World') 
    """

    # Need to know that the endpoint is supposed to do
    # Looks like its needed to check whether the verification was a success
    """
    response2 =  requests.post('https://core.human-id.org/v0.0.3/server/users/exchange', headers=headers)
    return_value = response2.json()
    """

    # Does something depending on whether the user was verified successfully
    # If they did, we send back a link?
    # else, we send a link indicating the error?
    """
    if return_value['success'] == True:
        et = return_value['exchangeToken']
        print('http://18.225.5.208:8000/success_bot?et=' + et)
    else:
        reason = str(response2.reason).replace(' ', '')
        fail_url = ('http://18.225.5.208:8000/failure_bot?code=' + str(response2.status_code) + '&message=' + reason)
        print(fail_url)
    """

    # Unknown link
    """
    await msg.channel.send(f"https://bit.ly/3A5b5bW")
    """


bot.run(TOKEN);
