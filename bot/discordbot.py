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


# Catches the /verify slash command
@bot.tree.command(name='verify')
async def verify(interaction: discord.Interaction):
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
        'http://0.0.0.0:8080/api/?serverId={}&userId={}'.format(str(interaction.guild.id), str(author.id))
    )

    # Creates a db entry for the user to keep track of the link timeout
    requests.put(
        'http://0.0.0.0:8080/api/start/?userId=' + str(author.id)
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
            'http://0.0.0.0:8080/api/confirm/?userId={}'.format(str(author.id)),
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

    # TODO
    if not interaction.user.guild_permissions.administrator and False:
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
    view.add_item(d)
    locked = discord.ui.Button(label='t')
    view.add_item(locked)
    locked = discord.ui.Button(label='test')
    view.add_item(locked)

    view.interaction_check = handleInteraction
    await interaction.response.send_message(
        embed=embed,
        view=view,
        ephemeral=True
    )



async def handleInteraction(interaction):
    origMessage = interaction.message
    print(33)

    if interaction.data['component_type'] == 2:
        print('button')
        return

    chosen = interaction.data['values']
    if chosen[0] in ['text', 'voice', 'category']:
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
        # channel
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
        await interaction.response.edit_message(embed=embed, view=view)



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
    print(interaction.data)


bot.run(TOKEN);
