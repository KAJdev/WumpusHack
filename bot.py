#Imports
print('Importing Libraries')
import discord, pymongo, config, asyncio, random, dns
from discord.ext import commands

#Prefix
print('Making Bot')
bot = commands.Bot(command_prefix = config.DEFAULT_PREFIX, case_insensitive = True)

#Main cache
cache = {}

#Version
version = "2019.0.0.1a"

#Defaults
basic_pc_stats = {'ram': 1, 'cpu': 1, 'gpu': 1}
basic_network_stats = {'bandwidth': 1, 'ddos_pro': False, 'firewall': False}

#Removes the default help command
bot.remove_command("help")

#Establishes connection to MongoDB
print('Connecting to MongoDB')
mongo = pymongo.MongoClient("mongodb+srv://hytexxity:hytexxity@cluster0-7rhwq.mongodb.net/test?retryWrites=true&w=majority")
wump_db = mongo.wumpus_hack
users_col = wump_db.users
print("bot connected to database. users: " + str(users_col.count()))

#On ready
@bot.event
async def on_ready():
    print("Bot is ready and online.")
    print("servers: %s, ping: %s ms" % (len(bot.guilds), bot.latency * 1000))
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=">login | Participating in Discord Hack Week!"))

async def tick():
    await asyncio.sleep(10)
    print("tick.")
    docs = users_col.find({})
    for doc in docs:
        new_doc = { '$set': {'balance': doc['balance'] + doc['pc']['gpu']}}
        users_col.update_one(doc, new_doc)
        print('updated users')

def calc_loading(doc, base):
    load_time = base / ((doc['network']['bandwidth'] * doc['pc']['cpu']) + 1)
    return load_time

#Login
@bot.command()
async def login(ctx):
    doc = users_col.find_one({'user_id': str(ctx.author.id)})
    if doc == None:
        embed = discord.Embed(
            title = "Welcome to Wumpus Inc. family!",
            description = "`Thank you for purchasing your new Wumpus system. Your Wumpus system is the way you can communicate with the world! Your computer is started, and ready to roll! Connect to your nation's help system to get the hang of things.` (>connect help.gov)",
            color = 0x35363B
        )
        await ctx.author.send(embed=embed)
        ip = str(random.randint(1, 255) + "." + str(random.randint(1, 255)) + "." + str(random.randint(1, 255)) + "." + str(random.randint(1, 255)))
        user = {'user_id': str(ctx.author.id), 'pc': basic_pc_stats, 'network': basic_network_stats, 'online': True, 'balance': 100, 'ip': ip}
        users_col.insert_one(user)
        print('created user')
    else:
        msg = await ctx.author.send("<a:loading2:592819419604975797> `logging in`")
        their_doc = {'user_id': str(ctx.author.id)}
        insert_doc = { '$set': {'online': True} }
        new_doc = users_col.update_one(their_doc, insert_doc)
        print('User '+str(ctx.author.id)+ " is now Online")
        await asyncio.sleep(calc_loading(doc, 5))
        msg.edit(content="<:done:592819995843624961> `welcome back, %s, to your Wumpus System.`" % (str(ctx.author)))
        await ctx.author.send("```**Wumpus OS [Version "+version+"]\n(c) 2019 Discord Inc. All rights reserved.\n\nC:\\Users\\%s>**```" % (str(ctx.author)))

#Logout
@bot.command()
async def logout(ctx):
    doc = users_col.find_one({'user_id': str(ctx.author.id)})
    if doc != None:
        if doc['online'] == True:
            await ctx.send("`Saving session...`")
            their_doc = {'user_id': str(ctx.author.id)}
            insert_doc = { '$set': {'online': False} }
            new_doc = users_col.update_one(their_doc, insert_doc)
            await ctx.send("`...copying shared history...`")
            await ctx.send("`...saving history...truncating history files...`")
            await ctx.send("`...completed`")
            await ctx.send("`Deleting expired sessions... 1 Completed`")
            await ctx.send("`Saving balance... " + str(their_doc['balance']) + "`<:coin:592831769024397332>")
            await ctx.send("[process completed]")
            #Other db stuff
        else:
            await ctx.send("`your computer is not online. Please >login`")
    else:
        await ctx.send("`Please type >login to start your adventure!`")

#Invite
@bot.command()
async def invite(ctx):
    embed = discord.Embed(
        title = "**Invite Me! 🔗**",
        url = "https://discordapp.com/api/oauth2/authorize?client_id=592803813593841689&permissions=8&scope=bot",
        color = 0x7289da
    )
    await ctx.send(embed = embed)

#Support
@bot.command()
async def support(ctx):
    embed = discord.Embed(
        title = "**Support Server! 🔗**",
        url = "https://discord.gg/GC7Pw9Y",
        color = 0x7289da
    )
    await ctx.send(embed = embed)

#Help
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title = "Help",
        description = "**Login** - Logs onto your computer.\n**Logout** - Logs out of your computer.\n**Invite** - Sends a link to invite me.\n**Support** - Sends an invite link to the support server.",
        color = 0x7289da

    )
    await ctx.send(embed = embed)

@bot.command(name="590806733924859943")
async def egg(ctx):
    await ctx.send(":egg:")

#Command not found
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('"\'%s\" is not recognized as an internal or external command, operable program or batch file.`' % (ctx.message.content))

#Sets the bot token
bot.loop.create_task(tick())
bot.run(config.TOKEN)
