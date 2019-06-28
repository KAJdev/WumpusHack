#Imports
print('Importing Libraries')
import discord, pymongo, config, asyncio, random, dns, json, math, time, importlib, sys
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
version = "2019.2.1.20b"

#tick counter
tick_number = 0

#Defaults
basic_pc_stats = {'ram': 1, 'cpu': 1, 'gpu': 1, 'cpu_name': "Intel Atom", 'gpu_name': "Integrated Graphics"}
basic_network_stats = {'bandwidth': 1, 'ddos_pro': False, 'firewall': False}
game_sites=['help.gov', 'store.gov', '0.0.0.1', 'mail.gov', 'wumpushack.com', 'bank.gov']#

#categories
categories = [Category.Maths, Category.Computers]
#difficulties
difficulties = [Diffculty.Easy, Diffculty.Medium, Diffculty.Hard]

#all of our discord ids for various purposes
owner_ids = [229695200082132993, 245653078794174465, 282565295351136256]

#default strings for game services
help_string = "Welcome to help.gov. Here you can find a list of commands you can use on your WumpusOS system.\n**__Commands__**\n**Connect** - Connects to another PC.\n**Disconnect** - Disconnects from another PC or Server.\n**System editcm <msg>** - Edits your connection message.\n**Pay** - Pays an IP a set ammount of money from your account.\n**Github** - Sends a link to the github repository.\n**Invite** - Sends a link to invite me.\n**Ping** - Checks Bot's Ping.\n**Login** - Logs onto your computer.\n**Logout** - Logs out of your computer.\n**Reset** - Resets all of your stats\n**Support** - Sends an invite link to the support server.\n**Breach / Hack** - Breach into someones computer/system.\n**Print** - Print a message in your computers log.\n**System / Stats / Sys** - Shows your system information.\n**Notify** - Toggles Email Notifications from mail.gov.\n\n**__Government websites__**\n**store.gov** - buy and upgrade your pc!\n**help.gov** - this network.\n**mail.gov** - see your inbox, and send messages."

#a list of items that are randomly selected for each day to be sold at store.gov
shop_items = [{'name': "GTX 1060", 'type': 'gpu', 'system': 5, 'cost': 50000}, {'name': "AMD Athlon II X3", 'type': 'cpu', 'system': 2, 'cost': 15000}, {'name': "Intel core i3", 'type': "cpu", 'system': 4, 'cost': 15000}, {'name': "4GB RAM Stick", 'type': 'ram', 'system': 4, 'cost': 40000}, {'name': "8GB RAM Stick", 'type': 'ram', 'system': 8, 'cost': 90000}, {'name': "16GB RAM Stick", 'type': 'ram', 'system': 16, 'cost': 200000}, {'name': "Intel core i5", 'type': "cpu", 'system': 5, 'cost': 35000}, {'name': "Intel core i7", 'type': "cpu", 'system': 6, 'cost': 50000}, {'name': "Intel Xeon", 'type': "cpu", 'system': 9, 'cost': 200000}, {'name': "AMD Threadripper", 'type': "cpu", 'system': 9, 'cost': 190000}, {'name': "AMD Radeon RX 580", 'type': 'gpu', 'system': 6, 'cost': 140000}, {'name': "Nvidia GeForce GTX 1070", 'type': 'gpu', 'system': 7, 'cost': 170000}, {'name': "Nvidia GeForce RTX 2080 Ti", 'type': 'gpu', 'system': 10, 'cost': 250000}]


#Removes the default help command
bot.remove_command("help")

#Establishes connection to MongoDB
print('Connecting to MongoDB')
myclient = pymongo.MongoClient(config.URI)
wumpdb = myclient["wumpus-hack"]
users_col = wumpdb['users']
mail_col = wumpdb['mail']
print("bot connected to database. users: " + str(users_col.count()))

#returns a number from 0 to 365 depending on the day
def get_day_of_year():
    return datetime.now().timetuple().tm_yday

#gets every cached user that has a common host value
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

    #pretty stats
    difference = time.time() - right_now
    print("updated %s firewall cooldown docs in %s seconds" % (str(updated_docs), str(round(difference, 1))))

#re imports the config
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

    #yummy stats
    difference = time.time() - right_now
    print("updated %s breach cooldown docs in %s seconds" % (str(updated_docs), str(round(difference, 1))))


@bot.command()
async def ping(ctx):
    #small ping command, might be removed as it doesn't really fit the theme
    embed=embed = discord.Embed(
        title = '🏓 PONG 🏓',
        description = "Ping: {0} ms".format(round(bot.latency * 1000, 1)),
        color = 0x7289da
    )
    await ctx.send(embed=embed)

#On ready
@bot.event
async def on_ready():
    #make sure username reflects version
    await bot.user.edit(username="WumpOS Terminal v"+version)
    if bot != None:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Bot starting..."))

    #yay more stats
    print("Bot is ready and online.")
    print("servers: %s, ping: %s ms, startup time: %s seconds" % (len(bot.guilds), bot.latency * 1000, str(round(time.time() - before_startup, 2))))


@bot.command(name="debug")
async def _debug(ctx):
    #small command to enable or disable raising of all command errors
    if ctx.author.id not in owner_ids:
        return

    config.DEBUG_STATUS = not config.DEBUG_STATUS
    await ctx.author.send("`Updated debug status to be`" + str(config.DEBUG_STATUS))

@bot.event
async def on_guild_join(guild):
    #change name on guild join.
    await guild.me.edit(nick="WumpusHack")
    print("WumpusHack Joined "+ str(guild))


#gets every user profile, and gives them money based on GPU stats (mines diamonds)
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

#the base tick of the bot. controls how many times mine() gets called, and the times in between checking for cooldowns
async def tick():
    #make sure bot is started
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
        if specs < 5 and specs >= 3:
            return 10


#Login
@bot.command()
async def login(ctx):
    if ctx.guild != None:
        await ctx.message.delete()
    #gets user document from DB
    doc = users_col.find_one({'user_id': str(ctx.author.id)})

    #ooooo new user... Fancy
    if doc == None:

        #make sure to clear cache just in case
        if str(ctx.author.id) in cache.keys():
            del cache[str(ctx.author.id)]
        embed = discord.Embed(
            title = "Welcome to WumpOS Inc. family!",
                description = "`Thank you for purchasing your new Wumpus system. Your Wumpus system is the way you can communicate with the world! Your computer is started, and ready to roll! Connect to your nation's help system to get the hang of things.` (>connect help.gov)",
            color = 0x35363B
        )
        await ctx.author.send(embed=embed)

        #randomly generate an IP address
        an_ip = str(random.randint(1, 255)) + "." + str(random.randint(1, 255)) + "." + str(random.randint(1, 255)) + "." + str(random.randint(1, 255))
        #make a quick account (its fast)
        user = {'user_id': str(ctx.author.id), 'pc': basic_pc_stats, 'network': basic_network_stats, 'online': True, 'balance': 100, 'ip': an_ip, 'connect_msg': "Hello. I am a PC.", 'breach': False, 'email': ctx.author.name.lower() + "@hackweek.com", 'notify': False}
        print('inserting...')
        #actually make the account (Its not so fast)
        users_col.insert_one(user)
        print('created user')

    #this guy came back
    else:
        #bruh if ur online why even... idk but gatta be safe right?
        if doc['online'] == True:
            await ctx.author.send("`error: Already online.`")
            return

        #start the cool msg show!
        msg = await ctx.author.send("<a:loading2:592819419604975797> `logging in`")
        their_doc = {'user_id': str(ctx.author.id)}
        insert_doc = { '$set': {'online': True} }
        #set profile online
        new_doc = users_col.update_one(their_doc, insert_doc)
        print('User '+str(ctx.author.id)+ " is now Online")

        #wait a bit using those nifty wait functions
        await asyncio.sleep(calc_loading(doc, 5))

        #neat. your in
        await msg.edit(content="<:done:592819995843624961> `Welcome back, %s, to your Wumpus System.`" % (str(ctx.author)))
        await ctx.author.send("**```WumpOS [Version "+version+"]\n(c) 2019 Discord Inc. All rights reserved.\n\nC:\\Users\\%s>```**" % (str(ctx.author)))

#Logout commando
@bot.command()
async def logout(ctx):
    if ctx.guild != None:
        await ctx.message.delete()
    #grab user document
    doc = users_col.find_one({'user_id': str(ctx.author.id)})
    #make sure it exists
    if doc != None:
        #make sure they are actually online
        if doc['online'] == True:
            if str(ctx.author.id) in cache.keys():
                if cache[str(ctx.author.id)]['type'] == 4:
                    await ctx.author.send("<:bad:593862973274062883> `PermissionError: Invalid permissions for this action`")
                    return
            #says saving session but actually just updates DB.. shh don't tell anyone
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
            #"Saves Balance" Lol not really
            await ctx.author.send("`Saving balance... " + str(doc['balance']) + "`<:coin:592831769024397332>")
            await ctx.author.send("[process completed]")
            print(str(ctx.author.id) + " is now offline")
        else:
            await ctx.author.send("`Your computer is not online. Please >login`")
    else:
        await ctx.author.send("`Please type >login to start your adventure!`")

#Connecto commando to peopleo
@bot.command()
async def connect(ctx, ip : str = None):
    #Makes sure they pass the tests
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
        # Starts Connecting to person/server
        msg = await ctx.author.send("<a:loading2:592819419604975797> `Connecting to %s`" % (ip))
        print('User '+str(ctx.author.id)+ " is now connecting to " + ip)
        #Loading Time
        await asyncio.sleep(calc_loading(user, 20))
        if ip in game_sites:
            #Pre-made Sites (.govs ect..)
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
            if ip == 'wumpushack.com':
                embed = discord.Embed(
                    title = "**Coming Soon! 🔗**",
                    url = "http://wumpushack.com",
                    color = 0x7289da
                )
                await msg.edit(content="<:done:592819995843624961> `You have successfully connected to %s`" % (ip), embed = embed)
                cache[str(ctx.author.id)] = {'status': True, 'type': 2, 'host': ip}
                return
            if ip == 'bank.gov':
                embed = discord.Embed(
                    title = "https://bank.gov",
                    description = "Welcome to Bank.gov\n\nYour Balance:\n `" + str(user['balance']) + "`<:coin:592831769024397332>\n\n**Pay** - Send Money to other players:\n`>pay <IP Address> <Amount>`",
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

#disconnect command
@bot.command(aliases=['dc'])
async def disconnect(ctx):
    #when u wanna go bye bye
    if ctx.guild != None:
        await ctx.message.delete()
    #mhm grab user
    user = users_col.find_one({'user_id': str(ctx.author.id)})
    #bruh this kid don't exist
    if user == None:
        await ctx.author.send("`Please type >login to start your adventure!`")
        return

    #make sure they arent trying to get out of a breach
    elif str(ctx.author.id) in cache.keys():
        if cache[str(ctx.author.id)]['type'] == 4:
            await ctx.author.send("<:bad:593862973274062883> `PermissionError: Invalid permissions for this action`")
            return

        #send confirmation
        await ctx.author.send("<:done:592819995843624961> `Disconnected from host %s`" % (cache[str(ctx.author.id)]['host']))

        #get the user thay are connected to
        doc = users_col.find_one({'ip': cache[str(ctx.author.id)]['host']})
        if doc != None:
            host_user = discord.utils.get(bot.get_all_members(), id=int(doc['user_id']))
            connecting_user = users_col.find_one({'user_id': str(ctx.author.id)})
            if host_user != None:
                #send message to connected user
                await host_user.send("`LOG: user "+ str(ctx.author) + " ("+connecting_user['ip']+") has disconnected from your network.`")

        #actually remove connection
        del cache[str(ctx.author.id)]
        return
    else:
        #lol
        await ctx.author.send("<:bad:593862973274062883> `SocketError: Not connected to any network.`")
        return

#Scan for people who exist
@bot.command(aliases=['scrape'])
async def scan(ctx):
    #get a profile
    user = users_col.find_one({'user_id': str(ctx.author.id)})
    #make sure they exist
    if user == None:
        await ctx.author.send("`Please type >login to start your adventure!`")
        return
    #make sure they are online
    if user['online'] == False:
        await ctx.author.send("`Your computer is not online. Please >login`")
        return
    #make sure they aren't already connected somewhere
    if str(ctx.author.id) in cache.keys():
        await ctx.author.send("<:bad:593862973274062883> `PortBindError: Port already in use. Use >disconnect to free up a port.`")
        return
    #Calls for loading time
    time_ = calc_loading(user, 600)
    msg = await ctx.author.send("<a:loading2:592819419604975797> `scraping for IP addresses. ( This will take around %s Minute(s) )`" % round(time_ / 60))

    #set connection so they cant do other stuff
    cache[str(ctx.author.id)] = {'status': True, 'type': 3, 'host': "using network card to scan for IPs"}

    #shhh its not actually doing anything... it can do it in milliseconds lol
    await asyncio.sleep(time_)

    #if they disconnected from scanning (decided to cancel)
    if str(ctx.author.id) not in cache.keys():
        return
    #remove that conenction
    del cache[str(ctx.author.id)]

    #decide if we should reward their patience with nothing
    if random.randint(1, 5) == 2:
         await msg.edit(content="<:done:592819995843624961> `Scrape returned (0) addresses`")
         return

    #gets all the DB docs. yay
    all_docs = users_col.find({})
    doc = None

    #make sure you get an IP hats not yours
    while True:
        doc = users_col.find({'online': True})
        doc = doc[random.randrange(doc.count()) - 1]
        if doc['user_id'] == user['user_id']:
            continue
        else:
            break

    #let the user know
    await msg.edit(content="<:done:592819995843624961> `Scrape returned (1) address: %s`" % (doc['ip']))

    #oh yeah, tells the guy you just pinged that their IP is leaked...
    host_user = discord.utils.get(bot.get_all_members(), id=int(doc['user_id']))
    if host_user != None:
        await host_user.send("`LOG: recived ping from host "+user['ip']+"`")


#We just got a letter, we just got a letter, we just got a letter. I wonder who its from? LOL
@bot.command()
async def inbox(ctx):
    user = users_col.find_one({'user_id': str(ctx.author.id)})
    #online
    if user['online'] == False:
        await ctx.author.send("`Your computer is not online. Please >login`")
        return
    #make sure connected
    elif str(ctx.author.id) not in cache:
        raise commands.CommandNotFound
        return
    #make sure connected to mail.gov as this command is only run when connected to that game service
    elif cache[str(ctx.author.id)]['host'] != 'mail.gov':
        raise commands.CommandNotFound
        return

    #deleteet begon guild message
    elif ctx.guild != None:
        await ctx.message.delete()

    #basic stuff u should know by now
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
        #get their email address
        email = user['email']
        #basic email string
        mail_string = "Hi, this is mail.gov, Here you can see your inbox, and send messages. \nUse the `>send <email> <message>` command to send an email!\n\n**inbox for %s**\n```" % (email)

        #get every mail document in DB thats for them
        mails = mail_col.find({'to': email})
        if mails.count() < 1:
            # ;(
            mail_string = mail_string + "\nYour inbox is empty :)\n"
        else:
            #for every mail document, add a bit to the string
            for mail in mails:
                mail_string = mail_string + "To: " + mail['to'] +"\nFrom: " + mail['from'] + "\n" + mail['content'] +"\n\n"

        embed = discord.Embed(
            title = "https://mail.gov",
            description = mail_string + "```\n\nUse `>clear` to clear your inbox of messages",
            color = 0x7289da
        )
        #SENDDD
        await ctx.author.send(embed=embed)



#Clears Inbox
@bot.command()
async def clear(ctx):
    #basic stuff in every command...
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
        # r u sureeee???
        await ctx.author.send("`LOG: (mail.gov) Are you sure you want toclear your inbox? Respond with `Y` or `N")

        #makes infinite loop so that they can make SURE that they want to clear their beloved inbox
        while True:
            msg = await bot.wait_for('message')
            #make sure msg is in the right place
            if msg.content.lower() == "y" and msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id:
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
                    # F
                    await ctx.author.send("`LOG: (mail.gov) You do not have any mail in your inbox.`")
                    return

            elif msg.content.lower() == 'n' and msg.author.id == ctx.author.id:
                #if they get cold feet Lol
                await ctx.author.send("`LOG: (mail.gov) purge canceled.`")
                break
            else:
                continue

#SEnd Email :D
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
        #grab the recievers profile
        reciver = users_col.find_one({'email': mail_to})
        if reciver != None:
            email = user['email']

            #make mail document and insert it into the mail collection in the DB.. god i love Mongo <3
            mail_doc = {'to': mail_to, 'from': email, 'content': msg}
            mail_col.insert_one(mail_doc)
            await ctx.author.send("`LOG: (mail.gov) email has been sent.`")

            #send the reciving user a little ping if they have it enabled (>sys notify)
            if reciver['notify'] == False:
                return
            else:
                emailperson = discord.utils.get(bot.get_all_members(), id= int(reciver['user_id']))
                if emailperson != None:
                    # Flashback to AOL lol
                    await emailperson.send("`LOG: (mail.gov) You've Got Mail`")
        else:
            #welp... they dont exist
            await ctx.author.send("`LOG: (mail.gov) email does not exist`")

#Pay Command
@bot.command()
async def pay(ctx, ip:str=None, amount:int=None):
    #grabs all profiles needed for this command
    author = users_col.find_one({'user_id': str(ctx.author.id)})
    user = users_col.find_one({'ip': ip})

    if ctx.guild != None:
        await ctx.message.delete()
    if author == None:
        await ctx.author.send("`Please type >login to start your adventure!`")
        return
    if author['online'] == False:
        await ctx.author.send("`Your computer is not online. Please >login`")
        return
    if str(ctx.author.id) not in cache.keys():
        raise commands.CommandNotFound
        return

    #need to be connected to teh bank
    elif cache[str(ctx.author.id)]['host'] != 'bank.gov':
        raise commands.CommandNotFound
        return

    #if anything went wrong grabbing users just cancel
    if user == None or author == None or amount == None:
        await ctx.author.send("`LOG: (bank.gov) error in command`")
        return

    #check if they are a cheapskate
    if amount > author['balance']:
        await ctx.author.send("`LOG: Insufficient Funds`")
        return

    if amount <= 0:
        await ctx.author.send("`LOG: (bank.gov) Amount must be above 0`")
        return
    #take from one, and give to the other. Notify both parties.
    user_member = discord.utils.get(bot.get_all_members(), id = int(user['user_id']))
    if user_member == None:
        await ctx.author.send("`LOG: (bank.gov) User not found.`")
        return

    users_col.update_one({'user_id': author['user_id']}, {'$set': {'balance': author['balance'] - amount}})
    users_col.update_one({'user_id': user['user_id']}, {'$set': {'balance': author['balance'] + amount}})
    await ctx.author.send("`LOG: (bank.gov) Sent "+ ip + " " + str(amount) + "`<:coin:592831769024397332>")
    await user_member.send("`LOG: (bank.gov) You have recived " + str(amount) + "` <:coin:592831769024397332> `From: " + str(ctx.author) + "`")

@bot.event
async def on_message(message):
    #just a handy debug tool.
    if message.content.startswith(">"):
        print("Command: " + message.content)
        print("User: " + str(message.author))

    #make sure to do that..
    await bot.process_commands(message)

#purchase command
@bot.command()
async def purchase(ctx, *, id:str=None):
    user = users_col.find_one({'user_id': str(ctx.author.id)})
    if user['online'] == False:
        await ctx.author.send("`Your computer is not online. Please >login`")
        return
    if str(ctx.author.id) not in cache:
        raise commands.CommandNotFound
        return
    #must be at the store to buy things
    elif cache[str(ctx.author.id)]['host'] != 'store.gov':
        raise commands.CommandNotFound
        return


    #set the python random gen seed, and grab the first 5 items of the day
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

    #thats not a product!
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

        #get user docuemnt from DB and check if they have an account
        doc = users_col.find_one({'user_id': str(ctx.author.id)})
        if doc == None:
            await ctx.author.send("`Please type >login to start your adventure!`")
            return

        #check for online status
        if doc['online'] == False:
            await ctx.author.send("`Your computer is not online. Please >login`")
            return

        else:
            #display firewall cooldown if active
            if doc['network']['firewall'] != False:
                firewall_time = round(float(doc['network']['firewall'])  - time.time())
                doc['network']['firewall'] = "Expires in " + time.strftime('%Hh%Mm%Ss', time.gmtime(firewall_time))

            #base system display with PC specs and such
            sys_string = "**__Computer Information__**\n**RAM** - "+str(doc['pc']['ram'])+ " GB\n**CPU** - "+str(doc['pc']['cpu'])+" GHz `"+doc['pc']['cpu_name']+"`\n**GPU** - "+str(doc['pc']['gpu'])+" GHz `"+doc['pc']['gpu_name']+"`\n\n**__Network Information__**\n**Bandwidth** - "+str(doc['network']['bandwidth'] + 10   )+" Mbps\n**Firewall** - "+str(doc['network']['firewall'])+"\n**IP Address** - ||"+doc['ip']+"||\n\n**__Other Information__**\n**Balance** - "+str(doc['balance'])+" <:coin:592831769024397332>\n**Connection Message** - "+doc['connect_msg']

            if str(ctx.author.id) in cache.keys():
                #grab hosts info to display
                host_email = users_col.find_one({'ip': cache[str(ctx.author.id)]['host']})
                sys_string = sys_string + "\n\n**__Connection__**\n**Host** - "+cache[str(ctx.author.id)]['host']

                # show email if connected to PC
                if cache[str(ctx.author.id)]['type'] == 1 and host_email != None:
                    sys_string = sys_string + "\n**Host's Email** - "+str(host_email['email'])

            #show breach duration if they have a cooldown active
            if doc['breach'] != False and doc['breach'] != True:
                breach_time = "Expires in " + time.strftime('%Hh%Mm%Ss', time.gmtime(round(float(doc['breach'])  - time.time())))
                sys_string = sys_string + "\n\n**Breach Cooldown** - " + breach_time

            embed = discord.Embed(
                title = "System Information",
                description = sys_string,
                color = 0x7289da
            )
            #send message
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

    #create field in DB if not already there
    if 'notify' not in user.keys():
        users_col.update_one(user, {'$set': {'notify': True}})
        await ctx.author.send("`LOG: Notifications are now set to: True`")
    else:
        #toggle the value in the DB
        users_col.update_one(user, {'$set': {'notify': not user['notify']}})
        await ctx.author.send("`LOG: Notifications are now set to: %s`" % (str(not user['notify'])))

#Generates Random Number based on current time
def randomNumber():
    random.seed(datetime.utcnow())
    num = random.randint(1, 30)
    return num * num

@bot.command(aliases=['hack', 'br', 'ddos'])
async def breach(ctx):
    #not the best way to do this, but.. I didn't do it (kaj) and it works. and we only have a week.
    user = users_col.find_one({'user_id': str(ctx.author.id)})

    #make sure they dont have a cooldown False = no cooldown, timestamp - cooldown
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

        #if they arent a PC, then u cant hack it
        if cache[str(ctx.author.id)]['type'] != 1:
            await ctx.author.send("<:bad:593862973274062883> `Error: Server refused packets`")
            return

        #if they are already in a breach, you cant hack them again.
        if cache[str(ctx.author.id)]['type'] == 4:
            await ctx.author.send("<:bad:593862973274062883> `Error: Port already open.`")
            return


        host_doc = users_col.find_one({'ip': cache[str(ctx.author.id)]['host']})
        if host_doc != None:
            host_member = discord.utils.get(bot.get_all_members(), id=int(host_doc['user_id']))
            if host_member != None:

                #Checks if host is already being breached
                if str(host_member.id) in cache.keys():
                    if cache[str(host_member.id)]['type'] == 4:
                        await ctx.author.send("`LOG: error sending breach packets`")
                        return
                #sets connection as to not let you >dc or >logout
                cache[str(host_member.id)] = {'status': False, 'type': 4, 'host': "**BREACH**"}
                breacher = ctx.author

                #give a cooldown now in case something happens
                hackercooldownadd = { '$set': {'breach': str(time.time() + 600)}}
                givecooldown = users_col.update_one({'user_id': str(breacher.id)}, hackercooldownadd)

                #send the host a message, and start the show!
                await ctx.author.send("`BREACH: A breach attack has been started... Sent initiation packets, awaiting host.`")
                await breach_host(host_member, host_doc, ctx, user, breacher)
            else:
                await ctx.author.send("<:bad:593862973274062883> `Error: unknown error in getting user`")
        else:
            await ctx.author.send("<:bad:593862973274062883> `Error: unknown error in getting document`")
    else:
        await ctx.author.send("<:bad:593862973274062883> `INFO: Your Breach Cooldown is still in effect.`")

#gets a random question, and answer from an API. with a backup
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
    #ugh welp.. good luck understanding this tbh

    #get basic stuff
    bypassed = False
    catstring, all_a, question, answer = get_random_q_a()
    doc = user
    print(answer)
    time_ = calc_time(doc)
    #send initial question
    await breacher.send("`RETALIATION: ("+host_doc['ip']+") "+str(question)+"\n\nYour Choices:\n"+ str(all_a)+ "\n\nYou have %s seconds, or the breach fails`" % (str(time_)))
    correct = False #Does Trivia Stuff

    #start loop checkign for answer
    while correct == False:
        try:
            msg = await bot.wait_for('message', timeout=time_)
            if  msg.author.id == breacher.id and msg.channel.id == breacher.dm_channel.id:
                if msg.content.lower() == str(answer).lower():
                    #they did it! Bounce question back to breach person
                    await breacher.send("`BREACH: Correct, retaliation sent.`")
                    correct = True
                    bypassed = True
                    break
                else:
                    #not right, re loop
                    await breacher.send("<:bad:593862973274062883>`BREACH: Error, incorrect. re-submit answer.`")
                    correct = False
            else:
                continue
        except:
            bypassed = False
            break
    if bypassed == True:
        #they did it! call other function
        await breach_host(host_member, host_doc, ctx, user, breacher)
    if bypassed == False:
        #well shit they didn't answer in time. do all this message garbage VVV

        #remove connections first
        del cache[str(breacher.id)]
        del cache[str(host_member.id)]

        #send a ton of stuff with information about end of breach
        await breacher.send("`BREACH FAILED: (You did not answer the math problem in time, the breach has failed.)`")
        await host_member.send("`BREACH BLOCKED: (The breach has been stopped by your defenses)`")
        await breacher.send("`INFO: A Cooldown for Breaching has been set on your account for 10 minutes.`")
        await host_member.send("`LOG: %s has been disconnected.`" % (user['ip']))
        await breacher.send("`LOG: %s has disconnected you from their network.`" % (host_doc['ip']))

        #add cooldown
        hackercooldownadd = { '$set': {'breach': str(time.time() + 600)}}
        givecooldown = users_col.update_one({'user_id': str(breacher.id)}, hackercooldownadd)


async def breach_host(host_member, host_doc, ctx, user, breacher):
    #ok now back to the breacher guy. this function is identical to the last, except for which side its for.
    bypassed = False
    catstring, all_a, question, answer = get_random_q_a()
    print(answer)
    doc = host_doc
    time_ = calc_time(doc)
    await host_member.send("`BREACH: ("+user['ip']+") "+str(question)+"\n\nYour Choices:\n"+ str(all_a)+ "\n\nYou have %s seconds, or 1/4th of your Funds are taken.`" % (str(time_)))
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
        #they breached it! take the money, and logout the breached persons PC to prevent them from being hacked again
        await host_member.send("`DEFENSE FAILED: (You did not answer the trivia question in time, your computer is compromized.)`")
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
                del cache[str(host_member.id)]

                #get a list of connections to our buddy after the breach
                connections = get_all_connections_to(doc['ip'])
                for connection in connections:
                    print(str(connection))
                    #send dc msg to each person connected to our buddy.
                    await connection.send("`LOG: Lost connection to "+doc['ip']+"`")
                    #remove each connection from our buddy and from each person
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

#Edit connection message
@system.command()
async def editcm(ctx, *, message = None):
    #simple command to edit what peopel see when they connect to you
    if ctx.guild != None:
        await ctx.message.delete()
    if message == None:
        await ctx.author.send("<:bad:593862973274062883> `LOG: error in command 'editcm', no message provided.`")
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
            await ctx.author.send("`LOG: Updated connection message: %s`" % (message))


@bot.command(name='print', aliases=['log', 'pr'])
async def _print(ctx, *, msg:str=None):
    #prints messages to peoples consoles. If your connected to a User, and not in a breach, you can log to their PC, meaning send msgs back and forth
    if ctx.guild != None:
        await ctx.message.delete()
    user = users_col.find_one({'user_id': str(ctx.author.id)})
    if user == None:
        await ctx.author.send("`Please type >login to start your adventure!`")
        return
    if user['online'] == False:
        await ctx.author.send("`Your computer is not online. Please >login`")
        return

    #cant send ""
    if msg == None:
        await ctx.author.send("<:bad:593862973274062883> `error in command \'print\'. A message must be provided.`")
        return

    #check if anyone is connected to them, and send message
    if str(ctx.author.id) not in cache.keys():
        #search through all connections
        for key, value in cache.items():
            if key == 'away':
                continue

            #if IPs match
            if value['host'] == user['ip']:
                #get user
                host_user = discord.utils.get(bot.get_all_members(), id=int(key))
                if host_user != None:
                    #send message
                    await host_user.send("`LOG: ("+value['host']+") "+msg+"`")

        await ctx.author.send("`LOG: ("+user['ip']+") "+msg+"`")

    else:
        #check if they are connected to anyone and send message AND if anyone is connected to them
        doc = users_col.find_one({'ip': cache[str(ctx.author.id)]['host']})
        if doc != None:
            #search through all connections
            for key, value in cache.items():
                if key == 'away':
                    continue
                #matching IPs awww <3
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
            #if it is some service, or not a user PC that they are connected to
            await ctx.author.send("`Error: server refused packets.`")
            return

#Invite
@bot.command()
async def invite(ctx):
    #send link to invite the bot to your server
    embed = discord.Embed(
        title = "**Invite Me! 🔗**",
        url = "https://discordapp.com/api/oauth2/authorize?client_id=592803813593841689&permissions=8&scope=bot",
        color = 0x7289da
    )
    await ctx.send(embed = embed)

#Cache
@bot.command(name="cache")
async def _cache(ctx):
    #debug command to show the cache in console
    print(cache)

#Support
@bot.command()
async def support(ctx):
    #send link to support discord server
    embed = discord.Embed(
        title = "**Support Server! 🔗**",
        url = "https://discord.gg/GC7Pw9Y",
        color = 0x7289da
    )
    await ctx.send(embed = embed)

#Github
@bot.command()
async def github(ctx):
    #send link to github repo
    embed = discord.Embed(
        title = "**Github Repository! 🔗**",
        url = "https://github.com/KAJdev/WumpusHack",
        color = 0x7289da
    )
    await ctx.send(embed = embed)

#Reset
@bot.command()
async def reset(ctx, user : discord.User = None):
    #this command isnt ready yet. and probably wont be active during hack week
    raise commands.CommandNotFound


    if ctx.guild != None:
        await ctx.message.delete()
    if user == None or ctx.author.id not in owner_ids:
        user = ctx.author
    await ctx.author.send("`Are you sure you would like to reset?\nReseting will reset all of your stats [Y/N]`")
    try:
        while True:
            msg = await bot.wait_for('message', timeout= 10)
            if "y" == msg.content.lower and msg.author.id == ctx.author.id and msg.channel.id == breacher.dm_channel.id:
                users_col.delete_one({'user_id': str(user.id)})
                an_ip = str(random.randint(1, 255)) + "." + str(random.randint(1, 255)) + "." + str(random.randint(1, 255)) + "." + str(random.randint(1, 255))
                users_col.insert_one({'user_id': str(user.id), 'pc': basic_pc_stats, 'network': basic_network_stats, 'online': True, 'balance': 100, 'ip': an_ip, 'connect_msg': "Hello. I am a PC."})
                await ctx.author.send("`"+str(user) + "'s systems have been re-imaged.`")
                break
            elif "n" == msg.content.lower and msg.author.id == ctx.author.id and msg.channel.id == breacher.dm_channel.id:
                await ctx.author.send("`LOG: Reset canceled.`")
                break
            else:
                continue


    except Exception as e:
        print(e)
        await message.delete()
        await ctx.author.send("<:bad:593862973274062883> `No reply recived. Prompt expired.`")
        return


#Command not found
@bot.event
async def on_command_error(ctx, error):
    #always make sure to leave no clutter in a guild.
    if ctx.guild != None:
        await ctx.message.delete()

    #no command? *gasp*
    if isinstance(error, commands.CommandNotFound):
        await ctx.author.send('<:bad:593862973274062883> `"%s" is not recognized as an internal or external command, operable program or batch file.`' % (ctx.message.content))

    #print the error if debug is enabled
    if config.DEBUG_STATUS == True:
        raise error


bot.loop.create_task(tick())
bot.run(config.TOKEN)
