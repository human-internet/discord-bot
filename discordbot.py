import discord
import asyncio
from discord.ext import commands
from discord.ext.commands import Bot
from discord.utils import get
from discord import Webhook
import aiohttp
import http.client
import requests
import pyshorteners as ps
import tracemalloc
tracemalloc.start()
from flask_mysqldb import MySQL
from flask import Flask


app = Flask(__name__)
app.config['MYSQL_HOST'] = '127.0.0.1'

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask'

mysql = MySQL(app)

#with app.app_context():
#            cursor = mysql.connection.cursor()
#cursor.execute(''' CREATE TABLE Users(ID NOT NULL,  USER VARCHAR(50)) ''')
#cursor = mysql.connection.cursor()

TOKEN = 'OTgyNDMwOTA4MjgxOTMzODY1.GMhrx5.dXdHiTfJGSIf1k1XfYxLUVmX2-i1xXekDlrRF0'

intents=intents=discord.Intents.all()#for member joining/leaving

#client and bot
client = commands.Bot(command_prefix='!')

#client = discord.Client()
bot = commands.Bot(command_prefix='.', intents=intents)

#get channel_name
channel_name_for_bot  = 'verify'


#Makes sure Bot is Getting Response
@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))


#Commands -- !verify, !help, !create, 'Hello', 'Bye'
@client.event
async def on_message(message):
    msg =  message
    username = str(msg.author).split('#')[0]
    content = str(msg.content)
    channel = str(msg.channel.name)

    if message.author == client.user:
       return
    #if content.lower() == 'thanks' or content.lower() == 'thank you' or content.lower() == 'thank':
    #    await msg.channel.send(f"You Welcome {username}!")
    #    return

    if content.lower() == "help" or content.lower() == "!help":
        await msg.channel.send(f'```Step 1: Use the link to authorize the bot onto the server: https://discord.com/api/oauth2/authorize?client_id=982430908281933865&permissions=534992386160&scope=bot\nStep 2: Go to the channel where you want the bot added and click the gear icon next to the channel. Go to *Permissions* and then *Add Members and Roles*\nStep 3: Search for *Chat Bot* and Add!\nStep 4: Type !verify to begin the verification process.```')
        return
    elif content.lower() == '!verify':
        #print("Verification Sent!")
        CLIENT_ID = 'SERVER_4R3QUQRNQOSK9TOTWHD7Q2'
        cs = 'g_zsgbW00owFeQHKmfyXP7p6_iUJ9U797_iThf19AsP-jeZu7DWeGqJ.V3aLRRzm'
        headers = {'client-id': 'SERVER_4R3QUQRNQOSK9TOTWHD7Q2', 'client-secret': cs , 'Content-Type' : 'application/json' }
        response = requests.post('https://core.human-id.org/v0.0.3/server/users/web-login', headers=headers)
        #print(response.json())
        return_url = response.json()['data']['webLoginUrl']
        short_url = ps.Shortener().tinyurl.short(return_url)
         
        #print(response.json())
        await msg.channel.send(short_url)
        #URL SENT - S U C C E S S -
        #-----------------------------------------------------------------------------------------------------------
        #CLIENT_ID = '982430908281933865'
        #cs = '6fJVAg9lYw9MtrLYF0DZM-67-W_aDC6A'
        #headers = {'client-id': CLIENT_ID, 'client-secret': cs , 'Content-Type' : 'application/json' }
        #response = requests.post('https://s-api.human-id.org/v1', headers=headers)
        #you are verified
        #step 1: get backend
        #step 2: store into mysql
        print(response.json())  
        #connect to #async with aiohttp.ClientSession() as session:
        #    webhook = Webhook.from_url('url-here', session=session)
        #    await webhook.send('Hello World') 
        print("verification successful")
        #msg.author gets new role when verification is complete
        #if response.json()['success'] == True:
        #
        #print(headers)
        #response2 =  requests.post('https://core.human-id.org/v0.0.3/server/users/exchange', headers=headers)
        #return_value = response2.json()
        #print(response2.json())
        #print(return_value['success'])
        #if return_value['success'] == True:
        #    et = return_value['exchangeToken']
        #    print('http://18.225.5.208:8000/success_bot?et=' + et)
        #else:
        #    await webhook.send('Hello World') 
        #msg.author gets new role when verification is complete
        #if response.json()['success'] == True:
        #
        #print(headers)
        #response2 =  requests.post('https://core.human-id.org/v0.0.3/server/users/exchange', headers=headers)
        #return_value = response2.json()
        #print(response2.json())
        #print(return_value['success'])
        #if return_value['success'] == True:
        #    et = return_value['exchangeToken']
        #    print('http://18.225.5.208:8000/success_bot?et=' + et)
        #else:
        #    print('http://18.225.5.208:8000/success_bot?et=' + et)
        #else:
        #    print('http://18.225.5.208:8000/success_bot?et=' + et)
        #else:
        #if return_value['success'] == True:
        #    et = return_value['exchangeToken']
        #    print('http://18.225.5.208:8000/success_bot?et=' + et)
        #else:
        #    reason = str(response2.reason)
        #    reason = reason.replace(' ', '')
        #    fail_url = ('http://18.225.5.208:8000/failure_bot?code=' + str(response2.status_code) + '&message=' + reason)
        #    print(fail_url)
        #await msg.channel.send(f"https://bit.ly/3A5b5bW")
        return
    elif content.lower() == '!create':
        if  get(msg.guild.text_channels, name="verify"):
            await msg.channel.send(f"Verification Channel already created")
            return
        else:
            await msg.guild.create_text_channel('verify')
            return


# AS MEMEBER JOINS, MESSAGE DISPLAYING!
@bot.event
async def on_member_join(member):
    channel = member.guild.get_channel(983183146910634024)
    print(member.name + " has joined the server!")
    embed=discord.Embed(
            title="Welcome "+member.name+"!",
            #description="We're so glad you're here! Type !verify to begin verification process!",
            color=discord.Color.green()
            )
    await member.send("thanks for joining")
    await channel.send(member.mention, embed=embed)
            #role = discord.utils.get(member.server.roles, name="name-of-your-role") #  Gets the member role as a `role` object
    #await client.add_roles(member, role) # Gives the role to the user
    #print("Added role '" + role.name + "' to " + member.name)
    return


# AS MEMBER LEAVES, MESSAGE DISPLAYING!
@bot.event
async def on_member_remove(member):
    print(member.name + " has left the server!")
    embed=discord.Embed(
            title="Goodbye "+member.name+"!",
            #description="Until we meet again old friend.",# A description isn't necessary, you can delete this line if you don't want a description.,
            color=discord.Color.red() # check them here: https://discordpy.readthedocs.io/en/latest/api.html?highlight=discord%20color#discord.Colour
            )
    await member.send("Thank you for your service!")
    return



@client.command()
@commands.has_guild_permissions(administrator=True)
async def send_message(ctx, channel: discord.TextChannel, *, message: str):
    print("call send message function")
    await channel.send(message)
    return


#Add new role
@client.command(pass_context=True)
@commands.has_permissions(manage_roles=True)
async def addRole(self, ctx, user: discord.Member, *, role: discord.Role):
    if role in user.roles:
        print("no role added")
    else:
        await user.add_roles(role)
#    role = get(member.server.roles, name="Verified")
#   await member.add_roles(member, role)
        print("should have worked")

client.run(TOKEN)
