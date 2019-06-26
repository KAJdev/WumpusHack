#Imports
print('Importing Libraries')
import discord, pymongo, config, asyncio, random, dns, json
from discord.ext import commands

#Prefix
print('Making Bot')
bot = commands.Bot(command_prefix = config.DEFAULT_PREFIX, case_insensitive = True)

#Main cache
cache = {'away': {}}

#Version
version = "2019.1.6.4a"

#Defaults
basic_pc_stats = {'ram': 1, 'cpu': 1, 'gpu': 1}
basic_network_stats = {'bandwidth': 1, 'ddos_pro': False, 'firewall': False}
game_sites=['help.gov', 'store.gov', '0.0.0.1']

owner_ids = [229695200082132993, 245653078794174465, 282565295351136256]
help_string = "**__Commands__**\n**Connect** - Connects to another PC.\n**Disonnect** - Disconnects from another PC.\n**Editcm** - Edits your connection message.\n**Github** - Sends a link to the github repository.\n**Invite** - Sends a link to invite me.\n**Login** - Logs onto your computer.\n**Logout** - Logs out of your computer.\n**Reset** - Resets all of your stats\n**Support** - Sends an invite link to the support server.\n**System / Stats / Sys** - Shows your system information.\n\n**__Government websites__**\n**store.gov** - Shows the store."
shop_string = "**__System Upgrades__**\n**Firewall**\nCost - 5000 <:coin:592831769024397332>\n`Stops connections to your IP address.`\n`ID - 1`\n\n**DDOS Protection**\nCost - 5000 <:coin:592831769024397332>\n`Protection from DDOS attacks.`\n`ID - 2`\n\n**__PCs__**\n**Medium-end PC**\nCost - 10000 <:coin:592831769024397332>\n`ID - 3`\n\n**High-end PC**\nCost - 20000 <:coin:592831769024397332>\n`ID - 4`"

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
print("bot connected to database. users: " + str(users_col.count()))

@bot.event
async def on_member_update(before, after):
    if before.status != after.status:
        if str(after.status) == "offline":
            if str(after.id) not in cache['away']:
                doc = users_col.find_one({'user_id': str(after.id)})
                if doc != None:
                    cache['away'][str(after.id)] = doc['balance']
                    print("cached " + str(after))

        elif str(before.status) == 'offline':
            if str(after.id) in cache['away']:
                doc = users_col.find_one({'user_id': str(after.id)})
                if doc != None:
                    difference = doc['balance'] - cache['away'][str(after.id)]
                    del cache['away'][str(after.id)]
                    embed = discord.Embed(
                        title = "Report",
                            description = "Actions have taken place since you were away.\nYou have gained %s <:coin:592831769024397332>." % (difference),
                        color = 0x35363B
                    )
                    if doc['online'] == True:
                        await after.send(embed=embed)
                    print(str(after) + " woke up")



#On ready
@bot.event
async def on_ready():
    print("Bot is ready and online.")
    print("servers: %s, ping: %s ms" % (len(bot.guilds), bot.latency * 1000))
    await bot.user.edit(username="WumpusOS Terminal v"+version)
    for member in bot.get_all_members():
        if str(member.status) == 'offline':
            doc = users_col.find_one({'user_id': str(member.id)})
            if doc != None:
                if str(member.id) not in cache['away']:
                    cache['away'][str(member.id)] = doc['balance']
                    print("cached " + str(member))


@bot.event
async def on_guild_join(guild):
    await guild.me.edit(nick="WumpusHack")
    print("WumpusHack Joined "+ str(guild))

async def tick():
    await asyncio.sleep(5)
    while not bot.is_closed():
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=">login | %s users online" % (users_col.find({'online': True}).count())))
        await asyncio.sleep(10)
        docs = users_col.find({})
        updated_count = 0
        for doc in docs:
            if doc['online'] == False:
                continue
            new_doc = { '$set': {'balance': doc['balance'] + doc['pc']['gpu']}}
            users_col.update_one(doc, new_doc)
            updated_count += 1

        print("Tick. Updated %s users." % (updated_count))

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


            global cache
            doc2 = None
            if str(ctx.author.id) in cache.keys():
                doc2 = users_col.find_one({'ip': cache[str(ctx.author.id)]['host']})

            temp_cache = cache
            for key, value in cache.items():
                if key == 'away':
                    continue
                if value['host'] == doc['ip']:
                    host_user = discord.utils.get(bot.get_all_members(), id=int(key))
                    if host_user != None:
                        await host_user.send("`LOG: host "+value['host']+" has disconnected you from their network.`")
                    del temp_cache[key]

            cache = temp_cache
            if doc2 != None:
                if str(ctx.author.id) in cache.keys():
                    host_user = discord.utils.get(bot.get_all_members(), id=int(doc2['user_id']))
                    connecting_user = users_col.find_one({'user_id': str(ctx.author.id)})
                    if host_user != None:
                        await host_user.send("`LOG: user "+ str(ctx.author) + " ("+connecting_user['ip']+") has disconnected from your network.`")

                    del cache[str(ctx.author.id)]
            else:
                if str(ctx.author.id) in cache.keys():
                    del cache[str(ctx.author.id)]



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
        await ctx.author.send("`error in command \'connect\'. An Internet Protocol Address must be provided.`")
        return
    if str(ctx.author.id) in cache.keys():
        await ctx.author.send("`PortBindError: Port already in use. Use >disconnect to free up a port.`")
        return
    if user['ip'] == ip:
        await ctx.author.send("`PortBindError: Port already in use. Cannot connect to localhost:21.`")
        return
    else:
        msg = await ctx.author.send("<a:loading2:592819419604975797> `Connecting to %s`" % (ip))
        print('User '+str(ctx.author.id)+ " is now connecting to " + ip)

        await asyncio.sleep(calc_loading(user, 10))
        if ip in game_sites:
            if ip == 'help.gov':
                embed = discord.Embed(title="https://help.gov", description = help_string, color = 0x7289da)
                await msg.edit(content="<:done:592819995843624961> `You have successfully connected to %s:`" % (ip), embed=embed)
                cache[str(ctx.author.id)] = {'status': True, 'type': 2, 'host': ip}
                return
            if ip == 'store.gov':
                embed = discord.Embed(
                    title = "https://store.gov",
                    description = shop_string,
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
            if doc['online'] == False:
                await msg.edit(content="<:done:592819995843624961> `TimeoutError: Server did not respond.`")
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
            await msg.edit(content="<:done:592819995843624961> `TimeoutError: Server did not respond.`")

@bot.command(aliases=['dc'])
async def disconnect(ctx):
    user = users_col.find_one({'user_id': str(ctx.author.id)})
    if user == None:
        await ctx.author.send("`Please type >login to start your adventure!`")
        return
    elif str(ctx.author.id) in cache.keys():
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
        await ctx.author.send("`SocketError: Not connected to any network.`")
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
        await ctx.author.send("`PortBindError: Port already in use. Use >disconnect to free up a port.`")
        return

    time_ = calc_loading(user, 600)
    msg = await ctx.author.send("<a:loading2:592819419604975797> `scraping for IP addresses. (this will take around %s minutes)`" % round(time_ / 60))

    cache[str(ctx.author.id)] = {'status': True, 'type': 3, 'host': None}
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
        count = users_col.count()
        doc = users_col.find()[random.randrange(count)]
        if doc == user:
            continue
        else:
            break
    await msg.edit(content="<:done:592819995843624961> `Scrape returned (1) address: %s`" % (doc['ip']))
    host_user = discord.utils.get(bot.get_all_members(), id=int(doc['user_id']))
    if host_user != None:
        await host_user.send("`LOG: recived ping from host "+user['ip']+"`")



@bot.command()
async def purchase(ctx, id : int = None):
    if str(ctx.author.id) not in cache:
        raise commands.CommandNotFound
        return
    elif cache[str(ctx.author.id)]['host'] != 'store.gov':
        raise commands.CommandNotFound
        return

    if id == None:
        await ctx.author.send("`error in command \'purchase\'. An Item ID must be provided.`")
        return
    else:
        pass

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
            try:
                sys_string = "**__Computer Information__**\n**Ram** - "+str(doc['pc']['ram'])+ "GB (used for programs)\n **CPU** - "+str(doc['pc']['ram'])+" GHz (used for cracking)\n **GPU** - "+str(doc['pc']['gpu'])+" GHz (used for datamining)\n\n**__Network Information__**\n**Bandwith** - "+str(doc['network']['bandwidth'] + 10   )+" Mbps (how fast things load)\n**DDOS Protection** - "+str(doc['network']['ddos_pro'])+" (protection against attacks)\n **Firewall** - "+str(doc['network']['firewall'])+" (protects against connections without a port)\n**IP Address** - ||"+doc['ip']+"||\n\n**__Other Information__**\n**Balance** - "+str(doc['balance'])+" <:coin:592831769024397332>\n**Connection Message** - "+doc['connect_msg']

                if str(ctx.author.id) in cache.keys():
                    sys_string = sys_string + "\n\n**__Connection__**\n**Host** - "+cache[str(ctx.author.id)]['host']+"\n**Admin** - False"

                embed = discord.Embed(
                    title = "System Information",
                    description = sys_string,
                    color = 0x7289da
                )
            except Exception as e:
                print(e)
            msg = await ctx.author.send("<a:loading2:592819419604975797> `Obtaining system information...`")
            await asyncio.sleep(calc_loading(doc, 5))
            await msg.edit(content="<:done:592819995843624961> `System information retreived`", embed=embed)



@bot.command()
async def breach(ctx):
    pass





#Edit connection message
@system.command()
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
        await ctx.author.send("`error in command \'print\'. A message must be provided.`")
        return
    if str(ctx.author.id) not in cache.keys():
        did_do = False
        for key, value in cache.items():
            if key == 'away':
                continue
            if value['host'] == user['ip']:
                host_user = discord.utils.get(bot.get_all_members(), id=int(key))
                if host_user != None:
                    await host_user.send("`LOG: ("+value['host']+") "+msg+"`")
                    await ctx.author.send("`LOG: ("+user['ip']+") "+msg+"`")
                    did_do = True

        if did_do == False:
            await ctx.author.send("`SocketError: not connected to any network.`")
            return
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

#Give
@bot.command()
async def setmoney(ctx, user : discord.User = None, amount : int = None):
    print("GUFAJD")
    if ctx.author.id not in owner_ids:
        print("no")
        return
    if user == None:
        user = ctx.author
    if amount == None:
        amount = 1

    doc = users_col.find_one({'user_id': str(user.id)})
    if doc == None:
        print("belhfdjgkf")
        await ctx.author.send("wtf who is that nerd. couldn't find him. you loser")
        return
    print("starting BS")
    new_doc = { '$set': {'balance': int(amount)}}
    users_col.update_one(doc, new_doc)
    print("IT did the bs")
    if int(amount) < 0:
        print("GAY")
        await ctx.author.send("Nom nom nom, Wumpus ate some of %s's coins, they have %s coins now. They used to have %s coins but Wumpus was hungry." % (user.name, str(doc['balance'] + amount), str(doc['balance'])))
        return
    elif int(amount) > 0:
        print("NotsoGay")
        await ctx.author.send("*Blech*, Wumpus threw up his left over coins. %s picked them up. They have %s coins now. They used to have %s coins but Wumpus didn't feel good." % (user.name, str(doc['balance'] + amount), str(doc['balance'])))
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


#Command not found
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('`"%s" is not recognized as an internal or external command, operable program or batch file.`' % (ctx.message.content))
    else:
        raise error


bot.loop.create_task(tick())
bot.run(config.TOKEN)
