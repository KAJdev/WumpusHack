#Imports
print('Importing Libraries')
import discord, pymongo, config, asyncio, random, dns, json
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
game_sites=['help.gov', 'store.gov']

owner_ids = [229695200082132993, 245653078794174465, 282565295351136256]
help_string = "**__Commands__**\n**Connect** - Connects to another PC.\n**Editcm** - Edits your connection message.\n**Invite** - Sends a link to invite me.\n**Login** - Logs onto your computer.\n**Logout** - Logs out of your computer.\n**Reset** - Resets all of your stats\n**Support** - Sends an invite link to the support server.\n**System / Stats / Sys** - Shows your system information.\n\n**__Government websites__**\n**store.gov** - Shows the store."
shop_string = "**__System Upgrades__**\n**Firewall**\nCost - 5000 <:coin:592831769024397332>\n`Stops connections to your IP address.`\n`ID - FIREWALL`\n\n**DDOS Protection**\nCost - 5000 <:coin:592831769024397332>\n`Protection from DDOS attacks.`\n`ID - DDOS_PROT`\n\n**__PCs__**\n**Medium-end PC**\nCost - 10000 <:coin:592831769024397332>\n`ID - MEDIUM_PC`\n\n**High-end PC**\nCost - 20000 <:coin:592831769024397332>\n`ID - HIGH_PC`"

#Removes the default help command
bot.remove_command("help")

#Establishes connection to MongoDB
print('Connecting to MongoDB')
myclient = pymongo.MongoClient("mongodb://hytexxity:hytexxity@cluster0-shard-00-00-7rhwq.mongodb.net:27017,cluster0-shard-00-01-7rhwq.mongodb.net:27017,cluster0-shard-00-02-7rhwq.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true")
wumpdb = myclient["wumpus-hack"]
users_col = wumpdb['users']
print("bot connected to database. users: " + str(users_col.count()))



#On ready
@bot.event
async def on_ready():
    print("Bot is ready and online.")
    print("servers: %s, ping: %s ms" % (len(bot.guilds), bot.latency * 1000))
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=">login | Participating in Discord Hack Week!"))

async def tick():
    while not bot.is_closed():
        await asyncio.sleep(10)
        print("tick.")
        docs = users_col.find({})
        for doc in docs:
            if doc['online'] == False:
                print('did not update user')
                continue
            new_doc = { '$set': {'balance': doc['balance'] + doc['pc']['gpu']}}
            users_col.update_one(doc, new_doc)
            print('updated users')

def calc_loading(doc, base):
    load_time = base / ((doc['network']['bandwidth'] * doc['pc']['cpu']) + 1)
    return load_time

#Login
@bot.command()
async def login(ctx):
    if ctx.guild != None:
        await ctx.message.delete()
    doc = users_col.find_one({'user_id': str(ctx.author.id)})
    if doc == None:
        embed = discord.Embed(
            title = "Welcome to Wumpus Inc. family!",
                description = "`Thank you for purchasing your new Wumpus system. Your Wumpus system is the way you can communicate with the world! Your computer is started, and ready to roll! Connect to your nation's help system to get the hang of things.` (>connect help.gov)",
            color = 0x35363B
        )
        await ctx.author.send(embed=embed)
        an_ip = str(random.randint(1, 255)) + "." + str(random.randint(1, 255)) + "." + str(random.randint(1, 255)) + "." + str(random.randint(1, 255))
        user = {'user_id': str(ctx.author.id), 'pc': basic_pc_stats, 'network': basic_network_stats, 'online': True, 'balance': 100, 'ip': an_ip, 'connect_msg': "Hello. I am a PC."}
        print('inserting...')
        users_col.insert_one(user)
        print('created user')
    else:
        if doc['online'] == True:
            await ctx.author.send("`error: Already online.`")
            return
        msg = await ctx.author.send("<a:loading2:592819419604975797> `logging in`")
        their_doc = {'user_id': str(ctx.author.id)}
        insert_doc = { '$set': {'online': True} }
        new_doc = users_col.update_one(their_doc, insert_doc)
        print('User '+str(ctx.author.id)+ " is now Online")
        await asyncio.sleep(calc_loading(doc, 5))
        await msg.edit(content="<:done:592819995843624961> `Welcome back, %s, to your Wumpus System.`" % (str(ctx.author)))
        await ctx.author.send("**```Wumpus OS [Version "+version+"]\n(c) 2019 Discord Inc. All rights reserved.\n\nC:\\Users\\%s>```**" % (str(ctx.author)))

#Logout
@bot.command()
async def logout(ctx):
    if ctx.guild != None:
        await ctx.message.delete()
    doc = users_col.find_one({'user_id': str(ctx.author.id)})
    if doc != None:
        if doc['online'] == True:
            await ctx.author.send("`Saving session...`")
            their_doc = {'user_id': str(ctx.author.id)}
            insert_doc = { '$set': {'online': False} }
            new_doc = users_col.update_one(their_doc, insert_doc)
            await ctx.author.send("`Copying shared history...\nSaving history...truncating history files...`")
            await ctx.author.send("`Completed\nDeleting expired sessions... 1 Completed`")
            await ctx.author.send("`Saving balance... " + str(doc['balance']) + "`<:coin:592831769024397332>")
            await ctx.author.send("[process completed]")
        else:
            await ctx.author.send("`Your computer is not online. Please >login`")
    else:
        await ctx.author.send("`Please type >login to start your adventure!`")

#Connect
@bot.command()
async def connect(ctx, ip : str = None):
    if ctx.guild != None:
        await ctx.message.delete()
    user = users_col.find_one({'user_id': str(ctx.author.id)})
    if user == None:
        await ctx.author.send("`Please type >login to start your adventure!`")
        return
    if user['online'] == False:
        await ctx.author.send("`Your computer is not online. Please >login`")
        return
    if ip == None:
        await ctx.author.send("`error in command \'connect\'. An Internet Protocol Address must be provided.`")
        return
    else:
        msg = await ctx.author.send("<a:loading2:592819419604975797> `Connecting to %s`" % (ip))
        print('User '+str(ctx.author.id)+ " is now connecting to " + ip)

        await asyncio.sleep(calc_loading(user, 10))
        if ip in game_sites:
            if ip == 'help.gov':
                embed = discord.Embed(title="https://help.gov", description = help_string, color = 0x7289da)
                await msg.edit(content="<:done:592819995843624961> `You have successfully connected to %s:`" % (ip), embed=embed)
                return
            if ip == 'store.gov':
                embed = discord.Embed(
                    title = "https://store.gov",
                    description = shop_string,
                    color = 0x7289da
                )
                await msg.edit(content="<:done:592819995843624961> `You have successfully connected to %s:`" % (ip), embed=embed)
                return
        print('Waited')
        doc = users_col.find_one({'ip': ip})
        print(doc)
        if doc != None:
            if doc['online'] == False:
                await msg.edit(content="<:done:592819995843624961> `TimeoutError: Server did not respond.`")
            else:
                await msg.edit(content="<:done:592819995843624961> `You have successfully connected to %s:`" % (ip))
                await ctx.author.send("```" + doc['connect_msg'] + "```")
                cache[str(ctx.author.id)] = {'status': True, 'type': 1, 'host': ip}
                try:
                    host_user = discord.utils.get(bot.get_all_members(), id=int(doc['user_id']))
                    print(host_user)
                    if host_user != None:
                        await host_user.send("`LOG: user "+ str(ctx.author) + "("+doc['ip']+") has connected to your network.`")
                        print('sent msg')
                except Exception as e:
                    print(e)
        else:
            await msg.edit(content="<:done:592819995843624961> `TimeoutError: Server did not respond.`")

#System
@bot.command(aliases=['sys', 'stats'])
async def system(ctx):
    if ctx.guild != None:
        await ctx.message.delete()

    doc = users_col.find_one({'user_id': str(ctx.author.id)})
    if doc == None:
        await ctx.author.send("`Please type >login to start your adventure!`")
        return
    else:
        try:
            embed = discord.Embed(
                title = "System Information",
                description = "**__Computer Information__**\n**Ram** - "+str(doc['pc']['ram'])+ "GB\n **CPU** - "+str(doc['pc']['ram'])+" GHz\n **GPU** - "+str(doc['pc']['gpu'])+" GHz\n\n**__Network Information__**\n**Bandwith** - "+str(doc['network']['bandwidth'] + 10   )+" Mbps\n**DDOS Protection** - "+str(doc['network']['ddos_pro'])+"\n **Firewall** - "+str(doc['network']['firewall'])+"\n**IP Address** - ||"+doc['ip']+"||\n\n**__Other Information__**\n**Balance** - "+str(doc['balance'])+" <:coin:592831769024397332>\n**Connection Message** - "+doc['connect_msg'],
                color = 0x7289da
            )
        except Exception as e:
            print(e)
        msg = await ctx.author.send("<a:loading2:592819419604975797> `Obtaining system information...`")
        await asyncio.sleep(calc_loading(doc, 5))
        await msg.edit(content="<:done:592819995843624961> `System information retreived`", embed=embed)

#Edit connection message
@bot.command()
async def editcm(ctx, *, message = None):
    if message == None:
        await ctx.send("`You have not sent a replacement connection message!`")
    else:
        user = users_col.find_one({'user_id': str(ctx.author.id)})
        if user == None:
            await ctx.author.send("`Please type >login to start your adventure!`")
            return
        if user['online'] == False:
            await ctx.author.send("`Your computer is not online. Please >login`")
            return
        else:
            users_col.update_one({'user_id': str(ctx.author.id)}, { '$set': {'connect_msg': message }})
            await ctx.send("`Updated connection message: %s`" % (message))


#Invite
@bot.command()
async def invite(ctx):
    embed = discord.Embed(
        title = "**Invite Me! 🔗**",
        url = "https://discordapp.com/api/oauth2/authorize?client_id=592803813593841689&permissions=8&scope=bot",
        color = 0x7289da
    )
    await ctx.send(embed = embed)

#Cache
@bot.command()
async def _cache(ctx):
    print(cache)

#Support
@bot.command()
async def support(ctx):
    embed = discord.Embed(
        title = "**Support Server! 🔗**",
        url = "https://discord.gg/GC7Pw9Y",
        color = 0x7289da
    )
    await ctx.send(embed = embed)


#Give
@bot.command(aliases = ["set-coins", "set_coins", "give_coins", "take-coins"])
async def give(ctx, user : discord.User = None, amount = None):
    if ctx.author.id not in owner_ids:
        return
    if user == None:
        user = ctx.author
    if amount == None:
        amount = 1

    doc = users_col.find({'user_id': str(user.id)})
    if doc == None:
        await ctx.send("wtf who is that nerd. couldn't find him. you loser")
        return

    new_doc = { '$set': {'balance': doc['balance'] + amount}}
    users_col.update_one(doc, new_doc)
    if amount < 0:
        await ctx.send("Nom nom nom, Wumpus ate some of %s's coins, they have %s coins now. They used to have %s coins but Wumpus was hungry." % (user.name, str(doc['balance'] + amount)), str(doc['balance']))
        return
    elif amount > 0:
        await ctx.send("*Blech*, Wumpus threw up his left over coins. %s picked them up. They have %s coins now. They used to have %s coins but Wumpus didn't feel good." % (user.name, str(doc['balance'] + amount)), str(doc['balance']))
        return

#Reset
@bot.command()
async def reset(ctx, user : discord.User = None):
    if user == None or ctx.author.id not in owner_ids:
        user = ctx.author
    await ctx.send("`Are you sure you would like to reset?\nReseting will reset all of your stats [Y/N]`")
    try:
        while True:
            msg = await bot.wait_for('message', timeout= 10)
            if "y" == msg.content.lower and msg.author.id == ctx.author.id:
                users_col.delete_one({'user_id': str(user.id)})
                an_ip = str(random.randint(1, 255)) + "." + str(random.randint(1, 255)) + "." + str(random.randint(1, 255)) + "." + str(random.randint(1, 255))
                users_col.insert_one({'user_id': str(user.id), 'pc': basic_pc_stats, 'network': basic_network_stats, 'online': True, 'balance': 100, 'ip': an_ip, 'connect_msg': "Hello. I am a PC."})
                await ctx.send("`"+str(user) + "'s systems have been re-imaged.`")
                break
            elif "n" == msg.content.lower and msg.author.id == ctx.author.id:
                await ctx.send("`Reset canceled.`")
                break
            else:
                continue


    except Exception as e:
        print(e)
        await message.delete()
        await ctx.send("`No reply recived. Prompt expired.`")
        return

#Block
@bot.command()
async def block(ctx, user = discord.User):
    if ctx.author.id not in owner_ids:
        return
    if user == None:
        await ctx.send("`wtf who is that nerd. couldn't find him. you loser`")

#Shop
@bot.command(aliases=['store'])
async def shop(ctx):
    embed = discord.Embed(
        embed = "Shop",
        description = shop_string,
        color = 0x7289da
    )
    await ctx.send(embed = embed)


#Help
@bot.command()
async def help(ctx):
    embed = discord.Embed(
    title = "Help",
    description = help_string,
    color = 0x7289da

    )
    await ctx.send(embed = embed)

#Command not found
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('`"\'%s\" is not recognized as an internal or external command, operable program or batch file.`' % (ctx.message.content))

#Sets the bot token
bot.loop.create_task(tick())
bot.run(config.TOKEN)
