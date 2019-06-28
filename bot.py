#Imports
print('Importing Libraries')
import discord, pymongo, config, asyncio, random, dns, json, math, time, importlib
before_startup = time.time()
from discord.ext import commands
from datetime import datetime
from pytrivia import Category, Diffculty, Type, Trivia

Trivia = Trivia(True)

#Prefix
print('Making Bot')
bot = commands.Bot(command_prefix = config.DEFAULT_PREFIX, case_insensitive = True)

#Main cache
cache = {'away': {}}

#Version
version = "2019.2.1.0b"

#tick counter
tick_number = 0

#Defaults
basic_pc_stats = {'ram': 1, 'cpu': 1, 'gpu': 1, 'cpu_name': "Intel Atom", 'gpu_name': "Integrated Graphics"}
basic_network_stats = {'bandwidth': 1, 'ddos_pro': False, 'firewall': False}
game_sites=['help.gov', 'store.gov', '0.0.0.1', 'mail.gov']#

#categories
categories = [Category.Maths, Category.Computers]
#difficulties
difficulties = [Diffculty.Easy, Diffculty.Medium, Diffculty.Hard]

owner_ids = [229695200082132993, 245653078794174465, 282565295351136256]
help_string = "Welcome to help.gov. Here you can find a list of commands you can use on your WumpusOS system.\n**__Commands__**\n**Connect** - Connects to another PC.\n**Disonnect** - Disconnects from another PC.\n**system editcm <msg>** - Edits your connection message.\n**Github** - Sends a link to the github repository.\n**Invite** - Sends a link to invite me.\n**Login** - Logs onto your computer.\n**Logout** - Logs out of your computer.\n**Reset** - Resets all of your stats\n**Support** - Sends an invite link to the support server.\n**Breach / Hack** - Breach into someones computer/system.\n**Print** - Print a message in your computers log.\n**System / Stats / Sys** - Shows your system information.\n\n**__Government websites__**\n**store.gov** - buy and upgrade your pc!\n**help.gov** - this network.\n**mail.gov** - see your inbox, and send messages."
shop_string = "**__Network Upgrades__**\n**Firewall**\nCost - 50000 <:coin:592831769024397332>\n`Temporary 12 Hour Firewall blocking all connecions.`\n`ID - 1`\n\n**DDOS Protection**\nCost - 80000 <:coin:592831769024397332>\n`Adds extra time on math problems.`\n`ID - 2`\n\n**Bandwidth**\nCost - 1000 <:coin:592831769024397332>\n`Improves loading times and breach times.`\n`ID - 3`\n\n**__PC Upgrades__**\n**CPU**\nCost - 500 <:coin:592831769024397332>\n`Improves your CPU's Ghz by .5`\n`ID - 4`\n\n**GPU**\nCost - 600 <:coin:592831769024397332>\n`Improves your GPU's Ghz by .3`\n`ID - 5`\n\n**RAM**\nCost - 500 <:coin:592831769024397332>\n`Improves RAM by 1GB`\n`ID - 6`"

shop_items = [{'name': "GTX 1060", 'type': 'gpu', 'system': 5, 'cost': 5000}, {'name': "AMD Athlon II X3", 'type': 'cpu', 'system': 2, 'cost': 1500}, {'name': "Intel core i3", 'type': "cpu", 'system': 4, 'cost': 1500}, {'name': "4GB RAM Stick", 'type': 'ram', 'system': 4, 'cost': 4000}, {'name': "8GB RAM Stick", 'type': 'ram', 'system': 8, 'cost': 9000}, {'name': "16GB RAM Stick", 'type': 'ram', 'system': 16, 'cost': 20000}, {'name': "Intel core i5", 'type': "cpu", 'system': 5, 'cost': 3500}, {'name': "Intel core i7", 'type': "cpu", 'system': 6, 'cost': 5000}, {'name': "Intel Xeon", 'type': "cpu", 'system': 9, 'cost': 20000}, {'name': "AMD Threadripper", 'type': "cpu", 'system': 9, 'cost': 19000}, {'name': "AMD Radeon RX 580", 'type': 'gpu', 'system': 6, 'cost': 14000}, {'name': "Nvidia GeForce GTX 1070", 'type': 'gpu', 'system': 7, 'cost': 17000}, {'name': "Nvidia GeForce RTX 2080 Ti", 'type': 'gpu', 'system': 10, 'cost': 25000}]

#embed=discord.Embed(title="`system connection status`", description="`234.56.432.523 has started an attack on your system.`")
#embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/591894598234800158/592847649481424896/Discord.png")
#embed.set_footer(text="Art made by Kiwi#6666")
#await ctx.send(embed=embed)


#Removes the default help command
bot.remove_command("help")

#Establishes connection to MongoDB
print('Connecting to MongoDB')
myclient = pymongo.MongoClient(config.URI)
wumpdb = myclient["wumpus-hack"]
users_col = wumpdb['users']
mail_col = wumpdb['mail']
print("bot connected to database. users: " + str(users_col.count()))


def get_day_of_year():
    return datetime.now().timetuple().tm_yday


def get_all_connections_to(host):
    connections = []
    for key, value in cache.items():
        if key == 'away':
            continue
        else:
            if value['host'] == host:
                mem = discord.utils.get(bot.get_all_members(), id=int(key))
                if mem != None:
                    connections.append(mem)
    return connections

#checks on firewall timer
async def check_timer_firewall():
    #get all documents from db
    docs = users_col.find({})
    right_now = time.time()
    updated_docs = 0
    for doc in docs:
        # check if firewall timer isnt over (False == no timer)
        if doc['network']['firewall'] != False:
            updated_docs += 1
            expire = float(doc['network']['firewall'])

            # if the firewall time (timestamp) is less than right now
            if expire <= time.time():
                #set network to be false, so it is not check against
                doc['network']['firewall'] = False
                # update document is DB
                users_col.update_one({'user_id': doc['user_id']}, {'$set':{'network': doc['network']}})

                #get user and send message
                member = discord.utils.get(bot.get_all_members(), id=int(doc['user_id']))
                if member != None:
                    await member.send("`LOG: Firewall has been disabled. ports are now unportected.`")


    difference = time.time() - right_now
    print("updated %s firewall cooldown docs in %s seconds" % (str(updated_docs), str(round(difference, 1))))


@bot.command()
async def reload(ctx):
    importlib.reload(config)


#checks on breach cooldown timer
async def check_timer_breach_cooldown():
    #get all documents from db
    docs = users_col.find({})
    right_now = time.time()
    updated_docs = 0
    for doc in docs:
        # check if breach timer isnt over (False == no timer)
        if doc['breach'] != False:
            updated_docs += 1
            expire = float(doc['breach'])

            # if the breach cooldown time (timestamp) is less than right now
            if expire <= time.time():
                #set network to be false, so it is not check against and update document is DB
                users_col.update_one({'user_id': doc['user_id']}, {'$set':{'breach': False}})

                #get user and send message
                member = discord.utils.get(bot.get_all_members(), id=int(doc['user_id']))
                if member != None:
                    await member.send("`LOG: Breach cooldown disabled.`")


    difference = time.time() - right_now
    print("updated %s breach cooldown docs in %s seconds" % (str(updated_docs), str(round(difference, 1))))

#@bot.event
#async def on_member_update(before, after):
#    if before.status != after.status:
#        if str(after.status) == "offline":
#            if str(after.id) not in cache['away']:
#                doc = users_col.find_one({'user_id': str(after.id)})
#                if doc != None:
#                    cache['away'][str(after.id)] = doc['balance']
#                    print("cached " + str(after))
#
#        elif str(before.status) == 'offline':
#            if str(after.id) in cache['away']:
#                doc = users_col.find_one({'user_id': str(after.id)})
#                if doc != None:
#                    difference = doc['balance'] - cache['away'][str(after.id)]
#                    if difference < 26:
#                       return
#                    del cache['away'][str(after.id)]
#                    embed = discord.Embed(
#                        title = "Report",
#                            description = "Actions have taken place since you were away.\nYou have gained %s <:coin:592831769024397332>." % (difference),
#                        color = 0x35363B
#                    )
#                   if doc['online'] == True:
#                        await after.send(embed=embed)
#                    print(str(after) + " woke up")


@bot.command()
async def ping(ctx):
    embed=embed = discord.Embed(
        title = '🏓 PONG 🏓',
        description = "{0} ms".format(round(bot.latency * 1000, 1)),
        color = 0x7289da
    )
    await ctx.send(embed=embed)

#On ready
@bot.event
async def on_ready():
    await bot.user.edit(username="WumpOS Terminal v"+version)
    if bot != None:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Bot starting..."))
    #print("caching users... ")
    #for member in bot.get_all_members():
    #    if str(member.status) == 'offline':
    #        doc = users_col.find_one({'user_id': str(member.id)})
    #        if doc != None:
    #            if str(member.id) not in cache['away']:
    #                cache['away'][str(member.id)] = doc['balance']
    #                print("cached " + str(member))
    print("Bot is ready and online.")
    print("servers: %s, ping: %s ms, startup time: %s seconds" % (len(bot.guilds), bot.latency * 1000, str(round(time.time() - before_startup, 2))))


@bot.event
async def on_guild_join(guild):
    await guild.me.edit(nick="WumpusHack")
    print("WumpusHack Joined "+ str(guild))

def mine():
    before = time.time()
    docs = users_col.find({})
    updated_count = 0
    for doc in docs:
        if doc['online'] == False:
            continue
        new_doc = { '$set': {'balance': doc['balance'] + doc['pc']['gpu']}}
        users_col.update_one(doc, new_doc)
        updated_count += 1

    difference = time.time() - before
    print("Updated %s online users in %s seconds" % (updated_count, str(round(difference, 1))))


async def tick():
    await asyncio.sleep(5)
    while not bot.is_closed():
        await asyncio.sleep(config.TICK_SPEED)
        before = time.time()
        global tick_number
        tick_number += 1
        print("TICK " + str(tick_number))
        if bot != None:
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=">login | %s users online | Tick %s" % (users_col.find({'online': True}).count(), str(tick_number))))

        mine()
        await check_timer_firewall()
        await check_timer_breach_cooldown()
        if round(time.time() - before, 1) > 5:
            print("ERROR | Tick took too long (%s seconds)" % (str(round(time.time() - before, 1))))
        print("")


#Calculates Loading for Stuff
def calc_loading(doc, base):
    load_time = base / ((doc['network']['bandwidth'] * doc['pc']['cpu']) + 1)
    return load_time

#calculates time for trivia questions
def calc_time(doc):
    specs = (doc['pc']['cpu'] + doc['pc']['ram'] + doc['pc']['gpu'])
    if doc['network']['ddos_pro'] == True:
        if specs >= 25:
            return 35
        if specs < 25 and specs > 15:
            return 30
        if specs < 15 and specs > 3:
            return 20
        if specs < 5 and specs > 3:
            return 15
    if doc['network']['ddos_pro'] == False:
        if specs >= 25:
            return 30
        if specs < 25 and specs > 15:
            return 25
        if specs < 15 and specs > 3:
            return 15
        if specs < 5 and specs > 3:
            return 10


#Login
@bot.command()
async def login(ctx):
    if ctx.guild != None:
        await ctx.message.delete()
    doc = users_col.find_one({'user_id': str(ctx.author.id)})
    if doc == None:
        if str(ctx.author.id) in cache.keys():
            del cache[str(ctx.author.id)]
        embed = discord.Embed(
            title = "Welcome to Wumpus Inc. family!",
                description = "`Thank you for purchasing your new Wumpus system. Your Wumpus system is the way you can communicate with the world! Your computer is started, and ready to roll! Connect to your nation's help system to get the hang of things.` (>connect help.gov)",
            color = 0x35363B
        )
        await ctx.author.send(embed=embed)
        an_ip = str(random.randint(1, 255)) + "." + str(random.randint(1, 255)) + "." + str(random.randint(1, 255)) + "." + str(random.randint(1, 255))
        user = {'user_id': str(ctx.author.id), 'pc': basic_pc_stats, 'network': basic_network_stats, 'online': True, 'balance': 100, 'ip': an_ip, 'connect_msg': "Hello. I am a PC.", 'breach': False, 'email': ctx.author.name.lower() + "@hackweek.com", 'notify': False}
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

#Logout bs
@bot.command()
async def logout(ctx):
    if ctx.guild != None:
        await ctx.message.delete()
    doc = users_col.find_one({'user_id': str(ctx.author.id)})
    if doc != None:
        if doc['online'] == True:
            if str(ctx.author.id) in cache.keys():
                if cache[str(ctx.author.id)]['type'] == 4:
                    await ctx.author.send("<:bad:593862973274062883> `PermissionError: Invalid permissions for this action`")
                    return

            await ctx.author.send("`Saving session...`")
            their_doc = {'user_id': str(ctx.author.id)}
            insert_doc = { '$set': {'online': False} }
            new_doc = users_col.update_one(their_doc, insert_doc)
            await ctx.author.send("`Copying shared history...\nSaving history...truncating history files...`")
            await ctx.author.send("`Completed\nDeleting expired sessions... 1 Completed`")

            #if our buddy is connected to anyone
            if str(ctx.author.id) in cache.keys():
                #grab his connection from cache
                outgoing = cache[str(ctx.author.id)]
                #if the type is to another PC
                if outgoing['type'] == 1:
                    #grab the profile of the person our buddy is connected to
                    host_doc = users_col.find_one({'ip':outgoing['host']})
                    if host_doc != None:
                        #grab the member object of the person our buddy is connected to
                        host_user = discord.utils.get(bot.get_all_members(), id=int(host_doc['user_id']))
                        if host_user != None:
                            #check to make sure that our buddy isn't connected to himself
                            if host_user.id != ctx.author.id:
                                #send dc message to person, and remove connection from cache
                                await host_user.send("`LOG: user "+ str(ctx.author) + " ("+doc['ip']+") has disconnected from your network.`")
                                del cache[str(ctx.author.id)]

            #get a list of connections to our buddy typing >logout
            connections = get_all_connections_to(doc['ip'])
            for connection in connections:
                print(str(connection))
                #send dc msg to each person connected to our buddy
                await connection.send("`LOG: Lost connection to "+doc['ip']+"`")
                #remove each connection from our buddy
                del cache[str(connection.id)]

            await ctx.author.send("`Saving balance... " + str(doc['balance']) + "`<:coin:592831769024397332>")
            await ctx.author.send("[process completed]")
            print(str(ctx.author.id) + " is now offline")
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
        await ctx.author.send("<:bad:593862973274062883> `error in command \'connect\'. An Internet Protocol Address must be provided.`")
        return
    if str(ctx.author.id) in cache.keys():
        await ctx.author.send("<:bad:593862973274062883> `PortBindError: Port already in use. Use >disconnect to free up a port.`")
        return
    if user['ip'] == ip:
        await ctx.author.send("<:bad:593862973274062883> `PortBindError: Port already in use. Cannot connect to localhost:21.`")
        return
    else:
        msg = await ctx.author.send("<a:loading2:592819419604975797> `Connecting to %s`" % (ip))
        print('User '+str(ctx.author.id)+ " is now connecting to " + ip)

        await asyncio.sleep(calc_loading(user, 20))
        if ip in game_sites:
            if ip == 'help.gov':
                embed = discord.Embed(title="https://help.gov", description = help_string, color = 0x7289da)
                await msg.edit(content="<:done:592819995843624961> `You have successfully connected to %s:`" % (ip), embed=embed)
                cache[str(ctx.author.id)] = {'status': True, 'type': 2, 'host': ip}
                return
            if ip == 'store.gov':
                shop_string = "Welcome to the shop! Here you can buy PC upgrades, and more!\nThe stock changes every day, so make sure to come back tomorrow!\nYour balance - %s <:coin:592831769024397332>\n\n**Firewall**\nA temporary way to prevent connections and scans.\ncost: 10000 <:coin:592831769024397332> per hour\n`>purchase firewall`\n\n" % (user['balance'])
                random.seed(get_day_of_year())
                items = random.sample(shop_items, 5)
                for item in items:
                    shop_string = shop_string + "**%s**\n%s - %s\ncost: %s <:coin:592831769024397332>\n`>purchase %s`\n\n" % (item['name'], item['type'], str(item['system']), str(item['cost']), item['name'])

                embed = discord.Embed(
                    title = "https://store.gov",
                    description = shop_string,
                    color = 0x7289da
                )
                await msg.edit(content="<:done:592819995843624961> `You have successfully connected to %s:`" % (ip), embed=embed)
                cache[str(ctx.author.id)] = {'status': True, 'type': 2, 'host': ip}
                return
            if ip == 'mail.gov':
                email = user['email']
                mail_string = "Hi, this is mail.gov, Here you can see your inbox, and send messages. \nUse the `>send <email> <message>` command to send an email!\n\n**inbox for %s**\n```" % (email)
                mails = mail_col.find({'to': email})
                if mails.count() < 1:
                    mail_string = mail_string + "\nYour inbox is empty :)\n"
                else:
                    for mail in mails:
                        mail_string = mail_string + "To: " + mail['to'] +"\nFrom: " + mail['from'] + "\n" + mail['content'] +"\n\n"

                embed = discord.Embed(
                    title = "https://mail.gov",
                    description = mail_string + "```\n\nuse `>clear` to clear your inbox of messages, and `>inbox` to show it again.",
                    color = 0x7289da
                )
                await msg.edit(content="<:done:592819995843624961> `You have successfully connected to %s:`" % (ip), embed=embed)
                cache[str(ctx.author.id)] = {'status': True, 'type': 2, 'host': ip}
                return
            if ip == '0.0.0.1':
                embed = discord.Embed(
                    title = "Discord Hack Week",
                    description = "Thank You so much Discord Hack week for making this be possible.\nWe couldn't have done it withough you!",
                    color = 0x7289da
                )
                await msg.edit(content="<:done:592819995843624961> `You have successfully connected to %s`" % (ip), embed = embed)
                cache[str(ctx.author.id)] = {'status': True, 'type': 2, 'host': ip}
                return
        doc = users_col.find_one({'ip': ip})
        if doc != None:
            test_member = discord.utils.get(bot.get_all_members(), id=int(doc['user_id']))
            if test_member == None:
                await msg.edit(content="<:bad:593862973274062883> `TimeoutError: Server did not respond.`")
                return

            if doc['online'] == False:
                await msg.edit(content="<:done:592819995843624961> `TimeoutError: Server did not respond.`")
                return
            elif doc['network']['firewall'] != False:
                await msg.edit(content="<:done:592819995843624961> `PacketRefusal: packets have been blocked by firewall.`")
                return
            else:
                await msg.edit(content="<:done:592819995843624961> `You have successfully connected to %s:`" % (ip))
                await ctx.author.send("```" + doc['connect_msg'] + "```")
                cache[str(ctx.author.id)] = {'status': True, 'type': 1, 'host': ip}
                try:
                    host_user = discord.utils.get(bot.get_all_members(), id=int(doc['user_id']))
                    connecting_user = users_col.find_one({'user_id': str(ctx.author.id)})
                    if host_user != None:
                        await host_user.send("`LOG: user "+ str(ctx.author) + " ("+connecting_user['ip']+") has connected to your network.`")
                except Exception as e:
                    print(e)
        else:
            await msg.edit(content="<:bad:593862973274062883> `TimeoutError: Server did not respond.`")

@bot.command(aliases=['dc'])
async def disconnect(ctx):
    user = users_col.find_one({'user_id': str(ctx.author.id)})
    if user == None:
        await ctx.author.send("`Please type >login to start your adventure!`")
        return
    elif str(ctx.author.id) in cache.keys():
        if cache[str(ctx.author.id)]['type'] == 4:
            await ctx.author.send("<:bad:593862973274062883> `PermissionError: Invalid permissions for this action`")
            return

        await ctx.author.send("<:done:592819995843624961> `Disconnected from host %s`" % (cache[str(ctx.author.id)]['host']))

        doc = users_col.find_one({'ip': cache[str(ctx.author.id)]['host']})
        if doc != None:
            host_user = discord.utils.get(bot.get_all_members(), id=int(doc['user_id']))
            connecting_user = users_col.find_one({'user_id': str(ctx.author.id)})
            if host_user != None:
                await host_user.send("`LOG: user "+ str(ctx.author) + " ("+connecting_user['ip']+") has disconnected from your network.`")

        del cache[str(ctx.author.id)]
        return
    else:
        await ctx.author.send("<:bad:593862973274062883> `SocketError: Not connected to any network.`")
        return

@bot.command(aliases=['scrape'])
async def scan(ctx):
    user = users_col.find_one({'user_id': str(ctx.author.id)})
    if user == None:
        await ctx.author.send("`Please type >login to start your adventure!`")
        return
    if user['online'] == False:
        await ctx.author.send("`Your computer is not online. Please >login`")
        return
    if str(ctx.author.id) in cache.keys():
        await ctx.author.send("<:bad:593862973274062883> `PortBindError: Port already in use. Use >disconnect to free up a port.`")
        return

    time_ = calc_loading(user, 600)
    msg = await ctx.author.send("<a:loading2:592819419604975797> `scraping for IP addresses. (this will take around %s minutes)`" % round(time_ / 60))

    cache[str(ctx.author.id)] = {'status': True, 'type': 3, 'host': "using network card to scan for IPs"}
    await asyncio.sleep(time_)
    if str(ctx.author.id) not in cache.keys():
        return
    del cache[str(ctx.author.id)]
    if random.randint(1, 5) == 2:
         await msg.edit(content="<:done:592819995843624961> `Scrape returned (0) addresses`")
         return

    all_docs = users_col.find({})
    doc = None
    while True:
        doc = users_col.find({'online': True})
        doc = doc[random.randrange(doc.count()) - 1]
        if doc['user_id'] == user['user_id']:
            continue
        else:
            break
    await msg.edit(content="<:done:592819995843624961> `Scrape returned (1) address: %s`" % (doc['ip']))
    host_user = discord.utils.get(bot.get_all_members(), id=int(doc['user_id']))
    if host_user != None:
        await host_user.send("`LOG: recived ping from host "+user['ip']+"`")



@bot.command()
async def inbox(ctx):
    user = users_col.find_one({'user_id': str(ctx.author.id)})
    if user['online'] == False:
        await ctx.author.send("`Your computer is not online. Please >login`")
        return
    elif str(ctx.author.id) not in cache:
        raise commands.CommandNotFound
        return
    elif cache[str(ctx.author.id)]['host'] != 'mail.gov':
        raise commands.CommandNotFound
        return

    elif ctx.guild != None:
        await ctx.message.delete()
    elif user == None:
        await ctx.author.send("`Please type >login to start your adventure!`")
        return
    elif user['online'] == False:
        await ctx.author.send("`Your computer is not online. Please >login`")
        return
    elif str(ctx.author.id) not in cache:
        await ctx.author.send("<:bad:593862973274062883> `SocketError: Not connected to Network`")
        return
    else:
        #send inbox
        email = user['email']
        mail_string = "Hi, this is mail.gov, Here you can see your inbox, and send messages. \nUse the `>send <email> <message>` command to send an email!\n\n**inbox for %s**\n```" % (email)
        mails = mail_col.find({'to': email})
        if mails.count() < 1:
            mail_string = mail_string + "\nYour inbox is empty :)\n"
        else:
            for mail in mails:
                mail_string = mail_string + "To: " + mail['to'] +"\nFrom: " + mail['from'] + "\n" + mail['content'] +"\n\n"

        embed = discord.Embed(
            title = "https://mail.gov",
            description = mail_string + "```\n\nuse `>clear` to clear your inbox of messages",
            color = 0x7289da
        )
        await ctx.author.send(embed=embed)




@bot.command()
async def clear(ctx):
    user = users_col.find_one({'user_id': str(ctx.author.id)})
    if user['online'] == False:
        await ctx.author.send("`Your computer is not online. Please >login`")
        return
    elif str(ctx.author.id) not in cache:
        raise commands.CommandNotFound
        return
    elif cache[str(ctx.author.id)]['host'] != 'mail.gov':
        raise commands.CommandNotFound
        return

    elif ctx.guild != None:
        await ctx.message.delete()
    elif user == None:
        await ctx.author.send("`Please type >login to start your adventure!`")
        return
    elif user['online'] == False:
        await ctx.author.send("`Your computer is not online. Please >login`")
        return
    elif str(ctx.author.id) not in cache:
        await ctx.author.send("<:bad:593862973274062883> `SocketError: Not connected to Network`")
        return
    else:
        await ctx.author.send("`LOG: (mail.gov) Are you sure you want toclear your inbox? Respond with `Y` or `N")
        while True:
            msg = await bot.wait_for('message')
            if msg.content.lower() == "y" and msg.author.id == ctx.author.id:
                mails = mail_col.find({'to': user['email']})
                if mails.count() > 0:
                    mail_col.delete_many({'to': user['email']})

                    #send inbox again
                    email = user['email']
                    mail_string = "Hi, this is mail.gov, Here you can see your inbox, and send messages. \nUse the `>send <email> <message>` command to send an email!\n\n**inbox for %s**\n```" % (email)
                    mails = mail_col.find({'to': email})
                    if mails.count() < 1:
                        mail_string = mail_string + "\nYour inbox is empty :)\n"
                    else:
                        for mail in mails:
                            mail_string = mail_string + "To: " + mail['to'] +"\nFrom: " + mail['from'] + "\n" + mail['content'] +"\n\n"

                    embed = discord.Embed(
                        title = "https://mail.gov",
                        description = mail_string + "```\n\nuse `>clear` to clear your inbox of messages",
                        color = 0x7289da
                    )
                    await ctx.author.send("`LOG: (mail.gov) you have cleared your inbox!`", embed=embed)
                    return
                else:
                    await ctx.author.send("`LOG: (mail.gov) You do not have any mail in your inbox.`")
                    return

            elif msg.content.lower() == 'n' and msg.author.id == ctx.author.id:
                await ctx.author.send("`LOG: (mail.gov) purge canceled.`")
                break
            else:
                continue


@bot.command()
async def send(ctx, mail_to:str=None, *, msg:str=None):
    user = users_col.find_one({'user_id': str(ctx.author.id)})
    if user['online'] == False:
        await ctx.author.send("`Your computer is not online. Please >login`")
        return
    if str(ctx.author.id) not in cache:
        raise commands.CommandNotFound
        return
    elif cache[str(ctx.author.id)]['host'] != 'mail.gov':
        raise commands.CommandNotFound
        return

    if ctx.guild != None:
        await ctx.message.delete()
    if user == None:
        await ctx.author.send("`Please type >login to start your adventure!`")
        return
    if user['online'] == False:
        await ctx.author.send("`Your computer is not online. Please >login`")
        return
    if str(ctx.author.id) not in cache:
        await ctx.author.send("<:bad:593862973274062883> `SocketError: Not connected to Network`")
        return
    elif mail_to == None:
        await ctx.author.send("`LOG: (mail.gov) Please specify an email to send to`")
        return
    elif msg == None:
        await ctx.author.send("`LOG: (mail.gov) Please specify a message to send`")
        return
    else:
        reciver = users_col.find_one({'email': mail_to})
        if reciver != None:
            email = user['email']
            mail_doc = {'to': mail_to, 'from': email, 'content': msg}
            mail_col.insert_one(mail_doc)
            await ctx.author.send("`LOG: (mail.gov) email has been sent.`")
            recivernotif = reciver['notify']
            if recivernotif == False:
                return
            else:
                emailperson = discord.utils.get(bot.get_all_members(), id= int(reciver['user_id']))
                if emailperson != None:
                    await emailperson.send("`LOG: (mail.gov) You've Got Mail`")
        else:
            await ctx.author.send("`LOG: (mail.gov) email does not exist`")



@bot.event
async def on_message(message):
    if message.content.startswith(">"):
        print("Command: " + message.content)
    await bot.process_commands(message)


@bot.command()
async def purchase(ctx, *, id:str=None):
    user = users_col.find_one({'user_id': str(ctx.author.id)})
    if user['online'] == False:
        await ctx.author.send("`Your computer is not online. Please >login`")
        return
    if str(ctx.author.id) not in cache:
        raise commands.CommandNotFound
        return
    elif cache[str(ctx.author.id)]['host'] != 'store.gov':
        raise commands.CommandNotFound
        return

    member = ctx.author

    random.seed(get_day_of_year())
    items = random.sample(shop_items, 5)

    if ctx.guild != None:
        await ctx.message.delete()
    if user == None:
        await ctx.author.send("`Please type >login to start your adventure!`")
        return
    if user['online'] == False:
        await ctx.author.send("`Your computer is not online. Please >login`")
        return
    if str(ctx.author.id) not in cache:
        await ctx.author.send("<:bad:593862973274062883> `SocketError: Not connected to Network`")
        return
    elif id == None:
        await ctx.author.send("`LOG: (store.gov) Please specify an ID to purchase`")
        return

    # check to see if the Item they specified is in today's list of items
    elif any(d['name'] == id for d in items):

        # grab that item object
        item = None
        for i in items:
            if i['name'] == id:
                item = i
        if item == None:
            await ctx.author.send("`LOG: (store.gov) unknown error occured when finding item.")
            return

        await ctx.author.send("`LOG: (store.gov) Are you sure you want to purchase this item? Respond with `Y` or `N")

        #start loop
        while True:
            msg = await bot.wait_for('message')
            if msg.content.lower() == "y" and msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id:
                # check for enough cash
                if user['balance'] >= item['cost']:
                    # create a new PC dict
                    new_pc = {'cpu': user['pc']['cpu'], 'ram': user['pc']['ram'], 'gpu': user['pc']['gpu'], 'gpu_name': user['pc']['gpu_name'], 'cpu_name': user['pc']['cpu_name']}

                    #replace the items modifying type with what the user bought
                    new_pc[item['type']] = item['system']
                    new_pc[item['type']+'_name'] = item['name']

                    # pdate the document in the database
                    users_col.update_one({'user_id': str(ctx.author.id)}, {'$set':{'balance': user['balance'] - item['cost'], 'pc': new_pc}})

                    #send confirmation message
                    await ctx.author.send("`LOG: (store.gov) You have just purchased `" + id + "` for " + str(item['cost']) + "<:coin:592831769024397332>!")
                    return
                else:
                    await ctx.author.send("`LOG: (store.gov) Insufficient balance.`")
                    return

            elif msg.content.lower() == 'n' and msg.author.id == ctx.author.id:
                await ctx.author.send("`LOG: (store.gov) Purchase canceled.`")
                break
            else:
                continue
    else:
        if id == 'firewall':
            await ctx.author.send("`LOG: (store.gov) Are you sure you want to purchase this item? Respond with `Y` or `N")

            #start loop
            while True:
                msg = await bot.wait_for('message')
                if msg.content.lower() == "y" and msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id:
                    # check for enough cash
                    if user['balance'] >= 10000:

                        # create a new NET dict
                        new_network = user['network']

                        #check if there is already a timer started, if so, add one hour to existing timer.
                        if new_network['firewall'] != False:
                            new_network['firewall'] = float(new_network['firewall']) + 3600

                        else:
                            #otherwise, just add a timer oh 1 hour.
                            new_network['firewall'] = str(time.time() + 3600)

                        #update dict in databse with timer set to one hour in the future
                        users_col.update_one({'user_id': str(ctx.author.id)}, {'$set': {'network': new_network, 'balance': user['balance'] - 10000}})

                        #send confirmation message
                        await ctx.author.send("`LOG: (store.gov) You have just purchased `one hour of Firewall protection` for 10000 <:coin:592831769024397332>!")
                        return
                    else:
                        await ctx.author.send("`LOG: (store.gov) Insufficient balance.`")
                        return

                elif msg.content.lower() == 'n' and msg.author.id == ctx.author.id:
                    await ctx.author.send("`LOG: (store.gov) Purchase canceled.`")
                    break
                else:
                    continue
        else:
            await ctx.author.send("`LOG: (store.gov) Not a valid ID.`")
            return

#System
@bot.group(aliases=['sys', 'stats'])
async def system(ctx):
    if ctx.invoked_subcommand is None:
        if ctx.guild != None:
            await ctx.message.delete()

        doc = users_col.find_one({'user_id': str(ctx.author.id)})
        if doc == None:
            await ctx.author.send("`Please type >login to start your adventure!`")
            return

        if doc['online'] == False:
            await ctx.author.send("`Your computer is not online. Please >login`")
            return

        else:
            if doc['network']['firewall'] != False:
                firewall_time = round(float(doc['network']['firewall'])  - time.time())
                doc['network']['firewall'] = "Expires in " + time.strftime('%Hh%Mm%Ss', time.gmtime(firewall_time))

            sys_string = "**__Computer Information__**\n**RAM** - "+str(doc['pc']['ram'])+ " GB\n**CPU** - "+str(doc['pc']['cpu'])+" GHz `"+doc['pc']['cpu_name']+"`\n**GPU** - "+str(doc['pc']['gpu'])+" GHz `"+doc['pc']['gpu_name']+"`\n\n**__Network Information__**\n**Bandwidth** - "+str(doc['network']['bandwidth'] + 10   )+" Mbps\n**Firewall** - "+str(doc['network']['firewall'])+"\n**IP Address** - ||"+doc['ip']+"||\n\n**__Other Information__**\n**Balance** - "+str(doc['balance'])+" <:coin:592831769024397332>\n**Connection Message** - "+doc['connect_msg']

            if str(ctx.author.id) in cache.keys():
                sys_string = sys_string + "\n\n**__Connection__**\n**Host** - "+cache[str(ctx.author.id)]['host']+"\n**Admin** - False"

            if doc['breach'] != False and doc['breach'] != True:
                breach_time = "Expires in " + time.strftime('%Hh%Mm%Ss', time.gmtime(round(float(doc['breach'])  - time.time())))
                sys_string = sys_string + "\n\n**Breach Cooldown** - " + breach_time

            embed = discord.Embed(
                title = "System Information",
                description = sys_string,
                color = 0x7289da
            )
            msg = await ctx.author.send("<a:loading2:592819419604975797> `Obtaining system information...`")
            await asyncio.sleep(calc_loading(doc, 5))
            await msg.edit(content="<:done:592819995843624961> `System information retreived`", embed=embed)

@system.command()
async def notify(ctx):
    if ctx.guild != None:
        await ctx.message.delete()

    user = users_col.find_one({'user_id': str(ctx.author.id)})
    if user == None:
        await ctx.author.send("`Please type >login to start your adventure!`")
        return

    if user['online'] == False:
        await ctx.author.send("`Your computer is not online. Please >login`")
        return

    if 'notify' not in user.keys():
        users_col.update_one(user, {'$set': {'notify': True}})
        await ctx.author.send("`LOG: Notifications are now set to: True`")
    else:
        users_col.update_one(user, {'$set': {'notify': not user['notify']}})
        await ctx.author.send("`LOG: Notifications are now set to: %s`" % (str(not user['notify'])))

#Generates Random Number
def randomNumber():
    random.seed(datetime.utcnow())
    num = random.randint(1, 30)
    return num * num

@bot.command(aliases=['hack', 'br', 'ddos'])
async def breach(ctx):
    user = users_col.find_one({'user_id': str(ctx.author.id)})
    if user['breach'] == False:
        if ctx.guild != None:
            await ctx.message.delete()
        if user == None:
            await ctx.author.send("`Please type >login to start your adventure!`")
            return
        if user['online'] == False:
            await ctx.author.send("`Your computer is not online. Please >login`")
            return
        if str(ctx.author.id) not in cache:
            await ctx.author.send("<:bad:593862973274062883> `SocketError: Not connected to Network`")
            return
        if cache[str(ctx.author.id)]['type'] != 1:
            await ctx.author.send("<:bad:593862973274062883> `Error: Server refused packets`")
            return
        if cache[str(ctx.author.id)]['type'] == 4:
            await ctx.author.send("<:bad:593862973274062883> `Error: Port already open.`")
            return
        #check for cooldown

        host_doc = users_col.find_one({'ip': cache[str(ctx.author.id)]['host']})
        if host_doc != None:
            host_member = discord.utils.get(bot.get_all_members(), id=int(host_doc['user_id']))
            if host_member != None:
                cache[str(host_member.id)] = {'status': False, 'type': 4, 'host': "**BREACH**"}
                breacher = ctx.author
                hackercooldownadd = { '$set': {'breach': str(time.time() + 600)}}
                givecooldown = users_col.update_one({'user_id': str(breacher.id)}, hackercooldownadd)
                await ctx.author.send("`BREACH: A breach attack has been started... Sent initiation packets, awaiting host.`")
                await breach_host(host_member, host_doc, ctx, user, breacher)
            else:
                await ctx.author.send("<:bad:593862973274062883> `Error: unknown error in getting user`")
        else:
            await ctx.author.send("<:bad:593862973274062883> `Error: unknown error in getting document`")
    else:
        await ctx.author.send("<:bad:593862973274062883> `INFO: Your Breach Cooldown is still in effect.`")


def get_random_q_a():
    cat = categories[random.randint(0, len(categories) - 1)]
    dif = difficulties[random.randint(0, len(difficulties) - 1)]
    tr = Trivia.request(1, cat, dif, Type.Multiple_Choice)
    #error handle
    if tr['response_code'] != 0:
        print("API error in getting question")
        answer = 4
        question = "What is 2 + 2"
        all_a = "4, 3, 6, 8"
        catstring = "Math"

    else:
        #regular day
        answer = tr['results'][0]['correct_answer']
        question = tr['results'][0]['question']
        all_a = ""
        catstring = str(tr['results'][0]['category'])
        # take all valid responses, and randomise order, and turn into one string.
        tr['results'][0]['incorrect_answers'].append(answer)
        random.shuffle(tr['results'][0]['incorrect_answers'])
        print(tr)
        i = 0
        for a in tr['results'][0]['incorrect_answers']:
            if i == 0:
                all_a = all_a + str(a)
            else:
                all_a = all_a +", "+str(a)
            i += 1

    #always give question and answer
    return catstring, all_a, question, answer

# the functiuons nthat we may or may not use (Spoiler alert we do)
async def breach_starter(host_member, host_doc, ctx, user, breacher):
    bypassed = False
    catstring, all_a, question, answer = get_random_q_a()
    doc = user
    print(answer)
    time_ = calc_time(doc)
    await breacher.send("`RETALIATION: ("+host_doc['ip']+") "+str(question)+"\n\nYour Choices:\n"+ str(all_a)+ "\n\n You have %s seconds, or the breach fails`" % (str(time_)))
    correct = False #Does Trivia Stuff
    while correct == False:
        try:
            msg = await bot.wait_for('message', timeout=time_)
            if  msg.author.id == breacher.id and msg.channel.id == breacher.dm_channel.id:
                if msg.content.lower() == str(answer).lower():
                    await breacher.send("`BREACH: Correct, retaliation sent.`")
                    correct = True
                    bypassed = True
                    break
                else:
                    await breacher.send("<:bad:593862973274062883>`BREACH: Error, incorrect. re-submit answer.`")
                    correct = False
            else:
                continue
        except:
            bypassed = False
            break
    if bypassed == True:
        await breach_host(host_member, host_doc, ctx, user, breacher)
    if bypassed == False:
        del cache[str(breacher.id)]
        del cache[str(host_member.id)]
        await breacher.send("`BREACH FAILED: (You did not answer the math problem in time, the breach has failed.)`")
        await host_member.send("`BREACH BLOCKED: (The breach has been stopped by your defenses)`")
        await breacher.send("`INFO: A Cooldown for Breaching has been set on your account for 10 minutes.`")
        await host_member.send("`LOG: %s has been disconnected.`" % (user['ip']))
        await breacher.send("`LOG: %s has disconnected you from their network.`" % (host_doc['ip']))
        hackercooldownadd = { '$set': {'breach': str(time.time() + 600)}}
        givecooldown = users_col.update_one({'user_id': str(breacher.id)}, hackercooldownadd)#
        #await breacher.send("`INFO: Your 10 minute Cooldown is now removed, you may now use >Breach`")
        #hackercooldownrem = { '$set': {'breach': False}}
        #removecooldown = users_col.update_one(hackers_oldfunds, hackercooldownrem)


async def breach_host(host_member, host_doc, ctx, user, breacher):
    bypassed = False
    catstring, all_a, question, answer = get_random_q_a()
    print(answer)
    doc = host_doc
    time_ = calc_time(doc)
    await host_member.send("`BREACH: ("+user['ip']+") "+str(question)+"\n\nYour Choices:\n"+ str(all_a)+ "\n\n You have %s seconds, or 1/4th of your Funds are taken.`" % (str(time_)))
    correct = False #Does Trivia Stuff
    while correct == False:
        try:
            msg = await bot.wait_for('message', timeout=time_)
            if  msg.author.id == host_member.id and msg.channel.id == host_member.dm_channel.id:
                if msg.content.lower() == str(answer).lower():
                    bypassed = True
                    await host_member.send("`BREACH: Correct, retaliation sent.`")
                    correct = True
                    break
                else:
                    await host_member.send("<:bad:593862973274062883> `BREACH: Error, incorrect. re-submit answer.`")
                    correct = False
            else:
                continue
        except:
            bypassed = False
            break
    if bypassed == True:
        await breach_starter(host_member, host_doc, ctx, user, breacher)

    if bypassed == False:
        await host_member.send("`DEFENSE FAILED: (You did not answer the math problem in time, your computer is compromized.)`")
        await breacher.send("`BREACH SUCCESFUL: (You have compromized the host's Computer, 1/4th of their funds will be moved into your account.)`")
        hacker = users_col.find_one({'user_id': str(breacher.id)})#Gets Hackers Document
        victim = users_col.find_one({'user_id': str(host_member.id)})#Gets Victims Document
        victims_funds = victim['balance']#Gets current balance
        ammount_toTake = int(victims_funds) * .25 #gets 1/4th

        #Transfers Money
        victims_oldfunds = {'user_id': str(host_member.id)}
        victims_newFunds = { '$set': {'balance': int(victim['balance']) - ammount_toTake}}
        newvictim = users_col.update_one(victims_oldfunds, victims_newFunds)
        hackers_oldfunds = {'user_id': str(breacher.id)}
        hackers_newFunds = { '$set': {'balance': int(hacker['balance']) + ammount_toTake}}
        newhacker = users_col.update_one(hacker, hackers_newFunds)
        await host_member.send("`BREACH: "+str(ammount_toTake)+"`<:coin:592831769024397332>` has been taken from your account.` ")
        await breacher.send("`BREACH: "+str(ammount_toTake)+"`<:coin:592831769024397332>` has been tranferred to your account.` ")
        #redoes logout to stop more hacking to 1 user


        doc = victim
        if doc != None:
            if doc['online'] == True:
                await host_member.send("**`Emergency shutdown initiated...`**")
                await host_member.send("`Saving session...`")
                their_doc = {'user_id': str(host_member.id)}
                insert_doc = { '$set': {'online': False} }
                new_doc = users_col.update_one(their_doc, insert_doc)
                await host_member.send("`Copying shared history...\nSaving history...truncating history files...`")
                await host_member.send("`Completed\nDeleting expired sessions... 1 Completed`")

                await host_member.send("`LOG: user "+ str(host_member) + " ("+hacker['ip']+") has disconnected from your network.`")
                del cache[str(host_member.id)]

                #get a list of connections to our buddy typing >logout
                connections = get_all_connections_to(doc['ip'])
                for connection in connections:
                    print(str(connection))
                    #send dc msg to each person connected to our buddy
                    await connection.send("`LOG: Lost connection to "+doc['ip']+"`")
                    #remove each connection from our buddy
                    del cache[str(connection.id)]

                await host_member.send("`Saving balance... " + str(victim['balance'] - ammount_toTake) + "`<:coin:592831769024397332>")
                await host_member.send("[process completed]")
                print(str(host_member.id) + " is now offline")
            else:
                await host_member.send("`Your computer is not online. Please >login`")
        else:
            await host_member.send("`Please type >login to start your adventure!`")


        await breacher.send("`INFO: A Cooldown for Breaching has been set on your account for 10 minutes.`")
        hackercooldownadd = { '$set': {'breach': str(time.time() + 600)}}
        givecooldown = users_col.update_one(hackers_oldfunds, hackercooldownadd)
        #await asyncio.sleep(600)
        #await breacher.send("`INFO: Your 10 minute Cooldown is now removed, you may now use >Breach`")
        #hackercooldownrem = { '$set': {'breach': False}}
        #removecooldown = users_col.update_one(hackers_oldfunds, hackercooldownrem)

#Edit connection message
@system.command()
async def editcm(ctx, *, message = None):
    if message == None:
        await ctx.send("<:bad:593862973274062883> `LOG: error in command 'editcm', no message provided.`")
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
            await ctx.send("`LOG: Updated connection message: %s`" % (message))


@bot.command(name='print', aliases=['log'])
async def _print(ctx, *, msg:str=None):
    if ctx.guild != None:
        await ctx.message.delete()
    user = users_col.find_one({'user_id': str(ctx.author.id)})
    if user == None:
        await ctx.author.send("`Please type >login to start your adventure!`")
        return
    if user['online'] == False:
        await ctx.author.send("`Your computer is not online. Please >login`")
        return
    if msg == None:
        await ctx.author.send("<:bad:593862973274062883> `error in command \'print\'. A message must be provided.`")
        return
    if str(ctx.author.id) not in cache.keys():
        for key, value in cache.items():
            if key == 'away':
                continue
            if value['host'] == user['ip']:
                host_user = discord.utils.get(bot.get_all_members(), id=int(key))
                if host_user != None:
                    await host_user.send("`LOG: ("+value['host']+") "+msg+"`")

        await ctx.author.send("`LOG: ("+user['ip']+") "+msg+"`")

    else:
        doc = users_col.find_one({'ip': cache[str(ctx.author.id)]['host']})
        if doc != None:
            for key, value in cache.items():
                if key == 'away':
                    continue
                if value['host'] == doc['ip']:
                    host_user = discord.utils.get(bot.get_all_members(), id=int(key))
                    if host_user.id == ctx.author.id:
                        await host_user.send("`LOG: ("+user['ip']+") "+msg+"`")
                        continue
                    if host_user != None:
                        await host_user.send("`LOG: ("+value['host']+") "+msg+"`")

            if str(ctx.author.id) in cache.keys():
                host_user = discord.utils.get(bot.get_all_members(), id=int(doc['user_id']))
                if host_user != None:
                    await host_user.send("`LOG: ("+user['ip']+") "+msg+"`")
                return

        else:
            await ctx.author.send("`Error: server refused packets.`")
            return

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

#Github
@bot.command()
async def github(ctx):
    embed = discord.Embed(
        title = "**Github Repository! 🔗**",
        url = "https://github.com/KAJdev/WumpusHack",
        color = 0x7289da
    )
    await ctx.send(embed = embed)

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
                await ctx.send("`LOG: Reset canceled.`")
                break
            else:
                continue


    except Exception as e:
        print(e)
        await message.delete()
        await ctx.send("<:bad:593862973274062883> `No reply recived. Prompt expired.`")
        return


#Command not found
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('<:bad:593862973274062883> `"%s" is not recognized as an internal or external command, operable program or batch file.`' % (ctx.message.content))


bot.loop.create_task(tick())
bot.run(config.TOKEN)
