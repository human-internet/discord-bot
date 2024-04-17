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
import sentry_sdk

# load the environment variables
env = dotenv_values()

# Will need to move this somewhere other than a source file in the future
TOKEN = env['DISCORD_TOKEN']

SENTRY_DSN = env['DISCORD_SENTRY_DSN']
sentry_sdk.init(
    dsn=SENTRY_DSN,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    # profiles_sample_rate=1.0,
)

# may want to limit the intents in the future
intents = discord.Intents.all()
intents.members = True

# bot (subclass of the discord client class)
bot = commands.Bot(
    command_prefix='!',
    case_insensitive=True,
    intents=intents
)

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Developer Console home page
dc_url = 'https://developers.human-id.org/'
# Discord Bot Integration Guide
guide_url = 'https://docs.human-id.org/discord-bot-integration-guide'

async def ensure_text_channel(member, interaction: discord.Interaction, channel_name):
    is_guild = isinstance(member, discord.Guild)
    if is_guild:
        channel = discord.utils.get(member.channels, name=channel_name)
    else:
        channel = discord.utils.get(member.guild.channels, name=channel_name)
    # Return the channel if it exists already
    if channel:
        return channel
    
    try:
        if is_guild:
            channel = await member.create_text_channel(channel_name)
        else:
            channel = await member.guild.create_text_channel(channel_name)
        return channel
    except discord.Forbidden as e:
        message = f"""Reminder: The humanID Verification bot requires administrator permissions to create the get-verified channel and assign the humanID-Verified role. Please ensure the bot has the necessary permissions to complete the verification process. If it does not, you may have to reinstall the bot with the correct permissions."""
        if interaction is None:
            await member.send(message)
        else:
            await interaction.response.send_message(message, ephemeral=True)
        return

# ensures the bot is working/connected
@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


@bot.event
async def on_member_join(member):
    # This function will be called when a new member joins the server
    # Sends the member a welcome message that mentions the server name and the member
    # Get the "get-verified" channel from the server and sends a reference to user DM
    get_verified_channel = await ensure_text_channel(member, None, "get-verified")
    server_name = member.guild.name
    await member.send(
        f"""Hey, {member.mention}! Welcome to {server_name}! We are thrilled to have you here. To get started, please head to the server and click on the {get_verified_channel.mention} channel. Then type '/verify' to invoke this bot to help complete the verification process.\nAfter that, you'll be all set to embark on your Discord journey. If you have any questions or need assistance, don't hesitate to reach out to humanID at discord@human-id.org. Replies to this message do not reach humanID. Enjoy your time here!
""")


# /help command that gives a list of commands
@bot.tree.command(name="help")
async def hello(interaction: discord.Interaction):
    member = interaction.user
    get_verified_channel = await ensure_text_channel(member, interaction, "get-verified")
    await interaction.response.send_message(f"""To get started, {member.mention}, please head to the server and click on the {get_verified_channel.mention} channel. Then type '/verify' to invoke this bot to help complete the verification process.\nAfter that, you'll be all set to embark on your Discord journey. If you have any questions or need assistance, don't hesitate to reach out to humanID at discord@human-id.org. Replies to this message do not reach humanID. Enjoy your time here!
""")


# When joining a server
# 1. automatically create the humanID-Verified role, get-verified channel, and logs channel
# 2. set the permissions for the humanID-Verified role
# 3. set the permissions for the get-verified channel
@bot.event
async def on_guild_join(guild):
    get_verified_channel = await ensure_text_channel(guild, None, "get-verified")
    log_channel = await ensure_text_channel(guild, None, "logs")
    log_channel = discord.utils.get(guild.channels, name='logs')
    if not log_channel:
        log_channel = await guild.create_text_channel('logs')
    await setupVerifiedRole(guild)
    # everyone_channels = []
    # for channel in guild.channels:
    #     # Check if the @everyone role has the "View Channel" permission
    #     if channel.permissions_for(guild.default_role).view_channel:
    #         everyone_channels.append(channel.name)
    # if everyone_channels:
    #     await verification_channel.send(f"Channels viewable by @everyone prior to installing humanID Discor Bot: {', '.join(everyone_channels)}")
    #     await verification_channel.send(f"These channels are now viewable by users with @humanID-Verified role through completing the /verify command.")
    # else:
    #     await verification_channel.send("There are no channels viewable by @everyone in this server.")
    # verified_role = discord.utils.get(guild.roles, name='humanID-Verified')
    # for channel_name in everyone_channels:
    #     if channel_name != 'get-verified':
    #         channel = discord.utils.get(guild.channels, name=channel_name)
    #         await channel.set_permissions(everyone, read_messages=False, send_messages=False)
    #         await channel.set_permissions(verified_role, read_messages=True, send_messages=True)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(
            view_channel=True,
            use_application_commands=True,
            change_nickname=True,
            send_messages=True
        )
    }
    await get_verified_channel.edit(overwrites=overwrites)


async def setupVerifiedRole(guild):
    # Getting the Verified Role
    verification_channel = await ensure_text_channel(guild, None, "get-verified")
    verified_role = discord.utils.get(guild.roles, name='humanID-Verified')
    if verified_role:
        await verification_channel.send(
            'Pre-existing humanID-Verified Role Detected: Please make sure the humanID-Verified role is ranked under the humanID Verification bot Role.')
    else:
        await guild.create_role(name='humanID-Verified')
    verified_role = discord.utils.get(guild.roles, name='humanID-Verified')
    verified_role_permissions = verified_role.permissions
    verified_role_permissions.update(
        view_channel=True,
        change_nickname=True,
        send_messages=True,
        send_messages_in_threads=True,
        create_public_threads=True,
        embed_links=True,
        attach_files=True,
        add_reactions=True,
        use_external_emojis=True,
        read_message_history=True,
        use_application_commands=True
    )
    try:
        # Update the permissions for the @humanID-Verified role
        await verified_role.edit(permissions=verified_role_permissions)
    except discord.Forbidden:
        # If the bot lacks the "Manage Roles" permission or other issues occur, send a message in the channel.
        error_message = (
            f"Failed to update @Verfied role permissions. "
            f"Please ensure the @humanID-Verified role has appropriate permissions within the server."
        )
        await verification_channel.send(error_message)
    await verification_channel.send("""To gain full access to this Discord server, please enter '/verify' in the chat box to initiate the verification process. Rest assured, we do not retain any of your private information during this process. If you encounter any issue, please contact humanID at discord@human-id.org. Replies to this message do not reach humanID.
                                    """)


# test simple slash commandac
@bot.tree.command(name="hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hey {interaction.user.mention}! This is a slash command!")


# Catches the /verify slash command
@bot.tree.command(name='verify')
async def verify(interaction: discord.Interaction):
    channels = await ensure_text_channel(interaction.user, interaction, "logs")

    author = interaction.user
    serverId = str(interaction.guild.id)
    userId = str(author.id)

    if interaction.channel.name != 'get-verified':
        # message was not sent in the allowed channel
        channels = await ensure_text_channel(interaction.user, interaction, "get-verified")
        channels = channels.id
        await interaction.response.send_message(
            'This command can only be used in the <#{}> channel.'.format(str(channels)),
            ephemeral=True
        )
        return

    BACKEND_URL = env["DISCORD_BACKEND_URL"]
    FRONTEND_URL = env["DISCORD_FRONTEND_URL"]
    response = requests.get(
        BACKEND_URL + '/api/?serverId=' + serverId
    )
    if response.status_code == 400:
        await interaction.response.send_message(
            'Your server is not yet registered with humanID. Please ask an admin to go to <{}> to register.\nFor a more detailed step-by-step walk-through, go to <{}>.'
            .format(dc_url, guide_url),
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
    message = 'Please use this link to verify: {}'.format(
        # TODO hash id
        FRONTEND_URL + '?server={}&url={}'.format(interaction.guild.id, url)
    )
    await interaction.response.send_message(
        message,
        ephemeral=True
    )
    success = False
    outcome = 'Failed to verify your identity. Please try again.'
    # 3 minute of pinging
    for timeout in range(60):
        # Trying the await clause
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
        roles = discord.utils.get(interaction.guild.roles, name='humanID-Verified')
        if roles:
            try:
                await author.add_roles(roles)
                outcome = 'Congratulations! You’ve been verified with humanID and been granted access to this server. To keep your identity secure and anonymous, all verification data is never stored and is immediately deleted upon completion.'
                requests.delete(
                    BACKEND_URL + '/api/removeEntry/?requestId={}'.format(requestId)
                )
            except discord.Forbidden:
                outcome = "I don't have the permission to add the humanID-Verified role, please contact humanID at discord@human-id.org."
            except discord.HTTPException as e:
                outcome = "An error occurred while trying to add the humanID-Verified role: {}".format(e)
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


# -----------------------------------Version 2 - Setup----------------------------------------
# Sets up the configuration the admin would like
# updates the verified role's name, get-verified channel name, and channel privacy settings
# specify the settings via the parameters

# @bot.tree.command(name='setup')
# async def setup(interaction: discord.Interaction):
#     if not interaction.user.guild_permissions.administrator:
#         # only admins can run this commmand
#         await interaction.response.send_message(
#             'Access to the bot settings is only available to admins. Please contact an admin if you would like to change the settings.',
#             ephemeral=True
#         )
#         return

#     embed = discord.Embed(
#         title='Verify Attempt',
#         description='Status: {}'.format('Success'),
#         colour=discord.Colour.dark_gold(),
#     )
#     view = discord.ui.View()
#     # interaction.data gives the value after selecting an option
#     d = discord.ui.Select(
#         placeholder='temp TODO',
#         options=[
#             discord.SelectOption(label='Voice Channels', value='voice'),
#             discord.SelectOption(label='Text Channels', value='text'),
#             discord.SelectOption(label='Categories', value='category'),
#         ]
#     )

#     # code for buttons if wanted for QOL in the future TODO
#     view.add_item(d)
#     locked = discord.ui.Button(label='t')
#     view.add_item(locked)
#     locked = discord.ui.Button(label='test')
#     view.add_item(locked)

#     view.interaction_check = handleInteraction
#     await interaction.response.send_message(
#         embed=embed,
#         view=view,
#         ephemeral=True
#     )


# async def handleInteraction(interaction):
#     origMessage = interaction.message

#     if interaction.data['component_type'] == 2:
#         # button interaction
#         print('button')
#         return

#     chosen = interaction.data['values']
#     if chosen[0] in ['text', 'voice', 'category']:
#         # setup choices for channel selection
#         channelType = discord.ChannelType.text
#         maxSize = len(interaction.guild.text_channels)
#         if chosen[0] == 'voice':
#             channelType = discord.ChannelType.voice
#             maxSize = len(interaction.guild.voice_channels)

#         elif chosen[0] == 'category':
#             channelType = discord.ChannelType.category
#             maxSize = len(interaction.guild.categories)

#         chooseChannel = discord.ui.ChannelSelect(
#             channel_types=[channelType],
#             max_values=maxSize,
#         )
#         view = discord.ui.View()
#         view.add_item(chooseChannel)
#         view.interaction_check = handleInteraction
#         await interaction.response.edit_message(view=view)

#     else:
#         # hide channel
#         updatedChannels = []
#         verifiedRole = discord.utils.get(origMessage.guild.roles, name='Verified')
#         everyone = discord.utils.get(origMessage.guild.roles, name='@everyone')
#         for channelId in chosen:
#             # removes perms for non-verified users for the chosen channels
#             channel = await origMessage.guild.fetch_channel(int(channelId))
#             updatedChannels.append(channel.name)
#             await channel.set_permissions(verifiedRole, read_messages=True, send_messages=True)
#             await channel.set_permissions(everyone, read_messages=False, send_messages=False)

#         view = discord.ui.View()
#         embed = discord.Embed(
#             title='Successfully locked {} channel(s)'.format(len(chosen)),
#             description=', '.join(updatedChannels),
#             colour=discord.Colour.dark_gold(),
#         )
#         d = discord.ui.Select(
#             placeholder='temp TODO',
#             options=[
#                 discord.SelectOption(label='Voice Channels', value='voice'),
#                 discord.SelectOption(label='Text Channels', value='text'),
#                 discord.SelectOption(label='Categories', value='category'),
#             ]
#         )
#         view.add_item(d)
#         view.interaction_check = handleInteraction
#         await interaction.response.edit_message(embed=embed, view=view)


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

    # await message.channel.send(embed=embed, view=view)


# async def role_positions_setup(guild):
#     num_roles = len(guild.roles)
#     new_bot_position = num_roles - 1
#     new_verify_position = num_roles - 2
#     verified_role = discord.utils.get(guild.roles, name='Verified') 
#     bot_role = discord.utils.get(guild.roles, name=bot_name)
#     positions = {
#         verified_role: new_verify_position,
#         bot_role: new_bot_position
#     }
#     new_positions = await guild.edit_role_positions(positions=positions)
#     roles = guild.roles
#     for role in new_positions:
#         print(role.name, ': ', role.position)

bot.run(TOKEN);