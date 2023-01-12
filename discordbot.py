import discord
import time
import datetime
from discord import app_commands
import asyncio
from discord.ext import commands
from discord import Webhook
import pyshorteners as ps
import aiohttp
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

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ensures the bot is working/connected
@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))

# TODO has not been tested
# Goal is to automatically create the verified role and get-verified channel when
# joining a server
@bot.event
async def on_guild_join(guild):
    roles = discord.utils.get(guild.roles, name='Verified')
    if not roles:
        await guild.create_role(name='Verified')

    # only create the channel if it does not exist
    channels = discord.utils.get(guild.channels, name='get-verified')
    if not channels:
        await guild.create_text_channel('get-verified')

    
# Catches the /blep slash command
@bot.tree.command(name='blep')
@discord.app_commands.choices(animal=[
    discord.app_commands.Choice(name='Dog', value='animal_dog'),
    discord.app_commands.Choice(name='Cat', value='animal_cat'),
    discord.app_commands.Choice(name='Penguin', value='animal_penguin'),
])
async def blep(interaction: discord.Interaction, animal: discord.app_commands.Choice[str]):
    channels = discord.utils.get(interaction.guild.channels, name='logs')
    if not channels:
        await interaction.guild.create_text_channel('logs')

    author = interaction.user
    currentTime = time.gmtime(time.time())
    embed = discord.Embed(
        title='Verify Attempt',
    )
    embed.set_footer(
        text=datetime.datetime(
            year=currentTime.tm_year,
            month=currentTime.tm_mon,
            day=currentTime.tm_mday,
            hour=currentTime.tm_hour,
            minute=currentTime.tm_min,
            second=currentTime.tm_sec
        )
    )
    embed.set_author(
        name=author.name,
        url=author.display_avatar.url,
        icon_url=author.display_avatar.url
    )

    await channels.send(embed=embed)
    # await channels.send('User {} (id: {}) tried to verify.')
    return

    CLIENT_ID = 'SERVER_4R3QUQRNQOSK9TOTWHD7Q2'
    cs = 'g_zsgbW00owFeQHKmfyXP7p6_iUJ9U797_iThf19AsP-jeZu7DWeGqJ.V3aLRRzm'
    headers = {'client-id': 'SERVER_4R3QUQRNQOSK9TOTWHD7Q2', 'client-secret': cs , 'Content-Type' : 'application/json' }
    response = requests.post('https://core.human-id.org/v0.0.3/server/users/web-login', headers=headers)
    return_url = response.json()['data']['webLoginUrl']
    short_url = ps.Shortener().tinyurl.short(return_url)
    await interaction.response.send_message(
            'Please use this link to verify: {}'.format(short_url),
            ephemeral=True
    )



###################################
# The commands below are currently only used for testing/development
###################################

# Command -- /hello-world
@bot.command('hello-world')
async def helloWorld(ctx):
    message = ctx.message
    sender = message.author
    channels = discord.utils.get(ctx.guild.channels, name='get-verified')

    # only look at messages that are not sent by this bot and that are sent in the get-verified channel
    if sender != bot.user and channels == message.channel:
        # grabs the id that represents the Verified role
        roles = discord.utils.get(ctx.guild.roles, name='Verified')


        # add the role to the user if the role exists
        if roles:
            await sender.add_roles(roles)
            await message.channel.send('Added the role')


# Command -- /log
@bot.command('log')
async def log(ctx):
    message = ctx.message

    channels = discord.utils.get(message.guild.channels, name='Logs')
    if not channels:
        await message.guild.create_text_channel('Logs')


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


    # TODO
    # may want to hash the ids in the future (will also need the user's id to identify which user to verify)
    # webhooks could be useful to determine whether someone has verified (clicking button -> change db -> webhook catches change)
    await message.channel.send('http://localhost:3010?channel={}&guild={}'.format(message.channel.id, message.channel.guild.id))
    response = requests.get('http://localhost:3010/data')

    sender = message.author

    # if the user was verified
    if sender != bot.user and response.json()['verify']:
        # grabs the id that represents the Verified role
        roles = discord.utils.get(ctx.guild.roles, name='Verified')


        # add the role to the user if the role exists
        if roles:
            await sender.add_roles(roles)
            await message.channel.send('Added the role')

    else:
        await message.channel.send('The link has expired.')

    return


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


@bot.command('eph')
async def eph(ctx):
    message = await ctx.message.channel.send('React to Verify')

    roles = discord.utils.get(ctx.guild.emojis, name='test')
    await message.add_reaction(roles)


"""
# cathes all slash commands (currently only one and should end with only 1 ie /verify)
# when a user does /verify, they'll be sent an ephemeral message with a link to humanID
@bot.event
async def on_interaction(interaction):
    print(interaction.guild)
    print(interaction.guild.id)
    print(interaction.guild.shard_id)
    print(bot.application_id)

    return
    CLIENT_ID = 'SERVER_4R3QUQRNQOSK9TOTWHD7Q2'
    cs = 'g_zsgbW00owFeQHKmfyXP7p6_iUJ9U797_iThf19AsP-jeZu7DWeGqJ.V3aLRRzm'
    headers = {'client-id': 'SERVER_4R3QUQRNQOSK9TOTWHD7Q2', 'client-secret': cs , 'Content-Type' : 'application/json' }
    response = requests.post('https://core.human-id.org/v0.0.3/server/users/web-login', headers=headers)
    return_url = response.json()['data']['webLoginUrl']
    short_url = ps.Shortener().tinyurl.short(return_url)
    await interaction.response.send_message(
            'Please use this link to verify: {}'.format(short_url),
            ephemeral=True
    )
"""


bot.run(TOKEN);
