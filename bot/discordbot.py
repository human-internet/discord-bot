import discord
import time
import datetime
from discord import app_commands
import asyncio
from discord.ext import commands
from discord import Webhook
import requests
import pyshorteners as ps
import aiohttp
from dotenv import dotenv_values

# load the environment variables
env = dotenv_values()

# Will need to move this somewhere other than a source file in the future
TOKEN = env['DISCORD_TOKEN']
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
    print("Bot is Up and Ready!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


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
    await channels.send('By using the ‘/verify’ command, you can start the humanID verification process.')


# test simple slash command
@bot.tree.command(name="hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hey {interaction.user.mention}! This is a slash command!"
                                            , ephemeral=True)


# Catches the /verify slash command
@bot.tree.command(name='verify')
async def verify(interaction: discord.Interaction):
    channels = discord.utils.get(interaction.guild.channels, name='logs')
    if not channels:
        channel = await interaction.guild.create_text_channel('logs')

    author = interaction.user
    serverId = str(interaction.guild.id)
    userId = str(author.id)

    if interaction.channel.name != 'get-verified':
        # message was not sent in the allowed channel
        channels = discord.utils.get(interaction.guild.channels, name='get-verified').id
        await interaction.response.send_message(
            'This command can only be used in the <#{}> channel.'.format(str(channels)),
            ephemeral=True
        )
        return

    BACKEND_URL = env["DISCORD_BACKEND_URL"]
    FRONTEND_URL = env["DISCORD_FRONTEND_URL"]

    # await interaction.response.send_message(
    #         # 'This server does not have associated credentials. Please ask an admin to add this server from the humanID developer console.',
    #         BACKEND_URL,
    #         ephemeral=True
    #     )
    # return
    # Gets the link to humanID
    response = requests.get(
        BACKEND_URL + '/api?serverId=' + serverId
    )

    if response.status_code == 400:
        await interaction.response.send_message(
            'This server does not have associated credentials. Please ask an admin to add this server from the humanID developer console.',
            ephemeral=True
        )
        return
    elif response.status_code == 403:
        await interaction.response.send_message(
            'Invalid credentials associated with this server.',
            ephemeral=True
        )
        return

    resJson = response.json()
    requestId = resJson['requestId']
    url = resJson['url']

    # Creates a db entry for the user to keep track of the link timeout
    requests.put(
        BACKEND_URL + '/api/start/?requestId={}&userId={}&serverId={}'.format(requestId, userId, serverId)
    )

    # hash id here TODO
    hashedId = userId;

    # Send the humanID link that is unique to the current discord server
    await interaction.response.send_message(
        'Please use this link to verify: {}'.format(
            # TODO hash id
            FRONTEND_URL + '?server={}&url={}'.format(interaction.guild.id, url)
        ),
        ephemeral=True
    )

    success = False
    outcome = 'Failed to verify your identity. Please try again.'

    # 5 minute of pinging
    for timeout in range(100):
        response = requests.get(
            BACKEND_URL + '/api/confirm/?requestId={}'.format(requestId),
        )

        # verification success
        if response.status_code == 200:
            success = True
            break

        # user has not verified yet
        elif response.status_code == 202:
            await asyncio.sleep(3)

        # unable to verify (timeout) or there was never an a verification attempt with the given user
        else:
            break

    if success:
        requests.delete(
            BACKEND_URL + '/api/removeEntry/?requestId={}'.format(requestId)
        )
        
        roles = discord.utils.get(interaction.guild.roles, name='Verified')
        await author.add_roles(roles)
        outcome = 'Congratulations! You’ve been verified with humanID and been granted access to this server. To keep your identity secure and anonymous, all verification data is never stored and is immediately deleted upon completion.'
    await interaction.edit_original_response(content=outcome)

    # log verification attempt into the log channel
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
    if not interaction.user.guild_permissions.administrator and False:
        # only admins can run this commmand
        await interaction.response.send_message(
            'Access to the bot settings is only available to admins. Please contact an admin if you would like to change the settings.',
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title='Verify Attempt',
        description='Status: {}'.format('Success'),
        colour=discord.Colour.dark_gold(),
    )
    view = discord.ui.View()
    # interaction.data gives the value after selecting an option
    d = discord.ui.Select(
        placeholder='temp TODO',
        options=[
            discord.SelectOption(label='Voice Channels', value='voice'),
            discord.SelectOption(label='Text Channels', value='text'),
            discord.SelectOption(label='Categories', value='category'),
        ]
    )

    # code for buttons if wanted for QOL in the future TODO
    # view.add_item(d)
    # locked = discord.ui.Button(label='t')
    # view.add_item(locked)
    # locked = discord.ui.Button(label='test')
    # view.add_item(locked)

    view.interaction_check = handleInteraction
    await interaction.response.send_message(
        embed=embed,
        view=view,
        ephemeral=True
    )


async def handleInteraction(interaction):
    origMessage = interaction.message

    if interaction.data['component_type'] == 2:
        # button interaction
        return

    chosen = interaction.data['values']
    if chosen[0] in ['text', 'voice', 'category']:
        # setup choices for channel selection
        channelType = discord.ChannelType.text
        maxSize = len(interaction.guild.text_channels)
        if chosen[0] == 'voice':
            channelType = discord.ChannelType.voice
            maxSize = len(interaction.guild.voice_channels)

        elif chosen[0] == 'category':
            channelType = discord.ChannelType.category
            maxSize = len(interaction.guild.categories)

        chooseChannel = discord.ui.ChannelSelect(
            channel_types=[channelType],
            max_values=maxSize,
        )
        view = discord.ui.View()
        view.add_item(chooseChannel)
        view.interaction_check = handleInteraction
        await interaction.response.edit_message(view=view)

    else:
        # hide channel
        updatedChannels = []
        verifiedRole = discord.utils.get(origMessage.guild.roles, name='Verified')
        everyone = discord.utils.get(origMessage.guild.roles, name='@everyone')
        for channelId in chosen:
            # removes perms for non-verified users for the chosen channels
            channel = await origMessage.guild.fetch_channel(int(channelId))
            updatedChannels.append(channel.name)
            await channel.set_permissions(verifiedRole, read_messages=True, send_messages=True)
            await channel.set_permissions(everyone, read_messages=False, send_messages=False)

        view = discord.ui.View()
        embed = discord.Embed(
            title='Successfully locked {} channel(s)'.format(len(chosen)),
            description=', '.join(updatedChannels),
            colour=discord.Colour.dark_gold(),
        )
        d = discord.ui.Select(
            placeholder='temp TODO',
            options=[
                discord.SelectOption(label='Voice Channels', value='voice'),
                discord.SelectOption(label='Text Channels', value='text'),
                discord.SelectOption(label='Categories', value='category'),
            ]
        )
        view.add_item(d)
        view.interaction_check = handleInteraction
        await interaction.response.edit_message(embed=embed, view=view)


@bot.command('serverid')
async def serverid(ctx):
    await message.channel.send('The server id of this server is: {}'.format(ctx.guild.id))


###################################
# The commands below are currently only used for testing/development
###################################

# Command -- /log
@bot.command('log')
async def log(ctx):
    channels = await ctx.guild.fetch_channels()


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
        placeholder='temp TODO',
        options=[
            discord.SelectOption(label='Voice Channels', value='voice'),
            discord.SelectOption(label='Text Channels', value='text'),
            discord.SelectOption(label='Categories', value='category'),
        ]
    )
    view.add_item(d)
    locked = discord.ui.Button(label='test')
    view.add_item(locked)

    view.interaction_check = handleInteraction
    # await message.channel.send(embed=embed, view=view)


@bot.event
async def on_interaction(interaction):
    print(interaction.guild.id)
    print(interaction.data)


bot.run(TOKEN);
