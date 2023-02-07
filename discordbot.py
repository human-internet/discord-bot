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
        command_prefix='!',
        case_insensitive=True,
        intents=intents
    )

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ensures the bot is working/connected
@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))

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

    channels = discord.utils.get(guild.channels, name='get-verified')
    await channels.send('Please use the ‘/verify’ command to start the humanID verification process.')


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

    if interaction.channel.name != 'get-verified':
        channels = discord.utils.get(interaction.guild.channels, name='get-verified').id
        await interaction.response.send_message(
            'This command can only be used in the <#{}> channel.'.format(str(channels)),
            ephemeral=True
        )
        return


    # Gets the link to humanID
    # response, requestId = requests.get(
    response = requests.get(
        'http://127.0.0.1:8000/api/?serverId={}&userId={}'.format(str(interaction.guild.id), str(author.id))
    )

    # Creates a db entry for the user to keep track of the link timeout
    requests.put(
        'http://127.0.0.1:8000/api/start/?userId=' + str(author.id)
    )


    # Send the humanID link that is unique to the current discord server
    await interaction.response.send_message(
        'Please use this link to verify: {}'.format('http://localhost:3000/?test=' + str(author.id) or response.json()),
        ephemeral=True
    )

    success = False
    outcome = 'Failed to verify your identity. Please try again.'
    for timeout in range(30):
        response = requests.get(
            'http://127.0.0.1:8000/api/confirm/?userId={}'.format(str(author.id)),
        )

        if response.status_code == 200:
            success = True
            break

        time.sleep(1)

    if success:
        roles = discord.utils.get(interaction.guild.roles, name='Verified')
        await author.add_roles(roles)
        outcome = 'Congratulations! You’ve been verified with humanID and been granted access to this server. To keep your identity secure and anonymous, all verification data is never stored and is immediately deleted upon completion.'


    await interaction.edit_original_response(content=outcome)


    currentTime = time.gmtime(time.time())

    embed = discord.Embed(
        title='Verify Attempt',
        description='Status: {}'.format('Success' if success else 'Failure'),
        colour=discord.Colour.dark_gold(),
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


# Sets up the configuration the admin would like
# updates the verified role's name, get-verified channel name, and channel privacy settings
# specify the settings via the parameters
@bot.tree.command(name='setup')
async def setup(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
                'Access to the bot settings is only available to admins. Please contact an admin if you would like to change the settings.',
                ephemeral=True
        )

    message = ctx.message
    embed = discord.Embed(
        title='Verify Attempt',
        description='Status: {}'.format('Success'),
        colour=discord.Colour.dark_gold(),
    )
    view = discord.ui.View()
    # interaction.data gives the value after selecting an option
    d = discord.ui.Select(
        options=[
            discord.SelectOption(label='Channel', value='channel'),
            discord.SelectOption(label='test', value='test'),
            discord.SelectOption(label='Lock', value='lock'),
        ]
    )
    view.add_item(d)

    view.interaction_check = handleInteraction
    await message.channel.send(embed=embed, view=view)



###################################
# The commands below are currently only used for testing/development
###################################

# Command -- /log
@bot.command('log')
async def log(ctx):
    message = ctx.message
    CLIENT_ID = 'SERVER_4R3QUQRNQOSK9TOTWHD7Q2'
    cs = 'g_zsgbW00owFeQHKmfyXP7p6_iUJ9U797_iThf19AsP-jeZu7DWeGqJ.V3aLRRzm'
    headers = {'client-id': CLIENT_ID, 'client-secret': cs , 'Content-Type' : 'application/json' }
    response = requests.get('https://core.human-id.org/v0.0.3/server', headers=headers)
    print(response)

    if response.status_code == 201:
        await message.channel.send('success')
    return
    link = requests.post('https://core.human-id.org/v0.0.3/server/users/web-login', headers=headers)
    CLIENT_ID = 'SERVER_4R3QUQRNQOSK9TOTWHD7Q2'
    cs = 'g_zsgbW00owFeQHKmfyXP7p6_iUJ9U797_iThf19AsP-jeZu7DWeGqJ.V3aLRRzm'
    headers = {'client-id': 'SERVER_4R3QUQRNQOSK9TOTWHD7Q2', 'client-secret': cs , 'Content-Type' : 'application/json' }
    response = requests.post('https://core.human-id.org/v0.0.3/server/users/web-login', headers=headers)
    short_url = ps.Shortener().tinyurl.short(return_url)
    await message.channel.send(short_url)


# Command -- /hello-world
@bot.command('hello-world')
async def helloWorld(ctx):
    message = ctx.message
    sender = message.author
    channels = discord.utils.get(ctx.guild.channels, name='get-verified')
    print(message.guild.id)

    # only look at messages that are not sent by this bot and that are sent in the get-verified channel
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
    print(message.guild.id)
    return


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



###################################
# The two commands below are used together
###################################
async def handleInteraction(interaction):
    print(interaction.data)
    origMessage = interaction.message
    chosen = interaction.data['values']
    if interaction.data['component_type'] == 8:
        # channel
        verifiedRole = discord.utils.get(origMessage.guild.roles, name='Verified')
        everyone = discord.utils.get(origMessage.guild.roles, name='@everyone')
        for channelId in chosen:
            # removes perms for non-verified users for the chosen channels
            channel = await origMessage.guild.fetch_channel(channelId)
            await channel.set_permissions(verifiedRole, read_messages=True, send_messages=True)
            await channel.set_permissions(everyone, read_messages=False, send_messages=False)

        #await interaction.
        await interaction.response.send_message(
                'The specified channels have been locked for non-verified users.',
                ephemeral=True
        )

    else:
        chosen = chosen[0]
        if chosen == 'channel':
            # Might want to rethink this because we would need a db to support it
            view = discord.ui.View()
            view.add_item(discord.ui.ChannelSelect())
            view.interaction_check = handleInteraction
            await interaction.message.edit(embeds=[], view=view)

        elif chosen == 'lock':
            chooseChannel = discord.ui.ChannelSelect(
                channel_types=[discord.ChannelType.text],
                placeholder='temp TODO',
                max_values=len(interaction.message.guild.text_channels)
            )
            view = discord.ui.View()
            view.add_item(chooseChannel)
            view.interaction_check = handleInteraction
            await interaction.message.edit(embeds=[], view=view)



# Should be a slash command, which might be why "This Interaction Failed" error is there
@bot.command('test')
async def test(ctx):

    message = ctx.message
    embed = discord.Embed(
        title='Verify Attempt',
        description='Status: {}'.format('Success'),
        colour=discord.Colour.dark_gold(),
    )
    view = discord.ui.View()
    # interaction.data gives the value after selecting an option
    d = discord.ui.Select(
        options=[
            discord.SelectOption(label='Channel', value='channel'),
            discord.SelectOption(label='test', value='test'),
            discord.SelectOption(label='Lock', value='lock'),
        ]
    )
    view.add_item(d)

    view.interaction_check = handleInteraction
    await message.channel.send(embed=embed, view=view)




"""
# cathes all slash commands (currently only one and should end with only 1 ie /verify)
# when a user does /verify, they'll be sent an ephemeral message with a link to humanID
@bot.event
async def on_interaction(interaction):
    print(interaction)

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
