#Imports
print('Importing Libraries')
import discord, pymongo, config, asyncio, random, dns, json, math, time, importlib, sys
before_startup = time.time()
from discord.ext import commands, tasks
from datetime import datetime
from pytrivia import Category, Diffculty, Type, Trivia


class main_commands(commands.Cog):

    def __init__(self, bot):
        print("Setting up")
        self.bot = bot
        self.Trivia = Trivia(True)

        wumpdb = pymongo.MongoClient(config.URI)["wumpus-hack"]
        self.users_col = wumpdb['users-beta']
        self.mail_col = wumpdb['mail-beta']

        self.owner_ids = [229695200082132993, 245653078794174465, 282565295351136256]

        self.categories = [Category.Maths, Category.Computers]
        self.difficulties = [Diffculty.Easy, Diffculty.Medium, Diffculty.Hard]
        self.bot.remove_command("help")

        self.basic_pc_stats = {'ram': 1, 'cpu': 1, 'gpu': 1, 'cpu_name': "Intel Atom", 'gpu_name': "Integrated Graphics"}
        self.basic_network_stats = {'bandwidth': 1, 'ddos_pro': False, 'firewall': False}
        self.game_sites=['help.gov', 'store.gov', '0.0.0.1', 'mail.gov', 'wumpushack.com', 'bank.gov', 'leaderboard.gov']

        self.cache = {'away': {}}
        self.version = "2019.2.1.20b"
        self.tick_number = 0

        self.tick.start()

        self.help_string = "Welcome to help.gov. Here you can find a list of commands you can use on your WumpusOS System.\n**__Commands__**\n**Breach / Hack / Br / DDOS** - Hack into someone's PC\n**Connect** - Connects to another PC.\n**Disconnect** - Disconnects from another PC.\n**Github** - Sends a link to the Github repository.\n**Invite** - Sends a link to invite me.\n**Login** - Logs onto your PC.\n**Logout** - Logs out of your PC.\n**Notify** - Toggle Email notification from mail.gov.\n**Ping** - Check the bot's current Ping.\n**Print** - Send a message to your PC's logs, as well as the IP you are connected.\n**Scan** - Scans for IP addresses.\n**Support** - Sends an invite link to the WumpusHack Support Server.\n**System / Stats / Sys** - Shows your current stats.\n**System editcm <Message>** - Edits your current connection message.\n\n**__Government Websites__**\n**store.gov** - Buy and upgrade your PC!\n**help.gov** - This network.\n**mail.gov** - See your inbox, and send messages.\n**bank.gov** - See your balance and send money to people"
        self.shop_items = config.shop_items
        print("cog initiated")


    #Returns a number from 0 to 365 depending on the day
    def get_day_of_year(self):
        return datetime.now().timetuple().tm_yday

    #Gets every self.cached user that has a common host value
    def get_all_connections_to(self, host):
        connections = []
        for key, value in self.cache.items():
            if key == 'away':
                continue
            else:
                if value['host'] == host:
                    mem = discord.utils.get(self.bot.get_all_members(), id=int(key))
                    if mem != None:
                        connections.append(mem)
        return connections

    #Checks on firewall timer
    async def check_timer_firewall(self):
        #Get all documents from db
        docs = self.users_col.find({})
        right_now = time.time()
        updated_docs = 0
        for doc in docs:
            #Check if firewall timer isnt over (False == no timer)
            if doc['network']['firewall'] != False:
                updated_docs += 1
                expire = float(doc['network']['firewall'])

                #If the firewall time (timestamp) is less than right now
                if expire <= time.time():
                    #Set network to be false, so it is not check against
                    doc['network']['firewall'] = False
                    #Update document is DB
                    self.users_col.update_one({'user_id': doc['user_id']}, {'$set':{'network': doc['network']}})

                    #Get user and send message
                    member = discord.utils.get(self.bot.get_all_members(), id=int(doc['user_id']))
                    if member != None:
                        await member.send("`LOG: Firewall has been disabled. ports are now unportected.`")

        #Pretty stats
        difference = time.time() - right_now
        print("Updated %s firewall cooldown docs in %s seconds" % (str(updated_docs), str(round(difference, 1))))


    #Checks on breach cooldown timer
    async def check_timer_breach_cooldown(self):
        #Get all documents from db
        docs = self.users_col.find({})
        right_now = time.time()
        updated_docs = 0
        for doc in docs:
            #Check if breach timer isnt over (False == no timer)
            if doc['breach'] != False:
                updated_docs += 1
                expire = float(doc['breach'])

                #If the breach cooldown time (timestamp) is less than right now
                if expire <= time.time():
                    #Set network to be false, so it is not check against and update document is DB
                    self.users_col.update_one({'user_id': doc['user_id']}, {'$set':{'breach': False}})

                    #Get user and send message
                    member = discord.utils.get(self.bot.get_all_members(), id=int(doc['user_id']))
                    if member != None:
                        await member.send("`LOG: Breach cooldown disabled.`")

        #Yummy stats
        difference = time.time() - right_now
        print("updated %s breach cooldown docs in %s seconds" % (str(updated_docs), str(round(difference, 1))))


    @commands.command()
    async def ping(self, ctx):
        #Small ping command, might be removed as it doesn't really fit the theme
        embed=embed = discord.Embed(
            title = '🏓 PONG 🏓',
            description = "Ping: {0} ms".format(round(self.bot.latency * 1000, 1)),
            color = 0x7289da
        )
        await ctx.send(embed=embed)

    #On ready
    @commands.Cog.listener()
    async def on_ready(self):
        #Make sure username reflects self.version
        await self.bot.user.edit(username="WumpOS Terminal v"+self.version)
        if self.bot != None:
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="bot starting..."))

        #Yay more stats
        print("Bot is ready and online.")
        print("Servers: %s, Ping: %s ms, Startup time: %s seconds" % (len(self.bot.guilds), self.bot.latency * 1000, str(round(time.time() - before_startup, 2))))


    @commands.command(name="debug")
    async def _debug(self, ctx):
        #Small command to enable or disable raising of all command errors
        if ctx.author.id not in self.owner_ids:
            return

        config.DEBUG_STATUS = not config.DEBUG_STATUS
        await ctx.author.send("`Updated debug status to be`" + str(config.DEBUG_STATUS))


    #Gets every user profile, and gives them money based on GPU stats (mines diamonds)
    def mine(self):
        before = time.time()
        docs = self.users_col.find({})
        updated_count = 0
        for doc in docs:
            if doc['online'] == False:
                continue
            new_doc = { '$set': {'balance': doc['balance'] + doc['pc']['gpu']}}
            self.users_col.update_one(doc, new_doc)
            updated_count += 1

        difference = time.time() - before
        print("Updated %s online users in %s seconds" % (updated_count, str(round(difference, 1))))


    def check_ghost_users(self):
        before = time.time()
        docs = self.users_col.find({})
        updated_count = 0
        for doc in docs:
            if discord.utils.get(self.bot.get_all_members(), id=int(doc['user_id'])) == None:
                self.users_col.delete_one({'user_id': doc['user_id']})
                updated_count += 1

        difference = time.time() - before
        print("Removed %s inactive users in %s seconds" % (updated_count, str(round(difference, 1))))

    #The base tick of the bot. controls how many times mine() gets called, and the times in between checking for cooldowns
    @tasks.loop(seconds=config.TICK_SPEED)
    async def tick(self):
        before = time.time()
        if self.bot != None:
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=">login | %s online | Tick %s" % (self.users_col.find({'online': True}).count(), str(self.tick_number))))
        self.tick_number += 1
        print("TICK " + str(self.tick_number))

        self.mine()
        self.check_ghost_users()
        await self.check_timer_firewall()
        await self.check_timer_breach_cooldown()
        if round(time.time() - before, 1) > 5:
            print("ERROR | Tick took too long (%s seconds)" % (str(round(time.time() - before, 1))))
        print("")

    @tick.before_loop
    async def before_tick(self):
        print('waiting...')
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.tick.cancel()


    #Calculates Loading for Stuff
    def calc_loading(self, doc, base):
        load_time = base / ((doc['network']['bandwidth'] * doc['pc']['cpu']) + 1)
        return load_time

    #Calculates time for self.Trivia questions
    def calc_time(self, doc):
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
                return 20
            if specs < 25 and specs > 15:
                return 15
            if specs < 15 and specs > 3:
                return 10
            if specs < 5 and specs >= 3:
                return 10


    #Login
    @commands.command()
    async def login(self, ctx):
        if ctx.guild != None:
            await ctx.message.delete()
        #Gets user document from DB
        doc = self.users_col.find_one({'user_id': str(ctx.author.id)})

        #Ooooo new user... Fancy
        if doc == None:

            #Make sure to clear self.cache just in case
            if str(ctx.author.id) in self.cache.keys():
                del self.cache[str(ctx.author.id)]
            embed = discord.Embed(
                title = "WumpOS User Manual",
                description = "Thank you for purchasing your new Wumpus system. Your Wumpus system is the way you can communicate with the world! Your computer is started, and ready to roll! Connect to your nation's help system to get the hang of things. \n(>connect help.gov)\n\nYour PC currently has pretty lame parts. Don't you want a god PC? Well first things first, you need money. Why don't you hack into some people by first getting their IP using `>scan`, and then connecting to them using `>connect <ip>`. After that, you can start a breach using `>breach`. If you can win, then you can steal some of their cash!\n\nWhen you have some cash, try visiting the the store (`>connect store.gov`) and looking at what is available that day. Taking a look at the bank is a good idea as well. Oh, and dont forget to check your mail!\n\noh! side note, Your PC parts actually do something! Each Tick (10s), you gain <:coin:592831769024397332> based on the GHz of your GPU. Every loading time, is based off your CPU, and the amount of money that you can steal from a user is based on your RAM. so, get to hacking!\n\n*if you ever need this message again, use >help*",
                color = 0x35363B
            )
            await ctx.author.send(embed=embed)
            await ctx.author.send("**```WumpOS [version "+self.version+"]\n(c) 2019 Discord Inc. All rights reserved.\n\nC:\\Users\\%s>```**" % (str(ctx.author)))

            #Randomly generate an IP address
            while True:
                an_ip = str(random.randint(1, 255)) + "." + str(random.randint(1, 255)) + "." + str(random.randint(1, 255)) + "." + str(random.randint(1, 255))
                ip_doc = self.users_col.find({'ip': an_ip})
                if ip_doc.count() > 0:
                    continue
                else:
                    break

            email_test = self.users_col.find({'email': ctx.author.name.lower() + "@beta.com"})
            if email_test.count() > 0:
                users_email = ctx.author.name.lower() + str(email_test.count()) + "@beta.com"
            else:
                users_email = ctx.author.name.lower() + "@beta.com"

            #Make a quick account (its fast)
            user = {'user_id': str(ctx.author.id), 'pc': self.basic_pc_stats, 'network': self.basic_network_stats, 'online': True, 'balance': 100, 'ip': an_ip, 'connect_msg': "Hello. I am a PC.", 'breach': False, 'email': users_email, 'notify': False, 'inventory': []}
            print('Inserting...')
            #Actually make the account (Its not so fast)
            self.users_col.insert_one(user)
            print('Created user')

        #This guy came back
        else:
            #Bruh if ur online why even... idk but gatta be safe right?
            if doc['online'] == True:
                await ctx.author.send("`error: Already online.`")
                return

            #Start the cool msg show!
            msg = await ctx.author.send("<a:loading2:592819419604975797> `Logging in`")
            their_doc = {'user_id': str(ctx.author.id)}
            insert_doc = { '$set': {'online': True} }
            #Set profile online
            new_doc = self.users_col.update_one(their_doc, insert_doc)
            print('User '+str(ctx.author.id)+ " is now Online")

            #Wait a bit using those nifty wait functions
            await asyncio.sleep(self.calc_loading(doc, 5))

            #Neat. your in
            await msg.edit(content="<:done:592819995843624961> `Welcome back, %s, to your Wumpus System.`" % (str(ctx.author)))
            await ctx.author.send("**```WumpOS [version "+self.version+"]\n(c) 2019 Discord Inc. All rights reserved.\n\nC:\\Users\\%s>```**" % (str(ctx.author)))

    #Logout commando
    @commands.command()
    async def logout(self, ctx):
        if ctx.guild != None:
            await ctx.message.delete()
        #Grab user document
        doc = self.users_col.find_one({'user_id': str(ctx.author.id)})
        #Make sure it exists
        if doc != None:
            #Make sure they are actually online
            if doc['online'] == True:
                if str(ctx.author.id) in self.cache.keys():
                    if self.cache[str(ctx.author.id)]['type'] == 4:
                        await ctx.author.send("<:bad:593862973274062883> `PermissionError: Invalid permissions for this action`")
                        return
                #Says saving session but actually just updates DB.. shh don't tell anyone
                await ctx.author.send("`Saving session...`")
                their_doc = {'user_id': str(ctx.author.id)}
                insert_doc = { '$set': {'online': False} }
                new_doc = self.users_col.update_one(their_doc, insert_doc)
                await ctx.author.send("`Copying shared history...\nSaving history...truncating history files...`")
                await ctx.author.send("`Completed\nDeleting expired sessions... 1 Completed`")

                #If our buddy is connected to anyone
                if str(ctx.author.id) in self.cache.keys():
                    #Grab his connection from self.cache
                    outgoing = self.cache[str(ctx.author.id)]
                    #If the type is to another PC
                    if outgoing['type'] == 1:
                        #Grab the profile of the person our buddy is connected to
                        host_doc = self.users_col.find_one({'ip':outgoing['host']})
                        if host_doc != None:
                            #Grab the member object of the person our buddy is connected to
                            host_user = discord.utils.get(self.bot.get_all_members(), id=int(host_doc['user_id']))
                            if host_user != None:
                                #Check to make sure that our buddy isn't connected to himself
                                if host_user.id != ctx.author.id:
                                    #Send dc message to person, and remove connection from self.cache
                                    await host_user.send("`LOG: User "+ str(ctx.author) + " ("+doc['ip']+") has disconnected from your network.`")
                                    del self.cache[str(ctx.author.id)]

                #Get a list of connections to our buddy typing >logout
                connections = self.get_all_connections_to(doc['ip'])
                for connection in connections:
                    print(str(connection))
                    #Send dc msg to each person connected to our buddy
                    await connection.send("`LOG: Lost connection to "+doc['ip']+"`")
                    #Remove each connection from our buddy
                    del self.cache[str(connection.id)]
                #"Saves Balance" Lol not really
                await ctx.author.send("`Saving balance... " + str(doc['balance']) + "`<:coin:592831769024397332>")
                await ctx.author.send("[Process completed]")
                print(str(ctx.author.id) + " is now offline")
            else:
                await ctx.author.send("`Your computer is not online. Please >login`")
        else:
            await ctx.author.send("`Please type >login to start your adventure!`")

    #Connects commands to people
    @commands.command(aliases=['c'])
    async def connect(self, ctx, ip : str = None):
        #Makes sure they pass the tests
        if ctx.guild != None:
            await ctx.message.delete()
        user = self.users_col.find_one({'user_id': str(ctx.author.id)})
        if user == None:
            await ctx.author.send("`Please type >login to start your adventure!`")
            return
        if user['online'] == False:
            await ctx.author.send("`Your computer is not online. Please >login`")
            return
        if ip == None:
            await ctx.author.send("<:bad:593862973274062883> `Error in command \'connect\'. An Internet Protocol Address must be provided.`")
            return
        if str(ctx.author.id) in self.cache.keys():
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
            await asyncio.sleep(self.calc_loading(user, 20))
            if ip in self.game_sites:
                #Pre-made Sites (.govs ect..)
                if ip == 'help.gov':
                    embed = discord.Embed(title="https://help.gov", description = self.help_string, color = 0x7289da)
                    await msg.edit(content="<:done:592819995843624961> `You have successfully connected to %s:`" % (ip), embed=embed)
                    self.cache[str(ctx.author.id)] = {'status': True, 'type': 2, 'host': ip}
                    return
                if ip == 'store.gov':
                    shop_string = "Welcome to the shop! Here you can buy PC upgrades, and more!\nThe stock changes every day, so make sure to come back tomorrow!\nYour balance - %s <:coin:592831769024397332>\n\n**Firewall**\nA temporary way to prevent connections and scans.\ncost: 10000 <:coin:592831769024397332> per hour\n`>purchase firewall`\n\n" % (user['balance'])
                    random.seed(self.get_day_of_year())
                    items = random.sample(self.shop_items, 5)
                    for item in items:
                        shop_string = shop_string + "**%s**\n%s - %s\ncost: %s <:coin:592831769024397332>\n`>purchase %s`\n\n" % (item['name'], item['type'], str(item['system']), str(item['cost']), item['name'])

                    embed = discord.Embed(
                        title = "https://store.gov",
                        description = shop_string,
                        color = 0x7289da
                    )
                    await msg.edit(content="<:done:592819995843624961> `You have successfully connected to %s:`" % (ip), embed=embed)
                    self.cache[str(ctx.author.id)] = {'status': True, 'type': 2, 'host': ip}
                    return
                if ip == 'mail.gov':
                    email = user['email']
                    mail_string = "Hi, this is mail.gov, Here you can see your inbox, and send messages. \nUse the `>send <email> <message>` command to send an email!\n\n**inbox for %s**\n```" % (email)
                    mails = self.mail_col.find({'to': email})
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
                    self.cache[str(ctx.author.id)] = {'status': True, 'type': 2, 'host': ip}
                    return
                if ip == '0.0.0.1':
                    embed = discord.Embed(
                        title = "Discord Hack Week",
                        description = "Thank You so much Discord Hack week for making this be possible.\nWe couldn't have done it withough you!",
                        color = 0x7289da
                    )
                    await msg.edit(content="<:done:592819995843624961> `You have successfully connected to %s`" % (ip), embed = embed)
                    self.cache[str(ctx.author.id)] = {'status': True, 'type': 2, 'host': ip}
                    return
                if ip == 'wumpushack.com':
                    embed = discord.Embed(
                        title = "**Coming Soon! 🔗**",
                        url = "http://wumpushack.com",
                        color = 0x7289da
                    )
                    await msg.edit(content="<:done:592819995843624961> `You have successfully connected to %s`" % (ip), embed = embed)
                    self.cache[str(ctx.author.id)] = {'status': True, 'type': 2, 'host': ip}
                    return
                if ip == 'bank.gov':
                    embed = discord.Embed(
                        title = "https://bank.gov",
                        description = "Welcome to Bank.gov\n\nYour Balance:\n `" + str(user['balance']) + "`<:coin:592831769024397332>\n\n**Pay** - Send Money to other players:\n`>pay <Email Address> <Amount>`",
                        color = 0x7289da
                    )
                    await msg.edit(content="<:done:592819995843624961> `You have successfully connected to %s`" % (ip), embed = embed)
                    self.cache[str(ctx.author.id)] = {'status': True, 'type': 2, 'host': ip}
                    return
            doc = self.users_col.find_one({'ip': ip})
            if doc != None:
                test_member = discord.utils.get(self.bot.get_all_members(), id=int(doc['user_id']))
                if test_member == None:
                    await msg.edit(content="<:bad:593862973274062883> `TimeoutError: Server did not respond.`")
                    return

                if doc['online'] == False:
                    await msg.edit(content="<:done:592819995843624961> `TimeoutError: Server did not respond.`")
                    return
                elif doc['network']['firewall'] != False:
                    await msg.edit(content="<:done:592819995843624961> `PacketRefusal: Packets have been blocked by firewall.`")
                    return
                else:
                    await msg.edit(content="<:done:592819995843624961> `You have successfully connected to %s:`" % (ip))
                    await ctx.author.send("```" + doc['connect_msg'] + "```")
                    self.cache[str(ctx.author.id)] = {'status': True, 'type': 1, 'host': ip}
                    try:
                        host_user = discord.utils.get(self.bot.get_all_members(), id=int(doc['user_id']))
                        connecting_user = self.users_col.find_one({'user_id': str(ctx.author.id)})
                        if host_user != None:
                            await host_user.send("`LOG: user "+ str(ctx.author) + " ("+connecting_user['ip']+") has connected to your network.`")
                    except Exception as e:
                        print(e)
            else:
                await msg.edit(content="<:bad:593862973274062883> `TimeoutError: Server did not respond.`")

    #Disconnect command
    @commands.command(aliases=['dc'])
    async def disconnect(self, ctx):
        #When u wanna go bye bye
        if ctx.guild != None:
            await ctx.message.delete()
        #Mhm grab user
        user = self.users_col.find_one({'user_id': str(ctx.author.id)})
        #Bruh this kid don't exist
        if user == None:
            await ctx.author.send("`Please type >login to start your adventure!`")
            return

        #Make sure they arent trying to get out of a breach
        elif str(ctx.author.id) in self.cache.keys():
            if self.cache[str(ctx.author.id)]['type'] == 4:
                await ctx.author.send("<:bad:593862973274062883> `PermissionError: Invalid permissions for this action`")
                return

            #Send confirmation
            await ctx.author.send("<:done:592819995843624961> `Disconnected from host %s`" % (self.cache[str(ctx.author.id)]['host']))

            #Get the user thay are connected to
            doc = self.users_col.find_one({'ip': self.cache[str(ctx.author.id)]['host']})
            if doc != None:
                host_user = discord.utils.get(self.bot.get_all_members(), id=int(doc['user_id']))
                connecting_user = self.users_col.find_one({'user_id': str(ctx.author.id)})
                if host_user != None:
                    #Send message to connected user
                    await host_user.send("`LOG: user "+ str(ctx.author) + " ("+connecting_user['ip']+") has disconnected from your network.`")

            #Actually remove connection
            del self.cache[str(ctx.author.id)]
            return
        else:
            #Lol
            await ctx.author.send("<:bad:593862973274062883> `SocketError: Not connected to any network.`")
            return

    #Scan for people who exist
    @commands.command(aliases=['scrape'])
    async def scan(self, ctx):
        if ctx.guild != None:
            await ctx.message.delete()

        #Get a profile
        user = self.users_col.find_one({'user_id': str(ctx.author.id)})
        #Make sure they exist
        if user == None:
            await ctx.author.send("`Please type >login to start your adventure!`")
            return
        #Make sure they are online
        if user['online'] == False:
            await ctx.author.send("`Your computer is not online. Please >login`")
            return
        #make sure they aren't already connected somewhere
        if str(ctx.author.id) in self.cache.keys():
            await ctx.author.send("<:bad:593862973274062883> `PortBindError: Port already in use. Use >disconnect to free up a port.`")
            return
        #Calls for loading time
        time_ = self.calc_loading(user, 120)
        msg = await ctx.author.send("<a:loading2:592819419604975797> `Scraping for IP addresses. ( This will take around %s Second(s) )`" % round(time_))

        #Set connection so they cant do other stuff
        self.cache[str(ctx.author.id)] = {'status': True, 'type': 3, 'host': "using network card to scan for IPs"}

        #Shhh its not actually doing anything... it can do it in milliseconds lol
        await asyncio.sleep(time_)

        #If they disconnected from scanning (decided to cancel)
        if str(ctx.author.id) not in self.cache.keys():
            return
        #Remove that conenction
        del self.cache[str(ctx.author.id)]

        #Decide if we should reward their patience with nothing
        if random.randint(1, 5) == 2:
             await msg.edit(content="<:done:592819995843624961> `Scrape returned (0) addresses`")
             return

        #Gets all the DB docs. yay
        all_docs = self.users_col.find({})
        doc = None

        #Make sure you get an IP hats not yours
        try:
            doc = self.users_col.find({'online': True, 'ip': {'$nin': [user['ip']] }})
            if doc.count() < 2:
                doc = doc[0]
            else:
                doc = doc[random.randrange(doc.count()) - 1]
        except:
            await msg.edit(content="<:done:592819995843624961> `Scrape returned (0) addresses`")
            return

        #Let the user know
        await msg.edit(content="<:done:592819995843624961> `Scrape returned (1) address: %s`" % (doc['ip']))

        #Oh yeah, tells the guy you just pinged that their IP is leaked...
        host_user = discord.utils.get(self.bot.get_all_members(), id=int(doc['user_id']))
        if host_user != None:
            await host_user.send("`LOG: Recived ping from host "+user['ip']+"`")


    @commands.command()
    async def help(self, ctx):
        if ctx.guild != None:
            await ctx.message.delete()

        embed = discord.Embed(
            title = "WumpOS User Manual",
            description = "Thank you for purchasing your new Wumpus system. Your Wumpus system is the way you can communicate with the world! Your computer is started, and ready to roll! Connect to your nation's help system to get the hang of things. \n(>connect help.gov)\n\nYour PC currently has pretty lame parts. Don't you want a god PC? Well first things first, you need money. Why don't you hack into some people by first getting their IP using `>scan`, and then connecting to them using `>connect <ip>`. After that, you can start a breach using `>breach`. If you can win, then you can steal some of their cash!\n\nWhen you have some cash, try visiting the the store (`>connect store.gov`) and looking at what is available that day. Taking a look at the bank is a good idea as well. Oh, and dont forget to check your mail!\n\noh! side note, Your PC parts actually do something! Each Tick (10s), you gain <:coin:592831769024397332> based on the GHz of your GPU. Every loading time, is based off your CPU, and the amount of money that you can steal from a user is based on your RAM. so, get to hacking!\n\n*if you ever need this message again, use >help*",
            color = 0x35363B
        )
        await ctx.author.send(embed=embed)

    #We just got a letter, we just got a letter, we just got a letter. I wonder who its from? LOL
    @commands.command()
    async def inbox(self, ctx):
        user = self.users_col.find_one({'user_id': str(ctx.author.id)})
        #Online
        if user['online'] == False:
            await ctx.author.send("`Your computer is not online. Please >login`")
            return
        #Make sure connected
        elif str(ctx.author.id) not in self.cache:
            raise commands.CommandNotFound
            return
        #Make sure connected to mail.gov as this command is only run when connected to that game service
        elif self.cache[str(ctx.author.id)]['host'] != 'mail.gov':
            raise commands.CommandNotFound
            return

        #Deleteet begon guild message
        elif ctx.guild != None:
            await ctx.message.delete()

        #Basic stuff u should know by now
        elif user == None:
            await ctx.author.send("`Please type >login to start your adventure!`")
            return
        elif user['online'] == False:
            await ctx.author.send("`Your computer is not online. Please >login`")
            return
        elif str(ctx.author.id) not in self.cache:
            await ctx.author.send("<:bad:593862973274062883> `SocketError: Not connected to Network`")
            return
        else:
            #Get their email address
            email = user['email']
            #Basic email string
            mail_string = "Hi, this is mail.gov, Here you can see your inbox, and send messages. \nUse the `>send <email> <message>` command to send an email!\n\n**inbox for %s**\n```" % (email)

            #Get every mail document in DB thats for them
            mails = self.mail_col.find({'to': email})
            if mails.count() < 1:
                #;(
                mail_string = mail_string + "\nYour inbox is empty :)\n"
            else:
                #For every mail document, add a bit to the string
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
    @commands.command()
    async def clear(self, ctx):
        #Basic stuff in every command...
        user = self.users_col.find_one({'user_id': str(ctx.author.id)})
        if user['online'] == False:
            await ctx.author.send("`Your computer is not online. Please >login`")
            return
        elif str(ctx.author.id) not in self.cache:
            raise commands.CommandNotFound
            return
        elif self.cache[str(ctx.author.id)]['host'] != 'mail.gov':
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
        elif str(ctx.author.id) not in self.cache:
            await ctx.author.send("<:bad:593862973274062883> `SocketError: Not connected to Network`")
            return
        else:
            #R u surreeeee?
            await ctx.author.send("`LOG: (mail.gov) Are you sure you want toclear your inbox? Respond with 'Y' or 'N'`")

            #Makes infinite loop so that they can make SURE that they want to clear their beloved inbox
            while True:
                msg = await self.bot.wait_for('message')
                #Make sure msg is in the right place
                if msg.content.lower() == "y" and msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id:
                    mails = self.mail_col.find({'to': user['email']})
                    if mails.count() > 0:
                        self.mail_col.delete_many({'to': user['email']})

                        #Send inbox again
                        email = user['email']
                        mail_string = "Hi, this is mail.gov, Here you can see your inbox, and send messages. \nUse the `>send <email> <message>` command to send an email!\n\n**inbox for %s**\n```" % (email)
                        mails = self.mail_col.find({'to': email})
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

    #Send Email :D
    @commands.command()
    async def send(self, ctx, mail_to:str=None, *, msg:str=None):
        user = self.users_col.find_one({'user_id': str(ctx.author.id)})
        if user['online'] == False:
            await ctx.author.send("`Your computer is not online. Please >login`")
            return
        if str(ctx.author.id) not in self.cache:
            raise commands.CommandNotFound
            return
        elif self.cache[str(ctx.author.id)]['host'] != 'mail.gov':
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
        if str(ctx.author.id) not in self.cache:
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
            reciver = self.users_col.find_one({'email': mail_to})
            if reciver != None:
                email = user['email']

                #make mail document and insert it into the mail collection in the DB.. god i love Mongo <3
                mail_doc = {'to': mail_to, 'from': email, 'content': msg}
                self.mail_col.insert_one(mail_doc)
                await ctx.author.send("`LOG: (mail.gov) email has been sent.`")

                #send the reciving user a little ping if they have it enabled (>sys notify)
                if reciver['notify'] == False:
                    return
                else:
                    emailperson = discord.utils.get(self.bot.get_all_members(), id= int(reciver['user_id']))
                    if emailperson != None:
                        # Flashback to AOL lol
                        await emailperson.send("`LOG: (mail.gov) You've Got Mail`")
            else:
                #welp... they dont exist
                await ctx.author.send("`LOG: (mail.gov) email does not exist`")

    #Pay Command
    @commands.command()
    async def pay(self, ctx, email:str=None, amount:float=None):
        #Grabs all profiles needed for this command
        author = self.users_col.find_one({'user_id': str(ctx.author.id)})
        user = self.users_col.find_one({'email': email})

        if ctx.guild != None:
            await ctx.message.delete()
        if author == None:
            await ctx.author.send("`Please type >login to start your adventure!`")
            return
        if author['online'] == False:
            await ctx.author.send("`Your computer is not online. Please >login`")
            return
        if str(ctx.author.id) not in self.cache.keys():
            raise commands.CommandNotFound
            return

        #Need to be connected to teh bank
        elif self.cache[str(ctx.author.id)]['host'] != 'bank.gov':
            raise commands.CommandNotFound
            return

        #If anything went wrong grabbing users just cancel
        if user == None or author == None or amount == None:
            await ctx.author.send("`LOG: (bank.gov) error in command`")
            return

        #make sure its a whole number before the tests
        amount = round(amount)

        #Check if they are a cheapskate
        if amount > author['balance']:
            await ctx.author.send("`LOG: Insufficient Funds`")
            return
        #No Cheapo
        if amount <= 1:
            await ctx.author.send("`LOG: (bank.gov) Amount must be above 1`")
            return


        #Take from one, and give to the other. Notify self.both parties.
        user_member = discord.utils.get(self.bot.get_all_members(), id = int(user['user_id']))



        if user_member == None:
            await ctx.author.send("`LOG: (bank.gov) User not found.`")
            return

        self.users_col.update_one({'user_id': author['user_id']}, {'$set': {'balance': author['balance'] - amount}})
        self.users_col.update_one({'user_id': user['user_id']}, {'$set': {'balance': author['balance'] + amount}})
        await ctx.author.send("`LOG: (bank.gov) Sent "+ email + " " + str(amount) + "`<:coin:592831769024397332>")
        await user_member.send("`LOG: (bank.gov) You have recived " + str(amount) + "` <:coin:592831769024397332> `From: " + author['email'] + "`")

    @commands.Cog.listener()
    async def on_message(self, message):
        #Just a handy debug tool.
        if message.content.startswith(">"):
            print("Command: " + message.content)
            print("User: " + str(message.author))

    #Purchase command
    @commands.command()
    async def purchase(self, ctx, *, id:str=None):
        user = self.users_col.find_one({'user_id': str(ctx.author.id)})
        if user['online'] == False:
            await ctx.author.send("`Your computer is not online. Please >login`")
            return
        if str(ctx.author.id) not in self.cache:
            raise commands.CommandNotFound
            return
        #Must be at the store to buy things
        elif self.cache[str(ctx.author.id)]['host'] != 'store.gov':
            raise commands.CommandNotFound
            return


        #Set the python random gen seed, and grab the first 5 items of the day
        random.seed(self.get_day_of_year())
        items = random.sample(config.shop_items, 5)

        if ctx.guild != None:
            await ctx.message.delete()
        if user == None:
            await ctx.author.send("`Please type >login to start your adventure!`")
            return
        if user['online'] == False:
            await ctx.author.send("`Your computer is not online. Please >login`")
            return
        if str(ctx.author.id) not in self.cache:
            await ctx.author.send("<:bad:593862973274062883> `SocketError: Not connected to Network`")
            return

        #Thats not a product!
        elif id == None:
            await ctx.author.send("`LOG: (store.gov) Please specify an ID to purchase`")
            return

        #Check to see if the Item they specified is in today's list of items
        elif any(d['name'] == id for d in items):

            #Grab that item object
            item = None
            for i in items:
                if i['name'] == id:
                    item = i
            if item == None:
                await ctx.author.send("`LOG: (store.gov) unknown error occured when finding item.")
                return

            await ctx.author.send("`LOG: (store.gov) Are you sure you want to purchase this item? Respond with 'Y' or 'N'`")

            #Start loop
            while True:
                msg = await self.bot.wait_for('message')
                if msg.content.lower() == "y" and msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id:
                    #Check for enough cash
                    if user['balance'] >= item['cost']:
                        # create a new PC dict
                        user['inventory'].append(item)

                        # udate the document in the database
                        self.users_col.update_one({'user_id': str(ctx.author.id)}, {'$set':{'balance': user['balance'] - item['cost'], 'inventory': user['inventory']}})

                        #send confirmation message
                        await ctx.author.send("`LOG: (store.gov)` You have just purchased " + id + " for " + str(item['cost']) + "` <:coin:592831769024397332> `. You can view it in your Inventory.`")
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
                await ctx.author.send("`LOG: (store.gov) Are you sure you want to purchase this item? Respond with 'Y' or 'N'`")

                #Start loop
                while True:
                    msg = await self.bot.wait_for('message')
                    if msg.content.lower() == "y" and msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id:
                        # check for enough cash
                        if user['balance'] >= 10000:

                            #Create a new NET dict
                            new_network = user['network']

                            #Check if there is already a timer started, if so, add one hour to existing timer.
                            if new_network['firewall'] != False:
                                new_network['firewall'] = float(new_network['firewall']) + 3600

                            else:
                                #Otherwise, just add a timer oh 1 hour.
                                new_network['firewall'] = str(time.time() + 3600)

                            #Update dict in databse with timer set to one hour in the future
                            self.users_col.update_one({'user_id': str(ctx.author.id)}, {'$set': {'network': new_network, 'balance': user['balance'] - 10000}})

                            #Send confirmation message
                            await ctx.author.send("`LOG: (store.gov) You have just purchased 'One hour of Firewall protection' for 10000 ` <:coin:592831769024397332>!")
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
    @commands.group(aliases=['sys', 'stats'])
    async def system(self, ctx):
        if ctx.invoked_subcommand is None:
            if ctx.guild != None:
                await ctx.message.delete()

            #Get user docuemnt from DB and check if they have an account
            doc = self.users_col.find_one({'user_id': str(ctx.author.id)})
            if doc == None:
                await ctx.author.send("`Please type >login to start your adventure!`")
                return

            #Check for online status
            if doc['online'] == False:
                await ctx.author.send("`Your computer is not online. Please >login`")
                return

            else:
                #Display firewall cooldown if active
                if doc['network']['firewall'] != False:
                    firewall_time = round(float(doc['network']['firewall'])  - time.time())
                    doc['network']['firewall'] = "Expires in " + time.strftime('%Hh%Mm%Ss', time.gmtime(firewall_time))

                #Base system display with PC specs and such
                sys_string = "**__Computer Information__**\n**RAM** - "+str(doc['pc']['ram'])+ " GB\n**CPU** - "+str(doc['pc']['cpu'])+" GHz `"+doc['pc']['cpu_name']+"`\n**GPU** - "+str(doc['pc']['gpu'])+" GHz `"+doc['pc']['gpu_name']+"`\n\n**__Network Information__**\n**Bandwidth** - "+str(doc['network']['bandwidth'] + 10   )+" Mbps\n**Firewall** - "+str(doc['network']['firewall'])+"\n**IP Address** - ||"+doc['ip']+"||\n\n**__Other Information__**\n**Balance** - "+str(round(doc['balance']))+" <:coin:592831769024397332>\n**Connection Message** - "+doc['connect_msg']

                if str(ctx.author.id) in self.cache.keys():
                    #Grab hosts info to display
                    host_email = self.users_col.find_one({'ip': self.cache[str(ctx.author.id)]['host']})
                    sys_string = sys_string + "\n\n**__Connection__**\n**Host** - "+self.cache[str(ctx.author.id)]['host']

                    #Show email if connected to PC
                    if self.cache[str(ctx.author.id)]['type'] == 1 and host_email != None:
                        sys_string = sys_string + "\n**Host's Email** - "+str(host_email['email'])

                #Show breach duration if they have a cooldown active
                if doc['breach'] != False and doc['breach'] != True:
                    breach_time = "Expires in " + time.strftime('%Hh%Mm%Ss', time.gmtime(round(float(doc['breach'])  - time.time())))
                    sys_string = sys_string + "\n\n**Breach Cooldown** - " + breach_time

                embed = discord.Embed(
                    title = "System Information",
                    description = sys_string,
                    color = 0x7289da
                )
                #Send message
                msg = await ctx.author.send("<a:loading2:592819419604975797> `Obtaining system information...`")
                await asyncio.sleep(self.calc_loading(doc, 5))
                await msg.edit(content="<:done:592819995843624961> `System information retreived`", embed=embed)

    @system.command()
    async def use(self, ctx, id:str=None):
        if ctx.guild != None:
            await ctx.message.delete()

        user = self.users_col.find_one({'user_id': str(ctx.author.id)})
        if user == None:
            await ctx.author.send("`Please type >login to start your adventure!`")
            return

        if user['online'] == False:
            await ctx.author.send("`Your computer is not online. Please >login`")
            return


        try:
            id = int(id)
        except:
            await ctx.author.send("`ERROR: component ID is not valid.`")
            return

        new_pc = user['pc']
        new_pc[user['inventory'][id]['type']] = user['inventory'][id]['system']
        new_pc[user['inventory'][id]['type'] + '_name'] = user['inventory'][id]['name']
        self.users_col.update({'user_id': user['user_id']}, {'$set': { 'pc': new_pc}})
        await ctx.author.send("`LOG: switched %s %s with %s`" % (user['inventory'][id]['type'].upper(), user['pc'][user['inventory'][id]['type'] + '_name'], new_pc[user['inventory'][id]['type'] + '_name']))


    @system.command()
    async def notify(self, ctx):
        if ctx.guild != None:
            await ctx.message.delete()

        user = self.users_col.find_one({'user_id': str(ctx.author.id)})
        if user == None:
            await ctx.author.send("`Please type >login to start your adventure!`")
            return

        if user['online'] == False:
            await ctx.author.send("`Your computer is not online. Please >login`")
            return

        #Create field in DB if not already there
        if 'notify' not in user.keys():
            self.users_col.update_one(user, {'$set': {'notify': True}})
            await ctx.author.send("`LOG: Notifications are now set to: True`")
        else:
            #Toggle the value in the DB
            self.users_col.update_one(user, {'$set': {'notify': not user['notify']}})
            await ctx.author.send("`LOG: Notifications are now set to: %s`" % (str(not user['notify'])))



    @commands.command(aliases=['hack', 'br', 'ddos'])
    async def breach(self, ctx):
        #Not the best way to do this, but.. I didn't do it (kaj) and it works. and we only have a week.
        user = self.users_col.find_one({'user_id': str(ctx.author.id)})

        #Make sure they dont have a cooldown False = no cooldown, timestamp - cooldown
        if user['breach'] == False:
            if ctx.guild != None:
                await ctx.message.delete()
            if user == None:
                await ctx.author.send("`Please type >login to start your adventure!`")
                return
            if user['online'] == False:
                await ctx.author.send("`Your computer is not online. Please >login`")
                return
            if str(ctx.author.id) not in self.cache:
                await ctx.author.send("<:bad:593862973274062883> `SocketError: Not connected to Network`")
                return

            #If they arent a PC, then u cant hack it
            if self.cache[str(ctx.author.id)]['type'] != 1:
                await ctx.author.send("<:bad:593862973274062883> `Error: Server refused packets`")
                return

            #If they are already in a breach, you cant hack them again.
            if self.cache[str(ctx.author.id)]['type'] == 4:
                await ctx.author.send("<:bad:593862973274062883> `Error: Port already open.`")
                return


            host_doc = self.users_col.find_one({'ip': self.cache[str(ctx.author.id)]['host']})
            if host_doc != None:
                host_member = discord.utils.get(self.bot.get_all_members(), id=int(host_doc['user_id']))
                if host_member != None:

                    #Checks if host is already being breached
                    if str(host_member.id) in self.cache.keys():
                        if self.cache[str(host_member.id)]['type'] == 4:
                            await ctx.author.send("`LOG: Error sending breach packets`")
                            return
                    #Sets connection as to not let you >dc or >logout
                    self.cache[str(host_member.id)] = {'status': False, 'type': 4, 'host': "**BREACH**"}
                    breacher = ctx.author

                    #Give a cooldown now in case something happens
                    hackercooldownadd = { '$set': {'breach': str(time.time() + 600)}}
                    givecooldown = self.users_col.update_one({'user_id': str(breacher.id)}, hackercooldownadd)

                    #Send the host a message, and start the show!
                    await ctx.author.send("`BREACH: A breach attack has been started... Sent initiation packets, awaiting host.`")
                    await self.breach_host(host_member, host_doc, ctx, user, breacher)
                else:
                    await ctx.author.send("<:bad:593862973274062883> `Error: Unknown error in getting user`")
            else:
                await ctx.author.send("<:bad:593862973274062883> `Error: Unknown error in getting document`")
        else:
            await ctx.author.send("<:bad:593862973274062883> `INFO: Your Breach Cooldown is still in effect.`")

    #Gets a random question, and answer from an API. with a backup
    def get_random_q_a(self):
        cat = self.categories[random.randint(0, len(self.categories) - 1)]
        dif = self.difficulties[random.randint(0, len(self.difficulties) - 1)]
        tr = self.Trivia.request(1, cat, dif, Type.Multiple_Choice)
        #Error handle
        if tr['response_code'] != 0:
            print("API error in getting question")
            answer = 4
            question = "What is 2 + 2"
            all_a = "4, 3, 6, 8"
            catstring = "Math"

        else:
            #Regular day
            answer = tr['results'][0]['correct_answer']
            question = tr['results'][0]['question']
            all_a = ""
            catstring = str(tr['results'][0]['category'])
            #Take all valid responses, and randomise order, and turn into one string.
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

        #Always give question and answer
        return catstring, all_a, question, answer

    #The functiuons nthat we may or may not use (Spoiler alert we do)
    async def breach_starter(self, host_member, host_doc, ctx, user, breacher):
        #Ugh welp.. good luck understanding this tbh

        #Get basic stuff
        bypassed = False
        catstring, all_a, question, answer = self.get_random_q_a()
        doc = user
        print(answer)
        time_ = self.calc_time(doc)
        #Send initial question
        await breacher.send("`RETALIATION: ("+host_doc['ip']+") "+str(question)+"\n\nYour Choices:\n"+ str(all_a)+ "\n\nYou have %s seconds, or the breach fails`" % (str(time_)))
        correct = False #Does self.Trivia Stuff

        #Start loop checkign for answer
        while correct == False:
            try:
                msg = await self.bot.wait_for('message', timeout=time_)
                if  msg.author.id == breacher.id and msg.channel.id == breacher.dm_channel.id:
                    if msg.content.lower() == str(answer).lower():
                        #They did it! Bounce question back to breach person
                        await breacher.send("`BREACH: Correct, retaliation sent.`")
                        correct = True
                        bypassed = True
                        break
                    else:
                        #Not right, re loop
                        await breacher.send("<:bad:593862973274062883>`BREACH: Error, incorrect. re-submit answer.`")
                        correct = False
                else:
                    continue
            except:
                bypassed = False
                break
        if bypassed == True:
            #They did it! call other function
            await self.breach_host(host_member, host_doc, ctx, user, breacher)
        if bypassed == False:
            #Well shit they didn't answer in time. do all this message garbage VVV

            #Remove connections first
            del self.cache[str(breacher.id)]
            del self.cache[str(host_member.id)]

            #Send a ton of stuff with information about end of breach
            await breacher.send("`BREACH FAILED: (You did not answer the Trivia problem in time, the breach has failed.)`")
            await host_member.send("`BREACH BLOCKED: (The breach has been stopped by your defenses)`")
            await breacher.send("`INFO: A Cooldown for Breaching has been set on your account for 10 minutes.`")
            await host_member.send("`LOG: %s has been disconnected.`" % (user['ip']))
            await breacher.send("`LOG: %s has disconnected you from their network.`" % (host_doc['ip']))

            #Add cooldown
            hackercooldownadd = { '$set': {'breach': str(time.time() + 600)}}
            givecooldown = self.users_col.update_one({'user_id': str(breacher.id)}, hackercooldownadd)


    async def breach_host(self, host_member, host_doc, ctx, user, breacher):
        #Ok now back to the breacher guy. this function is identical to the last, except for which side its for.
        bypassed = False
        catstring, all_a, question, answer = self.get_random_q_a()
        print(answer)
        doc = host_doc
        time_ = self.calc_time(doc)
        await host_member.send("`BREACH: ("+user['ip']+") "+str(question)+"\n\nYour Choices:\n"+ str(all_a)+ "\n\nYou have "+str(time_)+" seconds, or "+str(user['pc']['ram'] * 1.9)+"% of your Funds are taken.`")
        correct = False #Does self.Trivia Stuff
        while correct == False:
            try:
                msg = await self.bot.wait_for('message', timeout=time_)
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
            await self.breach_starter(host_member, host_doc, ctx, user, breacher)

        if bypassed == False:
            #They breached it! Take the money, and logout the breached persons PC to prevent them from being hacked again
            await host_member.send("`DEFENSE FAILED: (You did not answer the Trivia question in time, your computer is compromized.)`")
            await breacher.send("`BREACH SUCCESFUL: (You have compromized the host's Computer, "+str(user['pc']['ram'] * 1.9)+"% of their funds will be moved into your account.)`")
            hacker = self.users_col.find_one({'user_id': str(breacher.id)})#Gets Hackers Document
            victim = self.users_col.find_one({'user_id': str(host_member.id)})#Gets Victims Document
            victims_funds = victim['balance']#Gets current balance
            ammount_toTake = int(victims_funds) / (user['pc']['ram'] * 1.9)

            #make sure its a whole number
            ammount_toTake = round(ammount_toTake)

            #Transfers Money
            victims_oldfunds = {'user_id': str(host_member.id)}
            victims_newFunds = { '$set': {'balance': int(victim['balance']) - ammount_toTake}}
            newvictim = self.users_col.update_one(victims_oldfunds, victims_newFunds)
            hackers_oldfunds = {'user_id': str(breacher.id)}
            hackers_newFunds = { '$set': {'balance': int(hacker['balance']) + ammount_toTake}}
            newhacker = self.users_col.update_one(hacker, hackers_newFunds)
            await host_member.send("`BREACH: "+str(ammount_toTake)+"`<:coin:592831769024397332>` has been taken from your account.` ")
            await breacher.send("`BREACH: "+str(ammount_toTake)+"`<:coin:592831769024397332>` has been tranferred to your account.` ")
            #Redoes logout to stop more hacking to 1 user


            doc = victim
            if doc != None:
                if doc['online'] == True:
                    await host_member.send("**`Emergency shutdown initiated...`**")
                    await host_member.send("`Saving session...`")
                    their_doc = {'user_id': str(host_member.id)}
                    insert_doc = { '$set': {'online': False} }
                    new_doc = self.users_col.update_one(their_doc, insert_doc)
                    await host_member.send("`Copying shared history...\nSaving history...truncating history files...`")
                    await host_member.send("`Completed\nDeleting expired sessions... 1 Completed`")
                    del self.cache[str(host_member.id)]

                    #Get a list of connections to our buddy after the breach
                    connections = self.get_all_connections_to(doc['ip'])
                    for connection in connections:
                        print(str(connection))
                        #Send dc msg to each person connected to our buddy.
                        await connection.send("`LOG: Lost connection to "+doc['ip']+"`")
                        #Remove each connection from our buddy and from each person
                        del self.cache[str(connection.id)]


                    await host_member.send("`Saving balance... " + str(victim['balance'] - ammount_toTake) + "`<:coin:592831769024397332>")
                    await host_member.send("[Process completed]")
                    print(str(host_member.id) + " is now offline")
                else:
                    await host_member.send("`Your computer is not online. Please >login`")
            else:
                await host_member.send("`Please type >login to start your adventure!`")


            await breacher.send("`INFO: A Cooldown for Breaching has been set on your account for 10 minutes.`")
            hackercooldownadd = { '$set': {'breach': str(time.time() + 600)}}
            givecooldown = self.users_col.update_one(hackers_oldfunds, hackercooldownadd)

    #Edit connection message
    @system.command()
    async def editcm(self, ctx, *, message = None):
        #Simple command to edit what people see when they connect to you
        if ctx.guild != None:
            await ctx.message.delete()
        if message == None:
            await ctx.author.send("<:bad:593862973274062883> `LOG: Error in command 'editcm', no message provided.`")
        else:
            user = self.users_col.find_one({'user_id': str(ctx.author.id)})
            if user == None:
                await ctx.author.send("`Please type >login to start your adventure!`")
                return
            if user['online'] == False:
                await ctx.author.send("`Your computer is not online. Please >login`")
                return
            else:
                self.users_col.update_one({'user_id': str(ctx.author.id)}, { '$set': {'connect_msg': message }})
                await ctx.author.send("`LOG: Updated connection message: %s`" % (message))


    @commands.command(name='print', aliases=['log', 'pr'])
    async def _print(self, ctx, *, msg:str=None):
        #Prints messages to peoples consoles. If your connected to a User, and not in a breach, you can log to their PC, meaning send msgs back and forth
        if ctx.guild != None:
            await ctx.message.delete()
        user = self.users_col.find_one({'user_id': str(ctx.author.id)})
        if user == None:
            await ctx.author.send("`Please type >login to start your adventure!`")
            return
        if user['online'] == False:
            await ctx.author.send("`Your computer is not online. Please >login`")
            return

        #Cant send ""
        if msg == None:
            await ctx.author.send("<:bad:593862973274062883> `Error in command \'print\'. A message must be provided.`")
            return

        #Check if anyone is connected to them, and send message
        if str(ctx.author.id) not in self.cache.keys():
            #Search through all connections
            for key, value in self.cache.items():
                if key == 'away':
                    continue

                #If IPs match
                if value['host'] == user['ip']:
                    #Get user
                    host_user = discord.utils.get(self.bot.get_all_members(), id=int(key))
                    if host_user != None:
                        #Send message
                        await host_user.send("`LOG: ("+value['host']+") "+msg+"`")

            await ctx.author.send("`LOG: ("+user['ip']+") "+msg+"`")

        else:
            #Check if they are connected to anyone and send message AND if anyone is connected to them
            doc = self.users_col.find_one({'ip': self.cache[str(ctx.author.id)]['host']})
            if doc != None:
                #Search through all connections
                for key, value in self.cache.items():
                    if key == 'away':
                        continue
                    #Matching IPs awww <3
                    if value['host'] == doc['ip']:
                        host_user = discord.utils.get(self.bot.get_all_members(), id=int(key))
                        if host_user.id == ctx.author.id:
                            await host_user.send("`LOG: ("+user['ip']+") "+msg+"`")
                            continue
                        if host_user != None:
                            await host_user.send("`LOG: ("+value['host']+") "+msg+"`")

                if str(ctx.author.id) in self.cache.keys():
                    host_user = discord.utils.get(self.bot.get_all_members(), id=int(doc['user_id']))
                    if host_user != None:
                        await host_user.send("`LOG: ("+user['ip']+") "+msg+"`")
                    return

            else:
                #if it is some service, or not a user PC that they are connected to
                await ctx.author.send("`Error: server refused packets.`")
                return

    #self.cache
    @commands.command(name="cache")
    async def _cache(self, ctx):
        #debug command to show the self.cache in console
        print(self.cache)


    #Reset
    @commands.command()
    async def reset(self, ctx, user : discord.User = None):
        #this command isnt ready yet. and probably wont be active during hack week
        raise commands.CommandNotFound


        if ctx.guild != None:
            await ctx.message.delete()
        if user == None or ctx.author.id not in self.owner_ids:
            user = ctx.author
        await ctx.author.send("`Are you sure you would like to reset?\nReseting will reset all of your stats [Y/N]`")
        try:
            while True:
                msg = await self.bot.wait_for('message', timeout= 10)
                if "y" == msg.content.lower and msg.author.id == ctx.author.id and msg.channel.id == breacher.dm_channel.id:
                    self.users_col.delete_one({'user_id': str(user.id)})
                    an_ip = str(random.randint(1, 255)) + "." + str(random.randint(1, 255)) + "." + str(random.randint(1, 255)) + "." + str(random.randint(1, 255))
                    self.users_col.insert_one({'user_id': str(user.id), 'pc': self.basic_pc_stats, 'network': self.basic_network_stats, 'online': True, 'balance': 100, 'ip': an_ip, 'connect_msg': "Hello. I am a PC."})
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
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        #Always make sure to leave no clutter in a guild.
        if ctx.guild != None:
            await ctx.message.delete()

        #No command? *gasp*
        if isinstance(error, commands.CommandNotFound):
            await ctx.author.send('<:bad:593862973274062883> `"%s" is not recognized as an internal or external command, operable program or batch file.`' % (ctx.message.content))

        #Print the error if debug is enabled
        if config.DEBUG_STATUS == True:
            raise error


def setup(bot):
    bot.add_cog(main_commands(bot))
